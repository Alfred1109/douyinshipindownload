# 系统架构文档

## 📐 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Web 界面    │  │  API 文档    │  │  命令行工具   │      │
│  │ (index.html) │  │  (Swagger)   │  │  (测试脚本)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI 应用层                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  主路由      │  │  上传路由    │  │  Cookie路由   │      │
│  │  (routes)    │  │  (upload)    │  │  (cookie)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      业务编排层                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Pipeline (流水线编排)                    │    │
│  │  • 任务管理 (单个/批量)                               │    │
│  │  • 进度跟踪                                          │    │
│  │  • 错误处理                                          │    │
│  │  • 结果保存                                          │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      核心服务层                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 浏览器抓取   │  │  音频提取    │  │  语音识别    │      │
│  │ (Playwright) │→ │  (FFmpeg)    │→ │  (Whisper)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                              ↓               │
│                          ┌──────────────────────┐           │
│                          │    LLM 增强          │           │
│                          │  (DeepSeek API)      │           │
│                          └──────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      基础设施层                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  文件系统    │  │  配置管理    │  │  日志系统    │      │
│  │  (temp/out)  │  │  (.env)      │  │  (logging)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 🗂️ 目录结构

```
shipindownload/
├── app/                          # 应用主目录
│   ├── api/                      # API 路由层
│   │   ├── routes.py            # 主路由（提取、批量）
│   │   ├── upload_routes.py     # 文件上传路由
│   │   └── cookie_routes.py     # Cookie 管理路由
│   ├── models/                   # 数据模型
│   │   └── schemas.py           # Pydantic 模型定义
│   ├── services/                 # 核心服务层
│   │   ├── browser_fetcher.py   # Playwright 浏览器抓取
│   │   ├── douyin_parser.py     # 抖音视频解析
│   │   ├── audio_extractor.py   # 音频提取服务
│   │   ├── transcriber.py       # 语音识别服务
│   │   ├── llm_enhancer.py      # LLM 文案增强
│   │   └── pipeline.py          # 流水线编排
│   ├── utils/                    # 工具函数
│   │   ├── helpers.py           # 通用工具
│   │   └── cookie_helper.py     # Cookie 处理
│   ├── config.py                # 配置管理
│   └── main.py                  # FastAPI 应用入口
├── web/                          # 前端界面
│   └── index.html               # Web UI（单页应用）
├── temp/                         # 临时文件目录
│   ├── *.mp4                    # 下载的视频
│   ├── *.mp3                    # 提取的音频
│   └── cookies.txt              # Cookie 文件
├── output/                       # 输出目录
│   ├── *.json                   # 完整结果（JSON）
│   └── *.txt                    # 纯文本文案
├── .env                          # 环境配置
├── requirements.txt              # Python 依赖
├── start_with_check.bat         # Windows 启动脚本
├── start.sh                     # Linux/macOS 启动脚本
└── README.md                    # 项目文档
```

## 🔄 核心流程

### 1. URL 提取流程

```
用户输入 URL
    ↓
API 接收请求 (routes.py)
    ↓
Pipeline 创建任务 (pipeline.py)
    ↓
┌─────────────────────────────────────┐
│ 阶段 1: 下载视频                     │
│ • browser_fetcher.py 启动浏览器     │
│ • 加载 Cookie（如果有）              │
│ • 访问抖音页面                       │
│ • 拦截网络请求                       │
│ • 捕获视频 URL                       │
│ • 下载到 temp/*.mp4                 │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 阶段 2: 提取音频                     │
│ • audio_extractor.py 调用 FFmpeg    │
│ • 从 MP4 提取 MP3                   │
│ • 保存到 temp/*.mp3                 │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 阶段 3: 语音识别                     │
│ • transcriber.py 加载 Whisper       │
│ • 使用 GPU 加速（GTX 1060）          │
│ • 识别音频为文字                     │
│ • 返回原始文案                       │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 阶段 4: LLM 增强（可选）             │
│ • llm_enhancer.py 调用 API          │
│ • 纠正同音错字                       │
│ • 添加标点符号                       │
│ • 优化断句                          │
│ • 返回增强文案                       │
└─────────────────────────────────────┘
    ↓
保存结果到 output/
    ↓
返回给用户
```

### 2. 文件上传流程

```
用户上传视频文件
    ↓
API 接收文件 (upload_routes.py)
    ↓
保存到 temp/*.mp4
    ↓
跳过下载阶段，直接进入阶段 2
    ↓
提取音频 → 语音识别 → LLM 增强
    ↓
返回结果
```

## 🧩 核心组件详解

### 1. Browser Fetcher (浏览器抓取)

**文件**: `app/services/browser_fetcher.py`

**技术**: Playwright + Chromium

**功能**:
- 启动无头浏览器
- 加载 Cookie 模拟登录
- 拦截网络请求
- 捕获视频 URL
- 下载视频文件

**优势**:
- 完全绕过反爬虫
- 自动处理 JavaScript 加密
- 模拟真实用户行为

### 2. Audio Extractor (音频提取)

**文件**: `app/services/audio_extractor.py`

**技术**: FFmpeg

**功能**:
- 从视频提取音频
- 转换为 MP3 格式
- 优化音频质量

**参数**:
```bash
ffmpeg -i video.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3
```

### 3. Transcriber (语音识别)

**文件**: `app/services/transcriber.py`

**技术**: Faster-Whisper + CUDA

**配置**:
- 模型: medium
- 设备: CUDA (GTX 1060)
- 精度: float32
- 语言: 中文

**性能**:
- 5 分钟音频 → 1.9 秒识别
- 速度: 868 字/秒
- GPU 加速: 150-300 倍提升

### 4. LLM Enhancer (文案增强)

**文件**: `app/services/llm_enhancer.py`

**技术**: OpenAI API (兼容)

**功能**:
- 纠正同音错字
- 添加标点符号
- 优化断句
- 保持原意

**API**:
- 端点: `https://ark.cn-beijing.volces.com/api/v3`
- 模型: `deepseek-v3-2-251201`
- 温度: 0.3

### 5. Pipeline (流水线编排)

**文件**: `app/services/pipeline.py`

**功能**:
- 任务管理（单个/批量）
- 进度跟踪
- 错误处理
- 并发控制
- 结果保存

**特性**:
- 异步处理
- 信号量控制并发（最大 3 个）
- 自动清理临时文件
- 失败重试机制

## 🔧 配置系统

### 配置文件: `.env`

```env
# ─── ASR 语音识别 ───
ASR_MODE=local                    # local / api
WHISPER_MODEL_SIZE=medium         # tiny/base/small/medium/large
WHISPER_DEVICE=cuda               # auto/cpu/cuda
WHISPER_COMPUTE_TYPE=float32      # float16/int8/float32
WHISPER_LANGUAGE=zh               # 识别语言

# ─── LLM 大模型 ───
LLM_ENABLED=true                  # 是否启用
ARK_API_KEY=35a5ea0a-...          # API Key
LLM_API_BASE=https://ark...       # API 端点
LLM_MODEL=deepseek-v3-2-251201    # 模型名称
LLM_TEMPERATURE=0.3               # 温度参数

# ─── 批量处理 ───
MAX_CONCURRENT_TASKS=3            # 最大并发数
```

### 配置管理: `app/config.py`

使用 `pydantic-settings` 管理配置:
- 自动读取 `.env` 文件
- 支持环境变量覆盖
- 类型验证
- 默认值

## 🌐 API 接口

### 主要端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/extract` | POST | URL 提取 |
| `/api/batch` | POST | 批量提取 |
| `/api/upload` | POST | 文件上传 |
| `/api/task/{id}` | GET | 查询任务 |
| `/api/cookies/upload` | POST | 上传 Cookie |
| `/api/cookies/status` | GET | Cookie 状态 |
| `/api/cookies/clear` | DELETE | 清除 Cookie |

### 数据模型

**请求模型**:
```python
class ExtractRequest(BaseModel):
    url: str
    use_llm: bool = True
```

**响应模型**:
```python
class TaskResponse(BaseModel):
    task_id: str
    url: str
    status: TaskStatus
    progress: float
    video_info: Optional[VideoInfo]
    transcript: Optional[TranscriptResult]
    error: Optional[str]
```

## 🚀 性能优化

### 1. GPU 加速
- 使用 CUDA 加速 Whisper
- GTX 1060 (6GB 显存)
- float32 精度
- 150-300 倍速度提升

### 2. 并发处理
- 异步 I/O (AsyncIO)
- 信号量控制并发
- 最大 3 个并发任务

### 3. 资源管理
- 自动清理临时文件
- 浏览器实例复用
- 连接池管理

### 4. 缓存策略
- Whisper 模型缓存
- 浏览器 Cookie 缓存

## 🔒 安全考虑

### 1. 文件安全
- 临时文件自动清理
- 文件名安全过滤
- 路径遍历防护

### 2. API 安全
- CORS 配置
- 请求大小限制
- 超时控制

### 3. 隐私保护
- Cookie 本地存储
- 不上传用户数据
- 临时文件加密（可选）

## 📊 监控与日志

### 日志系统

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
)
```

### 关键日志点
- 任务创建/完成
- 下载进度
- 识别进度
- 错误信息
- 性能指标

## 🔄 扩展性

### 支持的扩展

1. **新的视频平台**
   - 实现新的 Parser 类
   - 继承 `BaseParser` 接口

2. **新的 ASR 引擎**
   - 实现新的 Transcriber
   - 继承 `BaseTranscriber` 接口

3. **新的 LLM 提供商**
   - 修改 `llm_enhancer.py`
   - 支持 OpenAI 兼容 API

4. **新的存储后端**
   - 实现存储适配器
   - 支持 S3/OSS/本地

## 🎯 最佳实践

### 1. 使用文件上传
- 最可靠的方式
- 无需配置 Cookie
- 支持任意来源视频

### 2. GPU 加速
- 使用 CUDA 设备
- 选择合适的精度
- 监控显存使用

### 3. 批量处理
- 控制并发数量
- 避免资源耗尽
- 监控任务状态

### 4. 错误处理
- 优雅降级
- 返回原始文案
- 记录详细日志

## 📈 性能指标

### 典型场景

**5 分钟视频处理时间**:
- 下载: 10-30 秒
- 音频提取: 2-5 秒
- 语音识别: 1-2 秒 (GPU)
- LLM 增强: 3-5 秒
- **总计**: 约 20-45 秒

**资源占用**:
- CPU: 10-30%
- GPU: 50-80% (识别时)
- 内存: 2-4 GB
- 磁盘: 临时文件 < 100 MB

## 🛠️ 故障排查

### 常见问题

1. **Playwright 未安装**
   ```bash
   playwright install chromium
   ```

2. **CUDA 不可用**
   - 检查 GPU 驱动
   - 安装 PyTorch CUDA 版本

3. **Cookie 失效**
   - 重新导出 Cookie
   - 或使用文件上传

4. **LLM API 错误**
   - 检查 API Key
   - 验证网络连接
   - 查看配额限制

## 📚 相关文档

- [README.md](README.md) - 快速开始指南
- [PLAYWRIGHT_方案.md](PLAYWRIGHT_方案.md) - Playwright 详细说明
- [API 文档](http://localhost:8000/docs) - Swagger UI
- [.env 配置](env.example) - 环境变量示例
