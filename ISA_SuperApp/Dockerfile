FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && groupadd -r app && useradd -r -g app app \
    && mkdir -p /app && chown -R app:app /app

COPY src /app/src
COPY webui /app/webui

USER app

EXPOSE 8787

HEALTHCHECK --interval=30s --timeout=5s --retries=5 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8787/metrics')"

CMD ["uvicorn", "src.api_server:app", "--host", "0.0.0.0", "--port", "8787"]
