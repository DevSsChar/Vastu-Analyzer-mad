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

# Load environment variables
load_dotenv()

# ---------------------------------
# CONFIG
# ---------------------------------
BASE_MODEL = os.getenv("BASE_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")
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
# LOAD MODEL (GPU + CPU HYBRID)
# ---------------------------------
def load_model():
    """Load model with GPU+CPU hybrid approach (no bitsandbytes)"""
    try:
        # Force garbage collection
        import gc
        gc.collect()
        
        print("Step 1/3: Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            BASE_MODEL,
            token=HF_TOKEN,
            trust_remote_code=True,
        )
        tokenizer.pad_token = tokenizer.eos_token
        print("✓ Tokenizer loaded")
        
        gc.collect()  # Free memory

        print("\nStep 2/3: Loading base model...")
        print("⚠ Loading to CPU with maximum memory efficiency")
        print("⚠ This will take 5-8 minutes...")
        print("⚠ If it hangs, you need to free up more RAM\n")
        
        # Load entirely to CPU first (no hanging issues)
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            token=HF_TOKEN,
            torch_dtype=torch.float16,
            device_map="cpu",
            low_cpu_mem_usage=True,
            trust_remote_code=True,
            use_safetensors=True,  # More memory efficient
        )
        
        print("\n✓ Base model loaded to CPU")
        gc.collect()  # Free memory

        print("\nStep 3/3: Loading LoRA adapter...")
        model = PeftModel.from_pretrained(
            base_model,
            LORA_PATH,
        )
        print("✓ LoRA adapter loaded")

        model.eval()
        
        # Check memory
        if torch.cuda.is_available():
            gpu_mem = torch.cuda.memory_allocated(0) / (1024**3)
            print(f"🎮 GPU memory used: {gpu_mem:.2f} GB")
        
        memory = psutil.virtual_memory()
        ram_used = (memory.total - memory.available) / (1024**3)
        print(f"💾 RAM used: {ram_used:.1f} GB")
        
        return model, tokenizer
    
    except Exception as e:
        print(f"\n❌ ERROR during model loading: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


print("="*60)
print("🚀 Starting Vastu AI Advisor API (CPU with GPU boost)")
print("="*60)
print()

if torch.cuda.is_available():
    print(f"✅ GPU detected: {torch.cuda.get_device_name(0)}")
    print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB")
else:
    print("❌ No GPU detected - will run on CPU only (slower)")

memory = psutil.virtual_memory()
print(f"💾 System RAM: {memory.total / (1024**3):.1f} GB total, {memory.available / (1024**3):.1f} GB available\n")

# Check if enough RAM
if memory.available / (1024**3) < 10:
    print("⚠️  WARNING: Low available RAM!")
    print(f"   Available: {memory.available / (1024**3):.1f} GB")
    print(f"   Recommended: 10+ GB free")
    print("\n💡 Solution: Close other applications (browsers, games, etc.)")
    print("   Then run this script again.\n")
    
    response = input("Continue anyway? (y/N): ")
    if response.lower() != 'y':
        print("Exiting. Please free up RAM and try again.")
        exit(0)
    print()

print("Loading Llama-3-8B with your trained LoRA adapter...")
print("(Base model + LoRA will work together)\n")

try:
    model, tokenizer = load_model()
    print("\n✅ Model loaded successfully!")
    print("Your VastuGPT is ready! 🏛️\n")
except Exception as e:
    print("\n❌ Failed to load model.")
    exit(1)

# ---------------------------------
# FASTAPI APP
# ---------------------------------
app = FastAPI(
    title="VastuGPT API",
    description="AI-powered Vastu Shastra consultation with fine-tuned model",
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
    
    # Move inputs to GPU for faster inference
    if torch.cuda.is_available():
        try:
            # Try to move input to GPU
            inputs = {k: v.to('cuda:0') for k, v in inputs.items()}
            
            # Move model to GPU (will use GPU memory during inference only)
            if next(model.parameters()).device.type == 'cpu':
                print("Moving model to GPU for inference...")
                model.to('cuda:0')
                
        except RuntimeError as e:
            # If GPU OOM, fall back to CPU
            print(f"GPU memory full, using CPU: {e}")
            inputs = {k: v.to('cpu') for k, v in inputs.items()}

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
    device_info = "GPU+CPU hybrid" if hasattr(model, 'hf_device_map') else "CPU"
    return {
        "status": "running",
        "message": "VastuGPT API - Fine-tuned Vastu Consultant",
        "model": BASE_MODEL,
        "lora_adapter": LORA_PATH,
        "device": device_info,
        "precision": "float16"
    }

@app.get("/health")
async def health():
    memory = psutil.virtual_memory()
    health_info = {
        "status": "healthy",
        "model_loaded": model is not None,
        "ram_usage_gb": f"{(memory.total - memory.available) / (1024**3):.1f}",
        "ram_available_gb": f"{memory.available / (1024**3):.1f}"
    }
    
    if torch.cuda.is_available():
        health_info.update({
            "cuda_available": True,
            "gpu_name": torch.cuda.get_device_name(0),
            "gpu_memory_allocated_gb": f"{torch.cuda.memory_allocated(0) / (1024**3):.2f}"
        })
    
    return health_info

@app.post("/ask", response_model=VastuResponse)
async def ask_vastu(query: VastuQuery):
    """
    Ask VastuGPT a question about Vastu Shastra
    
    Your fine-tuned model will provide expert Vastu consultation
    """
    try:
        if not query.question or len(query.question.strip()) == 0:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        print(f"\n{'='*60}")
        print(f"❓ Question: {query.question}")
        print("🤔 VastuGPT is thinking...")
        
        answer = generate_response(
            query.question,
            max_tokens=query.max_tokens,
            temperature=query.temperature
        )
        
        print(f"💡 Answer: {answer[:100]}...")
        print(f"{'='*60}\n")
        
        return VastuResponse(
            question=query.question,
            answer=answer,
            model=f"{BASE_MODEL} + {LORA_PATH}"
        )
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("✅ Starting VastuGPT FastAPI server")
    print("🌐 API: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("🏛️ Your fine-tuned Vastu expert is ready!")
    print("="*60 + "\n")
    
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info"
    )
