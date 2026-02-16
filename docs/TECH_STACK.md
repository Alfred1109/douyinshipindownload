# 技术栈详解

## 📚 完整技术栈

### 后端框架
- **FastAPI** 0.104+ - 现代化的 Python Web 框架
  - 自动生成 API 文档
  - 类型提示支持
  - 异步处理
  - 高性能

- **Uvicorn** - ASGI 服务器
  - 支持 WebSocket
  - 热重载
  - 生产级性能

### 浏览器自动化
- **Playwright** 1.40+ - 微软开源的浏览器自动化工具
  - 支持 Chromium/Firefox/WebKit
  - 网络请求拦截
  - 无头模式
  - 跨平台

### 语音识别
- **Faster-Whisper** 1.0+ - OpenAI Whisper 的优化版本
  - CTranslate2 加速
  - GPU 支持
  - 低内存占用
  - 高准确度

- **PyTorch** 2.5.1+cu121 - 深度学习框架
  - CUDA 12.1 支持
  - GPU 加速
  - 模型推理

### 音视频处理
- **FFmpeg** - 音视频处理工具
  - 格式转换
  - 音频提取
  - 编解码

### 大模型集成
- **OpenAI Python SDK** 1.6+ - LLM API 客户端
  - 兼容多种 API
  - 异步支持
  - 流式响应

### 数据验证
- **Pydantic** 2.5+ - 数据验证库
  - 类型验证
  - 自动文档
  - 配置管理

- **Pydantic-Settings** 2.1+ - 配置管理
  - .env 文件支持
  - 环境变量
  - 类型安全

### HTTP 客户端
- **HTTPX** 0.25+ - 现代 HTTP 客户端
  - 异步支持
  - HTTP/2
  - 连接池

### 其他工具
- **python-multipart** - 文件上传支持
- **yt-dlp** - 视频下载工具（备用）
- **rookiepy** - Cookie 提取（备用）

## 🔧 开发工具

### 代码质量
- Python 3.8+
- Type Hints
- Async/Await

### 测试工具
- 单元测试脚本
- API 测试
- 集成测试

### 部署工具
- 启动脚本 (Windows/Linux)
- 环境检查
- 依赖管理

## 🏗️ 架构模式

### 分层架构
```
┌─────────────────────┐
│   Presentation      │  Web UI + API
├─────────────────────┤
│   Application       │  Pipeline + Routes
├─────────────────────┤
│   Domain            │  Services + Models
├─────────────────────┤
│   Infrastructure    │  Config + Utils
└─────────────────────┘
```

### 设计模式

1. **单例模式**
   - Settings 配置
   - Service 实例

2. **工厂模式**
   - Task 创建
   - Service 初始化

3. **策略模式**
   - ASR 模式切换
   - 下载策略

4. **管道模式**
   - Pipeline 流水线
   - 中间件处理

## 🔄 数据流

### 请求流
```
HTTP Request
    ↓
FastAPI Router
    ↓
Pydantic Validation
    ↓
Pipeline Orchestration
    ↓
Service Layer
    ↓
External APIs/Tools
    ↓
Response Model
    ↓
HTTP Response
```

### 文件流
```
Video URL/File
    ↓
Browser/Upload
    ↓
temp/*.mp4
    ↓
FFmpeg
    ↓
temp/*.mp3
    ↓
Whisper
    ↓
Raw Text
    ↓
LLM API
    ↓
Enhanced Text
    ↓
output/*.txt/json
```

## 🚀 性能优化技术

### 1. 异步编程
```python
async def process_single(url: str):
    video = await download_video(url)
    audio = await extract_audio(video)
    text = await transcribe(audio)
    return text
```

### 2. 并发控制
```python
semaphore = asyncio.Semaphore(3)
async with semaphore:
    result = await process_task()
```

### 3. GPU 加速
```python
model = WhisperModel(
    model_size="medium",
    device="cuda",
    compute_type="float32"
)
```

### 4. 资源池化
- 浏览器实例复用
- HTTP 连接池
- 模型缓存

## 🔒 安全机制

### 1. 输入验证
```python
class ExtractRequest(BaseModel):
    url: HttpUrl  # 自动验证 URL 格式
    use_llm: bool = True
```

### 2. 文件安全
```python
# 安全的文件名
safe_title = "".join(
    c if c.isalnum() or c in '._- ' 
    else '_' 
    for c in title
)[:80]
```

### 3. 超时控制
```python
async with asyncio.timeout(120):
    await download_video(url)
```

### 4. 错误处理
```python
try:
    result = await process()
except Exception as e:
    logger.error(f"Error: {e}")
    return fallback_result
```

## 📊 监控指标

### 应用指标
- 请求数量
- 响应时间
- 错误率
- 并发数

### 系统指标
- CPU 使用率
- GPU 使用率
- 内存占用
- 磁盘 I/O

### 业务指标
- 任务成功率
- 平均处理时间
- 文案质量
- 用户满意度

## 🔄 CI/CD 建议

### 开发流程
```
开发 → 测试 → 构建 → 部署
```

### 自动化测试
- 单元测试
- 集成测试
- API 测试
- 性能测试

### 部署策略
- 蓝绿部署
- 滚动更新
- 金丝雀发布

## 📦 依赖管理

### 核心依赖
```
fastapi==0.104.0
playwright==1.40.0
faster-whisper==1.0.0
torch==2.5.1+cu121
openai==1.6.0
```

### 开发依赖
```
pytest
black
flake8
mypy
```

### 系统依赖
```
Python 3.8+
FFmpeg
CUDA 12.1 (可选)
Chromium (Playwright)
```

## 🌐 API 设计

### RESTful 原则
- 资源导向
- HTTP 方法语义
- 状态码规范
- 统一响应格式

### 版本控制
- URL 版本: `/api/v1/extract`
- Header 版本: `Accept: application/vnd.api+json; version=1`

### 错误处理
```json
{
  "error": {
    "code": "DOWNLOAD_FAILED",
    "message": "视频下载失败",
    "details": "网络超时"
  }
}
```

## 🔧 配置管理

### 环境分离
- `.env` - 本地开发
- `.env.production` - 生产环境
- `.env.test` - 测试环境

### 配置优先级
```
环境变量 > .env 文件 > 默认值
```

### 敏感信息
- API Key 加密存储
- 不提交到版本控制
- 使用密钥管理服务

## 📈 扩展方向

### 水平扩展
- 多实例部署
- 负载均衡
- 分布式任务队列

### 垂直扩展
- 更强的 GPU
- 更大的内存
- SSD 存储

### 功能扩展
- 支持更多平台
- 实时字幕
- 多语言支持
- 视频摘要

## 🎯 技术选型理由

### 为什么选择 FastAPI？
- ✅ 现代化、高性能
- ✅ 自动文档生成
- ✅ 类型安全
- ✅ 异步支持

### 为什么选择 Playwright？
- ✅ 完全绕过反爬
- ✅ 跨平台支持
- ✅ 活跃维护
- ✅ 强大的 API

### 为什么选择 Faster-Whisper？
- ✅ 比原版快 4 倍
- ✅ 内存占用低
- ✅ GPU 加速
- ✅ 准确度高

### 为什么选择 DeepSeek？
- ✅ 性价比高
- ✅ 中文优化
- ✅ API 兼容
- ✅ 响应快速

## 🔍 技术对比

### ASR 引擎对比

| 引擎 | 速度 | 准确度 | 成本 | 离线 |
|------|------|--------|------|------|
| Faster-Whisper | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 免费 | ✅ |
| OpenAI Whisper API | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 付费 | ❌ |
| 讯飞语音 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 付费 | ❌ |

### 下载方案对比

| 方案 | 成功率 | 速度 | 复杂度 | 维护 |
|------|--------|------|--------|------|
| Playwright | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| yt-dlp | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| 直接解析 | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |

### LLM 提供商对比

| 提供商 | 价格 | 速度 | 中文 | API |
|--------|------|------|------|-----|
| DeepSeek | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| OpenAI | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 通义千问 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 📚 学习资源

### 官方文档
- [FastAPI](https://fastapi.tiangolo.com/)
- [Playwright](https://playwright.dev/python/)
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper)
- [PyTorch](https://pytorch.org/)

### 社区资源
- GitHub Issues
- Stack Overflow
- 技术博客
- 视频教程

## 🤝 贡献指南

### 代码规范
- PEP 8 风格
- Type Hints
- Docstrings
- 单元测试

### 提交规范
```
feat: 添加新功能
fix: 修复 bug
docs: 更新文档
refactor: 重构代码
test: 添加测试
```

### 审查流程
1. 代码审查
2. 测试验证
3. 文档更新
4. 合并主分支
