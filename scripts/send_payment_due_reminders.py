#!/usr/bin/env python3
"""
Send Payment Due Reminder Emails

This script sends payment due reminder emails to customers whose subscriptions
are expiring soon (7 days and 3 days before expiry).

Usage:
    python scripts/send_payment_due_reminders.py

Schedule with cron:
    # Run daily at 10:00 AM
    0 10 * * * cd /path/to/project && python scripts/send_payment_due_reminders.py
"""

import sys
import os
from datetime import datetime, timezone, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import License, Customer
from app.services.email import send_payment_due_notification
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/payment_due_reminders.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def send_payment_due_reminders():
    """
    Send payment due reminder emails to customers
    
    Sends reminders at:
    - 7 days before expiry
    - 3 days before expiry
    """
    db = SessionLocal()
    
    try:
        now = datetime.now(timezone.utc)
        
        # Calculate reminder dates
        seven_days_from_now = now + timedelta(days=7)
        three_days_from_now = now + timedelta(days=3)
        
        # Get licenses expiring in 7 days
        licenses_7_days = db.query(License).join(Customer).filter(
            License.is_active == True,
            License.plan.in_(["basic", "premium"]),
            License.valid_till >= three_days_from_now,
            License.valid_till <= seven_days_from_now
        ).all()
        
        # Get licenses expiring in 3 days
        licenses_3_days = db.query(License).join(Customer).filter(
            License.is_active == True,
            License.plan.in_(["basic", "premium"]),
            License.valid_till >= now,
            License.valid_till <= three_days_from_now
        ).all()
        
        sent_count = 0
        error_count = 0
        
        # Send 7-day reminders
        for license in licenses_7_days:
            days_remaining = (license.valid_till - now).days
            if days_remaining == 7:  # Only send on exact day
                try:
                    send_payment_due_notification(db, license.customer_id, days_remaining)
                    sent_count += 1
                    logger.info(f"Sent 7-day reminder to customer {license.customer_id}")
                except Exception as e:
                    error_count += 1
                    logger.error(f"Failed to send 7-day reminder to customer {license.customer_id}: {str(e)}")
        
        # Send 3-day reminders
        for license in licenses_3_days:
            days_remaining = (license.valid_till - now).days
            if days_remaining == 3:  # Only send on exact day
                try:
                    send_payment_due_notification(db, license.customer_id, days_remaining)
                    sent_count += 1
                    logger.info(f"Sent 3-day reminder to customer {license.customer_id}")
                except Exception as e:
                    error_count += 1
                    logger.error(f"Failed to send 3-day reminder to customer {license.customer_id}: {str(e)}")
        
        logger.info(f"Payment due reminders complete: {sent_count} sent, {error_count} errors")
        
    except Exception as e:
        logger.error(f"Error in send_payment_due_reminders: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Starting payment due reminder job")
    send_payment_due_reminders()
    logger.info("Payment due reminder job complete")
