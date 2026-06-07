"""
Internationalization module for bilingual support (Chinese/English)
"""

import json
from pathlib import Path
from typing import Dict, Any

# Default language
DEFAULT_LANG = "zh"

# Translations dictionary
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # App title
    "app_title": {
        "zh": "GitHub Trending 周报生成器",
        "en": "GitHub Trending Weekly Report Generator"
    },
    # Main window
    "generate_report": {
        "zh": "生成报告",
        "en": "Generate Report"
    },
    "stop": {
        "zh": "停止",
        "en": "Stop"
    },
    "open_report": {
        "zh": "打开报告",
        "en": "Open Report"
    },
    "open_folder": {
        "zh": "打开文件夹",
        "en": "Open Folder"
    },
    # Settings
    "settings": {
        "zh": "设置",
        "en": "Settings"
    },
    "time_range": {
        "zh": "时间范围",
        "en": "Time Range"
    },
    "daily": {
        "zh": "每日",
        "en": "Daily"
    },
    "weekly": {
        "zh": "每周",
        "en": "Weekly"
    },
    "monthly": {
        "zh": "每月",
        "en": "Monthly"
    },
    "language": {
        "zh": "编程语言",
        "en": "Programming Language"
    },
    "all_languages": {
        "zh": "所有语言",
        "en": "All Languages"
    },
    "max_repos": {
        "zh": "最大项目数",
        "en": "Max Repositories"
    },
    "ai_provider": {
        "zh": "AI 提供商",
        "en": "AI Provider"
    },
    "none": {
        "zh": "无（基础模式）",
        "en": "None (Basic Mode)"
    },
    "openai": {
        "zh": "OpenAI",
        "en": "OpenAI"
    },
    "local": {
        "zh": "本地 Ollama",
        "en": "Local Ollama"
    },
    "api_key": {
        "zh": "API Key",
        "en": "API Key"
    },
    "output_dir": {
        "zh": "输出目录",
        "en": "Output Directory"
    },
    "browse": {
        "zh": "浏览...",
        "en": "Browse..."
    },
    "language_ui": {
        "zh": "界面语言",
        "en": "Interface Language"
    },
    # Report
    "report_tab": {
        "zh": "报告",
        "en": "Report"
    },
    "preview": {
        "zh": "预览",
        "en": "Preview"
    },
    "no_report": {
        "zh": "暂无报告，请先生成",
        "en": "No report yet, please generate one first"
    },
    # Status
    "status_ready": {
        "zh": "就绪",
        "en": "Ready"
    },
    "status_scraping": {
        "zh": "正在抓取 GitHub Trending...",
        "en": "Scraping GitHub Trending..."
    },
    "status_summarizing": {
        "zh": "正在生成 AI 总结...",
        "en": "Generating AI summaries..."
    },
    "status_generating": {
        "zh": "正在生成报告...",
        "en": "Generating report..."
    },
    "status_done": {
        "zh": "完成！",
        "en": "Done!"
    },
    "status_error": {
        "zh": "错误",
        "en": "Error"
    },
    "status_stopped": {
        "zh": "已停止",
        "en": "Stopped"
    },
    # Messages
    "msg_success": {
        "zh": "报告生成成功！",
        "en": "Report generated successfully!"
    },
    "msg_error": {
        "zh": "生成失败",
        "en": "Generation failed"
    },
    "msg_no_repos": {
        "zh": "未抓取到任何项目",
        "en": "No repositories found"
    },
    # Auto update
    "check_update": {
        "zh": "检查更新",
        "en": "Check for Updates"
    },
    "update_available": {
        "zh": "有新版本可用！",
        "en": "Update available!"
    },
    "update_now": {
        "zh": "立即更新",
        "en": "Update Now"
    },
    "update_later": {
        "zh": "稍后再说",
        "en": "Later"
    },
    "version": {
        "zh": "版本",
        "en": "Version"
    },
    "up_to_date": {
        "zh": "已是最新版本",
        "en": "You're up to date"
    },
    # Log
    "log_title": {
        "zh": "运行日志",
        "en": "Run Log"
    },
    # About
    "about": {
        "zh": "关于",
        "en": "About"
    },
    "about_text": {
        "zh": "GitHub Trending 周报生成器\n自动抓取热门项目并生成可视化报告",
        "en": "GitHub Trending Weekly Report Generator\nAutomatically scrape trending repos and generate visual reports"
    },
    # Schedule
    "schedule": {
        "zh": "定时任务",
        "en": "Schedule"
    },
    "enable_schedule": {
        "zh": "启用定时任务",
        "en": "Enable Scheduler"
    },
    "schedule_type": {
        "zh": "调度类型",
        "en": "Schedule Type"
    },
    "schedule_time": {
        "zh": "执行时间",
        "en": "Run Time"
    },
    "schedule_day": {
        "zh": "执行日",
        "en": "Run Day"
    },
    "scheduled_tasks": {
        "zh": "已计划的任务",
        "en": "Scheduled Tasks"
    },
    "no_scheduled_tasks": {
        "zh": "暂无计划任务",
        "en": "No scheduled tasks"
    },
    "scheduler_started": {
        "zh": "调度器已启动",
        "en": "Scheduler started"
    },
    "scheduler_stopped": {
        "zh": "调度器已停止",
        "en": "Scheduler stopped"
    },
    # Cache
    "cache_info": {
        "zh": "缓存信息",
        "en": "Cache Info"
    },
    "clear_cache": {
        "zh": "清除缓存",
        "en": "Clear Cache"
    },
}


class I18n:
    """Internationalization manager"""
    
    def __init__(self, lang: str = DEFAULT_LANG):
        self.lang = lang
        self._callbacks = []
    
    def set_language(self, lang: str):
        """Set language and notify observers"""
        if lang in ("zh", "en"):
            self.lang = lang
            for callback in self._callbacks:
                callback()
    
    def get_language(self) -> str:
        """Get current language"""
        return self.lang
    
    def t(self, key: str) -> str:
        """Translate a key to current language"""
        if key in TRANSLATIONS:
            return TRANSLATIONS[key].get(self.lang, TRANSLATIONS[key].get("en", key))
        return key
    
    def on_language_change(self, callback):
        """Register a callback for language change"""
        self._callbacks.append(callback)


# Global instance
i18n = I18n()
