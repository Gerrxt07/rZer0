"""
Using it for stress-test / load-test the FastAPI app.
For start, use following in Terminal: locust -f locust.py
"""

from locust import HttpUser, task, between

class UserBehavior(HttpUser):
    wait_time = between(1, 5)
    host = "http://127.0.0.1:8000"
    
    @task
    def get_root(self):
        self.client.get("/")

    @task
    def get_health(self):
        self.client.get("/health")

    @task
    def get_docs(self):
        self.client.get("/docs")
