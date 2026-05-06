"""
Settings API Router - Admin settings management endpoints

This router provides endpoints for:
- Get SMTP settings
- Save SMTP settings
- Test SMTP connection
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.database import get_db
from app.services.auth import get_current_admin
from app.services.settings import (
    get_smtp_settings,
    save_smtp_settings,
    test_smtp_connection,
    get_business_settings,
    save_business_settings,
    get_plan_settings,
    save_plan_settings,
    get_system_settings,
    save_system_settings,
    get_payment_gateway_settings,
    save_payment_gateway_settings,
    get_plan_features,
    save_plan_features,
    get_allowed_origins,
    save_allowed_origins
)

router = APIRouter(prefix="/api/admin/settings", tags=["admin-settings"])


class SMTPSettingsResponse(BaseModel):
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str  # Will be masked in response
    smtp_from_email: str
    smtp_use_tls: bool


class SMTPSettingsRequest(BaseModel):
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_from_email: EmailStr
    smtp_use_tls: bool


class SMTPTestRequest(BaseModel):
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_use_tls: bool


class BusinessSettingsResponse(BaseModel):
    app_name: str
    support_email: str
    frontend_url: str
    company_address: str
    company_gst: str
    company_phone: str
    invoice_footer: str


class BusinessSettingsRequest(BaseModel):
    app_name: str
    support_email: EmailStr
    frontend_url: str
    company_address: str = ""
    company_gst: str = ""
    company_phone: str = ""
    invoice_footer: str = ""


class PlanSettingsResponse(BaseModel):
    trial_days: int
    free_offline_grace: int
    basic_offline_grace: int
    premium_offline_grace: int
    basic_price: int
    premium_price: int


class PlanSettingsRequest(BaseModel):
    trial_days: int
    free_offline_grace: int
    basic_offline_grace: int
    premium_offline_grace: int
    basic_price: int
    premium_price: int


class SystemSettingsResponse(BaseModel):
    access_token_expire_minutes: int
    maintenance_mode: bool
    max_login_attempts: int
    session_timeout_minutes: int


class SystemSettingsRequest(BaseModel):
    access_token_expire_minutes: int
    maintenance_mode: bool
    max_login_attempts: int
    session_timeout_minutes: int


class PaymentGatewaySettingsResponse(BaseModel):
    razorpay_key_id: str
    razorpay_key_secret: str  # Will be masked
    payment_gateway_enabled: bool
    payment_gateway_mode: str


class PaymentGatewaySettingsRequest(BaseModel):
    razorpay_key_id: str
    razorpay_key_secret: str
    payment_gateway_enabled: bool
    payment_gateway_mode: str  # test or live


class PlanFeaturesResponse(BaseModel):
    trial: list
    free: list
    basic: list
    premium: list


class PlanFeaturesRequest(BaseModel):
    trial: list
    free: list
    basic: list
    premium: list


class AllowedOriginsResponse(BaseModel):
    origins: list


class AllowedOriginsRequest(BaseModel):
    origins: list


@router.get("/smtp", response_model=SMTPSettingsResponse)
async def get_smtp_config(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Get SMTP settings (admin only)
    
    Preconditions:
    - User is authenticated as admin
    
    Postconditions:
    - Returns SMTP configuration
    - Password is masked (first 2 chars + ***)
    """
    settings = get_smtp_settings(db)
    
    # Mask password for security
    password = settings.get("smtp_password", "")
    masked_password = password[:2] + "***" if len(password) > 2 else "***"
    
    return {
        "smtp_host": settings["smtp_host"],
        "smtp_port": settings["smtp_port"],
        "smtp_username": settings["smtp_username"],
        "smtp_password": masked_password,
        "smtp_from_email": settings["smtp_from_email"],
        "smtp_use_tls": settings["smtp_use_tls"]
    }


@router.post("/smtp")
async def save_smtp_config(
    request: SMTPSettingsRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Save SMTP settings (admin only)
    
    Preconditions:
    - User is authenticated as admin
    - All SMTP fields are valid
    
    Postconditions:
    - SMTP settings saved to database
    - Password is encrypted
    - Returns success message
    """
    try:
        save_smtp_settings(
            db=db,
            smtp_host=request.smtp_host,
            smtp_port=request.smtp_port,
            smtp_username=request.smtp_username,
            smtp_password=request.smtp_password,
            smtp_from_email=request.smtp_from_email,
            smtp_use_tls=request.smtp_use_tls,
            updated_by=admin.get("username", "admin")
        )
        
        return {
            "success": True,
            "message": "SMTP settings saved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save SMTP settings: {str(e)}"
        )


@router.post("/smtp/test")
async def test_smtp_config(
    request: SMTPTestRequest,
    admin: dict = Depends(get_current_admin)
):
    """
    Test SMTP connection (admin only)
    
    Preconditions:
    - User is authenticated as admin
    - SMTP parameters are provided
    
    Postconditions:
    - Tests connection to SMTP server
    - Returns success/failure status
    - Does not send actual email
    """
    result = await test_smtp_connection(
        smtp_host=request.smtp_host,
        smtp_port=request.smtp_port,
        smtp_username=request.smtp_username,
        smtp_password=request.smtp_password,
        smtp_use_tls=request.smtp_use_tls
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result



# ============================================================================
# BUSINESS SETTINGS ENDPOINTS
# ============================================================================

@router.get("/business", response_model=BusinessSettingsResponse)
async def get_business_config(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Get business/company settings (admin only)
    
    Preconditions:
    - User is authenticated as admin
    
    Postconditions:
    - Returns business configuration
    """
    settings = get_business_settings(db)
    return settings


@router.post("/business")
async def save_business_config(
    request: BusinessSettingsRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Save business/company settings (admin only)
    
    Preconditions:
    - User is authenticated as admin
    - All business fields are valid
    
    Postconditions:
    - Business settings saved to database
    - Returns success message
    """
    try:
        save_business_settings(
            db=db,
            app_name=request.app_name,
            support_email=request.support_email,
            frontend_url=request.frontend_url,
            company_address=request.company_address,
            company_gst=request.company_gst,
            company_phone=request.company_phone,
            invoice_footer=request.invoice_footer,
            updated_by=admin.get("username", "admin")
        )
        
        return {
            "success": True,
            "message": "Business settings saved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save business settings: {str(e)}"
        )


# ============================================================================
# PLAN SETTINGS ENDPOINTS
# ============================================================================

@router.get("/plans", response_model=PlanSettingsResponse)
async def get_plan_config(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Get plan configuration settings (admin only)
    
    Preconditions:
    - User is authenticated as admin
    
    Postconditions:
    - Returns plan configuration
    """
    settings = get_plan_settings(db)
    return settings


@router.post("/plans")
async def save_plan_config(
    request: PlanSettingsRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Save plan configuration settings (admin only)
    
    Preconditions:
    - User is authenticated as admin
    - All plan fields are valid positive integers
    
    Postconditions:
    - Plan settings saved to database
    - Returns success message
    """
    try:
        save_plan_settings(
            db=db,
            trial_days=request.trial_days,
            free_offline_grace=request.free_offline_grace,
            basic_offline_grace=request.basic_offline_grace,
            premium_offline_grace=request.premium_offline_grace,
            basic_price=request.basic_price,
            premium_price=request.premium_price,
            updated_by=admin.get("username", "admin")
        )
        
        return {
            "success": True,
            "message": "Plan settings saved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save plan settings: {str(e)}"
        )


# ============================================================================
# SYSTEM SETTINGS ENDPOINTS
# ============================================================================

@router.get("/system", response_model=SystemSettingsResponse)
async def get_system_config(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Get system settings (admin only)
    
    Preconditions:
    - User is authenticated as admin
    
    Postconditions:
    - Returns system configuration
    """
    settings = get_system_settings(db)
    return settings


@router.post("/system")
async def save_system_config(
    request: SystemSettingsRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Save system settings (admin only)
    
    Preconditions:
    - User is authenticated as admin
    - All system fields are valid
    
    Postconditions:
    - System settings saved to database
    - Returns success message
    """
    try:
        save_system_settings(
            db=db,
            access_token_expire_minutes=request.access_token_expire_minutes,
            maintenance_mode=request.maintenance_mode,
            max_login_attempts=request.max_login_attempts,
            session_timeout_minutes=request.session_timeout_minutes,
            updated_by=admin.get("username", "admin")
        )
        
        return {
            "success": True,
            "message": "System settings saved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save system settings: {str(e)}"
        )


# ============================================================================
# PAYMENT GATEWAY SETTINGS ENDPOINTS
# ============================================================================

@router.get("/payment-gateway", response_model=PaymentGatewaySettingsResponse)
async def get_payment_gateway_config(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Get payment gateway settings (admin only)
    
    Preconditions:
    - User is authenticated as admin
    
    Postconditions:
    - Returns payment gateway configuration
    - Secret is masked for security
    """
    settings = get_payment_gateway_settings(db)
    
    # Mask secret for security
    secret = settings.get("razorpay_key_secret", "")
    masked_secret = secret[:4] + "***" if len(secret) > 4 else "***"
    
    return {
        "razorpay_key_id": settings["razorpay_key_id"],
        "razorpay_key_secret": masked_secret,
        "payment_gateway_enabled": settings["payment_gateway_enabled"],
        "payment_gateway_mode": settings["payment_gateway_mode"]
    }


@router.post("/payment-gateway")
async def save_payment_gateway_config(
    request: PaymentGatewaySettingsRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Save payment gateway settings (admin only)
    
    Preconditions:
    - User is authenticated as admin
    - All payment gateway fields are valid
    
    Postconditions:
    - Payment gateway settings saved to database
    - Secret is encrypted
    - Returns success message
    """
    try:
        save_payment_gateway_settings(
            db=db,
            razorpay_key_id=request.razorpay_key_id,
            razorpay_key_secret=request.razorpay_key_secret,
            payment_gateway_enabled=request.payment_gateway_enabled,
            payment_gateway_mode=request.payment_gateway_mode,
            updated_by=admin.get("username", "admin")
        )
        
        return {
            "success": True,
            "message": "Payment gateway settings saved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save payment gateway settings: {str(e)}"
        )


# ============================================================================
# PLAN FEATURES ENDPOINTS
# ============================================================================

@router.get("/plans/features", response_model=PlanFeaturesResponse)
async def get_plan_features_config(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Get plan features configuration (admin only)
    
    Preconditions:
    - User is authenticated as admin
    
    Postconditions:
    - Returns plan features for all plans
    """
    features = get_plan_features(db)
    return features


@router.post("/plans/features")
async def save_plan_features_config(
    request: PlanFeaturesRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Save plan features configuration (admin only)
    
    Preconditions:
    - User is authenticated as admin
    - All plan features are valid
    
    Postconditions:
    - Plan features saved to database
    - Returns success message
    """
    try:
        features = {
            "trial": request.trial,
            "free": request.free,
            "basic": request.basic,
            "premium": request.premium
        }
        
        save_plan_features(
            db=db,
            features=features,
            updated_by=admin.get("username", "admin")
        )
        
        return {
            "success": True,
            "message": "Plan features saved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save plan features: {str(e)}"
        )


# ============================================================================
# CORS ORIGINS ENDPOINTS
# ============================================================================

@router.get("/cors/origins", response_model=AllowedOriginsResponse)
async def get_cors_origins_config(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Get allowed CORS origins (admin only)
    
    Preconditions:
    - User is authenticated as admin
    
    Postconditions:
    - Returns list of allowed origins
    """
    origins = get_allowed_origins(db)
    return {"origins": origins}


@router.post("/cors/origins")
async def save_cors_origins_config(
    request: AllowedOriginsRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Save allowed CORS origins (admin only)
    
    Preconditions:
    - User is authenticated as admin
    - All origins are valid URLs
    
    Postconditions:
    - Origins saved to database
    - Returns success message
    - Note: Server restart required for CORS changes to take effect
    """
    try:
        save_allowed_origins(
            db=db,
            origins=request.origins,
            updated_by=admin.get("username", "admin")
        )
        
        return {
            "success": True,
            "message": "CORS origins saved successfully. Note: Server restart required for changes to take effect."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save CORS origins: {str(e)}"
        )


