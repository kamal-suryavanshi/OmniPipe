# ─────────────────────────────────────────────────────────────────────────────
#  OmniPipe License Server — Dockerfile
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

LABEL maintainer="omnipipe-team"
LABEL description="OmniPipe central license validation server"

WORKDIR /app

# Copy only the server files (not the whole repo)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# ── Security: run as non-root ─────────────────────────────────────────────────
RUN useradd -m -u 1000 omnipipe
USER omnipipe

EXPOSE 8090

# ── Health check (Docker will mark container unhealthy if this fails) ─────────
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8090/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090", "--workers", "2"]
