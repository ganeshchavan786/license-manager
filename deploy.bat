@echo off
REM SalaryPay License Server - Windows Deployment Script
REM Usage: deploy.bat

echo ================================================
echo SalaryPay License Server - Deployment
echo ================================================

REM 1. Check Python
echo Checking Python...
python --version

REM 2. Install backend dependencies
echo Installing backend dependencies...
pip install -r requirements.txt -q

REM 3. Run database migrations
echo Running database migrations...
alembic upgrade head

REM 4. Build frontend
echo Building frontend...
cd frontend
call npm install --silent
call npm run build
cd ..

REM 5. Backup database
echo Creating database backup...
python scripts/backup_database.py

echo.
echo ================================================
echo Deployment complete!
echo Start server: python -m uvicorn app.main:app --host 0.0.0.0 --port 8661
echo ================================================
pause
