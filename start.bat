@echo off
chcp 65001 >nul 2>&1
title 抖音短视频文案提取工具

:: ─── 自动请求管理员权限（Chrome v130+ cookies 解密需要） ───
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在请求管理员权限...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)
cd /d "%~dp0"

echo ========================================
echo   抖音短视频文案提取工具
echo ========================================
echo.

:: 检查 Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

:: 检查 FFmpeg
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 未检测到 FFmpeg，音频提取功能将不可用
    echo         请从 https://ffmpeg.org/download.html 下载并添加到 PATH
    echo.
)

:: 检查 .env 文件
if not exist ".env" (
    if exist "env.example" (
        echo [提示] 未找到 .env 配置文件，正在从 env.example 创建...
        copy env.example .env >nul
        echo         请编辑 .env 文件填入你的 API Key
        echo.
    )
)

:: 检查依赖
echo [1/2] 检查 Python 依赖...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo       正在安装依赖，首次启动可能需要几分钟...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败，请检查网络或手动执行: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

:: 启动服务
echo [2/2] 启动服务...
echo.
echo ----------------------------------------
echo   服务地址:  http://localhost:8000
echo   API文档:   http://localhost:8000/docs
echo   按 Ctrl+C 停止服务
echo ----------------------------------------
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

pause
