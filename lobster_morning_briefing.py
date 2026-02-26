#!/usr/bin/env python3
"""
🦞 智能早报生成器 - 详细版
每天早上8:30自动生成详细早报并推送到Telegram
"""

import json
import os
import re
import urllib.request
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List

TELEGRAM_TARGET = '5440939697'

def send_to_telegram(message: str) -> bool:
    """推送消息到Telegram"""
    try:
        env = os.environ.copy()
        env['PATH'] = '/root/.nvm/versions/node/v22.22.0/bin:' + env.get('PATH', '')
        cmd = [
            '/root/.nvm/versions/node/v22.22.0/bin/openclaw',
            'message', 'send', '--channel', 'telegram',
            '--target', TELEGRAM_TARGET, '--message', message
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=30, env=env)
        return result.returncode == 0
    except:
        return False

def get_tencent_data(symbol: str) -> Dict:
    """从腾讯财经获取数据"""
    try:
        url = f"https://qt.gtimg.cn/q={symbol}"
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
                    'trend': 'up' if change_pct >= 0 else 'down',
                    'name': data[1] if len(data) > 1 else symbol
                }
    except Exception as e:
        print(f"❌ 获取 {symbol} 失败: {e}")
    return None

def get_binance_price(symbol: str) -> Dict:
    """从币安获取加密货币数据"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            change = float(data['priceChangePercent'])
            return {
                'price': float(data['lastPrice']),
                'change': change,
                'trend': 'up' if change >= 0 else 'down'
            }
    except Exception as e:
        print(f"❌ 获取 {symbol} 失败: {e}")
    return None

def get_market_data() -> Dict:
    """获取全面的市场数据"""
    print("🔄 获取全球市场数据...")
    
    # 美股指数
    nasdaq = get_tencent_data('us.IXIC') or {}
    dow = get_tencent_data('us.DJI') or {}
    sp500 = get_tencent_data('us.SPX') or get_tencent_data('us.INX') or {}
    
    # A股指数
    sh_index = get_tencent_data('sh000001') or {}  # 沪指
    sz_index = get_tencent_data('sz399001') or {}  # 深指
    
    # 港股指数
    hstech = get_tencent_data('hkHSTECH') or {}
    
    # 热门个股
    nvidia = get_tencent_data('us.NVDA') or {}
    tesla = get_tencent_data('us.TSLA') or {}
    amd = get_tencent_data('us.AMD') or {}
    
    # 加密货币
    btc = get_binance_price('BTCUSDT') or {}
    eth = get_binance_price('ETHUSDT') or {}
    sol = get_binance_price('SOLUSDT') or {}
    
    # 市场情绪判断
    up_count = sum([1 for x in [nasdaq, dow, sp500] if x.get('trend') == 'up'])
    sentiment = '🔥 强烈看涨' if up_count >= 3 else '❄️ 偏空' if up_count == 0 else '⚖️ 震荡'
    
    return {
        'sentiment': sentiment,
        'us_indices': {'nasdaq': nasdaq, 'dow': dow, 'sp500': sp500},
        'cn_indices': {'sh': sh_index, 'sz': sz_index},
        'hk_indices': {'hstech': hstech},
        'stocks': {'nvidia': nvidia, 'tesla': tesla, 'amd': amd},
        'crypto': {'btc': btc, 'eth': eth, 'sol': sol}
    }

def get_today_hot_news() -> List[str]:
    """获取今日热点新闻"""
    try:
        news_file = '/root/.openclaw/workspace/lobster-workspace/dashboard/data/finance_news.json'
        if os.path.exists(news_file):
            with open(news_file, 'r') as f:
                data = json.load(f)
                # 取前4条重要新闻
                news = data.get('news', [])[:4]
                return [f"• {n['title'][:35]}..." if len(n['title']) > 35 else f"• {n['title']}" for n in news]
    except:
        pass
    return ["• 暂无新闻数据"]

def get_twitter_summary() -> Dict:
    """智能总结Twitter昨日内容"""
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = f"/root/.openclaw/workspace/memory/twitter_logs/{today}.md"
    
    if not os.path.exists(log_file):
        return {
            'count': 0, 
            'summary': [
                "• 暂无今日推文数据"
            ]
        }
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 统计抓取次数
        update_count = content.count('## [')
        
        # 提取所有推文内容（从📝后面提取）
        tweets = []
        lines = content.split('\n')
        current_tweet = {}
        
        for line in lines:
            # 提取作者
            if line.startswith('### 👤'):
                author_match = re.search(r'@([^`]+)', line)
                if author_match:
                    current_tweet['author'] = author_match.group(1).strip()
            
            # 提取内容
            if '> 📝' in line:
                text = line.replace('> 📝', '').strip()
                if len(text) > 20:  # 过滤太短的
                    current_tweet['text'] = text
            
            # 提取翻译（如果有）
            if '> 🈯' in line:
                translate = line.replace('> 🈯', '').strip()
                current_tweet['translate'] = translate
            
            # 遇到分隔线或新推文，保存当前推文
            if line.startswith('---') and current_tweet.get('text'):
                # 优先使用中文翻译
                display_text = current_tweet.get('translate', current_tweet['text'])
                tweets.append({
                    'author': current_tweet.get('author', 'unknown'),
                    'text': display_text
                })
                current_tweet = {}
        
        # 最后一条
        if current_tweet.get('text'):
            display_text = current_tweet.get('translate', current_tweet['text'])
            tweets.append({
                'author': current_tweet.get('author', 'unknown'),
                'text': display_text
            })
        
        # 智能分类和提取要点
        summaries = []
        
        # 1. 找含有关键词的推文（财报、重大合作、宏观）
        keywords_map = {
            '财报': '财报',
            'earnings': '财报',
            '收购': '并购',
            '合作': '合作',
            'deal': '合作',
            '订单': '订单',
            '涨价': '涨价',
            '降息': '宏观',
            'Fed': '宏观',
            'CPI': '宏观'
        }
        
        important_tweets = []
        for t in tweets:
            text = t['text'].lower()
            for kw, category in keywords_map.items():
                if kw.lower() in text:
                    important_tweets.append((category, t))
                    break
        
        # 2. 找提及最多的股票
        all_text = ' '.join([t['text'] for t in tweets])
        tickers = re.findall(r'\$[A-Z]{2,5}', all_text)
        ticker_counts = {}
        for t in tickers:
            ticker_counts[t] = ticker_counts.get(t, 0) + 1
        top_tickers = sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # 构建总结
        if top_tickers:
            tickers_str = ', '.join([t[0] for t in top_tickers])
            summaries.append(f"• 热议标的: {tickers_str}")
        
        # 重要事件（取前2条）
        seen_categories = set()
        for category, tweet in important_tweets[:3]:
            if category not in seen_categories:
                # 提取核心内容（前40字）
                text = tweet['text'][:45] + "..." if len(tweet['text']) > 45 else tweet['text']
                summaries.append(f"• {category}: {text}")
                seen_categories.add(category)
        
        # 如果没有重要事件，取最新2条（排除太短的）
        if len(summaries) < 2 and tweets:
            seen_authors = set()
            for t in tweets[-5:]:  # 从后往前找更多条
                text = t['text'].strip()
                author = t['author']
                # 过滤太短的或只有"转"的，或已存在的作者
                if len(text) < 10 or text in ['转', '转发', 'RT'] or author in seen_authors:
                    continue
                text_display = text[:40] + "..." if len(text) > 40 else text
                summaries.append(f"• {author}: {text_display}")
                seen_authors.add(author)
                if len(summaries) >= 3:
                    break
        
        # 去重并限制条数
        summaries = list(dict.fromkeys(summaries))[:4]
        
        if not summaries:
            summaries = ["• 今日暂无重大事件"]
        
        return {
            'count': update_count,
            'summary': summaries
        }
    except Exception as e:
        print(f"❌ Twitter总结失败: {e}")
        return {
            'count': 0, 
            'summary': ["• 数据读取失败"]
        }

def get_fred_summary() -> str:
    """获取FRED宏观数据摘要"""
    try:
        # 尝试读取最新的FRED数据
        fred_files = sorted(glob.glob('/root/.openclaw/workspace/memory/fred_data_*.json'), reverse=True)
        if fred_files:
            with open(fred_files[0], 'r') as f:
                data = json.load(f)
                # 简单返回关键指标
                return "美联储数据正常更新"
    except:
        pass
    return "宏观数据监控中"

def format_num(value: float) -> str:
    """格式化数字"""
    if abs(value) >= 1000:
        return f"{value:,.0f}"
    return f"{value:,.2f}"

def generate_detailed_briefing() -> str:
    """生成详细早报"""
    now = datetime.now()
    data = get_market_data()
    news = get_today_hot_news()
    twitter = get_twitter_summary()
    
    lines = [
        f"🌅 *龙虾早报* | {now.strftime('%m/%d %a')}",
        f"⏰ `{now.strftime('%H:%M')}` 北京时间 | {data['sentiment']}",
        ""
    ]
    
    # 全球市场概览
    lines.append("━━━━━━━━━━━━━━━")
    lines.append("*🌍 全球市场*")
    lines.append("━━━━━━━━━━━━━━━")
    
    # 美股
    lines.append("🇺🇸 *美股隔夜*")
    us = data['us_indices']
    for key, name in [('nasdaq', '纳斯达克'), ('sp500', '标普500'), ('dow', '道琼斯')]:
        d = us.get(key, {})
        if d:
            emoji = "🟢" if d.get('trend') == 'up' else "🔴"
            lines.append(f"  {emoji} {name}: {format_num(d.get('price', 0))} ({d.get('change', 0):+.2f}%)")
    lines.append("")
    
    # A股
    lines.append("🇨🇳 *A股前瞻*")
    cn = data['cn_indices']
    for key, name in [('sh', '上证指数'), ('sz', '深证成指')]:
        d = cn.get(key, {})
        if d:
            emoji = "🟢" if d.get('trend') == 'up' else "🔴"
            lines.append(f"  {emoji} {name}: {format_num(d.get('price', 0))} ({d.get('change', 0):+.2f}%)")
    lines.append("")
    
    # 港股
    lines.append("🇭🇰 *港股收盘*")
    hk = data['hk_indices']['hstech']
    if hk:
        emoji = "🟢" if hk.get('trend') == 'up' else "🔴"
        lines.append(f"  {emoji} 恒生科技: {format_num(hk.get('price', 0))} ({hk.get('change', 0):+.2f}%)")
    lines.append("")
    
    # 热门个股
    lines.append("━━━━━━━━━━━━━━━")
    lines.append("*📈 热门个股*")
    lines.append("━━━━━━━━━━━━━━━")
    stocks = data['stocks']
    for key, name in [('nvidia', '英伟达 NVDA'), ('tesla', '特斯拉 TSLA'), ('amd', 'AMD')]:
        d = stocks.get(key, {})
        if d:
            emoji = "🟢" if d.get('trend') == 'up' else "🔴"
            lines.append(f"  {emoji} {name}: ${format_num(d.get('price', 0))} ({d.get('change', 0):+.2f}%)")
    lines.append("")
    
    # 加密货币
    lines.append("━━━━━━━━━━━━━━━")
    lines.append("*₿ 加密货币*")
    lines.append("━━━━━━━━━━━━━━━")
    crypto = data['crypto']
    for key, name in [('btc', '比特币'), ('eth', '以太坊'), ('sol', 'Solana')]:
        d = crypto.get(key, {})
        if d:
            emoji = "🟢" if d.get('trend') == 'up' else "🔴"
            price = d.get('price', 0)
            price_str = f"${price:,.0f}" if price >= 1000 else f"${price:,.2f}"
            lines.append(f"  {emoji} {name}: {price_str} ({d.get('change', 0):+.2f}%)")
    lines.append("")
    
    # 今日热点新闻
    lines.append("━━━━━━━━━━━━━━━")
    lines.append("*📰 今日热点*")
    lines.append("━━━━━━━━━━━━━━━")
    for n in news[:4]:
        lines.append(f"  {n}")
    lines.append("")
    
    # Twitter动态
    lines.append("━━━━━━━━━━━━━━━")
    lines.append("*🐦 Twitter要点*")
    lines.append("━━━━━━━━━━━━━━━")
    lines.append(f"  今日更新: {twitter['count']} 次")
    lines.append("")
    for item in twitter['summary']:
        lines.append(f"  {item}")
    lines.append("")
    
    # 今日关注
    lines.append("━━━━━━━━━━━━━━━")
    lines.append("*👀 今日关注*")
    lines.append("━━━━━━━━━━━━━━━")
    lines.append("  · 美联储官员讲话")
    lines.append("  · 英伟达财报后续影响")
    lines.append("  · 存储芯片涨价动态")
    lines.append("  · 南向资金流向")
    
    return "\n".join(lines)

import glob

def main():
    """生成并推送详细早报"""
    print("=" * 60)
    print("🦞 生成详细龙虾早报...")
    print("=" * 60)
    
    briefing = generate_detailed_briefing()
    
    # 保存
    with open("/tmp/lobster_morning_briefing.txt", 'w') as f:
        f.write(briefing)
    
    # 推送
    print("\n📱 推送到 Telegram...")
    if send_to_telegram(briefing):
        print("✅ 详细早报推送完成!")
    else:
        print("❌ 推送失败")
    
    print("\n" + briefing)

if __name__ == "__main__":
    main()
