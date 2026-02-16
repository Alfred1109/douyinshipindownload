"""
Cookie 提取增强脚本 - 诊断和修复 Cookie 问题
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.utils.cookie_helper import extract_cookies_to_file, _get_browser_funcs, _try_extract, _score_cookies

def diagnose_cookies():
    """诊断 Cookie 提取问题"""
    print("=" * 60)
    print("Cookie 提取诊断工具")
    print("=" * 60)
    
    # 检查 rookiepy
    try:
        import rookiepy
        print("✅ rookiepy 已安装")
    except ImportError:
        print("❌ rookiepy 未安装，请运行: pip install rookiepy")
        return
    
    # 检查浏览器
    print("\n📋 检查已安装的浏览器...")
    browser_funcs = _get_browser_funcs()
    
    results = {}
    for browser_name, func in browser_funcs.items():
        print(f"\n🔍 尝试从 {browser_name} 提取...")
        cookies = _try_extract(browser_name, func)
        
        if cookies:
            score = _score_cookies(cookies)
            results[browser_name] = (cookies, score)
            
            # 分析 Cookie 质量
            names = {c.get("name") for c in cookies}
            
            print(f"   ✅ 提取到 {len(cookies)} 个 cookies，质量分数: {score}")
            print(f"   Cookie 列表:")
            for name in sorted(names):
                print(f"      - {name}")
            
            # 检查关键字段
            print(f"\n   关键字段检查:")
            key_fields = {
                "sessionid": "登录态（强）",
                "sessionid_ss": "登录态（强）",
                "sid_tt": "用户身份",
                "uid_tt": "用户身份",
                "msToken": "反爬字段（新）",
                "ms_token": "反爬字段",
                "s_v_web_id": "设备指纹（重要）",
                "__ac_signature": "签名",
                "ttwid": "设备ID",
            }
            
            for field, desc in key_fields.items():
                status = "✅" if field in names else "❌"
                print(f"      {status} {field:20s} - {desc}")
        else:
            print(f"   ❌ 未找到抖音 cookies")
    
    # 推荐最佳浏览器
    if results:
        print("\n" + "=" * 60)
        print("📊 浏览器推荐排序（按质量分数）:")
        sorted_results = sorted(results.items(), key=lambda x: x[1][1], reverse=True)
        
        for i, (browser, (cookies, score)) in enumerate(sorted_results, 1):
            print(f"   {i}. {browser:10s} - 分数: {score:4d}, Cookies: {len(cookies):3d} 个")
        
        best_browser = sorted_results[0][0]
        best_score = sorted_results[0][1][1]
        
        print(f"\n💡 建议使用: {best_browser} (分数: {best_score})")
        
        # 检查是否需要登录
        best_cookies = sorted_results[0][1][0]
        names = {c.get("name") for c in best_cookies}
        
        if "sessionid" not in names and "sessionid_ss" not in names:
            print("\n⚠️  警告: 未检测到登录态 cookies")
            print("   建议操作:")
            print(f"   1. 用 {best_browser} 浏览器打开 https://www.douyin.com")
            print("   2. 登录你的抖音账号")
            print("   3. 浏览几个视频，确保页面完全加载")
            print("   4. 关闭浏览器")
            print("   5. 重新运行此脚本")
        
        if "s_v_web_id" not in names:
            print("\n⚠️  警告: 缺少 s_v_web_id 字段")
            print("   这可能导致 yt-dlp 提示 'Fresh cookies' 错误")
            print("   建议:")
            print(f"   1. 用 {best_browser} 访问抖音并刷新几次页面")
            print("   2. 或使用浏览器扩展手动导出 cookies")
        
        # 保存最佳 cookies
        print(f"\n💾 正在保存 {best_browser} 的 cookies...")
        cookie_file = extract_cookies_to_file()
        if cookie_file:
            print(f"   ✅ 已保存到: {cookie_file}")
        else:
            print(f"   ❌ 保存失败")
    else:
        print("\n" + "=" * 60)
        print("❌ 所有浏览器都没有抖音 cookies！")
        print("\n解决方案:")
        print("1. 用任意浏览器（推荐 Edge 或 Chrome）访问 https://www.douyin.com")
        print("2. 登录账号并浏览几个视频")
        print("3. 重新运行此脚本")
        print("\n或者:")
        print("使用浏览器扩展手动导出 cookies.txt 文件")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    diagnose_cookies()
