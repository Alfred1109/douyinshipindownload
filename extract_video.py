"""
提取抖音视频内容
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def main():
    url = "https://www.douyin.com/video/7605511073625656611"
    
    print("="*60)
    print("抖音视频内容提取")
    print("="*60)
    print(f"\n视频链接: {url}\n")
    
    try:
        # 导入服务
        from app.services.pipeline import process_single
        
        print("🚀 开始处理...")
        result = await process_single(url, use_llm=True)
        
        print("\n" + "="*60)
        print("✅ 提取完成！")
        print("="*60)
        print(f"\n视频ID: {result.video_info.video_id}")
        print(f"标题: {result.video_info.title}")
        print(f"作者: {result.video_info.author}")
        
        if result.transcript:
            print(f"\n原始文案:")
            print("-"*60)
            print(result.transcript.raw_text)
            
            if result.transcript.enhanced_text and result.transcript.enhanced_text != result.transcript.raw_text:
                print(f"\n优化后文案:")
                print("-"*60)
                print(result.transcript.enhanced_text)
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
