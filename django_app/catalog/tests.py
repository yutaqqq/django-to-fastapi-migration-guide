from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Category, Product


class CatalogAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.electronics = Category.objects.create(name="Electronics", slug="electronics")
        self.clothing = Category.objects.create(name="Clothing", slug="clothing")
        self.laptop = Product.objects.create(
            name="Laptop Pro",
            price=Decimal("1299.99"),
            stock=10,
            category=self.electronics,
        )
        self.tshirt = Product.objects.create(
            name="T-Shirt",
            price=Decimal("29.99"),
            stock=100,
            category=self.clothing,
        )

    def test_product_list_returns_all_products(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_product_list_includes_category_name(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200)
        names = {p["category_name"] for p in response.data}
        self.assertIn("Electronics", names)
        self.assertIn("Clothing", names)

    def test_product_detail_returns_product(self):
        response = self.client.get(f"/api/products/{self.laptop.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Laptop Pro")
        self.assertEqual(response.data["category_name"], "Electronics")

    def test_product_detail_404_for_missing(self):
        response = self.client.get("/api/products/99999/")
        self.assertEqual(response.status_code, 404)

    def test_product_create(self):
        payload = {
            "name": "Headphones",
            "price": "199.99",
            "stock": 50,
            "category": self.electronics.pk,
        }
        response = self.client.post("/api/products/create/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "Headphones")
        self.assertEqual(Product.objects.count(), 3)

    def test_product_create_validation_error(self):
        payload = {"name": "", "price": "bad", "stock": -1, "category": 9999}
        response = self.client.post("/api/products/create/", payload, format="json")
        self.assertEqual(response.status_code, 400)

    def test_product_update(self):
        payload = {
            "name": "Laptop Pro Max",
            "price": "1499.99",
            "stock": 5,
            "category": self.electronics.pk,
        }
        response = self.client.put(
            f"/api/products/{self.laptop.pk}/update/", payload, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Laptop Pro Max")
        self.laptop.refresh_from_db()
        self.assertEqual(self.laptop.name, "Laptop Pro Max")

    def test_categories_with_product_count(self):
        response = self.client.get("/api/categories/stats/")
        self.assertEqual(response.status_code, 200)
        by_slug = {c["slug"]: c for c in response.data}
        self.assertEqual(by_slug["electronics"]["product_count"], 1)
        self.assertEqual(by_slug["clothing"]["product_count"], 1)
