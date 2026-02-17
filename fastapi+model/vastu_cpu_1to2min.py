import argparse
import gc
import os
import time
import random
import statistics
import warnings
import logging
from typing import Dict, List

# Suppress all noisy warnings before any imports
warnings.filterwarnings("ignore")
os.environ["TORCHAO_DISABLE"] = "1"
os.environ["SAFETENSORS_FAST_GPU"] = "0"
logging.disable(logging.WARNING)

import psutil
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
import transformers.modeling_utils as _mu

# ---------------------------------------------------------------------------
# PATCH 1: Allow int8 weights to load as Parameter(requires_grad=False).
# transformers _load_parameter_into_model crashes on int8 because
# load_state_dict(assign=True) tries to set requires_grad=True.
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
# PATCH 2: Override nn.Linear.forward to properly dequantize BNB int8 weights.
# Uses the per-row SCB scale: w_float = w_int8.float() * SCB / 127
# The SCB buffers are loaded AFTER model load (see _load_scb_scales).
# ---------------------------------------------------------------------------

def _int8_linear_forward(self, input):
    w = self.weight
    if not w.is_floating_point():
        scb = getattr(self, "SCB", None)
        if scb is not None:
            # Proper BNB absmax dequant: float_w = int8_w * absmax_scale / 127
            # Use non-inplace ops to avoid any potential corruption
            w = w.float() * scb.float().unsqueeze(-1) / 127.0
        else:
            w = w.float()
        # Also promote input to float32 for the matmul
        input = input.float()
    elif input.dtype != w.dtype:
        input = input.to(w.dtype)

    b = self.bias
    if b is not None:
        b = b.to(w.dtype)
    return F.linear(input, w, b)

torch.nn.Linear.forward = _int8_linear_forward
# ---------------------------------------------------------------------------

MODEL_PATH = r"D:\mad\MadApp\fastapi+model\vastu-merged-llama3"

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

BENCH_QUESTIONS = [
    "Is a toilet in the northeast acceptable?",
    "Can the kitchen be in the south direction for a 30x40 plot?",
    "Main entrance in west – good or bad?",
    "Master bedroom in north-east for a married couple?",
    "Where should underground water tank be placed?",
]


def _print_stats(threads: int):
    m = psutil.virtual_memory()
    print("=" * 70)
    print("Vastu CPU Runner (1-2 min target)")
    print("=" * 70)
    print(f"RAM: {m.total / (1024**3):.1f} GB total, {m.available / (1024**3):.1f} GB free")
    print(f"CPU threads: {threads}")
    print("=" * 70)


class Engine:
    def __init__(self, model_path: str, max_new_tokens: int, threads: int):
        self.model_path = model_path
        self.max_new_tokens = max_new_tokens
        self.threads = threads
        self.tokenizer = None
        self.model = None
        self.device = "cpu"
        self._load()

    @staticmethod
    def _load_scb_scales(model, scb_dict):
        """Attach pre-loaded SCB scale tensors to the model's Linear modules.

        scb_dict maps e.g. "model.layers.0.self_attn.q_proj.SCB" -> tensor
        """
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

    @staticmethod
    def _preload_scb_dict(model_path: str):
        """Pre-load SCB tensors from safetensors BEFORE the model (when RAM is free).

        Returns a dict mapping key -> tensor. Total size is tiny (~1 MB for 224 scales).
        """
        import glob
        from safetensors import safe_open

        shard_files = sorted(glob.glob(os.path.join(model_path, "model*.safetensors")))
        scb_dict = {}
        for sf in shard_files:
            with safe_open(sf, framework="pt", device="cpu") as f:
                for key in f.keys():
                    if key.endswith(".SCB"):
                        # .clone() to fully detach from mmap before we close the file
                        scb_dict[key] = f.get_tensor(key).clone()
        gc.collect()
        return scb_dict

    def _load(self):
        gc.collect()
        torch.set_num_threads(self.threads)
        if hasattr(torch, "set_num_interop_threads"):
            try:
                torch.set_num_interop_threads(max(1, self.threads // 2))
            except RuntimeError:
                pass

        print("Loading tokenizer...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, use_fast=True, fix_mistral_regex=True,
            )
        except TypeError:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, use_fast=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Pre-load SCB scales while RAM is still free (before model load)
        print("Pre-loading SCB dequant scales...", flush=True)
        scb_dict = self._preload_scb_dict(self.model_path)
        print(f"  Got {len(scb_dict)} SCB tensors (~{sum(t.nbytes for t in scb_dict.values()) / 1024:.0f} KB)", flush=True)

        # Load model — the monkey-patch handles int8 weights
        print("Loading model (int8 CPU)...", flush=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            device_map="cpu",
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
        )
        self.device = "cpu"
        self.model.eval()

        # Attach pre-loaded SCB scales to model modules
        print("Attaching SCB scales to model...", flush=True)
        scb_count = self._load_scb_scales(self.model, scb_dict)
        del scb_dict
        print(f"  Attached {scb_count} / 224 SCB scales", flush=True)

        gc.collect()
        mem = psutil.virtual_memory()
        print(f"Model ready  |  RAM used: {(mem.total - mem.available) / (1024**3):.1f} GB")

    @torch.inference_mode()
    def ask(self, question: str) -> Dict[str, object]:
        prompt = (
            f"### System:\n{SYSTEM_PROMPT}\n\n"
            f"### User:\n{question.strip()}\n\n"
            "### Response:\n"
        )
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1536)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        t0 = time.perf_counter()
        output = self.model.generate(
            **inputs,
            max_new_tokens=self.max_new_tokens,
            temperature=0.2,
            do_sample=False,
            repetition_penalty=1.1,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        dt = time.perf_counter() - t0

        text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        ans = text.split("### Response:")[-1].strip()
        out_tokens = int(output.shape[-1] - inputs["input_ids"].shape[-1])
        return {
            "answer": ans,
            "latency_s": round(dt, 2),
            "tokens": out_tokens,
            "tps": round(out_tokens / dt, 2) if dt > 0 else 0.0,
        }


def run_benchmark(engine: Engine, requests: int):
    lats: List[float] = []
    tps: List[float] = []
    words: List[int] = []
    print("\nBenchmark start")
    for i in range(requests):
        q = random.choice(BENCH_QUESTIONS)
        r = engine.ask(q)
        lats.append(r["latency_s"])
        tps.append(r["tps"])
        words.append(len(r["answer"].split()))
        print(f"[{i+1:03d}/{requests}] {r['latency_s']:.2f}s | tok={r['tokens']} | tps={r['tps']} | words={words[-1]}")

    print("\nSummary")
    print(f"mean latency: {statistics.mean(lats):.2f}s")
    print(f"p90 latency: {sorted(lats)[max(0, int(0.9*len(lats))-1)]:.2f}s")
    print(f"mean tps: {statistics.mean(tps):.2f}")
    print(f"mean words: {statistics.mean(words):.1f}")


def main():
    parser = argparse.ArgumentParser(description="CPU optimized Vastu runner")
    parser.add_argument("--model-path", default=MODEL_PATH)
    parser.add_argument("--max-new-tokens", type=int, default=200, help="Max tokens to generate (200 matches original model)")
    parser.add_argument("--threads", type=int, default=max(1, (psutil.cpu_count(logical=False) or 4) - 1))
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--requests", type=int, default=5)
    args = parser.parse_args()

    _print_stats(args.threads)
    engine = Engine(args.model_path, args.max_new_tokens, args.threads)

    if args.benchmark:
        run_benchmark(engine, args.requests)
        return

    print("\nInteractive mode (type 'exit')")
    while True:
        q = input("Q> ").strip()
        if not q:
            continue
        if q.lower() in {"exit", "quit"}:
            break
        r = engine.ask(q)
        print(f"\nA ({r['latency_s']}s, {r['tps']} tok/s):\n{r['answer']}\n")


if __name__ == "__main__":
    main()
