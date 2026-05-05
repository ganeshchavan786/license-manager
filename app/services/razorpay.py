import razorpay
import hmac
import hashlib
from app.config import settings, PLAN_PRICES

client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


def create_order(plan: str, customer_id: str) -> dict:
    """Razorpay order create करतो"""
    amount = PLAN_PRICES.get(plan)
    if not amount:
        raise ValueError(f"Invalid plan: {plan}")

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "notes": {
            "customer_id": customer_id,
            "plan": plan,
        }
    })
    return order


def verify_payment_signature(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str
) -> bool:
    """Payment signature verify करतो"""
    message = f"{razorpay_order_id}|{razorpay_payment_id}"
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, razorpay_signature)


def verify_webhook_signature(payload_body: bytes, signature: str) -> bool:
    """Webhook signature verify करतो"""
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def fetch_payment(payment_id: str) -> dict:
    """Payment details fetch करतो"""
    return client.payment.fetch(payment_id)
