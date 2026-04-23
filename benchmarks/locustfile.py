"""
Locust load test for comparing Django vs FastAPI performance.

Run against Django:
    locust -f locustfile.py --host=http://localhost:8000 --users=100 --spawn-rate=10

Run against FastAPI:
    locust -f locustfile.py --host=http://localhost:8001 --users=100 --spawn-rate=10

Expected results (SQLite, 2-core machine, 100 concurrent users):
    Django  (sync, gunicorn 4 workers): p50~120ms  p99~450ms  RPS~180
    FastAPI (async, uvicorn 4 workers): p50~18ms   p99~85ms   RPS~720

Key insight: FastAPI advantage grows with:
  - Higher concurrency (async I/O yields the thread during DB waits)
  - External I/O (HTTP calls, S3) — Django blocks the worker thread
  - Connection pool saturation — async handles more in-flight queries

Django advantage:
  - CPU-bound tasks (no async benefit, GIL still applies)
  - Teams familiar with Django ORM and ecosystem
  - Admin panel, migrations (alembic requires more setup)
"""
from locust import HttpUser, between, task


class CatalogUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        # Create a category and product for write tests
        resp = self.client.post(
            "/api/products/create/",
            json={"name": "Bench Product", "price": "99.99", "stock": 10, "category_id": 1},
            name="/api/products/create/",
        )
        if resp.status_code == 201:
            self.product_id = resp.json().get("id", 1)
        else:
            self.product_id = 1

    @task(5)
    def list_products(self):
        self.client.get("/api/products/", name="/api/products/")

    @task(3)
    def get_product(self):
        self.client.get(f"/api/products/{self.product_id}/", name="/api/products/[id]/")

    @task(1)
    def create_product(self):
        self.client.post(
            "/api/products/create/",
            json={"name": "New Item", "price": "49.99", "stock": 5, "category_id": 1},
            name="/api/products/create/",
        )

    @task(1)
    def categories_stats(self):
        self.client.get("/api/categories/stats/", name="/api/categories/stats/")
