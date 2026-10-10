# 📅 Daily Progress Log

> My day-by-day log while going through this course with Claude.

**Format per entry:** date · what I did · quiz result (if any) · notes/blockers.

---

## 2026-10-10

**Did:**
- Phase 0 · `07-docker-for-ai` — ran the Flask container exercise end-to-end.
- Hit port 5000 held by macOS **AirPlay Receiver** (`Server: AirTunes`); worked around it by mapping the host side: `docker run --rm -p 5001:5000 -v "$PWD":/workspace ai-dev python app.py`.
- Debugged a Flask `500`: `index()` called `jsonify(...)` without `return`, so the view returned `None`. Added the `return` → `200 {"status":"ok"}`.
- Learned: `-p host:container` sides are independent; `-v` bind-mounts code live; `--rm` discards the container; trailing cmd overrides the image `CMD`; `Server:` header tells you who answered; no hot-reload without `debug=True`, so restart to pick up edits.

---

## 2026-10-02

**Did:**
- Adapted `gpu_check.py` for M2 (MPS).
- Built modular `benchmarks.py` suite.
- Results: MPS 2–4x faster on matmul, 17x on conv.
- Learned MPS = Apple's Metal GPU backend, unified memory.

---

## 2026-10-01

**Did:**
- Phase 0 · `01-dev-environment` — ran `env_setup.sh`, fixed a `uv run` gotcha (it skipped package install; fixed by running setup script then re-verifying through `.venv`), confirmed M2 Mac uses MPS not CUDA.
- Passed `01-dev-environment` quiz **5/5**.
- Passed `02-git-and-collaboration` quiz **5/5**.
- Took `03-gpu-setup-and-cloud` quiz — **4/5** (missed the fp16 VRAM-to-params question; 24GB ÷ 2 bytes = 12B params, not 24B).
- Started Phase 1 · `01-linear-algebra-intuition` (L01) — read `docs/en.md`, build in progress.

---

<!-- New entries go on top, newest first. -->
