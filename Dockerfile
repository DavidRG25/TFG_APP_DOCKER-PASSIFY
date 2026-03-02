# =========================================================
# Dockerfile para la aplicación principal PaaSify (Django)
# =========================================================

# Usar Python 3.10 como base ligera
FROM python:3.10-slim-bullseye

# Prevenir que Python escriba archivos .pyc e imprimir logs sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema necesarias
# - docker: necesario para interactuar con Docker en el host (DooD)
# - build-essential y libpq-dev: necesarios para compilar psycopg2 (PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    docker.io \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Configurar el directorio de trabajo
WORKDIR /app

# Instalar dependencias de Python
# Copiamos solo el TXT primero para aprovechar la caché de capas de Docker
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Recomendación de producción: instalar gunicorn (WSGI) y daphne (ASGI)
# Daphne ya debería estar en requirements.txt para los websockets, pero lo aseguramos
RUN pip install --no-cache-dir daphne gunicorn psycopg2-binary whitenoise

# Copiar el proyecto entero (respetando el .dockerignore)
COPY . .

# Preparar carpetas estáticas y de medios
RUN mkdir -p /app/staticfiles /app/media && \
    chmod -R 775 /app/staticfiles /app/media

# Hacer ejecutables los scripts
RUN chmod +x run.sh start.sh scripts/*.sh

# Exponer el puerto por defecto (Daphne/Gunicorn)
EXPOSE 8000

# Añadir script de punto de entrada (el mismo que en local)
# Usará --production para forzar 0.0.0.0 y Daphne
CMD ["./run.sh", "--production"]
