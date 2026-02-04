"""
VastuGPT FastAPI Server - Complete Pipeline
Floor Plan Vastu Analysis using Vision Language Model (Unsloth)
Based on app.py with full 3-phase room detection and verification
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
from unsloth import FastVisionModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURATION
# ============================================================
VASTU_RULES_PATH = "vastu_rules_home.json"

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
# LIFESPAN: LOAD MODEL ON STARTUP
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup, unload on shutdown"""
    global model, tokenizer

    logger.info("🚀 Starting VastuGPT API...")
    logger.info("⚠️  First run will download ~7GB model (cached after that)")

    try:
        # Load VLM using unsloth (optimized for Colab)
        logger.info("Loading Vision Language Model with Unsloth...")
        model, tokenizer = FastVisionModel.from_pretrained(
            "sabaridsnfuji/FloorPlanVisionAIAdaptor",
            load_in_4bit=True,
            device_map="cuda" if torch.cuda.is_available() else "cpu"
        )
        FastVisionModel.for_inference(model)
        logger.info("✅ VLM model loaded successfully")

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
    title="VastuGPT API - Complete Pipeline",
    description="AI-powered Vastu Shastra analysis for floor plans with 3-phase room detection",
    version="2.0.0",
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
    logger.info("🧭 [MODULE: get_compass_from_image] Starting compass detection...")
    prompt = """Look at this floor plan image carefully.

Is there a compass rose showing N/S/E/W directions?

If YES:
- Tell me where each direction (N, E, S, W) is located on the image
- Format: "N is at [position], E is at [position], S is at [position], W is at [position]"
- Positions: top, bottom, left, right, top-left, top-right, bottom-left, bottom-right

If NO compass visible:
- Just write "NO COMPASS"

Example: "N is at bottom-left, E is at top-right, S is at top-right, W is at bottom" """

    messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": prompt}]}]
    input_text = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
    inputs = tokenizer(images=[image_pil], text=input_text, add_special_tokens=False, return_tensors="pt")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=100, do_sample=False)

    text = tokenizer.decode(output[0], skip_special_tokens=True)
    logger.info(f"🧭 Compass Detection: {text[:200]}")
    logger.info("🔍 [MODULE: get_compass_from_image] Parsing compass positions from VLM output...")

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
        logger.info(f"✅ [MODULE: get_compass_from_image] Compass found: {compass_map}")
        return compass_map

    logger.info("⚠️ [MODULE: get_compass_from_image] No compass detected in image")
    return None


def calculate_offset_from_compass(compass_map):
    """Calculate rotation offset from compass readings"""
    logger.info(f"📐 [MODULE: calculate_offset_from_compass] Calculating offset from compass: {compass_map}")
    if 'N' not in compass_map:
        logger.warning("⚠️ [MODULE: calculate_offset_from_compass] North direction not found in compass map")
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
    logger.info(f"✅ [MODULE: calculate_offset_from_compass] Calculated offset: {offset}° (North at {north_visual})")

    return offset


def calculate_offset(house_facing: str, door_position: str) -> int:
    """Calculate north offset from house facing and door position"""
    logger.info(f"📐 [MODULE: calculate_offset] Calculating offset from manual input - Facing: {house_facing}, Door: {door_position}")
    angles = {'N': 0, 'NE': 45, 'E': 90, 'SE': 135, 'S': 180, 'SW': 225, 'W': 270, 'NW': 315}

    facing_angle = angles.get(house_facing.upper(), 0)
    door_angle = angles.get(door_position.upper(), 0)

    offset = (facing_angle - door_angle) % 360
    logger.info(f"✅ [MODULE: calculate_offset] Calculated offset: {offset}°")
    return offset


def get_rooms_with_positions(image_pil: Image.Image) -> tuple:
    """Use VLM with 2-phase detection for accurate room positioning"""
    logger.info("🏠 [MODULE: get_rooms_with_positions] Starting 2-phase room detection...")

    # PHASE 1: Count rooms
    logger.info("📊 [MODULE: get_rooms_with_positions] PHASE 1: Counting rooms...")
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

    messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": count_prompt}]}]
    input_text = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
    inputs = tokenizer(images=[image_pil], text=input_text, add_special_tokens=False, return_tensors="pt")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=200, do_sample=False)

    count_text = tokenizer.decode(output[0], skip_special_tokens=True)
    logger.info(f"📊 Room Count: {count_text[:300]}")

    # Parse expected counts
    expected_counts = parse_room_counts(count_text)
    logger.info(f"Expected counts: {expected_counts}")

    # PHASE 2: Get positions
    logger.info("📍 [MODULE: get_rooms_with_positions] PHASE 2: Detecting room positions...")
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
3. If room spans zones, pick zone with largest area overlap
4. Avoid assigning multiple rooms to same position if possible
5. Use dimensions from labels to distinguish rooms with same name

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
    logger.info(f"📝 Room Positions: {text[:500]}")

    rooms = parse_room_list_v2(text, expected_counts)
    logger.info(f"✅ [MODULE: get_rooms_with_positions] Completed: {len(rooms)} rooms detected")

    return rooms, expected_counts


def parse_room_counts(text):
    """Parse room counts from VLM output"""
    logger.info("🔢 [MODULE: parse_room_counts] Parsing room counts from VLM response...")
    counts = {}

    # Extract only assistant response
    if 'assistant' in text.lower():
        idx = text.lower().rfind('assistant')
        text = text[idx + len('assistant'):]

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

    text_lower = text.lower()
    for room_type, pattern in patterns.items():
        match = re.search(pattern, text_lower)
        if match:
            counts[room_type] = int(match.group(1))

    logger.info(f"✅ [MODULE: parse_room_counts] Parsed counts: {counts}")
    return counts


def parse_room_list_v2(text, expected_counts):
    """Parse room list with validation against expected counts"""
    logger.info("🔍 Parsing rooms with validation...")

    rooms = []
    room_type_counts = {}

    # Extract only assistant response
    if 'assistant' in text.lower():
        idx = text.lower().rfind('assistant')
        text = text[idx + len('assistant'):]

    lines = text.split('\n')

    # Position mapping
    position_map = {
        'n': 'N', 's': 'S', 'e': 'E', 'w': 'W', 'c': 'C',
        'nw corner': 'NW', 'nw': 'NW', 'northwest': 'NW',
        'ne corner': 'NE', 'ne': 'NE', 'northeast': 'NE',
        'sw corner': 'SW', 'sw': 'SW', 'southwest': 'SW',
        'se corner': 'SE', 'se': 'SE', 'southeast': 'SE',
        'top-left': 'NW', 'top left': 'NW', 'topleft': 'NW', 'upper-left': 'NW',
        'top-right': 'NE', 'top right': 'NE', 'topright': 'NE', 'upper-right': 'NE',
        'bot-left': 'SW', 'bottom-left': 'SW', 'bottom left': 'SW', 'lower-left': 'SW',
        'bot-right': 'SE', 'bottom-right': 'SE', 'bottom right': 'SE', 'lower-right': 'SE',
        'top': 'N', 'upper': 'N', 'north': 'N',
        'bottom': 'S', 'lower': 'S', 'south': 'S', 'bot': 'S',
        'left': 'W', 'west': 'W',
        'right': 'E', 'east': 'E',
        'center': 'C', 'centre': 'C', 'middle': 'C', 'central': 'C'
    }

    # Room type normalization
    room_type_map = {
        'bedroom': 'bedroom', 'bed room': 'bedroom', 'bed': 'bedroom',
        'master': 'bedroom', 'master bedroom': 'bedroom',
        'kitchen': 'kitchen',
        'living': 'living', 'living room': 'living', 'hall': 'living',
        'drawing': 'drawing', 'drawing room': 'drawing',
        'toilet': 'toilet', 'bathroom': 'toilet', 'wc': 'toilet', 'bath': 'toilet',
        'wash area': 'wash_area', 'wash': 'wash_area', 'washarea': 'wash_area',
        'store': 'store', 'storage': 'store', 'store room': 'store',
        'parking': 'parking', 'car park': 'parking', 'garage': 'parking',
        'lawn': 'lawn', 'garden': 'lawn'
    }

    seen_combinations = set()

    for line in lines:
        line_lower = line.lower().strip()

        if len(line_lower) < 3:
            continue

        # Skip header/instruction lines
        if any(skip in line_lower for skip in ['format', 'example', 'important', 'list', 'grid', '┌', '├', '└', '│']):
            continue

        # Must have '=' or 'at' or '-' to be a valid mapping
        if '=' not in line_lower and ' at ' not in line_lower and ' - ' not in line_lower:
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

        # Check against expected counts
        max_allowed = expected_counts.get(room_type, 10)
        current_count = room_type_counts.get(room_type, 0)

        if current_count >= max_allowed:
            continue

        # Deduplication
        combo_key = (room_type, visual_pos)
        if combo_key in seen_combinations:
            continue
        seen_combinations.add(combo_key)

        # Add room with priority score
        priority_map = {
            'bedroom': 100, 'kitchen': 90, 'living': 85, 'drawing': 80,
            'toilet': 70, 'store': 60, 'parking': 50, 'lawn': 40, 'wash_area': 35
        }

        room_type_counts[room_type] = current_count + 1
        rooms.append({
            'type': room_type,
            'subtype': None,
            'visual_position': visual_pos,
            'raw_text': line.strip(),
            '_priority': priority_map.get(room_type, 0)
        })

    logger.info(f"✓ Extracted {len(rooms)} rooms: {room_type_counts}")
    return rooms


def verify_rooms_with_grid(image_pil: Image.Image, rooms: List[Dict], expected_counts: Dict) -> List[Dict]:
    """PHASE 3: Verify and correct room positions"""
    logger.info("🔍 [MODULE: verify_rooms_with_grid] Phase 3: Verifying room positions with grid check...")
    logger.info(f"📥 [MODULE: verify_rooms_with_grid] Input: {len(rooms)} rooms from Phase 2")

    # Grid verification prompt
    verify_prompt = """Look at this floor plan divided into a 3x3 grid.

Tell me the MAIN room in each zone (the room that takes up most space in that zone):

TOP-LEFT zone: [room name]
TOP-CENTER zone: [room name]
TOP-RIGHT zone: [room name]
LEFT zone: [room name]
CENTER zone: [room name]
RIGHT zone: [room name]
BOTTOM-LEFT zone: [room name]
BOTTOM-CENTER zone: [room name]
BOTTOM-RIGHT zone: [room name]

Use room names: BEDROOM, KITCHEN, LIVING, DRAWING, TOILET, STORE, PARKING, LAWN, WASH AREA
Write "EMPTY" if no major room in that zone."""

    messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": verify_prompt}]}]
    input_text = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
    inputs = tokenizer(images=[image_pil], text=input_text, add_special_tokens=False, return_tensors="pt")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=300, do_sample=False)

    text = tokenizer.decode(output[0], skip_special_tokens=True)
    logger.info(f"📋 Grid Verification: {text[:500]}")

    # Parse grid verification
    grid_rooms = parse_grid_verification(text)

    # Merge with strict count enforcement
    logger.info("🔀 [MODULE: verify_rooms_with_grid] Merging Phase 2 and grid results...")
    corrected_rooms = merge_with_grid_strict(rooms, grid_rooms, expected_counts)
    logger.info(f"✅ [MODULE: verify_rooms_with_grid] Completed: {len(corrected_rooms)} rooms after verification")

    return corrected_rooms


def parse_grid_verification(text):
    """Parse grid zone verification output"""
    logger.info("🗺️ [MODULE: parse_grid_verification] Parsing grid verification output...")
    grid = {}

    if 'assistant' in text.lower():
        idx = text.lower().rfind('assistant')
        text = text[idx + len('assistant'):]

    text_lower = text.lower()

    zone_keywords = {
        'NW': ['top-left', 'top left', 'topleft'],
        'N': ['top-center', 'top center', 'topcenter'],
        'NE': ['top-right', 'top right', 'topright'],
        'W': ['left zone', 'left:'],
        'C': ['center zone', 'center:'],
        'E': ['right zone', 'right:'],
        'SW': ['bottom-left', 'bottom left', 'bottomleft'],
        'S': ['bottom-center', 'bottom center', 'bottomcenter'],
        'SE': ['bottom-right', 'bottom right', 'bottomright']
    }

    room_keywords = {
        'bedroom': ['bedroom', 'bed room'],
        'kitchen': ['kitchen'],
        'living': ['living'],
        'drawing': ['drawing'],
        'toilet': ['toilet', 'bathroom'],
        'store': ['store', 'storage'],
        'parking': ['parking'],
        'lawn': ['lawn', 'garden'],
        'wash_area': ['wash area', 'wash']
    }

    lines = text_lower.split('\n')
    for line in lines:
        found_zone = None
        for zone, keywords in zone_keywords.items():
            if any(kw in line for kw in keywords):
                found_zone = zone
                break

        if not found_zone:
            continue

        for room_type, keywords in room_keywords.items():
            if any(kw in line for kw in keywords):
                grid[found_zone] = room_type
                break

    logger.info(f"Grid map: {grid}")
    return grid


def merge_with_grid_strict(rooms, grid_rooms, expected_counts):
    """Merge with strict enforcement of expected counts"""
    logger.info("🔧 Merging with strict count enforcement...")

    type_counts = {}
    final_rooms = []
    seen_type_positions = set()
    position_occupancy = {}

    rooms_sorted = sorted(rooms, key=lambda r: r.get('_priority', 0), reverse=True)

    # First pass: Use rooms from Phase 2
    for room in rooms_sorted:
        room_type = room['type']
        max_allowed = expected_counts.get(room_type, 10)
        current = type_counts.get(room_type, 0)

        if current >= max_allowed:
            continue

        pos = room['visual_position']

        if pos in position_occupancy:
            continue

        if (room_type, pos) in seen_type_positions:
            continue

        seen_type_positions.add((room_type, pos))
        position_occupancy[pos] = room_type
        type_counts[room_type] = current + 1

        final_rooms.append({
            'type': room_type,
            'subtype': room.get('subtype'),
            'visual_position': pos,
            'raw_text': room.get('raw_text', '')
        })

    # Second pass: Fill missing from grid
    for pos, room_type in grid_rooms.items():
        if not room_type or room_type == 'empty':
            continue

        max_allowed = expected_counts.get(room_type, 10)
        current = type_counts.get(room_type, 0)

        if current >= max_allowed:
            continue

        if (room_type, pos) in seen_type_positions:
            continue

        seen_type_positions.add((room_type, pos))
        position_occupancy[pos] = room_type
        type_counts[room_type] = current + 1

        final_rooms.append({
            'type': room_type,
            'subtype': None,
            'visual_position': pos,
            'raw_text': f'From grid: {room_type} at {pos}'
        })

    logger.info(f"✓ Final rooms: {len(final_rooms)}, counts: {type_counts}")
    return final_rooms


def visual_to_compass(visual_pos: str, offset: int) -> str:
    """Convert visual position to compass direction"""
    logger.debug(f"🧭 [MODULE: visual_to_compass] Converting {visual_pos} with offset {offset}°")
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
    logger.info("🛏️ [MODULE: label_bedrooms] Classifying bedrooms as master/guest...")
    bedrooms = [r for r in rooms if r['type'] == 'bedroom']

    if not bedrooms:
        return

    if len(bedrooms) == 1:
        bedrooms[0]['bedroom_type'] = 'master'
        return

    # Try to identify master by dimensions in raw_text
    for bedroom in bedrooms:
        raw = bedroom.get('raw_text', '').lower()
        if "14'" in raw or "14x" in raw or "14'" in raw:
            bedroom['_size_hint'] = 'large'
        elif "10'" in raw or "10x" in raw:
            bedroom['_size_hint'] = 'small'
        else:
            bedroom['_size_hint'] = 'unknown'

    # Vastu priority for master: SW > S > W
    master_priority = {'SW': 1, 'S': 2, 'W': 3, 'NW': 4, 'N': 5, 'C': 6, 'SE': 7, 'E': 8, 'NE': 9}

    def sort_key(r):
        size_order = 0 if r.get('_size_hint') == 'large' else 1
        vastu_order = master_priority.get(r.get('visual_position', 'C'), 10)
        return (size_order, vastu_order)

    bedrooms_sorted = sorted(bedrooms, key=sort_key)

    for i, r in enumerate(bedrooms_sorted):
        r['bedroom_type'] = 'master' if i == 0 else 'guest'
        if '_size_hint' in r:
            del r['_size_hint']

    logger.info(f"✅ [MODULE: label_bedrooms] Classified {len(bedrooms)} bedrooms")


def load_vastu_rules():
    """Load Vastu rules from JSON file"""
    logger.info(f"📖 [MODULE: load_vastu_rules] Loading Vastu rules from {VASTU_RULES_PATH}...")
    with open(VASTU_RULES_PATH, "r") as f:
        rules = json.load(f)["vastu_rules_for_home"]
    logger.info(f"✅ [MODULE: load_vastu_rules] Loaded {len(rules)} Vastu rules")
    return rules


def evaluate_vastu(room: Dict) -> tuple:
    """Evaluate vastu compliance for a room"""
    logger.debug(f"⚖️ [MODULE: evaluate_vastu] Evaluating {room['type']} at {room.get('compass_direction', 'N')}")
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

    elif rt == 'wash_area':
        if d in ['NW', 'SE']:
            return "✅ COMPLIANT", None, f"Wash Area {d} GOOD"
        elif d in ['NE', 'SW']:
            return "❌ NON_COMPLIANT", "Relocate if possible | Keep clean", f"Wash Area {d} not ideal"
        else:
            return "⚠️ ACCEPTABLE", None, f"Wash Area {d} OK"

    else:
        return "⚠️ ACCEPTABLE", None, f"{rt.title()} {d} placement OK"


# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/", response_model=Dict)
async def root():
    """Root endpoint"""
    return {
        "message": "VastuGPT API - Complete Pipeline",
        "version": "2.0.0",
        "pipeline": "3-phase room detection with verification",
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
    Analyze floor plan for Vastu compliance using 3-phase detection pipeline

    **Parameters:**
    - **image**: Floor plan image (JPG, PNG)
    - **house_facing**: Direction the house faces (optional - will try compass detection first)
    - **door_position**: Where the main door appears on the IMAGE (optional - will try compass detection first)

    **Returns:**
    - Vastu score (0-100)
    - Room-wise analysis with 3-phase verification
    - Remedies for non-compliant rooms
    """
    logger.info("="*70)
    logger.info("🚀 [ENDPOINT: /analyze] NEW ANALYSIS REQUEST RECEIVED")
    logger.info("="*70)

    if not model or not tokenizer:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Read image
        logger.info(f"📸 [ENDPOINT: /analyze] Reading uploaded image: {image.filename}")
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        image_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image_cv is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        image_pil = Image.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))
        logger.info(f"📐 Image: {image_cv.shape[1]}x{image_cv.shape[0]} px")

        # STEP 1: Detect orientation (compass or manual)
        logger.info("="*70)
        logger.info("🧭 STEP 1: Detecting orientation...")
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

        logger.info(f"🧭 Orientation: facing={facing_display}, door={door_display}, offset={offset}°")

        # STEP 2: Get rooms (Phase 1 & 2)
        logger.info("="*70)
        logger.info("🏠 STEP 2: Identifying rooms (Phase 1 & 2)...")
        logger.info("="*70)
        rooms, expected_counts = get_rooms_with_positions(image_pil)

        if not rooms:
            raise HTTPException(status_code=422, detail="No rooms detected in floor plan")

        # STEP 2b: Verify with grid (Phase 3)
        logger.info("="*70)
        logger.info("🗺️ STEP 2b: Verifying with grid (Phase 3)...")
        logger.info("="*70)
        rooms = verify_rooms_with_grid(image_pil, rooms, expected_counts)

        # STEP 3: Convert to compass directions
        logger.info("="*70)
        logger.info("🧭 STEP 3: Converting to compass directions...")
        logger.info("="*70)
        for room in rooms:
            visual = room['visual_position']
            compass = visual_to_compass(visual, offset)
            room['compass_direction'] = compass

        # Label bedrooms
        label_bedrooms(rooms)

        # STEP 4: Evaluate vastu
        logger.info("="*70)
        logger.info("⚖️ STEP 4: Evaluating Vastu compliance...")
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

        message = f"Analysis complete (3-phase pipeline): {compliant} compliant, {non_compliant} critical issues, {acceptable} acceptable"

        logger.info("="*70)
        logger.info(f"✅ [ENDPOINT: /analyze] ANALYSIS COMPLETE - Score: {score}/100")
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
# if __name__ == "__main__":
#     import uvicorn
#     import sys

#     # Check if running in Google Colab
#     try:
#         import google.colab
#         IN_COLAB = True
#     except:
#         IN_COLAB = False

#     if IN_COLAB:
#         logger.info("🌐 Running in Google Colab - Setting up ngrok tunnel...")

#         # Install pyngrok if not available
#         try:
#             from pyngrok import ngrok
#         except ImportError:
#             import subprocess
#             subprocess.check_call([sys.executable, "-m", "pip", "install", "pyngrok"])
#             from pyngrok import ngrok

#         # Start uvicorn in background
#         import threading
#         import time

#         def run_server():
#             uvicorn.run(
#                 app,  # Pass app object directly instead of "api:app" string
#                 host="0.0.0.0",
#                 port=8000,
#                 reload=False,
#                 log_level="info"
#             )

#         # Run server in background thread
#         server_thread = threading.Thread(target=run_server, daemon=True)
#         server_thread.start()

#         # Wait for server to start
#         time.sleep(5)

#         # Setup ngrok auth token (required)
#         logger.info("🔑 Setting up ngrok authentication...")
#         logger.info("⚠️  FIRST TIME SETUP:")
#         logger.info("   1. Get free authtoken: https://dashboard.ngrok.com/get-started/your-authtoken")
#         logger.info("   2. Run: !ngrok config add-authtoken YOUR_TOKEN_HERE")
#         logger.info("   3. Then restart this cell")
#         logger.info("")

#         try:
#             # Create ngrok tunnel
#             public_url = ngrok.connect(8000)
#             logger.info("="*70)
#             logger.info("🚀 VastuGPT API is now PUBLIC!")
#             logger.info("="*70)
#             logger.info(f"📡 Public URL: {public_url}")
#             logger.info(f"📋 API Docs: {public_url}/docs")
#             logger.info(f"🔍 Health Check: {public_url}/health")
#             logger.info("="*70)
#             logger.info("⚠️  Keep this cell running to maintain the tunnel!")
#             logger.info("="*70)

#             # Keep the main thread alive
#             try:
#                 server_thread.join()
#             except KeyboardInterrupt:
#                 logger.info("Shutting down...")
#                 ngrok.disconnect(public_url)

#         except Exception as e:
#             logger.error("="*70)
#             logger.error("❌ Ngrok tunnel failed!")
#             logger.error("="*70)
#             logger.error("To fix this, run in a NEW cell:")
#             logger.error("")
#             logger.error("!ngrok config add-authtoken YOUR_NGROK_TOKEN")
#             logger.error("")
#             logger.error("Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken")
#             logger.error("(Sign up is FREE and takes 30 seconds)")
#             logger.error("="*70)
#             logger.error("")
#             logger.error("🌐 ALTERNATIVE: Server is running locally on http://localhost:8000")
#             logger.error("   You can test it in Colab using:")
#             logger.error("")
#             logger.error("   import requests")
#             logger.error("   response = requests.get('http://localhost:8000/health')")
#             logger.error("   print(response.json())")
#             logger.error("="*70)

#             # Keep server running even without tunnel
#             try:
#                 server_thread.join()
#             except KeyboardInterrupt:
#                 logger.info("Shutting down...")
#     else:
#         # Local execution
#         logger.info("Starting server on 0.0.0.0:8000")
#         uvicorn.run(
#             "api:app",
#             host="0.0.0.0",
#             port=8000,
#             reload=False
#         )
