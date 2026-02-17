"""
数据模型定义
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    EXTRACTING_AUDIO = "extracting_audio"
    TRANSCRIBING = "transcribing"
    ENHANCING = "enhancing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoInfo(BaseModel):
    """视频信息"""
    video_id: str = ""
    title: str = ""
    author: str = ""
    duration: float = 0.0
    url: str = ""
    cover_url: str = ""


class TranscriptSegment(BaseModel):
    """转录片段"""
    start: float = Field(description="开始时间(秒)")
    end: float = Field(description="结束时间(秒)")
    text: str = Field(description="文字内容")


class TranscriptResult(BaseModel):
    """转录结果"""
    raw_text: str = Field(default="", description="原始ASR识别文本")
    enhanced_text: str = Field(default="", description="大模型增强后的文本")
    segments: List[TranscriptSegment] = Field(default_factory=list, description="时间轴片段")
    language: str = Field(default="", description="检测到的语言")
    confidence: float = Field(default=0.0, description="整体置信度")


class TaskRequest(BaseModel):
    """单个任务请求"""
    url: str = Field(description="抖音视频链接")
    use_llm: bool = Field(default=True, description="是否使用大模型增强")


class BatchTaskRequest(BaseModel):
    """批量任务请求"""
    urls: List[str] = Field(description="抖音视频链接列表")
    use_llm: bool = Field(default=True, description="是否使用大模型增强")


class TaskResponse(BaseModel):
    """任务响应"""
    task_id: str
    url: str
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    video_info: Optional[VideoInfo] = None
    transcript: Optional[TranscriptResult] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class BatchTaskResponse(BaseModel):
    """批量任务响应"""
    batch_id: str
    total: int
    completed: int = 0
    failed: int = 0
    tasks: List[TaskResponse] = Field(default_factory=list)
