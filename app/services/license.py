from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session
from app.config import settings, GRACE_PERIOD_DAYS, PLAN_FEATURES
from app.models import License, Customer, AuditLog
import hashlib
import base64


def get_fernet():
    key = settings.LICENSE_ENCRYPTION_KEY
    # Fernet key 32 bytes base64 असणे आवश्यक आहे
    key_bytes = hashlib.sha256(key.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(fernet_key)


def generate_license_key(customer_id: str, machine_id: str, plan: str, valid_till: datetime) -> str:
    """JWT license key generate करतो"""
    payload = {
        "customer_id": customer_id,
        "machine_id": machine_id,
        "plan": plan,
        "valid_till": valid_till.isoformat(),
        "issued_at": datetime.now(timezone.utc).isoformat(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_license_key(license_key: str) -> dict | None:
    """License key verify करतो"""
    try:
        payload = jwt.decode(license_key, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def encrypt_cache_data(data: dict) -> str:
    """Customer च्या local cache साठी encrypted data"""
    import json
    f = get_fernet()
    json_data = json.dumps(data).encode()
    return f.encrypt(json_data).decode()


def decrypt_cache_data(encrypted: str) -> dict | None:
    """Encrypted cache data decrypt करतो"""
    import json
    try:
        f = get_fernet()
        decrypted = f.decrypt(encrypted.encode())
        return json.loads(decrypted)
    except Exception:
        return None


def create_trial_license(db: Session, customer: Customer, machine_id: str) -> License:
    """नवीन customer साठी 7-day trial license तयार करतो"""
    now = datetime.now(timezone.utc)
    trial_end = now + timedelta(days=settings.TRIAL_DAYS)

    license_key = generate_license_key(
        customer_id=customer.id,
        machine_id=machine_id,
        plan="trial",
        valid_till=trial_end
    )

    license = License(
        customer_id=customer.id,
        machine_id=machine_id,
        license_key=license_key,
        plan="trial",
        trial_start=now,
        trial_end=trial_end,
        valid_till=trial_end,
        last_validated=now,
    )
    db.add(license)
    db.commit()
    db.refresh(license)
    return license


def validate_license(db: Session, machine_id: str, license_key: str, ip: str = None) -> dict:
    """License validate करतो आणि result return करतो"""
    now = datetime.now(timezone.utc)

    # DB मध्ये license शोधा
    license = db.query(License).filter(
        License.machine_id == machine_id,
        License.license_key == license_key,
        License.is_active == True
    ).first()

    if not license:
        return {"valid": False, "reason": "License not found"}

    # Expiry check करा
    valid_till = license.valid_till
    if valid_till.tzinfo is None:
        valid_till = valid_till.replace(tzinfo=timezone.utc)

    if valid_till < now:
        # Trial संपली — free plan ला downgrade करा
        if license.plan == "trial":
            license.plan = "free"
            license.valid_till = now + timedelta(days=365 * 10)  # Free is forever
            db.commit()

    # Last validated update करा
    license.last_validated = now
    db.commit()

    # Grace period calculate करा
    grace_days = GRACE_PERIOD_DAYS.get(license.plan, 15)

    # Features list तयार करा
    features = PLAN_FEATURES.get(license.plan, [])
    if "*" in features:
        features = list(PLAN_FEATURES["trial"])  # सर्व features

    # Audit log
    log = AuditLog(
        customer_id=license.customer_id,
        action="license_validated",
        ip_address=ip,
        machine_id=machine_id,
        details=f"plan={license.plan}"
    )
    db.add(log)
    db.commit()

    # Days remaining
    days_remaining = None
    if license.plan == "trial":
        trial_end = license.trial_end
        if trial_end.tzinfo is None:
            trial_end = trial_end.replace(tzinfo=timezone.utc)
        days_remaining = max(0, (trial_end - now).days)

    # Cache साठी encrypted data
    cache_data = {
        "machine_id": machine_id,
        "license_key": license_key,
        "plan": license.plan,
        "features": features,
        "grace_period_days": grace_days,
        "last_online": now.isoformat(),
        "valid_till": license.valid_till.isoformat(),
        "days_remaining": days_remaining,
    }
    encrypted_cache = encrypt_cache_data(cache_data)

    return {
        "valid": True,
        "plan": license.plan,
        "features": features,
        "grace_period_days": grace_days,
        "days_remaining": days_remaining,
        "valid_till": license.valid_till.isoformat(),
        "encrypted_cache": encrypted_cache,
        "customer_id": license.customer_id,
    }


def upgrade_license(db: Session, customer_id: str, new_plan: str, months: int = 1) -> License:
    """Payment नंतर license upgrade करतो"""
    now = datetime.now(timezone.utc)

    license = db.query(License).filter(
        License.customer_id == customer_id,
        License.is_active == True
    ).first()

    if not license:
        return None

    # Existing valid_till timezone-aware करा (SQLite timezone strip करतो)
    existing_valid_till = license.valid_till
    if existing_valid_till is not None and existing_valid_till.tzinfo is None:
        existing_valid_till = existing_valid_till.replace(tzinfo=timezone.utc)

    # Early renewal: existing valid_till वर stack करा
    # Expired renewal: now पासून सुरू करा
    base_date = max(now, existing_valid_till) if existing_valid_till else now
    valid_till = base_date + timedelta(days=30 * months)

    # नवीन license key generate करा
    new_key = generate_license_key(
        customer_id=customer_id,
        machine_id=license.machine_id,
        plan=new_plan,
        valid_till=valid_till
    )

    license.plan = new_plan
    license.valid_till = valid_till
    license.license_key = new_key
    license.last_validated = now
    db.commit()
    db.refresh(license)

    log = AuditLog(
        customer_id=customer_id,
        action="license_upgraded",
        machine_id=license.machine_id,
        details=f"plan={new_plan}, valid_till={valid_till.isoformat()}"
    )
    db.add(log)
    db.commit()

    return license
