# ✅ unsloth MUST be the absolute first import
import unsloth

import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True,max_split_size_mb:64"
os.environ["TOKENIZERS_PARALLELISM"]  = "false"

import gc
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
VASTU_RULES_PATH    = "/content/vastu_rules_home.json"
MAX_IMAGE_DIMENSION = 336
MAX_SEQ_LENGTH      = 512


# ============================================================
# IMAGE PREPROCESSING
# ============================================================
def preprocess_image_for_vlm(image_pil, max_dim=MAX_IMAGE_DIMENSION):
    w, h = image_pil.size
    if max(w, h) <= max_dim:
        return image_pil
    scale        = max_dim / max(w, h)
    new_w, new_h = int(w * scale), int(h * scale)
    print(f"📏 Resizing: {w}x{h} → {new_w}x{new_h}")
    return image_pil.resize((new_w, new_h), Image.LANCZOS)


def clear_gpu_cache():
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()


def log_gpu_memory(label=""):
    if torch.cuda.is_available():
        alloc = torch.cuda.memory_allocated(0) / 1024**3
        free  = (torch.cuda.get_device_properties(0).total_memory
                 - torch.cuda.memory_reserved(0)) / 1024**3
        print(f"  [GPU {label}] Alloc: {alloc:.2f}GB | Free: {free:.2f}GB")


# ============================================================
# VLM INFERENCE
# ============================================================
def vlm_generate(model, tokenizer, image_pil, prompt, max_new_tokens=200):
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
# LOAD VLM
# ============================================================
def load_vlm():
    model, tokenizer = FastVisionModel.from_pretrained(
        "sabaridsnfuji/FloorPlanVisionAIAdaptor",
        load_in_4bit=True,
        device_map="cuda:0",
        max_seq_length=MAX_SEQ_LENGTH,
        attn_implementation="eager",   # kills flex_attention completely
    )
    FastVisionModel.for_inference(model)
    model.eval()
    for param in model.parameters():
        param.requires_grad = False
    print("  ✓ Model loaded — 4bit, eager attention")
    return model, tokenizer


# ============================================================
# STEP 2: MANUAL ORIENTATION
# ============================================================
def get_manual_orientation():
    print("\n" + "="*70)
    print("🏠 HOUSE ORIENTATION — which direction does your house FACE?")
    print("(Stand at main door, look OUT)\n")
    print("1.N  2.NE  3.E  4.SE  5.S  6.SW  7.W  8.NW")
    facing_map = {1:'N',2:'NE',3:'E',4:'SE',5:'S',6:'SW',7:'W',8:'NW'}
    while True:
        try:
            c = int(input("Enter (1-8): ").strip())
            if 1 <= c <= 8: facing = facing_map[c]; break
        except: pass
        print("Invalid.")

    print("\n🚪 MAIN DOOR position on this IMAGE?")
    print("1.Top  2.Top-Right  3.Right  4.Bottom-Right  5.Bottom  6.Bottom-Left  7.Left  8.Top-Left")
    while True:
        try:
            c = int(input("Enter (1-8): ").strip())
            if 1 <= c <= 8: door_pos = facing_map[c]; break
        except: pass
        print("Invalid.")

    angles = {'N':0,'NE':45,'E':90,'SE':135,'S':180,'SW':225,'W':270,'NW':315}
    offset = (angles[facing] - angles[door_pos]) % 360
    return facing, door_pos, offset


# ============================================================
# STEP 3: ROOM DETECTION  — STRICT PROMPT, SINGLE PASS
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


def get_rooms_with_positions(model, tokenizer, image_pil):
    raw = vlm_generate(model, tokenizer, image_pil, ROOM_PROMPT, max_new_tokens=150)
    print(f"\n📊 VLM Raw Output:\n{raw}\n")
    rooms = parse_strict_format(raw)
    return rooms


def parse_strict_format(text):
    """
    Parse the strict ROOM_TYPE = GRID_CODE format.
    Also handles fallback comma-separated format just in case VLM drifts.
    """
    print("🔍 Parsing rooms...")

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

    def resolve_room(raw_name):
        r = raw_name.strip().lower()
        for k, v in sorted(room_type_map.items(), key=lambda x: -len(x[0])):
            if k in r:
                return v
        return None

    def resolve_pos(raw_pos):
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

    def add_room(room_type, visual_pos, raw_text):
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

    print(f"\n✓ Extracted {len(rooms)} rooms:")
    for r in rooms:
        print(f"   • {r['type']:12s} at {r['visual_position']}")
    return rooms


# ============================================================
# STEP 4: VISUAL → COMPASS
# ============================================================
def visual_to_compass(visual_pos, offset):
    if visual_pos == 'C':
        return 'C'
    angles     = {'N':0,'NE':45,'E':90,'SE':135,'S':180,'SW':225,'W':270,'NW':315}
    actual     = (angles[visual_pos] + offset) % 360
    directions = [(0,'N'),(45,'NE'),(90,'E'),(135,'SE'),(180,'S'),(225,'SW'),(270,'W'),(315,'NW')]
    return min(directions, key=lambda x: min(abs(actual-x[0]), 360-abs(actual-x[0])))[1]


# ============================================================
# STEP 5: VASTU EVALUATION
# ============================================================
def label_bedrooms(rooms):
    bedrooms = [r for r in rooms if r['type'] == 'bedroom']
    if not bedrooms:
        return
    if len(bedrooms) == 1:
        bedrooms[0]['bedroom_type'] = 'master'
        return
    priority  = {'SW':1,'S':2,'W':3,'NW':4,'N':5,'C':6,'SE':7,'E':8,'NE':9}
    sorted_br = sorted(bedrooms, key=lambda r: priority.get(r.get('visual_position','C'), 10))
    sorted_br[0]['bedroom_type'] = 'master'
    for r in sorted_br[1:]:
        r['bedroom_type'] = 'guest'
    print("\n   Bedroom assignments:")
    for r in rooms:
        if r['type'] == 'bedroom':
            print(f"      {r.get('bedroom_type','?'):6s} at {r['visual_position']}")


def evaluate_vastu(room):
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
# MAIN
# ============================================================
def main():
    image_path = "/content/IMG_20260301_154836.jpg.jpeg"
    image_cv   = cv2.imread(image_path)
    if image_cv is None:
        raise RuntimeError("❌ Image not found")

    image_pil = Image.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))
    print(f"📐 Original: {image_cv.shape[1]}x{image_cv.shape[0]} px")
    image_pil = preprocess_image_for_vlm(image_pil)
    print(f"📐 VLM Input: {image_pil.size[0]}x{image_pil.size[1]} px\n")

    facing, door_pos, offset = get_manual_orientation()

    print("\n🔄 Loading VLM...")
    model, tokenizer = load_vlm()
    log_gpu_memory("After model load")
    clear_gpu_cache()

    print(f"\n✓ facing={facing}, door={door_pos}, offset={offset}°")

    # ── Single VLM call — no grid verification pass (saves 5+ minutes)
    print("\n" + "="*70)
    print("STEP 2: IDENTIFY ROOMS  (single pass)")
    print("="*70)
    rooms = get_rooms_with_positions(model, tokenizer, image_pil)

    if not rooms:
        raise RuntimeError("❌ No rooms detected — check VLM raw output above")

    # ── Compass conversion
    print("\n" + "="*70)
    print("STEP 3: COMPASS DIRECTIONS")
    print("="*70)
    for room in rooms:
        room['compass_direction'] = visual_to_compass(room['visual_position'], offset)
        print(f"  {room['type']:14s}: {room['visual_position']:2s} → {room['compass_direction']:2s}")

    label_bedrooms(rooms)

    # ── Vastu evaluation
    print("\n" + "="*70)
    print("STEP 4: VASTU EVALUATION")
    print("="*70)
    for i, room in enumerate(rooms):
        room['id'] = i + 1
        room['status'], room['remedy'], room['reason'] = evaluate_vastu(room)

    # ── Report
    print("\n" + "="*120)
    print("FINAL VASTU ANALYSIS REPORT")
    print("="*120)
    print(f"{'ID':<3} {'TYPE':<14} {'SUB':<8} {'DIR':<4} {'STATUS':<20} {'REASON'}")
    print("-"*120)
    for r in rooms:
        print(f"{r['id']:<3} {r['type']:<14} {r.get('bedroom_type','')[:7]:<8} "
              f"{r.get('compass_direction','N'):<4} {r.get('status',''):<20} {r.get('reason','')}")
    print("="*120)

    compliant     = sum(1 for r in rooms if '✅' in r.get('status',''))
    non_compliant = sum(1 for r in rooms if '❌' in r.get('status',''))
    acceptable    = len(rooms) - compliant - non_compliant
    total         = len(rooms)
    score         = min(100, int(((compliant*100)+(acceptable*60)+(non_compliant*20))/total)) if total else 0

    print(f"\n📊 {compliant} Compliant | {non_compliant} Critical | {acceptable} Acceptable")
    print(f"🏆 VASTU SCORE: {score}/100\n")

    if non_compliant > 0:
        print("💡 CRITICAL REMEDIES:")
        for r in rooms:
            if r.get('remedy'):
                print(f"  🔴 {r['type'].upper()} ({r.get('compass_direction')}): {r['remedy']}")

    result = {
        'score': score,
        'summary': {'compliant':compliant,'non_compliant':non_compliant,
                    'acceptable':acceptable,'total_rooms':total},
        'orientation': {'house_facing':facing,'door_position':door_pos,'north_offset':offset},
        'rooms': [{'id':r['id'],'type':r['type'],'subtype':r.get('bedroom_type',''),
                   'visual_position':r['visual_position'],'compass_direction':r.get('compass_direction',''),
                   'status':r.get('status',''),'reason':r.get('reason',''),'remedy':r.get('remedy','')}
                  for r in rooms]
    }

    with open('/content/vastu_analysis_result.json','w') as f:
        json.dump(result, f, indent=2)
    print("📁 Saved to vastu_analysis_result.json\n✅ COMPLETE!")


if __name__ == "__main__":
    main()