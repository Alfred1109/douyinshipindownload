"""
测试 Playwright 浏览器自动化方案
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def test():
    print("="*60)
    print("测试 Playwright 浏览器自动化")
    print("="*60)
    
    # 测试 URL
    test_url = input("\n请输入抖音视频链接（或按回车使用默认）: ").strip()
    if not test_url:
        test_url = "https://www.douyin.com/video/7605511073625656611"
    
    print(f"\n测试 URL: {test_url}")
    
    try:
        from app.services.browser_fetcher import browser_fetcher
        
        print("\n🚀 步骤 1: 启动浏览器...")
        await browser_fetcher._ensure_browser()
        print("   ✅ 浏览器启动成功")
        
        print("\n🔍 步骤 2: 获取视频信息和资源 URL...")
        video_url, video_info = await browser_fetcher.fetch_video_info(test_url)
        
        if video_info:
            print(f"   ✅ 标题: {video_info.title}")
            print(f"   ✅ 作者: {video_info.author}")
            print(f"   ✅ 视频ID: {video_info.video_id}")
        else:
            print("   ⚠️  未能提取视频信息")
        
        if video_url:
            print(f"   ✅ 资源 URL: {video_url[:100]}...")
            
            print("\n📥 步骤 3: 下载视频...")
            output_path = Path("temp") / f"test_{video_info.video_id if video_info else 'video'}.mp4"
            success = await browser_fetcher.download_resource(video_url, output_path)
            
            if success:
                print(f"   ✅ 下载成功: {output_path}")
                print(f"   ✅ 文件大小: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
                print("\n🎉 测试成功！浏览器自动化方案可用")
            else:
                print("   ❌ 下载失败")
        else:
            print("   ❌ 未能获取资源 URL")
            print("\n可能原因:")
            print("   1. 视频需要登录才能访问")
            print("   2. 视频设置了隐私权限")
            print("   3. 网络请求被拦截")
            print("\n建议:")
            print("   1. 在 Cookie 管理页面上传有效的 Cookie")
            print("   2. 或使用文件上传功能")
        
        print("\n🔒 关闭浏览器...")
        await browser_fetcher.close()
        
    except ImportError as e:
        print("\n❌ Playwright 未安装")
        print("\n请运行以下命令安装:")
        print("  pip install playwright")
        print("  playwright install chromium")
        print(f"\n错误详情: {e}")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(test())
