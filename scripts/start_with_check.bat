@echo off
chcp 65001 >nul
echo ========================================
echo 抖音短视频文案提取工具 - 启动检查
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python 已安装
echo.

REM 检查依赖
echo 📦 检查依赖...
python -c "import fastapi, yt_dlp, rookiepy, faster_whisper" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  依赖未完全安装
    echo.
    set /p install="是否现在安装依赖？(y/n): "
    if /i "%install%"=="y" (
        echo 正在安装依赖...
        pip install -r requirements.txt
    ) else (
        echo 请手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo ✅ 依赖已安装
echo.

REM 检查 FFmpeg
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  未检测到 FFmpeg
    echo    请从 https://ffmpeg.org/download.html 下载并安装
    echo.
) else (
    echo ✅ FFmpeg 已安装
)

echo.
echo 🔍 检查 Cookies 配置...
python -c "from pathlib import Path; import sys; f = Path('temp/cookies.txt'); sys.exit(0 if f.exists() and f.stat().st_size > 100 else 1)" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Cookies 文件不存在或无效
    echo.
    echo 💡 提示：视频下载功能需要有效的 cookies
    echo.
    echo    【推荐】使用文件上传功能（无需 cookies）
    echo    访问 http://localhost:8000 上传本地视频
    echo.
    echo    【或】提取浏览器 cookies（需管理员权限）
    echo    右键点击 fix_chrome_cookies.py → 以管理员身份运行
    echo.
) else (
    echo ✅ Cookies 文件存在
)

echo.
echo ========================================
echo 🚀 启动服务...
echo ========================================
echo.
echo 访问地址:
echo   - Web 界面: http://localhost:8000
echo   - API 文档: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
