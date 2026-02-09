# 抖音短视频文案提取工具

基于FastAPI的抖音视频音频文案提取工具，支持批量处理与大模型增强。

## ✨ 主要功能

- 🎵 **音频提取**: 从视频中提取高质量音频
- 🎯 **语音识别**: 使用Faster-Whisper进行本地语音转文字
- 🤖 **LLM增强**: 可选的大模型文案优化
- 📁 **文件上传**: 支持本地视频文件上传处理
- 🔄 **批量处理**: 支持多文件同时处理
- 🌐 **Web界面**: 提供友好的API文档界面

## 🚀 快速开始

### 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 配置环境

1. 复制环境配置文件：
```bash
cp env.example .env
```

2. 根据需要修改 `.env` 文件中的配置

### 启动服务

#### Linux/macOS
```bash
chmod +x start.sh
./start.sh
```

#### Windows
```bash
start.bat
```

### 访问服务

- **Web界面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc

## 📝 API使用

### URL处理
```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.douyin.com/video/xxx"}'
```

### 文件上传
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@video.mp4" \
  -F "title=测试视频"
```

## 🛠️ 技术栈

- **Web框架**: FastAPI + Uvicorn
- **语音识别**: Faster-Whisper
- **音频处理**: FFmpeg
- **LLM支持**: OpenAI API
- **异步处理**: AsyncIO

## ⚙️ 配置说明

主要配置项（`.env`文件）：

- `ASR_MODE`: 语音识别模式 (local)
- `WHISPER_MODEL_SIZE`: Whisper模型大小 (base/small/medium/large)
- `LLM_ENABLED`: 是否启用LLM增强
- `MAX_CONCURRENT_TASKS`: 最大并发任务数

## 📋 注意事项

- 直接抖音URL下载可能会受到反爬虫限制
- 推荐使用文件上传功能处理本地视频
- 首次运行会自动下载Whisper模型文件
- 确保系统已安装FFmpeg

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License
