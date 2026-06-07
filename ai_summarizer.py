"""
AI 智能总结模块
支持 OpenAI API / Ollama 本地模型 / 无 AI 模式
"""

import json
from typing import List, Optional
from config import AI_PROVIDER, OPENAI_API_KEY, OPENAI_MODEL, OLLAMA_BASE_URL, OLLAMA_MODEL


class AISummarizer:
    """AI 总结器"""
    
    def __init__(self, provider: str = None):
        self.provider = provider or AI_PROVIDER
        self._init_client()
    
    def _init_client(self):
        """初始化 AI 客户端"""
        self.client = None
        
        if self.provider == "openai" and OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=OPENAI_API_KEY)
                print(f"✅ 使用 OpenAI 模型: {OPENAI_MODEL}")
            except ImportError:
                print("⚠️  未安装 openai 库，使用无 AI 模式")
                self.provider = "none"
        elif self.provider == "local":
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    base_url=OLLAMA_BASE_URL,
                    api_key="ollama"
                )
                print(f"✅ 使用本地 Ollama 模型: {OLLAMA_MODEL}")
            except ImportError:
                print("⚠️  未安装 openai 库，使用无 AI 模式")
                self.provider = "none"
        else:
            print("ℹ️  使用无 AI 模式（基础描述）")
            self.provider = "none"
    
    def summarize_repo(self, name: str, description: str, language: str, 
                       stars: int, topics: List[str] = None) -> str:
        """
        生成单个项目的中文总结
        
        Args:
            name: 项目名称
            description: 项目描述
            language: 编程语言
            stars: 星标数
            topics: 标签列表
            
        Returns:
            中文总结
        """
        if self.provider == "none" or not self.client:
            return self._basic_summary(name, description, language, stars)
        
        prompt = self._build_summary_prompt(name, description, language, stars, topics)
        
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "你是一个技术文档翻译和总结专家。用简洁易懂的中文解释技术项目，让非技术人员也能理解。"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            elif self.provider == "local":
                response = self.client.chat.completions.create(
                    model=OLLAMA_MODEL,
                    messages=[
                        {"role": "system", "content": "你是一个技术文档翻译和总结专家。用简洁易懂的中文解释技术项目，让非技术人员也能理解。"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200
                )
                return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI 总结失败: {e}")
            return self._basic_summary(name, description, language, stars)
        
        return self._basic_summary(name, description, language, stars)
    
    def _build_summary_prompt(self, name: str, description: str, language: str,
                              stars: int, topics: List[str] = None) -> str:
        """构建总结提示词"""
        topics_str = ", ".join(topics[:5]) if topics else "无"
        
        return f"""请用简洁易懂的中文总结以下 GitHub 开源项目：

项目名称: {name}
英文描述: {description or "无描述"}
编程语言: {language}
星标数: {stars:,}
标签: {topics_str}

要求：
1. 用 2-3 句话解释这个项目是做什么的
2. 说明它能解决什么问题或有什么用途
3. 语言要通俗易懂，避免技术术语
4. 总结要控制在 100 字以内"""
    
    def _basic_summary(self, name: str, description: str, language: str, stars: int) -> str:
        """基础总结（无 AI 模式）"""
        if not description:
            return f"{name} 是一个使用 {language} 编写的开源项目。"
        
        # 简单翻译常见词汇
        summary = description
        summary = summary.replace("A ", "一个 ")
        summary = summary.replace("An ", "一个 ")
        summary = summary.replace("The ", "这个 ")
        summary = summary.replace("for", "用于")
        summary = summary.replace("with", "支持")
        summary = summary.replace("and", "和")
        
        return f"📌 {name}: {summary} (⭐ {stars:,} | {language})"
    
    def batch_summarize(self, repos: list, max_summary: int = 10) -> list:
        """
        批量生成总结
        
        Args:
            repos: TrendingRepo 列表
            max_summary: 最大总结数量
            
        Returns:
            添加了 ai_summary 的 repos 列表
        """
        summarized = []
        for idx, repo in enumerate(repos):
            if idx < max_summary:
                print(f"  📝 正在总结第 {idx+1}/{min(len(repos), max_summary)} 个: {repo.full_name}")
                repo.ai_summary = self.summarize_repo(
                    name=repo.full_name,
                    description=repo.description,
                    language=repo.language,
                    stars=repo.stars_total,
                    topics=repo.topics
                )
            else:
                repo.ai_summary = self._basic_summary(
                    repo.full_name, repo.description, repo.language, repo.stars_total
                )
            summarized.append(repo)
        
        return summarized
