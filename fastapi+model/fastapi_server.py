"""
VastuGPT FastAPI Server
=======================
REST API for Vastu consultation using int8-dequantized LLaMA on CPU.

Run:   python fastapi_server.py
Docs:  http://localhost:8000/docs
"""

import asyncio
import gc
import os
import time
import warnings
import logging
from typing import Optional, Dict, List

# Suppress noisy warnings before any other imports
warnings.filterwarnings("ignore")
os.environ["TORCHAO_DISABLE"] = "1"
os.environ["SAFETENSORS_FAST_GPU"] = "0"
logging.disable(logging.WARNING)

import psutil
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
import transformers.modeling_utils as _mu

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import uvicorn

# ---------------------------------------------------------------------------
# PATCH 1: Allow int8 weights AND capture BNB metadata (SCB scales)
# ---------------------------------------------------------------------------
_orig_load_param = _mu._load_parameter_into_model


def _patched_load_param(model, param_name, tensor, **kwargs):
    if not tensor.is_floating_point() and not tensor.is_complex():
        module, param_type = _mu.get_module_from_name(model, param_name)
        setattr(module, param_type, torch.nn.Parameter(tensor, requires_grad=False))
        return
    return _orig_load_param(model, param_name, tensor, **kwargs)


_mu._load_parameter_into_model = _patched_load_param

# ---------------------------------------------------------------------------
# PATCH 2: Dequantize int8 weights on-the-fly in Linear.forward
# ---------------------------------------------------------------------------


def _int8_linear_forward(self, input):
    w = self.weight
    if not w.is_floating_point():
        scb = getattr(self, "SCB", None)
        if scb is not None:
            # Proper BNB absmax dequant: float_w = int8_w * absmax_scale / 127
            w = w.float() * scb.float().unsqueeze(-1) / 127.0
        else:
            w = w.float()
        input = input.float()
    elif input.dtype != w.dtype:
        input = input.to(w.dtype)
    b = self.bias
    if b is not None:
        b = b.to(w.dtype)
    return F.linear(input, w, b)


torch.nn.Linear.forward = _int8_linear_forward

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MODEL_PATH = r"D:\mad\MadApp\fastapi+model\vastu-merged-llama3"
MAX_NEW_TOKENS = 200
THREADS = max(1, (psutil.cpu_count(logical=False) or 4) - 1)

SYSTEM_PROMPT = """You are a strict Vastu Shastra expert.
RULES (DO NOT BREAK):
1. Start every answer with exactly ONE word:
   IDEAL, ACCEPTABLE, or INADVISABLE
2. Follow with ONE short sentence explaining why.
3. If the answer is not IDEAL, list 3–6 practical remedies as bullet points.
4. Do NOT discuss multiple possibilities.
5. Do NOT hedge or give philosophical explanations.
6. Be decisive and authoritative.
Answer format MUST be:
<CLASSIFICATION>
<one-line reason>
- remedy 1
- remedy 2
- remedy 3"""

# ---------------------------------------------------------------------------
# Engine state
# ---------------------------------------------------------------------------
_engine_model = None
_engine_tokenizer = None
_request_count = 0
_total_latency = 0.0
_server_start = 0.0


def _preload_scb_dict(model_path: str):
    """Pre-load SCB tensors from safetensors BEFORE the model (when RAM is free)."""
    import glob
    from safetensors import safe_open

    shard_files = sorted(glob.glob(os.path.join(model_path, "model*.safetensors")))
    scb_dict = {}
    for sf in shard_files:
        with safe_open(sf, framework="pt", device="cpu") as f:
            for key in f.keys():
                if key.endswith(".SCB"):
                    scb_dict[key] = f.get_tensor(key).clone()
    gc.collect()
    return scb_dict


def _attach_scb_scales(model, scb_dict):
    """Attach pre-loaded SCB scale tensors to model Linear modules."""
    loaded = 0
    for key, scb_tensor in scb_dict.items():
        parts = key.split(".")
        attr_name = parts[-1]  # "SCB"
        module_path = ".".join(parts[:-1])
        try:
            module = model
            for p in module_path.split("."):
                module = getattr(module, p)
            module.register_buffer(attr_name, scb_tensor)
            loaded += 1
        except AttributeError:
            pass
    return loaded


def _load_engine():
    global _engine_model, _engine_tokenizer
    gc.collect()
    torch.set_num_threads(THREADS)
    try:
        torch.set_num_interop_threads(max(1, THREADS // 2))
    except RuntimeError:
        pass

    print("Loading tokenizer...")
    try:
        _engine_tokenizer = AutoTokenizer.from_pretrained(
            MODEL_PATH, use_fast=True, fix_mistral_regex=True
        )
    except TypeError:
        _engine_tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, use_fast=True)
    if _engine_tokenizer.pad_token is None:
        _engine_tokenizer.pad_token = _engine_tokenizer.eos_token

    # Pre-load SCB dequant scales while RAM is free (before model load)
    print("Pre-loading SCB dequant scales...", flush=True)
    scb_dict = _preload_scb_dict(MODEL_PATH)
    print(f"  Got {len(scb_dict)} SCB tensors", flush=True)

    print("Loading model (int8 CPU)...", flush=True)
    _engine_model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        device_map="cpu",
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
    )
    _engine_model.eval()

    # Attach SCB scales to model (transformers skips them during loading)
    print("Attaching SCB scales to model...", flush=True)
    scb_count = _attach_scb_scales(_engine_model, scb_dict)
    del scb_dict
    print(f"  Attached {scb_count} / 224 SCB scales", flush=True)

    gc.collect()
    mem = psutil.virtual_memory()
    print(f"Model ready  |  RAM used: {(mem.total - mem.available) / (1024**3):.1f} GB")


@torch.inference_mode()
def _ask(question: str) -> Dict:
    global _request_count, _total_latency

    prompt = (
        f"### System:\n{SYSTEM_PROMPT}\n\n"
        f"### User:\n{question.strip()}\n\n"
        "### Response:\n"
    )
    inputs = _engine_tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1536)
    inputs = {k: v.to("cpu") for k, v in inputs.items()}

    t0 = time.perf_counter()
    output = _engine_model.generate(
        **inputs,
        max_new_tokens=MAX_NEW_TOKENS,
        temperature=0.2,
        do_sample=False,
        repetition_penalty=1.1,
        pad_token_id=_engine_tokenizer.eos_token_id,
    )
    dt = time.perf_counter() - t0

    text = _engine_tokenizer.decode(output[0], skip_special_tokens=True)
    ans = text.split("### Response:")[-1].strip()
    out_tokens = int(output.shape[-1] - inputs["input_ids"].shape[-1])

    _request_count += 1
    _total_latency += dt

    return {
        "question": question,
        "answer": ans,
        "latency_s": round(dt, 2),
        "tokens_generated": out_tokens,
        "tokens_per_second": round(out_tokens / dt, 2) if dt > 0 else 0.0,
    }


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _server_start
    print("=" * 60)
    print("Starting VastuGPT API Server")
    print("=" * 60)
    _server_start = time.time()
    _load_engine()
    print(f"Server ready | http://localhost:8000/docs")
    print("=" * 60)
    yield
    print("Shutting down VastuGPT API Server")


app = FastAPI(
    title="VastuGPT API",
    description="AI-powered Vastu Shastra consultation",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic models ---
class VastuQueryRequest(BaseModel):
    question: str = Field(
        ..., description="Vastu question", min_length=5, max_length=500,
        examples=["Is a toilet in the northeast corner acceptable?"],
    )


class VastuQueryResponse(BaseModel):
    question: str
    answer: str
    latency_s: float
    tokens_generated: int
    tokens_per_second: float


class HealthResponse(BaseModel):
    status: str
    uptime_s: float
    total_requests: int
    avg_latency_s: float
    device: str
    ram_used_gb: float


# --- Endpoints ---
@app.get("/")
async def root():
    return {
        "service": "VastuGPT API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    if _engine_model is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Engine not loaded")
    mem = psutil.virtual_memory()
    return HealthResponse(
        status="healthy",
        uptime_s=round(time.time() - _server_start, 2),
        total_requests=_request_count,
        avg_latency_s=round(_total_latency / _request_count, 2) if _request_count else 0.0,
        device=f"CPU ({THREADS} threads)",
        ram_used_gb=round((mem.total - mem.available) / (1024**3), 1),
    )


@app.post("/api/vastu/ask", response_model=VastuQueryResponse)
async def ask_vastu(query: VastuQueryRequest):
    if _engine_model is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Engine not loaded")
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: _ask(query.question))
        return VastuQueryResponse(**result)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


@app.post("/api/vastu/batch")
async def batch_ask(questions: List[str]):
    if _engine_model is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Engine not loaded")
    if len(questions) > 10:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Max 10 questions per batch")
    loop = asyncio.get_event_loop()
    results = []
    for q in questions:
        try:
            r = await loop.run_in_executor(None, lambda q=q: _ask(q))
            results.append(r)
        except Exception as e:
            results.append({"question": q, "error": str(e)})
    return {"results": results}


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", access_log=True)


if __name__ == "__main__":
    main()
