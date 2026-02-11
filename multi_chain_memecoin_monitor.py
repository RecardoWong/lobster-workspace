#!/usr/bin/env python3
"""
多链 Memecoin 发射平台监控
整合 Pump.fun (Solana) + Clanker/Bankr (Base) + Four.meme (BSC)
抓第一手新币，比扫链更前置
"""

import requests
import json
from datetime import datetime
from typing import List, Dict
import time

class MemecoinLauncherMonitor:
    """多链发射平台监控器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    # ==================== Solana - Pump.fun ====================
    def get_pumpfun_new_tokens(self, limit: int = 20) -> List[Dict]:
        """
        获取 Pump.fun 最新发射的代币
        Pump.fun API: https://pump.fun/api/... (需要逆向或第三方API)
        """
        print("🔍 获取 Pump.fun (Solana) 新币...")
        
        # 使用 Solana FM API 或 DexScreener 筛选新币
        # 这里用 DexScreener 作为替代方案
        try:
            url = "https://api.dexscreener.com/latest/dex/search?q=pump"
            r = self.session.get(url, headers=self.headers, timeout=30)
            data = r.json()
            
            tokens = []
            for pair in data.get('pairs', [])[:limit]:
                if pair.get('chainId', '').lower() == 'solana':
                    tokens.append({
                        'chain': 'Solana',
                        'platform': 'Pump.fun',
                        'symbol': pair.get('baseToken', {}).get('symbol', 'N/A'),
                        'name': pair.get('baseToken', {}).get('name', 'N/A'),
                        'address': pair.get('baseToken', {}).get('address', ''),
                        'priceUsd': float(pair.get('priceUsd') or 0),
                        'volume24h': float(pair.get('volume', {}).get('h24') or 0),
                        'priceChange24h': float(pair.get('priceChange', {}).get('h24') or 0),
                        'liquidityUsd': float(pair.get('liquidity', {}).get('usd') or 0),
                        'createdAt': pair.get('pairCreatedAt', ''),
                    })
            
            return tokens
        except Exception as e:
            print(f"⚠️ Pump.fun 获取失败: {e}")
            return []
    
    # ==================== Base - Clanker ====================
    def get_clanker_new_tokens(self, limit: int = 20) -> List[Dict]:
        """
        获取 Clanker (Base) 最新发射的代币
        """
        print("🔍 获取 Clanker (Base) 新币...")
        
        try:
            # 搜索 Clanker 相关代币
            url = "https://api.dexscreener.com/latest/dex/search?q=clanker"
            r = self.session.get(url, headers=self.headers, timeout=30)
            data = r.json()
            
            tokens = []
            seen = set()
            
            for pair in data.get('pairs', []):
                if pair.get('chainId', '').lower() != 'base':
                    continue
                
                addr = pair.get('baseToken', {}).get('address', '')
                if addr in seen:
                    continue
                seen.add(addr)
                
                if len(tokens) >= limit:
                    break
                
                tokens.append({
                    'chain': 'Base',
                    'platform': 'Clanker',
                    'symbol': pair.get('baseToken', {}).get('symbol', 'N/A'),
                    'name': pair.get('baseToken', {}).get('name', 'N/A'),
                    'address': addr,
                    'priceUsd': float(pair.get('priceUsd') or 0),
                    'volume24h': float(pair.get('volume', {}).get('h24') or 0),
                    'priceChange24h': float(pair.get('priceChange', {}).get('h24') or 0),
                    'liquidityUsd': float(pair.get('liquidity', {}).get('usd') or 0),
                    'createdAt': pair.get('pairCreatedAt', ''),
                })
            
            return tokens
        except Exception as e:
            print(f"⚠️ Clanker 获取失败: {e}")
            return []
    
    # ==================== Base - Bankr ====================
    def get_bankr_new_tokens(self, limit: int = 20) -> List[Dict]:
        """
        获取 Bankr (Base) 最新发射的代币
        """
        print("🔍 获取 Bankr (Base) 新币...")
        
        try:
            url = "https://api.dexscreener.com/latest/dex/search?q=bankr"
            r = self.session.get(url, headers=self.headers, timeout=30)
            data = r.json()
            
            tokens = []
            seen = set()
            
            for pair in data.get('pairs', []):
                if pair.get('chainId', '').lower() != 'base':
                    continue
                
                addr = pair.get('baseToken', {}).get('address', '')
                if addr in seen:
                    continue
                seen.add(addr)
                
                if len(tokens) >= limit:
                    break
                
                tokens.append({
                    'chain': 'Base',
                    'platform': 'Bankr',
                    'symbol': pair.get('baseToken', {}).get('symbol', 'N/A'),
                    'name': pair.get('baseToken', {}).get('name', 'N/A'),
                    'address': addr,
                    'priceUsd': float(pair.get('priceUsd') or 0),
                    'volume24h': float(pair.get('volume', {}).get('h24') or 0),
                    'priceChange24h': float(pair.get('priceChange', {}).get('h24') or 0),
                    'liquidityUsd': float(pair.get('liquidity', {}).get('usd') or 0),
                    'createdAt': pair.get('pairCreatedAt', ''),
                })
            
            return tokens
        except Exception as e:
            print(f"⚠️ Bankr 获取失败: {e}")
            return []
    
    # ==================== BSC - Four.meme ====================
    def get_fourmeme_new_tokens(self, limit: int = 20) -> List[Dict]:
        """
        获取 Four.meme (BSC) 最新发射的代币
        """
        print("🔍 获取 Four.meme (BSC) 新币...")
        
        try:
            # 搜索 BSC 新币
            url = "https://api.dexscreener.com/latest/dex/search?q=meme"
            r = self.session.get(url, headers=self.headers, timeout=30)
            data = r.json()
            
            tokens = []
            seen = set()
            
            for pair in data.get('pairs', []):
                if pair.get('chainId', '').lower() != 'bsc':
                    continue
                
                addr = pair.get('baseToken', {}).get('address', '')
                if addr in seen:
                    continue
                seen.add(addr)
                
                if len(tokens) >= limit:
                    break
                
                tokens.append({
                    'chain': 'BSC',
                    'platform': 'Four.meme',
                    'symbol': pair.get('baseToken', {}).get('symbol', 'N/A'),
                    'name': pair.get('baseToken', {}).get('name', 'N/A'),
                    'address': addr,
                    'priceUsd': float(pair.get('priceUsd') or 0),
                    'volume24h': float(pair.get('volume', {}).get('h24') or 0),
                    'priceChange24h': float(pair.get('priceChange', {}).get('h24') or 0),
                    'liquidityUsd': float(pair.get('liquidity', {}).get('usd') or 0),
                    'createdAt': pair.get('pairCreatedAt', ''),
                })
            
            return tokens
        except Exception as e:
            print(f"⚠️ Four.meme 获取失败: {e}")
            return []
    
    # ==================== 生成综合报告 ====================
    def generate_multi_chain_report(self) -> str:
        """生成多链发射平台综合报告"""
        print("="*70)
        print("🚀 多链 Memecoin 发射平台监控报告")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*70)
        print()
        
        lines = []
        
        # 1. Pump.fun (Solana)
        pump_tokens = self.get_pumpfun_new_tokens(limit=10)
        if pump_tokens:
            lines.append("🔷 Solana - Pump.fun")
            lines.append("-"*70)
            for i, t in enumerate(pump_tokens[:5], 1):
                volume_k = t['volume24h'] / 1000
                change = t['priceChange24h']
                emoji = "🚀" if change > 50 else "📈" if change > 0 else "📉"
                lines.append(f"{i}. {emoji} ${t['symbol']}")
                lines.append(f"   价格: ${t['priceUsd']:.8f} | 24h: {change:+.1f}%")
                lines.append(f"   交易量: ${volume_k:.1f}K | 合约: {t['address'][:12]}...")
                lines.append("")
        
        # 2. Clanker (Base)
        clanker_tokens = self.get_clanker_new_tokens(limit=10)
        if clanker_tokens:
            lines.append("\n🔶 Base - Clanker")
            lines.append("-"*70)
            for i, t in enumerate(clanker_tokens[:5], 1):
                volume_k = t['volume24h'] / 1000
                change = t['priceChange24h']
                emoji = "🚀" if change > 50 else "📈" if change > 0 else "📉"
                lines.append(f"{i}. {emoji} ${t['symbol']}")
                lines.append(f"   价格: ${t['priceUsd']:.6f} | 24h: {change:+.1f}%")
                lines.append(f"   交易量: ${volume_k:.1f}K | 合约: {t['address'][:12]}...")
                lines.append("")
        
        # 3. Bankr (Base)
        bankr_tokens = self.get_bankr_new_tokens(limit=10)
        if bankr_tokens:
            lines.append("\n🔶 Base - Bankr")
            lines.append("-"*70)
            for i, t in enumerate(bankr_tokens[:5], 1):
                volume_k = t['volume24h'] / 1000
                change = t['priceChange24h']
                emoji = "🚀" if change > 50 else "📈" if change > 0 else "📉"
                lines.append(f"{i}. {emoji} ${t['symbol']}")
                lines.append(f"   价格: ${t['priceUsd']:.6f} | 24h: {change:+.1f}%")
                lines.append(f"   交易量: ${volume_k:.1f}K | 合约: {t['address'][:12]}...")
                lines.append("")
        
        # 4. Four.meme (BSC)
        four_tokens = self.get_fourmeme_new_tokens(limit=10)
        if four_tokens:
            lines.append("\n🟢 BSC - Four.meme")
            lines.append("-"*70)
            for i, t in enumerate(four_tokens[:5], 1):
                volume_k = t['volume24h'] / 1000
                change = t['priceChange24h']
                emoji = "🚀" if change > 50 else "📈" if change > 0 else "📉"
                lines.append(f"{i}. {emoji} ${t['symbol']}")
                lines.append(f"   价格: ${t['priceUsd']:.8f} | 24h: {change:+.1f}%")
                lines.append(f"   交易量: ${volume_k:.1f}K | 合约: {t['address'][:12]}...")
                lines.append("")
        
        # 统计
        total = len(pump_tokens) + len(clanker_tokens) + len(bankr_tokens) + len(four_tokens)
        lines.append("="*70)
        lines.append(f"📊 总计发现 {total} 个新币")
        lines.append("="*70)
        
        return "\n".join(lines)


def main():
    """主函数"""
    monitor = MemecoinLauncherMonitor()
    report = monitor.generate_multi_chain_report()
    print(report)
    
    # 保存到文件
    with open('/tmp/multi_chain_memecoins.txt', 'w') as f:
        f.write(report)
    
    print("\n✅ 报告已保存到: /tmp/multi_chain_memecoins.txt")


if __name__ == "__main__":
    main()
