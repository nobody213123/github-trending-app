"""
GitHub Trending 数据抓取模块
支持缓存和错误重试
"""

import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

from config import (
    GITHUB_TRENDING_URL, GITHUB_API_BASE, MAX_REPOS,
    MAX_RETRIES, RETRY_DELAY, CACHE_EXPIRY_HOURS
)
from cache import cache


@dataclass
class TrendingRepo:
    """趋势项目数据类"""
    rank: int
    name: str
    full_name: str
    url: str
    description: str
    language: str
    language_color: str
    stars_total: int
    stars_today: int
    forks: int
    built_by: List[str]
    topics: List[str] = None
    ai_summary: str = ""
    
    def __post_init__(self):
        if self.topics is None:
            self.topics = []
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'rank': self.rank,
            'name': self.name,
            'full_name': self.full_name,
            'url': self.url,
            'description': self.description,
            'language': self.language,
            'language_color': self.language_color,
            'stars_total': self.stars_total,
            'stars_today': self.stars_today,
            'forks': self.forks,
            'built_by': self.built_by,
            'topics': self.topics,
            'ai_summary': self.ai_summary
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TrendingRepo':
        """从字典创建"""
        return cls(**data)


class GitHubTrendingScraper:
    """GitHub Trending 抓取器，支持缓存和重试"""
    
    def __init__(self, use_cache: bool = True):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        self.use_cache = use_cache
    
    def scrape_trending(self, 
                        time_range: str = "weekly", 
                        language: str = None,
                        max_repos: int = MAX_REPOS) -> List[TrendingRepo]:
        """
        抓取 GitHub Trending 页面
        
        Args:
            time_range: 时间范围 (daily, weekly, monthly)
            language: 编程语言筛选
            max_repos: 最大抓取数量
            
        Returns:
            TrendingRepo 列表
        """
        # 检查缓存
        if self.use_cache:
            cached_data = cache.get(time_range, language)
            if cached_data:
                print(f"📦 使用缓存数据 ({time_range}, {language or 'all'})")
                repos = [TrendingRepo.from_dict(d) for d in cached_data]
                return repos[:max_repos]
        
        # 缓存未命中，进行抓取
        url = f"{GITHUB_TRENDING_URL}"
        params = {"since": time_range}
        if language:
            url = f"{GITHUB_TRENDING_URL}/{language}"
        
        # 带重试的请求
        response = self._request_with_retry(url, params)
        if not response:
            return []
        
        repos = self._parse_trending_page(response.text, max_repos)
        
        # 存入缓存
        if self.use_cache and repos:
            cache.set(time_range, language, [r.to_dict() for r in repos])
        
        return repos
    
    def _request_with_retry(self, url: str, params: dict = None) -> Optional[requests.Response]:
        """
        带重试的 HTTP 请求
        
        Args:
            url: 请求 URL
            params: 查询参数
            
        Returns:
            Response 对象或 None
        """
        last_error = None
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response
                
            except requests.exceptions.Timeout as e:
                last_error = e
                print(f"⏱️ 请求超时 (尝试 {attempt}/{MAX_RETRIES})")
                
            except requests.exceptions.ConnectionError as e:
                last_error = e
                print(f"🔌 连接失败 (尝试 {attempt}/{MAX_RETRIES})")
                
            except requests.exceptions.HTTPError as e:
                last_error = e
                status_code = e.response.status_code if e.response else 0
                print(f"⚠️ HTTP 错误 {status_code} (尝试 {attempt}/{MAX_RETRIES})")
                
                # 4xx 错误不重试
                if 400 <= status_code < 500:
                    print("❌ 客户端错误，不重试")
                    return None
                    
            except requests.RequestException as e:
                last_error = e
                print(f"❌ 请求失败 (尝试 {attempt}/{MAX_RETRIES})")
            
            # 等待后重试
            if attempt < MAX_RETRIES:
                delay = RETRY_DELAY * attempt  # 指数退避
                print(f"⏳ {delay} 秒后重试...")
                time.sleep(delay)
        
        print(f"❌ 达到最大重试次数，最后错误: {last_error}")
        return None
    
    def _parse_trending_page(self, html: str, max_repos: int) -> List[TrendingRepo]:
        """解析 Trending 页面"""
        soup = BeautifulSoup(html, 'lxml')
        repos = []
        
        # 查找所有项目卡片
        articles = soup.select('article.Box-row')
        
        for idx, article in enumerate(articles[:max_repos], 1):
            try:
                repo = self._parse_repo_card(article, idx)
                if repo:
                    repos.append(repo)
            except Exception as e:
                print(f"解析第 {idx} 个项目失败: {e}")
                continue
        
        return repos
    
    def _parse_repo_card(self, article, rank: int) -> Optional[TrendingRepo]:
        """解析单个项目卡片"""
        # 项目名称
        h2 = article.select_one('h2 a')
        if not h2:
            return None
        
        full_name = h2.get_text(strip=True).replace('\n', ' ').replace('  ', ' ')
        href = h2.get('href', '')
        url = f"https://github.com{href}" if href.startswith('/') else href
        
        # 描述
        desc_elem = article.select_one('p')
        description = desc_elem.get_text(strip=True) if desc_elem else ""
        
        # 编程语言
        lang_elem = article.select_one('[itemprop="programmingLanguage"]')
        language = lang_elem.get_text(strip=True) if lang_elem else "Unknown"
        
        # 语言颜色
        lang_color_elem = article.select_one('span[itemprop="programmingLanguage"] + span')
        language_color = "#f0e68c"  # 默认颜色
        
        # 星标数
        stars_total = self._extract_number(
            article.select_one('a.Link--muted d-inline-block mr-3')
        )
        
        # 今日/本周增长
        stars_today = 0
        today_elem = article.select_one('span.d-inline-block.float-sm-right')
        if today_elem:
            today_text = today_elem.get_text(strip=True)
            stars_today = self._parse_stars_change(today_text)
        
        # Forks
        forks = self._extract_number(
            article.select('a.Link--muted')[-1] if article.select('a.Link--muted') else None
        )
        
        # 贡献者
        built_by = []
        for avatar in article.select('a.avatar-user'):
            username = avatar.get('href', '').strip('/')
            if username:
                built_by.append(username)
        
        return TrendingRepo(
            rank=rank,
            name=full_name.split('/')[-1] if '/' in full_name else full_name,
            full_name=full_name,
            url=url,
            description=description,
            language=language,
            language_color=language_color,
            stars_total=stars_total,
            stars_today=stars_today,
            forks=forks,
            built_by=built_by[:5]  # 只保留前5个
        )
    
    def _extract_number(self, elem) -> int:
        """从元素中提取数字"""
        if not elem:
            return 0
        text = elem.get_text(strip=True)
        return self._parse_number(text)
    
    def _parse_number(self, text: str) -> int:
        """解析数字文本"""
        if not text:
            return 0
        # 移除逗号
        text = text.replace(',', '')
        # 提取数字
        match = re.search(r'(\d+)', text)
        return int(match.group(1)) if match else 0
    
    def _parse_stars_change(self, text: str) -> int:
        """解析星标变化文本"""
        if not text:
            return 0
        # "1,234 stars this week" -> 1234
        return self._parse_number(text)
    
    def get_repo_details(self, full_name: str) -> Dict:
        """通过 GitHub API 获取项目详细信息（带重试）"""
        url = f"{GITHUB_API_BASE}/repos/{full_name}"
        
        response = self._request_with_retry(url)
        if response and response.status_code == 200:
            data = response.json()
            return {
                'topics': data.get('topics', []),
                'description': data.get('description', ''),
                'homepage': data.get('homepage', ''),
                'license': data.get('license', {}).get('spdx_id', 'Unknown') if data.get('license') else 'Unknown',
                'open_issues': data.get('open_issues_count', 0),
                'watchers': data.get('subscribers_count', 0),
                'created_at': data.get('created_at', ''),
                'updated_at': data.get('updated_at', ''),
                'pushed_at': data.get('pushed_at', ''),
            }
        return {}


def scrape_all_languages(time_range: str = "weekly", max_repos: int = 10) -> Dict[str, List[TrendingRepo]]:
    """抓取多个语言的 Trending"""
    languages = ['python', 'javascript', 'typescript', 'go', 'rust', 'java']
    results = {}
    
    scraper = GitHubTrendingScraper()
    for lang in languages:
        repos = scraper.scrape_trending(time_range=time_range, language=lang, max_repos=max_repos)
        if repos:
            results[lang] = repos
    
    return results
