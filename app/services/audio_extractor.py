"""
音频提取服务
从视频文件中提取音频，转换为 ASR 友好的格式
"""

import asyncio
import logging
import subprocess
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


class AudioExtractor:
    """从视频中提取音频"""

    # ASR 最佳实践参数
    SAMPLE_RATE = 16000      # 16kHz 采样率
    CHANNELS = 1             # 单声道
    OUTPUT_FORMAT = "wav"    # WAV 无损格式

    async def extract(self, video_path: Path, output_path: Path = None) -> Path:
        """
        从视频文件提取音频

        Args:
            video_path: 视频文件路径
            output_path: 输出音频路径（可选）

        Returns:
            音频文件路径
        """
        if output_path is None:
            output_path = video_path.with_suffix(f".{self.OUTPUT_FORMAT}")

        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-vn',                              # 不要视频
            '-acodec', 'pcm_s16le',             # 16-bit PCM
            '-ar', str(self.SAMPLE_RATE),        # 采样率
            '-ac', str(self.CHANNELS),           # 声道数
            '-y',                                # 覆盖已有文件
            str(output_path),
        ]

        logger.info(f"提取音频: {video_path.name} -> {output_path.name}")

        def _run():
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=settings.download_timeout,
            )
            if result.returncode != 0:
                error_msg = result.stderr.decode('utf-8', errors='ignore')
                raise RuntimeError(f"FFmpeg 音频提取失败: {error_msg}")

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _run)

        if not output_path.exists():
            raise FileNotFoundError(f"音频提取完成但文件不存在: {output_path}")

        logger.info(f"音频提取完成: {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")
        return output_path


# 全局单例
audio_extractor = AudioExtractor()
