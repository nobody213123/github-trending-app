"""
GitHub Trending App 配置文件
"""

import os
from pathlib import Path

# === 路径配置 ===
DESKTOP_PATH = Path.home() / "Desktop"
OUTPUT_DIR = DESKTOP_PATH / "GitHub_Trending_Reports"
DATA_DIR = Path(__file__).parent / "data"
CACHE_DIR = Path(__file__).parent / "cache"

# === 缓存配置 ===
CACHE_EXPIRY_HOURS = 24  # 缓存有效期（小时）

# === 重试配置 ===
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 2  # 重试间隔（秒）

# === 定时任务配置 ===
SCHEDULE_ENABLED = False  # 是否启用定时任务
SCHEDULE_TIME = "09:00"  # 每天执行时间
SCHEDULE_DAY = "monday"  # 每周执行日（weekly模式）

# === GitHub Trending 配置 ===
GITHUB_TRENDING_URL = "https://github.com/trending"
GITHUB_API_BASE = "https://api.github.com"

# 支持的时间范围: daily, weekly, monthly
DEFAULT_TIME_RANGE = "weekly"

# 支持的语言筛选 (None 表示所有语言)
DEFAULT_LANGUAGE = None

# 每次抓取的项目数量
MAX_REPOS = 25

# === AI 配置 ===
# 支持的 AI 提供商: openai, local (Ollama), none
AI_PROVIDER = os.getenv("AI_PROVIDER", "none")

# OpenAI 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Ollama 本地模型配置
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

# === 输出配置 ===
REPORT_FILENAME = "GitHub_Trending_Weekly_{date}.md"
HTML_FILENAME = "GitHub_Trending_Weekly_{date}.html"

# === 报告配置 ===
# 每个分类显示的项目数量
TOP_REPOS_PER_CATEGORY = 5

# 图表配置
CHART_WIDTH = 800
CHART_HEIGHT = 400
