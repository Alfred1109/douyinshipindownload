@echo off
setlocal
chcp 65001 >nul 2>&1
title Restart Douyin Video Transcript Tool

:: Single UAC prompt for full restart flow
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)
cd /d "%~dp0"

echo ========================================
echo   Restart Douyin Video Transcript Tool
echo ========================================
echo.

:: Stop old service
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo Stopping process on port 8000, PID: %%a
    taskkill /pid %%a /f >nul 2>&1
)

:: Start new service (reuses full checks in start.bat)
call start.bat
