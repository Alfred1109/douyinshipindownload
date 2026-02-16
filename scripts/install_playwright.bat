@echo off
chcp 65001 >nul
echo ========================================
echo 安装 Playwright 浏览器自动化
echo ========================================
echo.

echo 📦 步骤 1: 安装 Playwright Python 包...
pip install playwright

echo.
echo 🌐 步骤 2: 安装 Chromium 浏览器...
playwright install chromium

echo.
echo ========================================
echo ✅ 安装完成！
echo ========================================
echo.
echo 现在可以使用浏览器自动化功能了
echo.
echo 测试命令:
echo   python test_playwright.py
echo.
pause
