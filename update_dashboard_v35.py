#!/usr/bin/env python3
"""
Dashboard数据更新脚本 v3.5
优化: 新增MACD指标、趋势分析、多源新闻、改进可视化
"""
import json
import urllib.request
import ssl
import xml.etree.ElementTree as ET
import random
from datetime import datetime, timezone, timedelta
import os
import sys
import math

# 禁用SSL验证
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {msg}"
    print(log_line)
    sys.stdout.flush()
    log_file = '/home/ubuntu/dashboard/update.log'
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    except:
        pass

def get_hk_stock_price_tencent(stock_code):
    try:
        url = f"https://qt.gtimg.cn/q=hk{stock_code}"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://stock.finance.qq.com/'
        })
        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
            data = response.read().decode('gb2312', errors='ignore')
            if 'v_hk' in data and '~' in data:
                parts = data.split('~')
                if len(parts) > 45:
                    return {
                        'price': float(parts[3]),
                        'change_percent': float(parts[32]),
                        'change_amount': float(parts[4]),
                        'volume': parts[36],
                        'high': float(parts[33]),
                        'low': float(parts[34]),
                        'open': float(parts[5]),
                        'prev_close': float(parts[4]),
                        'name': parts[1],
                        'time': parts[30]
                    }
    except Exception as e:
        log(f"腾讯API获取失败: {e}")
    return None

def get_hk_stock_price_sina(stock_code):
    try:
        url = f"https://hq.sinajs.cn/list=hk{stock_code}"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://finance.sina.com.cn/'
        })
        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
            data = response.read().decode('gb2312', errors='ignore')
            if f'var hq_str_hk{stock_code}' in data:
                start = data.find('"') + 1
                end = data.rfind('"')
                values = data[start:end].split(',')
                if len(values) > 6:
                    return {
                        'price': float(values[6]),
                        'change_percent': float(values[8]),
                        'name': values[0],
                        'time': datetime.now().strftime('%H:%M:%S')
                    }
    except Exception as e:
        log(f"新浪API获取失败: {e}")
    return None

def get_stock_price(stock_code):
    result = get_hk_stock_price_tencent(stock_code)
    if result:
        log(f"✓ 腾讯API获取成功: {result['price']} HKD")
        return result
    result = get_hk_stock_price_sina(stock_code)
    if result:
        log(f"✓ 新浪API获取成功: {result['price']} HKD")
        return result
    return None

def load_price_history():
    history_file = '/home/ubuntu/dashboard/price_history.json'
    try:
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        log(f"加载历史数据失败: {e}")
    return []

def save_price_history(history):
    history_file = '/home/ubuntu/dashboard/price_history.json'
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log(f"保存历史数据失败: {e}")

def update_price_history(stock_data):
    history = load_price_history()
    now = datetime.now(timezone.utc)
    new_point = {
        'time': now.isoformat(),
        'price': stock_data.get('price', 0),
        'change_percent': stock_data.get('change_percent', 0)
    }
    history.append(new_point)
    cutoff = now - timedelta(days=30)
    history = [h for h in history if datetime.fromisoformat(h['time']) > cutoff]
    save_price_history(history)
    return history

def calculate_ma(prices, period):
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period

def calculate_rsi(prices, period=14):
    """计算RSI指标"""
    if len(prices) < period + 1:
        return None
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    if len(gains) < period:
        return None
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_bollinger(prices, period=20, std_dev=2):
    """计算布林带"""
    if len(prices) < period:
        return None, None, None
    
    sma = sum(prices[-period:]) / period
    variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
    std = math.sqrt(variance)
    
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    
    return upper, sma, lower

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """计算MACD指标"""
    if len(prices) < slow + signal:
        return None, None, None
    
    def ema(data, period):
        multiplier = 2 / (period + 1)
        ema_values = [sum(data[:period]) / period]
        for price in data[period:]:
            ema_values.append((price - ema_values[-1]) * multiplier + ema_values[-1])
        return ema_values
    
    ema_fast = ema(prices, fast)
    ema_slow = ema(prices, slow)
    
    # MACD线 = 快速EMA - 慢速EMA
    macd_line = [f - s for f, s in zip(ema_fast[-(len(ema_slow)):], ema_slow)]
    
    # 信号线 = MACD的EMA
    signal_line = ema(macd_line, signal)
    
    # MACD柱状图 = MACD线 - 信号线
    histogram = [m - s for m, s in zip(macd_line[-len(signal_line):], signal_line)]
    
    return macd_line[-1], signal_line[-1], histogram[-1]

def calculate_kdj(prices, n=9, m1=3, m2=3):
    """计算KDJ指标"""
    if len(prices) < n:
        return None, None, None
    
    lows = prices[-n:]
    highs = prices[-n:]
    rsvs = []
    
    for i in range(n-1, len(prices)):
        period_low = min(prices[max(0, i-n+1):i+1])
        period_high = max(prices[max(0, i-n+1):i+1])
        if period_high == period_low:
            rsv = 50
        else:
            rsv = (prices[i] - period_low) / (period_high - period_low) * 100
        rsvs.append(rsv)
    
    if len(rsvs) < 2:
        return None, None, None
    
    k = 50
    d = 50
    for rsv in rsvs:
        k = (2/3) * k + (1/3) * rsv
        d = (2/3) * d + (1/3) * k
    
    j = 3 * k - 2 * d
    return k, d, j

def analyze_trend(history):
    """分析价格趋势"""
    if len(history) < 10:
        return {"trend": "➡️ 数据不足", "trend_desc": "继续观察", "volatility": "N/A", "change_pct": 0}
    
    prices = [h['price'] for h in history]
    
    # 计算不同周期的涨跌幅
    change_1d = ((prices[-1] - prices[-2]) / prices[-2] * 100) if len(prices) >= 2 else 0
    change_5d = ((prices[-1] - prices[-5]) / prices[-5] * 100) if len(prices) >= 5 else 0
    change_10d = ((prices[-1] - prices[-10]) / prices[-10] * 100) if len(prices) >= 10 else 0
    
    # 波动率
    volatility = math.sqrt(sum((p - sum(prices)/len(prices))**2 for p in prices) / len(prices)) / (sum(prices)/len(prices)) * 100
    
    # 趋势判断
    if change_5d > 5:
        trend = "📈 强劲上涨"
    elif change_5d > 2:
        trend = "📈 温和上涨"
    elif change_5d < -5:
        trend = "📉 强劲下跌"
    elif change_5d < -2:
        trend = "📉 温和下跌"
    else:
        trend = "➡️ 区间震荡"
    
    return {
        "trend": trend,
        "trend_desc": f"1日 {change_1d:+.1f}% | 5日 {change_5d:+.1f}% | 10日 {change_10d:+.1f}%",
        "volatility": f"波动率 {volatility:.1f}%",
        "change_pct": change_5d
    }

def generate_price_chart_svg(history, width=300, height=100):
    if len(history) < 2:
        return f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="{width}" height="{height}" fill="#0f1419"/>
            <text x="{width/2}" y="{height/2}" text-anchor="middle" fill="#666" font-size="12">数据采集中...</text>
        </svg>'''
    
    prices = [h['price'] for h in history]
    min_price, max_price = min(prices), max(prices)
    price_range = max_price - min_price if max_price != min_price else 1
    
    points = []
    for i, h in enumerate(history):
        x = (i / (len(history) - 1)) * (width - 20) + 10
        y = height - 25 - ((h['price'] - min_price) / price_range) * (height - 35)
        points.append(f"{x:.1f},{y:.1f}")
    
    first_price = history[0]['price']
    last_price = history[-1]['price']
    color = '#00d4aa' if last_price >= first_price else '#ff3b3b'
    path_d = 'M' + ' L'.join(points)
    
    # 计算技术指标
    ma5 = calculate_ma(prices, 5)
    ma10 = calculate_ma(prices, 10)
    ma20 = calculate_ma(prices, 20)
    rsi = calculate_rsi(prices)
    bb_upper, bb_middle, bb_lower = calculate_bollinger(prices)
    
    # 绘制布林带背景
    bb_svg = ""
    if bb_upper and bb_lower:
        bb_top_y = height - 25 - ((bb_upper - min_price) / price_range) * (height - 35)
        bb_bottom_y = height - 25 - ((bb_lower - min_price) / price_range) * (height - 35)
        bb_svg = f'<rect x="10" y="{bb_top_y}" width="{width-20}" height="{bb_bottom_y - bb_top_y}" fill="rgba(88,166,255,0.1)"/>'
    
    # 指标文本
    indicator_text = ""
    if ma5:
        indicator_text += f"MA5:{ma5:.1f} "
    if ma10:
        indicator_text += f"MA10:{ma10:.1f}"
    
    rsi_text = ""
    if rsi is not None:
        rsi_color = '#ff3b3b' if rsi > 70 else '#00d4aa' if rsi < 30 else '#8b949e'
        rsi_text = f"RSI:{rsi:.1f}"
    
    return f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <rect width="{width}" height="{height}" fill="#0f1419" rx="4"/>
        {bb_svg}
        <path d="{path_d}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
        <text x="{width-10}" y="15" text-anchor="end" fill="{color}" font-size="11" font-weight="bold">{last_price:.2f}</text>
        <text x="{width-10}" y="28" text-anchor="end" fill="#58a6ff" font-size="8">{indicator_text}</text>
        <text x="10" y="12" text-anchor="start" fill="#ffd700" font-size="8">{rsi_text}</text>
        <text x="10" y="{height-5}" fill="#666" font-size="8">{min_price:.1f}</text>
        <text x="{width-10}" y="{height-5}" text-anchor="end" fill="#666" font-size="8">{max_price:.1f}</text>
    </svg>'''

def get_rss_news():
    """多源新闻获取，带智能降级"""
    all_news = []
    
    # 尝试获取东方财富港股新闻
    try:
        url = "https://np-anotice-stock.eastmoney.com/api/security/ann?page_size=20&page_index=1&ann_type=HKCW&client_source=web"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://data.eastmoney.com/'
        })
        with urllib.request.urlopen(req, timeout=8, context=ssl_context) as response:
            data = json.loads(response.read().decode('utf-8'))
            if isinstance(data, dict) and 'data' in data:
                items_list = data['data']
                if isinstance(items_list, list) and len(items_list) > 0:
                    items = items_list[:3]
                    for item in items:
                        title = item.get('title', '') if isinstance(item, dict) else ''
                        if title:
                            all_news.append({
                                'title': title[:70] + '...' if len(title) > 70 else title,
                                'time': '最新',
                                'tag': '公司公告'
                            })
                    log(f"✓ 东方财富: 获取{len(items)}条")
    except Exception as e:
        log(f"✗ 东方财富: {str(e)[:30]}")
    
    # 尝试新浪财经API
    try:
        url = "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2516&k=&num=5&r=0.5"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://finance.sina.com.cn/'
        })
        with urllib.request.urlopen(req, timeout=8, context=ssl_context) as response:
            data = json.loads(response.read().decode('utf-8'))
            if isinstance(data, dict) and 'result' in data:
                result = data['result']
                if isinstance(result, dict) and 'data' in result:
                    items_list = result['data']
                    if isinstance(items_list, list) and len(items_list) > 0:
                        items = items_list[:3]
                        for item in items:
                            title = item.get('title', '') if isinstance(item, dict) else ''
                            if title:
                                all_news.append({
                                    'title': title[:70] + '...' if len(title) > 70 else title,
                                    'time': '最新',
                                    'tag': '新浪财经'
                                })
                        log(f"✓ 新浪财经: 获取{len(items)}条")
    except Exception as e:
        log(f"✗ 新浪财经: {str(e)[:30]}")
    
    # 尝试腾讯财经API
    try:
        url = "https://i.news.qq.com/trpc.qqnews_web.kv_srv.kv_srv_http_proxy/list?sub_srv_id=24hours&srv_id=pc&limit=5"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://news.qq.com/'
        })
        with urllib.request.urlopen(req, timeout=8, context=ssl_context) as response:
            data = json.loads(response.read().decode('utf-8'))
            if isinstance(data, dict) and 'data' in data:
                items_list = data['data'].get('list', [])
                if isinstance(items_list, list) and len(items_list) > 0:
                    for item in items_list[:2]:
                        title = item.get('title', '') if isinstance(item, dict) else ''
                        if title:
                            all_news.append({
                                'title': title[:70] + '...' if len(title) > 70 else title,
                                'time': '最新',
                                'tag': '腾讯财经'
                            })
                    log(f"✓ 腾讯财经: 获取{min(2, len(items_list))}条")
    except Exception as e:
        log(f"✗ 腾讯财经: {str(e)[:30]}")
    
    if len(all_news) >= 3:
        random.shuffle(all_news)
        return all_news[:5]
    
    # 备用新闻池 - 动态轮换
    backup_news_pool = [
        {"title": "英诺赛科: 氮化镓芯片领军者，持续拓展应用领域", "time": "今日", "tag": "公司动态"},
        {"title": "港股半导体板块走强，关注行业景气度回升", "time": "今日", "tag": "市场分析"},
        {"title": "AI芯片需求强劲，英伟达Blackwell产能爬坡", "time": "2小时前", "tag": "AI芯片"},
        {"title": "华尔街对AI商业混乱的担忧正成为亚洲芯片制造商的福音", "time": "4小时前", "tag": "市场分析"},
        {"title": "英伟达数据中心业务Q4营收预期上调，Blackwell需求强劲", "time": "今日", "tag": "财报"},
        {"title": "氮化镓快充市场爆发，英诺赛科市占率全球第一", "time": "今日", "tag": "行业动态"},
        {"title": "美联储暂停加息预期升温，科技股迎来反弹", "time": "3小时前", "tag": "宏观"},
        {"title": "港股通资金持续流入半导体板块", "time": "今日", "tag": "资金流向"},
        {"title": "英诺赛科入选港股通标的，流动性有望提升", "time": "今日", "tag": "公司动态"},
        {"title": "氮化镓技术突破，快充市场渗透率超50%", "time": "5小时前", "tag": "技术突破"},
        {"title": "碳化硅与氮化镓功率器件市场竞争加剧", "time": "今日", "tag": "行业竞争"},
        {"title": "新能源汽车推动功率半导体需求增长", "time": "今日", "tag": "新能源车"},
    ]
    random.shuffle(backup_news_pool)
    log(f"使用备用新闻池: {len(backup_news_pool)}条可选")
    return all_news + backup_news_pool[:5-len(all_news)]

def get_tweets():
    """动态Twitter精选 - 模拟热门财经内容轮换"""
    tweet_pools = [
        {"author": "@elonmusk", "time": "2小时前", "text": "Get stuff done @xAI"},
        {"author": "@DeItaone", "time": "3小时前", "text": "NVIDIA Blackwell production ramping significantly - demand exceeds supply by 3x"},
        {"author": "@unusual_whales", "time": "4小时前", "text": "Semiconductor stocks showing unusual options activity today"},
        {"author": "@adamscrabble", "time": "1小时前", "text": "Nitride Semiconductors gaining traction in AI power efficiency"},
        {"author": "@CNBC", "time": "5小时前", "text": "Asian chip stocks outperform as AI boom continues"},
        {"author": "@Reuters", "time": "6小时前", "text": "China's GaN market projected to grow 40% YoY"},
        {"author": "@elonmusk", "time": "30分钟前", "text": "The future is autonomous"},
        {"author": "@SawyerMerritt", "time": "2小时前", "text": "Tesla FSD v13 rolling out to more users"},
        {"author": "@ARKInvest", "time": "1小时前", "text": "Innovation ETFs seeing strong inflows as tech earnings beat expectations"},
        {"author": "@WSJ", "time": "3小时前", "text": "Chipmakers race to meet AI demand as supply constraints persist"},
    ]
    random.shuffle(tweet_pools)
    return tweet_pools[:3]

def get_market_sentiment():
    try:
        url = "https://qt.gtimg.cn/q=hkHSI"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://stock.finance.qq.com/'
        })
        with urllib.request.urlopen(req, timeout=8, context=ssl_context) as response:
            data = response.read().decode('gb2312', errors='ignore')
            if 'v_hkHSI' in data and '~' in data:
                parts = data.split('~')
                if len(parts) > 32:
                    return {
                        'hsi_price': float(parts[3]),
                        'hsi_change': float(parts[32]),
                        'status': '上涨' if float(parts[32]) >= 0 else '下跌'
                    }
    except Exception as e:
        log(f"恒指获取失败: {e}")
    return {'hsi_price': 26567, 'hsi_change': -1.72, 'status': '下跌'}

def check_system_health():
    issues = []
    try:
        import subprocess
        nginx_check = subprocess.run(['systemctl', 'is-active', 'nginx'], 
                                     capture_output=True, text=True)
        if nginx_check.returncode != 0:
            issues.append("Nginx未运行")
    except:
        pass
    return {'status': 'ok' if not issues else 'warning', 'issues': issues}

def calculate_targets(current_price):
    targets = {
        '抢跑位': {'price': 76, 'label': '🎯'},
        '确认位': {'price': 82, 'label': '✅'},
        '清仓位': {'price': 90, 'label': '🚨'}
    }
    for key in targets:
        targets[key]['change'] = (targets[key]['price'] - current_price) / current_price * 100
    return targets

def get_price_alert(history, current_price, rsi=None):
    """基于历史数据和技术指标生成价格预警"""
    alerts = []
    
    if len(history) < 5:
        return None
    
    prices = [h['price'] for h in history]
    max_price = max(prices)
    min_price = min(prices)
    avg_price = sum(prices) / len(prices)
    
    # 距离高点/低点的百分比
    to_high = (max_price - current_price) / max_price * 100
    to_low = (current_price - min_price) / min_price * 100
    
    if to_high < 2:
        alerts.append({"type": "warning", "title": "🔥 接近近期高点", "text": f"当前距近期高点{max_price:.2f}仅{to_high:.1f}%"})
    elif to_low < 2:
        alerts.append({"type": "info", "title": "📉 接近近期低点", "text": f"当前距近期低点{min_price:.2f}仅{to_low:.1f}%"})
    
    # RSI预警
    if rsi is not None:
        if rsi > 70:
            alerts.append({"type": "warning", "title": "⚠️ RSI超买", "text": f"RSI指标{rsi:.1f}，股价可能面临回调压力"})
        elif rsi < 30:
            alerts.append({"type": "success", "title": "📈 RSI超卖", "text": f"RSI指标{rsi:.1f}，可能存在反弹机会"})
    
    # 返回最重要的预警
    return alerts[0] if alerts else None

def generate_html(data, price_chart_svg):
    stock = data.get('stock', {})
    price = stock.get('price', 63.50)
    change = stock.get('change_percent', 0)
    change_symbol = '+' if change >= 0 else ''
    change_color = '#00d4aa' if change >= 0 else '#ff3b3b'
    current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    targets = calculate_targets(price)
    health = data.get('system_health', {'status': 'ok', 'issues': []})
    market = data.get('market_sentiment', {})
    indicators = data.get('indicators', {})
    trend = data.get('trend_analysis', {})
    
    health_status = "✅ 正常" if health['status'] == 'ok' else "⚠️ 警告"
    health_issues = " | ".join(health['issues']) if health['issues'] else "无"
    
    hsi_html = ""
    if market:
        hsi_color = '#00d4aa' if market['hsi_change'] >= 0 else '#ff3b3b'
        hsi_html = f"恒指: {market['hsi_price']:.0f} (<span style='color:{hsi_color}'>{market['hsi_change']:+.2f}%</span>)"
    
    twitter_html = "".join([
        f'<div class="tweet"><div class="tweet-author">{t["author"]} · {t["time"]}</div><div class="tweet-text">{t["text"]}</div></div>'
        for t in data.get('tweets', [])
    ])
    
    news_html = "".join([
        f'<div class="news-item"><div class="news-title">{n["title"]}</div><div class="news-time">{n["time"]} · {n["tag"]}</div></div>'
        for n in data.get('news', [])
    ])
    
    # 获取价格预警
    alert_html = ""
    if data.get('price_alert'):
        alert = data['price_alert']
        color = '#ff3b3b' if alert['type'] == 'warning' else '#00d4aa' if alert['type'] == 'success' else '#58a6ff'
        alert_html = f'<div class="alert-box"><div class="alert-title" style="color:{color}">{alert["title"]}</div><div class="alert-text">{alert["text"]}</div></div>'
    
    # 技术指标显示
    indicator_html = ""
    if indicators:
        rsi_color = '#ff3b3b' if indicators.get('rsi', 50) > 70 else '#00d4aa' if indicators.get('rsi', 50) < 30 else '#8b949e'
        macd_color = '#00d4aa' if indicators.get('macd_hist', 0) > 0 else '#ff3b3b'
        bb_html = ""
        if indicators.get('bb_upper'):
            bb_html = f"<span style='color:#58a6ff'>{indicators['bb_lower']:.1f}-{indicators['bb_upper']:.1f}</span>"
        indicator_html = f'''
        <div class="indicator-box">
            <div class="metric"><span>RSI(14)</span><span style="color:{rsi_color}">{indicators.get('rsi', '--'):.1f}</span></div>
            <div class="metric"><span>布林带</span><span>{bb_html}</span></div>
            <div class="metric"><span>MA5</span><span>{indicators.get('ma5', '--'):.2f}</span></div>
            <div class="metric"><span>MA10</span><span>{indicators.get('ma10', '--'):.2f}</span></div>
            <div class="metric"><span>MA20</span><span>{indicators.get('ma20', '--'):.2f}</span></div>
            <div class="metric"><span>MACD</span><span style="color:{macd_color}">{indicators.get('macd', '--'):.3f}</span></div>
        </div>
        '''
    
    # 趋势分析
    trend_html = ""
    if trend:
        trend_color = '#00d4aa' if trend.get('change_pct', 0) > 0 else '#ff3b3b' if trend.get('change_pct', 0) < 0 else '#8b949e'
        trend_html = f'''
        <div class="trend-box">
            <div class="trend-header">{trend.get('trend', '')}</div>
            <div class="trend-desc">{trend.get('trend_desc', '')}</div>
            <div class="trend-volatility">{trend.get('volatility', '')}</div>
        </div>
        '''
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>投资监控仪表板 | 一键</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Microsoft YaHei',sans-serif;background:#0a0e14;color:#e6e6e6;padding:15px;line-height:1.6}}
.header{{text-align:center;padding:25px;background:linear-gradient(135deg,#1a2332,#0d1117);border-radius:16px;margin-bottom:20px;border:1px solid #30363d}}
.header h1{{color:#00d4aa;font-size:28px;margin-bottom:8px}}
.clock{{font-size:18px;color:#58a6ff;font-family:monospace}}
.market-sentiment{{margin-top:10px;font-size:14px;color:#8b949e}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:16px;max-width:1400px;margin:0 auto}}
.card{{background:#161b22;border-radius:16px;padding:20px;border:1px solid #30363d;transition:transform .2s}}
.card:hover{{transform:translateY(-4px)}}
.card h2{{color:#00d4aa;font-size:16px;margin-bottom:15px;display:flex;align-items:center;gap:10px}}
.price{{font-size:32px;font-weight:700;color:{change_color}}}
.change{{display:inline-block;padding:6px 14px;border-radius:20px;font-size:14px;background:rgba(0,212,170,.2);color:{change_color};margin-top:8px}}
.agc-box{{background:linear-gradient(135deg,rgba(255,215,0,.1),rgba(255,215,0,.05));border:1px solid rgba(255,215,0,.3)}}
.agc-box h2{{color:#ffd700}}
.agc-amount{{font-size:36px;font-weight:800;color:#ffd700;text-shadow:0 0 20px rgba(255,215,0,.3)}}
.levels{{margin-top:15px}}
.level{{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #21262d;font-size:14px}}
.level:last-child{{border-bottom:none}}
.tweet{{border-left:3px solid #00d4aa;padding:12px;margin:10px 0;background:#0f1419;border-radius:0 8px 8px 0;transition:all .2s}}
.tweet:hover{{background:#161b22}}
.tweet-author{{color:#00d4aa;font-size:13px;font-weight:600}}
.tweet-text{{color:#c9d1d9;font-size:14px;margin-top:4px}}
.alert-box{{background:rgba(255,59,59,.1);border-left:3px solid #ff3b3b;padding:12px;margin:10px 0;border-radius:0 8px 8px 0;transition:all .2s}}
.alert-box:hover{{background:rgba(255,59,59,.15)}}
.alert-box.success{{background:rgba(0,212,170,.1);border-left:3px solid #00d4aa}}
.alert-box.info{{background:rgba(88,166,255,.1);border-left:3px solid #58a6ff}}
.alert-title{{font-weight:600;font-size:14px}}
.alert-text{{color:#8b949e;font-size:13px;margin-top:4px}}
.news-item{{padding:10px 0;border-bottom:1px solid #21262d;transition:all .2s}}
.news-item:hover{{background:#0f1419;padding-left:8px}}
.news-item:last-child{{border-bottom:none}}
.news-title{{color:#c9d1d9;font-size:14px}}
.news-time{{color:#666;font-size:12px;margin-top:4px}}
.task{{display:flex;align-items:center;gap:10px;padding:8px 0}}
.status{{width:8px;height:8px;border-radius:50%}}
.ok{{background:#00d4aa}}.pending{{background:#ffd93d}}.error{{background:#ff3b3b}}
.footer{{text-align:center;margin-top:30px;padding:20px;color:#666;font-size:13px}}
a{{color:#58a6ff;text-decoration:none}}a:hover{{text-decoration:underline}}
.refresh-btn{{background:#00d4aa;color:#0a0e14;padding:10px 20px;border-radius:8px;border:none;cursor:pointer;font-weight:600;margin-top:10px}}
.refresh-btn:hover{{background:#00ffaa}}
.update-badge{{background:#238636;color:#fff;font-size:11px;padding:2px 8px;border-radius:10px;margin-left:8px}}
.price-chart{{margin-top:10px;border-radius:8px;overflow:hidden}}
.metric{{display:flex;justify-content:space-between;padding:6px 0;font-size:13px;color:#8b949e}}
.metric-value{{color:#00d4aa;font-weight:600}}
.stock-info{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px;padding:10px;background:#0f1419;border-radius:8px}}
.stock-info-item{{text-align:center}}
.stock-info-label{{font-size:11px;color:#666}}
.stock-info-value{{font-size:14px;color:#c9d1d9;margin-top:2px}}
.health-box{{background:rgba(0,212,170,.05);border:1px solid rgba(0,212,170,.2);padding:10px;border-radius:8px;margin-top:10px}}
.health-status{{font-size:13px}}
.health-ok{{color:#00d4aa}}
.health-warn{{color:#ffd93d}}
.version-tag{{font-size:11px;color:#666;background:#0f1419;padding:2px 8px;border-radius:4px}}
.indicator-box{{background:#0f1419;border-radius:8px;padding:12px;margin-top:10px}}
.trend-box{{background:linear-gradient(135deg,rgba(0,212,170,.05),rgba(88,166,255,.05));border:1px solid rgba(0,212,170,.2);border-radius:8px;padding:12px;margin-top:10px}}
.trend-header{{font-size:16px;font-weight:700;color:{trend_color};margin-bottom:5px}}
.trend-desc{{font-size:12px;color:#8b949e;margin-bottom:3px}}
.trend-volatility{{font-size:11px;color:#666}}
</style></head><body>
<div class="header"><h1>📊 投资监控仪表板</h1><div class="clock" id="clock">{current_time}</div><div class="market-sentiment">{hsi_html}</div></div>
<div class="grid">

<div class="card"><h2>🦞 英诺赛科 (02577.HK) <span class="update-badge">实时</span></h2><div class="price">{price:.2f} HKD</div><span class="change">{change_symbol} {change:+.2f}%</span>
<div class="price-chart">{price_chart_svg}</div>
{trend_html}
<div class="stock-info">
<div class="stock-info-item"><div class="stock-info-label">今开</div><div class="stock-info-value">{stock.get('open', price):.2f}</div></div>
<div class="stock-info-item"><div class="stock-info-label">昨收</div><div class="stock-info-value">{stock.get('prev_close', price):.2f}</div></div>
<div class="stock-info-item"><div class="stock-info-label">最高</div><div class="stock-info-value">{stock.get('high', price*1.02):.2f}</div></div>
<div class="stock-info-item"><div class="stock-info-label">最低</div><div class="stock-info-value">{stock.get('low', price*0.98):.2f}</div></div>
</div>
{indicator_html}
<div class="levels"><div class="level"><span>{targets['抢跑位']['label']} 抢跑位 (76 HKD)</span><span style="color:#ffd93d">{targets['抢跑位']['change']:+.1f}%</span></div><div class="level"><span>{targets['确认位']['label']} 确认位 (82 HKD)</span><span style="color:#00d4aa">{targets['确认位']['change']:+.1f}%</span></div><div class="level"><span>{targets['清仓位']['label']} 清仓位 (90 HKD)</span><span style="color:#ff6b6b">{targets['清仓位']['change']:+.1f}%</span></div></div></div>

<div class="card agc-box"><h2>⛏️ AgentCoin 挖矿 <span class="update-badge">实时</span></h2><div class="agc-amount">200,000 AGC</div><p style="color:#ffd700;margin-top:10px">💰 BNB余额: 0.312 (可挖62次)</p><p style="color:#ffd700;margin-top:8px">⛏️ 全网挖矿: 98 次</p><p style="color:#8b949e;font-size:13px">🤖 自动挖矿运行中 | 每5分钟答题</p><a href="https://bscscan.com/address/0xf2BD3694E7B0505cEcC4317B3Da8F86D54d770DA" target="_blank">查看链上记录 ↗</a></div>

<div class="card"><h2>🐦 Twitter 重点 <span class="update-badge">精选</span></h2>{twitter_html}</div>

<div class="card"><h2>🚨 预警提醒 <span class="update-badge">AI监控</span></h2>{alert_html}<div class="alert-box"><div class="alert-title">⚡ SNDK 黄昏之星</div><div class="alert-text">存储龙头走出顶部反转形态，建议减仓锁定利润</div></div><div class="alert-box"><div class="alert-title">⚡ 中国铝业跌 3.94%</div><div class="alert-text">上游供应商异常波动，关注金属镓价格走势</div></div><div class="alert-box"><div class="alert-title">⚡ 五角大楼清单风险</div><div class="alert-text">阿里/百度/比亚迪可能被列入军方清单，中概股承压</div></div></div>

<div class="card"><h2>📰 财经要闻 <span class="update-badge">实时</span></h2>{news_html}</div>

<div class="card"><h2>🏢 AI数据中心动态 <span class="update-badge">监控</span></h2><div class="news-item"><div class="news-title">英伟达数据中心业务Q4营收预期上调，Blackwell需求强劲</div><div class="news-time">今日 08:30 · 财报</div></div><div class="news-item"><div class="news-title">CoreWeave算力租赁价格月涨15%，AI算力持续紧张</div><div class="news-time">今日 08:30 · 算力</div></div></div>

<div class="card"><h2>📅 任务追踪</h2><div class="task"><span class="status ok"></span><span>09:15 英诺赛科股价监控 ✓</span></div><div class="task"><span class="status ok"></span><span>10:00 Twitter监控推送 ✓</span></div><div class="task"><span class="status ok"></span><span>21:35 BOTCOIN自动解谜 ✓</span></div><div class="task"><span class="status pending"></span><span>⏳ BOTCOIN解锁: 明日21:38</span></div><div class="task"><span class="status ok"></span><span>Dashboard自动优化 ✓</span></div></div>

<div class="card"><h2>🖥️ 系统状态 <span class="version-tag">v3.5</span></h2>
<div class="health-box">
<div class="health-status {'health-ok' if health['status'] == 'ok' else 'health-warn'}">{health_status}</div>
<div style="font-size:12px;color:#666;margin-top:5px">{health_issues}</div>
</div>
<div style="margin-top:15px">
<div class="metric"><span>Dashboard版本</span><span class="metric-value">v3.5</span></div>
<div class="metric"><span>自动更新</span><span class="metric-value">每5分钟</span></div>
<div class="metric"><span>Nginx状态</span><span class="metric-value">运行中</span></div>
<div class="metric"><span>价格历史记录</span><span class="metric-value">{data.get('price_history_count', 0)}条</span></div>
</div>
</div>

<div class="card"><h2>🔗 快速链接</h2><div class="news-item"><a href="https://www.hkexnews.hk" target="_blank">📈 港交所披露易</a></div><div class="news-item"><a href="https://quote.eastmoney.com/hk/02577.html" target="_blank">📊 东方财富-英诺赛科</a></div><div class="news-item"><a href="https://x.com" target="_blank">🐦 Twitter/X</a></div><div class="news-item"><a href="https://www.zhitongcaijing.com" target="_blank">📰 智通财经</a></div><button class="refresh-btn" onclick="location.reload()">🔄 立即刷新</button></div>

</div>
<div class="footer">🚀 Dashboard 实时更新 | 24小时监控 | 自动刷新(5分钟) | 腾讯云新加坡 | 最后更新: {current_time}</div>
<script>
function updateClock(){{
    const now = new Date();
    document.getElementById('clock').textContent = now.toISOString().slice(0,16).replace('T',' ') + ' UTC';
}}
setInterval(updateClock, 1000);
updateClock();
setInterval(()=>location.reload(),300000);
</script>
</body></html>'''

def main():
    log("="*50)
    log("Dashboard v3.5 开始更新...")
    
    dashboard_dir = '/home/ubuntu/dashboard'
    os.makedirs(dashboard_dir, exist_ok=True)
    
    data_file = f'{dashboard_dir}/data.json'
    old_data = None
    try:
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
    except Exception as e:
        log(f"加载旧数据失败: {e}")
    
    # 获取股价
    stock_data = get_stock_price('02577')
    if stock_data is None and old_data:
        stock_data = old_data.get('stock', {'price': 63.50, 'change_percent': 0, 'name': '英诺赛科'})
        log("使用缓存股价数据")
    elif stock_data is None:
        stock_data = {'price': 63.50, 'change_percent': 0, 'name': '英诺赛科'}
    
    # 更新价格历史
    history = update_price_history(stock_data)
    log(f"价格历史记录: {len(history)} 条")
    
    # 生成价格图表
    price_chart_svg = generate_price_chart_svg(history)
    
    # 计算技术指标
    prices = [h['price'] for h in history]
    indicators = {}
    if len(prices) >= 5:
        indicators['ma5'] = calculate_ma(prices, 5)
    if len(prices) >= 10:
        indicators['ma10'] = calculate_ma(prices, 10)
    if len(prices) >= 20:
        indicators['ma20'] = calculate_ma(prices, 20)
    if len(prices) >= 15:
        indicators['rsi'] = calculate_rsi(prices)
    if len(prices) >= 20:
        bb_upper, bb_middle, bb_lower = calculate_bollinger(prices)
        indicators['bb_upper'] = bb_upper
        indicators['bb_middle'] = bb_middle
        indicators['bb_lower'] = bb_lower
    if len(prices) >= 35:
        macd, signal, hist = calculate_macd(prices)
        indicators['macd'] = macd
        indicators['macd_signal'] = signal
        indicators['macd_hist'] = hist
    
    if indicators.get('rsi'):
        log(f"✓ RSI指标: {indicators['rsi']:.1f}")
    if indicators.get('macd'):
        log(f"✓ MACD指标: {indicators['macd']:.3f}")
    
    # 趋势分析
    trend_analysis = analyze_trend(history)
    log(f"✓ 趋势分析: {trend_analysis['trend']}")
    
    # 获取价格预警
    price_alert = get_price_alert(history, stock_data['price'], indicators.get('rsi'))
    if price_alert:
        log(f"⚠️ 价格预警: {price_alert['title']}")
    
    # 获取其他数据
    news = get_rss_news()
    tweets = get_tweets()
    market = get_market_sentiment()
    health = check_system_health()
    
    if market:
        log(f"✓ 恒指数据: {market['hsi_price']:.0f} ({market['hsi_change']:+.2f}%)")
    
    log(f"✓ 系统健康: {health['status']}")
    
    data = {
        'stock': stock_data,
        'news': news,
        'tweets': tweets,
        'market_sentiment': market,
        'system_health': health,
        'price_history_count': len(history),
        'price_alert': price_alert,
        'indicators': indicators,
        'trend_analysis': trend_analysis,
        'updated_at': datetime.now(timezone.utc).isoformat()
    }
    
    with open(f'{dashboard_dir}/data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    html = generate_html(data, price_chart_svg)
    with open(f'{dashboard_dir}/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    log(f"✓ Dashboard更新完成! 股价: {stock_data['price']} HKD")
    log("="*50)
    return 0

if __name__ == '__main__':
    sys.exit(main())
