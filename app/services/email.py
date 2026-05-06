"""
Email Service - Manage email queue and sending functionality

This service provides functionality to:
- Queue emails for asynchronous sending
- Process email queue with retry logic
- Send emails via SMTP
- Send transactional emails (welcome, trial reminder, renewal confirmation)
"""

from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
import json
import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

from app.models import EmailQueue, Customer, License
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Jinja2 environment for email templates
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "emails")
jinja_env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=select_autoescape(['html', 'xml'])
)


def queue_email(
    db: Session,
    to_email: str,
    subject: str,
    body_html: str,
    body_text: str = None,
    attachments: List[str] = None,
    scheduled_at: datetime = None,
    max_retries: int = 3
) -> EmailQueue:
    """
    Queue an email for asynchronous sending
    
    Preconditions:
    - to_email is valid email format
    - subject is non-empty string
    - body_html or body_text is provided
    
    Postconditions:
    - New EmailQueue record created with status "pending"
    - scheduled_at defaults to current timestamp
    - retry_count initialized to 0
    - Returns EmailQueue object
    """
    # Validate email format (basic validation)
    if not to_email or '@' not in to_email:
        raise ValueError("Invalid email address")
    
    if not subject:
        raise ValueError("Subject cannot be empty")
    
    if not body_html and not body_text:
        raise ValueError("Either body_html or body_text must be provided")
    
    # Create email queue record
    email = EmailQueue(
        to_email=to_email,
        subject=subject,
        body_html=body_html,
        body_text=body_text or "",
        attachments=json.dumps(attachments) if attachments else None,
        status="pending",
        retry_count=0,
        max_retries=max_retries,
        scheduled_at=scheduled_at or datetime.now(timezone.utc)
    )
    
    db.add(email)
    db.commit()
    db.refresh(email)
    
    logger.info(f"Email queued: {to_email} - {subject}")
    return email


async def send_smtp_email(
    to_email: str,
    subject: str,
    body_html: str,
    body_text: str = None,
    attachments: List[str] = None
) -> None:
    """
    Send email via SMTP using aiosmtplib
    
    Preconditions:
    - SMTP server configured in settings
    - to_email is valid email address
    - subject is non-empty string
    - body_html or body_text is provided
    
    Postconditions:
    - Email sent via SMTP server
    - Raises exception if sending fails
    """
    # Create message
    message = MIMEMultipart('alternative')
    message['From'] = settings.SMTP_FROM_EMAIL
    message['To'] = to_email
    message['Subject'] = subject
    
    # Add text and HTML parts
    if body_text:
        part1 = MIMEText(body_text, 'plain')
        message.attach(part1)
    
    if body_html:
        part2 = MIMEText(body_html, 'html')
        message.attach(part2)
    
    # TODO: Add attachment support if needed
    
    # Send email
    try:
        # Determine TLS mode based on port
        if settings.SMTP_USE_TLS and settings.SMTP_PORT == 587:
            # Port 587: Use STARTTLS
            smtp = aiosmtplib.SMTP(
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT
            )
            await smtp.connect()
            await smtp.starttls()
            await smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            await smtp.send_message(message)
            await smtp.quit()
        elif settings.SMTP_PORT == 465:
            # Port 465: Use direct TLS/SSL
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                use_tls=True
            )
        else:
            # Plain connection
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD
            )
        
        logger.info(f"Email sent successfully: {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        raise


async def process_email_queue(db: Session) -> int:
    """
    Process pending emails in queue with retry logic
    
    Preconditions:
    - SMTP server configured in settings
    - email_queue table exists
    
    Postconditions:
    - All pending emails with scheduled_at <= now are processed
    - Successful emails marked as "sent" with sent_at timestamp
    - Failed emails marked as "failed" or retry_count incremented
    - Returns count of successfully sent emails
    
    Loop Invariants:
    - Each email processed exactly once per iteration
    - Failed emails with retry_count < max_retries remain in queue
    """
    now = datetime.now(timezone.utc)
    sent_count = 0
    
    # Get pending emails (batch of 100)
    pending_emails = db.query(EmailQueue).filter(
        EmailQueue.status == "pending",
        EmailQueue.scheduled_at <= now,
        EmailQueue.retry_count < EmailQueue.max_retries
    ).limit(100).all()
    
    logger.info(f"Processing {len(pending_emails)} pending emails")
    
    # Process each email
    for email in pending_emails:
        try:
            # Send email via SMTP
            await send_smtp_email(
                to_email=email.to_email,
                subject=email.subject,
                body_html=email.body_html,
                body_text=email.body_text,
                attachments=json.loads(email.attachments) if email.attachments else None
            )
            
            # Mark as sent
            email.status = "sent"
            email.sent_at = now
            sent_count += 1
            
        except Exception as e:
            # Handle failure
            email.retry_count += 1
            email.error_message = str(e)
            
            if email.retry_count >= email.max_retries:
                email.status = "failed"
                logger.error(f"Email failed after {email.max_retries} retries: {email.to_email}")
            else:
                logger.warning(f"Email send failed (retry {email.retry_count}/{email.max_retries}): {email.to_email}")
        
        db.commit()
    
    logger.info(f"Email queue processing complete: {sent_count} sent, {len(pending_emails) - sent_count} failed")
    return sent_count


def send_trial_reminder(
    db: Session,
    customer_id: str,
    days_remaining: int
) -> bool:
    """
    Send trial reminder email to customer
    
    Preconditions:
    - customer_id exists in customers table
    - days_remaining is positive integer
    
    Postconditions:
    - Email queued with trial reminder template
    - Returns True if successful
    """
    # Get customer
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise ValueError("Customer not found")
    
    # Get license
    license = db.query(License).filter(
        License.customer_id == customer_id,
        License.plan == "trial",
        License.is_active == True
    ).first()
    
    if not license:
        raise ValueError("No active trial license found")
    
    # Render template
    template = jinja_env.get_template('trial_reminder.html')
    body_html = template.render(
        owner_name=customer.owner_name,
        business_name=customer.business_name,
        days_remaining=days_remaining,
        trial_end=license.trial_end.strftime('%d %B %Y') if license.trial_end else '',
        upgrade_url=f"{settings.FRONTEND_URL}/plans"
    )
    
    # Plain text version
    body_text = f"""
Hi {customer.owner_name},

Your SalaryPay trial ends in {days_remaining} days.

Upgrade now to continue using premium features:
- Face recognition attendance
- Unlimited employees
- Full salary management
- Tax calculations
- Loans module
- Export reports

Upgrade at: {settings.FRONTEND_URL}/plans

Thank you,
SalaryPay Team
    """
    
    # Queue email
    queue_email(
        db=db,
        to_email=customer.email,
        subject=f"Your SalaryPay trial ends in {days_remaining} days",
        body_html=body_html,
        body_text=body_text
    )
    
    logger.info(f"Trial reminder queued for {customer.email} ({days_remaining} days)")
    return True


def send_welcome_email(
    db: Session,
    customer_id: str
) -> bool:
    """
    Send welcome email to new customer
    
    Preconditions:
    - customer_id exists in customers table
    
    Postconditions:
    - Email queued with welcome template
    - Returns True if successful
    """
    # Get customer
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise ValueError("Customer not found")
    
    # Render template
    template = jinja_env.get_template('welcome.html')
    body_html = template.render(
        owner_name=customer.owner_name,
        business_name=customer.business_name,
        dashboard_url=f"{settings.FRONTEND_URL}/dashboard",
        support_email=settings.SUPPORT_EMAIL
    )
    
    # Plain text version
    body_text = f"""
Hi {customer.owner_name},

Welcome to SalaryPay!

Thank you for registering your business "{customer.business_name}". Your account is now active.

Get started:
1. Log in to your dashboard: {settings.FRONTEND_URL}/dashboard
2. Add your employees
3. Start tracking attendance
4. Manage salaries and payroll

Need help? Contact us at {settings.SUPPORT_EMAIL}

Thank you,
SalaryPay Team
    """
    
    # Queue email
    queue_email(
        db=db,
        to_email=customer.email,
        subject="Welcome to SalaryPay!",
        body_html=body_html,
        body_text=body_text
    )
    
    logger.info(f"Welcome email queued for {customer.email}")
    return True


def send_renewal_confirmation(
    db: Session,
    customer_id: str,
    plan: str,
    amount: int,
    valid_till: datetime
) -> bool:
    """
    Send renewal confirmation email after successful payment
    
    Preconditions:
    - customer_id exists in customers table
    - plan is one of: "basic", "premium"
    - amount is positive integer in paise
    - valid_till is future datetime
    
    Postconditions:
    - Email queued with renewal confirmation template
    - Returns True if successful
    """
    # Get customer
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise ValueError("Customer not found")
    
    # Format amount in rupees
    amount_rupees = amount / 100
    
    # Render template
    template = jinja_env.get_template('renewal_confirmation.html')
    body_html = template.render(
        owner_name=customer.owner_name,
        business_name=customer.business_name,
        plan=plan.capitalize(),
        amount=f"₹{amount_rupees:.2f}",
        valid_till=valid_till.strftime('%d %B %Y'),
        dashboard_url=f"{settings.FRONTEND_URL}/dashboard",
        invoices_url=f"{settings.FRONTEND_URL}/invoices"
    )
    
    # Plain text version
    body_text = f"""
Hi {customer.owner_name},

Your SalaryPay subscription has been renewed successfully!

Plan: {plan.capitalize()}
Amount Paid: ₹{amount_rupees:.2f}
Valid Till: {valid_till.strftime('%d %B %Y')}

Your invoice is available in your dashboard: {settings.FRONTEND_URL}/invoices

Thank you for your continued trust in SalaryPay!

SalaryPay Team
    """
    
    # Queue email
    queue_email(
        db=db,
        to_email=customer.email,
        subject=f"SalaryPay Subscription Renewed - {plan.capitalize()} Plan",
        body_html=body_html,
        body_text=body_text
    )
    
    logger.info(f"Renewal confirmation queued for {customer.email}")
    return True


def send_payment_due_notification(
    db: Session,
    customer_id: str,
    days_remaining: int
) -> bool:
    """
    Send payment due notification email to customer before subscription expires
    
    Preconditions:
    - customer_id exists in customers table
    - days_remaining is positive integer
    
    Postconditions:
    - Email queued with payment due notification
    - Returns True if successful
    """
    # Get customer
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise ValueError("Customer not found")
    
    # Get active license
    license = db.query(License).filter(
        License.customer_id == customer_id,
        License.is_active == True,
        License.plan.in_(["basic", "premium"])
    ).first()
    
    if not license:
        raise ValueError("No active paid license found")
    
    # Calculate renewal amount based on plan
    from app.config import PLAN_PRICES
    renewal_amount = PLAN_PRICES.get(license.plan, 0) / 100
    
    # Create email body (no template file, inline HTML)
    body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .button {{ display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
        .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Subscription Expiring Soon</h1>
        </div>
        <div class="content">
            <p>Hi {customer.owner_name},</p>
            
            <p>Your SalaryPay <strong>{license.plan.capitalize()}</strong> subscription will expire in <strong>{days_remaining} days</strong>.</p>
            
            <p><strong>Expiry Date:</strong> {license.valid_till.strftime('%d %B %Y')}</p>
            
            <p>To continue enjoying premium features, please renew your subscription:</p>
            
            <ul>
                <li>Face recognition attendance</li>
                <li>Unlimited employees</li>
                <li>Full salary management</li>
                <li>Tax calculations</li>
                <li>Loans module</li>
                <li>Export reports</li>
            </ul>
            
            <p><strong>Renewal Amount:</strong> ₹{renewal_amount:.2f}</p>
            
            <p style="text-align: center;">
                <a href="{settings.FRONTEND_URL}/plans" class="button">Renew Now</a>
            </p>
            
            <p>Thank you for using SalaryPay!</p>
        </div>
        <div class="footer">
            <p>SalaryPay - Salary Management Made Easy</p>
            <p>Need help? Contact us at {settings.SUPPORT_EMAIL}</p>
        </div>
    </div>
</body>
</html>
    """
    
    # Plain text version
    body_text = f"""
Hi {customer.owner_name},

Your SalaryPay {license.plan.capitalize()} subscription will expire in {days_remaining} days.

Expiry Date: {license.valid_till.strftime('%d %B %Y')}

To continue enjoying premium features, please renew your subscription.

Renewal Amount: ₹{renewal_amount:.2f}

Renew at: {settings.FRONTEND_URL}/plans

Thank you for using SalaryPay!

Need help? Contact us at {settings.SUPPORT_EMAIL}
    """
    
    # Queue email
    queue_email(
        db=db,
        to_email=customer.email,
        subject=f"Your SalaryPay subscription expires in {days_remaining} days",
        body_html=body_html,
        body_text=body_text
    )
    
    logger.info(f"Payment due notification queued for {customer.email} ({days_remaining} days)")
    return True
