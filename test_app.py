import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"

def test_invalid_transaction_amount(client):
    response = client.post("/transactions", json={
        "source_account_id": "acc_alice",
        "destination_account_id": "acc_bob",
        "amount": -50.00
    })
    assert response.status_code == 400
    assert "Amount must be greater than zero" in response.get_json()["error"]