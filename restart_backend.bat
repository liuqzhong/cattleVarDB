@echo off
REM ============================================
REM Restart Backend Service
REM 重启后端服务
REM ============================================

echo.
echo ============================================
echo Stopping any existing backend processes...
echo ============================================
echo.

REM Kill any existing uvicorn processes on port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    echo Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 /nobreak >nul

echo.
echo ============================================
echo Starting backend server...
echo ============================================
echo.

cd /d D:\CCProject\VEP\cattleVarDB\backend
call venv312\Scripts\activate.bat
echo Backend starting on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
