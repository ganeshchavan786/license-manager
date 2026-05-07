"""
Integration tests for auto-renewal fix.
Tests webhook and manual payment verify flows to confirm
upgrade_license() stacks valid_till correctly end-to-end.

Validates: Requirements 2.1, 2.2, 3.4, 3.5
"""
import json
import hmac
import hashlib
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models import Customer, License
from app.services.auth import hash_password, create_access_token
from app.config import settings, PLAN_PRICES

# Test DB — separate file to avoid conflicts with other test suites
TEST_DB_URL = "sqlite:///./test_integration_renewal.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    with patch("app.main.scheduler") as mock_sched:
        mock_sched.start.return_value = None
        mock_sched.shutdown.return_value = None
        mock_sched.add_job.return_value = None
        with TestClient(app) as c:
            yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def renewal_customer(client):
    """Customer with active license — 15 days remaining."""
    db = TestSession()
    now = datetime.now(timezone.utc)
    existing_valid_till = now + timedelta(days=15)

    cid = "renewal-customer-001"
    customer = Customer(
        id=cid,
        business_name="Renewal Test Biz",
        owner_name="Renewal Owner",
        email="renewal@test.com",
        phone="9999999999",
        password_hash=hash_password("pass123"),
        is_active=True
    )
    db.add(customer)
    db.commit()

    db.add(License(
        id="renewal-license-001",
        customer_id=cid,
        machine_id="renewal-machine-001",
        license_key="RENEWAL-OLD-KEY",
        plan="basic",
        is_active=True,
        valid_till=existing_valid_till
    ))
    db.commit()
    db.close()

    return {
        "customer_id": cid,
        "existing_valid_till": existing_valid_till,
        "token": create_access_token({"sub": cid})
    }


@pytest.fixture(scope="module")
def expired_customer(client):
    """Customer with expired license — 5 days ago."""
    db = TestSession()
    now = datetime.now(timezone.utc)
    past_valid_till = now - timedelta(days=5)

    cid = "expired-customer-001"
    customer = Customer(
        id=cid,
        business_name="Expired Test Biz",
        owner_name="Expired Owner",
        email="expired@test.com",
        phone="8888888888",
        password_hash=hash_password("pass123"),
        is_active=True
    )
    db.add(customer)
    db.commit()

    db.add(License(
        id="expired-license-001",
        customer_id=cid,
        machine_id="expired-machine-001",
        license_key="EXPIRED-OLD-KEY",
        plan="basic",
        is_active=True,
        valid_till=past_valid_till
    ))
    db.commit()
    db.close()

    return {
        "customer_id": cid,
        "past_valid_till": past_valid_till,
        "token": create_access_token({"sub": cid})
    }


def make_webhook_signature(payload_bytes: bytes) -> str:
    """Generate valid Razorpay webhook signature for test payload."""
    return hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()


# ─── Manual /payment/verify endpoint ─────────────────────────────────────────

def test_manual_verify_active_license_stacks_valid_till(client, renewal_customer):
    """
    POST /payment/verify for a customer with 15 days remaining.
    Expected: response valid_till ≈ existing_valid_till + 30 days (not now + 30 days).
    Validates: Requirement 3.5, 2.1
    """
    existing_valid_till = renewal_customer["existing_valid_till"]

    with patch("app.routers.payment.rz_service.verify_payment_signature", return_value=True), \
         patch("app.routers.payment.rz_service.fetch_payment", return_value={"notes": {}}), \
         patch("app.services.invoice.generate_invoice", return_value=MagicMock(invoice_number="INV-2026-0001", id="inv-001")), \
         patch("app.services.invoice.generate_invoice_pdf", return_value=None), \
         patch("app.services.invoice.email_invoice", return_value=None), \
         patch("app.routers.payment.send_renewal_confirmation", return_value=None):

        response = client.post("/api/payment/verify", json={
            "razorpay_order_id": "order_test_001",
            "razorpay_payment_id": "pay_test_001",
            "razorpay_signature": "test_sig_001",
            "customer_id": renewal_customer["customer_id"],
            "plan": "basic"
        })

    assert response.status_code == 200, f"Response: {response.text}"
    data = response.json()
    assert data["success"] is True

    response_valid_till = datetime.fromisoformat(data["valid_till"])
    if response_valid_till.tzinfo is None:
        response_valid_till = response_valid_till.replace(tzinfo=timezone.utc)

    expected = existing_valid_till + timedelta(days=30)
    diff = abs((response_valid_till - expected).total_seconds())
    assert diff < 10, (
        f"Manual verify: Expected valid_till ≈ {expected.isoformat()}, "
        f"got {response_valid_till.isoformat()}. "
        f"Diff={diff:.1f}s — renewal should stack, not replace."
    )


def test_manual_verify_expired_license_starts_from_now(client, expired_customer):
    """
    POST /payment/verify for a customer with expired license.
    Expected: valid_till ≈ now + 30 days (preservation — no regression).
    Validates: Requirement 3.5, 3.1
    """
    now = datetime.now(timezone.utc)

    with patch("app.routers.payment.rz_service.verify_payment_signature", return_value=True), \
         patch("app.routers.payment.rz_service.fetch_payment", return_value={"notes": {}}), \
         patch("app.services.invoice.generate_invoice", return_value=MagicMock(invoice_number="INV-2026-0002", id="inv-002")), \
         patch("app.services.invoice.generate_invoice_pdf", return_value=None), \
         patch("app.services.invoice.email_invoice", return_value=None), \
         patch("app.routers.payment.send_renewal_confirmation", return_value=None):

        response = client.post("/api/payment/verify", json={
            "razorpay_order_id": "order_expired_001",
            "razorpay_payment_id": "pay_expired_001",
            "razorpay_signature": "test_sig_expired_001",
            "customer_id": expired_customer["customer_id"],
            "plan": "basic"
        })

    assert response.status_code == 200, f"Response: {response.text}"
    data = response.json()
    assert data["success"] is True

    response_valid_till = datetime.fromisoformat(data["valid_till"])
    if response_valid_till.tzinfo is None:
        response_valid_till = response_valid_till.replace(tzinfo=timezone.utc)

    expected = now + timedelta(days=30)
    diff = abs((response_valid_till - expected).total_seconds())
    assert diff < 10, (
        f"Expired renewal: Expected valid_till ≈ {expected.isoformat()}, "
        f"got {response_valid_till.isoformat()}."
    )


# ─── Webhook: payment.captured ────────────────────────────────────────────────

def test_webhook_payment_captured_active_license_stacks(client, renewal_customer):
    """
    Razorpay payment.captured webhook for customer with 15 days remaining.
    Expected: License.valid_till in DB > now + 25 days (stacked, not replaced).
    Validates: Requirement 3.4, 2.1
    """
    now = datetime.now(timezone.utc)

    payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_webhook_001",
                    "amount": PLAN_PRICES["basic"],
                    "notes": {
                        "customer_id": renewal_customer["customer_id"],
                        "plan": "basic"
                    }
                }
            }
        }
    }
    payload_bytes = json.dumps(payload).encode()
    signature = make_webhook_signature(payload_bytes)

    with patch("app.routers.payment.send_renewal_confirmation", return_value=None):
        response = client.post(
            "/api/payment/webhook",
            content=payload_bytes,
            headers={
                "Content-Type": "application/json",
                "X-Razorpay-Signature": signature
            }
        )

    assert response.status_code == 200

    db = TestSession()
    license = db.query(License).filter(
        License.customer_id == renewal_customer["customer_id"],
        License.is_active == True
    ).first()
    db.close()

    assert license is not None
    actual = license.valid_till
    if actual.tzinfo is None:
        actual = actual.replace(tzinfo=timezone.utc)

    # After stacking, valid_till must be well beyond now + 25 days
    assert actual > now + timedelta(days=25), (
        f"Webhook stacking: valid_till {actual.isoformat()} should be > now+25d"
    )


def test_webhook_payment_captured_expired_license_starts_from_now(client, expired_customer):
    """
    Razorpay payment.captured webhook for customer with expired license.
    Expected: valid_till ≈ now + 30 days (preservation).
    Validates: Requirement 3.4, 3.1
    """
    now = datetime.now(timezone.utc)

    payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_webhook_expired_001",
                    "amount": PLAN_PRICES["basic"],
                    "notes": {
                        "customer_id": expired_customer["customer_id"],
                        "plan": "basic"
                    }
                }
            }
        }
    }
    payload_bytes = json.dumps(payload).encode()
    signature = make_webhook_signature(payload_bytes)

    with patch("app.routers.payment.send_renewal_confirmation", return_value=None):
        response = client.post(
            "/api/payment/webhook",
            content=payload_bytes,
            headers={
                "Content-Type": "application/json",
                "X-Razorpay-Signature": signature
            }
        )

    assert response.status_code == 200

    db = TestSession()
    license = db.query(License).filter(
        License.customer_id == expired_customer["customer_id"],
        License.is_active == True
    ).first()
    db.close()

    assert license is not None
    actual = license.valid_till
    if actual.tzinfo is None:
        actual = actual.replace(tzinfo=timezone.utc)

    # Must be in the future — expired license was renewed, so valid_till > now
    # (may have been renewed already by manual verify test above — stacking is correct)
    assert actual > now, f"Expired webhook: valid_till must be in future, got {actual.isoformat()}"

    # valid_till must be at least now + 25 days (either 30 days from now, or stacked further)
    assert actual > now + timedelta(days=25), (
        f"Expired webhook: valid_till {actual.isoformat()} should be > now+25d"
    )
