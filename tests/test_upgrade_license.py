"""
Unit tests for upgrade_license() — auto-renewal fix.
Validates: Requirements 2.1–2.6, 3.1–3.3

Tests cover:
- Active license: renewal stacks on existing valid_till
- Expired license: renewal starts from now
- Boundary: valid_till == now
- Multi-month renewal
- Plan upgrade/downgrade
- Missing license returns None
- JWT license_key regenerated with correct valid_till
- AuditLog written
- license.plan, license_key, last_validated updated
"""
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jose import jwt

from app.database import Base
from app.models import Customer, License, AuditLog
from app.services.auth import hash_password
from app.services.license import upgrade_license
from app.config import settings

# In-memory DB for unit tests
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def make_customer_and_license(db, valid_till, plan="basic"):
    """Helper: create customer + license with given valid_till"""
    import uuid
    cid = str(uuid.uuid4())
    customer = Customer(
        id=cid,
        business_name="Unit Test Biz",
        owner_name="Unit Owner",
        email=f"{cid}@unit.com",
        phone="9999999999",
        password_hash=hash_password("pass123"),
        is_active=True
    )
    db.add(customer)
    db.commit()

    lic = License(
        id=str(uuid.uuid4()),
        customer_id=cid,
        machine_id=f"machine-{cid}",
        license_key=f"old-key-{cid}",
        plan=plan,
        is_active=True,
        valid_till=valid_till
    )
    db.add(lic)
    db.commit()
    db.refresh(lic)
    return cid, lic


# ─── Active license: stacking tests ─────────────────────────────────────────

def test_active_license_renewal_stacks_15_days():
    """
    Customer with 15 days remaining renews for 1 month.
    Expected: valid_till = existing_valid_till + 30 days (not now + 30 days).
    Validates: Requirement 2.1, 2.2
    """
    db = Session()
    try:
        now = datetime.now(timezone.utc)
        existing_valid_till = now + timedelta(days=15)
        cid, _ = make_customer_and_license(db, existing_valid_till)

        result = upgrade_license(db, cid, "basic", months=1)

        assert result is not None
        actual = result.valid_till
        if actual.tzinfo is None:
            actual = actual.replace(tzinfo=timezone.utc)

        expected = existing_valid_till + timedelta(days=30)
        diff = abs((actual - expected).total_seconds())
        assert diff < 5, f"Expected ≈{expected.isoformat()}, got {actual.isoformat()}"
    finally:
        db.close()


def test_plan_upgrade_mid_cycle_stacks_20_days():
    """
    Customer on basic with 20 days remaining upgrades to premium.
    Expected: valid_till = existing_valid_till + 30 days.
    Validates: Requirement 2.3
    """
    db = Session()
    try:
        now = datetime.now(timezone.utc)
        existing_valid_till = now + timedelta(days=20)
        cid, _ = make_customer_and_license(db, existing_valid_till, plan="basic")

        result = upgrade_license(db, cid, "premium", months=1)

        assert result is not None
        assert result.plan == "premium"
        actual = result.valid_till
        if actual.tzinfo is None:
            actual = actual.replace(tzinfo=timezone.utc)

        expected = existing_valid_till + timedelta(days=30)
        diff = abs((actual - expected).total_seconds())
        assert diff < 5, f"Plan upgrade: Expected ≈{expected.isoformat()}, got {actual.isoformat()}"
    finally:
        db.close()


def test_plan_downgrade_mid_cycle_stacks_10_days():
    """
    Customer on premium with 10 days remaining downgrades to basic.
    Expected: valid_till = existing_valid_till + 30 days.
    Validates: Requirement 2.4
    """
    db = Session()
    try:
        now = datetime.now(timezone.utc)
        existing_valid_till = now + timedelta(days=10)
        cid, _ = make_customer_and_license(db, existing_valid_till, plan="premium")

        result = upgrade_license(db, cid, "basic", months=1)

        assert result is not None
        assert result.plan == "basic"
        actual = result.valid_till
        if actual.tzinfo is None:
            actual = actual.replace(tzinfo=timezone.utc)

        expected = existing_valid_till + timedelta(days=30)
        diff = abs((actual - expected).total_seconds())
        assert diff < 5, f"Plan downgrade: Expected ≈{expected.isoformat()}, got {actual.isoformat()}"
    finally:
        db.close()


def test_multi_month_renewal_with_active_license():
    """
    Customer with 10 days remaining renews for 3 months.
    Expected: valid_till = existing_valid_till + 90 days.
    Validates: Requirement 2.1
    """
    db = Session()
    try:
        now = datetime.now(timezone.utc)
        existing_valid_till = now + timedelta(days=10)
        cid, _ = make_customer_and_license(db, existing_valid_till)

        result = upgrade_license(db, cid, "basic", months=3)

        assert result is not None
        actual = result.valid_till
        if actual.tzinfo is None:
            actual = actual.replace(tzinfo=timezone.utc)

        expected = existing_valid_till + timedelta(days=90)
        diff = abs((actual - expected).total_seconds())
        assert diff < 5, f"3-month renewal: Expected ≈{expected.isoformat()}, got {actual.isoformat()}"
    finally:
        db.close()


# ─── Expired license: preservation tests ─────────────────────────────────────

def test_expired_license_renewal_starts_from_now():
    """
    Customer whose license expired 5 days ago renews.
    Expected: valid_till = now + 30 days (not now - 5 + 30 = now + 25).
    Validates: Requirement 2.5, 3.1
    """
    db = Session()
    try:
        now = datetime.now(timezone.utc)
        past_valid_till = now - timedelta(days=5)
        cid, _ = make_customer_and_license(db, past_valid_till)

        result = upgrade_license(db, cid, "basic", months=1)

        assert result is not None
        actual = result.valid_till
        if actual.tzinfo is None:
            actual = actual.replace(tzinfo=timezone.utc)

        expected = now + timedelta(days=30)
        diff = abs((actual - expected).total_seconds())
        assert diff < 5, f"Expired renewal: Expected ≈{expected.isoformat()}, got {actual.isoformat()}"
    finally:
        db.close()


def test_long_expired_license_does_not_use_past_date():
    """
    Customer whose license expired 365 days ago renews.
    Expected: valid_till ≈ now + 30 days (NOT now - 335 days).
    Validates: Requirement 3.1
    """
    db = Session()
    try:
        now = datetime.now(timezone.utc)
        past_valid_till = now - timedelta(days=365)
        cid, _ = make_customer_and_license(db, past_valid_till)

        result = upgrade_license(db, cid, "basic", months=1)

        assert result is not None
        actual = result.valid_till
        if actual.tzinfo is None:
            actual = actual.replace(tzinfo=timezone.utc)

        # Must be in the future, not the past
        assert actual > now, f"valid_till must be in the future, got {actual.isoformat()}"

        expected = now + timedelta(days=30)
        diff = abs((actual - expected).total_seconds())
        assert diff < 5, f"Long-expired: Expected ≈{expected.isoformat()}, got {actual.isoformat()}"
    finally:
        db.close()


def test_boundary_valid_till_equals_now():
    """
    Customer whose license expires exactly now (boundary case).
    Expected: valid_till ≈ now + 30 days.
    Validates: Requirement 2.5
    """
    db = Session()
    try:
        now = datetime.now(timezone.utc)
        cid, _ = make_customer_and_license(db, now)

        result = upgrade_license(db, cid, "basic", months=1)

        assert result is not None
        actual = result.valid_till
        if actual.tzinfo is None:
            actual = actual.replace(tzinfo=timezone.utc)

        expected = now + timedelta(days=30)
        diff = abs((actual - expected).total_seconds())
        assert diff < 5, f"Boundary: Expected ≈{expected.isoformat()}, got {actual.isoformat()}"
    finally:
        db.close()


# ─── Missing license ──────────────────────────────────────────────────────────

def test_missing_license_returns_none():
    """
    upgrade_license() for a customer_id with no active license returns None.
    Validates: Requirement 3.3
    """
    db = Session()
    try:
        result = upgrade_license(db, "nonexistent-customer-id", "basic", 1)
        assert result is None
    finally:
        db.close()


# ─── JWT key regeneration ─────────────────────────────────────────────────────

def test_license_key_jwt_regenerated_with_correct_valid_till():
    """
    After upgrade, the license_key JWT must embed the new valid_till.
    Validates: Requirement 2.6
    """
    db = Session()
    try:
        now = datetime.now(timezone.utc)
        existing_valid_till = now + timedelta(days=15)
        cid, old_lic = make_customer_and_license(db, existing_valid_till)
        old_key = old_lic.license_key

        result = upgrade_license(db, cid, "basic", months=1)

        assert result is not None
        # Key must be regenerated
        assert result.license_key != old_key

        # Decode JWT and check valid_till
        payload = jwt.decode(result.license_key, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        jwt_valid_till = datetime.fromisoformat(payload["valid_till"])
        if jwt_valid_till.tzinfo is None:
            jwt_valid_till = jwt_valid_till.replace(tzinfo=timezone.utc)

        actual = result.valid_till
        if actual.tzinfo is None:
            actual = actual.replace(tzinfo=timezone.utc)

        diff = abs((jwt_valid_till - actual).total_seconds())
        assert diff < 5, f"JWT valid_till mismatch: JWT={jwt_valid_till.isoformat()}, DB={actual.isoformat()}"
    finally:
        db.close()


# ─── AuditLog and field updates ───────────────────────────────────────────────

def test_audit_log_written_after_upgrade():
    """
    AuditLog entry must be written after a successful upgrade.
    Validates: Requirement 3.2
    """
    db = Session()
    try:
        now = datetime.now(timezone.utc)
        cid, _ = make_customer_and_license(db, now + timedelta(days=5))

        result = upgrade_license(db, cid, "premium", months=1)

        assert result is not None
        log = db.query(AuditLog).filter(
            AuditLog.customer_id == cid,
            AuditLog.action == "license_upgraded"
        ).first()
        assert log is not None, "AuditLog entry not found after upgrade"
        assert "premium" in log.details
    finally:
        db.close()


def test_license_fields_updated_after_upgrade():
    """
    After upgrade: plan, license_key, last_validated must all be updated.
    Validates: Requirement 3.2
    """
    db = Session()
    try:
        now = datetime.now(timezone.utc)
        cid, old_lic = make_customer_and_license(db, now + timedelta(days=5), plan="basic")
        old_key = old_lic.license_key

        result = upgrade_license(db, cid, "premium", months=1)

        assert result is not None
        assert result.plan == "premium"
        assert result.license_key != old_key
        assert result.last_validated is not None
    finally:
        db.close()
