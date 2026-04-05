import pytest
from fastapi.testclient import TestClient
from db.database import SessionLocal
from db.models import Endpoint
from api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    yield
    db = SessionLocal()
    db.query(Endpoint).delete()
    db.commit()
    db.close()


def test_create_endpoint():
    response = client.post("/endpoints", json={
        "name": "Stripe API",
        "url": "https://api.stripe.com/v1/health",
        "interval_seconds": 60
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Stripe API"
    assert data["url"] == "https://api.stripe.com/v1/health"


def test_list_endpoints():
    response = client.get("/endpoints")
    assert response.status_code == 200
    assert isinstance(response.json(), list)