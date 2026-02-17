"""
服务器启动脚本 - 确保 Windows 平台使用正确的事件循环
"""
import asyncio
import sys

# Windows 平台修复：必须在导入 uvicorn 之前设置
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # 禁用 reload 以确保事件循环策略生效
        loop="asyncio"  # 使用 asyncio 循环
    )
