@echo off
echo SalaryPay License Server suru karto...
echo.
echo Server: http://localhost:8661
echo Docs:   http://localhost:8661/docs
echo.
echo Thambavayla Ctrl+C daba
echo.
venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8661 --reload
pause
