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
    BitsAndBytesConfig,
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
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, token=HF_TOKEN)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("✅ Tokenizer loaded")

# -------------------------------------------------
# LOAD MODEL (CORRECT INT8 + CPU OFFLOAD)
# -------------------------------------------------
print("🧠 Loading model with INT8 + CPU offload (RTX 3050 SAFE)...")

bnb_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_enable_fp32_cpu_offload=True,  # ✅ CORRECT LOCATION
)

max_memory = {
    0: "3500MB",   # GPU
    "cpu": "24GB"  # RAM
}

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,   # ✅ ONLY place it goes
    device_map="auto",
    max_memory=max_memory,
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

    first_device = next(iter(model.hf_device_map.values()))
    inputs = {k: v.to(first_device) for k, v in inputs.items()}

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
