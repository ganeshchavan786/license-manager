import pytest
from fastapi.testclient import TestClient
from app.models import Customer, License

def test_registration_machine_id_lock(client, db):
    # Step 1: Register customer A with machine_id 'machine-lock-123'
    payload_a = {
        "business_name": "Business A",
        "owner_name": "Owner A",
        "email": "customer_a@example.com",
        "phone": "1234567890",
        "city": "Pune",
        "password": "password123",
        "machine_id": "machine-lock-123"
    }
    
    res_a = client.post("/api/auth/register", json=payload_a)
    assert res_a.status_code == 200
    data_a = res_a.json()
    assert "license_key" in data_a
    assert data_a["plan"] == "trial"

    # Step 2: Try to register customer B with the SAME machine_id 'machine-lock-123'
    payload_b = {
        "business_name": "Business B",
        "owner_name": "Owner B",
        "email": "customer_b@example.com",
        "phone": "9876543210",
        "city": "Mumbai",
        "password": "password123",
        "machine_id": "machine-lock-123"
    }
    
    res_b = client.post("/api/auth/register", json=payload_b)
    # Must fail with 400 Bad Request
    assert res_b.status_code == 400
    data_b = res_b.json()
    assert data_b["detail"] == "This computer/VPS is already active with another account. Please contact support."

    # Step 3: Verify that register succeeds with a DIFFERENT machine_id
    payload_c = {
        "business_name": "Business C",
        "owner_name": "Owner C",
        "email": "customer_c@example.com",
        "phone": "5555555555",
        "city": "Nagpur",
        "password": "password123",
        "machine_id": "machine-lock-456"
    }
    
    res_c = client.post("/api/auth/register", json=payload_c)
    assert res_c.status_code == 200
    data_c = res_c.json()
    assert "license_key" in data_c
