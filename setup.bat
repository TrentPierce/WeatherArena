@echo off
REM Setup script for WeatherArena (Windows)

echo =========================================
echo WeatherArena Setup (Windows)
echo =========================================
echo.

REM Check Python version
echo Checking Python version...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+ from https://python.org
    exit /b 1
)
echo.
echo.

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
    echo.
) else (
    echo Virtual environment already exists
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Dependencies installed
echo.

REM Check for .env file
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env >nul
    echo .env file created
    echo.
    echo IMPORTANT: Please edit .env and add your Supabase credentials:
    echo    - SUPABASE_URL
    echo    - SUPABASE_KEY
    echo.
) else (
    echo .env file already exists
    echo.
)

echo =========================================
echo Setup complete!
echo =========================================
echo.
echo Next steps:
echo 1. Edit .env with your Supabase credentials
echo 2. Run tests: python scripts\test_setup.py
echo 3. Run verification: python scripts\weather_verification.py
echo.
pause
