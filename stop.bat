@echo off
chcp 65001 >nul 2>&1

echo ========================================
echo   停止抖音短视频文案提取工具
echo ========================================
echo.

:: 查找并终止 uvicorn 进程
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq python.exe" /v 2^>nul ^| findstr /i "uvicorn"') do (
    echo 正在停止进程 PID: %%a
    taskkill /pid %%a /f >nul 2>&1
)

:: 备用方案：通过端口查找
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo 正在停止端口 8000 上的进程 PID: %%a
    taskkill /pid %%a /f >nul 2>&1
)

echo.
echo 服务已停止。
timeout /t 2 >nul
