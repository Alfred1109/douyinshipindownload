@echo off
setlocal
chcp 65001 >nul 2>&1
title Douyin Video Transcript Tool

:: Auto-elevate to admin (needed for browser cookie decryption)
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)
cd /d "%~dp0"

echo ========================================
echo   Douyin Video Transcript Tool
echo ========================================
echo.

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not detected. Please install Python 3.10+ first.
    pause
    exit /b 1
)

:: Check FFmpeg
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] FFmpeg is not detected. Audio extraction may fail.
    echo        Install from https://ffmpeg.org/download.html and add to PATH.
    echo.
)

:: Create .env from template when missing
if not exist ".env" (
    if exist "env.example" (
        echo [INFO] .env not found. Creating from env.example...
        copy env.example .env >nul
        echo        Please edit .env and set your API keys.
        echo.
    )
)

:: Check dependencies
echo [1/2] Checking Python dependencies...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo       Installing requirements. First run may take a few minutes...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Dependency installation failed.
        echo        Run manually: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

:: Stop anything already listening on 8000
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo       Port 8000 is occupied by PID %%a. Stopping it...
    taskkill /pid %%a /f >nul 2>&1
)

:: Start service
echo [2/2] Starting service...
echo.
echo ----------------------------------------
echo   Service URL:  http://localhost:8000
echo   API Docs:     http://localhost:8000/docs
echo   Press Ctrl+C to stop
echo ----------------------------------------
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

pause
