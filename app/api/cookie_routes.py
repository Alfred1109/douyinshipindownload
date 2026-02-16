"""
Cookie 管理路由 - 让用户通过 Web 界面管理 cookies
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cookies", tags=["Cookie 管理"])


class CookieUploadRequest(BaseModel):
    """Cookie 上传请求"""
    cookies_text: str
    format: str = "netscape"  # netscape 或 json


class CookieStatusResponse(BaseModel):
    """Cookie 状态响应"""
    has_cookies: bool
    file_size: Optional[int] = None
    cookie_count: Optional[int] = None
    key_fields: dict = {}


@router.post("/upload", summary="上传 Cookies 文本")
async def upload_cookies(request: CookieUploadRequest):
    """
    通过 Web 界面上传 cookies
    
    支持两种格式:
    1. Netscape 格式 (浏览器扩展导出的标准格式)
    2. JSON 格式 (开发者工具复制的格式)
    """
    try:
        cookie_file = settings.temp_dir / "cookies.txt"
        cookie_file.parent.mkdir(parents=True, exist_ok=True)
        
        if request.format == "netscape":
            # 直接保存 Netscape 格式
            cookie_file.write_text(request.cookies_text, encoding='utf-8')
        else:
            # TODO: 支持 JSON 格式转换
            raise HTTPException(status_code=400, detail="暂不支持 JSON 格式")
        
        # 验证 cookies
        lines = [l for l in request.cookies_text.split('\n') if l.strip() and not l.startswith('#')]
        
        logger.info(f"Cookies 已上传: {len(lines)} 行")
        
        return {
            "success": True,
            "message": f"Cookies 已保存，共 {len(lines)} 条",
            "file_path": str(cookie_file),
        }
        
    except Exception as e:
        logger.error(f"上传 cookies 失败: {e}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/status", response_model=CookieStatusResponse, summary="查询 Cookies 状态")
async def get_cookie_status():
    """查询当前 cookies 配置状态"""
    cookie_file = settings.temp_dir / "cookies.txt"
    
    if not cookie_file.exists():
        return CookieStatusResponse(has_cookies=False)
    
    try:
        content = cookie_file.read_text(encoding='utf-8')
        lines = [l for l in content.split('\n') if l.strip() and not l.startswith('#')]
        
        # 提取 cookie 名称
        cookie_names = set()
        for line in lines:
            parts = line.strip().split('\t')
            if len(parts) >= 6:
                cookie_names.add(parts[5])
        
        # 检查关键字段
        key_fields = {
            "sessionid": "sessionid" in cookie_names,
            "s_v_web_id": "s_v_web_id" in cookie_names,
            "msToken": "msToken" in cookie_names,
            "ttwid": "ttwid" in cookie_names,
        }
        
        return CookieStatusResponse(
            has_cookies=True,
            file_size=cookie_file.stat().st_size,
            cookie_count=len(lines),
            key_fields=key_fields,
        )
        
    except Exception as e:
        logger.error(f"读取 cookies 失败: {e}")
        return CookieStatusResponse(has_cookies=False)


@router.delete("/clear", summary="清除 Cookies")
async def clear_cookies():
    """清除当前保存的 cookies"""
    try:
        cookie_file = settings.temp_dir / "cookies.txt"
        if cookie_file.exists():
            cookie_file.unlink()
            logger.info("Cookies 已清除")
            return {"success": True, "message": "Cookies 已清除"}
        else:
            return {"success": True, "message": "没有需要清除的 cookies"}
    except Exception as e:
        logger.error(f"清除 cookies 失败: {e}")
        raise HTTPException(status_code=500, detail=f"清除失败: {str(e)}")


@router.get("/guide", summary="获取 Cookie 导出指南")
async def get_cookie_guide():
    """返回详细的 cookie 导出指南"""
    return {
        "methods": [
            {
                "name": "浏览器扩展（推荐）",
                "difficulty": "简单",
                "steps": [
                    "安装 Chrome 扩展: Get cookies.txt LOCALLY",
                    "访问 https://www.douyin.com 并登录",
                    "点击扩展图标",
                    "复制导出的文本",
                    "粘贴到本页面的上传框",
                ],
                "extension_url": "https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc"
            },
            {
                "name": "开发者工具",
                "difficulty": "中等",
                "steps": [
                    "访问 https://www.douyin.com 并登录",
                    "按 F12 打开开发者工具",
                    "切换到 Application 标签",
                    "左侧选择 Cookies → https://www.douyin.com",
                    "右键 → Export → 保存为 cookies.txt",
                    "上传文件到本页面",
                ],
            },
            {
                "name": "EditThisCookie 扩展",
                "difficulty": "简单",
                "steps": [
                    "安装 EditThisCookie 扩展",
                    "访问 https://www.douyin.com 并登录",
                    "点击扩展图标",
                    "点击导出按钮",
                    "选择 Netscape 格式",
                    "粘贴到本页面",
                ],
            }
        ],
        "important_cookies": [
            {"name": "sessionid", "description": "登录态（必需）"},
            {"name": "s_v_web_id", "description": "设备指纹（重要）"},
            {"name": "msToken", "description": "反爬字段"},
            {"name": "ttwid", "description": "设备ID"},
        ],
        "tips": [
            "确保在登录状态下导出 cookies",
            "Cookies 通常 7-30 天过期，需定期更新",
            "不要分享你的 cookies 给他人（包含登录信息）",
        ]
    }
