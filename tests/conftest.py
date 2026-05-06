"""
Pytest configuration and shared fixtures
"""
import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base
from app.main import app
from app.services.auth import hash_password, create_access_token
from app.models import Customer, License, AdminUser

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


# Single shared client per module - avoids APScheduler restart issues
@pytest.fixture(scope="module")
def client():
    from app.database import get_db
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    # Patch scheduler to avoid event loop conflicts in tests
    with patch("app.main.scheduler") as mock_scheduler:
        mock_scheduler.start.return_value = None
        mock_scheduler.shutdown.return_value = None
        mock_scheduler.add_job.return_value = None
        with TestClient(app) as c:
            yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def sample_customer_module():
    """Module-scoped customer for integration tests"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    customer = Customer(
        id="int-customer-001",
        business_name="Integration Test Business",
        owner_name="Test Owner",
        email="integration@example.com",
        phone="9999999999",
        city="Mumbai",
        password_hash=hash_password("password123"),
        is_active=True
    )
    session.add(customer)
    session.commit()
    session.refresh(customer)
    license = License(
        id="int-license-001",
        customer_id=customer.id,
        machine_id="int-machine-001",
        license_key="INT-LICENSE-KEY-001",
        plan="basic",
        is_active=True
    )
    session.add(license)
    admin = AdminUser(
        id="int-admin-001",
        full_name="Integration Admin",
        username="intadmin",
        password_hash=hash_password("admin123"),
        role="admin",
        is_active=True
    )
    session.add(admin)
    session.commit()
    yield {"customer": customer, "license": license, "admin": admin}
    session.close()


@pytest.fixture(scope="module")
def customer_token_module(sample_customer_module):
    return create_access_token({"sub": sample_customer_module["customer"].id})


@pytest.fixture(scope="module")
def admin_token_module(sample_customer_module):
    return create_access_token({"sub": sample_customer_module["admin"].username, "role": "admin"})


# Function-scoped fixtures for unit tests
@pytest.fixture
def sample_customer(db):
    customer = Customer(
        id="test-customer-001",
        business_name="Test Business",
        owner_name="Test Owner",
        email="test@example.com",
        phone="9999999999",
        city="Mumbai",
        password_hash=hash_password("password123"),
        is_active=True
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@pytest.fixture
def sample_license(db, sample_customer):
    from datetime import datetime, timezone, timedelta
    license = License(
        id="test-license-001",
        customer_id=sample_customer.id,
        machine_id="test-machine-001",
        license_key="TEST-LICENSE-KEY-001",
        plan="basic",
        is_active=True,
        valid_till=datetime.now(timezone.utc) + timedelta(days=365)
    )
    db.add(license)
    db.commit()
    db.refresh(license)
    return license


@pytest.fixture
def customer_token(sample_customer):
    return create_access_token({"sub": sample_customer.id})


@pytest.fixture
def admin_user(db):
    admin = AdminUser(
        id="test-admin-001",
        full_name="Test Admin",
        username="testadmin",
        password_hash=hash_password("admin123"),
        role="admin",
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def admin_token(admin_user):
    return create_access_token({"sub": admin_user.username, "role": "admin"})
