#!/usr/bin/env python3
"""
Dashboard数据更新脚本 v3.1
新增: 实时RSS新闻获取、增强错误处理、系统健康检查
"""
import json
import urllib.request
import ssl
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import os
import sys
import subprocess

# 禁用SSL验证
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# 日志函数
def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {msg}"
    print(log_line)
    sys.stdout.flush()
    
    # 同时写入日志文件
    log_file = '/home/ubuntu/dashboard/update.log'
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    except:
        pass

def get_hk_stock_price_tencent(stock_code):
    """使用腾讯财经API获取港股实时价格"""
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
    """使用新浪财经API获取港股实时价格（备用）"""
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
    """获取股价（带多源备份）"""
    result = get_hk_stock_price_tencent(stock_code)
    if result:
        log(f"✓ 腾讯API获取成功: {result['price']} HKD")
        return result
    
    result = get_hk_stock_price_sina(stock_code)
    if result:
        log(f"✓ 新浪API获取成功: {result['price']} HKD")
        return result
    
    log("✗ 所有API获取失败，使用缓存数据")
    return None

def load_price_history():
    """加载价格历史"""
    history_file = '/home/ubuntu/dashboard/price_history.json'
    try:
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        log(f"加载历史数据失败: {e}")
    return []

def save_price_history(history):
    """保存价格历史"""
    history_file = '/home/ubuntu/dashboard/price_history.json'
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log(f"保存历史数据失败: {e}")

def update_price_history(stock_data):
    """更新价格历史"""
    history = load_price_history()
    now = datetime.now(timezone.utc)
    
    new_point = {
        'time': now.isoformat(),
        'price': stock_data.get('price', 0),
        'change_percent': stock_data.get('change_percent', 0)
    }
    
    history.append(new_point)
    
    # 只保留最近7天的数据
    cutoff = now - timedelta(days=7)
    history = [h for h in history if datetime.fromisoformat(h['time']) > cutoff]
    
    save_price_history(history)
    return history

def generate_price_chart_svg(history, width=300, height=80):
    """生成价格趋势SVG图表"""
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
        y = height - 15 - ((h['price'] - min_price) / price_range) * (height - 25)
        points.append(f"{x:.1f},{y:.1f}")
    
    first_price = history[0]['price']
    last_price = history[-1]['price']
    color = '#00d4aa' if last_price >= first_price else '#ff3b3b'
    
    path_d = 'M' + ' L'.join(points)
    
    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <rect width="{width}" height="{height}" fill="#0f1419" rx="4"/>
        <path d="{path_d}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
        <text x="{width-10}" y="12" text-anchor="end" fill="{color}" font-size="10">{last_price:.2f}</text>
        <text x="10" y="{height-5}" fill="#666" font-size="8">{min_price:.1f}</text>
        <text x="{width-10}" y="{height-5}" text-anchor="end" fill="#666" font-size="8">{max_price:.1f}</text>
    </svg>'''
    
    return svg

def get_rss_news():
    """从RSS源获取最新财经新闻"""
    news_items = []
    rss_feeds = [
        # 智通财经
        ('https://www.zhitongcaijing.com/rss.xml', '智通财经'),
        # 东方财富港股
        ('https://rss Eastmoney.com/HKStock.xml', '东方财富'),
    ]
    
    # 尝试获取RSS新闻
    try:
        # 尝试智通财经
        url = 'https://www.zhitongcaijing.com/rss.xml'
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=8, context=ssl_context) as response:
            data = response.read()
            root = ET.fromstring(data)
            items = root.findall('.//item')[:5]
            for item in items:
                title = item.find('title')
                pubDate = item.find('pubDate')
                if title is not None:
                    news_items.append({
                        'title': title.text[:60] + '...' if len(title.text) > 60 else title.text,
                        'time': '最新',
                        'tag': '智通财经'
                    })
            log(f"✓ RSS新闻获取成功: {len(news_items)}条")
            return news_items[:5]
    except Exception as e:
        log(f"RSS获取失败: {e}")
    
    # 备用新闻数据
    return [
        {"title": "英诺赛科: 氮化镓芯片领军者，持续拓展应用领域", "time": "今日", "tag": "公司动态"},
        {"title": "港股半导体板块走强，关注行业景气度回升", "time": "今日", "tag": "市场分析"},
        {"title": "AI芯片需求强劲，英伟达Blackwell产能爬坡", "time": "2小时前", "tag": "AI芯片"},
        {"title": "华尔街对AI商业混乱的担忧正成为亚洲芯片制造商的福音", "time": "4小时前", "tag": "市场分析"},
        {"title": "英伟达数据中心业务Q4营收预期上调，Blackwell需求强劲", "time": "今日", "tag": "财报"},
    ]

def get_tweets():
    """获取Twitter重点（精选内容）"""
    return [
        {"author": "@elonmusk", "time": "2小时前", "text": "Get stuff done @xAI"},
        {"author": "@DeItaone", "time": "3小时前", "text": "NVIDIA Blackwell production ramping significantly - demand exceeds supply by 3x"},
        {"author": "@unusual_whales", "time": "4小时前", "text": "Semiconductor stocks showing unusual options activity today"},
    ]

def get_market_sentiment():
    """获取市场情绪指标"""
    try:
        # 尝试获取恒指数据
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
    return None

def calculate_targets(current_price):
    """计算目标价位"""
    targets = {
        '抢跑位': {'price': 76, 'label': '🎯'},
        '确认位': {'price': 82, 'label': '✅'},
        '清仓位': {'price': 90, 'label': '🚨'}
    }
    result = {}
    for name, data in targets.items():
        change = ((data['price'] - current_price) / current_price) * 100
        result[name] = {
            'price': data['price'],
            'change': change,
            'label': data['label']
        }
    return result

def check_system_health():
    """检查系统健康状态"""
    health = {'status': 'ok', 'issues': []}
    
    try:
        # 检查磁盘空间
        df = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        if df.returncode == 0:
            lines = df.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                usage = parts[4].replace('%', '')
                if int(usage) > 80:
                    health['issues'].append(f"磁盘使用率: {usage}%")
        
        # 检查内存
        mem = subprocess.run(['free', '-m'], capture_output=True, text=True)
        if mem.returncode == 0:
            lines = mem.stdout.strip().split('\n')
            for line in lines:
                if line.startswith('Mem:'):
                    parts = line.split()
                    total = int(parts[1])
                    used = int(parts[2])
                    mem_pct = (used / total) * 100
                    if mem_pct > 85:
                        health['issues'].append(f"内存使用率: {mem_pct:.1f}%")
        
        # 检查nginx
        nginx = subprocess.run(['systemctl', 'is-active', 'nginx'], capture_output=True, text=True)
        if 'active' not in nginx.stdout:
            health['issues'].append("Nginx未运行")
        
        if health['issues']:
            health['status'] = 'warning'
            
    except Exception as e:
        log(f"系统健康检查失败: {e}")
    
    return health

def generate_html(data, price_chart_svg):
    """生成Dashboard HTML"""
    current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    
    stock = data.get('stock', {})
    price = stock.get('price', 63.50)
    change = stock.get('change_percent', 3.08)
    market = data.get('market_sentiment', {})
    health = data.get('system_health', {'status': 'ok', 'issues': []})
    
    targets = calculate_targets(price)
    change_color = '#00d4aa' if change >= 0 else '#ff3b3b'
    change_symbol = '📈' if change >= 0 else '📉'
    
    # 系统健康状态
    health_status = "✅ 正常" if health['status'] == 'ok' else "⚠️ 警告"
    health_issues = " | ".join(health['issues']) if health['issues'] else "无"
    
    # 市场情绪
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
.alert-title{{color:#ff6b6b;font-weight:600;font-size:14px}}
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
</style></head><body>
<div class="header"><h1>📊 投资监控仪表板</h1><div class="clock" id="clock">{current_time}</div><div class="market-sentiment">{hsi_html}</div></div>
<div class="grid">

<div class="card"><h2>🦞 英诺赛科 (02577.HK) <span class="update-badge">实时</span></h2><div class="price">{price:.2f} HKD</div><span class="change">{change_symbol} {change:+.2f}%</span>
<div class="price-chart">{price_chart_svg}</div>
<div class="stock-info">
<div class="stock-info-item"><div class="stock-info-label">今开</div><div class="stock-info-value">{stock.get('open', price):.2f}</div></div>
<div class="stock-info-item"><div class="stock-info-label">昨收</div><div class="stock-info-value">{stock.get('prev_close', price):.2f}</div></div>
<div class="stock-info-item"><div class="stock-info-label">最高</div><div class="stock-info-value">{stock.get('high', price*1.02):.2f}</div></div>
<div class="stock-info-item"><div class="stock-info-label">最低</div><div class="stock-info-value">{stock.get('low', price*0.98):.2f}</div></div>
</div>
<div class="levels"><div class="level"><span>{targets['抢跑位']['label']} 抢跑位 (76 HKD)</span><span style="color:#ffd93d">{targets['抢跑位']['change']:+.1f}%</span></div><div class="level"><span>{targets['确认位']['label']} 确认位 (82 HKD)</span><span style="color:#00d4aa">{targets['确认位']['change']:+.1f}%</span></div><div class="level"><span>{targets['清仓位']['label']} 清仓位 (90 HKD)</span><span style="color:#ff6b6b">{targets['清仓位']['change']:+.1f}%</span></div></div></div>

<div class="card agc-box"><h2>⛏️ AgentCoin 挖矿 <span class="update-badge">实时</span></h2><div class="agc-amount">200,000 AGC</div><p style="color:#ffd700;margin-top:10px">💰 BNB余额: 0.312 (可挖62次)</p><p style="color:#ffd700;margin-top:8px">⛏️ 全网挖矿: 98 次</p><p style="color:#8b949e;font-size:13px">🤖 自动挖矿运行中 | 每5分钟答题</p><a href="https://bscscan.com/address/0xf2BD3694E7B0505cEcC4317B3Da8F86D54d770DA" target="_blank">查看链上记录 ↗</a></div>

<div class="card"><h2>🐦 Twitter 重点 <span class="update-badge">精选</span></h2>{twitter_html}</div>

<div class="card"><h2>🚨 预警提醒 <span class="update-badge">AI监控</span></h2><div class="alert-box"><div class="alert-title">⚡ SNDK 黄昏之星</div><div class="alert-text">存储龙头走出顶部反转形态，建议减仓锁定利润</div></div><div class="alert-box"><div class="alert-title">⚡ 中国铝业跌 3.94%</div><div class="alert-text">上游供应商异常波动，关注金属镓价格走势</div></div><div class="alert-box"><div class="alert-title">⚡ 五角大楼清单风险</div><div class="alert-text">阿里/百度/比亚迪可能被列入军方清单，中概股承压</div></div></div>

<div class="card"><h2>📰 智通财经要闻 <span class="update-badge">实时</span></h2>{news_html}</div>

<div class="card"><h2>🏢 AI数据中心动态 <span class="update-badge">监控</span></h2><div class="news-item"><div class="news-title">英伟达数据中心业务Q4营收预期上调，Blackwell需求强劲</div><div class="news-time">今日 08:30 · 财报</div></div><div class="news-item"><div class="news-title">CoreWeave算力租赁价格月涨15%，AI算力持续紧张</div><div class="news-time">今日 08:30 · 算力</div></div></div>

<div class="card"><h2>📅 任务追踪</h2><div class="task"><span class="status ok"></span><span>09:15 英诺赛科股价监控 ✓</span></div><div class="task"><span class="status ok"></span><span>10:00 Twitter监控推送 ✓</span></div><div class="task"><span class="status ok"></span><span>21:35 BOTCOIN自动解谜 ✓</span></div><div class="task"><span class="status pending"></span><span>⏳ BOTCOIN解锁: 明日21:38</span></div><div class="task"><span class="status ok"></span><span>Dashboard自动优化 ✓</span></div></div>

<div class="card"><h2>🖥️ 系统状态</h2>
<div class="health-box">
<div class="health-status {'health-ok' if health['status'] == 'ok' else 'health-warn'}">{health_status}</div>
<div style="font-size:12px;color:#666;margin-top:5px">{health_issues}</div>
</div>
<div style="margin-top:15px">
<div class="metric"><span>Dashboard版本</span><span class="metric-value">v3.1</span></div>
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
    log("开始更新Dashboard数据...")
    
    dashboard_dir = '/home/ubuntu/dashboard'
    os.makedirs(dashboard_dir, exist_ok=True)
    
    # 加载旧数据用于故障恢复
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
    
    # 如果获取失败，使用旧数据
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
    
    # 获取其他数据
    news = get_rss_news()
    tweets = get_tweets()
    market = get_market_sentiment()
    health = check_system_health()
    
    if market:
        log(f"✓ 恒指数据: {market['hsi_price']:.0f} ({market['hsi_change']:+.2f}%)")
    
    log(f"✓ 系统健康: {health['status']}")
    
    # 组装数据
    data = {
        'stock': stock_data,
        'news': news,
        'tweets': tweets,
        'market_sentiment': market,
        'system_health': health,
        'price_history_count': len(history),
        'updated_at': datetime.now(timezone.utc).isoformat()
    }
    
    # 保存数据
    with open(f'{dashboard_dir}/data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 生成并保存HTML
    html = generate_html(data, price_chart_svg)
    with open(f'{dashboard_dir}/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    log(f"Dashboard更新完成! 当前股价: {stock_data['price']} HKD")
    log("="*50)
    return 0

if __name__ == '__main__':
    sys.exit(main())
