# Dockerfile-test
FROM python:3.10-slim

# Instalamos Flask
RUN pip install --no-cache-dir flask

WORKDIR /app

# Copiamos el servicio
COPY app.py /app/

# Exponemos el puerto 5000
EXPOSE 5000

# Arrancamos la app
CMD ["python", "app.py"]
