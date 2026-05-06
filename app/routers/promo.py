"""
Promo Code API Endpoints

Provides REST API endpoints for:
- Validating promo codes at checkout (public)
- Applying promo codes to payments (customer auth)
- Creating and managing promo codes (admin only)
- Viewing promo code usage statistics (admin only)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import json

from app.database import get_db
from app.services.auth import get_current_customer, get_current_admin
from app.services import promo

router = APIRouter(prefix="/promo", tags=["promo"])


# Request/Response Models

class ValidatePromoRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    plan: str = Field(..., pattern="^(basic|premium)$")
    customer_id: Optional[str] = None


class ValidatePromoResponse(BaseModel):
    valid: bool
    reason: Optional[str] = None
    promo_code_id: Optional[str] = None
    code: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[int] = None
    discount_amount: Optional[int] = None
    base_amount: Optional[int] = None
    final_amount: Optional[int] = None


class ApplyPromoRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    payment_id: str
    order_amount: int = Field(..., gt=0)


class ApplyPromoResponse(BaseModel):
    success: bool
    final_amount: int
    discount_amount: int
    message: str


class CreatePromoRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    discount_type: str = Field(..., pattern="^(percentage|fixed)$")
    discount_value: int = Field(..., gt=0)
    applicable_plans: List[str]
    expiry_date: Optional[datetime] = None
    usage_limit: Optional[int] = Field(None, gt=0)
    is_multi_use: bool = False


class CreatePromoResponse(BaseModel):
    success: bool
    promo_code_id: str
    code: str
    message: str


class PromoCodeInfo(BaseModel):
    id: str
    code: str
    discount_type: str
    discount_value: int
    expiry_date: Optional[str] = None
    usage_limit: Optional[int] = None
    usage_count: int
    is_multi_use: bool
    is_active: bool
    applicable_plans: List[str]
    created_at: str


class PromoListResponse(BaseModel):
    promo_codes: List[PromoCodeInfo]
    total: int


class PromoUsageResponse(BaseModel):
    code: str
    usage_count: int
    usage_limit: Optional[int] = None
    unique_customers: int
    total_discount_given: int
    is_active: bool
    expiry_date: Optional[str] = None


# Public Endpoints

@router.post("/validate", response_model=ValidatePromoResponse)
def validate_promo_code(
    data: ValidatePromoRequest,
    db: Session = Depends(get_db)
):
    """
    Validate promo code and calculate discount (Public endpoint)
    
    - **code**: Promo code to validate (case-insensitive)
    - **plan**: Plan to apply discount to ("basic" or "premium")
    - **customer_id**: Optional customer ID to check single-use restrictions
    """
    try:
        result = promo.validate_promo_code(
            db=db,
            code=data.code,
            plan=data.plan,
            customer_id=data.customer_id
        )
        
        return ValidatePromoResponse(**result)
    except Exception as e:
        # Return validation failure instead of raising error
        return ValidatePromoResponse(
            valid=False,
            reason=f"Validation error: {str(e)}"
        )


# Customer Endpoints

@router.post("/apply", response_model=ApplyPromoResponse)
def apply_promo_code(
    data: ApplyPromoRequest,
    customer_id: str = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Apply promo code to payment and record usage (Customer auth required)
    
    - **code**: Promo code to apply
    - **payment_id**: Payment ID to associate with promo usage
    - **order_amount**: Original order amount in paise
    """
    try:
        final_amount = promo.apply_promo_code(
            db=db,
            code=data.code,
            customer_id=customer_id,
            payment_id=data.payment_id,
            order_amount=data.order_amount
        )
        
        discount_amount = data.order_amount - final_amount
        
        return ApplyPromoResponse(
            success=True,
            final_amount=final_amount,
            discount_amount=discount_amount,
            message=f"Promo code applied successfully. Discount: ₹{discount_amount/100:.2f}"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply promo code: {str(e)}")


# Admin Endpoints

@router.post("/admin/create", response_model=CreatePromoResponse)
def create_promo_code(
    data: CreatePromoRequest,
    admin_payload: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new promo code (Admin only)
    
    - **code**: Unique promo code (will be stored in uppercase)
    - **discount_type**: "percentage" or "fixed"
    - **discount_value**: Percentage (1-100) or fixed amount in paise
    - **applicable_plans**: List of plans this code applies to
    - **expiry_date**: Optional expiry date
    - **usage_limit**: Optional maximum number of uses
    - **is_multi_use**: Whether customers can use this code multiple times
    """
    try:
        admin_id = admin_payload.get("sub")
        
        promo_code = promo.create_promo_code(
            db=db,
            code=data.code,
            discount_type=data.discount_type,
            discount_value=data.discount_value,
            applicable_plans=data.applicable_plans,
            expiry_date=data.expiry_date,
            usage_limit=data.usage_limit,
            is_multi_use=data.is_multi_use,
            created_by=admin_id
        )
        
        return CreatePromoResponse(
            success=True,
            promo_code_id=promo_code.id,
            code=promo_code.code,
            message=f"Promo code '{promo_code.code}' created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create promo code: {str(e)}")


@router.get("/admin/list", response_model=PromoListResponse)
def list_promo_codes(
    active_only: bool = False,
    admin_payload: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    List all promo codes (Admin only)
    
    - **active_only**: If true, only return active promo codes
    """
    try:
        promo_codes = promo.list_promo_codes(db=db, active_only=active_only)
        
        promo_list = []
        for pc in promo_codes:
            promo_list.append(PromoCodeInfo(
                id=pc.id,
                code=pc.code,
                discount_type=pc.discount_type,
                discount_value=pc.discount_value,
                expiry_date=pc.expiry_date.isoformat() if pc.expiry_date else None,
                usage_limit=pc.usage_limit,
                usage_count=pc.usage_count,
                is_multi_use=pc.is_multi_use,
                is_active=pc.is_active,
                applicable_plans=json.loads(pc.applicable_plans),
                created_at=pc.created_at.isoformat()
            ))
        
        return PromoListResponse(
            promo_codes=promo_list,
            total=len(promo_list)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list promo codes: {str(e)}")


@router.put("/admin/{promo_id}/deactivate")
def deactivate_promo_code(
    promo_id: str,
    admin_payload: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Deactivate a promo code (Admin only)
    
    - **promo_id**: ID of the promo code to deactivate
    """
    try:
        from app.models import PromoCode
        
        promo_code = db.query(PromoCode).filter(PromoCode.id == promo_id).first()
        if not promo_code:
            raise HTTPException(status_code=404, detail="Promo code not found")
        
        promo.deactivate_promo_code(db=db, code=promo_code.code)
        
        return {
            "success": True,
            "message": f"Promo code '{promo_code.code}' deactivated successfully"
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deactivate promo code: {str(e)}")


@router.get("/admin/{promo_id}/usage", response_model=PromoUsageResponse)
def get_promo_usage(
    promo_id: str,
    admin_payload: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get usage statistics for a promo code (Admin only)
    
    - **promo_id**: ID of the promo code
    """
    try:
        usage_stats = promo.get_promo_code_usage(db=db, promo_code_id=promo_id)
        
        return PromoUsageResponse(**usage_stats)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get promo usage: {str(e)}")
