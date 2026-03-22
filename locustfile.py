from locust import HttpUser, task, between
import random
from datetime import datetime, timedelta, timezone

class SmartParkingUser(HttpUser):
    wait_time = between(0.5, 2.0)
    
    token = 'USER_TOKEN'

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    @task(3)
    def view_spots(self):
        self.client.get("/api/v1/lots/", headers=self.headers, name="GET /lots")
        lot_id = random.randint(1, 10)
        self.client.get(f"/api/v1/lots/{lot_id}/spots/", headers=self.headers, name="GET /spots")

    @task(1)
    def create_booking(self):
        now = datetime.now(timezone.utc)
        start_time = now + timedelta(days=random.randint(1, 20), hours=random.randint(1, 12))
        end_time = start_time + timedelta(hours=random.randint(1, 4))

        spot_id = random.randint(1, 1000) 

        payload = {
            "spot": spot_id,
            "start_at": start_time.isoformat(),
            "end_at": end_time.isoformat()
        }

        with self.client.post("/api/v1/bookings/create/", json=payload, headers=self.headers, name="POST /bookings", catch_response=True) as response:
                if response.status_code in [201, 409]:
                    response.success()
                elif response.status_code == 400:
                    response.failure(f"400: {response.text[:100]}")
                elif response.status_code == 503:
                    response.failure("503: DB unavailable")
                elif response.status_code == 500:
                    response.failure(f"500: {response.text[:100]}")
                else:
                    response.failure(f"Unexpected {response.status_code}")