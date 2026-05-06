"""
Settings Service - Manage application settings in database

This service provides functionality to:
- Get/Set settings with encryption support
- Manage SMTP configuration
- Test SMTP connection
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from app.models import Settings
from app.services.encryption import encrypt_value, decrypt_value
import logging
import json

logger = logging.getLogger(__name__)


def get_setting(db: Session, key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get a setting value by key
    
    Preconditions:
    - key is non-empty string
    
    Postconditions:
    - Returns decrypted value if is_encrypted=True
    - Returns plain value if is_encrypted=False
    - Returns default if key not found
    """
    setting = db.query(Settings).filter(Settings.key == key).first()
    
    if not setting:
        return default
    
    if setting.is_encrypted and setting.value:
        try:
            return decrypt_value(setting.value)
        except Exception as e:
            logger.error(f"Failed to decrypt setting {key}: {str(e)}")
            return default
    
    return setting.value


def set_setting(
    db: Session,
    key: str,
    value: str,
    is_encrypted: bool = False,
    category: Optional[str] = None,
    description: Optional[str] = None,
    updated_by: Optional[str] = None
) -> Settings:
    """
    Set a setting value (create or update)
    
    Preconditions:
    - key is non-empty string
    - value is string (can be empty)
    
    Postconditions:
    - Setting created or updated in database
    - Value encrypted if is_encrypted=True
    - Returns Settings object
    """
    # Check if setting exists
    setting = db.query(Settings).filter(Settings.key == key).first()
    
    # Encrypt value if needed
    stored_value = encrypt_value(value) if is_encrypted and value else value
    
    if setting:
        # Update existing
        setting.value = stored_value
        setting.is_encrypted = is_encrypted
        if category:
            setting.category = category
        if description:
            setting.description = description
        if updated_by:
            setting.updated_by = updated_by
    else:
        # Create new
        setting = Settings(
            key=key,
            value=stored_value,
            is_encrypted=is_encrypted,
            category=category,
            description=description,
            updated_by=updated_by
        )
        db.add(setting)
    
    db.commit()
    db.refresh(setting)
    
    logger.info(f"Setting updated: {key} (encrypted={is_encrypted})")
    return setting


def get_smtp_settings(db: Session) -> Dict[str, Any]:
    """
    Get all SMTP settings
    
    Preconditions:
    - Database connection is valid
    
    Postconditions:
    - Returns dict with SMTP configuration
    - Password is decrypted if stored
    - Returns default values from config if not in database
    """
    from app.config import settings as config_settings
    
    return {
        "smtp_host": get_setting(db, "smtp_host", config_settings.SMTP_HOST),
        "smtp_port": int(get_setting(db, "smtp_port", str(config_settings.SMTP_PORT))),
        "smtp_username": get_setting(db, "smtp_username", config_settings.SMTP_USERNAME),
        "smtp_password": get_setting(db, "smtp_password", config_settings.SMTP_PASSWORD),
        "smtp_from_email": get_setting(db, "smtp_from_email", config_settings.SMTP_FROM_EMAIL),
        "smtp_use_tls": get_setting(db, "smtp_use_tls", str(config_settings.SMTP_USE_TLS)).lower() == "true"
    }


def get_business_settings(db: Session) -> Dict[str, Any]:
    """
    Get all business/company settings
    
    Preconditions:
    - Database connection is valid
    
    Postconditions:
    - Returns dict with business configuration
    - Returns default values from config if not in database
    """
    from app.config import settings as config_settings
    
    return {
        "app_name": get_setting(db, "app_name", config_settings.APP_NAME),
        "support_email": get_setting(db, "support_email", config_settings.SUPPORT_EMAIL),
        "frontend_url": get_setting(db, "frontend_url", config_settings.FRONTEND_URL),
        "company_address": get_setting(db, "company_address", ""),
        "company_gst": get_setting(db, "company_gst", ""),
        "company_phone": get_setting(db, "company_phone", ""),
        "invoice_footer": get_setting(db, "invoice_footer", "Thank you for your business!")
    }


def save_business_settings(
    db: Session,
    app_name: str,
    support_email: str,
    frontend_url: str,
    company_address: str = "",
    company_gst: str = "",
    company_phone: str = "",
    invoice_footer: str = "",
    updated_by: Optional[str] = None
) -> bool:
    """
    Save business settings to database
    
    Preconditions:
    - All business parameters are valid
    
    Postconditions:
    - All business settings saved to database
    - Returns True if successful
    """
    try:
        set_setting(db, "app_name", app_name, False, "business", "Application Name", updated_by)
        set_setting(db, "support_email", support_email, False, "business", "Support Email", updated_by)
        set_setting(db, "frontend_url", frontend_url, False, "business", "Frontend URL", updated_by)
        set_setting(db, "company_address", company_address, False, "business", "Company Address", updated_by)
        set_setting(db, "company_gst", company_gst, False, "business", "GST Number", updated_by)
        set_setting(db, "company_phone", company_phone, False, "business", "Company Phone", updated_by)
        set_setting(db, "invoice_footer", invoice_footer, False, "business", "Invoice Footer Text", updated_by)
        
        logger.info("Business settings saved successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to save business settings: {str(e)}")
        raise


def get_plan_settings(db: Session) -> Dict[str, Any]:
    """
    Get all plan configuration settings
    
    Preconditions:
    - Database connection is valid
    
    Postconditions:
    - Returns dict with plan configuration
    - Returns default values from config if not in database
    """
    from app.config import PLAN_PRICES, settings as config_settings
    
    return {
        "trial_days": int(get_setting(db, "trial_days", str(config_settings.TRIAL_DAYS))),
        "free_offline_grace": int(get_setting(db, "free_offline_grace", str(config_settings.FREE_OFFLINE_GRACE))),
        "basic_offline_grace": int(get_setting(db, "basic_offline_grace", str(config_settings.BASIC_OFFLINE_GRACE))),
        "premium_offline_grace": int(get_setting(db, "premium_offline_grace", str(config_settings.PREMIUM_OFFLINE_GRACE))),
        "basic_price": int(get_setting(db, "basic_price", str(PLAN_PRICES["basic"]))),
        "premium_price": int(get_setting(db, "premium_price", str(PLAN_PRICES["premium"])))
    }


def save_plan_settings(
    db: Session,
    trial_days: int,
    free_offline_grace: int,
    basic_offline_grace: int,
    premium_offline_grace: int,
    basic_price: int,
    premium_price: int,
    updated_by: Optional[str] = None
) -> bool:
    """
    Save plan configuration settings to database
    
    Preconditions:
    - All plan parameters are valid positive integers
    
    Postconditions:
    - All plan settings saved to database
    - Returns True if successful
    """
    try:
        set_setting(db, "trial_days", str(trial_days), False, "plan", "Trial Period Days", updated_by)
        set_setting(db, "free_offline_grace", str(free_offline_grace), False, "plan", "Free Plan Grace Days", updated_by)
        set_setting(db, "basic_offline_grace", str(basic_offline_grace), False, "plan", "Basic Plan Grace Days", updated_by)
        set_setting(db, "premium_offline_grace", str(premium_offline_grace), False, "plan", "Premium Plan Grace Days", updated_by)
        set_setting(db, "basic_price", str(basic_price), False, "plan", "Basic Plan Price (paise)", updated_by)
        set_setting(db, "premium_price", str(premium_price), False, "plan", "Premium Plan Price (paise)", updated_by)
        
        logger.info("Plan settings saved successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to save plan settings: {str(e)}")
        raise


def get_system_settings(db: Session) -> Dict[str, Any]:
    """
    Get all system settings
    
    Preconditions:
    - Database connection is valid
    
    Postconditions:
    - Returns dict with system configuration
    - Returns default values from config if not in database
    """
    from app.config import settings as config_settings
    
    return {
        "access_token_expire_minutes": int(get_setting(db, "access_token_expire_minutes", str(config_settings.ACCESS_TOKEN_EXPIRE_MINUTES))),
        "maintenance_mode": get_setting(db, "maintenance_mode", "false").lower() == "true",
        "max_login_attempts": int(get_setting(db, "max_login_attempts", "5")),
        "session_timeout_minutes": int(get_setting(db, "session_timeout_minutes", "30"))
    }


def save_system_settings(
    db: Session,
    access_token_expire_minutes: int,
    maintenance_mode: bool,
    max_login_attempts: int,
    session_timeout_minutes: int,
    updated_by: Optional[str] = None
) -> bool:
    """
    Save system settings to database
    
    Preconditions:
    - All system parameters are valid
    
    Postconditions:
    - All system settings saved to database
    - Returns True if successful
    """
    try:
        set_setting(db, "access_token_expire_minutes", str(access_token_expire_minutes), False, "system", "Token Expiry (minutes)", updated_by)
        set_setting(db, "maintenance_mode", str(maintenance_mode), False, "system", "Maintenance Mode", updated_by)
        set_setting(db, "max_login_attempts", str(max_login_attempts), False, "system", "Max Login Attempts", updated_by)
        set_setting(db, "session_timeout_minutes", str(session_timeout_minutes), False, "system", "Session Timeout (minutes)", updated_by)
        
        logger.info("System settings saved successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to save system settings: {str(e)}")
        raise


def save_smtp_settings(
    db: Session,
    smtp_host: str,
    smtp_port: int,
    smtp_username: str,
    smtp_password: str,
    smtp_from_email: str,
    smtp_use_tls: bool,
    updated_by: Optional[str] = None
) -> bool:
    """
    Save SMTP settings to database
    
    Preconditions:
    - All SMTP parameters are valid
    - smtp_port is integer
    
    Postconditions:
    - All SMTP settings saved to database
    - Password is encrypted
    - Returns True if successful
    """
    try:
        set_setting(db, "smtp_host", smtp_host, False, "smtp", "SMTP Server Host", updated_by)
        set_setting(db, "smtp_port", str(smtp_port), False, "smtp", "SMTP Server Port", updated_by)
        set_setting(db, "smtp_username", smtp_username, False, "smtp", "SMTP Username", updated_by)
        set_setting(db, "smtp_password", smtp_password, True, "smtp", "SMTP Password (Encrypted)", updated_by)
        set_setting(db, "smtp_from_email", smtp_from_email, False, "smtp", "From Email Address", updated_by)
        set_setting(db, "smtp_use_tls", str(smtp_use_tls), False, "smtp", "Use TLS", updated_by)
        
        logger.info("SMTP settings saved successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to save SMTP settings: {str(e)}")
        raise


async def test_smtp_connection(
    smtp_host: str,
    smtp_port: int,
    smtp_username: str,
    smtp_password: str,
    smtp_use_tls: bool
) -> Dict[str, Any]:
    """
    Test SMTP connection with provided settings
    
    Preconditions:
    - SMTP parameters are valid
    
    Postconditions:
    - Returns dict with success status and message
    - Does not send actual email
    """
    import aiosmtplib
    
    try:
        # Create SMTP client based on port and TLS settings
        if smtp_port == 465:
            # Port 465: Direct TLS/SSL from the start
            smtp = aiosmtplib.SMTP(hostname=smtp_host, port=smtp_port, use_tls=True, timeout=10)
            await smtp.connect()
        elif smtp_port == 587 and smtp_use_tls:
            # Port 587 with TLS: Use STARTTLS
            smtp = aiosmtplib.SMTP(hostname=smtp_host, port=smtp_port, timeout=10)
            await smtp.connect()
            # Check if we can call starttls (connection should be plain at this point)
            if hasattr(smtp, 'is_ehlo_or_helo_needed') or not smtp.is_connected:
                pass  # Connection not ready
            await smtp.starttls()
        else:
            # Plain connection (port 25 or TLS disabled)
            smtp = aiosmtplib.SMTP(hostname=smtp_host, port=smtp_port, timeout=10)
            await smtp.connect()
        
        # Authenticate
        await smtp.login(smtp_username, smtp_password)
        
        # Disconnect
        await smtp.quit()
        
        return {
            "success": True,
            "message": "✅ SMTP connection and authentication successful!"
        }
        
    except aiosmtplib.SMTPAuthenticationError as e:
        error_msg = str(e)
        if "BadCredentials" in error_msg or "535" in error_msg:
            return {
                "success": False,
                "message": "❌ Authentication failed: Invalid username or password.\n\nFor Gmail:\n1. Go to Google Account → Security\n2. Enable 2-Step Verification\n3. Generate App Password for 'Mail'\n4. Use that 16-character password here"
            }
        return {
            "success": False,
            "message": f"❌ Authentication failed: {error_msg}"
        }
        
    except aiosmtplib.SMTPConnectError as e:
        return {
            "success": False,
            "message": f"❌ Connection failed: Cannot connect to {smtp_host}:{smtp_port}. Check host and port."
        }
    
    except RuntimeError as e:
        # Handle "Connection already using TLS" error
        error_str = str(e)
        if "already using TLS" in error_str:
            # This means connection auto-upgraded to TLS, try without explicit starttls
            try:
                smtp2 = aiosmtplib.SMTP(hostname=smtp_host, port=smtp_port, timeout=10)
                await smtp2.connect()
                await smtp2.login(smtp_username, smtp_password)
                await smtp2.quit()
                return {
                    "success": True,
                    "message": "✅ SMTP connection and authentication successful!"
                }
            except Exception as e2:
                return {
                    "success": False,
                    "message": f"❌ Connection failed: {str(e2)}"
                }
        return {
            "success": False,
            "message": f"❌ Runtime error: {error_str}"
        }
        
    except Exception as e:
        error_str = str(e)
        
        # Handle "Connection already using TLS" error
        if "already using TLS" in error_str:
            # This means connection auto-upgraded to TLS, try without explicit starttls
            try:
                smtp2 = aiosmtplib.SMTP(hostname=smtp_host, port=smtp_port, timeout=10)
                await smtp2.connect()
                await smtp2.login(smtp_username, smtp_password)
                await smtp2.quit()
                return {
                    "success": True,
                    "message": "✅ SMTP connection and authentication successful!"
                }
            except Exception as e2:
                return {
                    "success": False,
                    "message": f"❌ Connection failed: {str(e2)}"
                }
        
        if "WRONG_VERSION_NUMBER" in error_str or "SSL" in error_str:
            return {
                "success": False,
                "message": f"❌ TLS/SSL error: Try port 587 with TLS enabled, or port 465 for direct SSL.\n\nError: {error_str}"
            }
        return {
            "success": False,
            "message": f"❌ Connection failed: {error_str}"
        }


def get_payment_gateway_settings(db: Session) -> Dict[str, Any]:
    """
    Get payment gateway settings
    
    Preconditions:
    - Database connection is valid
    
    Postconditions:
    - Returns dict with payment gateway configuration
    - Secrets are decrypted if stored
    - Returns default values from config if not in database
    """
    from app.config import settings as config_settings
    
    return {
        "razorpay_key_id": get_setting(db, "razorpay_key_id", config_settings.RAZORPAY_KEY_ID),
        "razorpay_key_secret": get_setting(db, "razorpay_key_secret", config_settings.RAZORPAY_KEY_SECRET),
        "payment_gateway_enabled": get_setting(db, "payment_gateway_enabled", "true").lower() == "true",
        "payment_gateway_mode": get_setting(db, "payment_gateway_mode", "test")  # test or live
    }


def save_payment_gateway_settings(
    db: Session,
    razorpay_key_id: str,
    razorpay_key_secret: str,
    payment_gateway_enabled: bool,
    payment_gateway_mode: str,
    updated_by: Optional[str] = None
) -> bool:
    """
    Save payment gateway settings to database
    
    Preconditions:
    - All payment gateway parameters are valid
    
    Postconditions:
    - All payment gateway settings saved to database
    - Secrets are encrypted
    - Returns True if successful
    """
    try:
        set_setting(db, "razorpay_key_id", razorpay_key_id, False, "payment", "Razorpay Key ID", updated_by)
        set_setting(db, "razorpay_key_secret", razorpay_key_secret, True, "payment", "Razorpay Key Secret (Encrypted)", updated_by)
        set_setting(db, "payment_gateway_enabled", str(payment_gateway_enabled), False, "payment", "Payment Gateway Enabled", updated_by)
        set_setting(db, "payment_gateway_mode", payment_gateway_mode, False, "payment", "Payment Gateway Mode (test/live)", updated_by)
        
        logger.info("Payment gateway settings saved successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to save payment gateway settings: {str(e)}")
        raise


def get_plan_features(db: Session) -> Dict[str, List[str]]:
    """
    Get plan features configuration
    
    Preconditions:
    - Database connection is valid
    
    Postconditions:
    - Returns dict with plan features
    - Returns default from config if not in database
    """
    from app.config import PLAN_FEATURES
    import json
    
    features_json = get_setting(db, "plan_features", None)
    if features_json:
        try:
            return json.loads(features_json)
        except:
            return PLAN_FEATURES
    else:
        return PLAN_FEATURES


def save_plan_features(
    db: Session,
    features: Dict[str, List[str]],
    updated_by: Optional[str] = None
) -> bool:
    """
    Save plan features configuration to database
    
    Preconditions:
    - features is valid dict with plan names as keys
    
    Postconditions:
    - Plan features saved to database as JSON
    - Returns True if successful
    """
    import json
    
    try:
        features_json = json.dumps(features)
        set_setting(db, "plan_features", features_json, False, "plans", "Plan Features Configuration", updated_by)
        
        logger.info("Plan features saved successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to save plan features: {str(e)}")
        raise


def get_allowed_origins(db: Session) -> List[str]:
    """
    Get allowed CORS origins
    
    Preconditions:
    - Database connection is valid
    
    Postconditions:
    - Returns list of allowed origins
    - Returns default from config if not in database
    """
    from app.config import settings as config_settings
    
    origins_str = get_setting(db, "allowed_origins", config_settings.ALLOWED_ORIGINS)
    return [o.strip() for o in origins_str.split(",") if o.strip()]


def save_allowed_origins(
    db: Session,
    origins: List[str],
    updated_by: Optional[str] = None
) -> bool:
    """
    Save allowed CORS origins to database
    
    Preconditions:
    - origins is list of valid URLs
    
    Postconditions:
    - Origins saved to database as comma-separated string
    - Returns True if successful
    """
    try:
        origins_str = ",".join(origins)
        set_setting(db, "allowed_origins", origins_str, False, "system", "Allowed CORS Origins", updated_by)
        
        logger.info("Allowed origins saved successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to save allowed origins: {str(e)}")
        raise

