#!/usr/bin/env python3
"""
GitHub Trending 周报生成器
自动抓取 GitHub 热门项目并生成可视化报告
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

from scraper import GitHubTrendingScraper
from ai_summarizer import AISummarizer
from report_generator import ReportGenerator
from config import DEFAULT_TIME_RANGE, MAX_REPOS


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='GitHub Trending 周报生成器')
    parser.add_argument('--time', '-t', 
                       choices=['daily', 'weekly', 'monthly'],
                       default=DEFAULT_TIME_RANGE,
                       help='时间范围 (default: weekly)')
    parser.add_argument('--lang', '-l', 
                       type=str, 
                       default=None,
                       help='编程语言筛选 (e.g., python, javascript)')
    parser.add_argument('--max', '-m', 
                       type=int, 
                       default=MAX_REPOS,
                       help='最大项目数量')
    parser.add_argument('--ai', '-a',
                       choices=['openai', 'local', 'none'],
                       default=None,
                       help='AI 提供商 (覆盖配置文件)')
    parser.add_argument('--no-html', 
                       action='store_true',
                       help='不生成 HTML 报告')
    parser.add_argument('--output', '-o',
                       type=str,
                       default=None,
                       help='自定义输出目录')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔥 GitHub Trending 周报生成器")
    print("=" * 60)
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 范围: {args.time}")
    print(f"💻 语言: {args.lang or '所有'}")
    print(f"📦 数量: {args.max}")
    print("=" * 60)
    
    # 1. 抓取数据
    print("\n📥 正在抓取 GitHub Trending...")
    scraper = GitHubTrendingScraper()
    repos = scraper.scrape_trending(
        time_range=args.time,
        language=args.lang,
        max_repos=args.max
    )
    
    if not repos:
        print("❌ 未抓取到任何项目，请检查网络连接")
        sys.exit(1)
    
    print(f"✅ 成功抓取 {len(repos)} 个项目")
    
    # 2. AI 总结
    print("\n🤖 生成 AI 总结...")
    summarizer = AISummarizer(provider=args.ai)
    repos = summarizer.batch_summarize(repos, max_summary=10)
    print("✅ AI 总结完成")
    
    # 3. 生成报告
    print("\n📝 生成报告...")
    generator = ReportGenerator()
    
    if args.output:
        generator.output_dir = Path(args.output)
        generator.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Markdown 报告
    md_path = generator.generate_markdown(repos, time_range=args.time)
    
    # HTML 报告
    if not args.no_html:
        html_path = generator.generate_html(repos, time_range=args.time)
    
    print("\n" + "=" * 60)
    print("🎉 报告生成完成！")
    print("=" * 60)
    print(f"📄 Markdown: {md_path}")
    if not args.no_html:
        print(f"🌐 HTML: {html_path}")
    print("\n💡 提示: 使用 --time weekly/monthly 可切换时间范围")
    print("   使用 --lang python 可筛选特定语言")
    print("   使用 --ai openai 启用 AI 智能总结")
    print("=" * 60)


if __name__ == "__main__":
    main()
