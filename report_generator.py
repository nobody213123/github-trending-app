"""
报告生成模块
生成 Markdown 和 HTML 格式的可视化报告
"""

import os
from datetime import datetime
from typing import List, Dict
from pathlib import Path
from collections import Counter

from scraper import TrendingRepo
from config import OUTPUT_DIR, REPORT_FILENAME, HTML_FILENAME


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_markdown(self, repos: List[TrendingRepo], 
                          time_range: str = "weekly",
                          language_stats: Dict = None) -> str:
        """
        生成 Markdown 报告
        
        Args:
            repos: TrendingRepo 列表
            time_range: 时间范围
            language_stats: 语言统计
            
        Returns:
            Markdown 文件路径
        """
        today = datetime.now().strftime("%Y-%m-%d")
        filename = REPORT_FILENAME.format(date=today)
        filepath = self.output_dir / filename
        
        # 统计数据
        total_stars = sum(r.stars_today for r in repos)
        languages = Counter(r.language for r in repos)
        top_languages = languages.most_common(5)
        
        # 生成内容
        content = self._build_markdown_content(
            repos, today, time_range, total_stars, top_languages, language_stats
        )
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Markdown 报告已保存: {filepath}")
        return str(filepath)
    
    def _build_markdown_content(self, repos: List[TrendingRepo], date: str,
                                time_range: str, total_stars: int,
                                top_languages: List, language_stats: Dict) -> str:
        """构建 Markdown 内容"""
        
        # 时间范围中文映射
        time_range_cn = {
            'daily': '今日',
            'weekly': '本周',
            'monthly': '本月'
        }.get(time_range, time_range)
        
        content = f"""# 🔥 GitHub 热门项目趋势报告

**日期：** {date}  
**时间范围：** {time_range_cn}  
**项目数量：** {len(repos)} 个

---

## 📊 总览

| 指标 | 数值 |
|------|------|
| 🔥 热门项目数 | {len(repos)} |
| ⭐ 今日总增长 | +{total_stars:,} |
| 📈 平均增长 | +{total_stars // len(repos) if repos else 0:,} |

---

## 🏆 热门项目排行榜

"""
        
        # 项目表格
        content += "| 排名 | 项目 | ⭐ 星标 | 📈 增长 | 📝 说明 |\n"
        content += "|:---:|------|-------:|-------:|---------|\n"
        
        for repo in repos[:15]:
            desc = repo.description[:60] + "..." if len(repo.description) > 60 else repo.description
            content += f"| {repo.rank} | **[{repo.name}]({repo.url})** | {repo.stars_total:,} | +{repo.stars_today:,} | {desc} |\n"
        
        content += "\n---\n\n"
        
        # 语言分布
        content += "## 📈 语言分布\n\n"
        content += "```\n"
        for lang, count in top_languages:
            bar = "█" * (count * 4)
            content += f"{lang:15} {bar} {count} 个\n"
        content += "```\n\n"
        
        # 增长趋势图
        content += "## 📈 今日增长 Top 5\n\n"
        content += "```\n"
        sorted_repos = sorted(repos, key=lambda x: x.stars_today, reverse=True)
        for repo in sorted_repos[:5]:
            bar = "█" * min(repo.stars_today // 10, 40)
            content += f"{repo.name[:20]:20} {bar} +{repo.stars_today:,}\n"
        content += "```\n\n"
        
        # 项目详情
        content += "---\n\n"
        content += "## 📋 项目详情\n\n"
        
        for repo in repos[:10]:
            content += f"### {repo.rank}. [{repo.name}]({repo.url})\n\n"
            content += f"**语言：** {repo.language} | **星标：** {repo.stars_total:,} | **增长：** +{repo.stars_today:,}\n\n"
            content += f"**简介：** {repo.ai_summary or repo.description}\n\n"
            if repo.topics:
                content += f"**标签：** {', '.join(repo.topics[:5])}\n\n"
            content += "---\n\n"
        
        # 底部统计
        content += f"""
## 📊 详细统计

### 语言分布表

| 语言 | 项目数 | 占比 |
|------|-------:|-----:|
"""
        for lang, count in top_languages:
            percentage = count / len(repos) * 100 if repos else 0
            content += f"| {lang} | {count} | {percentage:.1f}% |\n"
        
        content += f"""

---

*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*数据来源：GitHub Trending*
"""
        
        return content
    
    def generate_html(self, repos: List[TrendingRepo], 
                      time_range: str = "weekly") -> str:
        """
        生成 HTML 可视化报告
        
        Args:
            repos: TrendingRepo 列表
            time_range: 时间范围
            
        Returns:
            HTML 文件路径
        """
        today = datetime.now().strftime("%Y-%m-%d")
        filename = HTML_FILENAME.format(date=today)
        filepath = self.output_dir / filename
        
        # 统计数据
        languages = Counter(r.language for r in repos)
        top_languages = languages.most_common(8)
        sorted_repos = sorted(repos, key=lambda x: x.stars_today, reverse=True)[:10]
        
        # 生成 HTML
        html = self._build_html_content(repos, today, time_range, 
                                         top_languages, sorted_repos)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ HTML 报告已保存: {filepath}")
        return str(filepath)
    
    def _build_html_content(self, repos, date, time_range, 
                            top_languages, sorted_repos) -> str:
        """构建 HTML 内容"""
        
        time_range_cn = {
            'daily': '今日',
            'weekly': '本周',
            'monthly': '本月'
        }.get(time_range, time_range)
        
        total_stars = sum(r.stars_today for r in repos)
        avg_stars = total_stars // len(repos) if repos else 0
        
        # 准备图表数据
        lang_labels = [l[0] for l in top_languages]
        lang_counts = [l[1] for l in top_languages]
        repo_names = [r.name[:15] for r in sorted_repos]
        repo_stars = [r.stars_today for r in sorted_repos]
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub 热门项目趋势报告 - {date}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        .header h1 {{ color: #333; font-size: 28px; margin-bottom: 10px; }}
        .header p {{ color: #666; font-size: 14px; }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}
        .stat-card .number {{ font-size: 36px; font-weight: bold; color: #667eea; }}
        .stat-card .label {{ color: #666; font-size: 14px; margin-top: 5px; }}
        .chart-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .chart-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}
        .chart-card h3 {{ color: #333; margin-bottom: 15px; font-size: 18px; }}
        .repo-list {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}
        .repo-item {{
            display: flex;
            align-items: center;
            padding: 15px;
            border-bottom: 1px solid #eee;
            transition: background 0.2s;
        }}
        .repo-item:hover {{ background: #f8f9fa; }}
        .repo-item:last-child {{ border-bottom: none; }}
        .repo-rank {{
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            margin-right: 15px;
        }}
        .repo-info {{ flex: 1; }}
        .repo-name {{ font-weight: 600; color: #333; text-decoration: none; }}
        .repo-name:hover {{ color: #667eea; }}
        .repo-desc {{ color: #666; font-size: 14px; margin-top: 5px; }}
        .repo-stats {{ display: flex; gap: 20px; }}
        .repo-stat {{ text-align: center; }}
        .repo-stat .value {{ font-weight: 600; color: #333; }}
        .repo-stat .label {{ font-size: 12px; color: #999; }}
        .footer {{
            text-align: center;
            color: white;
            padding: 20px;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 GitHub 热门项目趋势报告</h1>
            <p>📅 {date} | ⏱️ {time_range_cn} | 📊 {len(repos)} 个项目</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="number">{len(repos)}</div>
                <div class="label">🔥 热门项目</div>
            </div>
            <div class="stat-card">
                <div class="number">+{total_stars:,}</div>
                <div class="label">📈 总增长</div>
            </div>
            <div class="stat-card">
                <div class="number">+{avg_stars:,}</div>
                <div class="label">📊 平均增长</div>
            </div>
            <div class="stat-card">
                <div class="number">{len(top_languages)}</div>
                <div class="label">💻 编程语言</div>
            </div>
        </div>
        
        <div class="chart-row">
            <div class="chart-card">
                <h3>📈 语言分布</h3>
                <canvas id="langChart"></canvas>
            </div>
            <div class="chart-card">
                <h3>🚀 增长 Top 10</h3>
                <canvas id="starsChart"></canvas>
            </div>
        </div>
        
        <div class="repo-list">
            <h3 style="margin-bottom: 15px; color: #333;">🏆 热门项目排行榜</h3>
"""
        
        # 项目列表
        for repo in repos[:15]:
            desc = repo.description[:80] + "..." if len(repo.description) > 80 else repo.description
            html += f"""
            <div class="repo-item">
                <div class="repo-rank">{repo.rank}</div>
                <div class="repo-info">
                    <a href="{repo.url}" class="repo-name" target="_blank">{repo.full_name}</a>
                    <div class="repo-desc">{desc}</div>
                </div>
                <div class="repo-stats">
                    <div class="repo-stat">
                        <div class="value">⭐ {repo.stars_total:,}</div>
                        <div class="label">星标</div>
                    </div>
                    <div class="repo-stat">
                        <div class="value" style="color: #28a745;">+{repo.stars_today:,}</div>
                        <div class="label">增长</div>
                    </div>
                </div>
            </div>
"""
        
        html += f"""
        </div>
        
        <div class="footer">
            <p>报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>数据来源：GitHub Trending</p>
        </div>
    </div>
    
    <script>
        // 语言分布饼图
        new Chart(document.getElementById('langChart'), {{
            type: 'doughnut',
            data: {{
                labels: {lang_labels},
                datasets: [{{
                    data: {lang_counts},
                    backgroundColor: [
                        '#667eea', '#764ba2', '#f093fb', '#f5576c',
                        '#4facfe', '#00f2fe', '#43e97b', '#fa709a'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'right' }}
                }}
            }}
        }});
        
        // 增长柱状图
        new Chart(document.getElementById('starsChart'), {{
            type: 'bar',
            data: {{
                labels: {repo_names},
                datasets: [{{
                    label: '星标增长',
                    data: {repo_stars},
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                indexAxis: 'y',
                scales: {{
                    x: {{ beginAtZero: true }}
                }},
                plugins: {{
                    legend: {{ display: false }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        return html
