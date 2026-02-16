"""
测试下载功能 - 验证 Playwright 方案
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def main():
    url = "https://www.douyin.com/video/7605511073625656611"
    
    print("="*60)
    print("测试 Playwright 下载方案")
    print("="*60)
    print(f"\n视频链接: {url}\n")
    
    try:
        from app.services.douyin_parser import douyin_parser
        
        print("🚀 开始下载...")
        video_path, video_info = await douyin_parser.download_video(url)
        
        print("\n" + "="*60)
        print("✅ 下载成功！")
        print("="*60)
        print(f"\n视频ID: {video_info.video_id}")
        print(f"标题: {video_info.title}")
        print(f"作者: {video_info.author}")
        print(f"文件路径: {video_path}")
        print(f"文件大小: {video_path.stat().st_size / 1024 / 1024:.2f} MB")
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ 下载失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
