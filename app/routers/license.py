from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.services.license import validate_license
from app.models import License, Customer

router = APIRouter(prefix="/license", tags=["License"])


class ValidateRequest(BaseModel):
    machine_id: str
    license_key: str


class LicenseStatusResponse(BaseModel):
    valid: bool
    plan: str = "free"
    features: list = []
    grace_period_days: int = 15
    days_remaining: int | None = None
    valid_till: str | None = None
    encrypted_cache: str | None = None
    reason: str | None = None


@router.post("/validate", response_model=LicenseStatusResponse)
def validate(req: ValidateRequest, request: Request, db: Session = Depends(get_db)):
    """
    App start होताना हे call होते.
    Online असेल तर validate करतो + encrypted cache देतो.
    """
    ip = request.client.host if request.client else "unknown"
    result = validate_license(db, req.machine_id, req.license_key, ip)

    if not result["valid"]:
        return LicenseStatusResponse(
            valid=False,
            reason=result.get("reason", "Invalid license")
        )

    return LicenseStatusResponse(
        valid=True,
        plan=result["plan"],
        features=result["features"],
        grace_period_days=result["grace_period_days"],
        days_remaining=result.get("days_remaining"),
        valid_till=result.get("valid_till"),
        encrypted_cache=result["encrypted_cache"],
    )


import razorpay
from datetime import datetime, timedelta
from app.config import settings

class PaymentRequest(BaseModel):
    license_key: str
    amount: int  # Amount in paise (e.g. 50000 for Rs. 500)
    plan: str = "basic"  # basic or premium

class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    license_key: str

@router.post("/create-order")
def create_order(req: PaymentRequest, db: Session = Depends(get_db)):
    """Razorpay Order तयार करतो — DB settings वापरतो"""
    from app.services.razorpay import get_razorpay_client
    from app.services.license import verify_license_key
    
    client = get_razorpay_client(db)
    
    # URL encoding fix: spaces → + (JWT token मध्ये + signs असतात)
    fixed_key = req.license_key.replace(" ", "+")
    
    # Exact match
    license = db.query(License).filter(
        License.license_key == fixed_key,
        License.is_active == True
    ).first()
    
    # JWT decode करून customer_id वरून शोधा
    if not license:
        payload = verify_license_key(fixed_key)
        if payload:
            customer_id = payload.get("customer_id")
            if customer_id:
                license = db.query(License).filter(
                    License.customer_id == customer_id,
                    License.is_active == True
                ).first()
    
    if not license:
        raise HTTPException(status_code=404, detail="License not found")
    
    data = {
        "amount": req.amount,
        "currency": "INR",
        "receipt": f"receipt_{license.customer_id[:8]}",
        "notes": {
            "license_key": license.license_key,
            "customer_id": license.customer_id,
            "plan": req.plan
        }
    }
    order = client.order.create(data=data)
    return order

@router.post("/verify-payment")
def verify_payment(req: PaymentVerify, db: Session = Depends(get_db)):
    """पेमेंट तपासून लायसन्सची तारीख वाढवतो"""
    from app.services.razorpay import verify_payment_signature
    from app.services.license import upgrade_license
    from app.services.email import send_renewal_confirmation
    from app.config import PLAN_PRICES
    import logging
    logger = logging.getLogger(__name__)

    # DB keys वापरून signature verify करा
    is_valid = verify_payment_signature(
        req.razorpay_order_id,
        req.razorpay_payment_id,
        req.razorpay_signature,
        db=db
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid payment signature")

    # License शोधा — URL encoding fix
    fixed_key = req.license_key.replace(" ", "+")
    license = db.query(License).filter(
        License.license_key == fixed_key,
        License.is_active == True
    ).first()
    if not license:
        # JWT decode करून शोधा
        from app.services.license import verify_license_key
        payload = verify_license_key(fixed_key)
        if payload:
            license = db.query(License).filter(
                License.customer_id == payload.get("customer_id"),
                License.is_active == True
            ).first()
    if not license:
        raise HTTPException(status_code=404, detail="License not found")

    # Plan determine करा — notes मधून किंवा existing plan वरून
    plan = license.plan if license.plan in ["basic", "premium"] else "basic"

    # Payment save करा
    from app.models import Payment, AuditLog
    payment = Payment(
        customer_id=license.customer_id,
        razorpay_payment_id=req.razorpay_payment_id,
        razorpay_order_id=req.razorpay_order_id,
        razorpay_signature=req.razorpay_signature,
        plan=plan,
        amount=PLAN_PRICES.get(plan, 49900),
        status="captured"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    # License upgrade करा
    upgraded = upgrade_license(db, license.customer_id, plan)

    # Renewal confirmation email
    try:
        send_renewal_confirmation(
            db=db,
            customer_id=license.customer_id,
            plan=plan,
            amount=PLAN_PRICES.get(plan, 49900),
            valid_till=upgraded.valid_till
        )
    except Exception as e:
        logger.error(f"Renewal email failed: {e}")

    return {
        "status": "success",
        "message": f"Payment verified. {plan.capitalize()} plan activated.",
        "new_expiry": upgraded.valid_till.isoformat(),
        "plan": plan
    }

@router.get("/status/{machine_id}")
def get_status(machine_id: str, db: Session = Depends(get_db)):
    """Machine ID वरून license status check करा"""
    license = db.query(License).filter(
        License.machine_id == machine_id,
        License.is_active == True
    ).first()

    if not license:
        return {"found": False}

    customer = db.query(Customer).filter(Customer.id == license.customer_id).first()

    return {
        "found": True,
        "plan": license.plan,
        "valid_till": license.valid_till.isoformat(),
        "business_name": customer.business_name if customer else None,
        "email": customer.email if customer else None,
    }
