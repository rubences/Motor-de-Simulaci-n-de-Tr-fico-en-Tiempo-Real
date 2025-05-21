from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import start_http_server, Counter, Gauge, Histogram
import time

app = FastAPI(
    title="Semaphores Service",
    description="Microservicio para controlar estados de semáforos",
    version="1.0.0"
)

# --- Métricas Prometheus ---
NODE_LOAD = Gauge('node_load', 'Número de semáforos activos en esta zona', ['zone'])
MIGRATIONS_IN = Counter('migrations_in_total', 'Total de migraciones entrantes', ['zone'])
MIGRATIONS_OUT = Counter('migrations_out_total', 'Total de migraciones salientes', ['zone'])
MESSAGE_LATENCY = Histogram('message_latency_seconds', 'Latencia en pub/sub de mensajes', ['zone'])

# Estado de semáforos (ejemplo)
semaphores = {}   # { semaphore_id: state }

class Semaphore(BaseModel):
    id: str
    state: str
    zone: str

@app.on_event("startup")
def startup_metrics():
    # Inicia servidor Prometheus en el puerto 8000
    start_http_server(8000)
    print("Metrics HTTP server for Semaphores started on :8000")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/semaforos")
async def set_semaphore(s: Semaphore):
    t0 = time.time()
    # Lógica para crear o actualizar semáforo
    semaphores[s.id] = {"state": s.state, "zone": s.zone}
    # Métricas
    NODE_LOAD.labels(zone=s.zone).set(len(semaphores))
    MESSAGE_LATENCY.labels(zone=s.zone).observe(time.time() - t0)
    return {"status": "ok", "semaphore": s.id}
