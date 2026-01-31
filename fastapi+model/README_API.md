# Vastu AI Advisor API

FastAPI endpoint for AI-powered Vastu Shastra consultations, optimized for NVIDIA RTX 3050 (4GB VRAM).

## Setup

### 1. Environment Configuration

Copy `.env.example` to `.env` and add your Hugging Face token:

```bash
cp .env.example .env
```

Edit `.env`:
```env
HF_TOKEN=your_actual_huggingface_token_here
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the API

```bash
python app.py
```

The API will start on `http://localhost:8000`

## API Endpoints

### Health Check
```bash
GET /
GET /health
```

### Ask Vastu Question
```bash
POST /ask
```

**Request Body:**
```json
{
  "question": "Is a toilet in NE acceptable?",
  "max_tokens": 128,
  "temperature": 0.3
}
```

**Response:**
```json
{
  "question": "Is a toilet in NE acceptable?",
  "answer": "Having a toilet in the North-East (NE) direction is INADVISABLE...",
  "model": "mistralai/Mistral-7B-Instruct-v0.2"
}
```

## Example Usage

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/ask",
    json={
        "question": "Where should I place my kitchen?",
        "max_tokens": 128,
        "temperature": 0.3
    }
)

print(response.json()["answer"])
```

### cURL
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Where should I place my kitchen?"}'
```

### JavaScript/Fetch
```javascript
const response = await fetch('http://localhost:8000/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: 'Where should I place my kitchen?',
    max_tokens: 128,
    temperature: 0.3
  })
});

const data = await response.json();
console.log(data.answer);
```

## Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## GPU Optimization

The API uses 4-bit quantization to fit the 7B parameter model in 4GB VRAM:
- **load_in_4bit**: Reduces memory usage by ~75%
- **nf4 quantization**: Maintains model quality
- **double quantization**: Further reduces memory overhead

## Performance

- **First request**: ~3-5 seconds (model warmup)
- **Subsequent requests**: ~1-2 seconds
- **VRAM usage**: ~3.5GB

## Troubleshooting

### Out of Memory Error
If you encounter OOM errors, try:
1. Reduce `max_tokens` in requests
2. Close other GPU-intensive applications
3. Restart the API server

### CUDA Not Available
Ensure:
1. PyTorch with CUDA is installed: `torch.cuda.is_available()`
2. NVIDIA drivers are up to date
3. CUDA toolkit is installed

Check with:
```bash
python -c "import torch; print(torch.cuda.is_available())"
```
