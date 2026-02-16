# 快速参考手册

## 🚀 一分钟启动

```bash
# 1. 安装依赖
pip install -r requirements.txt
playwright install chromium

# 2. 配置环境
cp env.example .env
# 编辑 .env 文件，填入 API Key

# 3. 启动服务
start_with_check.bat  # Windows
./start.sh            # Linux/macOS

# 4. 访问界面
http://localhost:8000
```

## 📋 核心命令

### 启动服务
```bash
# 开发模式（自动重载）
python -m uvicorn app.main:app --reload

# 生产模式
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 测试功能
```bash
# 测试 Playwright
python test_playwright.py

# 测试 Whisper GPU
python test_whisper_gpu.py

# 测试 LLM 增强
python test_llm_enhance.py
```

### 下载模型
```bash
# 下载 Whisper 模型
python download_whisper_model.py
```

## 🔧 配置速查

### 必需配置
```env
# GPU 加速（推荐）
WHISPER_DEVICE=cuda
WHISPER_COMPUTE_TYPE=float32

# LLM 增强
LLM_ENABLED=true
ARK_API_KEY=your-api-key-here
```

### 可选配置
```env
# 模型大小（tiny/base/small/medium/large）
WHISPER_MODEL_SIZE=medium

# 并发任务数
MAX_CONCURRENT_TASKS=3

# 调试模式
DEBUG=false
```

## 📡 API 速查

### 提取视频文案
```bash
curl -X POST "http://localhost:8000/api/extract" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.douyin.com/video/xxx"}'
```

### 上传视频文件
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@video.mp4"
```

### 查询任务状态
```bash
curl "http://localhost:8000/api/task/{task_id}"
```

### 批量处理
```bash
curl -X POST "http://localhost:8000/api/batch" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["url1", "url2"]}'
```

## 🗂️ 目录结构

```
shipindownload/
├── app/                    # 应用代码
│   ├── api/               # API 路由
│   ├── services/          # 核心服务
│   ├── models/            # 数据模型
│   └── utils/             # 工具函数
├── web/                   # Web 界面
├── temp/                  # 临时文件
├── output/                # 输出结果
└── .env                   # 配置文件
```

## 🔄 处理流程

```
URL/文件 → 下载视频 → 提取音频 → 语音识别 → LLM增强 → 保存结果
  (10s)     (20s)      (3s)       (2s)       (5s)      (1s)
```

## 🎯 使用场景

### 场景 1: 单个视频提取
1. 打开 http://localhost:8000
2. 输入抖音视频链接
3. 点击"开始提取"
4. 等待处理完成
5. 查看结果

### 场景 2: 批量处理
1. 准备视频链接列表
2. 使用批量 API
3. 监控任务进度
4. 下载所有结果

### 场景 3: 本地文件
1. 切换到"文件上传"
2. 选择视频文件
3. 自动处理
4. 获取文案

## 🐛 常见问题

### Q: Playwright 启动失败？
```bash
# 重新安装浏览器
playwright install chromium --force
```

### Q: CUDA 不可用？
```bash
# 检查 CUDA
python -c "import torch; print(torch.cuda.is_available())"

# 安装 CUDA 版本
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### Q: Cookie 失效？
- 方案 1: 重新导出 Cookie
- 方案 2: 使用文件上传（推荐）

### Q: LLM API 错误？
- 检查 API Key 是否正确
- 验证网络连接
- 查看 API 配额

### Q: 内存不足？
- 减小 Whisper 模型: `WHISPER_MODEL_SIZE=small`
- 降低并发数: `MAX_CONCURRENT_TASKS=1`
- 使用 CPU 模式: `WHISPER_DEVICE=cpu`

## 📊 性能参考

### 硬件配置
- CPU: Intel i5 或更高
- GPU: GTX 1060 6GB（可选）
- 内存: 8GB+
- 磁盘: 10GB 可用空间

### 处理速度
| 视频时长 | CPU 模式 | GPU 模式 |
|---------|---------|---------|
| 1 分钟  | 60 秒   | 5 秒    |
| 5 分钟  | 300 秒  | 20 秒   |
| 10 分钟 | 600 秒  | 40 秒   |

### 资源占用
- CPU: 10-30%
- GPU: 50-80%（识别时）
- 内存: 2-4 GB
- 磁盘: < 100 MB（临时）

## 🔒 安全建议

### 生产环境
- [ ] 修改默认端口
- [ ] 启用 HTTPS
- [ ] 设置访问限制
- [ ] 定期更新依赖
- [ ] 备份配置文件

### API Key 管理
- [ ] 不要提交到 Git
- [ ] 使用环境变量
- [ ] 定期轮换
- [ ] 限制权限

## 📈 监控指标

### 关键指标
- 任务成功率: > 95%
- 平均处理时间: < 60 秒
- API 响应时间: < 2 秒
- 错误率: < 5%

### 日志位置
- 应用日志: 控制台输出
- 错误日志: 控制台输出
- 访问日志: Uvicorn 日志

## 🔄 更新升级

### 更新依赖
```bash
pip install -r requirements.txt --upgrade
```

### 更新 Playwright
```bash
playwright install chromium
```

### 更新 Whisper 模型
```bash
python download_whisper_model.py
```

## 📞 获取帮助

### 文档
- [README.md](README.md) - 快速开始
- [ARCHITECTURE.md](ARCHITECTURE.md) - 架构详解
- [TECH_STACK.md](TECH_STACK.md) - 技术栈
- [PLAYWRIGHT_方案.md](PLAYWRIGHT_方案.md) - Playwright 说明

### API 文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 社区
- GitHub Issues
- 技术论坛
- 邮件支持

## 🎓 学习路径

### 初级
1. 阅读 README.md
2. 运行示例代码
3. 尝试单个视频提取
4. 了解基本配置

### 中级
1. 阅读 ARCHITECTURE.md
2. 理解处理流程
3. 自定义配置
4. 批量处理

### 高级
1. 阅读源代码
2. 扩展新功能
3. 性能优化
4. 部署生产

## 🛠️ 开发工具

### 推荐 IDE
- VS Code
- PyCharm
- Cursor

### 推荐插件
- Python
- Pylance
- REST Client
- GitLens

### 调试技巧
```python
# 启用调试日志
DEBUG=true

# 单步调试
import pdb; pdb.set_trace()

# 性能分析
import cProfile
```

## 📦 部署清单

### 部署前检查
- [ ] 测试所有功能
- [ ] 更新文档
- [ ] 备份数据
- [ ] 检查依赖版本
- [ ] 配置环境变量

### 部署步骤
1. 克隆代码
2. 安装依赖
3. 配置环境
4. 启动服务
5. 验证功能

### 部署后验证
- [ ] API 可访问
- [ ] 功能正常
- [ ] 性能达标
- [ ] 日志正常
- [ ] 监控就绪

## 🎯 最佳实践

### 开发
- 使用虚拟环境
- 遵循代码规范
- 编写单元测试
- 及时提交代码

### 运维
- 定期备份
- 监控资源
- 查看日志
- 更新依赖

### 使用
- 优先文件上传
- 合理设置并发
- 监控任务状态
- 及时清理临时文件

## 📝 备忘录

### 端口
- Web 服务: 8000
- API 文档: 8000/docs

### 路径
- 配置: `.env`
- 临时: `temp/`
- 输出: `output/`
- 日志: 控制台

### 命令
- 启动: `start_with_check.bat`
- 停止: `Ctrl+C`
- 测试: `python test_*.py`

### 链接
- 主页: http://localhost:8000
- API: http://localhost:8000/docs
- Cookie: http://localhost:8000/#cookie
