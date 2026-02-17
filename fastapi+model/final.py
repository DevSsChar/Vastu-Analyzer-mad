import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import psutil
import gc

MODEL_PATH = "D:\\mad\\MadApp\\fastapi+model\\vastu-merged-llama3"

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

print("="*60)
print("🚀 Loading VastuGPT Model (GPU Optimized)")
print("="*60)

# Check GPU
if torch.cuda.is_available():
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB")
else:
    print("❌ No GPU - using CPU (slower)")

# Check RAM
memory = psutil.virtual_memory()
print(f"💾 RAM: {memory.total / (1024**3):.1f} GB total, {memory.available / (1024**3):.1f} GB available")
print()

# Clean memory
gc.collect()
if torch.cuda.is_available():
    torch.cuda.empty_cache()

print("Step 1/2: Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, fix_mistral_regex=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
print("✅ Tokenizer loaded")

print("\nStep 2/2: Loading model...")
print("⚠ Model has 8-bit quantization - configuring for 4GB VRAM")
print("⚠ This may take 2-5 minutes...\n")

# ✅✅✅ THE FIX: Create a NEW quantization config that OVERRIDES the saved one ✅✅✅
bnb_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_enable_fp32_cpu_offload=True,  # Enable CPU offload
)

# Custom device map for 4GB VRAM (RTX 3050)
# Put first 8 layers on GPU (~3.5GB), rest on CPU
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
}

# Remaining layers go to CPU (8-31)
for i in range(8, 32):
    device_map[f"model.layers.{i}"] = "cpu"

device_map["model.norm"] = "cpu"
device_map["lm_head"] = "cpu"

# ✅ Load with EXPLICIT quantization_config to override the saved one
# NUCLEAR OPTION - Full CPU load
# model = AutoModelForCausalLM.from_pretrained(
#     MODEL_PATH,
#     device_map="cpu",
#     torch_dtype=torch.float16,
#     low_cpu_mem_usage=True,
# )
bnb_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_enable_fp32_cpu_offload=True,
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    device_map="auto",
    quantization_config=bnb_config,
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True,
)

model.eval()

print("\n✅ Model loaded successfully!")
print(f"📍 Device map: {model.hf_device_map}")

# Memory stats
if torch.cuda.is_available():
    gpu_mem = torch.cuda.memory_allocated(0) / (1024**3)
    print(f"🎮 GPU memory used: {gpu_mem:.2f} GB")

memory = psutil.virtual_memory()
ram_used = (memory.total - memory.available) / (1024**3)
print(f"💾 RAM used: {ram_used:.1f} GB")
print("\n🏛️ VastuGPT ready!\n")

@torch.inference_mode()
def ask(question):
    prompt = f"""### System:
{SYSTEM_PROMPT}

### User:
{question}

### Response:
"""
    
    inputs = tokenizer(prompt, return_tensors="pt")
    
    # Move to first device where model starts (GPU or CPU)
    first_device = next(iter(model.hf_device_map.values()))
    inputs = {k: v.to(first_device) for k, v in inputs.items()}

    output = model.generate(
        **inputs,
        max_new_tokens=200,
        temperature=0.2,
        do_sample=False,
        repetition_penalty=1.1,
        pad_token_id=tokenizer.eos_token_id
    )

    text = tokenizer.decode(output[0], skip_special_tokens=True)
    return text.split("### Response:")[-1].strip()

# -----------------------------
# TEST QUESTIONS
# -----------------------------
questions = [
    "Is a toilet in the northeast acceptable?",
    "Can the kitchen be in the south direction?",
    "Main entrance in west – good or bad?",
]

print("="*60)
print("TESTING VASTUGPT")
print("="*60)
print()

for i, q in enumerate(questions, 1):
    print(f"Test {i}/{len(questions)}")
    print(f"Q: {q}")
    print("🤔 Generating...")
    answer = ask(q)
    print(f"A: {answer}")
    print("-" * 60)
    print()

print("✅ All tests completed!")