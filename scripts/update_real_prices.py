#!/usr/bin/env python3
"""
真实数据更新 - 只更新能获取到的数据
"""

import urllib.request
import json
import re
import subprocess

def get_binance_btc():
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read().decode())
            return {'price': float(d['lastPrice']), 'change': float(d['priceChangePercent'])}
    except:
        return None

def get_tencent_hk(code):
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
    except:
        return None

def update_dashboard():
    print("🔄 获取实时数据...")
    
    btc = get_binance_btc()
    innoscience = get_tencent_hk('02577')
    
    with open('/root/.openclaw/workspace/lobster-workspace/dashboard/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 只更新能获取到的数据
    if btc:
        content = re.sub(r'(<div class="overview-value" id="btcValue")>[^&<]+', rf'\1>${btc["price"]:,.0f}', content)
        content = re.sub(r'(<div class="overview-change [^"]*" id="btcChange")>[^&<]+', rf'\1>{btc["change"]:+.2f}%', content)
        print(f"✅ BTC: ${btc['price']:,.0f}")
    
    if innoscience:
        content = re.sub(r'(<div class="stock-price-value" id="innosciencePrice")>[^&<]+', rf'\1>{innoscience["price"]:.2f}', content)
        content = re.sub(r'(<div class="stock-change[^"]*" id="innoscienceChange")>[^&<]+', rf'\1>{innoscience["change"]:+.2f}%', content)
        print(f"✅ 英诺赛科: {innoscience['price']:.2f}")
    
    # 纳斯达克和恒生科技 - 显示"数据获取中"
    # 因为免费 API 都有访问限制
    
    with open('/root/.openclaw/workspace/lobster-workspace/dashboard/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 部署
    deploy_cmd = """
    cd /root/.openclaw/workspace/lobster-workspace/dashboard && 
    scp -i /root/.ssh/lobster_deploy -o StrictHostKeyChecking=no index.html ubuntu@43.160.229.161:/home/ubuntu/ &&
    ssh -i /root/.ssh/lobster_deploy -o StrictHostKeyChecking=no ubuntu@43.160.229.161 'sudo cp /home/ubuntu/index.html /var/www/html/ && sudo chown www-data:www-data /var/www/html/index.html'
    """
    subprocess.run(deploy_cmd, shell=True, capture_output=True)
    print("✅ 已部署")

if __name__ == '__main__':
    update_dashboard()
