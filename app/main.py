"""
FastAPI 应用主入口
"""

import logging
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.api.upload_routes import router as upload_router
from app.config import BASE_DIR, settings

# ─── 日志配置 ───
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)

# ─── 创建 FastAPI 应用 ───
app = FastAPI(
    title=settings.app_name,
    description="抖音短视频音频文案提取工具 - 支持批量处理与大模型增强",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS 中间件 ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── 注册路由 ───
app.include_router(router)
app.include_router(upload_router, prefix="/api", tags=["文件上传"])

# ─── 静态文件 ───
web_dir = BASE_DIR / "web"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")


@app.get("/", include_in_schema=False)
async def index():
    """返回前端页面"""
    index_file = web_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": settings.app_name, "docs": "/docs"}


@app.on_event("startup")
async def startup():
    logger.info(f"🚀 {settings.app_name} 启动成功")
    logger.info(f"   ASR 模式: {settings.asr_mode}")
    logger.info(f"   LLM 增强: {'启用' if settings.llm_enabled else '禁用'}")
    logger.info(f"   并发任务: {settings.max_concurrent_tasks}")
    logger.info(f"   输出目录: {settings.output_dir}")
    settings.ensure_dirs()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
