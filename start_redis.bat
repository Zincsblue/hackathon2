@echo off
REM Start Redis Server for Rate Limiting
REM This script starts Redis in the background

echo Starting Redis server...
echo.

REM Check if Redis is installed
where redis-server >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Redis is not installed or not in PATH
    echo.
    echo To install Redis on Windows:
    echo 1. Download from: https://github.com/microsoftarchive/redis/releases
    echo 2. Or use WSL: wsl sudo service redis-server start
    echo 3. Or use Docker: docker run -d -p 6379:6379 redis:alpine
    echo.
    pause
    exit /b 1
)

REM Start Redis server
start "Redis Server" redis-server
echo Redis server started in new window
echo.
timeout /t 2 /nobreak >nul

REM Test Redis connection
redis-cli ping >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ Redis is running and responding
) else (
    echo ✗ Redis failed to start
    pause
    exit /b 1
)

echo.
echo Redis is ready for rate limiting!
pause
