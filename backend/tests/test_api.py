import os

os.environ["DATABASE_URL"] = "sqlite:///./test_shopsphere.db"

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_and_products():
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    products = client.get("/products")
    assert products.status_code == 200
    assert len(products.json()) >= 1


def test_register_and_checkout_flow():
    email = "customer@example.com"
    register = client.post(
        "/auth/register",
        json={"name": "Demo Customer", "email": email, "password": "secret123"},
    )
    assert register.status_code == 200, register.text
    user = register.json()
    assert user["email"] == email

    seed_products = client.get("/products")
    product = seed_products.json()[0]

    cart = client.post(
        "/cart/items",
        json={"user_id": user["id"], "product_id": product["id"], "quantity": 2},
    )
    assert cart.status_code == 200, cart.text

    checkout = client.post(
        "/orders/checkout",
        json={
            "user_id": user["id"],
            "idempotency_key": "checkout-1",
            "shipping_address": {
                "street": "1 Main Street",
                "city": "Seattle",
                "state": "WA",
                "postal_code": "98101",
                "country": "US",
            },
            "items": [{"product_id": product["id"], "quantity": 2}],
        },
    )
    assert checkout.status_code == 200, checkout.text
    assert checkout.json()["status"] == "paid"

    orders = client.get(f"/orders?user_id={user['id']}")
    assert orders.status_code == 200
    assert len(orders.json()) >= 1
