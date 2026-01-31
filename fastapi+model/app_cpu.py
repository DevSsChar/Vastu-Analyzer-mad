import os
import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# ---------------------------------
# CONFIG (CPU OPTIMIZED)
# ---------------------------------
BASE_MODEL = os.getenv("BASE_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
LORA_PATH = os.getenv("LORA_PATH", "vastu_lora_adapter_975")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

HF_TOKEN = os.getenv("HF_TOKEN")

SYSTEM_PROMPT = """You are a strict and authoritative Vastu Shastra expert.
You clearly classify every placement as IDEAL, ACCEPTABLE, or INADVISABLE.
You always give practical remedies if something is wrong.
Your tone is confident, traditional, and decisive.
Avoid unnecessary philosophy. Be precise and actionable.
"""

# ---------------------------------
# LOAD MODEL (CPU ONLY - NO GPU)
# ---------------------------------
@torch.inference_mode()
def load_model():
    """Load model on CPU only"""
    try:
        print("Step 1/3: Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            BASE_MODEL,
            token=HF_TOKEN,
            trust_remote_code=True,
        )
        tokenizer.pad_token = tokenizer.eos_token
        print("✓ Tokenizer loaded")

        print("\nStep 2/3: Loading base model on CPU...")
        print("⚠ This will take 5-10 minutes and use ~15GB RAM...")
        
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            token=HF_TOKEN,
            torch_dtype=torch.float32,
            device_map="cpu",
            low_cpu_mem_usage=True,
            trust_remote_code=True,
        )
        print("✓ Base model loaded")

        print("\nStep 3/3: Loading LoRA adapter...")
        model = PeftModel.from_pretrained(
            base_model,
            LORA_PATH,
        )
        print("✓ LoRA adapter loaded")

        model.eval()
        return model, tokenizer
    
    except Exception as e:
        print(f"\n❌ ERROR during model loading: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


print("="*60)
print("🚀 Starting Vastu AI Advisor API (CPU Mode)")
print("="*60)
print("\n⚠ Warning: CPU mode is SLOW (~30-60 seconds per response)")
print("Loading model... This may take 5-10 minutes...\n")

try:
    model, tokenizer = load_model()
    print("\n✅ Model loaded successfully on CPU!")
except Exception as e:
    print("\n❌ Failed to load model.")
    exit(1)

# ---------------------------------
# FASTAPI APP
# ---------------------------------
app = FastAPI(
    title="Vastu AI Advisor API (CPU)",
    description="AI-powered Vastu Shastra consultation API - CPU Mode",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VastuQuery(BaseModel):
    question: str
    max_tokens: int = 128
    temperature: float = 0.3

class VastuResponse(BaseModel):
    question: str
    answer: str
    model: str

@torch.inference_mode()
def generate_response(user_prompt: str, max_tokens: int = 128, temperature: float = 0.3):
    """Generate Vastu consultation response"""
    prompt = f"""### System:
{SYSTEM_PROMPT}
### User:
{user_prompt}
### Response:
"""

    inputs = tokenizer(prompt, return_tensors="pt")

    outputs = model.generate(
        **inputs,
        max_new_tokens=max_tokens,
        do_sample=temperature > 0,
        temperature=temperature if temperature > 0 else None,
        repetition_penalty=1.1,
        pad_token_id=tokenizer.eos_token_id,
    )

    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return decoded.split("### Response:")[-1].strip()

@app.get("/")
async def root():
    return {
        "status": "running",
        "message": "Vastu AI Advisor API (CPU Mode)",
        "model": BASE_MODEL,
        "device": "cpu",
        "warning": "Responses will be slow (30-60 seconds)"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": "cpu"
    }

@app.post("/ask", response_model=VastuResponse)
async def ask_vastu(query: VastuQuery):
    """Ask a Vastu Shastra question (CPU mode - slow)"""
    try:
        if not query.question or len(query.question.strip()) == 0:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        print(f"Processing: {query.question[:50]}...")
        answer = generate_response(
            query.question,
            max_tokens=query.max_tokens,
            temperature=query.temperature
        )
        
        return VastuResponse(
            question=query.question,
            answer=answer,
            model=BASE_MODEL
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Starting FastAPI server on http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info"
    )
