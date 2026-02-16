# 🎭 Playwright 浏览器自动化方案

## 🎯 方案说明

使用 Playwright 完全模拟真实浏览器行为，彻底解决抖音反爬问题。

### 核心优势

1. **完全模拟真实浏览器**
   - 自动执行 JavaScript
   - 自动处理加密和混淆
   - 完整的浏览器环境

2. **自动拦截网络请求**
   - 捕获视频/音频资源 URL
   - 无需解析复杂的页面结构
   - 直接获取真实下载链接

3. **自动加载 Cookie**
   - 从 `temp/cookies.txt` 自动加载
   - 支持完整的 Cookie 格式
   - 模拟登录状态

4. **智能资源选择**
   - 优先选择高质量视频
   - 自动选择最大文件
   - 支持音频降级

## 📦 安装步骤

### 方式 1: 使用安装脚本（推荐）

```bash
# Windows
install_playwright.bat

# Linux/macOS
chmod +x install_playwright.sh
./install_playwright.sh
```

### 方式 2: 手动安装

```bash
# 1. 安装 Python 包
pip install playwright

# 2. 安装 Chromium 浏览器
playwright install chromium
```

## 🧪 测试

```bash
python test_playwright.py
```

测试脚本会：
1. 启动浏览器
2. 访问抖音视频页面
3. 拦截网络请求获取资源 URL
4. 下载视频
5. 显示结果

## 🚀 使用方法

### 1. 启动服务

```bash
python -m uvicorn app.main:app --reload
```

### 2. 访问 Web 界面

```
http://localhost:8000
```

### 3. 使用 URL 提取

- 切换到"URL 提取"标签
- 输入抖音视频链接
- 点击"开始提取"
- 自动使用浏览器下载

### 4. 配置 Cookie（可选）

如果视频需要登录才能访问：
- 切换到"Cookie 管理"标签
- 导出并上传 Cookie
- 浏览器会自动加载 Cookie

## 🔧 工作原理

```
1. 启动 Chromium 浏览器（无头模式）
   ↓
2. 加载 Cookie（如果有）
   ↓
3. 访问抖音视频页面
   ↓
4. 拦截所有网络请求
   ↓
5. 捕获视频/音频资源 URL
   ↓
6. 提取视频信息（标题、作者等）
   ↓
7. 下载资源到本地
   ↓
8. 返回文件路径
```

## 📊 与其他方案对比

| 方案 | 可靠性 | 速度 | Cookie 需求 | 复杂度 |
|------|--------|------|------------|--------|
| **Playwright** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 可选 | ⭐⭐ |
| yt-dlp | ⭐⭐ | ⭐⭐⭐⭐⭐ | 必需 | ⭐ |
| 网页解析 | ⭐ | ⭐⭐⭐⭐ | 必需 | ⭐⭐⭐⭐ |
| 文件上传 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 不需要 | ⭐ |

## ⚙️ 配置选项

### 浏览器设置

在 `browser_fetcher.py` 中可以调整：

```python
# 无头模式（不显示浏览器窗口）
headless=True

# 窗口大小
viewport={'width': 1920, 'height': 1080}

# User-Agent
user_agent='Mozilla/5.0 ...'
```

### 超时设置

```python
# 页面加载超时
timeout=30000  # 30秒

# 等待时间
wait_for_timeout=2000  # 2秒
```

## 🐛 故障排查

### 问题 1: Playwright 未安装

```
❌ ImportError: No module named 'playwright'
```

**解决**:
```bash
pip install playwright
playwright install chromium
```

### 问题 2: Chromium 未安装

```
❌ Executable doesn't exist at ...
```

**解决**:
```bash
playwright install chromium
```

### 问题 3: 未捕获到资源

```
❌ 未捕获到视频/音频资源
```

**可能原因**:
- 视频需要登录
- 视频设置了隐私权限
- 网络请求被拦截

**解决**:
1. 上传有效的 Cookie
2. 增加等待时间
3. 使用文件上传功能

### 问题 4: 下载失败

```
❌ 下载失败: HTTP 403
```

**解决**:
- 检查 Cookie 是否有效
- 尝试重新导出 Cookie
- 使用文件上传功能

## 💡 最佳实践

### 1. Cookie 管理

- 定期更新 Cookie（7-30天过期）
- 确保 Cookie 包含登录态
- 使用浏览器扩展导出

### 2. 性能优化

- 首次启动较慢（需要启动浏览器）
- 后续请求会复用浏览器实例
- 批量处理时效率更高

### 3. 错误处理

- 自动重试机制
- 降级到文件上传
- 详细的错误日志

## 🎊 总结

Playwright 方案的优势：

1. ✅ **最可靠** - 完全模拟真实浏览器
2. ✅ **最智能** - 自动处理 JavaScript 和加密
3. ✅ **最灵活** - 支持各种复杂场景
4. ✅ **最简单** - 无需手动解析页面

现在你的工具可以：
- 自动获取抖音视频
- 无需担心反爬问题
- 专注于文案提取的核心价值

🚀 开始使用吧！
