@echo off
REM FIN-DASH Application Startup Script for Windows
REM ================================================
REM This script starts both the backend and frontend servers

echo.
echo ============================================================
echo              FIN-DASH Application Startup
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org/
    pause
    exit /b 1
)

echo [INFO] Python and Node.js found
echo.

REM Setup backend virtual environment if it doesn't exist
if not exist "backend\venv" (
    echo [INFO] Creating Python virtual environment...
    cd backend
    python -m venv venv
    cd ..
    echo [SUCCESS] Virtual environment created
) else (
    echo [SUCCESS] Virtual environment already exists
)

REM Install backend dependencies
echo [INFO] Installing backend dependencies...
cd backend
call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to install backend dependencies
    pause
    exit /b 1
)
cd ..
echo [SUCCESS] Backend dependencies installed

REM Install frontend dependencies
if not exist "node_modules" (
    echo [INFO] Installing frontend dependencies (this may take a few minutes)...
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install frontend dependencies
        pause
        exit /b 1
    )
    echo [SUCCESS] Frontend dependencies installed
) else (
    echo [SUCCESS] Frontend dependencies already installed
)

echo.
echo ============================================================
echo                   Starting Servers
echo ============================================================
echo.

REM Start backend in a new window
echo [INFO] Starting backend server...
start "FIN-DASH Backend" cmd /k "cd backend && venv\Scripts\activate.bat && python app.py"
timeout /t 3 /nobreak >nul

REM Start frontend in a new window
echo [INFO] Starting frontend server...
start "FIN-DASH Frontend" cmd /k "npm run dev"
timeout /t 3 /nobreak >nul

echo.
echo ============================================================
echo              FIN-DASH is Running!
echo ============================================================
echo.
echo [SUCCESS] Backend API: http://127.0.0.1:8777
echo [SUCCESS] API Docs: http://127.0.0.1:8777/docs
echo [SUCCESS] Frontend: http://localhost:5173
echo.
echo Two new windows have been opened for backend and frontend.
echo Close those windows to stop the servers.
echo.
echo Press any key to exit this window...
pause >nul

