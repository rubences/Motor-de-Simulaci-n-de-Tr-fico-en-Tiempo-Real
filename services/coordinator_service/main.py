from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Optional

app = FastAPI(title="Coordinator Service")

class LoadReport(BaseModel):
    zone: str
    load: int

# Almacén en memoria de cargas por zona
zone_loads: Dict[str, int] = {}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/report_load")
async def report_load(report: LoadReport):
    """
    Recibe un reporte de carga de un nodo (zona) y actualiza el estado interno.
    """
    zone_loads[report.zone] = report.load
    return {"status": "received"}

@app.get("/assign")
async def assign_zone():
    """
    Devuelve la zona con menor carga registrada.
    Si no hay reportes, retorna {"zone": null}.
    """
    if not zone_loads:
        return {"zone": None}
    # Encuentra la zona con la carga mínima
    assigned = min(zone_loads.items(), key=lambda item: item[1])[0]
    return {"zone": assigned}
