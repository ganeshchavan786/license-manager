from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import mimetypes
mimetypes.add_type('text/css', '.css')
import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

from app.config import settings
from app.database import create_tables, SessionLocal
from app.routers import auth, license, payment, admin, analytics, promo, email, invoice
from app.routers import settings as settings_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SalaryPay License Server",
    description="Subscription & License management for SalaryPay HRMS",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",
)

# Initialize APScheduler
scheduler = AsyncIOScheduler()

# CORS — React frontend साठी
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers include करा
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os

# API Routes आधी असावेत
app.include_router(auth.router, prefix="/api")
app.include_router(license.router, prefix="/api")
app.include_router(payment.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(promo.router, prefix="/api")
app.include_router(email.router, prefix="/api")
app.include_router(invoice.router, prefix="/api")
app.include_router(settings_router.router)

# Frontend serving - फक्त SERVE_FRONTEND=true असेल तरच serve करा
# Production मध्ये frontend वेगळ्या domain/port वर असतो
# Development मध्ये: SERVE_FRONTEND=true uvicorn app.main:app ...
frontend_path = os.path.join(os.getcwd(), "frontend", "dist")
serve_frontend = os.getenv("SERVE_FRONTEND", "false").lower() == "true"

if serve_frontend and os.path.exists(frontend_path):
    # सर्व static files (css, js, images) serve करण्यासाठी
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

    # Client-side routing साठी (React)
    @app.exception_handler(404)
    async def not_found_exception_handler(request: Request, exc: Exception):
        if not request.url.path.startswith("/api"):
            return FileResponse(os.path.join(frontend_path, "index.html"))
        return JSONResponse(status_code=404, content={"detail": "Not Found"})


async def process_email_queue_job():
    """
    Scheduled job to process email queue
    Runs every 1 minute
    """
    from app.services.email import process_email_queue
    
    logger.info("Running scheduled email queue processing...")
    db = SessionLocal()
    try:
        sent_count = await process_email_queue(db)
        logger.info(f"Email queue job complete: {sent_count} emails sent")
    except Exception as e:
        logger.error(f"Error in email queue job: {str(e)}", exc_info=True)
    finally:
        db.close()


async def send_trial_reminders_job():
    """
    Scheduled job to send trial reminder emails
    Runs daily at 9 AM
    """
    from app.models import License
    from app.services.email import send_trial_reminder
    from datetime import timedelta, timezone
    
    logger.info("Running scheduled trial reminder check...")
    db = SessionLocal()
    reminder_count = 0
    
    try:
        now = datetime.now(timezone.utc)
        
        # Get all active trial licenses
        trial_licenses = db.query(License).filter(
            License.plan == "trial",
            License.is_active == True,
            License.trial_end.isnot(None)
        ).all()
        
        logger.info(f"Found {len(trial_licenses)} active trial licenses")
        
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
                    logger.info(f"Sending {days_remaining}-day reminder for customer {license_obj.customer_id}")
                    send_trial_reminder(
                        db=db,
                        customer_id=license_obj.customer_id,
                        days_remaining=days_remaining
                    )
                    reminder_count += 1
                except Exception as e:
                    logger.error(f"Failed to send reminder for customer {license_obj.customer_id}: {str(e)}")
        
        logger.info(f"Trial reminder job complete: {reminder_count} reminders queued")
        
    except Exception as e:
        logger.error(f"Error in trial reminder job: {str(e)}", exc_info=True)
    finally:
        db.close()


@app.on_event("startup")
async def startup():
    create_tables()
    
    # Start APScheduler
    scheduler.start()
    logger.info("✅ APScheduler started")
    
    # Schedule email queue processing (every 1 minute)
    scheduler.add_job(
        process_email_queue_job,
        trigger=IntervalTrigger(minutes=1),
        id='process_email_queue',
        name='Process Email Queue',
        replace_existing=True
    )
    logger.info("📧 Scheduled: Email queue processing (every 1 minute)")
    
    # Schedule trial reminders (daily at 9 AM)
    scheduler.add_job(
        send_trial_reminders_job,
        trigger=CronTrigger(hour=9, minute=0),
        id='send_trial_reminders',
        name='Send Trial Reminders',
        replace_existing=True
    )
    logger.info("📧 Scheduled: Trial reminders (daily at 9 AM)")
    
    print("✅ SalaryPay License Server started!")
    print(f"📖 API Docs: http://localhost:8661/docs")


@app.on_event("shutdown")
async def shutdown():
    """Shutdown event handler to stop scheduler"""
    scheduler.shutdown()
    logger.info("✅ APScheduler stopped")


@app.get("/")
def root():
    return {
        "app": "SalaryPay License Server",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health():
    return {"status": "ok"}
