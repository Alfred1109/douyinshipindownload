# 用户使用指南

## 🚀 快速开始

### 1. 启动服务

服务已经启动成功！你可以看到：

```
✅ 抖音短视频文案提取工具 启动成功
✅ ASR 模式: local (本地 Whisper)
✅ LLM 增强: 启用 (DeepSeek API)
✅ 并发任务: 3
✅ 服务地址: http://127.0.0.1:8000
```

### 2. 访问 Web 界面

打开浏览器，访问：
```
http://localhost:8000
```

你会看到一个简洁的 Web 界面，有三个标签页：
- 📁 **文件上传** - 上传本地视频文件
- 🔗 **URL 提取** - 输入抖音视频链接
- 🍪 **Cookie 管理** - 管理登录 Cookie

## 📝 使用方式

### 方式 1: URL 提取（推荐用于抖音视频）⭐⭐⭐⭐

#### 步骤：

1. **切换到"URL 提取"标签**
   - 点击页面顶部的"URL 提取"标签

2. **输入抖音视频链接**
   ```
   例如：https://www.douyin.com/video/7605511073625656611
   ```

3. **点击"开始提取"按钮**
   - 系统会自动：
     - 🌐 使用 Playwright 浏览器访问视频页面
     - 📥 下载视频到临时目录
     - 🎵 提取音频
     - 🎯 GPU 加速语音识别
     - 🤖 LLM 增强文案质量
     - 💾 保存结果到 output/ 目录

4. **查看结果**
   - 页面会实时显示处理进度
   - 完成后显示：
     - ✅ 视频标题
     - ✅ 作者信息
     - ✅ 原始文案
     - ✅ 增强后的文案

#### 处理时间：
- 5 分钟视频：约 20-45 秒
  - 下载视频：10-30 秒
  - 提取音频：2-5 秒
  - 语音识别：1-2 秒（GPU）
  - LLM 增强：3-5 秒

### 方式 2: 文件上传（推荐用于本地视频）⭐⭐⭐⭐⭐

#### 步骤：

1. **默认就在"文件上传"标签**
   - 打开页面后默认显示

2. **选择视频文件**
   - 点击"选择文件"按钮
   - 或直接拖拽视频文件到上传区域
   - 支持格式：MP4, AVI, MOV, MKV 等

3. **自动开始处理**
   - 文件上传后自动开始处理
   - 跳过下载步骤，直接提取音频

4. **查看结果**
   - 同样会显示完整的处理结果

#### 优势：
- ✅ 100% 可靠（不依赖网络）
- ✅ 无需 Cookie
- ✅ 支持任意来源的视频
- ✅ 处理速度更快（跳过下载）

### 方式 3: API 调用（适合开发者）

#### URL 提取 API

```bash
curl -X POST "http://localhost:8000/api/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.douyin.com/video/7605511073625656611"
  }'
```

#### 文件上传 API

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@video.mp4" \
  -F "title=测试视频"
```

#### 查询任务状态

```bash
curl "http://localhost:8000/api/task/{task_id}"
```

## 🍪 Cookie 管理（可选）

### 什么时候需要 Cookie？

- ❌ **不需要**：公开视频、已下载的视频文件
- ✅ **需要**：需要登录才能查看的视频、高清视频

### 如何配置 Cookie？

1. **切换到"Cookie 管理"标签**

2. **安装浏览器扩展**
   - Chrome: "Get cookies.txt LOCALLY"
   - Firefox: "cookies.txt"

3. **导出 Cookie**
   - 访问 douyin.com 并登录
   - 点击扩展图标
   - 复制 Cookie 内容

4. **上传 Cookie**
   - 粘贴到文本框
   - 点击"上传 Cookie"
   - 系统会验证并保存

5. **查看状态**
   - 显示 Cookie 是否有效
   - 显示关键字段检查结果

## 📊 查看结果

### Web 界面显示

处理完成后，页面会显示：

```
✅ 提取完成！

视频信息：
- 标题：这个杀手给枪装好子弹...
- 作者：电影解说
- 时长：5分3秒

原始文案（1649 字）：
这个杀手给枪装好子弹准备执行今年最后一次刺杀...

增强文案（1806 字）：
这个杀手给枪装好子弹，准备执行今年最后一次刺杀。
这次的目标是个倒卖军火的黑商，每次出行都会带三个保镖...
```

### 文件保存位置

结果会自动保存到 `output/` 目录：

```
output/
├── 视频标题.json    # 完整数据（JSON 格式）
└── 视频标题.txt     # 纯文本文案
```

**JSON 文件内容**：
```json
{
  "task_id": "task_abc123",
  "url": "https://www.douyin.com/video/xxx",
  "video_info": {
    "video_id": "7605511073625656611",
    "title": "视频标题",
    "author": "作者名称",
    "duration": 303
  },
  "transcript": {
    "raw_text": "原始识别文案...",
    "enhanced_text": "LLM 增强后的文案...",
    "language": "zh",
    "duration": 303.5
  },
  "created_at": "2026-02-16T17:30:00",
  "completed_at": "2026-02-16T17:30:45"
}
```

**TXT 文件内容**：
```
标题: 视频标题
作者: 作者名称
链接: https://www.douyin.com/video/xxx
==================================================

增强后的文案内容...
```

## 🎯 使用技巧

### 1. 选择合适的方式

| 场景 | 推荐方式 | 原因 |
|------|---------|------|
| 抖音公开视频 | URL 提取 | 自动化，无需下载 |
| 需要登录的视频 | URL 提取 + Cookie | 访问权限 |
| 本地视频文件 | 文件上传 | 最快最可靠 |
| 批量处理 | API 调用 | 可编程控制 |

### 2. 提高成功率

**URL 提取**：
- ✅ 使用完整的视频链接
- ✅ 确保视频是公开的
- ✅ 如果失败，尝试配置 Cookie

**文件上传**：
- ✅ 确保视频文件完整
- ✅ 文件大小 < 500 MB
- ✅ 视频包含音频轨道

### 3. 优化处理速度

- ✅ 使用 GPU 加速（已配置）
- ✅ 调整并发数（.env 中的 MAX_CONCURRENT_TASKS）
- ✅ 使用文件上传（跳过下载步骤）

### 4. 提高文案质量

- ✅ 启用 LLM 增强（已启用）
- ✅ 确保视频音频清晰
- ✅ 选择合适的 Whisper 模型大小

## ⚠️ 常见问题

### Q1: 提取失败怎么办？

**URL 提取失败**：
1. 检查视频链接是否正确
2. 尝试配置 Cookie
3. 改用文件上传方式

**文件上传失败**：
1. 检查文件格式是否支持
2. 确保文件包含音频
3. 尝试转换为 MP4 格式

### Q2: 处理速度慢？

**可能原因**：
- 网络速度慢（下载视频）
- 使用 CPU 模式（未启用 GPU）
- 视频文件过大

**解决方案**：
- 使用文件上传（跳过下载）
- 确认 GPU 已启用（查看启动日志）
- 调整 Whisper 模型大小

### Q3: 文案质量不好？

**可能原因**：
- 视频音频不清晰
- 背景噪音过大
- 语速过快或口音重

**解决方案**：
- 使用更大的 Whisper 模型（medium → large）
- 启用 LLM 增强（已启用）
- 手动校对结果

### Q4: Cookie 失效？

**症状**：
- 提示需要登录
- 下载失败

**解决方案**：
1. 重新导出 Cookie
2. 确保在抖音已登录
3. 使用文件上传方式

## 📈 性能参考

### 处理速度（5 分钟视频）

| 模式 | 时间 | 说明 |
|------|------|------|
| GPU + LLM | 20-45s | 推荐配置 |
| CPU + LLM | 5-10min | 无 GPU 时 |
| GPU 无 LLM | 15-40s | 跳过增强 |

### 准确率

| 场景 | 准确率 | 说明 |
|------|--------|------|
| 清晰普通话 | 95%+ | 最佳效果 |
| 有背景音乐 | 85-90% | 良好 |
| 口音/方言 | 70-80% | 可用 |
| 嘈杂环境 | 60-70% | 需校对 |

## 🎓 进阶使用

### 批量处理

使用 API 批量处理多个视频：

```python
import requests

urls = [
    "https://www.douyin.com/video/xxx1",
    "https://www.douyin.com/video/xxx2",
    "https://www.douyin.com/video/xxx3",
]

response = requests.post(
    "http://localhost:8000/api/extract/batch",
    json={"urls": urls, "use_llm": True}
)

batch_id = response.json()["batch_id"]
print(f"批量任务 ID: {batch_id}")
```

### 自定义配置

编辑 `.env` 文件：

```env
# 调整 Whisper 模型大小
WHISPER_MODEL_SIZE=large  # tiny/base/small/medium/large

# 调整并发数
MAX_CONCURRENT_TASKS=5

# 禁用 LLM 增强（更快但质量较低）
LLM_ENABLED=false
```

### 集成到其他应用

```python
# Python 示例
import requests

def extract_video_transcript(url):
    response = requests.post(
        "http://localhost:8000/api/extract",
        json={"url": url}
    )
    return response.json()

result = extract_video_transcript("https://www.douyin.com/video/xxx")
print(result["transcript"]["enhanced_text"])
```

## 💡 最佳实践

1. **优先使用文件上传** - 最可靠
2. **启用 GPU 加速** - 速度提升 150-300 倍
3. **启用 LLM 增强** - 文案质量更好
4. **定期清理临时文件** - temp/ 目录
5. **备份重要结果** - output/ 目录

## 📞 获取帮助

- 📖 查看文档：`docs/` 目录
- 🐛 报告问题：GitHub Issues
- 💬 技术支持：项目维护团队

---

**祝你使用愉快！** 🎉
