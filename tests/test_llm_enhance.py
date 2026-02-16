"""
测试 LLM 文案增强功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.llm_enhancer import llm_enhancer


async def main():
    # 读取已识别的文案
    transcript_file = Path("output/transcript.txt")
    if not transcript_file.exists():
        print("❌ 未找到 output/transcript.txt 文件")
        return
    
    raw_text = transcript_file.read_text(encoding='utf-8')
    # 提取正文部分（跳过前面的标题等信息）
    lines = raw_text.split('\n')
    content_start = 0
    for i, line in enumerate(lines):
        if '=' * 20 in line:
            content_start = i + 1
            break
    
    raw_content = '\n'.join(lines[content_start:]).strip()
    
    print(f"📝 原始文案长度: {len(raw_content)} 字")
    print(f"{'='*60}")
    print(f"原始文案前 200 字:\n{raw_content[:200]}...")
    print(f"{'='*60}\n")
    
    print("🤖 开始 LLM 增强...")
    try:
        enhanced_text = await llm_enhancer.enhance(raw_content)
        
        print(f"✅ LLM 增强完成!")
        print(f"📝 增强后文案长度: {len(enhanced_text)} 字")
        print(f"{'='*60}")
        print(f"增强后文案前 200 字:\n{enhanced_text[:200]}...")
        print(f"{'='*60}\n")
        
        # 保存增强后的结果
        output_file = Path("output/transcript_enhanced.txt")
        output_file.write_text(enhanced_text, encoding='utf-8')
        print(f"💾 增强后的文案已保存到: {output_file}")
        
    except Exception as e:
        print(f"❌ LLM 增强失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
