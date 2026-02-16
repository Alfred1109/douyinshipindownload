"""
从已下载的视频文件提取内容
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def main():
    # 使用之前下载的视频文件
    video_file = Path("temp/test_7605511073625656611.mp4")
    
    if not video_file.exists():
        print(f"❌ 文件不存在: {video_file}")
        return
    
    print("="*60)
    print("从视频文件提取内容")
    print("="*60)
    print(f"\n视频文件: {video_file}")
    print(f"文件大小: {video_file.stat().st_size / 1024 / 1024:.2f} MB\n")
    
    try:
        from app.services.audio_extractor import audio_extractor
        from app.services.transcriber import transcriber_service
        from app.services.llm_enhancer import llm_enhancer
        from app.config import settings
        
        # 步骤 1: 提取音频
        print("🎵 步骤 1: 提取音频...")
        audio_path = await audio_extractor.extract(video_file)
        print(f"   ✅ 音频提取完成: {audio_path}")
        
        # 步骤 2: 语音识别
        print("\n🎤 步骤 2: 语音识别...")
        transcript = await transcriber_service.transcribe(audio_path)
        print(f"   ✅ 识别完成")
        
        # 步骤 3: LLM 增强（如果启用）
        if settings.llm_enabled and (settings.ark_api_key or settings.llm_api_key):
            print("\n🤖 步骤 3: LLM 文案增强...")
            enhanced_text = await llm_enhancer.enhance(transcript.raw_text)
            transcript.enhanced_text = enhanced_text
            print(f"   ✅ 增强完成")
        else:
            print("\n⚠️  LLM 未启用，跳过文案增强")
            transcript.enhanced_text = transcript.raw_text
        
        # 显示结果
        print("\n" + "="*60)
        print("✅ 提取完成！")
        print("="*60)
        print(f"\n原始文案:")
        print("-"*60)
        print(transcript.raw_text)
        
        if transcript.enhanced_text and transcript.enhanced_text != transcript.raw_text:
            print(f"\n优化后文案:")
            print("-"*60)
            print(transcript.enhanced_text)
        
        print("\n" + "="*60)
        
        # 清理临时音频文件
        if audio_path.exists():
            audio_path.unlink()
            print(f"🗑️  已清理临时文件: {audio_path}")
        
    except Exception as e:
        print(f"\n❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
