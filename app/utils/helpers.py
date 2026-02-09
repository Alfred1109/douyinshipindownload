"""
工具函数
"""

import re
import uuid
from pathlib import Path


def generate_task_id() -> str:
    """生成唯一任务ID"""
    return uuid.uuid4().hex[:12]


def generate_batch_id() -> str:
    """生成批次ID"""
    return f"batch_{uuid.uuid4().hex[:8]}"


def sanitize_filename(name: str) -> str:
    """清理文件名，去除非法字符"""
    if not name:
        return "unnamed"
    
    # 移除或替换非法字符
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'\s+', '_', name)
    
    # 确保文件名是有效的ASCII字符或正确编码的Unicode
    try:
        # 尝试编码为utf-8并解码，确保字符串有效
        name.encode('utf-8').decode('utf-8')
    except UnicodeError:
        # 如果编码失败，只保留ASCII字符
        name = re.sub(r'[^\x00-\x7F]+', '_', name)
    
    # 移除首尾空白和点号
    name = name.strip(' .')
    
    # 确保不是保留名称
    reserved = ['CON', 'PRN', 'AUX', 'NUL'] + [f'COM{i}' for i in range(1, 10)] + [f'LPT{i}' for i in range(1, 10)]
    if name.upper() in reserved:
        name = f"_{name}"
    
    return name[:100] if name else "unnamed"  # 限制长度


def is_douyin_url(url: str) -> bool:
    """检查是否为抖音链接"""
    patterns = [
        r'https?://v\.douyin\.com/',
        r'https?://www\.douyin\.com/video/',
        r'https?://www\.iesdouyin\.com/',
        r'https?://www\.tiktok\.com/',
    ]
    return any(re.match(p, url.strip()) for p in patterns)


def format_time(seconds: float) -> str:
    """格式化时间为 HH:MM:SS.mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


def clean_temp_files(*paths: Path):
    """清理临时文件"""
    for p in paths:
        try:
            if p and p.exists():
                p.unlink()
        except Exception:
            pass
