#!/usr/bin/env python3
"""
Memecoin 定时监控 - 每小时扫描热点
"""

import requests
import json
from datetime import datetime
import time

# 配置
MIN_VOLUME = 10000      # 最小交易量 $10K
MIN_CHANGE = 20         # 最小涨幅 20%
CHECK_INTERVAL = 3600   # 检查间隔 1小时

class MemecoinMonitor:
    def __init__(self):
        self.seen_coins = set()  # 已发送的币，避免重复
        
    def scan_hot_coins(self):
        """扫描热点币"""
        headers = {'User-Agent': 'Mozilla/5.0'}
        keywords = ['clanker', 'bankr', 'base', 'solana', 'meme']
        hot_coins = []
        
        for kw in keywords:
            url = f"https://api.dexscreener.com/latest/dex/search?q={kw}"
            try:
                r = requests.get(url, headers=headers, timeout=10)
                data = r.json()
                
                for pair in data.get('pairs', [])[:10]:
                    chain = pair.get('chainId', '').lower()
                    if chain not in ['base', 'solana']:
                        continue
                    
                    address = pair.get('baseToken', {}).get('address')
                    symbol = pair.get('baseToken', {}).get('symbol')
                    
                    if not address or address in self.seen_coins:
                        continue
                    
                    mcap = float(pair.get('marketCap') or 0)
                    volume = float(pair.get('volume', {}).get('h24') or 0)
                    change = float(pair.get('priceChange', {}).get('h24') or 0)
                    
                    # 热点标准
                    if (change > MIN_CHANGE or volume > 100000) and mcap < 10000000:
                        hot_coins.append({
                            'chain': chain.upper(),
                            'symbol': symbol,
                            'change': change,
                            'volume': volume,
                            'mcap': mcap,
                            'address': address,
                            'dex_url': f"https://dexscreener.com/{chain}/{address}"
                        })
                        self.seen_coins.add(address)
            except:
                continue
            time.sleep(0.3)
        
        return hot_coins

if __name__ == "__main__":
    monitor = MemecoinMonitor()
    coins = monitor.scan_hot_coins()
    print(f"发现 {len(coins)} 个新热点币")
    for c in coins:
        print(f"{c['symbol']} | {c['change']:+.1f}% | {c['dex_url']}")
