"""
Analytics Service - Track and report feature usage

This service provides functionality to:
- Track feature usage per customer
- Retrieve usage analytics with filtering
- Generate usage reports
- Provide admin analytics overview
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import json
import logging

from app.models import UsageAnalytics, Customer, License

logger = logging.getLogger(__name__)


def track_usage(
    db: Session,
    customer_id: str,
    feature_name: str,
    metadata: dict = None,
    ip_address: str = None,
    user_agent: str = None
) -> UsageAnalytics:
    """
    Track feature usage for analytics
    
    Preconditions:
    - customer_id is valid UUID and exists in customers table
    - feature_name is non-empty string
    - metadata is valid dict or None
    
    Postconditions:
    - New UsageAnalytics record created in database
    - Returns UsageAnalytics object with id and created_at
    - No side effects on existing data
    """
    try:
        # Validate customer exists
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            logger.error(f"Customer not found: {customer_id}")
            raise ValueError("Customer not found")
        
        # Get active license for customer
        license = db.query(License).filter(
            License.customer_id == customer_id,
            License.is_active == True
        ).first()
        
        # Create analytics record
        analytics = UsageAnalytics(
            customer_id=customer_id,
            license_id=license.id if license else None,
            feature_name=feature_name,
            action="used",
            meta_data=json.dumps(metadata) if metadata else None,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(analytics)
        db.commit()
        db.refresh(analytics)
        
        logger.info(f"Usage tracked: customer={customer_id}, feature={feature_name}")
        return analytics
        
    except Exception as e:
        logger.error(f"Failed to track usage: {str(e)}")
        db.rollback()
        # Don't raise - tracking failures should not block feature usage
        return None


def get_customer_usage(
    db: Session,
    customer_id: str,
    start_date: datetime = None,
    end_date: datetime = None
) -> List[UsageAnalytics]:
    """
    Get usage analytics for a customer with optional date filtering
    
    Preconditions:
    - customer_id is valid UUID
    - start_date and end_date are datetime objects or None
    
    Postconditions:
    - Returns list of UsageAnalytics records
    - Records are filtered by customer_id and date range
    - No database modifications
    """
    query = db.query(UsageAnalytics).filter(
        UsageAnalytics.customer_id == customer_id
    )
    
    if start_date:
        query = query.filter(UsageAnalytics.created_at >= start_date)
    
    if end_date:
        query = query.filter(UsageAnalytics.created_at <= end_date)
    
    return query.order_by(UsageAnalytics.created_at.desc()).all()


def get_feature_stats(
    db: Session,
    feature_name: str = None,
    start_date: datetime = None,
    end_date: datetime = None
) -> Dict[str, Any]:
    """
    Get feature usage statistics
    
    Preconditions:
    - feature_name is string or None
    - start_date and end_date are datetime objects or None
    
    Postconditions:
    - Returns dict with feature usage counts
    - No database modifications
    """
    query = db.query(
        UsageAnalytics.feature_name,
        func.count(UsageAnalytics.id).label('usage_count'),
        func.count(func.distinct(UsageAnalytics.customer_id)).label('unique_customers')
    )
    
    if feature_name:
        query = query.filter(UsageAnalytics.feature_name == feature_name)
    
    if start_date:
        query = query.filter(UsageAnalytics.created_at >= start_date)
    
    if end_date:
        query = query.filter(UsageAnalytics.created_at <= end_date)
    
    results = query.group_by(UsageAnalytics.feature_name).all()
    
    stats = {}
    for row in results:
        stats[row.feature_name] = {
            'usage_count': row.usage_count,
            'unique_customers': row.unique_customers
        }
    
    return stats


def generate_monthly_report(
    db: Session,
    customer_id: str,
    year: int,
    month: int
) -> Dict[str, Any]:
    """
    Generate monthly usage report for a customer
    
    Preconditions:
    - customer_id exists in customers table
    - year is valid year (2020-2100)
    - month is between 1 and 12
    
    Postconditions:
    - Returns dict with usage statistics for the month
    - Includes: total_usage_count, features_used, daily_breakdown
    - No database modifications
    """
    # Calculate month start and end dates
    start_date = datetime(year, month, 1, tzinfo=timezone.utc)
    if month == 12:
        end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc)
    
    # Get all usage for the month
    usage_records = get_customer_usage(db, customer_id, start_date, end_date)
    
    # Calculate total usage
    total_usage_count = len(usage_records)
    
    # Get unique features used
    features_used = {}
    for record in usage_records:
        if record.feature_name not in features_used:
            features_used[record.feature_name] = 0
        features_used[record.feature_name] += 1
    
    # Daily breakdown
    daily_breakdown = {}
    for record in usage_records:
        day = record.created_at.date().isoformat()
        if day not in daily_breakdown:
            daily_breakdown[day] = 0
        daily_breakdown[day] += 1
    
    return {
        'customer_id': customer_id,
        'year': year,
        'month': month,
        'total_usage_count': total_usage_count,
        'features_used': features_used,
        'daily_breakdown': daily_breakdown,
        'generated_at': datetime.now(timezone.utc).isoformat()
    }


def get_analytics_dashboard(
    db: Session,
    customer_id: str,
    days: int = 30
) -> Dict[str, Any]:
    """
    Get analytics dashboard data for a customer
    
    Preconditions:
    - customer_id exists in customers table
    - days is positive integer
    
    Postconditions:
    - Returns dict with dashboard data
    - Includes: total_usage, feature_breakdown, daily_usage
    - No database modifications
    """
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Get usage data
    usage_data = get_customer_usage(db, customer_id, start_date)
    
    # Aggregate by feature
    feature_counts = {}
    for record in usage_data:
        feature = record.feature_name
        feature_counts[feature] = feature_counts.get(feature, 0) + 1
    
    # Aggregate by day
    daily_counts = {}
    for record in usage_data:
        day = record.created_at.date().isoformat()
        daily_counts[day] = daily_counts.get(day, 0) + 1
    
    return {
        'total_usage': len(usage_data),
        'feature_breakdown': feature_counts,
        'daily_usage': daily_counts,
        'period_days': days,
        'start_date': start_date.isoformat(),
        'end_date': datetime.now(timezone.utc).isoformat()
    }


def get_admin_analytics_overview(
    db: Session,
    start_date: datetime = None,
    end_date: datetime = None
) -> Dict[str, Any]:
    """
    Get system-wide analytics overview for admins
    
    Preconditions:
    - start_date and end_date are datetime objects or None
    
    Postconditions:
    - Returns dict with system-wide analytics
    - No database modifications
    """
    query = db.query(UsageAnalytics)
    
    if start_date:
        query = query.filter(UsageAnalytics.created_at >= start_date)
    
    if end_date:
        query = query.filter(UsageAnalytics.created_at <= end_date)
    
    total_usage = query.count()
    unique_customers = query.with_entities(
        func.count(func.distinct(UsageAnalytics.customer_id))
    ).scalar()
    
    # Feature usage stats
    feature_stats = get_feature_stats(db, None, start_date, end_date)
    
    # Top features
    top_features = sorted(
        feature_stats.items(),
        key=lambda x: x[1]['usage_count'],
        reverse=True
    )[:10]
    
    return {
        'total_usage': total_usage,
        'unique_customers': unique_customers,
        'feature_stats': feature_stats,
        'top_features': dict(top_features),
        'period': {
            'start': start_date.isoformat() if start_date else None,
            'end': end_date.isoformat() if end_date else None
        }
    }
