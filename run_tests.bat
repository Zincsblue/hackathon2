@echo off
REM Run Authentication Backend Tests
REM This script runs the comprehensive test suite

echo Running Authentication Backend Tests...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if server is running
curl -s http://localhost:8000/health >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Server is not running
    echo Please start the server first: start_server.bat
    echo.
    pause
    exit /b 1
)

REM Install requests if not already installed
python -c "import requests" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing requests library...
    pip install requests
    echo.
)

REM Run the test script
python test_auth.py

echo.
pause
