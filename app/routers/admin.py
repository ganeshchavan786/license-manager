from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Customer, License, Payment, AuditLog
from app.services.license import upgrade_license
from app.services.auth import get_current_admin
from app.config import settings
from datetime import datetime, timezone

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


@router.get("/customers")
def list_customers(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """सर्व customers list करा"""
    customers = db.query(Customer).order_by(Customer.created_at.desc()).offset(skip).limit(limit).all()
    result = []
    for c in customers:
        license = db.query(License).filter(
            License.customer_id == c.id,
            License.is_active == True
        ).first()
        result.append({
            "id": c.id,
            "business_name": c.business_name,
            "owner_name": c.owner_name,
            "email": c.email,
            "phone": c.phone,
            "city": c.city,
            "is_active": c.is_active,
            "plan": license.plan if license else "none",
            "valid_till": license.valid_till.isoformat() if license else None,
            "created_at": c.created_at.isoformat(),
        })
    return {"total": len(result), "customers": result}


@router.get("/customers/{customer_id}")
def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """Single customer details"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    licenses = db.query(License).filter(License.customer_id == customer_id).all()
    payments = db.query(Payment).filter(Payment.customer_id == customer_id).all()

    return {
        "customer": {
            "id": customer.id,
            "business_name": customer.business_name,
            "owner_name": customer.owner_name,
            "email": customer.email,
            "phone": customer.phone,
            "city": customer.city,
            "created_at": customer.created_at.isoformat(),
        },
        "licenses": [{
            "plan": l.plan,
            "valid_till": l.valid_till.isoformat(),
            "machine_id": l.machine_id,
            "is_active": l.is_active,
        } for l in licenses],
        "payments": [{
            "plan": p.plan,
            "amount": p.amount / 100,  # paise to rupees
            "status": p.status,
            "created_at": p.created_at.isoformat(),
        } for p in payments],
    }


@router.post("/customers/{customer_id}/upgrade")
def manual_upgrade(
    customer_id: str,
    plan: str,
    months: int = 1,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """Manual plan upgrade — customer ला free extension द्यायचे असेल तर"""
    if plan not in ["free", "basic", "premium"]:
        raise HTTPException(status_code=400, detail="Invalid plan")

    license = upgrade_license(db, customer_id, plan, months)
    if not license:
        raise HTTPException(status_code=404, detail="License not found")

    return {
        "success": True,
        "customer_id": customer_id,
        "new_plan": plan,
        "valid_till": license.valid_till.isoformat(),
    }


@router.post("/customers/{customer_id}/toggle-status")
def toggle_customer_status(
    customer_id: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """Customer ला Enable/Disable करा"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer.is_active = not customer.is_active
    db.commit()
    
    return {"success": True, "is_active": customer.is_active}


@router.get("/stats")
def dashboard_stats(
    range: str = "month",  # today, week, month, year, all
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """Dashboard statistics with date range"""
    from datetime import timedelta
    
    # Calculate date range
    now = datetime.now(timezone.utc)
    if range == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif range == "week":
        start_date = now - timedelta(days=7)
    elif range == "month":
        start_date = now - timedelta(days=30)
    elif range == "year":
        start_date = now - timedelta(days=365)
    else:  # all
        start_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
    
    # Total customers
    total_customers = db.query(Customer).count()
    
    # Active plans
    trial_count = db.query(License).filter(
        License.plan == "trial", 
        License.is_active == True,
        License.valid_till > now
    ).count()
    
    free_count = db.query(License).filter(
        License.plan == "free", 
        License.is_active == True
    ).count()
    
    basic_count = db.query(License).filter(
        License.plan == "basic", 
        License.is_active == True,
        License.valid_till > now
    ).count()
    
    premium_count = db.query(License).filter(
        License.plan == "premium", 
        License.is_active == True,
        License.valid_till > now
    ).count()
    
    # Revenue calculations
    all_payments = db.query(Payment).filter(
        Payment.status == "captured"
    ).all()
    total_revenue = sum(p.amount for p in all_payments)
    
    period_payments = db.query(Payment).filter(
        Payment.status == "captured",
        Payment.created_at >= start_date
    ).all()
    period_revenue = sum(p.amount for p in period_payments)
    
    # Basic and Premium revenue
    basic_revenue = sum(p.amount for p in all_payments if p.plan == "basic")
    premium_revenue = sum(p.amount for p in all_payments if p.plan == "premium")
    
    # ARPU (Average Revenue Per User)
    paid_users = basic_count + premium_count
    arpu = (basic_revenue + premium_revenue) / paid_users if paid_users > 0 else 0
    
    # Conversion rate (trial to paid)
    total_trials = db.query(License).filter(License.plan == "trial").count()
    total_paid = db.query(License).filter(
        License.plan.in_(["basic", "premium"])
    ).count()
    conversion_rate = (total_paid / total_trials * 100) if total_trials > 0 else 0
    
    # Recent registrations
    recent_regs = db.query(Customer).order_by(
        Customer.created_at.desc()
    ).limit(10).all()
    
    return {
        "total_customers": total_customers,
        "active_trials": trial_count,
        "free_plan": free_count,
        "basic_plan": basic_count,
        "premium_plan": premium_count,
        "revenue_total": total_revenue,
        "revenue_this_period": period_revenue,
        "basic_revenue": basic_revenue,
        "premium_revenue": premium_revenue,
        "arpu": int(arpu),
        "conversion_rate": round(conversion_rate, 2),
        "recent_registrations": [{
            "business_name": c.business_name,
            "email": c.email,
            "created_at": c.created_at.isoformat()
        } for c in recent_regs]
    }


@router.get("/payments")
def list_payments(
    range: str = "month",  # today, week, month, year, all
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """सर्व payments list करा with date range"""
    from datetime import timedelta
    
    # Calculate date range
    now = datetime.now(timezone.utc)
    if range == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif range == "week":
        start_date = now - timedelta(days=7)
    elif range == "month":
        start_date = now - timedelta(days=30)
    elif range == "year":
        start_date = now - timedelta(days=365)
    else:  # all
        start_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
    
    payments = db.query(Payment).filter(
        Payment.created_at >= start_date
    ).order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for p in payments:
        customer = db.query(Customer).filter(Customer.id == p.customer_id).first()
        result.append({
            "id": p.id,
            "customer_id": p.customer_id,
            "business_name": customer.business_name if customer else "Unknown",
            "plan": p.plan,
            "amount": p.amount,
            "status": p.status,
            "razorpay_payment_id": p.razorpay_payment_id,
            "created_at": p.created_at.isoformat(),
        })
    
    return {"payments": result}
