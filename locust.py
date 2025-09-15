"""
Using it for stress-test / load-test the FastAPI app.
For start, use following in Terminal: locust -f locust.py --processes 4
"""

from locust import HttpUser, task, between

class UserBehavior(HttpUser):
    wait_time = between(1, 5)
    host = "http://127.0.0.1:8000"
    
    @task(3)  # Weight: 3x more likely to be called
    def get_root(self):
        self.client.get("/")

    @task(2)  # Weight: 2x more likely to be called
    def get_health(self):
        self.client.get("/health")

    @task(1)  # Weight: 1x (default)
    def get_docs(self):
        self.client.get("/docs")