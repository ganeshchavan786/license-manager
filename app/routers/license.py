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

class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    license_key: str

@router.post("/create-order")
def create_order(req: PaymentRequest, db: Session = Depends(get_db)):
    """Razorpay Order तयार करतो"""
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    data = {
        "amount": req.amount,
        "currency": "INR",
        "receipt": f"receipt_{req.license_key}",
        "notes": {"license_key": req.license_key}
    }
    order = client.order.create(data=data)
    return order

@router.post("/verify-payment")
def verify_payment(req: PaymentVerify, db: Session = Depends(get_db)):
    """पेमेंट तपासून लायसन्सची तारीख वाढवतो"""
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    params_dict = {
        'razorpay_order_id': req.razorpay_order_id,
        'razorpay_payment_id': req.razorpay_payment_id,
        'razorpay_signature': req.razorpay_signature
    }
    
    try:
        client.utility.verify_payment_signature(params_dict)
    except:
        raise HTTPException(status_code=400, detail="Invalid payment signature")

    # लायसन्स शोधा आणि तारीख ३६५ दिवसांनी वाढवा
    license = db.query(License).filter(License.license_key == req.license_key).first()
    if not license:
        raise HTTPException(status_code=404, detail="License not found")

    # जर ट्रायल असेल तर आजपासून ३६५ दिवस द्या, 
    # जर आधीच प्रीमियम असेल तर जुन्या तारखेपासून ३६५ दिवस पुढे वाढवा
    now = datetime.now()
    base_date = license.valid_till if license.valid_till > now else now
    license.valid_till = base_date + timedelta(days=365)
    license.plan = "premium"
    license.is_active = True
    
    db.commit()
    
    return {
        "status": "success",
        "message": "Payment verified. License extended by 365 days.",
        "new_expiry": license.valid_till.isoformat()
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
