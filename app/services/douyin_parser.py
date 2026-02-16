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

        优先使用 yt-dlp 原生 cookiesfrombrowser（通常更完整、支持多 profile 自动挑最新 DB），
        失败时再回退到 rookiepy 导出的 cookiefile。
        """
        # 方式 1: 用户手动提供 cookies 文件
        if settings.ytdlp_cookies_file:
            cookie_path = Path(settings.ytdlp_cookies_file)
            if cookie_path.exists():
                yield {"cookiefile": str(cookie_path)}
            else:
                logger.warning(f"指定的 cookies 文件不存在: {cookie_path}")
            return

        # 方式 2: rookiepy 导出 cookies 到文件（支持 Chromium v20/v130+ 的 appbound 加密）
        cookie_file = extract_cookies_to_file()
        if cookie_file:
            yield {"cookiefile": cookie_file}

        # 方式 3: yt-dlp 原生从浏览器读取 cookies（部分 Chromium 新版本加密可能不支持，作为降级尝试）
        if settings.ytdlp_cookies_from_browser:
            candidates = [
                settings.ytdlp_cookies_from_browser,
                "edge",
                "chrome",
                "firefox",
            ]
            seen = set()
            for b in candidates:
                b = (b or "").strip().lower()
                if not b or b in seen:
                    continue
                seen.add(b)
                yield {"cookiesfrombrowser": (b,)}

    async def extract_info(self, url: str) -> VideoInfo:
        """
        提取视频信息（不下载）
        """
        try:
            def _extract():
                last_exc = None
                for cookie_opts in self._iter_cookie_opts():
                    opts = {
                        **self._base_opts,
                        **cookie_opts,
                        'skip_download': True,
                    }
                    try:
                        with yt_dlp.YoutubeDL(opts) as ydl:
                            return ydl.extract_info(url, download=False)
                    except Exception as e:
                        last_exc = e
                        if self._cookie_error_hint(e):
                            continue
                        break
                if last_exc:
                    raise last_exc
                raise RuntimeError("yt-dlp 提取失败：未知错误")

            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, _extract)

            return VideoInfo(
                video_id=str(info.get('id', '')),
                title=info.get('title', '未知标题'),
                author=info.get('uploader', info.get('creator', '未知作者')),
                duration=float(info.get('duration', 0)),
                url=info.get('webpage_url', url),
                cover_url=info.get('thumbnail', ''),
            )
        except Exception as e:
            logger.warning(f"yt-dlp 提取失败: {e}")
            # 返回基本信息，让用户知道需要手动上传
            return VideoInfo(
                video_id="unknown",
                title="无法自动提取，请使用文件上传功能",
                author="未知作者",
                duration=0,
                url=url,
                cover_url="",
            )

    async def download_video(self, url: str, output_dir: Optional[Path] = None) -> Tuple[Path, VideoInfo]:
        """
        下载视频并返回文件路径与视频信息
        """
        output_dir = output_dir or settings.temp_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        # 先提取信息获取文件名
        video_info = await self.extract_info(url)
        safe_name = sanitize_filename(video_info.title) or video_info.video_id
        output_path = output_dir / f"{safe_name}.mp4"

        def _download():
            last_exc = None
            for cookie_opts in self._iter_cookie_opts():
                opts = {
                    **self._base_opts,
                    **cookie_opts,
                    'outtmpl': str(output_path),
                    'format': 'best[ext=mp4]/best',
                    'merge_output_format': 'mp4',
                    'socket_timeout': settings.download_timeout,
                }
                try:
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        ydl.download([url])
                    return
                except Exception as e:
                    last_exc = e
                    if self._cookie_error_hint(e):
                        continue
                    break
            if last_exc:
                raise last_exc
            raise RuntimeError("视频下载失败：未知错误")

        logger.info(f"开始下载视频: {video_info.title}")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _download)

        # yt-dlp 可能会自动添加扩展名
        if not output_path.exists():
            # 尝试查找实际输出文件
            candidates = list(output_dir.glob(f"{safe_name}.*"))
            if candidates:
                output_path = candidates[0]
            else:
                raise FileNotFoundError(f"下载完成但未找到输出文件: {output_path}")

        logger.info(f"视频下载完成: {output_path}")
        return output_path, video_info


# 全局单例
douyin_parser = DouyinParser()
