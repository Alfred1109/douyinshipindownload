"""
快速提取 - 只做音频提取和语音识别，跳过 LLM
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def main():
    video_file = Path("temp/test_7605511073625656611.mp4")
    
    if not video_file.exists():
        print(f"❌ 文件不存在: {video_file}")
        return
    
    print("="*60)
    print("快速提取视频文案")
    print("="*60)
    print(f"\n视频文件: {video_file}")
    print(f"文件大小: {video_file.stat().st_size / 1024 / 1024:.2f} MB\n")
    
    try:
        from app.services.audio_extractor import audio_extractor
        from app.services.transcriber import transcriber_service
        
        # 步骤 1: 提取音频
        print("🎵 步骤 1: 提取音频...")
        audio_path = await audio_extractor.extract(video_file)
        print(f"   ✅ 音频: {audio_path}")
        print(f"   大小: {audio_path.stat().st_size / 1024:.2f} KB")
        
        # 步骤 2: 语音识别
        print("\n🎤 步骤 2: 语音识别（首次运行会下载模型，请耐心等待）...")
        transcript = await transcriber_service.transcribe(audio_path)
        
        # 显示结果
        print("\n" + "="*60)
        print("✅ 提取完成！")
        print("="*60)
        print(f"\n文案内容:")
        print("-"*60)
        print(transcript.raw_text)
        print("\n" + "="*60)
        
        # 保存到文件
        output_file = Path("output/transcript.txt")
        output_file.parent.mkdir(exist_ok=True)
        output_file.write_text(transcript.raw_text, encoding='utf-8')
        print(f"\n💾 已保存到: {output_file}")
        
    except Exception as e:
        print(f"\n❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
