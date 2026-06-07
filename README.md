# 🔥 GitHub Trending 周报生成器

自动抓取 GitHub 热门项目并生成可视化周报。

## ✨ 功能特点

- 📊 **自动抓取** - 每周自动获取 GitHub Trending 项目
- 🤖 **AI 总结** - 支持 OpenAI / Ollama 本地模型
- 📈 **可视化** - 生成带图表的 HTML 报告
- 📄 **多格式** - Markdown + HTML 双格式输出
- ⏰ **内置定时任务** - 无需 cron，应用内设置定时执行
- 💾 **智能缓存** - 24 小时缓存，避免重复抓取
- 🔄 **错误重试** - 网络失败自动重试 3 次（指数退避）
- 🖥️ **图形界面** - 支持 Windows / macOS / Linux
- 🌐 **双语支持** - 中文 / English 完整界面切换
- 🔄 **自动更新** - 检查 GitHub Releases 获取更新
- ✅ **单元测试** - 16 个测试用例，确保代码质量

## 🚀 快速开始

### 方式一：下载可执行文件（推荐）

前往 [Releases](https://github.com/nobody213123/github-trending-app/releases) 下载最新版本：

| 平台 | 文件 |
|------|------|
| Windows | `GitHubTrending.exe` |
| macOS | `GitHubTrending-macOS.dmg` |
| Linux | `GitHubTrending-Linux.AppImage` |

### 方式二：从源码运行

```bash
# 克隆仓库
git clone https://github.com/nobody213123/github-trending-app.git
cd github-trending-app

# 安装依赖
pip install -r requirements.txt

# 运行 GUI 版本
python gui_app.py

# 或运行命令行版本
python main.py
```

## 📖 使用说明

### GUI 版本

#### 1. 生成报告

1. 打开「生成报告」标签页
2. 选择时间范围：
   - **daily** - 每日趋势
   - **weekly** - 每周趋势（推荐）
   - **monthly** - 每月趋势
3. 可选：输入编程语言筛选（如 `python`, `javascript`）
4. 拖动滑块设置最大项目数量（5-50）
5. 点击「生成报告」按钮

#### 2. 查看报告

- 切换到「报告」标签页
- 在预览区查看 Markdown 内容
- 点击「打开报告」在浏览器查看 HTML 版本（有图表）
- 点击「打开文件夹」查看报告保存位置

#### 3. 设置

- 切换到「设置」标签页
- 配置 AI 提供商：
  - **none** - 无 AI（免费基础模式）
  - **openai** - 使用 OpenAI API（需要 API Key）
  - **local** - 使用本地 Ollama 模型
- 设置 API Key（如果使用 OpenAI）
- 设置输出目录（默认在桌面）

#### 4. 定时任务

- 切换到「定时任务」标签页
- 打开「启用定时任务」开关
- 选择调度类型：daily / weekly / monthly
- 设置执行时间（如 `09:00`）
- 如果选 weekly，还要选择星期几

#### 5. 切换语言

- 点击右上角 **ZH** 切换中文
- 点击右上角 **EN** 切换英文
- 所有界面元素会自动更新

### 命令行版本

```bash
# 运行（基础模式）
python main.py

# 指定时间范围
python main.py --time weekly

# 筛选语言
python main.py --lang python

# 启用 AI 总结
python main.py --ai openai

# 自定义输出目录
python main.py --output ~/Desktop/Reports
```

## 🤖 AI 配置

### 使用 OpenAI

```bash
export AI_PROVIDER=openai
export OPENAI_API_KEY=your-api-key
export OPENAI_MODEL=gpt-4o-mini
python main.py --ai openai
```

### 使用本地 Ollama

```bash
# 先安装 Ollama: https://ollama.ai
ollama pull qwen2.5:7b

export AI_PROVIDER=local
export OLLAMA_MODEL=qwen2.5:7b
python main.py --ai local
```

## 📁 项目结构

```
github-trending-app/
├── gui_app.py              # GUI 入口
├── main.py                 # 命令行入口
├── scraper.py              # 数据抓取（支持缓存和重试）
├── ai_summarizer.py        # AI 总结
├── report_generator.py     # 报告生成
├── config.py               # 配置文件
├── i18n.py                 # 国际化（中英文）
├── updater.py              # 自动更新
├── cache.py                # 缓存管理
├── scheduler.py            # 内置定时任务调度器
├── gui_components/         # GUI 组件
│   ├── __init__.py
│   └── main_window.py      # 主窗口
├── assets/                 # 图标等资源
│   └── icon.svg
├── tests/                  # 单元测试
│   └── test_app.py
├── build_macos.sh          # macOS 打包脚本
├── build_windows.bat       # Windows 打包脚本
├── build_linux.sh          # Linux 打包脚本
├── .github/workflows/      # CI/CD 自动打包
│   └── build.yml
├── requirements.txt        # 依赖列表
└── README.md               # 使用说明
```

## 🔧 依赖

- Python 3.8+
- requests
- beautifulsoup4
- lxml
- openai (可选)
- jinja2
- customtkinter

## 🧪 运行测试

```bash
# 安装测试依赖
pip install pytest

# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_app.py::TestCacheManager -v
```

## 📊 示例输出

### Markdown

```markdown
# 🔥 GitHub 热门项目趋势报告

**日期：** 2026-06-07
**时间范围：** 本周
**项目数量：** 15 个

---

## 📊 总览

| 指标 | 数值 |
|------|------|
| 🔥 热门项目数 | 15 |
| ⭐ 今日总增长 | +72,282 |
| 📈 平均增长 | +4,818 |

---

## 🏆 热门项目排行榜

| 排名 | 项目 | ⭐ 星标 | 📈 增长 | 📝 说明 |
|:---:|------|-------:|-------:|---------|
| 1 | project/name | 12,345 | +567 | 项目说明... |
```

### HTML

生成带 Chart.js 图表的可视化网页，包含：
- 📊 语言分布饼图
- 📈 增长 Top 10 柱状图
- 📋 项目详情列表

## 🔧 打包为可执行文件

### macOS

```bash
chmod +x build_macos.sh
./build_macos.sh
# 输出: dist/GitHubTrending.app
```

### Windows

```bash
build_windows.bat
# 输出: dist\GitHubTrending.exe
```

### Linux

```bash
chmod +x build_linux.sh
./build_linux.sh
# 输出: dist/GitHubTrending
```

## 🤝 致谢

灵感来源：
- [bonfy/github-trending](https://github.com/bonfy/github-trending)
- [deariary/github-weekly-reporter](https://github.com/deariary/github-weekly-reporter)

## 📄 License

MIT
