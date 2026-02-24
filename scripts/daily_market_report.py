#!/usr/bin/env python3
"""
每日市场早报 - 合并 Twitter 复盘 + FRED 宏观数据
每天早上8:30发送
"""

import subprocess
import sys
sys.path.insert(0, '/root/.openclaw/workspace/lobster-workspace/scripts')
sys.path.insert(0, '/root/.openclaw/workspace/learning/fund_manager')

from twitter_daily_review import parse_daily_log, analyze_tweets
from fred_client import FREDClient
from datetime import datetime, timedelta

TELEGRAM_CHAT_ID = "5440939697"

def send_message(message):
    """发送消息到Telegram"""
    escaped = message.replace('"', '\\"').replace("'", "\\'")
    cmd = f'openclaw message send -t "{TELEGRAM_CHAT_ID}" -m "{escaped[:4000]}"'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[{datetime.now().strftime('%H:%M')}] 消息已发送")
        else:
            print(f"发送失败: {result.stderr}")
    except Exception as e:
        print(f"发送异常: {e}")

def get_fred_summary():
    """获取FRED宏观数据摘要"""
    try:
        client = FREDClient()
        
        # 获取关键指标最新值
        indicators = {
            "fed_funds_rate": "联邦基金利率",
            "treasury_10y": "10年期国债",
            "treasury_2y": "2年期国债",
            "sp500": "标普500",
            "vix": "VIX波动率",
            "unemployment": "失业率",
        }
        
        lines = ["📊 **美联储宏观数据**"]
        
        for key, name in indicators.items():
            try:
                data = client.get_series(key, limit=2)
                if data and len(data) > 0:
                    latest = data[0]
                    value = latest.get('value', 'N/A')
                    date = latest.get('date', '')
                    lines.append(f"• {name}: {value} ({date})")
            except:
                pass
        
        return "\n".join(lines)
    except Exception as e:
        return f"📊 **美联储宏观数据**\n⚠️ 获取失败: {str(e)[:50]}"

def get_twitter_summary():
    """获取Twitter复盘摘要"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    tweets = parse_daily_log(yesterday)
    if not tweets:
        return f"📱 **Twitter 复盘 ({yesterday})**\n⚠️ 无推文记录"
    
    analysis = analyze_tweets(tweets)
    
    lines = [
        f"📱 **Twitter 复盘 ({yesterday})**",
        f"📈 总计: {analysis['total']} 条推文",
        f"🏷️ 主题: {', '.join(analysis['themes']) if analysis['themes'] else '无'}",
        "",
        "**作者分布:**"
    ]
    
    for author, tweets in list(analysis['by_author'].items())[:3]:
        lines.append(f"• @{author}: {len(tweets)}条")
    
    lines.append("")
    lines.append("**🔍 市场信号:**")
    
    if '地缘政治' in analysis['themes']:
        lines.append("⚠️ 地缘政治风险 → 关注国防/能源")
    if 'AI/科技' in analysis['themes']:
        lines.append("🤖 AI热度高 → 关注科技股")
    if '加密货币' in analysis['themes']:
        lines.append("₿ 加密讨论 → 关注相关资产")
    if '股票/投资' in analysis['themes']:
        lines.append("📈 投资活跃 → 关注提及个股")
    
    return "\n".join(lines)

def main():
    print(f"[{datetime.now().strftime('%H:%M')}] 生成每日市场早报...")
    
    # 获取Twitter复盘
    twitter_part = get_twitter_summary()
    
    # 获取FRED数据
    fred_part = get_fred_summary()
    
    # 合并消息
    message = f"""🌅 **每日市场早报** - {datetime.now().strftime('%Y-%m-%d')}

{'='*30}

{twitter_part}

{'='*30}

{fred_part}

{'='*30}

💡 完整报告: `memory/twitter_review_{(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')}.md`
"""
    
    print(message)
    send_message(message)
    
    # 保存完整报告
    report_file = f'/root/.openclaw/workspace/memory/daily_market_report_{datetime.now().strftime("%Y-%m-%d")}.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(message)
    print(f"[{datetime.now().strftime('%H:%M')}] 报告已保存: {report_file}")

if __name__ == '__main__':
    main()
