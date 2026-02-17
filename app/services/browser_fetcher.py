"""
浏览器自动化获取器 - 使用 Playwright 模拟真实浏览器
完全模拟人的行为，自动获取视频/音频资源
"""
import asyncio
import logging
import re
from pathlib import Path
from typing import Optional, Tuple
import json

from app.config import settings
from app.models.schemas import VideoInfo

logger = logging.getLogger(__name__)


class BrowserFetcher:
    """
    浏览器自动化获取器
    
    使用 Playwright 模拟真实浏览器：
    1. 自动加载 Cookie
    2. 模拟人的浏览行为
    3. 拦截网络请求获取资源 URL
    4. 直接下载音频/视频
    """
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
    
    async def _ensure_browser(self):
        """确保浏览器已启动"""
        if self.browser:
            return
        
        try:
            # Windows 平台修复：确保使用正确的事件循环
            import sys
            if sys.platform == 'win32':
                # 获取当前事件循环
                try:
                    loop = asyncio.get_running_loop()
                    # 如果当前循环不是 ProactorEventLoop，我们需要记录警告
                    if not isinstance(loop, asyncio.ProactorEventLoop):
                        logger.warning("当前事件循环不是 ProactorEventLoop，Playwright 可能无法正常工作")
                        # 设置策略以便将来的循环使用正确的类型
                        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                except RuntimeError:
                    # 没有运行中的循环，设置策略
                    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            
            # 启动浏览器（使用 chromium，最接近 Chrome）
            self.browser = await self.playwright.chromium.launch(
                headless=True,  # 无头模式
                args=[
                    '--disable-blink-features=AutomationControlled',  # 隐藏自动化特征
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                ]
            )
            
            # 创建浏览器上下文
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='zh-CN',
            )
            
            logger.info("✅ 浏览器启动成功")
            
        except ImportError:
            logger.error("❌ Playwright 未安装，请运行: pip install playwright && playwright install chromium")
            raise
        except Exception as e:
            logger.error(f"❌ 浏览器启动失败: {e}")
            raise
    
    async def fetch_video_info(self, url: str) -> Tuple[Optional[str], Optional[VideoInfo]]:
        """
        获取视频信息和资源 URL
        
        Returns:
            (video_url, video_info) 或 (None, None)
        """
        await self._ensure_browser()
        
        page = await self.context.new_page()
        video_url = None
        video_info = None
        
        try:
            # 拦截网络请求，捕获视频/音频 URL
            captured_urls = []
            
            async def handle_response(response):
                url = response.url
                content_type = response.headers.get('content-type', '')
                
                # 捕获视频/音频资源
                if any(ext in url for ext in ['.mp4', '.m4a', '.mp3']) or \
                   any(t in content_type for t in ['video/', 'audio/']):
                    captured_urls.append({
                        'url': url,
                        'type': content_type,
                        'size': response.headers.get('content-length', 0),
                    })
                    logger.info(f"📦 捕获资源: {url[:100]}...")
            
            page.on('response', handle_response)
            
            logger.info(f"🌐 正在访问: {url}")
            
            # 访问页面（使用更宽松的等待策略）
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            except Exception as e:
                logger.warning(f"页面加载超时，尝试继续: {e}")
                # 即使超时也继续，因为可能已经加载了部分内容
            
            # 等待页面加载和 JavaScript 执行
            await page.wait_for_timeout(5000)
            
            # 尝试提取视频信息
            try:
                # 方法 1: 从页面标题提取
                title = await page.title()
                
                # 方法 2: 从页面元素提取
                try:
                    desc_element = await page.query_selector('[data-e2e="video-desc"]')
                    if desc_element:
                        title = await desc_element.inner_text()
                except:
                    pass
                
                # 方法 3: 从 meta 标签提取
                try:
                    og_title = await page.get_attribute('meta[property="og:title"]', 'content')
                    if og_title:
                        title = og_title
                except:
                    pass
                
                # 提取作者
                author = "未知作者"
                try:
                    author_element = await page.query_selector('[data-e2e="video-author-name"]')
                    if author_element:
                        author = await author_element.inner_text()
                except:
                    pass
                
                # 提取视频 ID
                video_id = re.search(r'/video/(\d+)', url)
                video_id = video_id.group(1) if video_id else 'unknown'
                
                video_info = VideoInfo(
                    video_id=video_id,
                    title=title or f"抖音视频 {video_id}",
                    author=author,
                    duration=0,  # 需要从视频元数据获取
                    url=url,
                    cover_url="",
                )
                
                logger.info(f"✅ 视频信息: {video_info.title} - {video_info.author}")
                
            except Exception as e:
                logger.warning(f"⚠️  提取视频信息失败: {e}")
            
            # 选择最佳资源 URL
            if captured_urls:
                # 优先选择 mp4 视频
                video_urls = [u for u in captured_urls if '.mp4' in u['url'] or 'video/' in u['type']]
                if video_urls:
                    # 选择最大的
                    video_urls.sort(key=lambda x: int(x['size']) if x['size'] else 0, reverse=True)
                    video_url = video_urls[0]['url']
                    logger.info(f"✅ 选择视频 URL: {video_url[:100]}...")
                else:
                    # 没有视频，选择音频
                    audio_urls = [u for u in captured_urls if '.m4a' in u['url'] or '.mp3' in u['url'] or 'audio/' in u['type']]
                    if audio_urls:
                        video_url = audio_urls[0]['url']
                        logger.info(f"✅ 选择音频 URL: {video_url[:100]}...")
            
            if not video_url:
                logger.error("❌ 未捕获到视频/音频资源")
                
                # 尝试从页面 JavaScript 中提取
                try:
                    video_url = await self._extract_from_page_script(page)
                except Exception as e:
                    logger.error(f"从脚本提取失败: {e}")
            
            return video_url, video_info
            
        except Exception as e:
            logger.error(f"❌ 获取失败: {e}", exc_info=True)
            return None, None
        finally:
            await page.close()
    
    async def _extract_from_page_script(self, page) -> Optional[str]:
        """从页面 JavaScript 中提取视频 URL"""
        try:
            # 执行 JavaScript 获取视频元素
            video_src = await page.evaluate('''() => {
                // 尝试从 video 标签获取
                const video = document.querySelector('video');
                if (video && video.src) {
                    return video.src;
                }
                
                // 尝试从 source 标签获取
                const source = document.querySelector('video source');
                if (source && source.src) {
                    return source.src;
                }
                
                // 尝试从全局变量获取
                if (window.__INITIAL_STATE__) {
                    try {
                        const state = window.__INITIAL_STATE__;
                        // 根据实际结构调整路径
                        if (state.video && state.video.playAddr) {
                            return state.video.playAddr;
                        }
                    } catch (e) {}
                }
                
                return null;
            }''')
            
            if video_src:
                logger.info(f"✅ 从页面脚本提取到 URL: {video_src[:100]}...")
                return video_src
            
        except Exception as e:
            logger.debug(f"从脚本提取失败: {e}")
        
        return None
    
    async def download_resource(self, url: str, output_path: Path) -> bool:
        """下载资源"""
        try:
            await self._ensure_browser()
            
            page = await self.context.new_page()
            
            logger.info(f"📥 开始下载: {url[:100]}...")
            
            # 使用浏览器上下文下载，携带完整的请求头和 Cookie
            response = await page.request.get(url, headers={
                'Referer': 'https://www.douyin.com/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }, timeout=120000)  # 增加到 120 秒
            
            if response.status != 200:
                logger.error(f"❌ 下载失败: HTTP {response.status}")
                
                # 尝试备用方案：直接在页面中下载
                logger.info("🔄 尝试备用下载方案...")
                try:
                    await page.goto(url)
                    await page.wait_for_timeout(3000)
                    
                    # 获取页面内容
                    content = await page.content()
                    if len(content) > 1000:  # 简单判断是否是视频内容
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(output_path, 'wb') as f:
                            f.write(content.encode())
                        logger.info(f"✅ 备用方案下载完成")
                        await page.close()
                        return True
                except Exception as e2:
                    logger.error(f"备用方案也失败: {e2}")
                
                await page.close()
                return False
            
            # 保存文件
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(await response.body())
            
            file_size = output_path.stat().st_size
            logger.info(f"✅ 下载完成: {output_path} ({file_size / 1024 / 1024:.2f} MB)")
            
            await page.close()
            
            # 检查文件大小是否合理
            if file_size < 1024:  # 小于 1KB 可能是错误页面
                logger.warning("⚠️  下载的文件太小，可能不是有效的视频")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 下载失败: {e}")
            return False
    
    async def fetch_and_download(self, url: str) -> Tuple[Optional[Path], Optional[VideoInfo]]:
        """
        完整流程: 获取信息并下载视频
        
        Returns:
            (video_path, video_info) 或 (None, None)
        """
        # 1. 获取视频 URL 和信息
        video_url, video_info = await self.fetch_video_info(url)
        
        if not video_url:
            logger.error("❌ 无法获取视频 URL")
            return None, video_info
        
        if not video_info:
            # 创建基本信息
            video_id = re.search(r'/video/(\d+)', url)
            video_id = video_id.group(1) if video_id else 'unknown'
            video_info = VideoInfo(
                video_id=video_id,
                title=f"抖音视频 {video_id}",
                author="未知作者",
                duration=0,
                url=url,
                cover_url="",
            )
        
        # 2. 下载视频
        output_path = settings.temp_dir / f"{video_info.video_id}.mp4"
        success = await self.download_resource(video_url, output_path)
        
        if not success:
            return None, video_info
        
        return output_path, video_info
    
    async def close(self):
        """关闭浏览器"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("🔒 浏览器已关闭")


# 全局单例
browser_fetcher = BrowserFetcher()
