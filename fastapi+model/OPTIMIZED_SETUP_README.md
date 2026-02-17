# VastuGPT Optimization Playbook (CPU + GPU)

This guide is an end-to-end setup to reduce response latency while preserving output quality for production chatbot usage.

## 1) What changed

- Rebuilt inference flow in final.py with:
  - backend auto-selection (`llama-cpp` preferred for CPU if GGUF exists)
  - CPU thread tuning
  - proper chat template formatting (better instruction following)
  - deterministic low-latency generation defaults
  - warmup request to reduce first-user latency
  - built-in benchmark mode
- Added scale benchmark script benchmark_scale.py for sustained-load simulation.
- Upgraded prompt policy to produce slightly more detailed outputs with strict structure.

## 2) Why old version was slow

Main issues in old script:
- model was loaded with `torch.float16` on CPU (very slow on most CPUs)
- no backend specialization for CPU inference
- larger generation than needed for chatbot turn-time target

## 3) Latency targets and realistic expectations

For a 7B-class model:
- **CPU (Transformers FP32):** often ~60s to several minutes
- **CPU (llama.cpp GGUF Q4/Q5):** typically 10-30s on strong desktop CPUs
- **GPU (4-bit on 4GB card):** typically 8-20s depending on token count

If you need stable 10-15s on CPU, GGUF + llama.cpp is usually required.

## 4) Setup

## 4.1 Install dependencies

```powershell
pip install -r requirements.txt
```

If `llama-cpp-python` build fails on Windows, install C++ Build Tools first, then retry.

## 4.2 (Recommended for CPU) Create GGUF model

Use llama.cpp conversion tools to convert your HF model to GGUF Q4_K_M or Q5_K_M.

Expected output file path used by default:
- `fastapi+model/vastu-merged-llama3/model-q4_k_m.gguf`

If you use a different filename/path, pass `--gguf-path` at runtime.

## 5) Run interactive optimized inference

```powershell
python final.py --backend auto --threads 8 --max-new-tokens 140
```

Useful options:
- `--backend auto|transformers|llama-cpp`
- `--threads <n>` CPU threads
- `--gpu-layers <n>` for llama.cpp hybrid mode
- `--max-new-tokens <n>` lower value => lower latency

## 6) Run benchmark (single-stream)

```powershell
python final.py --benchmark --requests 20 --backend auto --threads 8
```

Output JSON default:
- `benchmark_results.json`

Metrics:
- avg latency
- p50/p90/p95 latency
- throughput (req/s)

## 7) Run scale benchmark (virtual users)

```powershell
python benchmark_scale.py --requests 50 --users 5 --backend auto --threads 8
```

Output JSON default:
- `benchmark_scale_results.json`

Interpretation:
- With one model instance, generation is mostly serialized.
- Increasing virtual users raises queueing delay and p95 latency.
- Use this to estimate capacity and decide when to add replicas.

## 8) How to test quality retention

1. Build a fixed evaluation set (50-200 real user queries).
2. Run old and new pipelines on the same set.
3. Compare:
   - format compliance rate
   - domain correctness score (manual rubric)
   - actionable remedy quality
4. Track regressions before go-live.

Suggested quick rubric (0-5 each):
- Classification correctness
- Practicality of assessment bullets
- Remedy usefulness
- Concision/clarity

## 9) Production recommendations

- Keep one warmed process always alive.
- Cap output tokens for latency (`max_new_tokens` 100-160).
- Add response caching for repeated user intents.
- Use queue + timeout guardrails.
- For high concurrency: scale horizontally (multiple model replicas).

## 10) Quick command matrix

- CPU best chance of low latency:
  - `python final.py --backend llama-cpp --threads 8 --max-new-tokens 120`
- GPU on small VRAM:
  - `python final.py --backend transformers --max-new-tokens 120`
- Baseline benchmark:
  - `python final.py --benchmark --requests 20`
- Load profile:
  - `python benchmark_scale.py --requests 100 --users 10`
