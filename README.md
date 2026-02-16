# 抖音短视频文案提取工具

基于 FastAPI + Playwright 的抖音视频音频文案提取工具，支持批量处理与大模型增强。

## ✨ 主要功能

- 🎭 **浏览器自动化**: 使用 Playwright 模拟真实浏览器，完全绕过反爬限制
- 🎵 **音频提取**: 从视频中提取高质量音频
- 🎯 **语音识别**: 使用 Faster-Whisper 进行本地语音转文字
- 🤖 **LLM 增强**: 可选的大模型文案优化（纠错、标点、断句）
- 📁 **文件上传**: 支持本地视频文件上传处理
- 🔄 **批量处理**: 支持多文件同时处理
- 🌐 **Web 界面**: 提供友好的 API 文档界面
- 🍪 **Cookie 管理**: Web 界面管理 Cookie，无需命令行

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
python scripts/install_playwright.bat  # Windows
playwright install chromium            # 或直接运行
```

### 2. 配置环境

```bash
# 复制环境配置文件
cp env.example .env

# 根据需要修改 .env 文件中的配置
```

### 3. 启动服务

```bash
# 方式 1: 使用启动脚本（推荐）
scripts\start_with_check.bat  # Windows
./scripts/start.sh            # Linux/macOS

# 方式 2: 直接启动
python -m uvicorn app.main:app --reload
```

### 4. 访问服务

- **Web 界面**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **ReDoc 文档**: http://localhost:8000/redoc

## 📝 使用方式

### 方式 1: 文件上传（推荐）⭐⭐⭐⭐⭐

1. 访问 http://localhost:8000
2. 默认就是"文件上传"模式
3. 点击选择视频文件或拖拽上传
4. 自动提取文案

**优点**: 100% 可靠，无需配置 Cookie，支持任意来源的视频

### 方式 2: URL 提取 ⭐⭐⭐⭐

1. 切换到"URL 提取"标签
2. 输入抖音视频链接
3. 自动使用浏览器下载并提取

**优点**: 自动化程度高，适合批量处理

### 方式 3: API 调用

```bash
# 文件上传
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@video.mp4" \
  -F "title=测试视频"

# URL 提取
curl -X POST "http://localhost:8000/api/extract" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.douyin.com/video/xxx"}'
```

## 🛠️ 技术栈

- **Web 框架**: FastAPI + Uvicorn
- **浏览器自动化**: Playwright (Chromium)
- **语音识别**: Faster-Whisper (本地)
- **音频处理**: FFmpeg
- **LLM 支持**: OpenAI API 兼容接口
- **异步处理**: AsyncIO

## ⚙️ 配置说明

主要配置项（`.env` 文件）：

```env
# ASR 语音识别
ASR_MODE=local                    # local 或 api
WHISPER_MODEL_SIZE=medium         # tiny/base/small/medium/large
WHISPER_DEVICE=auto               # auto/cpu/cuda
WHISPER_LANGUAGE=zh               # 识别语言

# LLM 大模型增强
LLM_ENABLED=true                  # 是否启用
LLM_API_KEY=your-key              # API Key
LLM_MODEL=deepseek-v3-2-251201    # 模型名称

# 批量处理
MAX_CONCURRENT_TASKS=3            # 最大并发数
```

## 🎭 Playwright 方案

本工具使用 Playwright 浏览器自动化技术：

### 优势

- ✅ **完全绕过反爬** - 模拟真实浏览器行为
- ✅ **自动处理加密** - JavaScript 自动执行
- ✅ **无需解析页面** - 直接拦截网络请求
- ✅ **Cookie 可选** - 游客也能访问公开视频

### 工作原理

1. 启动 Chromium 浏览器（无头模式）
2. 加载 Cookie（如果有）
3. 访问抖音视频页面
4. 拦截网络请求，捕获视频 URL
5. 下载视频到本地
6. 提取音频并进行语音识别

### 测试

```bash
# 测试 Playwright 浏览器自动化
python tests/test_playwright.py

# 测试 Whisper GPU 加速
python tests/test_whisper_gpu.py

# 测试 LLM 增强
python tests/test_llm_enhance.py
```

详细文档: [docs/PLAYWRIGHT_方案.md](docs/PLAYWRIGHT_方案.md)

## 🍪 Cookie 管理

### 为什么需要 Cookie？

- 访问需要登录的视频
- 提高下载成功率
- 访问高清视频

### 如何配置？

1. 访问 http://localhost:8000
2. 切换到"Cookie 管理"标签
3. 按教程导出 Cookie
4. 粘贴上传

**推荐工具**: Get cookies.txt LOCALLY (Chrome 扩展)

## 📋 注意事项

- 首次运行会自动下载 Whisper 模型文件
- 确保系统已安装 FFmpeg
- Playwright 首次启动需要下载 Chromium（约 150MB）
- 推荐使用文件上传功能（最可靠）

## 🔧 故障排查

### Playwright 未安装

```bash
pip install playwright
playwright install chromium
```

### FFmpeg 未安装

从 https://ffmpeg.org/download.html 下载并安装

### Cookie 问题

- 使用文件上传功能（无需 Cookie）
- 或在 Web 界面的"Cookie 管理"中上传有效 Cookie

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📚 文档

- [架构文档](docs/ARCHITECTURE.md) - 系统架构详解
- [技术栈说明](docs/TECH_STACK.md) - 完整技术栈
- [快速参考](docs/QUICK_REFERENCE.md) - 命令速查
- [系统总览](docs/SYSTEM_OVERVIEW.md) - 可视化架构
- [优化说明](docs/OPTIMIZATION_NOTES.md) - 性能优化分析
- [Playwright 方案](docs/PLAYWRIGHT_方案.md) - 浏览器自动化详解

## 📄 许可证

MIT License
