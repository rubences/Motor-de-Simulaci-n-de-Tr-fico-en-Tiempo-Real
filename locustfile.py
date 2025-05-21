from locust import HttpUser, TaskSet, task, between
import random
import uuid

class CoordinatorBehavior(TaskSet):
    @task(5)
    def report_load(self):
        payload = {
            "zone": random.choice(["zona1", "zona2", "zona3"]),
            "load": random.randint(0, 100)
        }
        self.client.post("/report_load", json=payload)

    @task(3)
    def assign_zone(self):
        exclude = random.choice([[], ["zona1"], ["zona2"], ["zona3"]])
        self.client.post("/assign", json={"exclude_zones": exclude})

class VehiclesBehavior(TaskSet):
    def on_start(self):
        # Pool de IDs de vehículos creados
        self.created_ids = []
        self.zone_choices = ["zona1", "zona2", "zona3"]

    @task(5)
    def create_vehicle(self):
        vid = str(uuid.uuid4())
        zone = random.choice(self.zone_choices)
        payload = {
            "id": vid,
            "position": [random.uniform(0, 800), random.uniform(0, 600)],
            "zone": zone
        }
        r = self.client.post("/vehiculos", json=payload)
        if r.status_code == 200:
            self.created_ids.append((vid, zone))

    @task(3)
    def update_vehicle(self):
        if not self.created_ids:
            return
        # Elige un vehículo existente y reenvía TODO el JSON
        vid, zone = random.choice(self.created_ids)
        payload = {
            "id": vid,
            "position": [random.uniform(0, 800), random.uniform(0, 600)],
            "zone": zone
        }
        self.client.put(f"/vehiculos/{vid}", json=payload)

class CoordinatorUser(HttpUser):
    host = "http://localhost:5000"
    tasks = [CoordinatorBehavior]
    wait_time = between(0.5, 1.5)

class VehiclesUser(HttpUser):
    host = "http://localhost:5001"
    tasks = [VehiclesBehavior]
    wait_time = between(0.5, 1.5)
