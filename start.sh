#!/bin/bash

# 设置脚本在任何命令失败时继续执行，但会显示错误
set -e

# 设置UTF-8编码
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "   抖音短视频文案提取工具"
echo "========================================"
echo

# 检查 Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ [错误] 未检测到 Python，请先安装 Python 3.10+"
    exit 1
fi

# 确定Python命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# 检查Python版本
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | sed 's/.* \([0-9]\).\([0-9]*\).*/\1\2/')
if [ "$PYTHON_VERSION" -lt "310" ]; then
    echo "❌ [错误] Python 版本过低，需要 Python 3.10+"
    echo "   当前版本: $($PYTHON_CMD --version)"
    exit 1
fi

# 检查 FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  [警告] 未检测到 FFmpeg，音频提取功能将不可用"
    echo "         Ubuntu/Debian: sudo apt install ffmpeg"
    echo "         CentOS/RHEL: sudo yum install ffmpeg"
    echo "         macOS: brew install ffmpeg"
    echo
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        echo "💡 [提示] 未找到 .env 配置文件，正在从 env.example 创建..."
        cp env.example .env
        echo "         请编辑 .env 文件填入你的 API Key"
        echo
    else
        echo "⚠️  [警告] 未找到 .env 配置文件"
    fi
fi

# 检查是否有虚拟环境，如果没有则建议创建
if [ -z "$VIRTUAL_ENV" ] && [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "💡 [建议] 检测到未使用虚拟环境，建议创建虚拟环境："
    echo "         python3 -m venv venv"
    echo "         source venv/bin/activate"
    echo "         然后重新运行此脚本"
    echo
    read -p "是否继续在全局环境安装？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 激活虚拟环境（如果存在）
if [ -f "venv/bin/activate" ]; then
    echo "🔧 [信息] 激活虚拟环境 venv/"
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    echo "🔧 [信息] 激活虚拟环境 .venv/"
    source .venv/bin/activate
fi

# 检查依赖
echo "📦 [1/2] 检查 Python 依赖..."
if ! $PYTHON_CMD -c "import fastapi" &> /dev/null; then
    echo "       正在安装依赖，首次启动可能需要几分钟..."
    if ! $PYTHON_CMD -m pip install -r requirements.txt; then
        echo "❌ [错误] 依赖安装失败，请检查网络或手动执行:"
        echo "         $PYTHON_CMD -m pip install -r requirements.txt"
        exit 1
    fi
fi

# 检查端口是否被占用
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null; then
    echo "⚠️  [警告] 端口 8000 已被占用"
    read -p "是否停止占用进程并继续？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 停止占用端口 8000 的进程..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 2
    else
        exit 1
    fi
fi

# 启动服务
echo "🚀 [2/2] 启动服务..."
echo
echo "----------------------------------------"
echo "   服务地址:  http://localhost:8000"
echo "   API文档:   http://localhost:8000/docs"
echo "   按 Ctrl+C 停止服务"
echo "----------------------------------------"
echo

# 捕获中断信号，优雅关闭
trap 'echo -e "\n🛑 正在停止服务..."; kill $PID 2>/dev/null; exit 0' INT TERM

# 启动服务
$PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
PID=$!

# 等待进程结束
wait $PID
