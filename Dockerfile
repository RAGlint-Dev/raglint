# Använd en lättviktig Python-bas
FROM python:3.10-slim

# Sätt miljövariabler för att förhindra .pyc filer och buffring
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Sätt arbetskatalog
WORKDIR /app

# Installera systemberoenden (behövs för vissa Python-paket)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Kopiera beroendefiler först (för bättre caching)
COPY pyproject.toml README.md ./

# Installera beroenden
# Vi installerar projektet i "editable" mode eller direkt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Kopiera resten av koden
COPY . .

# Exponera porten som dashboarden körs på
EXPOSE 8000

# Starta dashboarden när containern startar
# Vi använder uvicorn direkt för produktion
CMD ["uvicorn", "raglint.dashboard.app:app", "--host", "0.0.0.0", "--port", "8000"]
