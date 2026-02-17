"""
编排流水线
串联视频下载 → 音频提取 → 语音识别 → LLM增强 的完整流程
支持单个和批量处理
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional

from app.config import settings
from app.models.schemas import (
    BatchTaskResponse,
    TaskResponse,
    TaskStatus,
    TranscriptResult,
)
from app.services.audio_extractor import audio_extractor
from app.services.douyin_parser import douyin_parser
from app.services.llm_enhancer import llm_enhancer
from app.services.transcriber import transcriber_service
from app.utils.helpers import clean_temp_files, generate_batch_id, generate_task_id

logger = logging.getLogger(__name__)

# 任务存储（生产环境可替换为 Redis）
_task_store: Dict[str, TaskResponse] = {}
_batch_store: Dict[str, BatchTaskResponse] = {}


def get_task(task_id: str) -> Optional[TaskResponse]:
    return _task_store.get(task_id)


def get_batch(batch_id: str) -> Optional[BatchTaskResponse]:
    return _batch_store.get(batch_id)


def create_task(url: str) -> tuple[str, TaskResponse]:
    """创建新任务并返回任务ID和任务对象"""
    task_id = generate_task_id()
    task = TaskResponse(task_id=task_id, url=url, status=TaskStatus.PENDING, progress=0.0)
    _task_store[task_id] = task
    return task_id, task


async def process_single(
    task_id: str,
    url: str,
    use_llm: bool = True,
    on_progress: Optional[Callable] = None,
) -> TaskResponse:
    """
    处理单个视频的完整流水线

    Args:
        task_id: 任务ID
        url: 抖音视频链接
        use_llm: 是否使用大模型增强
        on_progress: 进度回调函数

    Returns:
        TaskResponse 任务结果
    """
    task = _task_store.get(task_id)
    if not task:
        raise ValueError(f"任务不存在: {task_id}")

    video_path = None
    audio_path = None

    try:
        # ─── 阶段1: 下载视频 ───
        task.status = TaskStatus.DOWNLOADING
        task.progress = 0.1
        if on_progress:
            await _safe_callback(on_progress, task)

        video_path, video_info = await douyin_parser.download_video(url)
        task.video_info = video_info
        task.progress = 0.3

        # ─── 阶段2: 提取音频 ───
        task.status = TaskStatus.EXTRACTING_AUDIO
        task.progress = 0.4
        if on_progress:
            await _safe_callback(on_progress, task)

        audio_path = await audio_extractor.extract(video_path)
        task.progress = 0.5

        # ─── 阶段3: 语音识别 ───
        task.status = TaskStatus.TRANSCRIBING
        task.progress = 0.6
        if on_progress:
            await _safe_callback(on_progress, task)

        transcript = await transcriber_service.transcribe(audio_path)
        task.progress = 0.8

        # ─── 阶段4: LLM 增强 ───
        if use_llm and settings.llm_enabled and (settings.ark_api_key or settings.llm_api_key):
            task.status = TaskStatus.ENHANCING
            task.progress = 0.85
            if on_progress:
                await _safe_callback(on_progress, task)

            enhanced_text = await llm_enhancer.enhance(transcript.raw_text)
            transcript.enhanced_text = enhanced_text
        else:
            transcript.enhanced_text = transcript.raw_text

        # ─── 完成 ───
        task.transcript = transcript
        task.status = TaskStatus.COMPLETED
        task.progress = 1.0
        task.completed_at = datetime.now()

        # 保存结果到文件
        await _save_result(task)

        logger.info(f"任务完成: {task_id} - {video_info.title}")

    except Exception as e:
        logger.error(f"任务失败: {task_id} - {e}", exc_info=True)
        task.status = TaskStatus.FAILED
        task.error = str(e)

    finally:
        # 清理临时文件
        if video_path:
            clean_temp_files(video_path)
        if audio_path:
            clean_temp_files(audio_path)

        if on_progress:
            await _safe_callback(on_progress, task)

    return task


async def process_batch(
    urls: List[str],
    use_llm: bool = True,
    on_progress: Optional[Callable] = None,
) -> BatchTaskResponse:
    """
    批量处理多个视频

    Args:
        urls: 视频链接列表
        use_llm: 是否使用大模型增强
        on_progress: 进度回调

    Returns:
        BatchTaskResponse 批量任务结果
    """
    batch_id = generate_batch_id()
    batch = BatchTaskResponse(
        batch_id=batch_id,
        total=len(urls),
    )
    _batch_store[batch_id] = batch

    semaphore = asyncio.Semaphore(settings.max_concurrent_tasks)

    async def _process_one(url: str):
        async with semaphore:
            # 为批量任务中的每个子任务创建独立的task_id
            task_id, _ = create_task(url)
            result = await process_single(task_id, url, use_llm=use_llm)
            batch.tasks.append(result)
            if result.status == TaskStatus.COMPLETED:
                batch.completed += 1
            else:
                batch.failed += 1
            if on_progress:
                await _safe_callback(on_progress, batch)
            return result

    # 并发执行所有任务（受 semaphore 控制并发数）
    logger.info(f"开始批量处理: {batch_id}，共 {len(urls)} 个视频")
    await asyncio.gather(*[_process_one(url) for url in urls], return_exceptions=True)
    logger.info(
        f"批量处理完成: {batch_id}，"
        f"成功 {batch.completed}/{batch.total}，"
        f"失败 {batch.failed}"
    )

    return batch


async def _save_result(task: TaskResponse):
    """保存结果到 output 目录"""
    try:
        output_dir = settings.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        title = task.video_info.title if task.video_info else task.task_id
        # 清理文件名
        safe_title = "".join(c if c.isalnum() or c in '._- ' else '_' for c in title)[:80]

        result = {
            "task_id": task.task_id,
            "url": task.url,
            "video_info": task.video_info.model_dump() if task.video_info else None,
            "transcript": task.transcript.model_dump() if task.transcript else None,
            "created_at": task.created_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        }

        output_file = output_dir / f"{safe_title}.json"
        output_file.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )

        # 同时保存纯文本版本
        if task.transcript:
            txt_file = output_dir / f"{safe_title}.txt"
            content = f"标题: {title}\n"
            content += f"作者: {task.video_info.author if task.video_info else '未知'}\n"
            content += f"链接: {task.url}\n"
            content += f"{'=' * 50}\n\n"
            content += task.transcript.enhanced_text or task.transcript.raw_text
            txt_file.write_text(content, encoding='utf-8')

        logger.info(f"结果已保存: {output_file}")

    except Exception as e:
        logger.warning(f"保存结果失败: {e}")


async def _safe_callback(callback: Callable, *args):
    """安全执行回调"""
    try:
        result = callback(*args)
        if asyncio.iscoroutine(result):
            await result
    except Exception as e:
        logger.warning(f"回调执行失败: {e}")
