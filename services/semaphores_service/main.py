from fastapi import FastAPI

app = FastAPI(title="Semaphores Service")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Más adelante: endpoints para controlar y sincronizar semáforos.
