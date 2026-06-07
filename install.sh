#!/bin/bash
# GitHub Trending 周报生成器 - 快速安装脚本

set -e

echo "🔧 GitHub Trending 周报生成器 - 安装"
echo "====================================="

# 检查 Python 版本
python3 --version || { echo "❌ 需要 Python 3.8+"; exit 1; }

# 创建虚拟环境
echo "📦 创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -r requirements.txt

echo ""
echo "✅ 安装完成！"
echo ""
echo "🚀 使用方法:"
echo "   source venv/bin/activate"
echo "   python main.py --time weekly"
echo ""
echo "💡 可选参数:"
echo "   --time daily/weekly/monthly  时间范围"
echo "   --lang python               筛选语言"
echo "   --ai openai/local/none      AI 模式"
echo "   --max 25                    项目数量"
