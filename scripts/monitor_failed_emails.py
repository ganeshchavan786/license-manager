#!/usr/bin/env python3
"""
Failed Email Monitoring Script

This script monitors the email queue for failed emails and sends alerts.
It can be run as a cron job to check for emails that have failed after max retries.

Usage:
    python scripts/monitor_failed_emails.py

Cron Example (every hour):
    0 * * * * cd /path/to/license-server && python scripts/monitor_failed_emails.py >> logs/email_monitoring.log 2>&1
"""

import sys
import os
import logging
from datetime import datetime, timezone, timedelta

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models import EmailQueue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def monitor_failed_emails():
    """
    Monitor email queue for failed emails and generate alerts
    
    Preconditions:
    - Database is accessible
    
    Postconditions:
    - Failed emails logged
    - Alert generated if threshold exceeded
    """
    logger.info("Starting failed email monitoring...")
    
    db = SessionLocal()
    
    try:
        now = datetime.now(timezone.utc)
        one_hour_ago = now - timedelta(hours=1)
        
        # Get failed emails from the last hour
        recent_failed = db.query(EmailQueue).filter(
            EmailQueue.status == "failed",
            EmailQueue.created_at >= one_hour_ago
        ).all()
        
        # Get all failed emails
        total_failed = db.query(EmailQueue).filter(
            EmailQueue.status == "failed"
        ).count()
        
        # Get pending emails with high retry count
        high_retry_pending = db.query(EmailQueue).filter(
            EmailQueue.status == "pending",
            EmailQueue.retry_count >= 2
        ).all()
        
        logger.info(f"Failed emails in last hour: {len(recent_failed)}")
        logger.info(f"Total failed emails: {total_failed}")
        logger.info(f"Pending emails with high retry count: {len(high_retry_pending)}")
        
        # Alert if too many failures
        if len(recent_failed) > 10:
            logger.warning(f"⚠️ ALERT: {len(recent_failed)} emails failed in the last hour!")
            logger.warning("This may indicate an SMTP server issue or configuration problem.")
        
        # Log details of recent failures
        if recent_failed:
            logger.info("Recent failed emails:")
            for email in recent_failed[:10]:  # Show first 10
                logger.info(f"  - To: {email.to_email}, Subject: {email.subject}")
                logger.info(f"    Error: {email.error_message}")
                logger.info(f"    Retry count: {email.retry_count}/{email.max_retries}")
        
        # Log high retry pending emails
        if high_retry_pending:
            logger.warning(f"⚠️ {len(high_retry_pending)} emails are on their last retry attempt:")
            for email in high_retry_pending[:5]:  # Show first 5
                logger.warning(f"  - To: {email.to_email}, Subject: {email.subject}")
                logger.warning(f"    Retry count: {email.retry_count}/{email.max_retries}")
        
        # Summary statistics
        pending_count = db.query(EmailQueue).filter(
            EmailQueue.status == "pending"
        ).count()
        
        sent_count = db.query(EmailQueue).filter(
            EmailQueue.status == "sent",
            EmailQueue.sent_at >= one_hour_ago
        ).count()
        
        logger.info(f"Email queue summary:")
        logger.info(f"  - Pending: {pending_count}")
        logger.info(f"  - Sent (last hour): {sent_count}")
        logger.info(f"  - Failed (last hour): {len(recent_failed)}")
        logger.info(f"  - Total failed: {total_failed}")
        
        return len(recent_failed)
        
    except Exception as e:
        logger.error(f"Error monitoring failed emails: {str(e)}", exc_info=True)
        return -1
        
    finally:
        db.close()


if __name__ == "__main__":
    start_time = datetime.now()
    
    # Monitor failed emails
    failed_count = monitor_failed_emails()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info(f"Script completed in {duration:.2f} seconds")
    
    # Exit with appropriate code
    sys.exit(0 if failed_count >= 0 else 1)
