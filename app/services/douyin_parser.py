"""
抖音视频解析与下载服务
支持URL下载和本地文件处理
"""

import asyncio
import logging
import re
from pathlib import Path
from typing import Optional, Tuple

from app.config import settings
from app.models.schemas import VideoInfo

logger = logging.getLogger(__name__)


class DouyinParser:
    """抖音视频解析器 - 使用 Playwright 浏览器自动化"""

    def __init__(self):
        pass

    async def extract_info(self, url: str) -> VideoInfo:
        """
        提取视频信息（使用浏览器自动化）
        """
        try:
            from app.services.browser_fetcher import browser_fetcher
            
            logger.info(f"🔍 提取视频信息: {url}")
            
            # 使用浏览器获取信息
            _, video_info = await browser_fetcher.fetch_video_info(url)
            
            if video_info:
                return video_info
            
            # 如果失败，返回基本信息
            video_id = self.extract_video_id(url)
            return VideoInfo(
                video_id=video_id or "unknown",
                title=f"抖音视频 {video_id}" if video_id else "未知视频",
                author="未知作者",
                duration=0,
                url=url,
                cover_url="",
            )
            
        except ImportError:
            logger.warning("⚠️  Playwright 未安装，返回基本信息")
            video_id = self.extract_video_id(url)
            return VideoInfo(
                video_id=video_id or "unknown",
                title=f"抖音视频 {video_id}" if video_id else "未知视频",
                author="未知作者",
                duration=0,
                url=url,
                cover_url="",
            )
        except Exception as e:
            logger.warning(f"⚠️  提取视频信息失败: {e}")
            video_id = self.extract_video_id(url)
            return VideoInfo(
                video_id=video_id or "unknown",
                title=f"抖音视频 {video_id}" if video_id else "未知视频",
                author="未知作者",
                duration=0,
                url=url,
                cover_url="",
            )
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """从 URL 提取视频 ID"""
        patterns = [
            r'/video/(\d+)',
            r'modal_id=(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    async def download_video(self, url: str, output_dir: Optional[Path] = None) -> Tuple[Path, VideoInfo]:
        """
        使用浏览器自动化下载视频
        
        完全模拟真实浏览器行为，绕过所有反爬限制
        """
        output_dir = output_dir or settings.temp_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"🌐 使用浏览器自动化下载: {url}")
        
        try:
            from app.services.browser_fetcher import browser_fetcher
            
            # 使用浏览器自动化获取并下载
            video_path, video_info = await browser_fetcher.fetch_and_download(url)
            
            if not video_path or not video_path.exists():
                raise RuntimeError("浏览器自动化下载失败")
            
            logger.info(f"✅ 下载成功: {video_path}")
            return video_path, video_info
            
        except ImportError:
            logger.error("❌ Playwright 未安装")
            logger.error("请运行以下命令安装:")
            logger.error("  pip install playwright")
            logger.error("  playwright install chromium")
            raise RuntimeError(
                "Playwright 未安装。请运行: pip install playwright && playwright install chromium"
            )
        except Exception as e:
            logger.error(f"❌ 下载失败: {e}")
            raise


# 全局单例
douyin_parser = DouyinParser()
