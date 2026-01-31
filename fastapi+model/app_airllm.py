import os
import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
)

load_dotenv()

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
BASE_MODEL = os.getenv("BASE_MODEL", "vastu-merged-llama3")
HOST = "0.0.0.0"
PORT = 8000
HF_TOKEN = os.getenv("HF_TOKEN")

SYSTEM_PROMPT = """You are a traditional Vastu Shastra expert.

Rules:
- You MUST classify every answer as IDEAL, ACCEPTABLE, or INADVISABLE.
- Be decisive and authoritative.
- Avoid astrology, professions, or philosophy.
- Give remedies ONLY if needed.
- Be concise and actionable.
"""

# -------------------------------------------------
# LOAD TOKENIZER
# -------------------------------------------------
print("🔤 Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL, 
    token=HF_TOKEN,
    fix_mistral_regex=True
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("✅ Tokenizer loaded")

# -------------------------------------------------
# LOAD MODEL - THE ACTUAL FIX
# -------------------------------------------------
print("🧠 Loading model with CPU offload...")

# Custom device map
device_map = {
    "model.embed_tokens": 0,
    "model.layers.0": 0,
    "model.layers.1": 0,
    "model.layers.2": 0,
    "model.layers.3": 0,
    "model.layers.4": 0,
    "model.layers.5": 0,
    "model.layers.6": 0,
    "model.layers.7": 0,
    "model.layers.8": "cpu",
    "model.layers.9": "cpu",
    "model.layers.10": "cpu",
    "model.layers.11": "cpu",
    "model.layers.12": "cpu",
    "model.layers.13": "cpu",
    "model.layers.14": "cpu",
    "model.layers.15": "cpu",
    "model.layers.16": "cpu",
    "model.layers.17": "cpu",
    "model.layers.18": "cpu",
    "model.layers.19": "cpu",
    "model.layers.20": "cpu",
    "model.layers.21": "cpu",
    "model.layers.22": "cpu",
    "model.layers.23": "cpu",
    "model.layers.24": "cpu",
    "model.layers.25": "cpu",
    "model.layers.26": "cpu",
    "model.layers.27": "cpu",
    "model.layers.28": "cpu",
    "model.layers.29": "cpu",
    "model.layers.30": "cpu",
    "model.layers.31": "cpu",
    "model.norm": "cpu",
    "lm_head": "cpu",
}

# ✅✅✅ THE ACTUAL FIX ✅✅✅
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    device_map=device_map,
    llm_int8_enable_fp32_cpu_offload=True,  # ✅ Pass as kwarg, NOT in quantization_config!
    low_cpu_mem_usage=True,
    token=HF_TOKEN,
)

model.eval()

print("✅ Model loaded successfully")
print("📍 Device map:")
for k, v in model.hf_device_map.items():
    print(f"  {k} → {v}")

# -------------------------------------------------
# FASTAPI
# -------------------------------------------------
app = FastAPI(title="VastuGPT API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class VastuQuery(BaseModel):
    question: str
    max_tokens: int = 128
    temperature: float = 0.2

class VastuResponse(BaseModel):
    question: str
    answer: str
    model: str

# -------------------------------------------------
# GENERATION
# -------------------------------------------------
def generate_response(question, max_tokens, temperature):
    prompt = f"""### System:
{SYSTEM_PROMPT}

### User:
{question}

### Response:
"""

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
    
    # Move inputs to GPU
    inputs = {k: v.to(0) for k, v in inputs.items()}

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=False,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.eos_token_id,
        )

    text = tokenizer.decode(output[0], skip_special_tokens=True)
    return text.split("### Response:")[-1].strip()

# -------------------------------------------------
# API ENDPOINT
# -------------------------------------------------
@app.post("/ask", response_model=VastuResponse)
def ask_vastu(query: VastuQuery):
    if not query.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    answer = generate_response(
        query.question,
        query.max_tokens,
        query.temperature,
    )

    return VastuResponse(
        question=query.question,
        answer=answer,
        model="VastuGPT (Merged Llama-3-8B)",
    )

# -------------------------------------------------
# RUN
# -------------------------------------------------
if __name__ == "__main__":
    print("🌐 http://localhost:8000")
    print("📖 http://localhost:8000/docs")
    uvicorn.run(app, host=HOST, port=PORT)