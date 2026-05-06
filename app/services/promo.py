"""
Promo Code Service - Manage discount codes for marketing campaigns

This service provides functionality to:
- Create and manage promo codes
- Validate codes at checkout
- Apply discounts to order amounts
- Track usage and enforce limits
"""

from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import json
import logging

from app.models import PromoCode, PromoCodeUsage, Customer

logger = logging.getLogger(__name__)

# Plan prices in paise (₹499 = 49900 paise, ₹999 = 99900 paise)
PLAN_PRICES = {
    "basic": 49900,
    "premium": 99900
}


def create_promo_code(
    db: Session,
    code: str,
    discount_type: str,
    discount_value: int,
    applicable_plans: list,
    expiry_date: datetime = None,
    usage_limit: int = None,
    is_multi_use: bool = False,
    created_by: str = None
) -> PromoCode:
    """
    Create a new promo code
    
    Preconditions:
    - code is non-empty string
    - discount_type is "percentage" or "fixed"
    - discount_value is positive integer
    - applicable_plans is list of plan names
    
    Postconditions:
    - New PromoCode record created
    - code stored in uppercase
    - Returns PromoCode object
    """
    # Validate discount type
    if discount_type not in ["percentage", "fixed"]:
        raise ValueError("discount_type must be 'percentage' or 'fixed'")
    
    # Validate discount value
    if discount_value <= 0:
        raise ValueError("discount_value must be positive")
    
    if discount_type == "percentage" and (discount_value < 1 or discount_value > 100):
        raise ValueError("percentage discount must be between 1 and 100")
    
    # Check if code already exists
    code_upper = code.upper()
    existing = db.query(PromoCode).filter(PromoCode.code == code_upper).first()
    if existing:
        raise ValueError(f"Promo code '{code}' already exists")
    
    # Validate expiry date
    if expiry_date and expiry_date <= datetime.now(timezone.utc):
        raise ValueError("expiry_date must be in the future")
    
    # Create promo code
    promo = PromoCode(
        code=code_upper,
        discount_type=discount_type,
        discount_value=discount_value,
        expiry_date=expiry_date,
        usage_limit=usage_limit,
        usage_count=0,
        is_multi_use=is_multi_use,
        is_active=True,
        applicable_plans=json.dumps(applicable_plans),
        created_by=created_by
    )
    
    db.add(promo)
    db.commit()
    db.refresh(promo)
    
    logger.info(f"Promo code created: {code_upper}")
    return promo


def validate_promo_code(
    db: Session,
    code: str,
    plan: str,
    customer_id: str = None
) -> Dict[str, Any]:
    """
    Validate promo code and calculate discount
    
    Preconditions:
    - code is non-empty string
    - plan is one of: "basic", "premium"
    - customer_id is valid UUID or None
    
    Postconditions:
    - Returns dict with valid=True and discount info if valid
    - Returns dict with valid=False and reason if invalid
    - No database modifications
    """
    # Find promo code (case-insensitive)
    promo = db.query(PromoCode).filter(
        PromoCode.code == code.upper(),
        PromoCode.is_active == True
    ).first()
    
    if not promo:
        return {"valid": False, "reason": "Invalid promo code"}
    
    # Check expiry date
    now = datetime.now(timezone.utc)
    if promo.expiry_date:
        # Make expiry_date timezone-aware if it isn't
        expiry = promo.expiry_date
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if expiry < now:
            return {"valid": False, "reason": "Promo code expired"}
    
    # Check usage limit
    if promo.usage_limit and promo.usage_count >= promo.usage_limit:
        return {"valid": False, "reason": "Promo code usage limit reached"}
    
    # Check if customer already used (for single-use codes)
    if not promo.is_multi_use and customer_id:
        existing_usage = db.query(PromoCodeUsage).filter(
            PromoCodeUsage.promo_code_id == promo.id,
            PromoCodeUsage.customer_id == customer_id
        ).first()
        
        if existing_usage:
            return {"valid": False, "reason": "Promo code already used"}
    
    # Check applicable plans
    applicable_plans = json.loads(promo.applicable_plans)
    if plan not in applicable_plans:
        return {"valid": False, "reason": f"Promo code not applicable to {plan} plan"}
    
    # Calculate discount
    base_amount = PLAN_PRICES.get(plan, 0)
    
    if promo.discount_type == "percentage":
        discount_amount = int(base_amount * promo.discount_value / 100)
    else:  # fixed
        discount_amount = min(promo.discount_value, base_amount)
    
    final_amount = base_amount - discount_amount
    
    return {
        "valid": True,
        "promo_code_id": promo.id,
        "code": promo.code,
        "discount_type": promo.discount_type,
        "discount_value": promo.discount_value,
        "discount_amount": discount_amount,
        "base_amount": base_amount,
        "final_amount": final_amount
    }


def apply_promo_code(
    db: Session,
    code: str,
    customer_id: str,
    payment_id: str,
    order_amount: int
) -> int:
    """
    Apply promo code and record usage
    
    Preconditions:
    - code is valid active promo code
    - customer_id exists in customers table
    - order_amount is positive integer in paise
    - Promo code validation passed
    
    Postconditions:
    - Returns discounted amount in paise
    - Promo code usage_count incremented by 1
    - New PromoCodeUsage record created
    - Discount amount never exceeds order_amount
    """
    # Find promo code
    promo = db.query(PromoCode).filter(
        PromoCode.code == code.upper(),
        PromoCode.is_active == True
    ).first()
    
    if not promo:
        raise ValueError("Invalid promo code")
    
    # Calculate discount
    if promo.discount_type == "percentage":
        discount_amount = int(order_amount * promo.discount_value / 100)
    else:  # fixed
        discount_amount = min(promo.discount_value, order_amount)
    
    # Ensure discount doesn't exceed order amount
    discount_amount = min(discount_amount, order_amount)
    final_amount = order_amount - discount_amount
    
    # Increment usage count
    promo.usage_count += 1
    
    # Record usage
    usage = PromoCodeUsage(
        promo_code_id=promo.id,
        customer_id=customer_id,
        payment_id=payment_id,
        discount_amount=discount_amount
    )
    
    db.add(usage)
    db.commit()
    
    logger.info(f"Promo code applied: {code.upper()}, discount: ₹{discount_amount/100}")
    return final_amount


def deactivate_promo_code(db: Session, code: str) -> bool:
    """
    Deactivate a promo code
    
    Preconditions:
    - code is non-empty string
    
    Postconditions:
    - Promo code is_active set to False
    - Returns True if successful
    """
    promo = db.query(PromoCode).filter(PromoCode.code == code.upper()).first()
    
    if not promo:
        raise ValueError("Promo code not found")
    
    promo.is_active = False
    db.commit()
    
    logger.info(f"Promo code deactivated: {code.upper()}")
    return True


def get_promo_code_usage(db: Session, promo_code_id: str) -> Dict[str, Any]:
    """
    Get usage statistics for a promo code
    
    Preconditions:
    - promo_code_id is valid UUID
    
    Postconditions:
    - Returns dict with usage statistics
    - No database modifications
    """
    promo = db.query(PromoCode).filter(PromoCode.id == promo_code_id).first()
    
    if not promo:
        raise ValueError("Promo code not found")
    
    usages = db.query(PromoCodeUsage).filter(
        PromoCodeUsage.promo_code_id == promo_code_id
    ).all()
    
    total_discount = sum(usage.discount_amount for usage in usages)
    unique_customers = len(set(usage.customer_id for usage in usages))
    
    return {
        "code": promo.code,
        "usage_count": promo.usage_count,
        "usage_limit": promo.usage_limit,
        "unique_customers": unique_customers,
        "total_discount_given": total_discount,
        "is_active": promo.is_active,
        "expiry_date": promo.expiry_date.isoformat() if promo.expiry_date else None
    }


def list_promo_codes(
    db: Session,
    active_only: bool = False
) -> list:
    """
    List all promo codes
    
    Preconditions:
    - active_only is boolean
    
    Postconditions:
    - Returns list of PromoCode objects
    - No database modifications
    """
    query = db.query(PromoCode)
    
    if active_only:
        query = query.filter(PromoCode.is_active == True)
    
    return query.order_by(PromoCode.created_at.desc()).all()
