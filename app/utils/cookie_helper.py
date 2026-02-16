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
COOKIE_TTL_SECONDS = 60


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
        # 说明：
        # rookiepy 的 domains 过滤在部分环境下会漏掉抖音关键字段（如 s_v_web_id）。
        # 这里改为先提取全量 cookies，再做域名过滤。由于只写入 douyin/iesdouyin 的少量 cookies，
        # 配合 TTL 缓存，整体开销可控。
        raw_cookies = func()
        cookies = []
        for c in raw_cookies or []:
            domain = str(c.get("domain", "")).lower()
            if "douyin.com" in domain or "iesdouyin.com" in domain:
                cookies.append(c)

        if cookies:
            logger.info(f"✅ 从 {browser_name} 成功提取 {len(cookies)} 个抖音 cookies")
            return cookies

        logger.debug(f"{browser_name} 中无抖音 cookies")
    except RuntimeError as e:
        error_msg = str(e)
        if "appbound encryption" in error_msg or "running as admin" in error_msg:
            logger.warning(
                f"⚠️  {browser_name} 需要管理员权限（Chrome v130+ 加密限制）\n"
                f"   解决方案:\n"
                f"   1. 以管理员身份运行程序\n"
                f"   2. 或使用浏览器扩展手动导出 cookies.txt\n"
                f"   3. 或使用文件上传功能绕过下载"
            )
        else:
            logger.debug(f"{browser_name} 提取失败: {e}")
    except Exception as e:
        logger.debug(f"{browser_name} 提取失败: {e}")
    return []


def _score_cookies(cookies: list) -> int:
    """
    给 cookies 集合打分，用于从多个浏览器候选中选择“最可能可用”的一份。

    经验规则：
    - 抖音/头条系常见关键字段存在时更可能绕过风控
    - cookies 越多通常越“新”/越完整
    """
    names = set()
    for c in cookies or []:
        name = c.get("name")
        if isinstance(name, str) and name:
            names.add(name)

    score = len(cookies or [])

    # 加权：更偏向能通过风控的关键字段（不一定需要登录）
    key_weights = {
        # 登录态/强身份字段（若存在，强烈加分）
        "sessionid": 120,
        "sessionid_ss": 120,
        "sid_tt": 90,
        "uid_tt": 90,
        "passport_auth_status": 60,
        # 常见风控/反爬字段（通常需要“新”）
        "msToken": 60,
        "ms_token": 60,
        "s_v_web_id": 40,
        "__ac_signature": 30,
        "__ac_nonce": 20,
        "ttwid": 20,
        "odin_tt": 20,
        "passport_csrf_token": 15,
        "passport_csrf_token_default": 10,
    }

    for k, w in key_weights.items():
        if k in names:
            score += w

    return score


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

    # 关键字段检查（只打日志，不输出具体值）
    names = {c.get("name") for c in cookies or [] if isinstance(c, dict)}
    if "s_v_web_id" not in names:
        logger.warning("cookies 中未包含 s_v_web_id，yt-dlp 可能仍会提示 Fresh cookies")

    return str(COOKIE_FILE)


def extract_cookies_to_file() -> str:
    """
    从浏览器提取抖音 cookies 并保存为文件

    策略: 优先使用配置的浏览器，但会综合比较多个候选，选择更“完整”的 cookies

    Returns:
        cookies.txt 文件路径，提取失败返回空字符串
    """
    configured = settings.ytdlp_cookies_from_browser
    if not configured:
        return ""

    # 小 TTL 缓存：同一请求内 extract_info + download 两次调用时不重复解密
    try:
        if COOKIE_FILE.exists():
            age = time.time() - COOKIE_FILE.stat().st_mtime
            if age >= 0 and age < COOKIE_TTL_SECONDS:
                return str(COOKIE_FILE)
    except Exception:
        pass

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

    best = None  # (score, browser_name, cookies)

    # 依次尝试每个浏览器，选“最优”候选
    for browser_name in try_order:
        func = browser_funcs.get(browser_name)
        if not func:
            continue

        cookies = _try_extract(browser_name, func)
        if cookies:
            score = _score_cookies(cookies)
            if best is None or score > best[0]:
                best = (score, browser_name, cookies)

    if best:
        _, selected_browser, cookies = best
        if selected_browser != configured.lower():
            logger.info(f"💡 已自动选择 {selected_browser} 的 cookies（配置为 {configured}）")
        return _save_cookies(cookies)

    logger.error(
        "❌ 所有浏览器均无法提取抖音 cookies！\n"
        "   可能原因：\n"
        "   1. 浏览器未访问过抖音或未登录\n"
        "   2. Chrome/Edge v130+ 需要管理员权限（appbound encryption）\n"
        "   \n"
        "   解决方案（3选1）：\n"
        "   【方案1 - 最简单】使用文件上传功能\n"
        "      访问 http://localhost:8000 上传本地视频文件\n"
        "   \n"
        "   【方案2 - 管理员权限】\n"
        "      以管理员身份运行: python fix_chrome_cookies.py\n"
        "   \n"
        "   【方案3 - 手动导出】\n"
        "      1. 安装浏览器扩展 'Get cookies.txt LOCALLY'\n"
        "      2. 访问 https://www.douyin.com 并登录\n"
        "      3. 导出 cookies.txt 到项目根目录\n"
        "      4. 在 .env 中设置: YTDLP_COOKIES_FILE=cookies.txt"
    )
    return ""
