"""
VastuGPT FastAPI Server
Floor Plan Vastu Analysis using Vision Language Model
"""
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
from transformers import MllamaForConditionalGeneration, AutoProcessor, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# GLOBAL MODEL VARIABLES
# ============================================================
model = None
processor = None
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
# LIFESPAN: LOAD MODEL ON STARTUP
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup, unload on shutdown"""
    global model, processor, tokenizer
    
    logger.info("🚀 Starting VastuGPT API...")
    logger.info("⚠️  First run will download ~7GB model (cached after that)")
    
    try:
        # Load processor and tokenizer
        logger.info("Loading processor and tokenizer...")
        processor = AutoProcessor.from_pretrained(
            "sabaridsnfuji/FloorPlanVisionAIAdaptor",
            trust_remote_code=True
        )
        tokenizer = AutoTokenizer.from_pretrained(
            "sabaridsnfuji/FloorPlanVisionAIAdaptor",
            trust_remote_code=True
        )
        
        # Load VLM (Llama 3.2 Vision with LoRA adapter)
        logger.info("Loading Vision Language Model...")
        base_model_id = "unsloth/Llama-3.2-11B-Vision-Instruct"
        adapter_id = "sabaridsnfuji/FloorPlanVisionAIAdaptor"
        
        # 4-bit quantization config for low VRAM
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True
        )
        
        # Load base model with 4-bit quantization + auto device map (GPU + CPU offload)
        logger.info(f"Loading base model: {base_model_id} (4-bit quantized)")
        model = MllamaForConditionalGeneration.from_pretrained(
            base_model_id,
            quantization_config=bnb_config,
            device_map="auto",  # Auto offload to CPU if GPU full
            low_cpu_mem_usage=True,
            max_memory={0: "3.5GiB", "cpu": "16GiB"}  # Leave some GPU headroom
        )
        
        # Load and apply LoRA adapter
        logger.info(f"Loading LoRA adapter: {adapter_id}")
        model = PeftModel.from_pretrained(model, adapter_id)
        model.eval()
        logger.info("✅ VLM model loaded successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        raise RuntimeError(f"Model loading failed: {e}")
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down...")
    if model:
        del model
        del processor
        del tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

# ============================================================
# FASTAPI APP
# ============================================================
app = FastAPI(
    title="VastuGPT API",
    description="AI-powered Vastu Shastra analysis for floor plans",
    version="1.0.0",
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
# HELPER FUNCTIONS (FROM app.py)
# ============================================================

def get_compass_from_image(image_pil: Image.Image) -> Optional[Dict]:
    """Try to detect compass rose from image"""
    prompt = """Look at this floor plan image carefully.

Is there a compass rose showing N/S/E/W directions?

If YES:
- Tell me where each direction (N, E, S, W) is located on the image
- Format: "N is at [position], E is at [position], S is at [position], W is at [position]"
- Positions: top, bottom, left, right, top-left, top-right, bottom-left, bottom-right

If NO compass visible:
- Just write "NO COMPASS"

Example: "N is at bottom-left, E is at top-right, S is at top-right, W is at bottom" """

    inputs = processor(text=prompt, images=image_pil, return_tensors="pt")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=100, do_sample=False)

    text = processor.batch_decode(output, skip_special_tokens=True)[0]
    logger.info(f"🧭 Compass Detection: {text[:200]}")

    # Parse compass positions
    compass_map = {}
    text_lower = text.lower()

    if "no compass" in text_lower:
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
        return compass_map

    return None


def calculate_offset(house_facing: str, door_position: str) -> int:
    """Calculate north offset from house facing and door position"""
    angles = {'N': 0, 'NE': 45, 'E': 90, 'SE': 135, 'S': 180, 'SW': 225, 'W': 270, 'NW': 315}
    
    facing_angle = angles.get(house_facing.upper(), 0)
    door_angle = angles.get(door_position.upper(), 0)
    
    offset = (facing_angle - door_angle) % 360
    return offset


def get_rooms_with_positions(image_pil: Image.Image) -> tuple:
    """Get room positions using VLM"""
    
    # PHASE 1: Count rooms
    count_prompt = """Count the EXACT number of each room type visible in this floor plan.
Look at the TEXT LABELS written inside each room.

Answer in this EXACT format:
Bedroom: [number]
Kitchen: [number]
Living: [number]
Drawing: [number]
Toilet: [number]
Store: [number]
Parking: [number]
Lawn: [number]
Wash Area: [number]

COUNT ONLY ROOMS WITH VISIBLE LABELS."""

    inputs = processor(text=count_prompt, images=image_pil, return_tensors="pt")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=200, do_sample=False)

    count_text = processor.batch_decode(output, skip_special_tokens=True)[0]
    logger.info(f"📊 Room Count Response: {count_text[:300]}")

    # Parse counts
    expected_counts = {}
    patterns = {
        'bedroom': r'bedroom[s]?\s*[:\-=]\s*(\d+)',
        'kitchen': r'kitchen[s]?\s*[:\-=]\s*(\d+)',
        'living': r'living\s*(?:room)?\s*[:\-=]\s*(\d+)',
        'drawing': r'drawing\s*(?:room)?\s*[:\-=]\s*(\d+)',
        'toilet': r'toilet[s]?\s*[:\-=]\s*(\d+)',
        'store': r'store\s*(?:room)?\s*[:\-=]\s*(\d+)',
        'parking': r'parking\s*[:\-=]\s*(\d+)',
        'lawn': r'lawn[s]?\s*[:\-=]\s*(\d+)',
        'wash_area': r'wash\s*area\s*[:\-=]\s*(\d+)'
    }
    
    if 'assistant' in count_text.lower():
        idx = count_text.lower().rfind('assistant')
        count_text = count_text[idx + len('assistant'):]
    
    text_lower = count_text.lower()
    for room_type, pattern in patterns.items():
        match = re.search(pattern, text_lower)
        if match:
            expected_counts[room_type] = int(match.group(1))
    
    logger.info(f"Expected counts: {expected_counts}")

    # PHASE 2: Get positions
    room_list_lines = []
    for room_type, count in expected_counts.items():
        display_name = room_type.upper().replace('_', ' ')
        if count == 1:
            room_list_lines.append(f"{display_name} = [position]")
        else:
            for i in range(1, count + 1):
                room_list_lines.append(f"{display_name} {i} = [position]")

    room_list_str = '\n'.join(room_list_lines)

    position_prompt = f"""Look at this floor plan. Map each TEXT LABELED room to its grid position.

GRID SYSTEM (9 zones):
┌─────────┬─────────┬─────────┐
│ NW      │ N       │ NE      │
├─────────┼─────────┼─────────┤
│ W       │ C       │ E       │
├─────────┼─────────┼─────────┤
│ SW      │ S       │ SE      │
└─────────┴─────────┴─────────┘

RULES:
1. Use ONLY these codes: NW, N, NE, W, C, E, SW, S, SE
2. Each room gets ONE primary position (where MOST of its area is)

FORMAT: ROOM_NAME = POSITION

Expected rooms:
{room_list_str}

Your response (exactly one line per room):"""

    messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": position_prompt}]}]
    input_text = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
    inputs = tokenizer(images=[image_pil], text=input_text, add_special_tokens=False, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=600, do_sample=False)

    text = tokenizer.decode(output[0], skip_special_tokens=True)
    logger.info(f"📝 Room Positions Response: {text[:500]}")

    # Parse rooms
    rooms = parse_room_list(text, expected_counts)
    
    return rooms, expected_counts


def parse_room_list(text: str, expected_counts: Dict) -> List[Dict]:
    """Parse room list from VLM output"""
    rooms = []
    room_type_counts = {}

    if 'assistant' in text.lower():
        idx = text.lower().rfind('assistant')
        text = text[idx + len('assistant'):]

    lines = text.split('\n')

    position_map = {
        'n': 'N', 's': 'S', 'e': 'E', 'w': 'W', 'c': 'C',
        'nw': 'NW', 'ne': 'NE', 'sw': 'SW', 'se': 'SE',
        'northwest': 'NW', 'northeast': 'NE', 'southwest': 'SW', 'southeast': 'SE',
        'top-left': 'NW', 'top left': 'NW', 'upper-left': 'NW',
        'top-right': 'NE', 'top right': 'NE', 'upper-right': 'NE',
        'bottom-left': 'SW', 'bottom left': 'SW', 'lower-left': 'SW',
        'bottom-right': 'SE', 'bottom right': 'SE', 'lower-right': 'SE',
        'top': 'N', 'upper': 'N', 'north': 'N',
        'bottom': 'S', 'lower': 'S', 'south': 'S',
        'left': 'W', 'west': 'W',
        'right': 'E', 'east': 'E',
        'center': 'C', 'centre': 'C', 'middle': 'C'
    }

    room_type_map = {
        'bedroom': 'bedroom', 'bed room': 'bedroom', 'bed': 'bedroom',
        'master': 'bedroom', 'master bedroom': 'bedroom',
        'kitchen': 'kitchen',
        'living': 'living', 'living room': 'living', 'hall': 'living',
        'drawing': 'drawing', 'drawing room': 'drawing',
        'toilet': 'toilet', 'bathroom': 'toilet', 'wc': 'toilet',
        'wash area': 'wash_area', 'wash': 'wash_area',
        'store': 'store', 'storage': 'store',
        'parking': 'parking', 'garage': 'parking',
        'lawn': 'lawn', 'garden': 'lawn'
    }

    seen = set()

    for line in lines:
        line_lower = line.lower().strip()

        if len(line_lower) < 3:
            continue

        if '=' not in line_lower and ' at ' not in line_lower:
            continue

        # Extract room type
        room_type = None
        for keyword, rt in room_type_map.items():
            if keyword in line_lower:
                room_type = rt
                break

        if not room_type:
            continue

        # Extract position
        visual_pos = None
        
        # Try single letter pattern
        single_letter_pattern = r'[=\-]\s*([NSEWC])\s*$|[=\-]\s*([NSEWC])\s+'
        match = re.search(single_letter_pattern, line_lower.upper())
        if match:
            letter = (match.group(1) or match.group(2)).strip()
            visual_pos = position_map.get(letter.lower())

        # Try compound positions
        if not visual_pos:
            for pos_keyword, pos_code in sorted(position_map.items(), key=lambda x: -len(x[0])):
                if pos_keyword in line_lower:
                    visual_pos = pos_code
                    break

        if not visual_pos:
            continue

        # Check counts
        max_allowed = expected_counts.get(room_type, 10)
        current_count = room_type_counts.get(room_type, 0)

        if current_count >= max_allowed:
            continue

        combo_key = (room_type, visual_pos)
        if combo_key in seen:
            continue
        seen.add(combo_key)

        room_type_counts[room_type] = current_count + 1
        rooms.append({
            'type': room_type,
            'visual_position': visual_pos,
            'raw_text': line.strip()
        })

    logger.info(f"Parsed {len(rooms)} rooms: {room_type_counts}")
    return rooms


def visual_to_compass(visual_pos: str, offset: int) -> str:
    """Convert visual position to compass direction"""
    if visual_pos == 'C':
        return 'C'

    angles = {'N': 0, 'NE': 45, 'E': 90, 'SE': 135, 'S': 180, 'SW': 225, 'W': 270, 'NW': 315}

    visual_angle = angles[visual_pos]
    actual_angle = (visual_angle + offset) % 360

    # Round to nearest 45°
    directions = [(0, 'N'), (45, 'NE'), (90, 'E'), (135, 'SE'),
                  (180, 'S'), (225, 'SW'), (270, 'W'), (315, 'NW')]

    min_diff = 360
    result = 'N'

    for angle, direction in directions:
        diff = min(abs(actual_angle - angle), abs(actual_angle - angle + 360), abs(actual_angle - angle - 360))
        if diff < min_diff:
            min_diff = diff
            result = direction

    return result


def label_bedrooms(rooms: List[Dict]) -> None:
    """Label bedrooms as master/guest"""
    bedrooms = [r for r in rooms if r['type'] == 'bedroom']

    if not bedrooms:
        return

    if len(bedrooms) == 1:
        bedrooms[0]['bedroom_type'] = 'master'
        return

    # Vastu priority for master: SW > S > W
    master_priority = {'SW': 1, 'S': 2, 'W': 3, 'NW': 4, 'N': 5, 'C': 6, 'SE': 7, 'E': 8, 'NE': 9}
    
    bedrooms_sorted = sorted(bedrooms, key=lambda r: master_priority.get(r.get('visual_position', 'C'), 10))

    for i, r in enumerate(bedrooms_sorted):
        r['bedroom_type'] = 'master' if i == 0 else 'guest'


def evaluate_vastu(room: Dict) -> tuple:
    """Evaluate vastu compliance for a room"""
    rt = room['type']
    d = room.get('compass_direction', 'N')

    if rt == 'bedroom':
        bt = room.get('bedroom_type', 'guest')
        if bt == 'master':
            if d == 'SW':
                return "✅ COMPLIANT", None, "Master bedroom SW PERFECT - stability/prosperity"
            elif d in ['NE', 'SE']:
                return "❌ NON_COMPLIANT", "Move to SW | Heavy furniture SW corner | Earthy colors", f"Master {d} INAUSPICIOUS"
            else:
                return "⚠️ ACCEPTABLE", None, f"Master {d} OK, SW ideal"
        else:
            if d == 'NW':
                return "✅ COMPLIANT", None, f"Guest bedroom NW PERFECT"
            elif d in ['NE', 'SE']:
                return "❌ NON_COMPLIANT", "Light colors | Convert to study", f"Bedroom {d} disrupts energy"
            else:
                return "⚠️ ACCEPTABLE", None, f"Bedroom {d} acceptable"

    elif rt == 'kitchen':
        if d == 'SE':
            return "✅ COMPLIANT", None, "Kitchen SE IDEAL - Agni element"
        elif d == 'NW':
            return "✅ COMPLIANT", None, "Kitchen NW GOOD"
        elif d in ['SW', 'NE']:
            return "❌ NON_COMPLIANT", "Stove E facing | Fire colors | Ventilation", f"Kitchen {d} VERY BAD"
        else:
            return "⚠️ ACCEPTABLE", None, f"Kitchen {d} workable"

    elif rt == 'toilet':
        if d in ['NW', 'W', 'S', 'SE']:
            return "✅ COMPLIANT", None, f"Toilet {d} GOOD"
        elif d in ['NE', 'SW']:
            return "❌ NON_COMPLIANT", "Door closed | Exhaust | Rock salt | Light colors", f"Toilet {d} HIGHLY INAUSPICIOUS"
        else:
            return "⚠️ ACCEPTABLE", None, f"Toilet {d} OK"

    elif rt in ['living', 'hall']:
        if d in ['N', 'NE', 'E']:
            return "✅ COMPLIANT", None, f"Living {d} EXCELLENT"
        elif d == 'C':
            return "⚠️ ACCEPTABLE", None, "Center OK - keep uncluttered"
        elif d in ['SW', 'S']:
            return "❌ NON_COMPLIANT", "Heavy furniture SW | Light NE", f"Living {d} blocks energy"
        else:
            return "⚠️ ACCEPTABLE", None, f"Living {d} workable"

    elif rt == 'store':
        if d in ['S', 'SW', 'W']:
            return "✅ COMPLIANT", None, f"Store {d} IDEAL"
        elif d in ['NE', 'N', 'E']:
            return "❌ NON_COMPLIANT", "Move to SW | Keep NE clear", f"Store {d} blocks energy"
        else:
            return "⚠️ ACCEPTABLE", None, f"Store {d} OK"

    elif rt == 'drawing':
        if d in ['N', 'NE', 'E', 'NW']:
            return "✅ COMPLIANT", None, f"Drawing {d} GOOD for guests"
        elif d in ['SW', 'S']:
            return "❌ NON_COMPLIANT", "Heavy furniture SW | Bright lighting", f"Drawing {d} not ideal"
        else:
            return "⚠️ ACCEPTABLE", None, f"Drawing {d} OK"

    elif rt == 'parking':
        if d in ['NW', 'SE', 'E']:
            return "✅ COMPLIANT", None, f"Parking {d} GOOD"
        elif d in ['NE', 'SW']:
            return "❌ NON_COMPLIANT", "Avoid NE/SW parking | Keep clean", f"Parking {d} not recommended"
        else:
            return "⚠️ ACCEPTABLE", None, f"Parking {d} acceptable"

    elif rt == 'lawn':
        if d in ['N', 'NE', 'E']:
            return "✅ COMPLIANT", None, f"Lawn {d} EXCELLENT - positive energy"
        elif d in ['SW']:
            return "❌ NON_COMPLIANT", "Plant heavy trees SW | Tulsi in NE", f"Lawn {d} needs balancing"
        else:
            return "⚠️ ACCEPTABLE", None, f"Lawn {d} OK"

    else:
        return "⚠️ ACCEPTABLE", None, f"{rt.title()} {d} placement OK"


# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/", response_model=Dict)
async def root():
    """Root endpoint"""
    return {
        "message": "VastuGPT API",
        "version": "1.0.0",
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
    house_facing: str = Form(..., description="Direction house faces: N, NE, E, SE, S, SW, W, NW"),
    door_position: str = Form(..., description="Door position on image: N, NE, E, SE, S, SW, W, NW")
):
    
    
    if not model or not tokenizer:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Validate inputs
    valid_directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    house_facing = house_facing.upper()
    door_position = door_position.upper()
    
    if house_facing not in valid_directions:
        raise HTTPException(status_code=400, detail=f"Invalid house_facing. Must be one of: {valid_directions}")
    
    if door_position not in valid_directions:
        raise HTTPException(status_code=400, detail=f"Invalid door_position. Must be one of: {valid_directions}")
    
    try:
        # Read image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        image_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image_cv is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        image_pil = Image.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))
        logger.info(f"📐 Image: {image_cv.shape[1]}x{image_cv.shape[0]} px")
        
        # Calculate offset
        offset = calculate_offset(house_facing, door_position)
        logger.info(f"🧭 House facing: {house_facing}, Door: {door_position}, Offset: {offset}°")
        
        # Get rooms
        logger.info("🔍 Identifying rooms...")
        rooms, expected_counts = get_rooms_with_positions(image_pil)
        
        if not rooms:
            raise HTTPException(status_code=422, detail="No rooms detected in floor plan")
        
        # Convert to compass directions
        logger.info("🧭 Converting to compass directions...")
        for room in rooms:
            visual = room['visual_position']
            compass = visual_to_compass(visual, offset)
            room['compass_direction'] = compass
        
        # Label bedrooms
        label_bedrooms(rooms)
        
        # Evaluate vastu
        logger.info("📊 Evaluating Vastu compliance...")
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
        
        message = f"Analysis complete: {compliant} compliant, {non_compliant} critical issues, {acceptable} acceptable"
        
        return VastuAnalysisResponse(
            score=score,
            summary={
                "compliant": compliant,
                "non_compliant": non_compliant,
                "acceptable": acceptable,
                "total_rooms": total_rooms
            },
            orientation={
                "house_facing": house_facing,
                "door_position": door_position,
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
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
