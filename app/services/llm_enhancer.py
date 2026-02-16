"""
大模型文案增强服务
使用 LLM 对 ASR 识别结果进行校正和润色，提升文案准确度
"""

import asyncio
import logging
from typing import Optional

from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)

# ─── 系统提示词 ───
SYSTEM_PROMPT = """你是一个专业的中文文案校对和修正助手。你的任务是对语音识别(ASR)的转录结果进行校正和优化。

## 你需要做的：
1. **纠正同音错字**：ASR 经常产生同音替换错误，请根据上下文语义纠正
2. **修复标点符号**：添加正确的标点符号，使文本可读性更好
3. **修复断句**：合并被错误分割的句子，分割被错误合并的句子
4. **保留原意**：严格保持原文的意思和说话风格，不要改变内容含义
5. **处理口语化表达**：保留合理的口语化表达，但修正明显的语病
6. **处理专业术语**：根据上下文推断并修正可能被错误识别的专业术语

## 你不应该做的：
- 不要添加原文没有的内容
- 不要改变说话人的语气和风格
- 不要过度书面化，保持原有的表达方式
- 不要删除有意义的内容

## 输出要求：
- 直接输出修正后的文案全文
- 不要添加任何解释、注释或说明
- 不要使用 markdown 格式"""


class LLMEnhancer:
    """大模型文案增强器"""

    def __init__(self):
        self._client: Optional[OpenAI] = None

    def _get_client(self) -> OpenAI:
        """获取 OpenAI 客户端"""
        if self._client is None:
            api_key = settings.ark_api_key or settings.llm_api_key
            if not api_key:
                raise ValueError(
                    "LLM API Key 未配置！请在 .env 文件中设置 ARK_API_KEY（或兼容的 LLM_API_KEY）"
                )
            self._client = OpenAI(
                api_key=api_key,
                base_url=settings.llm_api_base,
            )
        return self._client

    @staticmethod
    def _extract_text(response) -> str:
        """从 responses.create 的返回结果中提取文本输出"""
        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()

        output = getattr(response, "output", None)
        if not output and isinstance(response, dict):
            output = response.get("output")

        if not output:
            return ""

        parts = []
        for item in output or []:
            content = getattr(item, "content", None)
            if content is None and isinstance(item, dict):
                content = item.get("content")
            if not content:
                continue

            for c in content:
                c_type = getattr(c, "type", None)
                if c_type is None and isinstance(c, dict):
                    c_type = c.get("type")

                text = getattr(c, "text", None)
                if text is None and isinstance(c, dict):
                    text = c.get("text")

                if c_type in ("output_text", "text") and isinstance(text, str) and text.strip():
                    parts.append(text.strip())

        return "\n".join(parts).strip()

    async def enhance(self, raw_text: str) -> str:
        """
        使用大模型增强文案

        Args:
            raw_text: ASR 原始识别文本

        Returns:
            增强后的文案文本
        """
        if not raw_text or not raw_text.strip():
            return raw_text

        if not settings.llm_enabled:
            logger.info("LLM 增强已禁用，跳过")
            return raw_text

        client = self._get_client()

        user_prompt = f"请对以下语音识别转录文本进行校正和优化：\n\n{raw_text}"

        logger.info(f"开始 LLM 文案增强 (模型: {settings.llm_model})，原文 {len(raw_text)} 字")

        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=settings.llm_temperature,
            )

            enhanced_text = response.choices[0].message.content.strip()
            if not enhanced_text:
                enhanced_text = raw_text
            logger.info(f"LLM 增强完成，结果 {len(enhanced_text)} 字")
            return enhanced_text

        except Exception as e:
            logger.error(f"LLM 增强失败: {e}")
            # 失败时返回原文，保证流程不中断
            return raw_text


# 全局单例
llm_enhancer = LLMEnhancer()
