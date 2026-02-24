#!/usr/bin/env python3
"""
Twitter 每日复盘 - 带推送功能
生成复盘报告并通过Telegram发送
"""

import subprocess
import sys
sys.path.insert(0, '/root/.openclaw/workspace/lobster-workspace/scripts')

from twitter_daily_review import parse_daily_log, analyze_tweets, generate_report
from datetime import datetime, timedelta
import os

# Telegram 配置
TELEGRAM_CHAT_ID = "5440939697"

def send_telegram_message(message):
    """通过openclaw命令行发送消息 - 使用 -t 和 -m 参数"""
    # 转义消息中的特殊字符
    escaped_message = message.replace('"', '\\"').replace("'", "\\'")
    
    # 使用正确的参数: -t (target) 和 -m (message)
    cmd = f'openclaw message send -t "{TELEGRAM_CHAT_ID}" -m "{escaped_message[:4000]}"'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[{datetime.now().strftime('%H:%M')}] 消息已发送到 Telegram")
        else:
            print(f"[{datetime.now().strftime('%H:%M')}] 发送失败: {result.stderr}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M')}] 发送异常: {e}")

def main():
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"[{datetime.now().strftime('%H:%M')}] 生成 {yesterday} 的Twitter复盘...")
    
    tweets = parse_daily_log(yesterday)
    
    if tweets:
        analysis = analyze_tweets(tweets)
        report = generate_report(yesterday, analysis)
        
        # 打印到控制台
        print(report)
        
        # 保存到文件
        report_file = f'/root/.openclaw/workspace/memory/twitter_review_{yesterday}.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# Twitter 每日复盘 - {yesterday}\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC\n\n")
            f.write("---\n\n")
            f.write(report)
        
        print(f"[{datetime.now().strftime('%H:%M')}] 报告已保存: {report_file}")
        
        # 简化版消息用于Telegram推送
        summary = f"""📊 **Twitter 每日复盘 - {yesterday}**

📈 **总计**: {analysis['total']} 条推文
🏷️ **主题**: {', '.join(analysis['themes']) if analysis['themes'] else '无明确主题'}

---

**作者分布:**
"""
        for author, tweets in list(analysis['by_author'].items())[:3]:
            name = tweets[0].get('name', author)
            summary += f"• @{author}: {len(tweets)}条\n"
        
        summary += f"""
---

**🔍 市场信号:**
"""
        if '地缘政治' in analysis['themes']:
            summary += "⚠️ 地缘政治风险提及 → 关注国防/能源股\n"
        if 'AI/科技' in analysis['themes']:
            summary += "🤖 AI话题热度高 → 关注科技股\n"
        if '加密货币' in analysis['themes']:
            summary += "₿ 加密市场讨论 → 关注相关资产\n"
        if '股票/投资' in analysis['themes']:
            summary += "📈 投资讨论活跃 → 关注提及个股\n"
        
        summary += f"""
---

**💡 操作建议:**
"""
        if analysis['total'] > 20:
            summary += "• 推文旅密度高，可能有重要事件\n"
        if '地缘政治' in analysis['themes']:
            summary += "• 建议关注VIX波动率指数和黄金\n"
        if 'AI/科技' in analysis['themes']:
            summary += "• 建议关注NVDA、AI板块\n"
        
        summary += f"""
---

📁 完整报告: `memory/twitter_review_{yesterday}.md`
"""
        
        # 发送到Telegram
        send_telegram_message(summary)
        
    else:
        print(f"⚠️ {yesterday} 没有找到推文记录")
        send_telegram_message(f"⚠️ Twitter每日复盘: {yesterday} 没有找到推文记录")

if __name__ == '__main__':
    main()
