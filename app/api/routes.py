"""
API 路由层
提供 RESTful API 接口
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.config import settings
from app.models.schemas import (
    BatchTaskRequest,
    BatchTaskResponse,
    TaskRequest,
    TaskResponse,
)
from app.services.pipeline import get_batch, get_task, process_batch, process_single
from app.utils.helpers import is_douyin_url

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["视频文案提取"])


@router.post("/extract", summary="提交视频提取任务")
async def extract_single(request: TaskRequest):
    """
    提交单个抖音视频的提取任务（异步）
    
    返回任务ID，前端可以通过 /api/task/{task_id} 查询进度
    """
    url = request.url.strip()

    if not is_douyin_url(url):
        raise HTTPException(
            status_code=400,
            detail="不支持的链接格式，请提供有效的抖音视频链接"
        )

    try:
        # 创建异步任务
        import asyncio
        from app.services.pipeline import _task_store, create_task
        
        task_id, task = create_task(url)
        
        # 在后台启动处理任务
        asyncio.create_task(process_single(task_id, url, use_llm=request.use_llm))
        
        # 立即返回任务ID
        return task
        
    except Exception as e:
        logger.error(f"创建任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.post("/extract/batch", response_model=BatchTaskResponse, summary="批量提取视频文案")
async def extract_batch(request: BatchTaskRequest):
    """
    批量提取多个抖音视频的音频文案

    支持同时处理多个视频链接，自动控制并发数
    """
    urls = [u.strip() for u in request.urls if u.strip()]

    if not urls:
        raise HTTPException(status_code=400, detail="请提供至少一个视频链接")

    if len(urls) > 50:
        raise HTTPException(status_code=400, detail="单次最多支持 50 个视频")

    # 验证所有链接
    invalid_urls = [u for u in urls if not is_douyin_url(u)]
    if invalid_urls:
        raise HTTPException(
            status_code=400,
            detail=f"以下链接格式无效: {', '.join(invalid_urls[:3])}"
        )

    try:
        result = await process_batch(urls, use_llm=request.use_llm)
        return result
    except Exception as e:
        logger.error(f"批量提取失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@router.get("/task/{task_id}", response_model=Optional[TaskResponse], summary="查询任务状态")
async def get_task_status(task_id: str):
    """查询指定任务的处理状态和结果"""
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.get("/batch/{batch_id}", response_model=Optional[BatchTaskResponse], summary="查询批量任务状态")
async def get_batch_status(batch_id: str):
    """查询批量任务的处理状态"""
    batch = get_batch(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="批量任务不存在")
    return batch


@router.get("/health", summary="健康检查")
async def health_check():
    """服务健康检查"""
    return {
        "status": "ok",
        "asr_mode": settings.asr_mode,
        "llm_enabled": settings.llm_enabled,
        "llm_key_configured": bool(settings.ark_api_key or settings.llm_api_key),
    }
