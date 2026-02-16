"""
抖音视频解析与下载服务
支持URL下载和本地文件处理
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, Tuple

import yt_dlp
from yt_dlp.cookies import CookieLoadError

from app.config import settings
from app.models.schemas import VideoInfo
from app.utils.cookie_helper import extract_cookies_to_file
from app.utils.helpers import sanitize_filename

logger = logging.getLogger(__name__)


class DouyinParser:
    """抖音视频解析器"""

    def __init__(self):
        self._base_opts = {
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': settings.request_timeout,
            'retries': 3,
            'nocheckcertificate': True,
            # 模拟浏览器请求头
            'http_headers': {
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/120.0.0.0 Safari/537.36'
                ),
                'Referer': 'https://www.douyin.com/',
            },
        }

    @staticmethod
    def _cookie_error_hint(exc: Exception) -> bool:
        msg = str(exc) or ""
        hints = (
            "Fresh cookies",
            "failed to load cookies",
            "CookieLoadError",
            "Failed to decrypt",
            "DPAPI",
            "Chrome cookie database",
            "cookies database",
        )
        return any(h in msg for h in hints) or isinstance(exc, CookieLoadError)

    def _iter_cookie_opts(self):
        """
        生成一组 cookie 加载策略（按优先级排序）。

        策略调整：优先使用 yt-dlp 原生 cookiesfrombrowser（绕过 rookiepy 的加密问题）
        """
        # 方式 1: 用户手动提供 cookies 文件（最高优先级）
        if settings.ytdlp_cookies_file:
            cookie_path = Path(settings.ytdlp_cookies_file)
            if cookie_path.exists():
                logger.info(f"使用手动指定的 cookies 文件: {cookie_path}")
                yield {"cookiefile": str(cookie_path)}
                return
            else:
                logger.warning(f"指定的 cookies 文件不存在: {cookie_path}")

        # 方式 2: yt-dlp 原生从浏览器读取（推荐，绕过 rookiepy 加密问题）
        # yt-dlp 有自己的解密实现，可能比 rookiepy 更好
        if settings.ytdlp_cookies_from_browser:
            # 尝试多个浏览器，增加成功率
            browsers = [
                settings.ytdlp_cookies_from_browser,
                "edge",
                "chrome", 
                "firefox",
                "chromium",
                "brave",
                "opera",
            ]
            seen = set()
            for browser in browsers:
                browser = (browser or "").strip().lower()
                if not browser or browser in seen:
                    continue
                seen.add(browser)
                logger.debug(f"尝试从 {browser} 读取 cookies")
                yield {"cookiesfrombrowser": (browser,)}

        # 方式 3: rookiepy 导出（作为最后的降级方案）
        # 注意：Chrome v130+ 可能失败
        try:
            cookie_file = extract_cookies_to_file()
            if cookie_file:
                logger.info(f"使用 rookiepy 导出的 cookies: {cookie_file}")
                yield {"cookiefile": cookie_file}
        except Exception as e:
            logger.debug(f"rookiepy 提取失败: {e}")

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
        output_dir.mkdir(parents=True, exist_ok=True

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
