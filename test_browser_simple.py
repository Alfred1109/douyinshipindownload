"""
简单的浏览器测试 - 验证 Playwright 是否正常工作
"""
import asyncio
from playwright.async_api import async_playwright

async def test_browser():
    print("="*60)
    print("测试 Playwright 浏览器基础功能")
    print("="*60)
    
    try:
        print("\n🚀 步骤 1: 启动 Playwright...")
        async with async_playwright() as p:
            print("   ✅ Playwright 启动成功")
            
            print("\n🌐 步骤 2: 启动 Chromium 浏览器...")
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            print("   ✅ 浏览器启动成功")
            
            print("\n📄 步骤 3: 创建页面...")
            page = await browser.new_page()
            print("   ✅ 页面创建成功")
            
            print("\n🔗 步骤 4: 访问测试网站...")
            await page.goto('https://www.baidu.com', timeout=30000)
            title = await page.title()
            print(f"   ✅ 成功访问，页面标题: {title}")
            
            print("\n🔒 步骤 5: 关闭浏览器...")
            await browser.close()
            print("   ✅ 浏览器关闭成功")
            
            print("\n" + "="*60)
            print("🎉 测试成功！Playwright 工作正常")
            print("="*60)
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_browser())
