@echo off
REM CV Optimizer ATS - Quick Start Script for Windows

echo ==========================================
echo CV Optimizer for ATS - Startup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo Python found: 
python --version

REM Check if virtual environment exists
if not exist "venv" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo.
echo Installing dependencies...
pip install -q -r requirements.txt

REM Check for .env file
if not exist ".env" (
    echo.
    echo Warning: .env file not found!
    echo.
    echo Please create a .env file with your DeepSeek API key:
    echo   1. Copy: copy .env.example .env
    echo   2. Edit: notepad .env
    echo   3. Add your DeepSeek API key
    echo.
    echo Get your API key at: https://platform.deepseek.com/api_keys
    pause
    exit /b 1
)

echo Configuration loaded

REM Run the app
echo.
echo ==========================================
echo Starting CV Optimizer...
echo ==========================================
echo.
echo Opening browser at: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py
pause
