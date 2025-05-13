from fastapi import FastAPI

app = FastAPI(title="Vehicles Service")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Aquí irán más endpoints para registrar, actualizar y migrar vehículos.
