from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import start_http_server, Counter, Gauge, Histogram
import time

app = FastAPI(
    title="Vehicles Service",
    description="Microservicio para registrar y actualizar vehículos",
    version="1.0.0"
)

# --- Métricas Prometheus ---
NODE_LOAD = Gauge('node_load', 'Número de vehículos activos en esta zona', ['zone'])
MIGRATIONS_IN = Counter('migrations_in_total', 'Total de migraciones entrantes', ['zone'])
MIGRATIONS_OUT = Counter('migrations_out_total', 'Total de migraciones salientes', ['zone'])
MESSAGE_LATENCY = Histogram('message_latency_seconds', 'Latencia en pub/sub de mensajes', ['zone'])

# Estado en memoria (ejemplo)
vehicles = {}   # { vehicle_id: {position, zone, ...} }

class Vehicle(BaseModel):
    id: str
    position: tuple[float, float]
    zone: str

@app.on_event("startup")
def startup_metrics():
    # Inicia servidor Prometheus en el puerto 8000
    start_http_server(8000)
    print("Metrics HTTP server for Vehicles started on :8000")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/vehiculos")
async def register_vehicle(v: Vehicle):
    t0 = time.time()
    # Lógica de registro
    vehicles[v.id] = {"position": v.position, "zone": v.zone}
    # Métricas
    NODE_LOAD.labels(zone=v.zone).set(len(vehicles))
    MIGRATIONS_IN.labels(zone=v.zone).inc()
    MESSAGE_LATENCY.labels(zone=v.zone).observe(time.time() - t0)
    return {"status": "registered", "vehicle": v.id}

@app.put("/vehiculos/{vehicle_id}")
async def update_vehicle(vehicle_id: str, v: Vehicle):
    t0 = time.time()
    if vehicle_id not in vehicles:
        raise HTTPException(404, "Vehículo no encontrado")
    # Actualiza posición y zona (eventual migración)
    prev_zone = vehicles[vehicle_id]["zone"]
    vehicles[vehicle_id] = {"position": v.position, "zone": v.zone}
    # Métricas
    NODE_LOAD.labels(zone=v.zone).set(
        sum(1 for vh in vehicles.values() if vh["zone"] == v.zone)
    )
    if prev_zone != v.zone:
        MIGRATIONS_OUT.labels(zone=prev_zone).inc()
        MIGRATIONS_IN.labels(zone=v.zone).inc()
    MESSAGE_LATENCY.labels(zone=v.zone).observe(time.time() - t0)
    return {"status": "updated", "vehicle": vehicle_id}

# Ejecuta con `uvicorn main:app --host 0.0.0.0 --port 5000`
