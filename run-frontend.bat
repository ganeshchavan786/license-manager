@echo off
echo ================================================
echo  SalaryPay License UI - Windows Setup
echo ================================================
echo.

cd frontend

REM Check if node_modules exists
if not exist node_modules (
    echo [1/2] Dependencies install karto...
    call npm install
    if errorlevel 1 (
        echo ERROR: npm install failed
        pause
        exit /b 1
    )
    echo Done!
    echo.
)

echo [2/2] UI suru karto...
echo.
echo ================================================
echo  Browser madhye ughadaa: http://localhost:3441
echo  Thambavayla: Ctrl+C
echo ================================================
echo.

call npm run dev

pause
