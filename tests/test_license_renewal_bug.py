"""
Bug condition exploration tests for auto-renewal fix.
Task 1: These tests MUST FAIL on unfixed code (confirms bug exists).
Task 2: Preservation tests MUST PASS on unfixed code (establishes baseline).

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 3.1, 3.2, 3.3**
"""
import pytest
from datetime import datetime, timezone, timedelta
from hypothesis import given, settings as h_settings, assume
from hypothesis import strategies as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Customer, License, AuditLog
from app.services.auth import hash_password
from app.services.license import upgrade_license

# In-memory DB for property tests
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def make_customer_and_license(db, valid_till):
    """Helper: create a customer + license with given valid_till"""
    import uuid
    cid = str(uuid.uuid4())
    customer = Customer(
        id=cid,
        business_name="Test Biz",
        owner_name="Test Owner",
        email=f"{cid}@test.com",
        phone="9999999999",
        password_hash=hash_password("pass123"),
        is_active=True
    )
    db.add(customer)
    db.commit()

    license = License(
        id=str(uuid.uuid4()),
        customer_id=cid,
        machine_id=f"machine-{cid}",
        license_key=f"key-{cid}",
        plan="basic",
        is_active=True,
        valid_till=valid_till
    )
    db.add(license)
    db.commit()
    db.refresh(license)
    return cid, license


# ─── Task 1: Bug Condition Exploration ───────────────────────────────────────
# These tests MUST FAIL on unfixed code.
# Failure confirms: upgrade_license() replaces valid_till instead of extending it.

@given(
    days_remaining=st.integers(min_value=1, max_value=60),
    months=st.integers(min_value=1, max_value=12)
)
@h_settings(max_examples=20, deadline=5000)
def test_bug_condition_early_renewal_should_stack(days_remaining, months):
    """
    EXPECTED TO FAIL on unfixed code.
    When valid_till is in the future, renewal should EXTEND from valid_till,
    not replace with now + 30*months.

    **Validates: Requirements 1.1, 1.2, 1.3, 1.4**
    """
    db = Session()
    try:
        now = datetime.now(timezone.utc)
        future_valid_till = now + timedelta(days=days_remaining)

        cid, _ = make_customer_and_license(db, future_valid_till)
        result = upgrade_license(db, cid, "basic", months)

        assert result is not None
        expected_valid_till = future_valid_till + timedelta(days=30 * months)
        actual_valid_till = result.valid_till
        if actual_valid_till.tzinfo is None:
            actual_valid_till = actual_valid_till.replace(tzinfo=timezone.utc)

        # This assertion FAILS on unfixed code:
        # unfixed code returns now + 30*months, not future_valid_till + 30*months
        diff = abs((actual_valid_till - expected_valid_till).total_seconds())
        assert diff < 5, (
            f"Bug confirmed: days_remaining={days_remaining}, months={months}. "
            f"Expected valid_till ≈ {expected_valid_till.isoformat()}, "
            f"got {actual_valid_till.isoformat()}. "
            f"Diff={diff:.1f}s — renewal replaced instead of extended."
        )
    finally:
        db.close()


# ─── Task 2: Preservation Tests ──────────────────────────────────────────────
# These tests MUST PASS on unfixed code (establishes baseline to preserve).

@given(
    days_expired=st.integers(min_value=1, max_value=730),
    months=st.integers(min_value=1, max_value=12)
)
@h_settings(max_examples=20, deadline=5000)
def test_preservation_expired_license_starts_from_now(days_expired, months):
    """
    MUST PASS on both unfixed and fixed code.
    When valid_till is in the past, renewal should start from now.

    **Validates: Requirements 3.1**
    """
    db = Session()
    try:
        now = datetime.now(timezone.utc)
        past_valid_till = now - timedelta(days=days_expired)

        cid, _ = make_customer_and_license(db, past_valid_till)
        result = upgrade_license(db, cid, "basic", months)

        assert result is not None
        expected_valid_till = now + timedelta(days=30 * months)
        actual_valid_till = result.valid_till
        if actual_valid_till.tzinfo is None:
            actual_valid_till = actual_valid_till.replace(tzinfo=timezone.utc)

        diff = abs((actual_valid_till - expected_valid_till).total_seconds())
        assert diff < 5, (
            f"Preservation broken: days_expired={days_expired}, months={months}. "
            f"Expected valid_till ≈ {expected_valid_till.isoformat()}, "
            f"got {actual_valid_till.isoformat()}."
        )
    finally:
        db.close()


def test_preservation_missing_license_returns_none():
    """
    Missing license must return None — both before and after fix.

    **Validates: Requirements 3.3**
    """
    db = Session()
    try:
        result = upgrade_license(db, "nonexistent-customer-id", "basic", 1)
        assert result is None
    finally:
        db.close()
