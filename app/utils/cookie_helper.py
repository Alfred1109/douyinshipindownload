"""
Cookie 提取工具
从浏览器中安全提取 cookies，支持多浏览器自动降级
"""

import logging
import time
from http.cookiejar import Cookie, MozillaCookieJar
from pathlib import Path

from app.config import BASE_DIR, settings

logger = logging.getLogger(__name__)

COOKIE_FILE = BASE_DIR / "temp" / "cookies.txt"


def _get_browser_funcs() -> dict:
    """获取所有支持的浏览器提取函数"""
    import rookiepy
    return {
        "chrome": rookiepy.chrome,
        "edge": rookiepy.edge,
        "firefox": rookiepy.firefox,
        "chromium": rookiepy.chromium,
        "brave": rookiepy.brave,
        "opera": rookiepy.opera,
        "vivaldi": rookiepy.vivaldi,
    }


def _try_extract(browser_name: str, func) -> list:
    """尝试从指定浏览器提取 cookies"""
    try:
        cookies = func(domains=[".douyin.com"])
        if cookies:
            logger.info(f"✅ 从 {browser_name} 成功提取 {len(cookies)} 个 cookies")
            return cookies
        else:
            logger.debug(f"{browser_name} 中无抖音 cookies")
    except Exception as e:
        logger.debug(f"{browser_name} 提取失败: {e}")
    return []


def _save_cookies(cookies: list) -> str:
    """将 cookies 列表保存为 Netscape 格式文件"""
    COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)
    jar = MozillaCookieJar(str(COOKIE_FILE))

    for c in cookies:
        expires = c.get("expires", 0)
        if isinstance(expires, str):
            try:
                expires = int(expires)
            except ValueError:
                expires = int(time.time()) + 86400 * 365

        cookie = Cookie(
            version=0,
            name=c["name"],
            value=c["value"],
            port=None,
            port_specified=False,
            domain=c.get("domain", ".douyin.com"),
            domain_specified=True,
            domain_initial_dot=c.get("domain", ".douyin.com").startswith("."),
            path=c.get("path", "/"),
            path_specified=True,
            secure=c.get("secure", False),
            expires=expires or int(time.time()) + 86400 * 365,
            discard=False,
            comment=None,
            comment_url=None,
            rest={"HttpOnly": str(c.get("httpOnly", False))},
        )
        jar.set_cookie(cookie)

    jar.save(ignore_discard=True, ignore_expires=True)
    logger.info(f"cookies 已保存到 {COOKIE_FILE}")
    return str(COOKIE_FILE)


def extract_cookies_to_file() -> str:
    """
    从浏览器提取抖音 cookies 并保存为文件

    策略: 优先使用配置的浏览器，失败后自动降级尝试其他浏览器
    降级顺序: 配置的浏览器 → edge → chrome → firefox → 其他

    Returns:
        cookies.txt 文件路径，提取失败返回空字符串
    """
    configured = settings.ytdlp_cookies_from_browser
    if not configured:
        return ""

    try:
        browser_funcs = _get_browser_funcs()
    except ImportError:
        logger.error("rookiepy 未安装，请执行: pip install rookiepy")
        return ""

    # 构建尝试顺序：配置的浏览器优先，然后是降级列表
    fallback_order = ["edge", "chrome", "firefox", "chromium", "brave", "opera", "vivaldi"]
    try_order = [configured.lower()]
    for b in fallback_order:
        if b not in try_order:
            try_order.append(b)

    # 依次尝试每个浏览器
    for browser_name in try_order:
        func = browser_funcs.get(browser_name)
        if not func:
            continue

        cookies = _try_extract(browser_name, func)
        if cookies:
            if browser_name != configured.lower():
                logger.info(f"💡 {configured} 提取失败，已自动降级使用 {browser_name} 的 cookies")
            return _save_cookies(cookies)

    logger.error(
        "❌ 所有浏览器均无法提取抖音 cookies！\n"
        "   解决方案：\n"
        "   1. 用 Edge 浏览器打开 https://www.douyin.com 并登录\n"
        "   2. 或用浏览器扩展导出 cookies.txt 文件，放到项目目录并在 .env 中设置 YTDLP_COOKIES_FILE=cookies.txt"
    )
    return ""
