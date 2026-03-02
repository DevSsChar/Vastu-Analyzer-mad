"""
VastuGPT FastAPI Server - Optimized Single-Pass Pipeline
Floor Plan Vastu Analysis using Vision Language Model (Unsloth)
Based on updated_main.py with strict parsing and memory optimization
"""

# ✅ unsloth MUST be the absolute first import
import unsloth

import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True,max_split_size_mb:64"
os.environ["TOKENIZERS_PARALLELISM"]  = "false"

import gc
import io
import json
import re
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import torch
import numpy as np
import cv2
from PIL import Image
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from unsloth import FastVisionModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURATION
# ============================================================
VASTU_RULES_PATH    = "vastu_rules_home.json"
MAX_IMAGE_DIMENSION = 336
MAX_SEQ_LENGTH      = 512

# ============================================================
# GLOBAL MODEL VARIABLES
# ============================================================
model = None
tokenizer = None

# ============================================================
# PYDANTIC MODELS
# ============================================================
class RoomAnalysis(BaseModel):
    id: int
    type: str
    subtype: Optional[str] = None
    visual_position: str
    compass_direction: str
    status: str
    reason: str
    remedy: Optional[str] = None

class VastuAnalysisResponse(BaseModel):
    score: int = Field(..., ge=0, le=100)
    summary: Dict[str, int]
    orientation: Dict[str, Any]
    rooms: List[RoomAnalysis]
    message: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    gpu_available: bool

# ============================================================
# GPU MEMORY MANAGEMENT
# ============================================================
def clear_gpu_cache():
    """Clear GPU cache and run garbage collection"""
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

def log_gpu_memory(label=""):
    """Log current GPU memory usage"""
    if torch.cuda.is_available():
        alloc = torch.cuda.memory_allocated(0) / 1024**3
        free  = (torch.cuda.get_device_properties(0).total_memory
                 - torch.cuda.memory_reserved(0)) / 1024**3
        logger.info(f"  [GPU {label}] Alloc: {alloc:.2f}GB | Free: {free:.2f}GB")

# ============================================================
# IMAGE PREPROCESSING
# ============================================================
def preprocess_image_for_vlm(image_pil: Image.Image, max_dim=MAX_IMAGE_DIMENSION) -> Image.Image:
    """Resize image if needed to avoid OOM"""
    w, h = image_pil.size
    if max(w, h) <= max_dim:
        return image_pil
    scale        = max_dim / max(w, h)
    new_w, new_h = int(w * scale), int(h * scale)
    logger.info(f"📏 Resizing: {w}x{h} → {new_w}x{new_h}")
    return image_pil.resize((new_w, new_h), Image.LANCZOS)

# ============================================================
# VLM INFERENCE
# ============================================================
def vlm_generate(image_pil: Image.Image, prompt: str, max_new_tokens: int = 200) -> str:
    """Generate VLM response with memory optimization"""
    clear_gpu_cache()
    log_gpu_memory("pre-generate")

    image_copy = image_pil.copy()
    messages   = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": prompt}]}]
    input_text = tokenizer.apply_chat_template(messages, add_generation_prompt=True)

    with torch.no_grad():
        with torch.amp.autocast("cuda", dtype=torch.float16):
            inputs = tokenizer(
                images=[image_copy],
                text=input_text,
                add_special_tokens=False,
                return_tensors="pt",
                truncation=True,
                max_length=MAX_SEQ_LENGTH,
            )
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
            del image_copy
            gc.collect()

            output = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                min_new_tokens=5,
                do_sample=False,
                use_cache=False,
                num_beams=1,
                temperature=1.0,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

    text = tokenizer.decode(output[0].cpu(), skip_special_tokens=True)
    del output, inputs
    clear_gpu_cache()
    log_gpu_memory("post-generate")
    return text

# ============================================================
# ORIENTATION DETECTION
# ============================================================
def get_compass_from_image(image_pil: Image.Image) -> Optional[Dict]:
    """Try to detect compass rose from image"""
    logger.info("🧭 Attempting compass detection...")
    prompt = """Look at this floor plan image carefully.

Is there a compass rose showing N/S/E/W directions?

If YES:
- Tell me where each direction (N, E, S, W) is located on the image
- Format: "N is at [position], E is at [position], S is at [position], W is at [position]"
- Positions: top, bottom, left, right, top-left, top-right, bottom-left, bottom-right

If NO compass visible:
- Just write "NO COMPASS"

Example: "N is at bottom-left, E is at top-right, S is at top-right, W is at bottom" """

    text = vlm_generate(image_pil, prompt, max_new_tokens=100)
    logger.info(f"🧭 Compass Detection: {text[:200]}")

    # Parse compass positions
    compass_map = {}
    text_lower = text.lower()

    if "no compass" in text_lower:
        logger.info("⚠️ No compass detected in image")
        return None

    # Try to extract compass directions
    for direction in ['n', 'e', 's', 'w', 'north', 'east', 'south', 'west']:
        pattern = rf'{direction}\s+(?:is\s+)?(?:at\s+)?(?:the\s+)?([a-z\-]+)'
        match = re.search(pattern, text_lower)
        if match:
            position = match.group(1).strip()
            dir_key = direction[0].upper()

            # Map position to visual direction
            if 'top' in position and 'left' in position:
                compass_map[dir_key] = 'NW'
            elif 'top' in position and 'right' in position:
                compass_map[dir_key] = 'NE'
            elif 'bottom' in position and 'left' in position:
                compass_map[dir_key] = 'SW'
            elif 'bottom' in position and 'right' in position:
                compass_map[dir_key] = 'SE'
            elif 'top' in position:
                compass_map[dir_key] = 'N'
            elif 'bottom' in position:
                compass_map[dir_key] = 'S'
            elif 'left' in position:
                compass_map[dir_key] = 'W'
            elif 'right' in position:
                compass_map[dir_key] = 'E'

    if len(compass_map) >= 2:
        logger.info(f"✅ Compass found: {compass_map}")
        return compass_map

    logger.info("⚠️ No compass detected in image")
    return None

def calculate_offset_from_compass(compass_map: Dict) -> Optional[int]:
    """Calculate rotation offset from compass readings"""
    logger.info(f"📐 Calculating offset from compass: {compass_map}")
    if 'N' not in compass_map:
        logger.warning("⚠️ North direction not found in compass map")
        return None

    # Where North actually points on the image
    north_visual = compass_map['N']

    # Map visual positions to angles
    angles = {
        'N': 0, 'NE': 45, 'E': 90, 'SE': 135,
        'S': 180, 'SW': 225, 'W': 270, 'NW': 315
    }

    north_angle = angles.get(north_visual, 0)

    # Offset to rotate North to point up
    offset = (360 - north_angle) % 360
    logger.info(f"✅ Calculated offset: {offset}° (North at {north_visual})")

    return offset

def calculate_offset(house_facing: str, door_position: str) -> int:
    """Calculate north offset from house facing and door position"""
    logger.info(f"📐 Calculating offset - Facing: {house_facing}, Door: {door_position}")
    angles = {'N': 0, 'NE': 45, 'E': 90, 'SE': 135, 'S': 180, 'SW': 225, 'W': 270, 'NW': 315}

    facing_angle = angles.get(house_facing.upper(), 0)
    door_angle = angles.get(door_position.upper(), 0)

    offset = (facing_angle - door_angle) % 360
    logger.info(f"✅ Calculated offset: {offset}°")
    return offset

# ============================================================
# ROOM DETECTION — STRICT SINGLE-PASS APPROACH
# ============================================================

# ✅ KEY FIX: Prompt now forces EXACT one-per-line "TYPE = POSITION" output.
# No dimensions, no sizes, no markdown, no free text.
# This eliminates ALL parsing ambiguity and cuts output tokens in half.
ROOM_PROMPT = """You are analyzing a floor plan. List every labeled room.

OUTPUT FORMAT — strictly one line per room, nothing else:
ROOM_TYPE = GRID_CODE

ROOM_TYPE must be exactly one of:
BEDROOM, MASTER_BEDROOM, KITCHEN, LIVING, DINING, TOILET, C_TOILET, STORE, WASH, BALCONY, LOBBY, PARKING, DRAWING

GRID_CODE must be exactly one of:
NW  N  NE
W   C  E
SW  S  SE

NO dimensions. NO sizes. NO markdown. NO extra text. Just the list.

Example output:
KITCHEN = N
LIVING = NW
MASTER_BEDROOM = SE
TOILET = NE"""

def get_rooms_with_positions(image_pil: Image.Image) -> List[Dict]:
    """Single-pass room detection with strict parsing"""
    logger.info("🏠 Starting single-pass room detection...")
    
    raw = vlm_generate(image_pil, ROOM_PROMPT, max_new_tokens=150)
    logger.info(f"\n📊 VLM Raw Output:\n{raw}\n")
    
    rooms = parse_strict_format(raw)
    logger.info(f"✅ Completed: {len(rooms)} rooms detected")
    
    return rooms

def parse_strict_format(text: str) -> List[Dict]:
    """
    Parse the strict ROOM_TYPE = GRID_CODE format.
    Also handles fallback comma-separated format just in case VLM drifts.
    """
    logger.info("🔍 Parsing rooms...")

    # Extract only assistant response
    if 'assistant' in text.lower():
        idx  = text.lower().rfind('assistant')
        text = text[idx + len('assistant'):]

    # Clean markdown
    text = re.sub(r'\*+', '', text)

    # Canonical room type mapping
    room_type_map = {
        'master_bedroom': 'bedroom', 'master bedroom': 'bedroom', 'master': 'bedroom',
        'bedroom': 'bedroom',
        'kitchen': 'kitchen',
        'living room': 'living', 'living': 'living', 'hall': 'living',
        'dining room': 'living',  'dining': 'living',   # dining → living zone for vastu
        'lobby': 'living',
        'drawing room': 'drawing', 'drawing': 'drawing',
        'c_toilet': 'toilet', 'c toilet': 'toilet', 'c-toilet': 'toilet',
        'toilet': 'toilet', 'bathroom': 'toilet', 'wc': 'toilet',
        'wash area': 'wash_area', 'wash': 'wash_area',
        'store room': 'store', 'store': 'store', 'storage': 'store',
        'parking': 'parking', 'garage': 'parking',
        'balcony': 'lawn', 'lawn': 'lawn', 'garden': 'lawn',
    }

    # Valid grid codes
    valid_positions = {'NW','N','NE','W','C','E','SW','S','SE'}

    # Descriptive position fallback
    desc_position_map = {
        'northwest':'NW','northeast':'NE','southwest':'SW','southeast':'SE',
        'north':'N','south':'S','east':'E','west':'W','center':'C','centre':'C','middle':'C',
        'top-left':'NW','top left':'NW','top-right':'NE','top right':'NE',
        'bottom-left':'SW','bottom left':'SW','bottom-right':'SE','bottom right':'SE',
        'top':'N','bottom':'S','left':'W','right':'E',
    }

    rooms            = []
    seen             = set()
    priority_map     = {
        'bedroom':100,'kitchen':90,'living':85,'drawing':80,
        'toilet':70,'store':60,'parking':50,'lawn':40,'wash_area':35
    }

    def resolve_room(raw_name: str) -> Optional[str]:
        r = raw_name.strip().lower()
        for k, v in sorted(room_type_map.items(), key=lambda x: -len(x[0])):
            if k in r:
                return v
        return None

    def resolve_pos(raw_pos: str) -> Optional[str]:
        p = raw_pos.strip().upper()
        if p in valid_positions:
            return p
        p_lower = raw_pos.strip().lower()
        for k, v in sorted(desc_position_map.items(), key=lambda x: -len(x[0])):
            if k in p_lower:
                return v
        # Single letter fallback
        m = re.search(r'\b([NSEWC])\b', p)
        if m:
            letter = m.group(1)
            mapping = {'N':'N','S':'S','E':'E','W':'W','C':'C'}
            return mapping.get(letter)
        return None

    def add_room(room_type: str, visual_pos: str, raw_text: str):
        key = (room_type, visual_pos)
        if key in seen:
            return
        seen.add(key)
        rooms.append({
            'type':            room_type,
            'subtype':         None,
            'visual_position': visual_pos,
            'raw_text':        raw_text,
            '_priority':       priority_map.get(room_type, 0)
        })

    for line in text.split('\n'):
        line = line.strip()
        if not line or len(line) < 3:
            continue

        # ── Primary format: ROOM = POSITION
        if '=' in line:
            parts = line.split('=', 1)
            if len(parts) == 2:
                room_type  = resolve_room(parts[0])
                visual_pos = resolve_pos(parts[1])
                if room_type and visual_pos:
                    add_room(room_type, visual_pos, line)
                    continue

        # ── Fallback format: "Room Name: POSITION" or comma-separated
        # Split by comma first to handle "Living: NW, Kitchen: N, ..."
        segments = re.split(r',\s*', line)
        for seg in segments:
            seg = seg.strip()
            if ':' in seg:
                colon = seg.rfind(':')
                room_part = seg[:colon]
                pos_part  = seg[colon+1:]
                room_type  = resolve_room(room_part)
                visual_pos = resolve_pos(pos_part)
                if room_type and visual_pos:
                    add_room(room_type, visual_pos, seg)

    logger.info(f"\n✓ Extracted {len(rooms)} rooms:")
    for r in rooms:
        logger.info(f"   • {r['type']:12s} at {r['visual_position']}")
    return rooms

# ============================================================
# COMPASS CONVERSION
# ============================================================
def visual_to_compass(visual_pos: str, offset: int) -> str:
    """Convert visual position to compass direction"""
    if visual_pos == 'C':
        return 'C'
    angles     = {'N':0,'NE':45,'E':90,'SE':135,'S':180,'SW':225,'W':270,'NW':315}
    actual     = (angles[visual_pos] + offset) % 360
    directions = [(0,'N'),(45,'NE'),(90,'E'),(135,'SE'),(180,'S'),(225,'SW'),(270,'W'),(315,'NW')]
    return min(directions, key=lambda x: min(abs(actual-x[0]), 360-abs(actual-x[0])))[1]

# ============================================================
# BEDROOM CLASSIFICATION
# ============================================================
def label_bedrooms(rooms: List[Dict]) -> None:
    """Label bedrooms as master/guest based on Vastu priority"""
    logger.info("🛏️ Classifying bedrooms...")
    bedrooms = [r for r in rooms if r['type'] == 'bedroom']
    if not bedrooms:
        return
    if len(bedrooms) == 1:
        bedrooms[0]['bedroom_type'] = 'master'
        logger.info("   Single bedroom → master")
        return
    
    # Vastu priority for master bedroom: SW > S > W > NW > N > C > SE > E > NE
    priority  = {'SW':1,'S':2,'W':3,'NW':4,'N':5,'C':6,'SE':7,'E':8,'NE':9}
    sorted_br = sorted(bedrooms, key=lambda r: priority.get(r.get('visual_position','C'), 10))
    sorted_br[0]['bedroom_type'] = 'master'
    for r in sorted_br[1:]:
        r['bedroom_type'] = 'guest'
    
    logger.info("   Bedroom assignments:")
    for r in rooms:
        if r['type'] == 'bedroom':
            logger.info(f"      {r.get('bedroom_type','?'):6s} at {r['visual_position']}")

# ============================================================
# VASTU EVALUATION
# ============================================================
def evaluate_vastu(room: Dict) -> tuple:
    """Evaluate vastu compliance for a room"""
    rt = room['type']
    d  = room.get('compass_direction', 'N')

    if rt == 'bedroom':
        bt = room.get('bedroom_type', 'guest')
        if bt == 'master':
            if d == 'SW':          return "✅ COMPLIANT",    None,                                        "Master SW PERFECT"
            elif d in ['NE','SE']: return "❌ NON_COMPLIANT","Move to SW | Earthy colors",                f"Master {d} INAUSPICIOUS"
            else:                  return "⚠️ ACCEPTABLE",   None,                                        f"Master {d} OK, SW ideal"
        else:
            if d == 'NW':          return "✅ COMPLIANT",    None,                                        f"{bt.title()} NW PERFECT"
            elif d in ['NE','SE']: return "❌ NON_COMPLIANT","Light colors | Convert to study",           f"Bedroom {d} disrupts energy"
            else:                  return "⚠️ ACCEPTABLE",   None,                                        f"Bedroom {d} acceptable"

    elif rt == 'kitchen':
        if d == 'SE':              return "✅ COMPLIANT",    None,                                        "Kitchen SE IDEAL"
        elif d == 'NW':            return "✅ COMPLIANT",    None,                                        "Kitchen NW GOOD"
        elif d in ['SW','NE']:     return "❌ NON_COMPLIANT","Stove E facing | Ventilation",              f"Kitchen {d} VERY BAD"
        else:                      return "⚠️ ACCEPTABLE",   None,                                        f"Kitchen {d} workable"

    elif rt == 'toilet':
        if d in ['NW','W','S','SE']:   return "✅ COMPLIANT",    None,                                    f"Toilet {d} GOOD"
        elif d in ['NE','SW']:         return "❌ NON_COMPLIANT","Rock salt | Exhaust | Light colors",    f"Toilet {d} INAUSPICIOUS"
        else:                          return "⚠️ ACCEPTABLE",   None,                                    f"Toilet {d} OK"

    elif rt in ['living','hall']:
        if d in ['N','NE','E']:    return "✅ COMPLIANT",    None,                                        f"Living {d} EXCELLENT"
        elif d == 'C':             return "⚠️ ACCEPTABLE",   None,                                        "Center — keep uncluttered"
        elif d in ['SW','S']:      return "❌ NON_COMPLIANT","Heavy furniture SW | Light NE",             f"Living {d} blocks energy"
        else:                      return "⚠️ ACCEPTABLE",   None,                                        f"Living {d} workable"

    elif rt == 'store':
        if d in ['S','SW','W']:    return "✅ COMPLIANT",    None,                                        f"Store {d} IDEAL"
        elif d in ['NE','N','E']:  return "❌ NON_COMPLIANT","Move to SW | Keep NE clear",                f"Store {d} blocks energy"
        else:                      return "⚠️ ACCEPTABLE",   None,                                        f"Store {d} OK"

    elif rt == 'drawing':
        if d in ['N','NE','E','NW']:  return "✅ COMPLIANT",    None,                                     f"Drawing {d} GOOD"
        elif d in ['SW','S']:         return "❌ NON_COMPLIANT","Heavy furniture SW | Bright lighting",   f"Drawing {d} not ideal"
        else:                         return "⚠️ ACCEPTABLE",   None,                                     f"Drawing {d} OK"

    elif rt == 'parking':
        if d in ['NW','SE','E']:   return "✅ COMPLIANT",    None,                                        f"Parking {d} GOOD"
        elif d in ['NE','SW']:     return "❌ NON_COMPLIANT","Avoid NE/SW | Keep clean",                  f"Parking {d} not recommended"
        else:                      return "⚠️ ACCEPTABLE",   None,                                        f"Parking {d} acceptable"

    elif rt == 'lawn':
        if d in ['N','NE','E']:    return "✅ COMPLIANT",    None,                                        f"Lawn {d} EXCELLENT"
        elif d == 'SW':            return "❌ NON_COMPLIANT","Heavy trees SW | Tulsi in NE",              f"Lawn {d} needs balancing"
        else:                      return "⚠️ ACCEPTABLE",   None,                                        f"Lawn {d} OK"

    elif rt == 'wash_area':
        if d in ['N','NE','E','NW']:  return "✅ COMPLIANT",    None,                                     f"Wash area {d} GOOD"
        else:                         return "⚠️ ACCEPTABLE",   None,                                     f"Wash area {d} OK"

    else:
        return "⚠️ ACCEPTABLE", None, f"{rt.title()} {d} OK"

# ============================================================
# LIFESPAN: LOAD MODEL ON STARTUP
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup, unload on shutdown"""
    global model, tokenizer

    logger.info("🚀 Starting VastuGPT API (Optimized)...")
    logger.info("⚠️  First run will download ~7GB model (cached after that)")

    try:
        # Load VLM using unsloth (optimized for Colab)
        logger.info("Loading Vision Language Model with Unsloth...")
        model, tokenizer = FastVisionModel.from_pretrained(
            "sabaridsnfuji/FloorPlanVisionAIAdaptor",
            load_in_4bit=True,
            device_map="cuda:0" if torch.cuda.is_available() else "cpu",
            max_seq_length=MAX_SEQ_LENGTH,
            attn_implementation="eager",   # kills flex_attention completely
        )
        FastVisionModel.for_inference(model)
        model.eval()
        for param in model.parameters():
            param.requires_grad = False
        logger.info("✅ VLM model loaded — 4bit, eager attention")
        log_gpu_memory("After model load")

    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        raise RuntimeError(f"Model loading failed: {e}")

    yield

    # Cleanup on shutdown
    logger.info("Shutting down...")
    if model:
        del model
        del tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

# ============================================================
# FASTAPI APP
# ============================================================
app = FastAPI(
    title="VastuGPT API - Optimized Single-Pass Pipeline",
    description="AI-powered Vastu Shastra analysis with strict parsing and memory optimization",
    version="3.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/", response_model=Dict)
async def root():
    """Root endpoint"""
    return {
        "message": "VastuGPT API - Optimized Single-Pass Pipeline",
        "version": "3.0.0",
        "pipeline": "Single-pass room detection with strict parsing",
        "improvements": [
            "Memory-optimized VLM inference",
            "Strict one-line parsing format",
            "Reduced token usage",
            "Faster analysis"
        ],
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze (POST)"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "gpu_available": torch.cuda.is_available()
    }


@app.post("/analyze", response_model=VastuAnalysisResponse)
async def analyze_floor_plan(
    image: UploadFile = File(..., description="Floor plan image file"),
    house_facing: Optional[str] = Form(None, description="Direction house faces: N, NE, E, SE, S, SW, W, NW (optional if compass detected)"),
    door_position: Optional[str] = Form(None, description="Door position on image: N, NE, E, SE, S, SW, W, NW (optional if compass detected)")
):
    """
    Analyze floor plan for Vastu compliance using optimized single-pass pipeline

    **Parameters:**
    - **image**: Floor plan image (JPG, PNG)
    - **house_facing**: Direction the house faces (optional - will try compass detection first)
    - **door_position**: Where the main door appears on the IMAGE (optional - will try compass detection first)

    **Returns:**
    - Vastu score (0-100)
    - Room-wise analysis with strict parsing
    - Remedies for non-compliant rooms
    """
    logger.info("="*70)
    logger.info("🚀 NEW ANALYSIS REQUEST RECEIVED")
    logger.info("="*70)

    if not model or not tokenizer:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Read image
        logger.info(f"📸 Reading uploaded image: {image.filename}")
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        image_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image_cv is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        image_pil = Image.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))
        logger.info(f"📐 Original: {image_cv.shape[1]}x{image_cv.shape[0]} px")
        
        # Preprocess image
        image_pil = preprocess_image_for_vlm(image_pil)
        logger.info(f"📐 VLM Input: {image_pil.size[0]}x{image_pil.size[1]} px\n")

        # STEP 1: Detect orientation (compass or manual)
        logger.info("="*70)
        logger.info("STEP 1: ORIENTATION")
        logger.info("="*70)
        compass_map = get_compass_from_image(image_pil)

        if compass_map and len(compass_map) >= 2:
            offset = calculate_offset_from_compass(compass_map)
            if offset is not None:
                logger.info(f"✓ Compass detected! North at {compass_map['N']}, offset: {offset}°")
                facing_display = "Detected from compass"
                door_display = "N/A"
            else:
                if not house_facing or not door_position:
                    raise HTTPException(status_code=400, detail="Compass unclear. Please provide house_facing and door_position")
                offset = calculate_offset(house_facing, door_position)
                facing_display = house_facing.upper()
                door_display = door_position.upper()
        else:
            if not house_facing or not door_position:
                raise HTTPException(status_code=400, detail="No compass found. Please provide house_facing and door_position")

            valid_directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
            house_facing = house_facing.upper()
            door_position = door_position.upper()

            if house_facing not in valid_directions:
                raise HTTPException(status_code=400, detail=f"Invalid house_facing. Must be one of: {valid_directions}")

            if door_position not in valid_directions:
                raise HTTPException(status_code=400, detail=f"Invalid door_position. Must be one of: {valid_directions}")

            offset = calculate_offset(house_facing, door_position)
            facing_display = house_facing
            door_display = door_position

        logger.info(f"✓ facing={facing_display}, door={door_display}, offset={offset}°")

        # STEP 2: Single-pass room detection
        logger.info("="*70)
        logger.info("STEP 2: ROOM DETECTION (single pass)")
        logger.info("="*70)
        rooms = get_rooms_with_positions(image_pil)

        if not rooms:
            raise HTTPException(status_code=422, detail="No rooms detected in floor plan")

        # STEP 3: Convert to compass directions
        logger.info("="*70)
        logger.info("STEP 3: COMPASS CONVERSION")
        logger.info("="*70)
        for room in rooms:
            room['compass_direction'] = visual_to_compass(room['visual_position'], offset)
            logger.info(f"  {room['type']:14s}: {room['visual_position']:2s} → {room['compass_direction']:2s}")

        # Label bedrooms
        label_bedrooms(rooms)

        # STEP 4: Evaluate vastu
        logger.info("="*70)
        logger.info("STEP 4: VASTU EVALUATION")
        logger.info("="*70)
        for i, room in enumerate(rooms):
            room['id'] = i + 1
            status, remedy, reason = evaluate_vastu(room)
            room['status'] = status
            room['remedy'] = remedy
            room['reason'] = reason

        # Calculate summary
        compliant = sum(1 for r in rooms if '✅' in r.get('status', ''))
        non_compliant = sum(1 for r in rooms if '❌' in r.get('status', ''))
        acceptable = len(rooms) - compliant - non_compliant

        # Calculate score
        total_rooms = len(rooms)
        if total_rooms > 0:
            score = int(((compliant * 100) + (acceptable * 60) + (non_compliant * 20)) / total_rooms)
        else:
            score = 0
        score = min(100, max(0, score))

        # Build response
        room_analyses = [
            RoomAnalysis(
                id=r['id'],
                type=r['type'],
                subtype=r.get('bedroom_type'),
                visual_position=r['visual_position'],
                compass_direction=r['compass_direction'],
                status=r['status'],
                reason=r['reason'],
                remedy=r['remedy']
            )
            for r in rooms
        ]

        message = f"Analysis complete (optimized single-pass): {compliant} compliant, {non_compliant} critical issues, {acceptable} acceptable"

        logger.info("="*70)
        logger.info(f"✅ ANALYSIS COMPLETE - Score: {score}/100")
        logger.info(f"📊 Summary: {compliant} compliant, {non_compliant} non-compliant, {acceptable} acceptable")
        logger.info("="*70)

        return VastuAnalysisResponse(
            score=score,
            summary={
                "compliant": compliant,
                "non_compliant": non_compliant,
                "acceptable": acceptable,
                "total_rooms": total_rooms
            },
            orientation={
                "house_facing": facing_display,
                "door_position": door_display,
                "north_offset": offset
            },
            rooms=room_analyses,
            message=message
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ============================================================
# RUN SERVER
# ============================================================
if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting server on 0.0.0.0:8000")
    uvicorn.run(
        "updated_api:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
