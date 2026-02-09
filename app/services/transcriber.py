"""
语音转文字服务
支持本地 faster-whisper 和 OpenAI Whisper API 两种模式
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Optional

from app.config import settings
from app.models.schemas import TranscriptResult, TranscriptSegment

logger = logging.getLogger(__name__)


class LocalTranscriber:
    """
    本地 Whisper 转录器
    使用 faster-whisper (CTranslate2 后端) 实现高效的本地语音识别
    """

    def __init__(self):
        self._model = None

    def _get_model(self):
        """懒加载模型（首次调用时加载）"""
        if self._model is None:
            from faster_whisper import WhisperModel

            device = settings.whisper_device
            if device == "auto":
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"

            compute_type = settings.whisper_compute_type
            if device == "cpu" and compute_type == "float16":
                compute_type = "int8"  # CPU 不支持 float16

            logger.info(
                f"加载 Whisper 模型: {settings.whisper_model_size} "
                f"(设备: {device}, 精度: {compute_type})"
            )
            self._model = WhisperModel(
                settings.whisper_model_size,
                device=device,
                compute_type=compute_type,
            )
            logger.info("Whisper 模型加载完成")
        return self._model

    async def transcribe(self, audio_path: Path) -> TranscriptResult:
        """
        转录音频文件

        Args:
            audio_path: 音频文件路径

        Returns:
            TranscriptResult 转录结果
        """
        def _transcribe():
            model = self._get_model()

            segments_iter, info = model.transcribe(
                str(audio_path),
                language=settings.whisper_language or None,
                beam_size=5,
                best_of=5,
                vad_filter=True,           # 启用 VAD 过滤静音
                vad_parameters=dict(
                    min_silence_duration_ms=500,
                    speech_pad_ms=200,
                ),
                word_timestamps=False,
            )

            segments: List[TranscriptSegment] = []
            full_text_parts = []

            for seg in segments_iter:
                segment = TranscriptSegment(
                    start=round(seg.start, 3),
                    end=round(seg.end, 3),
                    text=seg.text.strip(),
                )
                segments.append(segment)
                full_text_parts.append(seg.text.strip())

            raw_text = ''.join(full_text_parts)

            return TranscriptResult(
                raw_text=raw_text,
                segments=segments,
                language=info.language,
                confidence=round(info.language_probability, 4),
            )

        logger.info(f"开始本地语音识别: {audio_path.name}")
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _transcribe)
        logger.info(f"语音识别完成，共 {len(result.segments)} 个片段，{len(result.raw_text)} 字")
        return result


class APITranscriber:
    """
    OpenAI Whisper API 转录器
    适用于没有本地 GPU 或需要快速处理的场景
    """

    async def transcribe(self, audio_path: Path) -> TranscriptResult:
        """
        使用 OpenAI Whisper API 转录

        Args:
            audio_path: 音频文件路径

        Returns:
            TranscriptResult 转录结果
        """
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_api_base,
        )

        logger.info(f"开始 API 语音识别: {audio_path.name}")

        with open(audio_path, 'rb') as f:
            # 获取详细的时间轴结果
            response = await client.audio.transcriptions.create(
                model=settings.openai_whisper_model,
                file=f,
                language=settings.whisper_language or None,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )

        segments = []
        if hasattr(response, 'segments') and response.segments:
            for seg in response.segments:
                segments.append(TranscriptSegment(
                    start=round(seg['start'], 3),
                    end=round(seg['end'], 3),
                    text=seg['text'].strip(),
                ))

        raw_text = response.text if hasattr(response, 'text') else ''

        result = TranscriptResult(
            raw_text=raw_text,
            segments=segments,
            language=getattr(response, 'language', settings.whisper_language),
            confidence=0.0,
        )

        logger.info(f"API 语音识别完成，{len(result.raw_text)} 字")
        return result


class TranscriberService:
    """
    转录服务统一入口
    根据配置自动选择本地模型或 API 模式
    """

    def __init__(self):
        self._local: Optional[LocalTranscriber] = None
        self._api: Optional[APITranscriber] = None

    def _get_transcriber(self):
        if settings.asr_mode == "api":
            if self._api is None:
                self._api = APITranscriber()
            return self._api
        else:
            if self._local is None:
                self._local = LocalTranscriber()
            return self._local

    async def transcribe(self, audio_path: Path) -> TranscriptResult:
        """执行语音转文字"""
        transcriber = self._get_transcriber()
        return await transcriber.transcribe(audio_path)


# 全局单例
transcriber_service = TranscriberService()
