@echo off
echo =========================================================
echo    Starting Construction Intelligence Hub
echo =========================================================
echo.

echo [1/3] Launching FastAPI Backend Server on port 8000...
start "Construction Intelligence - Backend" cmd /k "python -m  uvicorn backend.main:app --port 8000 --reload"

echo [2/3] Launching React Vite Frontend on port 5173...
start "Construction Intelligence - Frontend" cmd /k "cd frontend && npm run dev"

echo [3/3] Waiting 4 seconds for servers to initialize...
timeout /t 4 >nul

echo.
echo Opening Application in Browser...
start http://localhost:5173/

echo.
echo =========================================================
echo  Construction Intelligence Hub is now RUNNING!
echo  - Web App:      http://localhost:5173/
echo  - Backend API:  http://127.0.0.1:8000/
echo  - API Docs:     http://127.0.0.1:8000/docs
echo.
echo  Keep the two opened command prompt windows open.
echo  To stop the servers, simply close those windows.
echo =========================================================
