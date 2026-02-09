"""
应用配置管理模块
使用 pydantic-settings 管理所有配置，支持 .env 文件和环境变量
"""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """应用全局配置"""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ─── 基础配置 ───
    app_name: str = "抖音短视频文案提取工具"
    debug: bool = False
    temp_dir: Path = BASE_DIR / "temp"
    output_dir: Path = BASE_DIR / "output"

    # ─── ASR 语音识别配置 ───
    # 模式: "local" 使用本地 faster-whisper, "api" 使用 OpenAI Whisper API
    asr_mode: str = "local"
    # 本地 Whisper 模型大小: tiny, base, small, medium, large-v3
    whisper_model_size: str = "medium"
    # Whisper 设备: cpu / cuda / auto
    whisper_device: str = "auto"
    # Whisper 计算精度: float16 / int8 / float32
    whisper_compute_type: str = "float16"
    # 识别语言 (留空自动检测)
    whisper_language: str = "zh"

    # ─── OpenAI Whisper API 配置 (asr_mode=api 时使用) ───
    openai_api_key: Optional[str] = None
    openai_api_base: str = "https://api.openai.com/v1"
    openai_whisper_model: str = "whisper-1"

    # ─── LLM 大模型配置 (用于文案增强) ───
    llm_enabled: bool = True
    llm_api_key: Optional[str] = None
    ark_api_key: Optional[str] = None
    llm_api_base: str = "https://ark.cn-beijing.volces.com/api/v3"
    llm_model: str = "deepseek-v3-2-251201"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 4096

    # ─── 批量处理配置 ───
    max_concurrent_tasks: int = 3
    download_timeout: int = 120
    request_timeout: int = 30

    # ─── yt-dlp 配置 ───
    ytdlp_cookies_file: Optional[str] = None
    # 从浏览器自动提取 cookies: chrome / edge / firefox / 留空不使用
    ytdlp_cookies_from_browser: str = "chrome"

    def ensure_dirs(self):
        """确保必要目录存在"""
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)


# 全局单例
settings = Settings()
settings.ensure_dirs()
