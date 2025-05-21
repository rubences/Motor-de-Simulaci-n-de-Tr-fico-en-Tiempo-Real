from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import start_http_server, Counter, Gauge, Histogram
import time

# --- App Initialization ---
app = FastAPI(
    title="Coordinator Service",
    description="Microservicio central para controlar la carga y distribuir tareas entre nodos.",
    version="1.0.0"
)

# --- Prometheus Metrics ---
# Mide la carga (número de vehículos) reportada por cada zona
default_labels = ['zone']
NODE_LOAD = Gauge('node_load', 'Número de vehículos activos en cada zona', default_labels)
# Contadores de migraciones entrantes y salientes
MIGRATIONS_IN = Counter('migrations_in_total', 'Total de migraciones entrantes al coordinador', default_labels)
MIGRATIONS_OUT = Counter('migrations_out_total', 'Total de migraciones asignadas por el coordinador', default_labels)
# Histograma de latencia de asignación de tareas
ASSIGN_LATENCY = Histogram('assign_latency_seconds', 'Latencia en la asignación de nodos', default_labels)

# --- In-Memory State ---
# Almacena la carga actual (número de vehículos) de cada zona registrada
tzone_loads = {}

# --- Data Models ---
class LoadReport(BaseModel):
    zone: str
    load: int

class AssignRequest(BaseModel):
    exclude_zones: list[str] = []  # Zonas a excluir de la asignación

class AssignResponse(BaseModel):
    zone: str

# --- Startup Event: Iniciar servidor de métricas Prometheus ---
@app.on_event("startup")
def startup_metrics_server():
    # Inicia el servidor en el puerto 8000 para exponer /metrics
    start_http_server(8000)
    print("Prometheus metrics server started on port 8000")

# --- Health Check Endpoint ---
@app.get("/health")
async def health():
    return {"status": "ok"}

# --- Endpoint: Reporte de carga de zona ---
@app.post("/report_load")
async def report_load(report: LoadReport):
    # Actualiza estado interno
    tzone_loads[report.zone] = report.load
    # Actualiza métricas
    NODE_LOAD.labels(zone=report.zone).set(report.load)
    MIGRATIONS_IN.labels(zone=report.zone).inc()
    return {"status": "ok", "zone": report.zone, "load": report.load}

# --- Endpoint: Asignar mejor zona para nueva tarea/migración ---
@app.post("/assign", response_model=AssignResponse)
def assign(req: AssignRequest):
    start_time = time.time()
    # Filtra zonas disponibles
    candidates = [z for z in tzone_loads.keys() if z not in req.exclude_zones]
    if not candidates:
        raise HTTPException(status_code=404, detail="No hay zonas disponibles para asignar.")
    # Selección de la zona con menor carga
    best_zone = min(candidates, key=lambda z: tzone_loads[z])
    # Métricas y respuesta
    latency = time.time() - start_time
    ASSIGN_LATENCY.labels(zone=best_zone).observe(latency)
    MIGRATIONS_OUT.labels(zone=best_zone).inc()
    return AssignResponse(zone=best_zone)

# --- Run Server (si se ejecuta directamente) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)  # Cambiar puerto si es necesario
