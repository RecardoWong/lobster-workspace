#!/usr/bin/env python3
"""
获取真实股价数据
"""

import urllib.request
import json
import re
from datetime import datetime

def get_binance_btc():
    """币安 BTC"""
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read().decode())
            return {
                'price': float(d['lastPrice']),
                'change': float(d['priceChangePercent'])
            }
    except Exception as e:
        print(f"BTC 失败: {e}")
        return None

def get_sina_index(symbol):
    """新浪财经指数"""
    try:
        url = f"https://hq.sinajs.cn/list={symbol}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.sina.com.cn'})
        with urllib.request.urlopen(req, timeout=10) as r:
            text = r.read().decode('gbk')
            match = re.search(r'"([^"]+)"', text)
            if match:
                data = match.group(1).split(',')
                if len(data) >= 3:
                    return {
                        'price': float(data[1]),
                        'change': float(data[3])
                    }
    except Exception as e:
        print(f"{symbol} 失败: {e}")
        return None

def get_tencent_hk(code):
    """腾讯财经港股"""
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
                change = ((price - prev) / prev) * 100
                return {'price': price, 'change': change}
    except Exception as e:
        print(f"港股{code} 失败: {e}")
        return None

def update_dashboard():
    print("🔄 获取实时数据...")
    
    btc = get_binance_btc()
    nasdaq = get_sina_index('ixic')
    hstech = get_sina_index('hs_tech')
    innoscience = get_tencent_hk('02577')
    
    html_path = '/root/.openclaw/workspace/lobster-workspace/dashboard/index.html'
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    updates = []
    
    if btc:
        content = re.sub(r'(<div class="overview-value" id="btcValue")>[^<]+</div>', 
                        rf'\1>${btc["price"]:,.0f}</div>', content)
        content = re.sub(r'(<div class="overview-change [^"]*" id="btcChange")>[^<]+</div>',
                        rf'\1>{btc["change"]:+.2f}%</div>', content)
        updates.append(f"BTC ${btc['price']:,.0f}")
    
    if nasdaq:
        content = re.sub(r'(<div class="overview-value" id="nasdaqValue")>[^<]+</div>',
                        rf'\1>{nasdaq["price"]:,.0f}</div>', content)
        content = re.sub(r'(<div class="overview-change [^"]*" id="nasdaqChange")>[^<]+</div>',
                        rf'\1>{nasdaq["change"]:+.2f}%</div>', content)
        updates.append(f"纳斯达克 {nasdaq['price']:,.0f}")
    
    if hstech:
        content = re.sub(r'(<div class="overview-value" id="hsTechValue")>[^<]+</div>',
                        rf'\1>{hstech["price"]:,.0f}</div>', content)
        content = re.sub(r'(<div class="overview-change [^"]*" id="hsTechChange")>[^<]+</div>',
                        rf'\1>{hstech["change"]:+.2f}%</div>', content)
        updates.append(f"恒生科技 {hstech['price']:,.0f}")
    
    if innoscience:
        content = re.sub(r'(<div class="stock-price-value" id="innosciencePrice")>[^<]+</div>',
                        rf'\1>{innoscience["price"]:.2f}</div>', content)
        content = re.sub(r'(<div class="stock-change[^"]*" id="innoscienceChange")>[^<]+</div>',
                        rf'\1>{innoscience["change"]:+.2f}%</div>', content)
        updates.append(f"英诺赛科 {innoscience['price']:.2f}")
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 更新: {', '.join(updates)}")
    
    # 部署
    import subprocess
    deploy_cmd = """
    cd /root/.openclaw/workspace/lobster-workspace/dashboard && 
    scp -i /root/.ssh/lobster_deploy -o StrictHostKeyChecking=no index.html ubuntu@43.160.229.161:/home/ubuntu/ &&
    ssh -i /root/.ssh/lobster_deploy -o StrictHostKeyChecking=no ubuntu@43.160.229.161 'sudo cp /home/ubuntu/index.html /var/www/html/ && sudo chown www-data:www-data /var/www/html/index.html'
    """
    subprocess.run(deploy_cmd, shell=True, capture_output=True)
    print("✅ 已部署")

if __name__ == '__main__':
    update_dashboard()
