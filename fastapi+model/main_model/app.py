import cv2
import numpy as np
import torch
from PIL import Image
from unsloth import FastVisionModel
import json
import re

# ============================================================
# CONFIGURATION
# ============================================================
VASTU_RULES_PATH = "/content/vastu_rules_home.json"

# ============================================================
# LOAD VLM
# ============================================================
def load_vlm():
    model, tokenizer = FastVisionModel.from_pretrained(
        "sabaridsnfuji/FloorPlanVisionAIAdaptor",
        load_in_4bit=True,
        device_map="cuda"
    )
    FastVisionModel.for_inference(model)
    return model, tokenizer

# ============================================================
# STEP 1: GET ACTUAL COMPASS DIRECTIONS FROM IMAGE
# ============================================================
def get_compass_from_image(model, tokenizer, image_pil):
    """Try to read compass rose from image"""
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
    inputs = {k: v.to("cuda") for k, v in inputs.items()}

    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=100, do_sample=False)

    text = tokenizer.decode(output[0], skip_special_tokens=True)
    print(f"\n🧭 Compass Detection:\n{text}\n")

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

def calculate_offset_from_compass(compass_map):
    """Calculate rotation offset from compass readings"""
    if 'N' not in compass_map:
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

    return offset

# ============================================================
# STEP 2: MANUAL INPUT (FALLBACK)
# ============================================================
def get_manual_orientation():
    """Get house facing and door position manually"""
    print("\n" + "="*70)
    print("🏠 HOUSE ORIENTATION")
    print("="*70)
    print("Which direction does your house face?")
    print("(Stand at main door, look OUT - which direction?)")
    print()
    print("1. North (N)      2. NorthEast (NE)    3. East (E)      4. SouthEast (SE)")
    print("5. South (S)      6. SouthWest (SW)    7. West (W)      8. NorthWest (NW)")
    print("="*70)

    facing_map = {1: 'N', 2: 'NE', 3: 'E', 4: 'SE', 5: 'S', 6: 'SW', 7: 'W', 8: 'NW'}

    while True:
        try:
            choice = int(input("Enter (1-8): ").strip())
            if 1 <= choice <= 8:
                facing = facing_map[choice]
                break
        except:
            pass
        print("Invalid. Try again.")

    print("\n" + "="*70)
    print("🚪 MAIN DOOR POSITION")
    print("="*70)
    print("Where is the main door on this IMAGE?")
    print()
    print("1. Top        2. Top-Right    3. Right       4. Bottom-Right")
    print("5. Bottom     6. Bottom-Left  7. Left        8. Top-Left")
    print("="*70)

    while True:
        try:
            choice = int(input("Enter (1-8): ").strip())
            if 1 <= choice <= 8:
                door_pos = facing_map[choice]
                break
        except:
            pass
        print("Invalid. Try again.")

    # Calculate offset
    angles = {'N': 0, 'NE': 45, 'E': 90, 'SE': 135, 'S': 180, 'SW': 225, 'W': 270, 'NW': 315}

    facing_angle = angles[facing]
    door_angle = angles[door_pos]

    offset = (facing_angle - door_angle) % 360

    return facing, door_pos, offset

# ============================================================
# STEP 3: GET ROOMS WITH POSITIONS (IMPROVED VLM PIPELINE)
# ============================================================
def get_rooms_with_positions(model, tokenizer, image_pil):
    """Use VLM with improved prompting for accurate room detection"""

    # PHASE 1: Get room count first
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
    inputs = {k: v.to("cuda") for k, v in inputs.items()}

    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=200, do_sample=False)

    count_text = tokenizer.decode(output[0], skip_special_tokens=True)
    print(f"\n📊 Room Count:\n{count_text}\n")

    # Parse expected counts
    expected_counts = parse_room_counts(count_text)
    print(f"   Expected: {expected_counts}")

    # PHASE 2: Get positions - build prompt dynamically based on Phase 1 counts
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
    inputs = {k: v.to("cuda") for k, v in inputs.items()}

    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=600, do_sample=False)

    text = tokenizer.decode(output[0], skip_special_tokens=True)
    print(f"\n📝 VLM Room Positions:\n{text}\n")

    rooms = parse_room_list_v2(text, expected_counts)

    # Return both rooms and expected_counts for verification phase
    return rooms, expected_counts


def parse_room_counts(text):
    """Parse room counts from VLM output"""
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
        'wash_area': r'wash\s*area\s*[:\-=]\s*(\d+)'  # Use wash_area to match room_type_map
    }

    text_lower = text.lower()
    for room_type, pattern in patterns.items():
        match = re.search(pattern, text_lower)
        if match:
            counts[room_type] = int(match.group(1))

    return counts


def parse_room_list_v2(text, expected_counts):
    """Parse room list with validation against expected counts"""
    print("🔍 Parsing rooms with validation...")

    rooms = []
    room_type_counts = {}  # Track how many of each type we've added

    # Extract only assistant response
    if 'assistant' in text.lower():
        idx = text.lower().rfind('assistant')
        text = text[idx + len('assistant'):]

    lines = text.split('\n')

    # Position mapping - include cardinal directions AND descriptive terms
    position_map = {
        # CRITICAL: Single letter codes (most common VLM output)
        'n': 'N', 's': 'S', 'e': 'E', 'w': 'W', 'c': 'C',
        # Cardinal directions (what VLM often outputs)
        'nw corner': 'NW', 'nw': 'NW', 'northwest': 'NW',
        'ne corner': 'NE', 'ne': 'NE', 'northeast': 'NE',
        'sw corner': 'SW', 'sw': 'SW', 'southwest': 'SW',
        'se corner': 'SE', 'se': 'SE', 'southeast': 'SE',
        # Descriptive terms
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

        # Extract position - use word boundaries for single letters to avoid false matches
        visual_pos = None

        # First try to match single-letter positions with = or - separator (= N, = E, etc.)
        single_letter_pattern = r'[=\-]\s*([NSEWC])\s*$|[=\-]\s*([NSEWC])\s+'
        match = re.search(single_letter_pattern, line_lower.upper())
        if match:
            letter = (match.group(1) or match.group(2)).strip()
            visual_pos = position_map.get(letter.lower())

        # If no single letter match, try compound positions (longer patterns first)
        if not visual_pos:
            for pos_keyword, pos_code in sorted(position_map.items(), key=lambda x: -len(x[0])):
                if pos_keyword in line_lower:
                    visual_pos = pos_code
                    break

        if not visual_pos:
            continue

        # Check against expected counts
        max_allowed = expected_counts.get(room_type, 10)  # Default high if not specified
        current_count = room_type_counts.get(room_type, 0)

        if current_count >= max_allowed:
            print(f"   ⛔ Skipping extra {room_type} (already have {current_count}/{max_allowed})")
            continue

        # Deduplication - only skip if SAME room type at SAME position
        # Different room types CAN share the same zone (e.g., bedroom and toilet both in NW)
        combo_key = (room_type, visual_pos)
        if combo_key in seen_combinations:
            print(f"   ⚠️ Skipping duplicate: {room_type} at {visual_pos}")
            continue
        seen_combinations.add(combo_key)

        # Add room with priority score (for conflict resolution later)
        # Priority: bedroom > kitchen > living > drawing > toilet > store > parking > lawn > wash_area
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

    print(f"\n✓ Extracted {len(rooms)} rooms (validated)")
    print(f"   Counts: {room_type_counts}")

    # Print for verification
    for r in rooms:
        print(f"   • {r['type']:10s} at {r['visual_position']}")

    return rooms


def verify_rooms_with_grid(model, tokenizer, image_pil, rooms, expected_counts):
    """PHASE 3: Verify and CORRECT room positions (not add new rooms)"""
    print("\n🔍 Verifying room positions with grid check...")

    # Create verification prompt for uncertain positions
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
    inputs = {k: v.to("cuda") for k, v in inputs.items()}

    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=300, do_sample=False)

    text = tokenizer.decode(output[0], skip_special_tokens=True)
    print(f"\n📋 Grid Verification:\n{text}\n")

    # Parse grid verification
    grid_rooms = parse_grid_verification(text)

    # Merge with STRICT count enforcement
    corrected_rooms = merge_with_grid_strict(rooms, grid_rooms, expected_counts)

    return corrected_rooms


def parse_grid_verification(text):
    """Parse grid zone verification output"""
    grid = {}

    if 'assistant' in text.lower():
        idx = text.lower().rfind('assistant')
        text = text[idx + len('assistant'):]

    # Simplified parsing - look for zone: room patterns
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
        # Find which zone this line refers to
        found_zone = None
        for zone, keywords in zone_keywords.items():
            if any(kw in line for kw in keywords):
                found_zone = zone
                break

        if not found_zone:
            continue

        # Find which room type
        for room_type, keywords in room_keywords.items():
            if any(kw in line for kw in keywords):
                grid[found_zone] = room_type
                break

    print(f"   Grid map: {grid}")
    return grid


def merge_with_grid_strict(rooms, grid_rooms, expected_counts):
    """Merge with STRICT enforcement of expected counts"""
    print("\n🔧 Merging with strict count enforcement...")

    # Track counts
    type_counts = {}
    final_rooms = []
    seen_type_positions = set()  # (room_type, position) - different types CAN share position
    position_occupancy = {}  # Track which room type is at each position (for priority resolution)

    # Sort rooms by priority (higher priority rooms get their positions first)
    rooms_sorted = sorted(rooms, key=lambda r: r.get('_priority', 0), reverse=True)

    # First pass: Use rooms from Phase 2 (they respect counts)
    for room in rooms_sorted:
        room_type = room['type']
        max_allowed = expected_counts.get(room_type, 10)
        current = type_counts.get(room_type, 0)

        if current >= max_allowed:
            continue

        pos = room['visual_position']

        # Check for position conflict with a different room type
        if pos in position_occupancy:
            existing_type = position_occupancy[pos]
            print(f"   ⚠️ Position conflict at {pos}: {room_type} blocked by {existing_type} (higher priority)")
            # Let grid verification handle this room
            continue

        # Check if this exact (type, position) already exists
        if (room_type, pos) in seen_type_positions:
            # Try to find alternative position from grid
            grid_positions_for_type = [z for z, rt in grid_rooms.items() if rt == room_type]
            found_alt = False
            for alt_pos in grid_positions_for_type:
                if (room_type, alt_pos) not in seen_type_positions:
                    pos = alt_pos
                    print(f"   📍 Relocating duplicate {room_type}: {room['visual_position']} → {pos}")
                    found_alt = True
                    break
            if not found_alt:
                continue  # Skip true duplicate

        seen_type_positions.add((room_type, pos))
        position_occupancy[pos] = room_type  # Track which room occupies this position
        type_counts[room_type] = current + 1

        # Remove priority field before adding to final list
        final_room = {
            'type': room_type,
            'subtype': room.get('subtype'),
            'visual_position': pos,
            'raw_text': room.get('raw_text', '')
        }
        final_rooms.append(final_room)

    # Second pass: Fill missing rooms from grid (only if under count)
    for pos, room_type in grid_rooms.items():
        if not room_type or room_type == 'empty':
            continue

        max_allowed = expected_counts.get(room_type, 10)
        current = type_counts.get(room_type, 0)

        # Skip if we already have enough of this type
        if current >= max_allowed:
            continue

        # Skip if this exact (type, position) already exists
        if (room_type, pos) in seen_type_positions:
            continue

        # Add this room
        seen_type_positions.add((room_type, pos))
        position_occupancy[pos] = room_type
        type_counts[room_type] = current + 1

        final_rooms.append({
            'type': room_type,
            'subtype': None,
            'visual_position': pos,
            'raw_text': f'From grid: {room_type} at {pos}'
        })

    # CRITICAL: Third pass - rescue any missing rooms by finding empty/alternative positions
    all_positions = ['NW', 'N', 'NE', 'W', 'C', 'E', 'SW', 'S', 'SE']
    for room_type, expected_count in expected_counts.items():
        current = type_counts.get(room_type, 0)
        missing = expected_count - current

        if missing > 0:
            print(f"\n   🚨 RESCUE MODE: Missing {missing} {room_type}(s)")

            # Find positions not occupied by higher priority rooms
            available_positions = [p for p in all_positions if p not in position_occupancy]

            # Try to recover from original Phase 2 data
            for room in rooms:
                if room['type'] == room_type and missing > 0:
                    # Check if this room was blocked
                    orig_pos = room['visual_position']

                    # Try original position if now available
                    if orig_pos in available_positions:
                        pos = orig_pos
                        print(f"      ✓ Recovered {room_type} at original position {pos}")
                    # Otherwise use first available
                    elif available_positions:
                        pos = available_positions[0]
                        print(f"      ✓ Recovered {room_type}, relocated to {pos}")
                    else:
                        print(f"      ⚠️ No positions available for {room_type}")
                        continue

                    seen_type_positions.add((room_type, pos))
                    position_occupancy[pos] = room_type
                    available_positions.remove(pos) if pos in available_positions else None
                    type_counts[room_type] = type_counts.get(room_type, 0) + 1

                    final_rooms.append({
                        'type': room_type,
                        'subtype': room.get('subtype'),
                        'visual_position': pos,
                        'raw_text': room.get('raw_text', f'Recovered: {room_type} at {pos}')
                    })

                    missing -= 1

    # Validation check
    print(f"\n   Final counts: {type_counts}")

    critical_errors = []
    for room_type, expected in expected_counts.items():
        actual = type_counts.get(room_type, 0)
        if actual != expected:
            critical_errors.append(f"{room_type}: expected={expected}, got={actual}")
            print(f"   ⚠️ Count mismatch: {room_type} expected={expected}, got={actual}")

    # CRITICAL: If we still have missing rooms, this is a system failure
    if critical_errors:
        print(f"\n   ❌ SYSTEM WARNING: {len(critical_errors)} room type(s) have count mismatches")
        print(f"   This may indicate VLM position errors or parsing failures")

    print(f"\n✓ Final rooms: {len(final_rooms)}")
    for r in final_rooms:
        print(f"   • {r['type']:10s} at {r['visual_position']}")

    return final_rooms

# ============================================================
# STEP 4: CONVERT VISUAL → COMPASS
# ============================================================
def visual_to_compass(visual_pos, offset):
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

# ============================================================
# STEP 5: VASTU EVALUATION
# ============================================================
def load_vastu_rules():
    with open(VASTU_RULES_PATH, "r") as f:
        return json.load(f)["vastu_rules_for_home"]

def label_bedrooms(rooms):
    """Label bedrooms as master/guest based on position and dimensions"""
    bedrooms = [r for r in rooms if r['type'] == 'bedroom']

    if not bedrooms:
        return

    if len(bedrooms) == 1:
        bedrooms[0]['bedroom_type'] = 'master'
        return

    # Try to identify master by dimensions in raw_text
    for bedroom in bedrooms:
        raw = bedroom.get('raw_text', '').lower()
        # Check for larger dimensions (14' is bigger than 10')
        if "14'" in raw or "14x" in raw or "14'" in raw:
            bedroom['_size_hint'] = 'large'
        elif "10'" in raw or "10x" in raw:
            bedroom['_size_hint'] = 'small'
        else:
            bedroom['_size_hint'] = 'unknown'

    # Vastu priority for master: SW > S > W (stability zones)
    # Guest/Kids: NW > N > E (lighter energy)
    master_priority = {'SW': 1, 'S': 2, 'W': 3, 'NW': 4, 'N': 5, 'C': 6, 'SE': 7, 'E': 8, 'NE': 9}

    # Sort: Large bedrooms first, then by vastu priority
    def sort_key(r):
        size_order = 0 if r.get('_size_hint') == 'large' else 1
        vastu_order = master_priority.get(r.get('visual_position', 'C'), 10)
        return (size_order, vastu_order)

    bedrooms_sorted = sorted(bedrooms, key=sort_key)

    # First is master, rest are guest
    for i, r in enumerate(bedrooms_sorted):
        if i == 0:
            r['bedroom_type'] = 'master'
        else:
            r['bedroom_type'] = 'guest'

        # Clean up temp field
        if '_size_hint' in r:
            del r['_size_hint']

    print(f"\n   Bedroom assignments:")
    for r in rooms:
        if r['type'] == 'bedroom':
            print(f"      {r.get('bedroom_type', '?'):6s} at {r['visual_position']}")

def evaluate_vastu(room):
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
                return "✅ COMPLIANT", None, f"{bt.title()} bedroom NW PERFECT"
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

    elif rt == 'dining':
        if d in ['W', 'E', 'N', 'NW']:
            return "✅ COMPLIANT", None, f"Dining {d} GOOD"
        else:
            return "⚠️ ACCEPTABLE", None, f"Dining {d} OK"

    elif rt == 'puja':
        if d in ['NE', 'N', 'E']:
            return "✅ COMPLIANT", None, f"Puja {d} PERFECT - Ishanya zone"
        elif d in ['SW', 'S', 'SE']:
            return "❌ NON_COMPLIANT", "Move to NE/N/E | Idols face E/W | Light colors", f"Puja {d} NOT recommended"
        else:
            return "⚠️ ACCEPTABLE", None, f"Puja {d} OK"

    elif rt == 'store':
        if d in ['S', 'SW', 'W']:
            return "✅ COMPLIANT", None, f"Store {d} IDEAL"
        elif d in ['NE', 'N', 'E']:
            return "❌ NON_COMPLIANT", "Move to SW | Keep NE clear", f"Store {d} blocks energy"
        else:
            return "⚠️ ACCEPTABLE", None, f"Store {d} OK"

    elif rt == 'drawing':
        # Drawing room similar to living room
        if d in ['N', 'NE', 'E', 'NW']:
            return "✅ COMPLIANT", None, f"Drawing {d} GOOD for guests"
        elif d in ['SW', 'S']:
            return "❌ NON_COMPLIANT", "Heavy furniture SW | Bright lighting", f"Drawing {d} not ideal"
        else:
            return "⚠️ ACCEPTABLE", None, f"Drawing {d} OK"

    elif rt == 'parking':
        # Parking best in NW or SE
        if d in ['NW', 'SE', 'E']:
            return "✅ COMPLIANT", None, f"Parking {d} GOOD"
        elif d in ['NE', 'SW']:
            return "❌ NON_COMPLIANT", "Avoid NE/SW parking | Keep clean", f"Parking {d} not recommended"
        else:
            return "⚠️ ACCEPTABLE", None, f"Parking {d} acceptable"

    elif rt == 'lawn':
        # Lawn/garden best in N, NE, E
        if d in ['N', 'NE', 'E']:
            return "✅ COMPLIANT", None, f"Lawn {d} EXCELLENT - positive energy"
        elif d in ['SW']:
            return "❌ NON_COMPLIANT", "Plant heavy trees SW | Tulsi in NE", f"Lawn {d} needs balancing"
        else:
            return "⚠️ ACCEPTABLE", None, f"Lawn {d} OK"

    else:
        return "⚠️ ACCEPTABLE", None, f"{rt.title()} {d} placement OK"

# ============================================================
# MAIN
# ============================================================
def main():
    image_path = "/content/update.jpg"
    image_cv = cv2.imread(image_path)
    if image_cv is None:
      raise RuntimeError("❌ Image not found or path incorrect")

    image_pil = Image.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))
    print(f"📐 Image: {image_cv.shape[1]}x{image_cv.shape[0]} px\n")

    # Load VLM
    print("🔄 Loading VLM...")
    model, tokenizer = load_vlm()

    # Try compass detection first
    print("\n" + "="*70)
    print("STEP 1: DETECT ORIENTATION")
    print("="*70)

    compass_map = get_compass_from_image(model, tokenizer, image_pil)

    if compass_map and len(compass_map) >= 2:
        offset = calculate_offset_from_compass(compass_map)
        if offset is not None:
            print(f"✓ Compass detected! North at {compass_map['N']}")
            print(f"✓ Calculated offset: {offset}°")
            facing = "Detected from compass"
            door_pos = "N/A"
        else:
            print("⚠️ Compass unclear, using manual input")
            facing, door_pos, offset = get_manual_orientation()
    else:
        print("⚠️ No compass found, using manual input")
        facing, door_pos, offset = get_manual_orientation()

    print(f"\n✓ Configuration:")
    print(f"  House facing: {facing}")
    print(f"  Door position: {door_pos}")
    print(f"  North offset: {offset}°")

    # Get rooms
    print("\n" + "="*70)
    print("STEP 2: IDENTIFY ROOMS")
    print("="*70)

    rooms, expected_counts = get_rooms_with_positions(model, tokenizer, image_pil)

    # Verify with grid check
    print("\n" + "="*70)
    print("STEP 2b: VERIFY WITH GRID")
    print("="*70)

    rooms = verify_rooms_with_grid(model, tokenizer, image_pil, rooms, expected_counts)

    if not rooms:
        raise RuntimeError("❌ No rooms detected!")

    # Convert to compass
    print("\n" + "="*70)
    print("STEP 3: CONVERT TO COMPASS DIRECTIONS")
    print("="*70)

    for room in rooms:
        visual = room['visual_position']
        compass = visual_to_compass(visual, offset)
        room['compass_direction'] = compass
        print(f"  {room['type']:12s}: {visual:2s} → {compass:2s}")

    # Label bedrooms
    label_bedrooms(rooms)

    # Evaluate
    print("\n" + "="*70)
    print("STEP 4: VASTU EVALUATION")
    print("="*70)

    for i, room in enumerate(rooms):
        room['id'] = i + 1
        status, remedy, reason = evaluate_vastu(room)
        room['status'] = status
        room['remedy'] = remedy
        room['reason'] = reason

    # Report
    print("\n" + "="*120)
    print("FINAL VASTU ANALYSIS REPORT")
    print("="*120)
    print(f"{'ID':<3} {'TYPE':<12} {'SUB':<8} {'DIR':<3} {'STATUS':<20} {'REASON':<50}")
    print("-"*120)

    for r in rooms:
        print(f"{r['id']:<3} {r['type']:<12} {r.get('bedroom_type','')[:7]:<8} {r.get('compass_direction','N'):<3} {r.get('status',''):<20} {r.get('reason',''):<50}")

    print("="*120)

    # Summary
    compliant = sum(1 for r in rooms if '✅' in r.get('status', ''))
    non_compliant = sum(1 for r in rooms if '❌' in r.get('status', ''))
    acceptable = len(rooms) - compliant - non_compliant

    print(f"\n📊 SUMMARY: {compliant} Compliant | {non_compliant} Critical | {acceptable} Acceptable")

    # Better scoring formula
    total_rooms = len(rooms)
    if total_rooms > 0:
        score = int(((compliant * 100) + (acceptable * 60) + (non_compliant * 20)) / total_rooms)
    else:
        score = 0
    score = min(100, max(0, score))

    print(f"🏆 VASTU SCORE: {score}/100\n")

    if non_compliant > 0:
        print("💡 CRITICAL REMEDIES:")
        for r in rooms:
            if r.get('remedy'):
                print(f"  🔴 {r['type'].upper()} ({r.get('compass_direction')}): {r['remedy']}")

    # Export results to JSON
    result = {
        'score': score,
        'summary': {
            'compliant': compliant,
            'non_compliant': non_compliant,
            'acceptable': acceptable,
            'total_rooms': total_rooms
        },
        'orientation': {
            'house_facing': facing,
            'door_position': door_pos,
            'north_offset': offset
        },
        'rooms': [
            {
                'id': r['id'],
                'type': r['type'],
                'subtype': r.get('bedroom_type', ''),
                'visual_position': r['visual_position'],
                'compass_direction': r.get('compass_direction', ''),
                'status': r.get('status', ''),
                'reason': r.get('reason', ''),
                'remedy': r.get('remedy', '')
            }
            for r in rooms
        ]
    }

    # Save to file
    with open('/content/vastu_analysis_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    print("📁 Results saved to: vastu_analysis_result.json")

    print("\n✅ COMPLETE!")

if __name__ == "__main__":
    main()