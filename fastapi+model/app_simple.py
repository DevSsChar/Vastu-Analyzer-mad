import os
import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from dotenv import load_dotenv
import uvicorn
import psutil
import gc

# Load environment variables
load_dotenv()

# ---------------------------------
# CONFIG
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

def check_system_resources():
    """Check if system has enough resources"""
    memory = psutil.virtual_memory()
    total_gb = memory.total / (1024**3)
    available_gb = memory.available / (1024**3)
    
    print(f"System RAM: {total_gb:.1f} GB total, {available_gb:.1f} GB available")
    
    if available_gb < 6:
        print(f"⚠ WARNING: Low available RAM ({available_gb:.1f} GB)")
        print("  Recommended: At least 6GB available RAM")
        print("  Close other applications to free up memory")
        return False
    return True

# ---------------------------------
# LOAD MODEL (NO BITSANDBYTES - NATIVE PYTORCH)
# ---------------------------------
def load_model():
    """Load model using native PyTorch (no bitsandbytes)"""
    try:
        print("Step 1/3: Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            BASE_MODEL,
            token=HF_TOKEN,
            trust_remote_code=True,
        )
        tokenizer.pad_token = tokenizer.eos_token
        print("✓ Tokenizer loaded")
        
        gc.collect()  # Free up memory

        print("\nStep 2/3: Loading base model...")
        print("⚠ Using float16 precision to reduce memory usage")
        print("⚠ This will take 3-5 minutes and download ~14GB...")
        print("Progress will be shown below:\n")
        
        # Load without bitsandbytes - use native PyTorch
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            token=HF_TOKEN,
            torch_dtype=torch.float16,  # Use float16 instead of float32
            device_map="cpu",           # Load to CPU
            low_cpu_mem_usage=True,     # Memory efficient loading
            trust_remote_code=True,
        )
        
        print("\n✓ Base model loaded")
        
        gc.collect()  # Free up memory

        print("\nStep 3/3: Loading LoRA adapter...")
        model = PeftModel.from_pretrained(
            base_model,
            LORA_PATH,
        )
        print("✓ LoRA adapter loaded")

        model.eval()
        
        # Check memory usage
        memory = psutil.virtual_memory()
        used_gb = (memory.total - memory.available) / (1024**3)
        print(f"\n📊 Current RAM usage: {used_gb:.1f} GB")
        
        return model, tokenizer
    
    except Exception as e:
        print(f"\n❌ ERROR during model loading: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


print("="*60)
print("🚀 Starting Vastu AI Advisor API (Native PyTorch)")
print("="*60)
print()

# Check resources
if not check_system_resources():
    print("\n⚠ Continuing anyway, but loading may fail...")

print("\nLoading model with float16 precision...")
print("(No bitsandbytes quantization - using native PyTorch)\n")

try:
    model, tokenizer = load_model()
    print("\n✅ Model loaded successfully!")
except Exception as e:
    print("\n❌ Failed to load model.")
    print("\nPossible solutions:")
    print("1. Close other applications to free up RAM")
    print("2. Restart your computer to clear memory")
    print("3. Consider using a smaller model")
    exit(1)

# ---------------------------------
# FASTAPI APP
# ---------------------------------
app = FastAPI(
    title="Vastu AI Advisor API",
    description="AI-powered Vastu Shastra consultation API",
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

    print(f"Generating response (this may take 30-60 seconds on CPU)...")
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
        "message": "Vastu AI Advisor API",
        "model": BASE_MODEL,
        "device": "cpu",
        "precision": "float16"
    }

@app.get("/health")
async def health():
    memory = psutil.virtual_memory()
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": "cpu",
        "ram_usage_gb": f"{(memory.total - memory.available) / (1024**3):.1f}",
        "ram_available_gb": f"{memory.available / (1024**3):.1f}"
    }

@app.post("/ask", response_model=VastuResponse)
async def ask_vastu(query: VastuQuery):
    """Ask a Vastu Shastra question"""
    try:
        if not query.question or len(query.question.strip()) == 0:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        print(f"\n{'='*60}")
        print(f"Question: {query.question}")
        
        answer = generate_response(
            query.question,
            max_tokens=query.max_tokens,
            temperature=query.temperature
        )
        
        print(f"Answer: {answer[:100]}...")
        print(f"{'='*60}\n")
        
        return VastuResponse(
            question=query.question,
            answer=answer,
            model=BASE_MODEL
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("✅ Starting FastAPI server on http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("⚠  Responses will take 30-60 seconds (CPU inference)")
    print("="*60 + "\n")
    
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info"
    )
