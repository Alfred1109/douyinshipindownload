#!/bin/bash

echo "🛑 停止抖音短视频文案提取工具..."

# 查找并停止uvicorn进程
PIDS=$(pgrep -f "uvicorn app.main:app")

if [ -z "$PIDS" ]; then
    echo "❌ 未找到运行中的服务"
    exit 1
fi

echo "📋 找到以下进程:"
ps -fp $PIDS

echo
read -p "确认停止这些进程？(Y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "❌ 已取消"
    exit 0
fi

# 优雅停止
echo "🔄 正在停止服务..."
kill $PIDS

# 等待进程结束
sleep 3

# 检查是否还在运行
REMAINING=$(pgrep -f "uvicorn app.main:app")
if [ ! -z "$REMAINING" ]; then
    echo "⚠️  进程未能正常结束，强制停止..."
    kill -9 $REMAINING
    sleep 1
fi

# 最终检查
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo "❌ 停止失败，请手动停止进程"
    exit 1
else
    echo "✅ 服务已成功停止"
fi
