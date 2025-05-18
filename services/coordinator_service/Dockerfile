FROM python:3.10-slim

WORKDIR /app

# Copia y instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código del servicio
COPY . .

# Exponer puertos: 5000 para FastAPI, 8000 para /metrics
EXPOSE 5000 8000

# Comando por defecto al arrancar el contenedor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
