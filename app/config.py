from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./license.db"  # SQLite default
    SECRET_KEY: str = "test-secret-key-change-this-in-production-minimum-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    LICENSE_ENCRYPTION_KEY: str = "test-encryption-key-for-local-testing-only"
    RAZORPAY_KEY_ID: str = "rzp_test_xxxxxxxxxx"
    RAZORPAY_KEY_SECRET: str = "test_secret_here"
    APP_NAME: str = "SalaryPay License Server"
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    TRIAL_DAYS: int = 7
    FREE_OFFLINE_GRACE: int = 15
    BASIC_OFFLINE_GRACE: int = 15
    PREMIUM_OFFLINE_GRACE: int = 30
    
    # SMTP Configuration for Email Service
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "your-email@gmail.com"
    SMTP_PASSWORD: str = "your-app-password"
    SMTP_FROM_EMAIL: str = "noreply@salarypay.com"
    SMTP_USE_TLS: bool = True
    
    # Frontend and Support URLs
    FRONTEND_URL: str = "http://localhost:3000"
    SUPPORT_EMAIL: str = "support@salarypay.com"
    
    # Internal API Key for cron jobs
    INTERNAL_API_KEY: str = "internal-api-key-change-in-production"

    @property
    def origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"


settings = Settings()

# Plan features map
PLAN_FEATURES = {
    "trial": [
        "attendance_face", "employees_unlimited", "salary_full",
        "tax", "loans", "export_pdf", "export_excel",
        "leaves", "reports_full", "holidays"
    ],
    "free": [
        "attendance_basic", "employees_5",
        "salary_basic", "leaves", "holidays"
    ],
    "basic": [
        "attendance_face", "employees_25", "salary_full",
        "tax", "export_pdf", "export_excel",
        "leaves", "reports_basic", "holidays"
    ],
    "premium": ["*"],  # सर्व features
}

GRACE_PERIOD_DAYS = {
    "trial": 15,
    "free": 15,
    "basic": 15,
    "premium": 30,
}

PLAN_PRICES = {
    "basic": 49900,   # ₹499 in paise
    "premium": 99900, # ₹999 in paise
}
