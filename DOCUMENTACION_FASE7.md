# Documentación Técnica y Guía de Despliegue (Fase 7)

## 1. Introducción

Este documento describe la **arquitectura distribuida**, el **flujo de mensajes**, y la **guía de despliegue** del motor de simulación de tráfico en tiempo real. Incluye los pasos necesarios para levantar el sistema completo en Docker Compose, así como sugerencias para escalar y unirte a un entorno Kubernetes.

---

## 2. Arquitectura Distribuida

### 2.1 Componentes Principales

* **RabbitMQ**: Broker de mensajería AMQP para las migraciones de vehículos entre zonas.
* **Coordinator Service**: Microservicio en FastAPI que supervisa carga de nodos y asigna nuevas migraciones.
* **Vehicles Service**: Microservicio en FastAPI que gestiona la lógica y migración de vehículos.
* **Semaphores Service**: Microservicio en FastAPI que controla estados de semáforos.
* **Simulator Nodes**: Instancias del simulador por zona (p. ej. `simulator-zona1`), exponen métricas Prometheus.
* **Prometheus**: Raspador de métricas, recoge `/metrics` de cada componente.
* **Grafana**: Dashboard para visualizar métricas en tiempo real.

### 2.2 Diagrama de Despliegue

```plantuml
@startuml
!define AWSPUML https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v14.0/Advanced/AWSPUML
!includeurl AWSPUML/Common.puml

node "RabbitMQ" as rabbit
node "Coordinator" as coord
node "Vehicles" as veh
node "Semaphores" as sem
node "Simulator Zona1" as sim1

[rabbit] --> [coord]
[rabbit] --> [veh]
[rabbit] --> [sem]
[veh] --> [sim1]
[coord] --> [sim1]

cloud "Prometheus" as prom
prom --> [coord]
prom --> [veh]
prom --> [sem]
prom --> [sim1]

database "Grafana" as graf
[graf] --> prom
@enduml
```

*Figura 1. Despliegue de microservicios y flujos de métricas.*

---

## 3. Flujo de Mensajes

1. **Migración de Vehículos**:

   * Cuando un vehículo sale de una zona, el servicio de vehículos publica en RabbitMQ un mensaje de migración.
   * El nodo destino suscribe su cola y consume el mensaje, integrando el vehículo.
   * Coordinator ajusta estadísticas y balanceo si es necesario.

2. **Sincronización Global**:

   * Coordinator recibe reportes periódicos de carga (`/report_load`) y decide asignación de nuevas migraciones.
   * Opcional: implementar consenso Raft o etcd para estado replicado.

---

## 4. Guía de Despliegue con Docker Compose

### 4.1 Prerrequisitos

* Docker Desktop (SM): asegurar Docker Engine en ejecución.
* Docker Compose v2 (comando `docker compose`).

### 4.2 Estructura de Archivos

```
project-root/
├── docker-compose.yml
├── Dockerfile.simulator
├── monitoring/
│   └── prometheus.yml
├── services/
│   ├── coordinator_service/
│   ├── vehicles_service/
│   └── semaphores_service/
├── simulation/
│   ├── __init__.py
│   ├── city.py
│   └── simulator.py
└── README.md
```

### 4.3 Comandos de Arranque

```bash
# En la raíz del proyecto
docker compose up --build -d

docker compose ps  # Verifica que todos los servicios estén Up
```

### 4.4 Endpoints de Interés

* **RabbitMQ UI**: [http://localhost:15672](http://localhost:15672)  (guest/guest)
* **Coordinator API**: [http://localhost:5000/health](http://localhost:5000/health)
* **Vehicles API**:   [http://localhost:5001/health](http://localhost:5001/health)
* **Semaphores API**: [http://localhost:5002/health](http://localhost:5002/health)
* **Simulator Zona1**: [http://localhost:8003/metrics](http://localhost:8003/metrics)
* **Prometheus UI**:  [http://localhost:9090](http://localhost:9090)
* **Grafana UI**:     [http://localhost:3000](http://localhost:3000)  (admin/changeme)

---

## 5. Escalado Multi-Nodo

Para añadir más zonas (por ejemplo `zona2`, `zona3`):

1. Copia el bloque `simulator-zona1` en **docker-compose.yml** y ajústalo:

   ```yaml
   simulator-zona2:
     build: ...
     container_name: simulator-zona2
     command: ["python", "simulation/simulator.py", "--zone", "zona2"]
     ports:
       - "8004:8001"
     depends_on:
       - rabbitmq
   ```
2. Reconstruye y levanta:

   ```bash
   ```

docker compose up --build -d simulator-zona2

````
3. Añade un `scrape_config` para `simulator-zona2:8001` en `monitoring/prometheus.yml`.

---

## 6. Despliegue en Kubernetes (Opcional)

**Ejemplo básico** de Deployment y Service para un microservicio:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
name: vehicles-deployment
spec:
replicas: 3
selector:
 matchLabels:
   app: vehicles
template:
 metadata:
   labels:
     app: vehicles
 spec:
   containers:
   - name: vehicles
     image: tu-registry/vehicles:latest
     ports:
     - containerPort: 8000
````

---

## 7. Próximos Pasos y Mejoras

* Integrar algoritmo de consenso (Raft) para estado global.
* Orquestación con Helm Charts.
* Pruebas de carga con Locust o JMeter.
* Alertas en Grafana basadas en umbrales de latencia y carga.

---

*Este documento forma parte de la entrega de la Práctica 2; Fase 7. ¡Buena suerte!*
