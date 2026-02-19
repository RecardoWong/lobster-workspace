#!/usr/bin/env python3
"""
币安 API 获取实时价格并更新 Dashboard
"""

import urllib.request
import json
import re
from datetime import datetime

def get_binance_price(symbol):
    """从币安获取实时价格"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return {
                'price': float(data['lastPrice']),
                'change': float(data['priceChangePercent']),
                'symbol': symbol
            }
    except Exception as e:
        print(f"❌ 获取 {symbol} 失败: {e}")
        return None

def update_dashboard():
    """更新 Dashboard HTML"""
    # 获取 BTC 价格
    btc = get_binance_price('BTCUSDT')
    
    if not btc:
        print("❌ 无法获取价格")
        return
    
    print(f"✅ BTC: ${btc['price']:,.2f} ({btc['change']:+.2f}%)")
    
    # 读取 Dashboard HTML
    html_path = '/root/.openclaw/workspace/lobster-workspace/dashboard/index.html'
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新比特币价格
    # 找到 id="btcValue" 和 id="btcChange" 并更新
    
    # 更新价格数值
    content = re.sub(
        r'(<div class="overview-value" id="btcValue")>[^<]+</div>',
        rf'\1>${btc["price"]:,.0f}</div>',
        content
    )
    
    # 更新涨跌幅
    change_class = 'up' if btc['change'] >= 0 else 'down'
    change_sign = '+' if btc['change'] >= 0 else ''
    
    content = re.sub(
        r'(<div class="overview-change [^"]*" id="btcChange")>[^<]+</div>',
        rf'\1>{change_sign}{btc["change"]:.2f}%</div>',
        content
    )
    
    # 更新最后更新时间
    now = datetime.now().strftime('%m/%d %H:%M')
    content = re.sub(
        r'(<div class="last-update" id="lastUpdate">)最后更新:[^<]+</div>',
        rf'\1最后更新: {now}</div>',
        content
    )
    
    # 保存
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Dashboard 已更新 ({now})")
    
    # 部署到服务器
    import subprocess
    deploy_cmd = """
    cd /root/.openclaw/workspace/lobster-workspace/dashboard && 
    scp -i /root/.ssh/lobster_deploy -o StrictHostKeyChecking=no index.html ubuntu@43.160.229.161:/home/ubuntu/ &&
    ssh -i /root/.ssh/lobster_deploy -o StrictHostKeyChecking=no ubuntu@43.160.229.161 'sudo cp /home/ubuntu/index.html /var/www/html/ && sudo chown www-data:www-data /var/www/html/index.html'
    """
    
    try:
        result = subprocess.run(deploy_cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ 已部署到服务器")
        else:
            print(f"⚠️ 部署警告")
    except Exception as e:
        print(f"❌ 部署失败: {e}")

if __name__ == '__main__':
    print(f"{'='*50}")
    print("🪙 币安价格更新")
    print(f"{'='*50}")
    update_dashboard()
    print(f"{'='*50}")
