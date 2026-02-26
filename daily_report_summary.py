#!/usr/bin/env python3
"""
📊 每日晚报生成器 - 真实数据版
每天晚上18:30自动生成专业晚报并推送到Telegram
"""

import json
import os
import re
import urllib.request
import subprocess
import glob
from datetime import datetime
from typing import Dict, List

# Telegram推送配置
TELEGRAM_TARGET = '5440939697'

def send_to_telegram(message: str) -> bool:
    """推送消息到Telegram"""
    try:
        env = os.environ.copy()
        env['PATH'] = '/root/.nvm/versions/node/v22.22.0/bin:' + env.get('PATH', '')
        
        cmd = [
            '/root/.nvm/versions/node/v22.22.0/bin/openclaw',
            'message', 'send',
            '--channel', 'telegram',
            '--target', TELEGRAM_TARGET,
            '--message', message
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=30, env=env)
        if result.returncode == 0:
            print("✅ Telegram 推送成功")
            return True
        else:
            err = result.stderr.decode()[:100] if result.stderr else '未知错误'
            print(f"⚠️ Telegram 推送失败: {err}")
            return False
    except Exception as e:
        print(f"❌ Telegram 推送异常: {e}")
        return False

def get_tencent_us(symbol: str) -> Dict:
    """从腾讯财经获取美股数据"""
    try:
        url = f"https://qt.gtimg.cn/q=us.{symbol}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            text = r.read().decode('gbk')
            match = re.search(r'"([^"]+)"', text)
            if match:
                data = match.group(1).split('~')
                price = float(data[3])
                prev = float(data[4])
                change_pct = ((price - prev) / prev) * 100
                return {
                    'price': price,
                    'change': change_pct,
                    'trend': 'up' if change_pct >= 0 else 'down'
                }
    except Exception as e:
        print(f"❌ 获取 {symbol} 失败: {e}")
    return None

def get_tencent_hk(code: str) -> Dict:
    """从腾讯财经获取港股数据"""
    try:
        url = f"https://qt.gtimg.cn/q=hk{code}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            text = r.read().decode('gbk')
            match = re.search(r'"([^"]+)"', text)
            if match:
                data = match.group(1).split('~')
                price = float(data[3])
                prev = float(data[4])
                change_pct = ((price - prev) / prev) * 100
                return {
                    'price': price,
                    'change': change_pct,
                    'trend': 'up' if change_pct >= 0 else 'down'
                }
    except Exception as e:
        print(f"❌ 获取 hk{code} 失败: {e}")
    return None

def get_binance_price(symbol: str) -> Dict:
    """从币安获取加密货币数据"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return {
                'price': float(data['lastPrice']),
                'change': float(data['priceChangePercent']),
                'trend': 'up' if float(data['priceChangePercent']) >= 0 else 'down'
            }
    except Exception as e:
        print(f"❌ 获取 {symbol} 失败: {e}")
    return None

def get_closing_data() -> Dict:
    """获取收盘数据"""
    print("🔄 获取收盘数据...")
    
    # 美股
    nasdaq = get_tencent_us('IXIC') or {'price': 0, 'change': 0, 'trend': 'flat'}
    dow = get_tencent_us('DJI') or {'price': 0, 'change': 0, 'trend': 'flat'}
    sp500 = get_tencent_us('SPX') or get_tencent_us('INX') or {'price': 0, 'change': 0, 'trend': 'flat'}
    
    # 港股
    hstech = get_tencent_hk('HSTECH') or {'price': 0, 'change': 0, 'trend': 'flat'}
    innoscience = get_tencent_hk('02577') or {'price': 0, 'change': 0, 'trend': 'flat'}
    
    # 加密货币
    btc = get_binance_price('BTCUSDT') or {'price': 0, 'change': 0, 'trend': 'flat'}
    eth = get_binance_price('ETHUSDT') or {'price': 0, 'change': 0, 'trend': 'flat'}
    
    return {
        'us_stocks': {
            'nasdaq': nasdaq,
            'dow': dow,
            'sp500': sp500
        },
        'hk_stocks': {
            'hstech': hstech,
            'innoscience': innoscience
        },
        'crypto': {
            'btc': btc,
            'eth': eth
        }
    }

def get_twitter_summary() -> str:
    """获取今日Twitter抓取摘要"""
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = f"/root/.openclaw/workspace/memory/twitter_logs/{today}.md"
    
    if not os.path.exists(log_file):
        return "暂无今日推文记录"
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 统计抓取次数
        update_count = content.count('## [')
        
        # 提取最新几条推文标题
        lines = content.split('\n')
        recent_tweets = []
        for line in lines:
            if '💡' in line and len(line) > 10:
                recent_tweets.append(line.replace('💡 ', '').strip()[:40])
            if len(recent_tweets) >= 3:
                break
        
        summary = f"今日抓取 {update_count} 次"
        if recent_tweets:
            summary += "\n最新动态:\n"
            for t in recent_tweets:
                summary += f"  · {t}...\n"
        return summary
    except Exception as e:
        return f"读取失败: {e}"

def format_price(value: float) -> str:
    """格式化价格"""
    if value >= 1000:
        return f"{value:,.0f}"
    return f"{value:,.2f}"

def generate_evening_report() -> str:
    """生成晚报"""
    now = datetime.now()
    market = get_closing_data()
    twitter_summary = get_twitter_summary()
    
    lines = [
        f"🌙 *龙虾晚报* | {now.strftime('%m/%d %a')}",
        f"⏰ `{now.strftime('%H:%M')}` 北京时间",
        ""
    ]
    
    # 美股收盘
    lines.append("*📊 美股收盘*")
    for name, data in market['us_stocks'].items():
        emoji = "📈" if data['trend'] == 'up' else "📉" if data['trend'] == 'down' else "➖"
        name_cn = {'nasdaq': '纳斯达克', 'dow': '道琼斯', 'sp500': '标普500'}.get(name, name)
        lines.append(f"  {emoji} {name_cn}: {format_price(data['price'])} ({data['change']:+.2f}%)")
    lines.append("")
    
    # 港股收盘
    lines.append("*🇭🇰 港股收盘*")
    hstech = market['hk_stocks']['hstech']
    emoji = "📈" if hstech['trend'] == 'up' else "📉"
    lines.append(f"  {emoji} 恒生科技: {format_price(hstech['price'])} ({hstech['change']:+.2f}%)")
    
    inn = market['hk_stocks']['innoscience']
    if inn['price'] > 0:
        emoji = "📈" if inn['trend'] == 'up' else "📉"
        lines.append(f"  {emoji} 英诺赛科: {format_price(inn['price'])} ({inn['change']:+.2f}%)")
    lines.append("")
    
    # 加密货币
    lines.append("*₿ 加密货币*")
    for name, data in market['crypto'].items():
        emoji = "🟢" if data['trend'] == 'up' else "🔴"
        symbol = "BTC" if name == 'btc' else "ETH"
        lines.append(f"  {emoji} {symbol}: ${format_price(data['price'])} ({data['change']:+.2f}%)")
    lines.append("")
    
    # Twitter动态
    lines.append("*🐦 Twitter今日动态*")
    for line in twitter_summary.split('\n'):
        lines.append(f"  {line}")
    lines.append("")
    
    # 明日关注
    lines.append("*📅 明日关注*")
    lines.append("  · 美股科技股走势")
    lines.append("  · 存储芯片涨价动态")
    lines.append("  · 英伟达后续影响")
    lines.append("  · 港股南向资金流向")
    
    return "\n".join(lines)

def main():
    """生成并推送晚报"""
    print("=" * 50)
    print("🌙 生成龙虾晚报...")
    print("=" * 50)
    
    # 生成晚报
    report = generate_evening_report()
    
    # 保存到文件
    report_file = f"/tmp/evening_report_{datetime.now().strftime('%H%M')}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"\n💾 已保存: {report_file}")
    
    # 推送到Telegram
    print("\n📱 推送到 Telegram...")
    if send_to_telegram(report):
        print("✅ 晚报推送完成!")
    else:
        print("❌ 推送失败，但文件已保存")
    
    print("\n" + "=" * 50)
    print(report)

if __name__ == "__main__":
    main()
