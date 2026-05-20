# locustfile.py
from locust import HttpUser, task, between, events
import random

class BeatMarketUser(HttpUser):
    wait_time = between(1, 3)  # Пауза между действиями 1-3 сек
    
    @task(3)
    def view_popular_tracks(self):
        self.client.get("/tracks/popular")
        
    @task(2)
    def search_tracks(self):
        queries = ["beat", "hip-hop", "trap", "love", "summer"]
        self.client.get(f"/tracks/search?query={random.choice(queries)}&limit=10")
        
    @task(2)
    def stream_track(self):
        # Эмуляция получения ID трека из каталога
        track_id = random.randint(1, 100)
        self.client.get(f"/tracks/{track_id}/stream", name="/tracks/{id}/stream")
        
    @task(1)
    def purchase_track(self):
        track_id = random.randint(1, 50)
        self.client.post("/purchase/purchases", json={
            "track_id": track_id,
            "license_type": "standard",
            "buyer_name": "Load Tester",
            "buyer_email": "test@load.com"
        })

    @task(1)
    def auth_flow(self):
        # 10% запросов будут регистрацией/входом
        self.client.post("/auth/register", json={
            "full_name": "Load User", "login": f"loaduser_{random.randint(100,999)}",
            "email": f"load{random.randint(1,999)}@test.com", "password": "12345678", "role": "user"
        })
        self.client.post("/auth/login", data={
            "username": "testuser", "password": "12345678"
        })