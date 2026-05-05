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
