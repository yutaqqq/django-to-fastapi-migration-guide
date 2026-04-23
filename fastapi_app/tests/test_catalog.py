import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_product_list_returns_all_products(client: AsyncClient, seed_data):
    response = await client.get("/api/products/")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_product_list_includes_category_name(client: AsyncClient, seed_data):
    response = await client.get("/api/products/")
    assert response.status_code == 200
    names = {p["category_name"] for p in response.json()}
    assert "Electronics" in names
    assert "Clothing" in names


@pytest.mark.asyncio
async def test_product_detail(client: AsyncClient, seed_data):
    laptop_id = seed_data["laptop"].id
    response = await client.get(f"/api/products/{laptop_id}/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Laptop Pro"
    assert data["category_name"] == "Electronics"


@pytest.mark.asyncio
async def test_product_detail_404(client: AsyncClient, seed_data):
    response = await client.get("/api/products/99999/")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_product_create(client: AsyncClient, seed_data):
    payload = {
        "name": "Headphones",
        "price": "199.99",
        "stock": 50,
        "category_id": seed_data["electronics"].id,
    }
    response = await client.post("/api/products/create/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Headphones"
    assert data["category_name"] == "Electronics"


@pytest.mark.asyncio
async def test_product_create_invalid_category(client: AsyncClient, seed_data):
    payload = {"name": "Ghost", "price": "10.00", "stock": 1, "category_id": 99999}
    response = await client.post("/api/products/create/", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_product_update(client: AsyncClient, seed_data):
    laptop_id = seed_data["laptop"].id
    payload = {
        "name": "Laptop Pro Max",
        "price": "1499.99",
        "stock": 5,
        "category_id": seed_data["electronics"].id,
    }
    response = await client.put(f"/api/products/{laptop_id}/update/", json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Laptop Pro Max"


@pytest.mark.asyncio
async def test_product_update_404(client: AsyncClient, seed_data):
    payload = {
        "name": "X",
        "price": "1.00",
        "stock": 1,
        "category_id": seed_data["electronics"].id,
    }
    response = await client.put("/api/products/99999/update/", json=payload)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_categories_with_product_count(client: AsyncClient, seed_data):
    response = await client.get("/api/categories/stats/")
    assert response.status_code == 200
    by_slug = {c["slug"]: c for c in response.json()}
    assert by_slug["electronics"]["product_count"] == 1
    assert by_slug["clothing"]["product_count"] == 1
