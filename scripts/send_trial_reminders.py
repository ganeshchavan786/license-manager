#!/usr/bin/env python3
"""
Trial Reminder Email Script

This script sends trial reminder emails to customers whose trial is ending soon.
It checks for trials ending in 3 days and 1 day, and queues reminder emails.

Usage:
    python scripts/send_trial_reminders.py

Cron Example (daily at 9 AM):
    0 9 * * * cd /path/to/license-server && python scripts/send_trial_reminders.py >> logs/trial_reminders.log 2>&1
"""

import sys
import os
import logging
from datetime import datetime, timezone, timedelta

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models import License, Customer
from app.services.email import send_trial_reminder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def send_trial_reminders():
    """
    Send trial reminder emails for trials ending in 3 days or 1 day
    
    Preconditions:
    - Database is accessible
    - Email service is configured
    
    Postconditions:
    - Reminder emails queued for eligible customers
    - Success/failure logged
    """
    logger.info("Starting trial reminder check...")
    
    db = SessionLocal()
    reminder_count = 0
    
    try:
        now = datetime.now(timezone.utc)
        
        # Calculate target dates (3 days and 1 day from now)
        # We check for trials ending on these specific dates
        three_days_from_now = now + timedelta(days=3)
        one_day_from_now = now + timedelta(days=1)
        
        # Get all active trial licenses
        trial_licenses = db.query(License).filter(
            License.plan == "trial",
            License.is_active == True,
            License.trial_end.isnot(None)
        ).all()
        
        logger.info(f"Found {len(trial_licenses)} active trial licenses")
        
        # Check each trial license
        for license in trial_licenses:
            if not license.trial_end:
                continue
            
            # Make trial_end timezone-aware if it isn't
            trial_end = license.trial_end
            if trial_end.tzinfo is None:
                trial_end = trial_end.replace(tzinfo=timezone.utc)
            
            # Calculate days remaining (rounded to nearest day)
            days_remaining = (trial_end - now).days
            
            # Send reminder if trial ends in 3 days or 1 day
            if days_remaining == 3 or days_remaining == 1:
                try:
                    logger.info(f"Sending {days_remaining}-day reminder for customer {license.customer_id}")
                    
                    send_trial_reminder(
                        db=db,
                        customer_id=license.customer_id,
                        days_remaining=days_remaining
                    )
                    
                    reminder_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to send reminder for customer {license.customer_id}: {str(e)}")
        
        logger.info(f"Trial reminder check complete: {reminder_count} reminders queued")
        
        return reminder_count
        
    except Exception as e:
        logger.error(f"Error in trial reminder check: {str(e)}", exc_info=True)
        return 0
        
    finally:
        db.close()


if __name__ == "__main__":
    start_time = datetime.now()
    
    # Send trial reminders
    reminder_count = send_trial_reminders()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info(f"Script completed in {duration:.2f} seconds")
    
    # Exit with appropriate code
    sys.exit(0 if reminder_count >= 0 else 1)
