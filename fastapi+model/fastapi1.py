import os
import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
from transformers import AutoModelForCausalLM, AutoTokenizer

load_dotenv()

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
BASE_MODEL = os.getenv("BASE_MODEL", "D:\\mad\\MadApp\\fastapi+model\\vastu-merged-llama3")
HOST = "0.0.0.0"
PORT = 8000
HF_TOKEN = os.getenv("HF_TOKEN")

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

# -------------------------------------------------
# LOAD TOKENIZER
# -------------------------------------------------
print("🔤 Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, fix_mistral_regex=True)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("✅ Tokenizer loaded")

# -------------------------------------------------
# LOAD MODEL (CPU ONLY - STABLE)
# -------------------------------------------------
print("🧠 Loading model on CPU (stable, no GPU errors)...")

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    device_map="cpu",
    torch_dtype=torch.float16,  # Use FP16 for efficiency
    low_cpu_mem_usage=True,
)

model.eval()

print("✅ Model loaded successfully on CPU")
print("💾 Using ~11GB RAM")

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
    max_tokens: int = 200
    temperature: float = 0.2

class VastuResponse(BaseModel):
    question: str
    answer: str
    model: str

# -------------------------------------------------
# GENERATION
# -------------------------------------------------
@torch.inference_mode()
def generate_response(question, max_tokens):
    prompt = f"""### System:
{SYSTEM_PROMPT}

### User:
{question}

### Response:
"""

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)

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
    )

    return VastuResponse(
        question=query.question,
        answer=answer,
        model="VastuGPT (Llama-3-8B CPU)",
    )

# -------------------------------------------------
# RUN
# -------------------------------------------------
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🌐 VastuGPT API Server Running")
    print("="*60)
    print(f"📍 Local: http://localhost:{PORT}")
    print(f"📖 Docs: http://localhost:{PORT}/docs")
    print("="*60 + "\n")
    uvicorn.run(app, host=HOST, port=PORT)