#!/usr/bin/env python3
"""
热点 Memecoin 整理工具 - 基于 DexScreener
比扫链更高效，数据更丰富
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
import time

class MemecoinScreener:
    """Memecoin 热点筛选器"""
    
    def __init__(self):
        self.base_url = "https://api.dexscreener.com/latest"
        self.session = requests.Session()
    
    def get_base_chain_hot_tokens(self, min_volume_24h: float = 10000) -> List[Dict]:
        """
        获取 Base chain 热门代币 - 通过搜索热门关键词
        
        Args:
            min_volume_24h: 最小24小时交易量（美元）
        
        Returns:
            按交易量排序的热门代币列表
        """
        print("🔍 正在获取 Base chain 热门代币...")
        
        # 搜索 Base chain 热门关键词
        hot_keywords = ['clanker', 'bankr', 'meme', 'ai', 'elon', 'based']
        all_tokens = []
        
        for keyword in hot_keywords:
            try:
                url = f"{self.base_url}/dex/search?q={keyword}"
                response = self.session.get(url, timeout=30)
                data = response.json()
                
                pairs = data.get('pairs', []) or []
                
                for pair in pairs:
                    if not pair or pair.get('chainId', '').lower() != 'base':
                        continue
                    
                    # 提取关键信息
                    token_info = {
                        'symbol': pair.get('baseToken', {}).get('symbol', 'N/A'),
                        'name': pair.get('baseToken', {}).get('name', 'N/A'),
                        'address': pair.get('baseToken', {}).get('address', ''),
                        'priceUsd': float(pair.get('priceUsd') or 0),
                        'volume24h': float(pair.get('volume', {}).get('h24') or 0),
                        'volumeChange24h': float(pair.get('volume', {}).get('change24h') or 0),
                        'priceChange24h': float(pair.get('priceChange', {}).get('h24') or 0),
                        'liquidityUsd': float(pair.get('liquidity', {}).get('usd') or 0),
                        'marketCap': float(pair.get('marketCap') or 0),
                        'fdv': float(pair.get('fdv') or 0),
                        'pairAddress': pair.get('pairAddress', ''),
                        'dexId': pair.get('dexId', ''),
                        'createdAt': pair.get('pairCreatedAt', ''),
                    }
                    
                    # 过滤低交易量
                    if token_info['volume24h'] >= min_volume_24h:
                        # 去重检查
                        if not any(t['address'] == token_info['address'] for t in all_tokens):
                            all_tokens.append(token_info)
                
                time.sleep(0.5)  # 避免请求过快
                
            except Exception as e:
                print(f"⚠️ 搜索 {keyword} 失败: {e}")
                continue
        
        # 按24h交易量排序
        all_tokens.sort(key=lambda x: x['volume24h'], reverse=True)
        
        return all_tokens
    
    def search_tokens(self, query: str, chain: str = "base") -> List[Dict]:
        """
        搜索特定代币
        
        Args:
            query: 搜索关键词（如 "AI", "Elon", "China"）
            chain: 链名（base, ethereum, bsc等）
        """
        print(f"🔍 搜索关键词: {query}...")
        
        url = f"{self.base_url}/dex/search?q={query}"
        
        try:
            response = self.session.get(url, timeout=30)
            data = response.json()
            
            pairs = data.get('pairs', [])
            
            # 过滤指定链
            chain_pairs = [p for p in pairs if p and p.get('chainId', '').lower() == chain.lower()]
            
            results = []
            for pair in chain_pairs[:20]:  # 取前20个
                results.append({
                    'symbol': pair.get('baseToken', {}).get('symbol', 'N/A'),
                    'name': pair.get('baseToken', {}).get('name', 'N/A'),
                    'address': pair.get('baseToken', {}).get('address', ''),
                    'priceUsd': float(pair.get('priceUsd', 0)),
                    'volume24h': float(pair.get('volume', {}).get('h24', 0)),
                    'priceChange24h': float(pair.get('priceChange', {}).get('h24', 0)),
                    'marketCap': float(pair.get('marketCap', 0)),
                })
            
            return results
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []
    
    def get_token_details(self, token_address: str) -> Dict:
        """获取特定代币详情"""
        url = f"{self.base_url}/dex/tokens/{token_address}"
        
        try:
            response = self.session.get(url, timeout=30)
            data = response.json()
            
            pairs = data.get('pairs', [])
            if not pairs:
                return {}
            
            # 取交易量最大的pair
            best_pair = max(pairs, key=lambda x: float(x.get('volume', {}).get('h24', 0)))
            
            return {
                'symbol': best_pair.get('baseToken', {}).get('symbol'),
                'name': best_pair.get('baseToken', {}).get('name'),
                'address': token_address,
                'priceUsd': float(best_pair.get('priceUsd', 0)),
                'volume24h': float(best_pair.get('volume', {}).get('h24', 0)),
                'volumeChange24h': float(best_pair.get('volume', {}).get('change24h', 0)),
                'priceChange5m': float(best_pair.get('priceChange', {}).get('m5', 0)),
                'priceChange1h': float(best_pair.get('priceChange', {}).get('h1', 0)),
                'priceChange24h': float(best_pair.get('priceChange', {}).get('h24', 0)),
                'liquidityUsd': float(best_pair.get('liquidity', {}).get('usd', 0)),
                'marketCap': float(best_pair.get('marketCap', 0)),
                'buys24h': int(best_pair.get('txns', {}).get('h24', {}).get('buys', 0)),
                'sells24h': int(best_pair.get('txns', {}).get('h24', {}).get('sells', 0)),
            }
            
        except Exception as e:
            print(f"❌ 获取详情失败: {e}")
            return {}
    
    def generate_hot_memecoin_report(self, top_n: int = 20) -> str:
        """生成热点 memecoin 报告"""
        print("="*70)
        print("🔥 Base Chain 热点 Memecoin 报告")
        print(f"⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*70)
        print()
        
        # 获取热门代币
        tokens = self.get_base_chain_hot_tokens(min_volume_24h=5000)
        
        if not tokens:
            return "❌ 获取数据失败"
        
        lines = []
        
        # 按不同维度分类
        
        # 1. 交易量最高
        lines.append("📊 24小时交易量 TOP 10")
        lines.append("-"*70)
        for i, t in enumerate(tokens[:10], 1):
            volume_m = t['volume24h'] / 1_000_000
            price_change = t['priceChange24h']
            emoji = "🚀" if price_change > 20 else "📈" if price_change > 0 else "📉"
            lines.append(f"{i}. {emoji} ${t['symbol']} | ${volume_m:.1f}M")
            lines.append(f"   价格: ${t['priceUsd']:.6f} | 24h: {price_change:+.1f}%")
            lines.append(f"   市值: ${t['marketCap']/1_000_000:.1f}M | 合约: {t['address'][:15]}...")
            lines.append("")
        
        # 2. 涨幅最大
        gainers = sorted([t for t in tokens if t['priceChange24h'] > 0], 
                        key=lambda x: x['priceChange24h'], reverse=True)[:5]
        
        if gainers:
            lines.append("\n🚀 24小时涨幅最大")
            lines.append("-"*70)
            for i, t in enumerate(gainers, 1):
                lines.append(f"{i}. 🚀 ${t['symbol']} | +{t['priceChange24h']:.1f}%")
                lines.append(f"   交易量: ${t['volume24h']/1_000_000:.1f}M")
                lines.append("")
        
        # 3. 新币（24小时内创建）
        # 需要额外逻辑判断创建时间
        
        return "\n".join(lines)


def main():
    """主函数"""
    screener = MemecoinScreener()
    
    # 生成热点报告
    report = screener.generate_hot_memecoin_report()
    print(report)
    
    # 保存到文件
    with open('/tmp/hot_memecoins_report.txt', 'w') as f:
        f.write(report)
    
    print("\n" + "="*70)
    print("✅ 报告已保存到: /tmp/hot_memecoins_report.txt")
    print("="*70)


if __name__ == "__main__":
    main()
