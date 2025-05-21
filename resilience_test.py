import subprocess
import time
import requests

CONTAINER = "vehicles"               # o "semaphores", "coordinator"
METRICS_URL = "http://localhost:8001/metrics"  # ajusta el puerto de cada servicio
# para el contenedor que estés probando
# el contenedor debe estar levantado y en estado healthy
CHECK_INTERVAL = 0.5  # seg
TIMEOUT = 120         # seg

def is_metrics_up():
    try:
        r = requests.get(METRICS_URL, timeout=1)
        return r.status_code == 200
    except:
        return False

def docker_cmd(cmd):
    return subprocess.check_output(["docker", "compose"] + cmd, text=True).strip()

def main():
    print("👉 Asegurando que el contenedor está UP y healthy...")
    # Primero arrancamos para asegurar estado limpio
    docker_cmd(["up", "-d", CONTAINER])
    # Esperamos hasta que /metrics responda OK
    while not is_metrics_up():
        time.sleep(CHECK_INTERVAL)
    print("✅ Ready. Ahora inyectamos fallo...")

    # Kill del contenedor
    start = time.time()
    print(f"💥 Matando contenedor {CONTAINER}...")
    subprocess.check_call(["docker", "kill", CONTAINER])

    # Esperamos a que caiga (ya se da por muerto) y luego a que resurja
    print("⌛ Esperando que resurja y exponga métricas de nuevo...")
    # Levantamos de nuevo
    docker_cmd(["up", "-d", CONTAINER])

    # Poll hasta que /metrics responda OK o timeout
    deadline = start + TIMEOUT
    while time.time() < deadline:
        if is_metrics_up():
            recovery = time.time() - start
            print(f"🎉 El servicio se recuperó en {recovery:.2f} segundos.")
            return
        time.sleep(CHECK_INTERVAL)

    print(f"❌ Timeout ({TIMEOUT}s) sin recuperar /metrics")

if __name__ == "__main__":
    main()
