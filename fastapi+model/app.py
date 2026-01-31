import os
import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# ---------------------------------
# CONFIG
# ---------------------------------
BASE_MODEL = os.getenv("BASE_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
LORA_PATH = os.getenv("LORA_PATH", "vastu_lora_adapter_975")
DEVICE = os.getenv("DEVICE", "cuda")
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
# LOAD MODEL (GPU OPTIMIZED FOR 4GB VRAM)
# ---------------------------------
@torch.inference_mode()
def load_model():
    """Load model with 4-bit quantization for 4GB VRAM with CPU offloading"""
    try:
        print("Step 1/4: Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            BASE_MODEL,
            token=HF_TOKEN,
            trust_remote_code=True,
        )
        tokenizer.pad_token = tokenizer.eos_token
        print("✓ Tokenizer loaded")

        print("\nStep 2/4: Configuring quantization...")
        # 4-bit quantization config for 4GB VRAM with CPU offloading
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            llm_int8_enable_fp32_cpu_offload=True  # Enable CPU offloading
        )
        print("✓ Quantization config ready")

        # Set max memory - more conservative for 4GB GPU
        max_memory = {
            0: "2800MB",  # GPU 0 - reduced to leave room for system
            "cpu": "20GB"  # CPU memory
        }

        print("\nStep 3/4: Loading base model (this will take 2-3 minutes)...")
        print("⚠ Large download expected (~14GB). Please be patient...")
        print("⏳ Loading layers... (this might appear frozen but it's working)")
        
        import sys
        sys.stdout.flush()  # Force output to display
        
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            token=HF_TOKEN,
            quantization_config=bnb_config,
            device_map="balanced",  # Try balanced instead of auto
            max_memory=max_memory,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
            offload_folder="offload",
            offload_state_dict=True,  # Offload state dict to save memory
        )
        print("✓ Base model loaded")

        print("\nStep 4/4: Loading LoRA adapter...")
        model = PeftModel.from_pretrained(
            base_model,
            LORA_PATH,
        )
        print("✓ LoRA adapter loaded")

        model.eval()
        
        # Print device map
        print("\n" + "="*50)
        print("Model device map:")
        if hasattr(model, 'hf_device_map'):
            for name, device in list(model.hf_device_map.items())[:5]:
                print(f"  {name}: {device}")
            if len(model.hf_device_map) > 5:
                print(f"  ... and {len(model.hf_device_map) - 5} more layers")
        print("="*50 + "\n")
        
        return model, tokenizer
    
    except Exception as e:
        print(f"\n❌ ERROR during model loading: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        raise


print("="*60)
print("🚀 Starting Vastu AI Advisor API")
print("="*60)
print("\nLoading model... This may take 2-3 minutes on first run...")
print("(Model will be cached for faster subsequent loads)\n")

try:
    model, tokenizer = load_model()
    print("\n✅ Model loaded successfully!")
    print(f"GPU Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU Name: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
except Exception as e:
    print("\n❌ Failed to load model. Please check the error above.")
    print("\nTroubleshooting:")
    print("1. Ensure HF_TOKEN is set in your .env file")
    print("2. Check if you have enough disk space (~14GB needed)")
    print("3. Verify CUDA is properly installed: python -c 'import torch; print(torch.cuda.is_available())'")
    exit(1)

# ---------------------------------
# FASTAPI APP
# ---------------------------------
app = FastAPI(
    title="Vastu AI Advisor API",
    description="AI-powered Vastu Shastra consultation API",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class VastuQuery(BaseModel):
    question: str
    max_tokens: int = 128
    temperature: float = 0.3

class VastuResponse(BaseModel):
    question: str
    answer: str
    model: str

# ---------------------------------
# GENERATION (GPU OPTIMIZED)
# ---------------------------------
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
    
    # Move inputs to first available device (works with device_map="auto")
    if hasattr(model, 'hf_device_map'):
        first_device = list(model.hf_device_map.values())[0]
        inputs = {k: v.to(first_device) for k, v in inputs.items()}

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


# ---------------------------------
# API ENDPOINTS
# ---------------------------------
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "message": "Vastu AI Advisor API is running",
        "model": BASE_MODEL,
        "device": DEVICE
    }

@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": DEVICE,
        "cuda_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    }

@app.post("/ask", response_model=VastuResponse)
async def ask_vastu(query: VastuQuery):
    """
    Ask a Vastu Shastra question
    
    - **question**: Your Vastu question (e.g., "Is a toilet in NE acceptable?")
    - **max_tokens**: Maximum tokens in response (default: 128)
    - **temperature**: Response creativity (0.0-1.0, default: 0.3)
    """
    try:
        if not query.question or len(query.question.strip()) == 0:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
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
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")


# ---------------------------------
# RUN SERVER
# ---------------------------------
if __name__ == "__main__":
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info"
    )