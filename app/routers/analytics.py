"""
Analytics API Endpoints

Provides REST API endpoints for:
- Tracking feature usage
- Retrieving usage analytics
- Generating reports
- Admin analytics overview
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from app.database import get_db
from app.services.auth import get_current_customer, get_current_admin
from app.services import analytics

router = APIRouter(prefix="/analytics", tags=["analytics"])


# Request/Response Models

class TrackUsageRequest(BaseModel):
    feature_name: str = Field(..., min_length=1, max_length=200)
    metadata: Optional[Dict[str, Any]] = None


class TrackUsageResponse(BaseModel):
    success: bool
    message: str


class AnalyticsDashboardResponse(BaseModel):
    total_usage: int
    feature_breakdown: Dict[str, int]
    daily_usage: Dict[str, int]
    period_days: int
    start_date: str
    end_date: str


class MonthlyReportResponse(BaseModel):
    customer_id: str
    year: int
    month: int
    total_usage_count: int
    features_used: Dict[str, int]
    daily_breakdown: Dict[str, int]
    generated_at: str


# Customer Endpoints

@router.post("/track", response_model=TrackUsageResponse)
def track_feature_usage(
    request: Request,
    data: TrackUsageRequest,
    customer_id: str = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Track feature usage for analytics
    
    - **feature_name**: Name of the feature being used
    - **metadata**: Optional additional data (JSON object)
    """
    try:
        # Get IP address and user agent
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Track usage (non-blocking - failures don't raise errors)
        analytics.track_usage(
            db=db,
            customer_id=customer_id,
            feature_name=data.feature_name,
            metadata=data.metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return TrackUsageResponse(
            success=True,
            message="Usage tracked successfully"
        )
    except Exception as e:
        # Don't fail the request if tracking fails
        return TrackUsageResponse(
            success=False,
            message=f"Tracking failed: {str(e)}"
        )


@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
def get_analytics_dashboard(
    days: int = 30,
    customer_id: str = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get usage analytics dashboard for the authenticated customer
    
    - **days**: Number of days to include in the report (default: 30)
    """
    if days < 1 or days > 365:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 365")
    
    dashboard_data = analytics.get_analytics_dashboard(db, customer_id, days)
    
    return AnalyticsDashboardResponse(**dashboard_data)


@router.get("/monthly-report", response_model=MonthlyReportResponse)
def get_monthly_report(
    year: int,
    month: int,
    customer_id: str = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Generate monthly usage report for the authenticated customer
    
    - **year**: Year (e.g., 2024)
    - **month**: Month (1-12)
    """
    if year < 2020 or year > 2100:
        raise HTTPException(status_code=400, detail="Invalid year")
    
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    
    report = analytics.generate_monthly_report(db, customer_id, year, month)
    
    return MonthlyReportResponse(**report)


# Admin Endpoints

@router.get("/admin/overview")
def get_admin_analytics_overview(
    days: Optional[int] = 30,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get system-wide analytics overview (Admin only)
    
    - **days**: Number of days to include (default: 30, None for all time)
    """
    start_date = None
    end_date = datetime.now()
    
    if days:
        start_date = end_date - timedelta(days=days)
    
    overview = analytics.get_admin_analytics_overview(db, start_date, end_date)
    
    return overview


@router.get("/admin/feature-stats")
def get_admin_feature_stats(
    feature_name: Optional[str] = None,
    days: Optional[int] = 30,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get feature usage statistics (Admin only)
    
    - **feature_name**: Specific feature to get stats for (optional)
    - **days**: Number of days to include (default: 30, None for all time)
    """
    start_date = None
    end_date = datetime.now()
    
    if days:
        start_date = end_date - timedelta(days=days)
    
    stats = analytics.get_feature_stats(db, feature_name, start_date, end_date)
    
    return {
        "feature_stats": stats,
        "period": {
            "start": start_date.isoformat() if start_date else None,
            "end": end_date.isoformat()
        }
    }
