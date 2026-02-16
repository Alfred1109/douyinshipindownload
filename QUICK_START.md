# 🚀 快速开始指南

## ✅ 服务已启动！

你的服务已经成功启动并运行在：
```
http://localhost:8000
```

## 📝 三步开始使用

### 第 1 步：打开浏览器

在浏览器中访问：
```
http://localhost:8000
```

### 第 2 步：选择使用方式

你会看到三个标签页：

#### 🔗 方式 A: URL 提取（推荐）

1. 点击"URL 提取"标签
2. 输入抖音视频链接，例如：
   ```
   https://www.douyin.com/video/7605511073625656611
   ```
3. 点击"开始提取"
4. 等待 20-45 秒
5. 查看结果！

#### 📁 方式 B: 文件上传（最可靠）

1. 默认就在"文件上传"标签
2. 点击"选择文件"或拖拽视频文件
3. 自动开始处理
4. 查看结果！

### 第 3 步：查看结果

处理完成后，你会看到：
- ✅ 视频标题和作者
- ✅ 原始识别文案
- ✅ LLM 增强后的文案（带标点、已纠错）

结果也会自动保存到 `output/` 目录。

## 🎯 示例视频

你可以用这个视频测试：
```
https://www.douyin.com/video/7605511073625656611
```

预期结果：
- 视频时长：5 分 3 秒
- 处理时间：约 30 秒
- 文案长度：约 1800 字

## 📊 系统状态

当前配置：
- ✅ ASR 模式：local（本地 Whisper）
- ✅ GPU 加速：已启用（GTX 1060）
- ✅ LLM 增强：已启用（DeepSeek API）
- ✅ 并发任务：3 个

## 🔧 其他功能

### API 文档
访问 Swagger UI 查看完整 API：
```
http://localhost:8000/docs
```

### Cookie 管理
如果需要访问需要登录的视频：
1. 点击"Cookie 管理"标签
2. 按照教程导出 Cookie
3. 粘贴并上传

### 批量处理
使用 API 批量处理多个视频：
```bash
curl -X POST "http://localhost:8000/api/extract/batch" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["url1", "url2", "url3"]}'
```

## 📚 更多帮助

- 详细使用指南：`docs/USER_GUIDE.md`
- 快速参考：`docs/QUICK_REFERENCE.md`
- 架构文档：`docs/ARCHITECTURE.md`

## ⚠️ 注意事项

1. **首次使用**：第一次识别会下载 Whisper 模型（约 1.5 GB）
2. **网络要求**：URL 提取需要访问抖音网站
3. **文件格式**：支持 MP4, AVI, MOV, MKV 等常见格式
4. **处理时间**：5 分钟视频约需 20-45 秒

## 🎉 开始使用吧！

现在就打开浏览器，访问 http://localhost:8000，开始提取你的第一个视频文案！

---

**需要帮助？** 查看 `docs/USER_GUIDE.md` 获取详细说明。
