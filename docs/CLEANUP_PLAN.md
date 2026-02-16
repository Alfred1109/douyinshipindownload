# 项目清理计划

## 📋 冗余文件分析

### 🗑️ 建议删除的文件

#### 1. 旧的测试脚本（功能已被 test_playwright.py 覆盖）
- ❌ `test_browser_simple.py` - 简单浏览器测试，功能已包含在 test_playwright.py
- ❌ `test_download_only.py` - 只测试下载，功能已包含在 test_playwright.py
- ❌ `whisper_simple.py` - 简化版识别，功能已包含在 test_whisper_gpu.py

#### 2. 旧的提取脚本（功能已被 Web API 和 pipeline 覆盖）
- ❌ `extract_from_file.py` - 从文件提取，现在用 Web 界面的文件上传
- ❌ `extract_video.py` - 从 URL 提取，现在用 Web 界面的 URL 提取
- ❌ `quick_extract.py` - 快速提取，功能已被 pipeline 覆盖

#### 3. 失败的实验性脚本
- ❌ `test_stream_mode.py` - 流式模式测试，已证明不可行

### ✅ 保留的文件

#### 核心功能脚本
- ✅ `download_whisper_model.py` - 下载 Whisper 模型（首次安装需要）
- ✅ `install_playwright.bat` - 安装 Playwright（首次安装需要）
- ✅ `start_with_check.bat` - Windows 启动脚本
- ✅ `start.sh` - Linux/macOS 启动脚本
- ✅ `stop.sh` - 停止脚本

#### 测试脚本（保留用于验证）
- ✅ `test_playwright.py` - Playwright 完整测试（推荐）
- ✅ `test_whisper_gpu.py` - GPU 加速测试（推荐）
- ✅ `test_whisper_direct.py` - Whisper 直接测试
- ✅ `test_llm_enhance.py` - LLM 增强测试

#### 文档文件
- ✅ `README.md` - 项目说明
- ✅ `ARCHITECTURE.md` - 架构文档
- ✅ `TECH_STACK.md` - 技术栈说明
- ✅ `QUICK_REFERENCE.md` - 快速参考
- ✅ `SYSTEM_OVERVIEW.md` - 系统总览
- ✅ `OPTIMIZATION_NOTES.md` - 优化说明
- ✅ `PLAYWRIGHT_方案.md` - Playwright 详解

#### 配置文件
- ✅ `.env` - 环境配置（不在 git 中）
- ✅ `env.example` - 配置示例
- ✅ `.gitignore` - Git 忽略规则
- ✅ `requirements.txt` - Python 依赖

### 📊 清理统计

**删除文件**: 7 个
- 3 个旧测试脚本
- 3 个旧提取脚本
- 1 个失败实验脚本

**保留文件**: 
- 5 个核心脚本
- 4 个测试脚本
- 7 个文档文件
- 4 个配置文件

**预计节省空间**: ~15 KB（代码文件较小）

## 🔍 代码冗余检查

### app/services/ 目录

#### ✅ 无冗余
所有服务都在使用：
- `audio_extractor.py` - 音频提取
- `browser_fetcher.py` - 浏览器抓取
- `douyin_parser.py` - 抖音解析
- `llm_enhancer.py` - LLM 增强
- `pipeline.py` - 流水线编排
- `transcriber.py` - 语音识别

### app/api/ 目录

#### ✅ 无冗余
所有路由都在使用：
- `routes.py` - 主路由
- `upload_routes.py` - 文件上传
- `cookie_routes.py` - Cookie 管理

### app/utils/ 目录

#### ✅ 无冗余
- `helpers.py` - 工具函数
- `cookie_helper.py` - Cookie 处理

### app/models/ 目录

#### ✅ 无冗余
- `schemas.py` - 数据模型

## 🎯 清理建议

### 立即删除（安全）
这些文件功能已被替代，可以安全删除：
```bash
rm test_browser_simple.py
rm test_download_only.py
rm whisper_simple.py
rm extract_from_file.py
rm extract_video.py
rm quick_extract.py
rm test_stream_mode.py
```

### 可选删除（根据需要）
如果不需要测试，可以删除：
```bash
# 保留 test_playwright.py 和 test_whisper_gpu.py 即可
rm test_whisper_direct.py
rm test_llm_enhance.py
```

### 不建议删除
- 所有文档文件（提供重要信息）
- 核心脚本（安装和启动需要）
- 推荐的测试脚本（验证功能）

## 📝 清理后的项目结构

```
shipindownload/
├── app/                          # 应用代码（无冗余）
│   ├── api/                      # API 路由
│   ├── models/                   # 数据模型
│   ├── services/                 # 核心服务
│   └── utils/                    # 工具函数
├── web/                          # Web 界面
├── temp/                         # 临时文件
├── output/                       # 输出结果
├── docs/                         # 文档（建议创建）
│   ├── ARCHITECTURE.md
│   ├── TECH_STACK.md
│   ├── QUICK_REFERENCE.md
│   ├── SYSTEM_OVERVIEW.md
│   ├── OPTIMIZATION_NOTES.md
│   └── PLAYWRIGHT_方案.md
├── scripts/                      # 脚本（建议创建）
│   ├── download_whisper_model.py
│   ├── install_playwright.bat
│   ├── start_with_check.bat
│   ├── start.sh
│   └── stop.sh
├── tests/                        # 测试（建议创建）
│   ├── test_playwright.py
│   ├── test_whisper_gpu.py
│   ├── test_whisper_direct.py
│   └── test_llm_enhance.py
├── .env                          # 环境配置
├── .gitignore                    # Git 忽略
├── env.example                   # 配置示例
├── README.md                     # 项目说明
└── requirements.txt              # Python 依赖
```

## 🔄 可选的重构建议

### 1. 整理文档到 docs/ 目录
```bash
mkdir docs
mv ARCHITECTURE.md docs/
mv TECH_STACK.md docs/
mv QUICK_REFERENCE.md docs/
mv SYSTEM_OVERVIEW.md docs/
mv OPTIMIZATION_NOTES.md docs/
mv PLAYWRIGHT_方案.md docs/
```

### 2. 整理脚本到 scripts/ 目录
```bash
mkdir scripts
mv download_whisper_model.py scripts/
mv install_playwright.bat scripts/
mv start_with_check.bat scripts/
mv start.sh scripts/
mv stop.sh scripts/
```

### 3. 整理测试到 tests/ 目录
```bash
mkdir tests
mv test_*.py tests/
```

### 4. 更新 README.md 中的路径引用
```markdown
# 文档
- [架构文档](docs/ARCHITECTURE.md)
- [技术栈](docs/TECH_STACK.md)

# 脚本
python scripts/download_whisper_model.py
scripts/start_with_check.bat
```

## ⚠️ 注意事项

### 删除前备份
```bash
# 创建备份
mkdir backup
cp test_*.py backup/
cp extract_*.py backup/
cp quick_extract.py backup/
cp whisper_simple.py backup/
```

### Git 提交
```bash
git rm test_browser_simple.py test_download_only.py whisper_simple.py
git rm extract_from_file.py extract_video.py quick_extract.py
git rm test_stream_mode.py
git commit -m "清理: 删除冗余测试和提取脚本"
```

## 📈 清理收益

### 代码质量
- ✅ 减少维护负担
- ✅ 降低混淆风险
- ✅ 提高项目清晰度

### 开发体验
- ✅ 更容易找到正确的文件
- ✅ 减少选择困难
- ✅ 新人更容易上手

### 项目管理
- ✅ 更清晰的项目结构
- ✅ 更好的文档组织
- ✅ 更专业的印象
