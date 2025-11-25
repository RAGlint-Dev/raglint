# RAGLint - Quick Start

## 1. Install (Locally)
```bash
cd /home/yesir/Dokument/RAGlint
pip install -e .
```

## 2. Start the Dashboard
```bash
cd raglint/dashboard
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Then open: **http://localhost:8000**

## 3. Generate Demo Data
In another terminal:
```bash
cd /home/yesir/Dokument/RAGlint
python demo_traffic.py
```

This creates events in `raglint_events.jsonl` which are shown under "Traces".

## 4. Test Auto-Instrumentation
Create a file `test_watch.py`:
```python
from raglint import watch
import time

@watch(tags=["demo"])
def my_function(x):
    time.sleep(0.5)
    return x * 2

my_function(10)
print("Check raglint_events.jsonl!")
```

Run: `python test_watch.py`

---

## Docker (Optional)
The Docker version takes longer to build due to PyTorch. When it is ready:
```bash
docker-compose up -d
```
