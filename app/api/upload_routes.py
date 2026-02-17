"""
本地文件上传路由 - 绕过抖音下载限制的实用方案
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import logging
import shutil
from typing import List

from app.config import settings
from app.services.pipeline import process_single
from app.models.schemas import TaskResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=TaskResponse)
async def upload_video_file(
    file: UploadFile = File(...),
    title: str = "上传的视频"
):
    """
    上传本地视频文件进行文案提取
    """
    # 验证文件类型
    if not file.content_type or not file.content_type.startswith('video/'):
        raise HTTPException(
            status_code=400,
            detail="请上传视频文件 (支持mp4, mov, avi等格式)"
        )
    
    # 验证文件大小 (限制100MB)
    max_size = 100 * 1024 * 1024  # 100MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail="文件大小不能超过100MB"
        )
    
    try:
        # 保存上传的文件
        temp_dir = settings.temp_dir
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = temp_dir / file.filename
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"文件上传成功: {file_path}")
        
        # 创建虚拟URL用于处理
        fake_url = f"file:///{file.filename}"
        
        # 直接处理上传的文件，跳过下载阶段
        from app.services.audio_extractor import audio_extractor
        from app.services.transcriber import transcriber_service
        from app.services.llm_enhancer import llm_enhancer
        from app.models.schemas import TaskStatus, TaskResponse
        from app.utils.helpers import generate_task_id
        
        task_id = generate_task_id()
        task = TaskResponse(task_id=task_id, url=fake_url, status=TaskStatus.PENDING)
        
        # 创建视频信息
        from app.models.schemas import VideoInfo
        task.video_info = VideoInfo(
            video_id=task_id,
            title=title,
            author="上传用户",
            duration=0,  # 可以后续通过ffprobe获取
            url=fake_url,
            cover_url=""
        )
        
        # 直接从上传的文件提取音频
        task.status = TaskStatus.EXTRACTING_AUDIO
        audio_path = await audio_extractor.extract_audio(file_path)
        
        # 转录音频
        task.status = TaskStatus.TRANSCRIBING
        transcript = await transcriber_service.transcribe(audio_path)
        task.transcript = transcript
        
        # LLM增强（如果启用）
        if settings.llm_enabled and transcript.raw_text:
            task.status = TaskStatus.ENHANCING
            enhanced_text = await llm_enhancer.enhance(transcript.raw_text)
            transcript.enhanced_text = enhanced_text
        
        task.status = TaskStatus.COMPLETED
        
        return task
        
    except Exception as e:
        logger.error(f"文件处理失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"文件处理失败: {str(e)}"
        )


@router.post("/upload-batch", response_model=TaskResponse)
async def upload_multiple_files(
    files: List[UploadFile] = File(...)
):
    """
    批量上传视频文件
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="单次最多上传10个文件"
        )
    
    results = []
    
    for file in files:
        try:
            # 重用单文件上传逻辑
            result = await upload_video_file(file, file.filename)
            results.append(result)
        except Exception as e:
            logger.error(f"文件 {file.filename} 处理失败: {e}")
            continue
    
    return JSONResponse(content={
        "message": f"成功处理 {len(results)} 个文件",
        "results": results
    })
