# Imagen del servicio web para docker-compose
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

WORKDIR /app

RUN useradd -m appuser
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=2s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz')"

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app", "--workers", "2", "--threads", "4"]
