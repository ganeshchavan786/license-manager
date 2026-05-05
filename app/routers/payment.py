from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.services import razorpay as rz_service
from app.services.license import upgrade_license
from app.models import Payment, Subscription, License, AuditLog
from datetime import datetime, timezone
import json

router = APIRouter(prefix="/payment", tags=["Payment"])


class CreateOrderRequest(BaseModel):
    plan: str        # basic, premium
    customer_id: str


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    customer_id: str
    plan: str


@router.post("/create-order")
def create_order(req: CreateOrderRequest, db: Session = Depends(get_db)):
    """
    Payment सुरू करण्यापूर्वी Razorpay order create करतो.
    React frontend हे call करतो.
    """
    if req.plan not in ["basic", "premium"]:
        raise HTTPException(status_code=400, detail="Invalid plan")

    try:
        order = rz_service.create_order(req.plan, req.customer_id)
        return {
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "plan": req.plan,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Order creation failed: {str(e)}")


@router.post("/verify")
def verify_payment(req: VerifyPaymentRequest, db: Session = Depends(get_db)):
    """
    Payment झाल्यावर signature verify करतो आणि license upgrade करतो.
    """
    # Signature verify करा
    is_valid = rz_service.verify_payment_signature(
        req.razorpay_order_id,
        req.razorpay_payment_id,
        req.razorpay_signature
    )

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid payment signature")

    # Payment DB मध्ये save करा
    from app.config import PLAN_PRICES
    payment = Payment(
        customer_id=req.customer_id,
        razorpay_payment_id=req.razorpay_payment_id,
        razorpay_order_id=req.razorpay_order_id,
        razorpay_signature=req.razorpay_signature,
        plan=req.plan,
        amount=PLAN_PRICES.get(req.plan, 0),
        status="captured"
    )
    db.add(payment)
    db.commit()

    # License upgrade करा
    license = upgrade_license(db, req.customer_id, req.plan)

    if not license:
        raise HTTPException(status_code=404, detail="License not found")

    # Audit log
    log = AuditLog(
        customer_id=req.customer_id,
        action="payment_verified",
        details=f"plan={req.plan}, payment_id={req.razorpay_payment_id}"
    )
    db.add(log)
    db.commit()

    return {
        "success": True,
        "plan": req.plan,
        "license_key": license.license_key,
        "valid_till": license.valid_till.isoformat(),
        "message": f"{req.plan.capitalize()} plan activated successfully!"
    }


@router.post("/webhook")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Razorpay webhook — automatic subscription renewal साठी.
    Razorpay dashboard मध्ये हा URL set करा.
    """
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    # Webhook signature verify करा
    if not rz_service.verify_webhook_signature(body, signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    try:
        event = json.loads(body)
        event_type = event.get("event")

        if event_type == "payment.captured":
            payment_data = event["payload"]["payment"]["entity"]
            notes = payment_data.get("notes", {})
            customer_id = notes.get("customer_id")
            plan = notes.get("plan")

            if customer_id and plan:
                upgrade_license(db, customer_id, plan)

                log = AuditLog(
                    customer_id=customer_id,
                    action="webhook_payment_captured",
                    details=f"plan={plan}, payment_id={payment_data['id']}"
                )
                db.add(log)
                db.commit()

        elif event_type == "subscription.charged":
            # Auto-renewal
            sub_data = event["payload"]["subscription"]["entity"]
            razorpay_sub_id = sub_data.get("id")

            sub = db.query(Subscription).filter(
                Subscription.razorpay_subscription_id == razorpay_sub_id
            ).first()

            if sub:
                upgrade_license(db, sub.customer_id, sub.plan)

        elif event_type == "subscription.cancelled":
            sub_data = event["payload"]["subscription"]["entity"]
            razorpay_sub_id = sub_data.get("id")

            sub = db.query(Subscription).filter(
                Subscription.razorpay_subscription_id == razorpay_sub_id
            ).first()

            if sub:
                sub.status = "cancelled"
                # Free plan ला downgrade करा
                upgrade_license(db, sub.customer_id, "free")
                db.commit()

    except Exception as e:
        # Webhook errors log करा पण 200 return करा (Razorpay retry करत राहतो)
        print(f"Webhook error: {e}")

    return {"status": "ok"}
