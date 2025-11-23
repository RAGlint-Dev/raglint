# RAGLint - Snabbstart

## 1. Installera (Lokalt)
```bash
cd /home/yesir/Dokument/RAGlint
pip install -e .
```

## 2. Starta Dashboarden
```bash
cd raglint/dashboard
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Öppna sedan: **http://localhost:8000**

## 3. Generera Demo-data
I en annan terminal:
```bash
cd /home/yesir/Dokument/RAGlint
python demo_traffic.py
```

Detta skapar events i `raglint_events.jsonl` som visas under "Traces".

## 4. Testa Auto-Instrumentation
Skapa en fil `test_watch.py`:
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

Kör: `python test_watch.py`

---

## Docker (Om du vill)
Docker-versionen tar längre tid att bygga pga PyTorch. När den är klar:
```bash
docker-compose up -d
```
