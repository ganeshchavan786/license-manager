from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models import Customer, AuditLog, AdminUser
from app.services.auth import hash_password, verify_password, create_access_token
from app.services.license import create_trial_license

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    business_name: str
    owner_name: str
    email: EmailStr
    phone: str
    city: str = ""
    password: str
    machine_id: str  # Customer च्या PC चा unique ID


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    machine_id: str


class AdminRegisterRequest(BaseModel):
    full_name: str
    username: str
    password: str


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class RegisterResponse(BaseModel):
    customer_id: str
    license_key: str
    plan: str
    trial_days: int
    message: str


@router.post("/register", response_model=RegisterResponse)
def register(req: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    """
    नवीन customer register करतो आणि 7-day trial automatically देतो.
    App install नंतर हे call होते.
    """
    # Email already exists का check करा
    existing = db.query(Customer).filter(Customer.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Customer create करा
    customer = Customer(
        business_name=req.business_name,
        owner_name=req.owner_name,
        email=req.email,
        phone=req.phone,
        city=req.city,
        password_hash=hash_password(req.password),
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)

    # Auto 7-day trial license create करा
    license = create_trial_license(db, customer, req.machine_id)

    # Audit log
    ip = request.client.host if request.client else "unknown"
    log = AuditLog(
        customer_id=customer.id,
        action="customer_registered",
        ip_address=ip,
        machine_id=req.machine_id,
        details=f"trial_start={license.trial_start.isoformat()}"
    )
    db.add(log)
    db.commit()

    return RegisterResponse(
        customer_id=customer.id,
        license_key=license.license_key,
        plan="trial",
        trial_days=7,
        message="Registration successful! 7-day free trial activated."
    )


@router.post("/login")
def login(req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Customer login करतो"""
    customer = db.query(Customer).filter(Customer.email == req.email).first()
    if not customer or not verify_password(req.password, customer.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not customer.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    token = create_access_token({"sub": customer.id, "email": customer.email})

    # License info fetch करा
    from app.models import License
    license = db.query(License).filter(
        License.customer_id == customer.id,
        License.machine_id == req.machine_id,
        License.is_active == True
    ).first()

    return {
        "access_token": token,
        "token_type": "bearer",
        "customer_id": customer.id,
        "business_name": customer.business_name,
        "license_key": license.license_key if license else None,
        "plan": license.plan if license else "free",
    }


@router.post("/admin/register")
def admin_register(req: AdminRegisterRequest, x_admin_key: str = Header(...), db: Session = Depends(get_db)):
    """नवीन Admin register करण्यासाठी (प्रथमतः X-Admin-Key लागेल)"""
    from app.config import settings
    if x_admin_key != settings.SECRET_KEY[:32]:
        raise HTTPException(status_code=403, detail="Invalid admin secret key")

    existing = db.query(AdminUser).filter(AdminUser.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    admin = AdminUser(
        full_name=req.full_name,
        username=req.username,
        password_hash=hash_password(req.password)
    )
    db.add(admin)
    db.commit()
    return {"success": True, "message": f"Admin {req.username} created successfully"}


@router.post("/admin/login")
def admin_login(req: AdminLoginRequest, db: Session = Depends(get_db)):
    """Admin login करतो आणि token देतो"""
    admin = db.query(AdminUser).filter(AdminUser.username == req.username).first()
    if not admin or not verify_password(req.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not admin.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    token = create_access_token({"sub": admin.id, "username": admin.username, "role": admin.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "full_name": admin.full_name,
        "username": admin.username
    }
