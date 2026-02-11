#!/usr/bin/env python3
"""
新发射 Memecoin 监控 - 抓刚发射的币
专注 Clanker/Bankr/Pump.fun 新发射
"""

import requests
import json
from datetime import datetime, timedelta
import time

# 发射平台合约地址
LAUNCH_PLATFORMS = {
    'clanker': '0x1bc0c42215582d5A085795f4baDbaC3ff36d1Bcb',  # Clanker工厂
    'bankr': '0x3485B01a2C3E5b3C6E8F9A2B4C5D6E7F8A9B0C1D',  # Bankr工厂
}

class NewLaunchMonitor:
    def __init__(self):
        self.seen_launches = set()
        
    def scan_new_launches(self):
        """扫描新发射的币"""
        headers = {'User-Agent': 'Mozilla/5.0'}
        new_launches = []
        
        # 1. 搜索 Clanker 新发射
        print("🔍 扫描 Clanker 新发射...")
        url = "https://api.dexscreener.com/latest/dex/search?q=clanker"
        try:
            r = requests.get(url, headers=headers, timeout=15)
            data = r.json()
            
            for pair in data.get('pairs', [])[:20]:
                if pair.get('chainId', '').lower() != 'base':
                    continue
                
                address = pair.get('baseToken', {}).get('address')
                symbol = pair.get('baseToken', {}).get('symbol')
                created = pair.get('pairCreatedAt', '')
                
                if not address or address in self.seen_launches:
                    continue
                
                # 检查是否新创建 (< 2小时)
                if created:
                    try:
                        created_time = datetime.fromtimestamp(int(created)/1000)
                        age_hours = (datetime.now() - created_time).total_seconds() / 3600
                        
                        if age_hours < 2:  # 2小时内新发射
                            new_launches.append({
                                'platform': 'Clanker',
                                'chain': 'Base',
                                'symbol': symbol,
                                'address': address,
                                'age_hours': round(age_hours, 1),
                                'price': float(pair.get('priceUsd') or 0),
                                'mcap': float(pair.get('marketCap') or 0),
                                'volume': float(pair.get('volume', {}).get('h24') or 0),
                                'dex_url': f"https://dexscreener.com/base/{address}"
                            })
                            self.seen_launches.add(address)
                    except:
                        pass
        except Exception as e:
            print(f"⚠️ Clanker扫描失败: {e}")
        
        # 2. 搜索 Bankr 新发射
        print("🔍 扫描 Bankr 新发射...")
        url = "https://api.dexscreener.com/latest/dex/search?q=bankr"
        try:
            r = requests.get(url, headers=headers, timeout=15)
            data = r.json()
            
            for pair in data.get('pairs', [])[:20]:
                if pair.get('chainId', '').lower() != 'base':
                    continue
                
                address = pair.get('baseToken', {}).get('address')
                symbol = pair.get('baseToken', {}).get('symbol')
                created = pair.get('pairCreatedAt', '')
                
                if not address or address in self.seen_launches:
                    continue
                
                if created:
                    try:
                        created_time = datetime.fromtimestamp(int(created)/1000)
                        age_hours = (datetime.now() - created_time).total_seconds() / 3600
                        
                        if age_hours < 2:
                            new_launches.append({
                                'platform': 'Bankr',
                                'chain': 'Base',
                                'symbol': symbol,
                                'address': address,
                                'age_hours': round(age_hours, 1),
                                'price': float(pair.get('priceUsd') or 0),
                                'mcap': float(pair.get('marketCap') or 0),
                                'volume': float(pair.get('volume', {}).get('h24') or 0),
                                'dex_url': f"https://dexscreener.com/base/{address}"
                            })
                            self.seen_launches.add(address)
                    except:
                        pass
        except Exception as e:
            print(f"⚠️ Bankr扫描失败: {e}")
        
        # 3. 搜索 Solana Pump.fun 新发射
        print("🔍 扫描 Pump.fun 新发射...")
        url = "https://api.dexscreener.com/latest/dex/search?q=pump"
        try:
            r = requests.get(url, headers=headers, timeout=15)
            data = r.json()
            
            for pair in data.get('pairs', [])[:20]:
                if pair.get('chainId', '').lower() != 'solana':
                    continue
                
                address = pair.get('baseToken', {}).get('address')
                symbol = pair.get('baseToken', {}).get('symbol')
                created = pair.get('pairCreatedAt', '')
                
                if not address or address in self.seen_launches:
                    continue
                
                if created:
                    try:
                        created_time = datetime.fromtimestamp(int(created)/1000)
                        age_hours = (datetime.now() - created_time).total_seconds() / 3600
                        
                        if age_hours < 2:
                            new_launches.append({
                                'platform': 'Pump.fun',
                                'chain': 'Solana',
                                'symbol': symbol,
                                'address': address,
                                'age_hours': round(age_hours, 1),
                                'price': float(pair.get('priceUsd') or 0),
                                'mcap': float(pair.get('marketCap') or 0),
                                'volume': float(pair.get('volume', {}).get('h24') or 0),
                                'dex_url': f"https://dexscreener.com/solana/{address}"
                            })
                            self.seen_launches.add(address)
                    except:
                        pass
        except Exception as e:
            print(f"⚠️ Pump.fun扫描失败: {e}")
        
        # 4. 搜索 BSC Four.meme 新发射
        print("🔍 扫描 Four.meme (BSC) 新发射...")
        url = "https://api.dexscreener.com/latest/dex/search?q=meme"
        try:
            r = requests.get(url, headers=headers, timeout=15)
            data = r.json()
            
            for pair in data.get('pairs', [])[:20]:
                if pair.get('chainId', '').lower() != 'bsc':
                    continue
                
                address = pair.get('baseToken', {}).get('address')
                symbol = pair.get('baseToken', {}).get('symbol')
                created = pair.get('pairCreatedAt', '')
                
                if not address or address in self.seen_launches:
                    continue
                
                if created:
                    try:
                        created_time = datetime.fromtimestamp(int(created)/1000)
                        age_hours = (datetime.now() - created_time).total_seconds() / 3600
                        
                        if age_hours < 2:
                            new_launches.append({
                                'platform': 'Four.meme',
                                'chain': 'BSC',
                                'symbol': symbol,
                                'address': address,
                                'age_hours': round(age_hours, 1),
                                'price': float(pair.get('priceUsd') or 0),
                                'mcap': float(pair.get('marketCap') or 0),
                                'volume': float(pair.get('volume', {}).get('h24') or 0),
                                'dex_url': f"https://dexscreener.com/bsc/{address}"
                            })
                            self.seen_launches.add(address)
                    except:
                        pass
        except Exception as e:
            print(f"⚠️ Four.meme扫描失败: {e}")
        
        return new_launches


if __name__ == "__main__":
    print("="*70)
    print("🚀 新发射 Memecoin 扫描")
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print("="*70)
    print()
    
    monitor = NewLaunchMonitor()
    launches = monitor.scan_new_launches()
    
    if launches:
        print(f"\n🎉 发现 {len(launches)} 个新发射！\n")
        for coin in launches:
            emoji = "🔶" if coin['chain'] == 'Base' else "🔷"
            print(f"{emoji} {coin['platform']} | ${coin['symbol']}")
            print(f"   发射时间: {coin['age_hours']}小时前")
            print(f"   价格: ${coin['price']:.8f}")
            print(f"   市值: ${coin['mcap']/1000:.1f}K")
            print(f"   CA: {coin['address']}")
            print(f"   链接: {coin['dex_url']}")
            print()
    else:
        print("\n📭 过去2小时暂无新发射")
        print("(市场较冷清，或需要更频繁监控)")
    
    print("="*70)
