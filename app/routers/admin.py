from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Customer, License, Payment, AuditLog, Invoice
from app.services.license import upgrade_license
from app.services.auth import get_current_admin
from app.config import settings, GRACE_PERIOD_DAYS, PLAN_PRICES
from datetime import datetime, timezone, timedelta

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
    now = datetime.now(timezone.utc)
    for c in customers:
        license = db.query(License).filter(
            License.customer_id == c.id,
            License.is_active == True
        ).first()

        # Days remaining calculate करा
        days_remaining = None
        is_expired = False
        if license and license.valid_till:
            vt = license.valid_till
            if vt.tzinfo is None:
                vt = vt.replace(tzinfo=timezone.utc)
            delta = (vt - now).days
            days_remaining = max(0, delta)
            is_expired = vt < now

        result.append({
            "id": c.id,
            "business_name": c.business_name,
            "owner_name": c.owner_name,
            "email": c.email,
            "phone": c.phone,
            "city": c.city,
            "is_active": c.is_active,
            "plan": license.plan if license else "none",
            "valid_till": license.valid_till.isoformat() if license and license.valid_till else None,
            "trial_start": license.trial_start.isoformat() if license and license.trial_start else None,
            "trial_end": license.trial_end.isoformat() if license and license.trial_end else None,
            "license_start": license.created_at.isoformat() if license and license.created_at else None,
            "days_remaining": days_remaining,
            "is_expired": is_expired,
            "is_paused": license.is_paused if license else False,
            "paused_at": license.paused_at.isoformat() if license and license.paused_at else None,
            "pause_days_remaining": license.pause_days_remaining if license else None,
            "created_at": c.created_at.isoformat(),
        })
    return {"total": len(result), "customers": result}


@router.get("/customers/{customer_id}/payments")
def get_customer_payments(
    customer_id: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """Customer चे payment history + invoices"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    payments = db.query(Payment).filter(
        Payment.customer_id == customer_id
    ).order_by(Payment.created_at.desc()).all()

    result = []
    for p in payments:
        # Invoice शोधा या payment साठी
        invoice = db.query(Invoice).filter(Invoice.payment_id == p.id).first()
        result.append({
            "id": p.id,
            "plan": p.plan,
            "amount": p.amount,
            "status": p.status,
            "razorpay_payment_id": p.razorpay_payment_id,
            "created_at": p.created_at.isoformat(),
            "invoice_id": invoice.id if invoice else None,
            "invoice_number": invoice.invoice_number if invoice else None,
            "pdf_available": bool(invoice and invoice.pdf_path) if invoice else False,
        })

    return {"payments": result, "total": len(result)}


@router.get("/expiring-soon")
def get_expiring_soon(
    days: int = 7,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """X दिवसांत expire होणारे customers"""
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(days=days)

    # Active paid licenses जे cutoff च्या आत expire होतील
    expiring_licenses = db.query(License).filter(
        License.is_active == True,
        License.plan.in_(["trial", "basic", "premium"]),
        License.valid_till <= cutoff,
        License.valid_till >= now  # आधीच expired नाहीत
    ).order_by(License.valid_till.asc()).all()

    # Expired licenses (grace period मध्ये असतील)
    expired_licenses = db.query(License).filter(
        License.is_active == True,
        License.plan.in_(["basic", "premium"]),
        License.valid_till < now
    ).order_by(License.valid_till.desc()).limit(20).all()

    def build_entry(lic, is_expired_entry=False):
        customer = db.query(Customer).filter(Customer.id == lic.customer_id).first()
        if not customer:
            return None

        vt = lic.valid_till
        if vt and vt.tzinfo is None:
            vt = vt.replace(tzinfo=timezone.utc)

        if is_expired_entry:
            days_overdue = (now - vt).days if vt else 0
            grace_days = GRACE_PERIOD_DAYS.get(lic.plan, 15)
            grace_remaining = max(0, grace_days - days_overdue)
        else:
            days_remaining = (vt - now).days if vt else 0
            grace_remaining = None

        return {
            "customer_id": customer.id,
            "business_name": customer.business_name,
            "email": customer.email,
            "phone": customer.phone,
            "plan": lic.plan,
            "valid_till": vt.isoformat() if vt else None,
            "days_remaining": (vt - now).days if vt and not is_expired_entry else None,
            "is_expired": is_expired_entry,
            "grace_remaining": grace_remaining,
        }

    expiring = [e for e in [build_entry(l) for l in expiring_licenses] if e]
    expired = [e for e in [build_entry(l, True) for l in expired_licenses] if e]

    return {
        "expiring_soon": expiring,
        "expired_in_grace": expired,
        "expiring_count": len(expiring),
        "expired_count": len(expired),
    }


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


@router.post("/customers/{customer_id}/pause")
def pause_subscription(
    customer_id: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """Subscription pause करा — valid_till freeze होतो"""
    license = db.query(License).filter(
        License.customer_id == customer_id,
        License.is_active == True
    ).first()
    if not license:
        raise HTTPException(status_code=404, detail="License not found")
    if license.plan not in ["basic", "premium"]:
        raise HTTPException(status_code=400, detail="Only basic/premium plans can be paused")
    if license.is_paused:
        raise HTTPException(status_code=400, detail="Subscription already paused")

    now = datetime.now(timezone.utc)
    vt = license.valid_till
    if vt and vt.tzinfo is None:
        vt = vt.replace(tzinfo=timezone.utc)

    days_remaining = max(0, (vt - now).days) if vt else 0

    license.is_paused = True
    license.paused_at = now
    license.pause_days_remaining = days_remaining
    db.commit()

    log = AuditLog(
        customer_id=customer_id,
        action="subscription_paused",
        machine_id=license.machine_id,
        details=f"paused_at={now.isoformat()}, days_remaining={days_remaining}"
    )
    db.add(log)
    db.commit()

    return {
        "success": True,
        "paused_at": now.isoformat(),
        "days_remaining_frozen": days_remaining,
    }


@router.post("/customers/{customer_id}/resume")
def resume_subscription(
    customer_id: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """Subscription resume करा — frozen days परत मिळतात"""
    license = db.query(License).filter(
        License.customer_id == customer_id,
        License.is_active == True
    ).first()
    if not license:
        raise HTTPException(status_code=404, detail="License not found")
    if not license.is_paused:
        raise HTTPException(status_code=400, detail="Subscription is not paused")

    now = datetime.now(timezone.utc)
    days = license.pause_days_remaining or 0
    new_valid_till = now + timedelta(days=days)

    from app.services.license import generate_license_key
    new_key = generate_license_key(
        customer_id=customer_id,
        machine_id=license.machine_id,
        plan=license.plan,
        valid_till=new_valid_till
    )

    license.is_paused = False
    license.valid_till = new_valid_till
    license.license_key = new_key
    license.paused_at = None
    license.pause_days_remaining = None
    license.last_validated = now
    db.commit()

    log = AuditLog(
        customer_id=customer_id,
        action="subscription_resumed",
        machine_id=license.machine_id,
        details=f"resumed_at={now.isoformat()}, new_valid_till={new_valid_till.isoformat()}"
    )
    db.add(log)
    db.commit()

    return {
        "success": True,
        "resumed_at": now.isoformat(),
        "new_valid_till": new_valid_till.isoformat(),
    }


@router.post("/customers/bulk-action")
def bulk_action(
    action: str,
    customer_ids: list,
    days: int = 7,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """Multiple customers वर एकत्र action — extend/block/unblock"""
    if action not in ["extend", "block", "unblock"]:
        raise HTTPException(status_code=400, detail="Invalid action. Use: extend, block, unblock")

    results = {"success": [], "failed": []}

    for cid in customer_ids:
        try:
            if action == "extend":
                license = db.query(License).filter(
                    License.customer_id == cid,
                    License.is_active == True
                ).first()
                if not license:
                    results["failed"].append(cid)
                    continue
                now = datetime.now(timezone.utc)
                vt = license.valid_till
                if vt and vt.tzinfo is None:
                    vt = vt.replace(tzinfo=timezone.utc)
                base = max(now, vt) if vt else now
                new_vt = base + timedelta(days=days)
                from app.services.license import generate_license_key
                license.valid_till = new_vt
                license.license_key = generate_license_key(cid, license.machine_id, license.plan, new_vt)
                if license.plan == "trial":
                    te = license.trial_end
                    if te and te.tzinfo is None:
                        te = te.replace(tzinfo=timezone.utc)
                    base_te = max(now, te) if te else now
                    license.trial_end = base_te + timedelta(days=days)
                db.commit()
            elif action in ["block", "unblock"]:
                customer = db.query(Customer).filter(Customer.id == cid).first()
                if not customer:
                    results["failed"].append(cid)
                    continue
                customer.is_active = (action == "unblock")
                db.commit()
            results["success"].append(cid)
        except Exception:
            results["failed"].append(cid)

    return {
        "action": action,
        "success_count": len(results["success"]),
        "failed_count": len(results["failed"]),
        "results": results,
    }


@router.get("/customers/export-csv")
def export_customers_csv(
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """Customers list CSV मध्ये export करा"""
    import csv
    import io
    from fastapi.responses import StreamingResponse

    customers = db.query(Customer).order_by(Customer.created_at.desc()).all()
    now = datetime.now(timezone.utc)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Business Name", "Owner Name", "Email", "Phone", "City",
        "Plan", "Status", "Trial Start", "Trial End",
        "Valid Till", "Days Remaining", "Registered On"
    ])

    for c in customers:
        license = db.query(License).filter(
            License.customer_id == c.id,
            License.is_active == True
        ).first()

        days_remaining = ""
        if license and license.valid_till:
            vt = license.valid_till
            if vt.tzinfo is None:
                vt = vt.replace(tzinfo=timezone.utc)
            days_remaining = max(0, (vt - now).days)

        def fmt(dt):
            if not dt:
                return ""
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.strftime("%d %b %Y")

        writer.writerow([
            c.business_name,
            c.owner_name,
            c.email,
            c.phone,
            c.city or "",
            license.plan if license else "none",
            "Active" if c.is_active else "Blocked",
            fmt(license.trial_start) if license else "",
            fmt(license.trial_end) if license else "",
            fmt(license.valid_till) if license else "",
            days_remaining,
            fmt(c.created_at),
        ])

    output.seek(0)
    filename = f"customers_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/customers/{customer_id}/extend-trial")
def extend_trial(
    customer_id: str,
    days: int = 7,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """Trial period extend करा — फक्त trial plan साठी"""
    if days not in [7, 14, 30]:
        raise HTTPException(status_code=400, detail="Days must be 7, 14, or 30")

    license = db.query(License).filter(
        License.customer_id == customer_id,
        License.is_active == True
    ).first()

    if not license:
        raise HTTPException(status_code=404, detail="License not found")

    if license.plan != "trial":
        raise HTTPException(status_code=400, detail="Only trial plans can be extended")

    now = datetime.now(timezone.utc)

    # trial_end extend करा — आधीच expire झाली असेल तर now पासून, नाहीतर existing trial_end पासून
    existing_trial_end = license.trial_end
    if existing_trial_end and existing_trial_end.tzinfo is None:
        existing_trial_end = existing_trial_end.replace(tzinfo=timezone.utc)

    base = max(now, existing_trial_end) if existing_trial_end else now
    new_trial_end = base + timedelta(days=days)

    # valid_till पण update करा
    existing_valid_till = license.valid_till
    if existing_valid_till and existing_valid_till.tzinfo is None:
        existing_valid_till = existing_valid_till.replace(tzinfo=timezone.utc)

    base_vt = max(now, existing_valid_till) if existing_valid_till else now
    new_valid_till = base_vt + timedelta(days=days)

    # नवीन license key generate करा
    from app.services.license import generate_license_key
    new_key = generate_license_key(
        customer_id=customer_id,
        machine_id=license.machine_id,
        plan="trial",
        valid_till=new_valid_till
    )

    license.trial_end = new_trial_end
    license.valid_till = new_valid_till
    license.license_key = new_key
    license.last_validated = now
    db.commit()
    db.refresh(license)

    log = AuditLog(
        customer_id=customer_id,
        action="trial_extended",
        machine_id=license.machine_id,
        details=f"extended_by={days}days, new_trial_end={new_trial_end.isoformat()}"
    )
    db.add(log)
    db.commit()

    return {
        "success": True,
        "customer_id": customer_id,
        "extended_by_days": days,
        "new_trial_end": new_trial_end.isoformat(),
        "new_valid_till": new_valid_till.isoformat(),
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
