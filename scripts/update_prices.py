#!/usr/bin/env python3
"""
实时股价更新 - 使用腾讯财经
"""

import urllib.request
import re
import subprocess
from datetime import datetime

def get_tencent_us(symbol):
    try:
        url = f"https://qt.gtimg.cn/q=us.{symbol}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            text = r.read().decode('gbk')
            match = re.search(r'"([^"]+)"', text)
            if match:
                data = match.group(1).split('~')
                return {
                    'price': float(data[3]),
                    'change': ((float(data[3]) - float(data[4])) / float(data[4])) * 100
                }
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
                return {'price': price, 'change': ((price - prev) / prev) * 100}
    except:
        return None

# 获取数据
print("🔄 获取实时数据...")
nasdaq = get_tencent_us('IXIC')
hstech = get_tencent_hk('HSTECH')
innoscience = get_tencent_hk('02577')

# 读取HTML
with open('/root/.openclaw/workspace/lobster-workspace/dashboard/index.html', 'r') as f:
    content = f.read()

import re as regex

# 更新数据
if nasdaq:
    content = regex.sub(r'(<div class="overview-value" id="nasdaqValue")>[^\u003c]+', rf'\1>{nasdaq["price"]:,.2f}', content)
    content = regex.sub(r'(<div class="overview-change[^"]*" id="nasdaqChange")>[^\u003c]+', rf'\1>{nasdaq["change"]:+.2f}%', content)
    print(f"✅ 纳斯达克: {nasdaq['price']:,.2f} ({nasdaq['change']:+.2f}%)")

if hstech:
    content = regex.sub(r'(<div class="overview-value" id="hsTechValue")>[^\u003c]+', rf'\1>{hstech["price"]:,.2f}', content)
    content = regex.sub(r'(<div class="overview-change[^"]*" id="hsTechChange")>[^\u003c]+', rf'\1>{hstech["change"]:+.2f}%', content)
    print(f"✅ 恒生科技: {hstech['price']:,.2f} ({hstech['change']:+.2f}%)")

if innoscience:
    content = regex.sub(r'(<div class="stock-price-value" id="innosciencePrice")>[^\u003c]+', rf'\1>{innoscience["price"]:.2f}', content)
    content = regex.sub(r'(<div class="stock-change[^"]*" id="innoscienceChange")>[^\u003c]+', rf'\1>{innoscience["change"]:+.2f}%', content)
    print(f"✅ 英诺赛科: {innoscience['price']:.2f} ({innoscience['change']:+.2f}%)")

# 更新时间
now = datetime.now().strftime('%m/%d %H:%M')
content = regex.sub(r'(<div class="last-update" id="lastUpdate">)最后更新:[^\u003c]+', rf'\1最后更新: {now}', content)

# 保存
with open('/root/.openclaw/workspace/lobster-workspace/dashboard/index.html', 'w') as f:
    f.write(content)

# 部署
deploy_cmd = """
cd /root/.openclaw/workspace/lobster-workspace/dashboard && 
scp -i /root/.ssh/lobster_deploy -o StrictHostKeyChecking=no index.html ubuntu@43.160.229.161:/home/ubuntu/ &&
ssh -i /root/.ssh/lobster_deploy -o StrictHostKeyChecking=no ubuntu@43.160.229.161 'sudo cp /home/ubuntu/index.html /var/www/html/ && sudo chown www-data:www-data /var/www/html/index.html'
"""
subprocess.run(deploy_cmd, shell=True, capture_output=True)
print(f"✅ 已部署 ({now})")
