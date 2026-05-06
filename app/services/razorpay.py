import razorpay
import hmac
import hashlib
from sqlalchemy.orm import Session
from app.config import settings as config_settings, PLAN_PRICES
from app.services.settings import get_payment_gateway_settings


def get_razorpay_client(db: Session = None):
    """
    Get Razorpay client with credentials from database or config
    
    Preconditions:
    - Database session is optional
    
    Postconditions:
    - Returns configured Razorpay client
    - Uses database settings if available, otherwise falls back to config
    """
    if db:
        try:
            settings = get_payment_gateway_settings(db)
            key_id = settings.get("razorpay_key_id", config_settings.RAZORPAY_KEY_ID)
            key_secret = settings.get("razorpay_key_secret", config_settings.RAZORPAY_KEY_SECRET)
        except:
            # Fallback to config if database read fails
            key_id = config_settings.RAZORPAY_KEY_ID
            key_secret = config_settings.RAZORPAY_KEY_SECRET
    else:
        key_id = config_settings.RAZORPAY_KEY_ID
        key_secret = config_settings.RAZORPAY_KEY_SECRET
    
    return razorpay.Client(auth=(key_id, key_secret))


def create_order(plan: str, customer_id: str, amount: int = None, db: Session = None) -> dict:
    """Razorpay order create करतो"""
    if amount is None:
        amount = PLAN_PRICES.get(plan)
    
    if not amount:
        raise ValueError(f"Invalid plan: {plan}")

    client = get_razorpay_client(db)
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
    razorpay_signature: str,
    db: Session = None
) -> bool:
    """Payment signature verify करतो"""
    if db:
        try:
            settings = get_payment_gateway_settings(db)
            key_secret = settings.get("razorpay_key_secret", config_settings.RAZORPAY_KEY_SECRET)
        except:
            key_secret = config_settings.RAZORPAY_KEY_SECRET
    else:
        key_secret = config_settings.RAZORPAY_KEY_SECRET
    
    message = f"{razorpay_order_id}|{razorpay_payment_id}"
    expected = hmac.new(
        key_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, razorpay_signature)


def verify_webhook_signature(payload_body: bytes, signature: str, db: Session = None) -> bool:
    """Webhook signature verify करतो"""
    if db:
        try:
            settings = get_payment_gateway_settings(db)
            key_secret = settings.get("razorpay_key_secret", config_settings.RAZORPAY_KEY_SECRET)
        except:
            key_secret = config_settings.RAZORPAY_KEY_SECRET
    else:
        key_secret = config_settings.RAZORPAY_KEY_SECRET
    
    expected = hmac.new(
        key_secret.encode(),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def fetch_payment(payment_id: str) -> dict:
    """Payment details fetch करतो"""
    return client.payment.fetch(payment_id)
