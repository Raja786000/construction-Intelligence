@echo off
echo =========================================================
echo    Construction Intelligence Hub - One-Time Setup Script
echo =========================================================
echo.

:: 1. Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from python.org and check "Add Python to PATH".
    pause
    exit /b 1
)
echo [OK] Python found:
python --version

:: 2. Check Node.js
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js / npm is not installed or not in PATH!
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js and npm found:
npm --version

:: 3. Install Python Dependencies
echo.
echo Installing Python backend dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies may have had installation warnings. Continuing...
)

:: 4. Install Frontend Dependencies
echo.
echo Installing Frontend dependencies...
cd frontend
call npm install
cd ..

:: 5. Initialize Database
echo.
echo Seeding MongoDB Database (Projects, Workers, Alerts, Weather)...
python backend/app/db/init_db.py

echo.
echo =========================================================
echo  [SUCCESS] Setup Completed!
echo  You can now start the platform by running: run_hub.bat
echo =========================================================
pause
