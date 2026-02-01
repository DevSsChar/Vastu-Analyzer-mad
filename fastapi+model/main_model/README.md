# VastuGPT FastAPI Server

AI-powered Vastu Shastra analysis for floor plans using Vision Language Model.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** First run will download ~7GB model (cached after that)

### 2. Run Server

```bash
python main.py
```

Server starts at: `http://localhost:8000`

### 3. Test API

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Analyze Floor Plan:**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "image=@floorplan.jpg" \
  -F "house_facing=N" \
  -F "door_position=E"
```

## 📋 API Endpoints

### `GET /health`
Check server and model status

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "gpu_available": true
}
```

### `POST /analyze`
Analyze floor plan for Vastu compliance

**Parameters:**
- `image` (file): Floor plan image (JPG/PNG)
- `house_facing` (string): Direction house faces - `N`, `NE`, `E`, `SE`, `S`, `SW`, `W`, `NW`
  - Stand at main door, look OUT - which direction?
- `door_position` (string): Where main door appears on IMAGE - `N`, `NE`, `E`, `SE`, `S`, `SW`, `W`, `NW`

**Response:**
```json
{
  "score": 75,
  "summary": {
    "compliant": 5,
    "non_compliant": 2,
    "acceptable": 3,
    "total_rooms": 10
  },
  "orientation": {
    "house_facing": "N",
    "door_position": "E",
    "north_offset": 270
  },
  "rooms": [
    {
      "id": 1,
      "type": "bedroom",
      "subtype": "master",
      "visual_position": "SW",
      "compass_direction": "N",
      "status": "✅ COMPLIANT",
      "reason": "Master bedroom SW PERFECT - stability/prosperity",
      "remedy": null
    }
  ],
  "message": "Analysis complete: 5 compliant, 2 critical issues, 3 acceptable"
}
```

## 🎯 Direction Guide

### House Facing
The direction the house faces when you **stand at the main door and look OUTSIDE**.

### Door Position
Where the main door appears on the **floor plan image**:
- `N` = Top
- `S` = Bottom
- `E` = Right
- `W` = Left
- `NE` = Top-Right
- `SE` = Bottom-Right
- `SW` = Bottom-Left
- `NW` = Top-Left

## 📊 Vastu Status Codes

- `✅ COMPLIANT` - Ideal placement
- `⚠️ ACCEPTABLE` - Acceptable but not ideal
- `❌ NON_COMPLIANT` - Critical issue, remedy needed

## 🧪 Test with Python

```python
import requests

# Analyze floor plan
with open("floorplan.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/analyze",
        files={"image": f},
        data={
            "house_facing": "N",
            "door_position": "E"
        }
    )

result = response.json()
print(f"Vastu Score: {result['score']}/100")
print(f"Total Rooms: {result['summary']['total_rooms']}")

# Show critical issues
for room in result['rooms']:
    if '❌' in room['status']:
        print(f"\n🔴 {room['type'].upper()}")
        print(f"   Position: {room['compass_direction']}")
        print(f"   Issue: {room['reason']}")
        print(f"   Remedy: {room['remedy']}")
```

## ⚙️ Requirements

- Python 3.10+
- CUDA-capable GPU (recommended) or CPU
- 10GB RAM minimum
- 20GB disk space (for model cache)

## 📝 API Documentation

Once server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🐛 Troubleshooting

### Model Download Issues
First run downloads ~7GB. If interrupted:
```bash
rm -rf ~/.cache/huggingface  # Clear cache
python main.py  # Restart - will resume download
```

### GPU Not Detected
Check CUDA:
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

If False, model will use CPU (slower but works).

### Memory Issues
Reduce batch size or use CPU:
```python
# In main.py, change:
device_map="cpu"  # Instead of "cuda"
```

## 📄 License

MIT License
