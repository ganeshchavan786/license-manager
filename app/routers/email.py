"""
Email API Endpoints

Provides REST API endpoints for:
- Processing email queue (internal/cron)
- Sending trial reminders (internal/cron)
- Viewing email queue (admin only)
- Retrying failed emails (admin only)
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.services.auth import get_current_admin
from app.services import email as email_service
from app.config import settings

router = APIRouter(prefix="/email", tags=["email"])


# Request/Response Models

class ProcessEmailsResponse(BaseModel):
    success: bool
    emails_sent: int
    message: str


class SendTrialRemindersResponse(BaseModel):
    success: bool
    reminders_queued: int
    message: str


class EmailQueueItem(BaseModel):
    id: str
    to_email: str
    subject: str
    status: str
    retry_count: int
    max_retries: int
    error_message: Optional[str] = None
    scheduled_at: str
    sent_at: Optional[str] = None
    created_at: str


class EmailQueueResponse(BaseModel):
    emails: List[EmailQueueItem]
    total: int
    pending: int
    sent: int
    failed: int


class RetryEmailResponse(BaseModel):
    success: bool
    message: str


# Helper function for internal authentication
def verify_internal_auth(x_api_key: Optional[str] = Header(None)):
    """
    Verify internal API key for cron jobs
    Can also accept admin JWT token as fallback
    """
    if x_api_key and x_api_key == settings.INTERNAL_API_KEY:
        return True
    raise HTTPException(
        status_code=401,
        detail="Unauthorized: Invalid or missing API key"
    )


# Internal/Cron Endpoints

@router.post("/cron/process-emails", response_model=ProcessEmailsResponse)
async def process_emails_endpoint(
    _: bool = Depends(verify_internal_auth),
    db: Session = Depends(get_db)
):
    """
    Process pending emails in queue (Internal/Cron endpoint)
    
    Requires X-API-Key header with internal API key
    
    This endpoint:
    - Fetches pending emails from queue
    - Sends them via SMTP
    - Updates status (sent/failed)
    - Handles retry logic
    """
    try:
        sent_count = await email_service.process_email_queue(db)
        
        return ProcessEmailsResponse(
            success=True,
            emails_sent=sent_count,
            message=f"Successfully processed email queue: {sent_count} emails sent"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process email queue: {str(e)}"
        )


@router.post("/cron/send-trial-reminders", response_model=SendTrialRemindersResponse)
def send_trial_reminders_endpoint(
    _: bool = Depends(verify_internal_auth),
    db: Session = Depends(get_db)
):
    """
    Send trial reminder emails to customers (Internal/Cron endpoint)
    
    Requires X-API-Key header with internal API key
    
    This endpoint:
    - Finds active trial licenses expiring in 3 or 1 days
    - Queues reminder emails for those customers
    - Returns count of reminders queued
    """
    try:
        from app.models import License
        from datetime import timedelta, timezone
        
        now = datetime.now(timezone.utc)
        reminder_count = 0
        
        # Get all active trial licenses
        trial_licenses = db.query(License).filter(
            License.plan == "trial",
            License.is_active == True,
            License.trial_end.isnot(None)
        ).all()
        
        # Check each trial license
        for license_obj in trial_licenses:
            if not license_obj.trial_end:
                continue
            
            # Make trial_end timezone-aware if it isn't
            trial_end = license_obj.trial_end
            if trial_end.tzinfo is None:
                trial_end = trial_end.replace(tzinfo=timezone.utc)
            
            # Calculate days remaining
            days_remaining = (trial_end - now).days
            
            # Send reminder if trial ends in 3 days or 1 day
            if days_remaining == 3 or days_remaining == 1:
                try:
                    email_service.send_trial_reminder(
                        db=db,
                        customer_id=license_obj.customer_id,
                        days_remaining=days_remaining
                    )
                    reminder_count += 1
                except Exception as e:
                    # Log error but continue processing other reminders
                    print(f"Failed to send reminder for customer {license_obj.customer_id}: {str(e)}")
        
        return SendTrialRemindersResponse(
            success=True,
            reminders_queued=reminder_count,
            message=f"Successfully queued {reminder_count} trial reminder emails"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send trial reminders: {str(e)}"
        )


# Admin Endpoints

@router.get("/admin/queue", response_model=EmailQueueResponse)
def get_email_queue(
    status: Optional[str] = None,
    limit: int = 100,
    admin_payload: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get email queue with optional filtering (Admin only)
    
    - **status**: Filter by status (pending, sent, failed) - optional
    - **limit**: Maximum number of emails to return (default: 100, max: 500)
    """
    from app.models import EmailQueue
    
    # Validate limit
    if limit < 1 or limit > 500:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 500")
    
    # Validate status if provided
    if status and status not in ["pending", "sent", "failed"]:
        raise HTTPException(status_code=400, detail="Status must be one of: pending, sent, failed")
    
    try:
        # Build query
        query = db.query(EmailQueue)
        
        if status:
            query = query.filter(EmailQueue.status == status)
        
        # Get emails ordered by created_at desc
        emails = query.order_by(EmailQueue.created_at.desc()).limit(limit).all()
        
        # Get counts
        total = db.query(EmailQueue).count()
        pending = db.query(EmailQueue).filter(EmailQueue.status == "pending").count()
        sent = db.query(EmailQueue).filter(EmailQueue.status == "sent").count()
        failed = db.query(EmailQueue).filter(EmailQueue.status == "failed").count()
        
        # Format response
        email_list = []
        for email in emails:
            email_list.append(EmailQueueItem(
                id=email.id,
                to_email=email.to_email,
                subject=email.subject,
                status=email.status,
                retry_count=email.retry_count,
                max_retries=email.max_retries,
                error_message=email.error_message,
                scheduled_at=email.scheduled_at.isoformat() if email.scheduled_at else "",
                sent_at=email.sent_at.isoformat() if email.sent_at else None,
                created_at=email.created_at.isoformat() if email.created_at else ""
            ))
        
        return EmailQueueResponse(
            emails=email_list,
            total=total,
            pending=pending,
            sent=sent,
            failed=failed
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get email queue: {str(e)}"
        )


@router.post("/admin/retry/{email_id}", response_model=RetryEmailResponse)
def retry_failed_email(
    email_id: str,
    admin_payload: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Retry a failed email (Admin only)
    
    - **email_id**: ID of the email to retry
    
    This endpoint:
    - Resets the email status to "pending"
    - Resets retry_count to 0
    - Clears error_message
    - Email will be processed in next queue run
    """
    from app.models import EmailQueue
    
    try:
        # Get email
        email = db.query(EmailQueue).filter(EmailQueue.id == email_id).first()
        
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        # Check if email is in a retryable state
        if email.status == "sent":
            raise HTTPException(
                status_code=400,
                detail="Cannot retry an email that was already sent successfully"
            )
        
        # Reset email for retry
        email.status = "pending"
        email.retry_count = 0
        email.error_message = None
        email.scheduled_at = datetime.now()
        
        db.commit()
        
        return RetryEmailResponse(
            success=True,
            message=f"Email '{email.subject}' to {email.to_email} has been queued for retry"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retry email: {str(e)}"
        )
