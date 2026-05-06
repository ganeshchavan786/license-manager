#!/usr/bin/env python3
"""
Email Queue Processing Script

This script processes the email queue by sending pending emails via SMTP.
It can be run as a cron job or manually for testing.

Usage:
    python scripts/process_emails.py

Cron Example (every 1 minute):
    * * * * * cd /path/to/license-server && python scripts/process_emails.py >> logs/email_queue.log 2>&1
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.services.email import process_email_queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """
    Main function to process email queue
    
    Preconditions:
    - Database is accessible
    - SMTP server is configured
    
    Postconditions:
    - Pending emails are processed
    - Success/failure logged
    """
    logger.info("Starting email queue processing...")
    
    db = SessionLocal()
    try:
        # Process email queue
        sent_count = await process_email_queue(db)
        
        logger.info(f"Email queue processing complete: {sent_count} emails sent")
        
        return sent_count
        
    except Exception as e:
        logger.error(f"Error processing email queue: {str(e)}", exc_info=True)
        return 0
        
    finally:
        db.close()


if __name__ == "__main__":
    start_time = datetime.now()
    
    # Run async main function
    sent_count = asyncio.run(main())
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info(f"Script completed in {duration:.2f} seconds")
    
    # Exit with appropriate code
    sys.exit(0 if sent_count >= 0 else 1)
