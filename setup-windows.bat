@echo off
echo ================================================
echo  SalaryPay License Server - Windows Setup v4
echo ================================================
echo.

REM Step 1: Virtual Environment
echo [1/4] Virtual environment tayar karto...
if exist venv rmdir /s /q venv
python -m venv venv
if errorlevel 1 (
    echo ERROR: Python check kara
    pause
    exit /b 1
)
echo Done!
echo.

REM Step 2: Install
echo [2/4] Dependencies install karto...
venv\Scripts\python.exe -m pip install --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org --quiet

venv\Scripts\python.exe -m pip install -r requirements-windows.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org

if errorlevel 1 (
    echo ERROR: Install failed - mobile hotspot try kara
    pause
    exit /b 1
)
echo Done!
echo.

REM Step 3: .env
if not exist .env (
    echo [3/4] .env file tayar karto...
    copy .env.example .env > nul
    echo Done!
) else (
    echo [3/4] .env already exists - skip
)
echo.

REM Step 4: Run
echo [4/4] Server suru karto...
echo.
echo ================================================
echo  Browser madhye ughadaa: http://localhost:8661/docs
echo  Thambavayla: Ctrl+C
echo ================================================
echo.

venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8661 --reload

pause
