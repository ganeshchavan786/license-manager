from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.services import razorpay as rz_service
from app.services.license import upgrade_license
from app.services.email import send_renewal_confirmation
from app.models import Payment, Subscription, License, AuditLog
from datetime import datetime, timezone
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payment", tags=["Payment"])


class CreateOrderRequest(BaseModel):
    plan: str        # basic, premium
    customer_id: str
    promo_code: str = None  # Optional promo code


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
    Supports optional promo code for discounts.
    """
    if req.plan not in ["basic", "premium"]:
        raise HTTPException(status_code=400, detail="Invalid plan")

    try:
        # Validate and apply promo code if provided
        from app.services.promo import validate_promo_code
        from app.config import PLAN_PRICES
        
        base_amount = PLAN_PRICES.get(req.plan, 0)
        final_amount = base_amount
        promo_info = None
        
        if req.promo_code:
            # Validate promo code
            validation = validate_promo_code(
                db=db,
                code=req.promo_code,
                plan=req.plan,
                customer_id=req.customer_id
            )
            
            if not validation["valid"]:
                raise HTTPException(status_code=400, detail=validation["reason"])
            
            # Apply discount
            final_amount = validation["final_amount"]
            promo_info = {
                "code": validation["code"],
                "discount_amount": validation["discount_amount"],
                "promo_code_id": validation["promo_code_id"]
            }
        
        # Create Razorpay order with final amount
        order = rz_service.create_order(req.plan, req.customer_id, amount=final_amount)
        
        # Store promo code info in order notes
        if promo_info:
            order["notes"] = {
                "customer_id": req.customer_id,
                "plan": req.plan,
                "promo_code": promo_info["code"],
                "promo_code_id": promo_info["promo_code_id"],
                "discount_amount": promo_info["discount_amount"]
            }
        
        return {
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "plan": req.plan,
            "promo_applied": promo_info is not None,
            "discount_info": promo_info
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Order creation failed: {str(e)}")


@router.post("/verify")
def verify_payment(req: VerifyPaymentRequest, db: Session = Depends(get_db)):
    """
    Payment झाल्यावर signature verify करतो आणि license upgrade करतो.
    Also records promo code usage if promo code was applied.
    """
    # Signature verify करा
    is_valid = rz_service.verify_payment_signature(
        req.razorpay_order_id,
        req.razorpay_payment_id,
        req.razorpay_signature
    )

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid payment signature")

    # Fetch payment details from Razorpay to get notes
    try:
        payment_details = rz_service.fetch_payment(req.razorpay_payment_id)
        notes = payment_details.get("notes", {})
        promo_code = notes.get("promo_code")
        promo_code_id = notes.get("promo_code_id")
        discount_amount = notes.get("discount_amount", 0)
    except Exception as e:
        # If we can't fetch payment details, continue without promo code
        promo_code = None
        promo_code_id = None
        discount_amount = 0

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
    db.refresh(payment)

    # Record promo code usage if promo code was applied
    if promo_code and promo_code_id:
        from app.models import PromoCode, PromoCodeUsage
        
        # Increment promo code usage_count
        promo = db.query(PromoCode).filter(PromoCode.id == promo_code_id).first()
        if promo:
            promo.usage_count += 1
            
            # Create PromoCodeUsage record
            usage = PromoCodeUsage(
                promo_code_id=promo_code_id,
                customer_id=req.customer_id,
                payment_id=payment.id,
                discount_amount=int(discount_amount)
            )
            db.add(usage)
            db.commit()

    # License upgrade करा
    license = upgrade_license(db, req.customer_id, req.plan)

    if not license:
        raise HTTPException(status_code=404, detail="License not found")

    # Generate invoice (non-blocking)
    invoice_number = None
    try:
        from app.services.invoice import generate_invoice, generate_invoice_pdf, email_invoice
        
        # Generate invoice
        invoice = generate_invoice(
            db=db,
            customer_id=req.customer_id,
            payment_id=payment.id,
            plan=req.plan,
            base_amount=PLAN_PRICES.get(req.plan, 0),
            discount_amount=int(discount_amount) if discount_amount else 0,
            promo_code_id=promo_code_id
        )
        invoice_number = invoice.invoice_number
        logger.info(f"Invoice {invoice_number} generated for customer {req.customer_id}")
        
        # Generate PDF
        generate_invoice_pdf(db=db, invoice_id=invoice.id)
        logger.info(f"Invoice PDF generated for {invoice_number}")
        
        # Email invoice to customer
        email_invoice(db=db, invoice_id=invoice.id)
        logger.info(f"Invoice {invoice_number} queued for email to customer {req.customer_id}")
        
    except Exception as e:
        # Log error but don't fail payment verification
        logger.error(f"Failed to generate/email invoice for customer {req.customer_id}: {str(e)}")

    # Send renewal confirmation email (non-blocking)
    try:
        send_renewal_confirmation(
            db=db,
            customer_id=req.customer_id,
            plan=req.plan,
            amount=PLAN_PRICES.get(req.plan, 0),
            valid_till=license.valid_till
        )
        logger.info(f"Renewal confirmation email queued for customer {req.customer_id}")
    except Exception as e:
        # Log error but don't fail payment verification
        logger.error(f"Failed to queue renewal confirmation email for customer {req.customer_id}: {str(e)}")

    # Audit log
    log_details = f"plan={req.plan}, payment_id={req.razorpay_payment_id}"
    if promo_code:
        log_details += f", promo_code={promo_code}, discount=₹{discount_amount/100}"
    if invoice_number:
        log_details += f", invoice={invoice_number}"
    
    log = AuditLog(
        customer_id=req.customer_id,
        action="payment_verified",
        details=log_details
    )
    db.add(log)
    db.commit()

    return {
        "success": True,
        "plan": req.plan,
        "license_key": license.license_key,
        "valid_till": license.valid_till.isoformat(),
        "message": f"{req.plan.capitalize()} plan activated successfully!",
        "promo_applied": promo_code is not None,
        "invoice_number": invoice_number
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
                license = upgrade_license(db, customer_id, plan)
                
                # Send renewal confirmation email
                if license:
                    try:
                        send_renewal_confirmation(
                            db=db,
                            customer_id=customer_id,
                            plan=plan,
                            amount=payment_data.get("amount", 0),
                            valid_till=license.valid_till
                        )
                        logger.info(f"Renewal confirmation email queued for customer {customer_id} (webhook)")
                    except Exception as e:
                        logger.error(f"Failed to queue renewal confirmation email (webhook): {str(e)}")

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
                license = upgrade_license(db, sub.customer_id, sub.plan)
                
                # Send renewal confirmation email
                if license:
                    try:
                        send_renewal_confirmation(
                            db=db,
                            customer_id=sub.customer_id,
                            plan=sub.plan,
                            amount=sub_data.get("amount", 0),
                            valid_till=license.valid_till
                        )
                        logger.info(f"Renewal confirmation email queued for customer {sub.customer_id} (subscription)")
                    except Exception as e:
                        logger.error(f"Failed to queue renewal confirmation email (subscription): {str(e)}")

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
