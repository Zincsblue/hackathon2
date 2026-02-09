@echo off
REM Start FastAPI Backend Server
REM This script starts the authentication backend

echo Starting FastAPI Backend Server...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found
    echo Please run: python -m venv venv
    echo Then: venv\Scripts\activate
    echo Then: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import fastapi" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Dependencies not installed
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Start the server
echo Starting server at http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
