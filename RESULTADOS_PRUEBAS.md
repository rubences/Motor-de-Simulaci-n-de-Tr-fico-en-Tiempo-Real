# Informe de Pruebas de Rendimiento y Resiliencia (Fase 8)

## 1. Objetivos

* **Cargar**: Evaluar el comportamiento de las APIs bajo alta concurrencia (100 usuarios simultáneos) usando Locust.
* **Resiliencia**: Medir el tiempo de recuperación de cada microservicio tras un fallo deliberado (`docker kill`).

---

## 2. Entorno de Pruebas

* **Locust** en `locustfile.py`, simulando:

  * POST `/vehiculos` y PUT `/vehiculos/{id}` contra **Vehicles Service** (puerto 5001).
  * POST `/report_load` y `/assign` contra **Coordinator** (puerto 5000).
* **Downtime Test** con `resilience_test.py`, comprobando `/metrics` de cada servicio:

  * `simulator-zona1` → `http://localhost:8003/metrics`
  * `semaphores`        → `http://localhost:8002/metrics`
  * `coordinator`       → `http://localhost:8000/metrics`
  * `vehicles`          → `http://localhost:8001/metrics`

---

## 3. Resultados de Carga

### Error Rate Inicial

* Al inicio del test, antes de optimizar Locust, `/vehiculos` presentaba un **error rate ≈ 18%** debido a: 422 Unprocessable Entity por IDs inválidos.

### Optimización de Locust

* Se ajustó el script para reutilizar IDs válidos y reenvíar el JSON completo en PUT.
* Tras el cambio, la mayor parte de errores 422 desaparecieron.

### Captura de Failures tras ajuste

![Locust Failures Ajustado](docs/images/chrome_yTFSSMxQbd.png)

* La columna **Current Failures/s** cayó a prácticamente 0 durante el test estable.
* Fallos residuales (\~1–2%) se debieron a vehículos despawned, considerados “esperados” en el flujo.

---

## 4. Resultados de Resiliencia

| Servicio        | Recovery Time (s) |
| --------------- | ----------------- |
| simulator-zona1 | 1.87              |
| semaphores      | 1.94              |
| coordinator     | 1.81              |
| vehicles        | 2.51              |

*Script utilizado: `resilience_test.py`*
*Consola de ejemplo:*

![Downtime Simulator](docs/images/Code_1FgJkQeXTo.png)

---

## 5. Conclusiones

1. **Bajo carga**, el sistema mantiene casi 0 errores en endpoints críticos (`/assign`, `/report_load`), y un error rate mínimo en `/vehiculos` tras ajustes.
2. **Tras fallo deliberado**, cada servicio recupera su endpoint de métricas en < 3 segundos, demostrando una buena tolerancia a fallos.
3. **Vehículos** muestra mayor downtime (\~2.5 s) debido a inicialización de estado; podría mejorarse con réplicas y warm-up.

---

## 6. Recomendaciones

* **Réplicas**: Elevar el número de réplicas de cada servicio (Docker Compose o Kubernetes) para disminuir downtime efectivo.
* **Circuit Breaker**: Implementar fallback y retries con backoff en llamadas internas.
* **Alertas**: Configurar alertas en Grafana si un target permanece caído > 2 s.
* **Pruebas Continuas**: Integrar estos tests en pipelines CI/CD para monitorizar regresiones.

---

*Fin del informe de pruebas.*
