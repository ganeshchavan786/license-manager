from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


def gen_uuid():
    return str(uuid.uuid4())


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, default=gen_uuid)
    business_name = Column(String(200), nullable=False)
    owner_name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    city = Column(String(100))
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    licenses = relationship("License", back_populates="customer")
    subscriptions = relationship("Subscription", back_populates="customer")
    payments = relationship("Payment", back_populates="customer")


class License(Base):
    __tablename__ = "licenses"

    id = Column(String, primary_key=True, default=gen_uuid)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    machine_id = Column(String(255), nullable=False, index=True)
    license_key = Column(String(500), nullable=False, unique=True)
    plan = Column(String(50), default="trial")  # trial, free, basic, premium
    is_active = Column(Boolean, default=True)
    is_paused = Column(Boolean, default=False)
    paused_at = Column(DateTime(timezone=True), nullable=True)
    pause_days_remaining = Column(Integer, nullable=True)
    trial_start = Column(DateTime(timezone=True))
    trial_end = Column(DateTime(timezone=True))
    valid_till = Column(DateTime(timezone=True))
    last_validated = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("Customer", back_populates="licenses")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=gen_uuid)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    license_id = Column(String, ForeignKey("licenses.id"))
    razorpay_subscription_id = Column(String(200), unique=True)
    razorpay_plan_id = Column(String(200))
    plan = Column(String(50), nullable=False)  # basic, premium
    status = Column(String(50), default="created")  # created, active, cancelled, expired
    current_start = Column(DateTime(timezone=True))
    current_end = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("Customer", back_populates="subscriptions")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=gen_uuid)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    razorpay_payment_id = Column(String(200), unique=True)
    razorpay_order_id = Column(String(200))
    razorpay_signature = Column(String(500))
    plan = Column(String(50))
    amount = Column(BigInteger)  # paise मध्ये
    currency = Column(String(10), default="INR")
    status = Column(String(50), default="pending")  # pending, captured, failed, refunded
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", back_populates="payments")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=gen_uuid)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=True)
    action = Column(String(100), nullable=False)
    details = Column(Text)
    ip_address = Column(String(50))
    machine_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(String, primary_key=True, default=gen_uuid)
    full_name = Column(String(200), nullable=False)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="admin")  # admin, staff
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Advanced Features Phase 1 Models

class UsageAnalytics(Base):
    __tablename__ = "usage_analytics"

    id = Column(String, primary_key=True, default=gen_uuid)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    license_id = Column(String, ForeignKey("licenses.id"), nullable=True)
    feature_name = Column(String(200), nullable=False)
    action = Column(String(100), nullable=False)
    meta_data = Column('metadata', Text, nullable=True)  # Map to 'metadata' column in DB
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(String, primary_key=True, default=gen_uuid)
    code = Column(String(50), unique=True, nullable=False, index=True)
    discount_type = Column(String(20), nullable=False)  # "percentage" or "fixed"
    discount_value = Column(Integer, nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    usage_limit = Column(Integer, nullable=True)
    usage_count = Column(Integer, default=0)
    is_multi_use = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    applicable_plans = Column(Text, nullable=False)  # JSON array
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PromoCodeUsage(Base):
    __tablename__ = "promo_code_usage"

    id = Column(String, primary_key=True, default=gen_uuid)
    promo_code_id = Column(String, ForeignKey("promo_codes.id"), nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    payment_id = Column(String, ForeignKey("payments.id"), nullable=True)
    discount_amount = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EmailQueue(Base):
    __tablename__ = "email_queue"

    id = Column(String, primary_key=True, default=gen_uuid)
    to_email = Column(String(200), nullable=False)
    subject = Column(String(500), nullable=False)
    body_html = Column(Text, nullable=False)
    body_text = Column(Text, nullable=True)
    attachments = Column(Text, nullable=True)  # JSON array
    status = Column(String(20), default="pending")  # pending, sent, failed
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    error_message = Column(Text, nullable=True)
    scheduled_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, default=gen_uuid)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    payment_id = Column(String, ForeignKey("payments.id"), nullable=False)
    plan = Column(String(50), nullable=False)
    base_amount = Column(BigInteger, nullable=False)
    gst_rate = Column(Integer, nullable=False)  # 18 for 18%
    gst_amount = Column(BigInteger, nullable=False)
    total_amount = Column(BigInteger, nullable=False)
    discount_amount = Column(BigInteger, default=0)
    promo_code_id = Column(String, ForeignKey("promo_codes.id"), nullable=True)
    invoice_date = Column(DateTime(timezone=True), server_default=func.now())
    pdf_path = Column(String(500), nullable=True)
    is_emailed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(String, primary_key=True, default=gen_uuid)
    license_id = Column(String, ForeignKey("licenses.id"), nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    email = Column(String(200), nullable=False)
    full_name = Column(String(200), nullable=True)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False)  # admin, manager, employee
    permissions = Column(Text, nullable=False)  # JSON array
    invitation_token = Column(String(100), unique=True, nullable=True)
    invitation_expires = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Settings(Base):
    __tablename__ = "settings"

    id = Column(String, primary_key=True, default=gen_uuid)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    is_encrypted = Column(Boolean, default=False)
    category = Column(String(50), nullable=True, index=True)
    description = Column(String(255), nullable=True)
    updated_by = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Role-based permissions
ROLE_PERMISSIONS = {
    "admin": [
        "view_dashboard",
        "manage_employees",
        "manage_attendance",
        "manage_salary",
        "manage_leaves",
        "manage_loans",
        "export_reports",
        "manage_settings",
        "manage_team",
        "view_analytics"
    ],
    "manager": [
        "view_dashboard",
        "view_employees",
        "manage_attendance",
        "view_salary",
        "manage_leaves",
        "export_reports",
        "view_analytics"
    ],
    "employee": [
        "view_dashboard",
        "view_own_attendance",
        "view_own_salary",
        "apply_leave",
        "view_own_loans"
    ]
}

# Team size limits per plan
TEAM_SIZE_LIMITS = {
    "trial": 3,
    "free": 1,
    "basic": 5,
    "premium": 25
}
