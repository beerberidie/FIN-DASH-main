@echo off
REM Start script for FIN-DASH backend (Windows)

echo Starting FIN-DASH Backend...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Ensure data directory exists
if not exist "..\data\backups" mkdir "..\data\backups"

REM Start the server
echo Starting FastAPI server on http://localhost:8777
python app.py

pause

