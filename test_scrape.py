#!/usr/bin/env python3
"""
股价数据爬取 - 从东方财富网页抓取
"""

import urllib.request
import re
from datetime import datetime

def fetch_nasdaq():
    """从东方财富抓取纳斯达克"""
    try:
        url = "https://quote.eastmoney.com/globalindex/IXIC.html"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://quote.eastmoney.com/'
        })
        
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode('utf-8')
            
            # 查找价格
            price_match = re.search(r'id="price9"[^>]*>([0-9,.]+)', html)
            change_match = re.search(r'id="km2"[^>]*>([+-]?[0-9.]+)%', html)
            
            if price_match:
                price = float(price_match.group(1).replace(',', ''))
                change = float(change_match.group(1)) if change_match else 0
                return {'price': price, 'change': change}
    except Exception as e:
        print(f"纳斯达克抓取失败: {e}")
    return None

def fetch_hstech():
    """从东方财富抓取恒生科技"""
    try:
        url = "https://quote.eastmoney.com/globalindex/HSTECH.html"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://quote.eastmoney.com/'
        })
        
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode('utf-8')
            
            price_match = re.search(r'id="price9"[^>]*>([0-9,.]+)', html)
            change_match = re.search(r'id="km2"[^>]*>([+-]?[0-9.]+)%', html)
            
            if price_match:
                price = float(price_match.group(1).replace(',', ''))
                change = float(change_match.group(1)) if change_match else 0
                return {'price': price, 'change': change}
    except Exception as e:
        print(f"恒生科技抓取失败: {e}")
    return None

if __name__ == '__main__':
    print("测试数据爬取...")
    nasdaq = fetch_nasdaq()
    hstech = fetch_hstech()
    
    if nasdaq:
        print(f"✅ 纳斯达克: {nasdaq['price']:,.2f} ({nasdaq['change']:+.2f}%)")
    else:
        print("❌ 纳斯达克获取失败")
    
    if hstech:
        print(f"✅ 恒生科技: {hstech['price']:,.2f} ({hstech['change']:+.2f}%)")
    else:
        print("❌ 恒生科技获取失败")
