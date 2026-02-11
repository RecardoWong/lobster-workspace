#!/usr/bin/env python3
"""
Meme币实时监控系统 v3.0 - 演示版
每小时扫描Base链，提供原因分析和热点识别
"""

import urllib.request
import json
import random
from datetime import datetime
from typing import Dict, List, Optional

class BaseMemeMonitor:
    """Base链Meme币监控器"""
    
    def __init__(self):
        self.hotspots = []
        self.signals = []
    
    def get_base_hot_tokens(self) -> List[Dict]:
        """获取Base链热门代币"""
        print("🔍 正在扫描Base链...")
        
        try:
            # 使用DexScreener search API获取Base链代币
            url = "https://api.dexscreener.com/latest/dex/search?q=base%20chain"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                pairs = data.get('pairs', [])
                
                # 筛选Base链且符合条件的代币
                filtered = []
                seen_symbols = set()
                
                for pair in pairs:
                    chain = pair.get('chainId', '').lower()
                    if chain != 'base':
                        continue
                    
                    symbol = pair.get('baseToken', {}).get('symbol', '???')
                    if symbol in seen_symbols or symbol == '???':
                        continue
                    seen_symbols.add(symbol)
                    
                    liquidity = float(pair.get('liquidity', {}).get('usd', 0) or 0)
                    volume_24h = float(pair.get('volume', {}).get('h24', 0) or 0)
                    price_change = float(pair.get('priceChange', {}).get('h24', 0) or 0)
                    
                    # 只监控Clanker发布的币
                    # Clanker是OpenClaw的Token Factory，Base链AI Agent Launchpad
                    # CLANKER合约: 0x1bc0...6d1bcb
                    CLANKER_KEYWORDS = ['clanker', 'claw', 'ai', 'agent', 'bot', 'bankr', 'aixbt', 'luna', 'zerebro']
                    
                    symbol_lower = symbol.lower()
                    name_lower = pair.get('baseToken', {}).get('name', '').lower()
                    
                    # 检查是否为Clanker生态币
                    is_clanker = any(keyword in symbol_lower or keyword in name_lower 
                                     for keyword in CLANKER_KEYWORDS)
                    
                    # 同时需要是Meme币规模（排除超大市值）
                    is_meme_size = 10000 < liquidity < 100000000  # $10K - $100M
                    
                    if is_clanker and is_meme_size:
                        address = pair.get('baseToken', {}).get('address', '')
                        # 检查是否为新合约
                        is_new = self.db.is_new(address)
                        # 检查今天是否已出现过
                        today = datetime.now().strftime('%Y-%m-%d')
                        appears_today = False
                        if address.lower() in self.db.contract_history:
                            first_seen = self.db.contract_history[address.lower()].get('first_seen', '')
                            appears_today = today in first_seen or (datetime.now() - datetime.fromisoformat(first_seen.replace('Z', '+00:00'))).days == 0
                        
                        filtered.append({
                            'name': pair.get('baseToken', {}).get('name', 'Unknown'),
                            'symbol': symbol,
                            'address': address,
                            'price': float(pair.get('priceUsd', 0) or 0),
                            'liquidity': liquidity,
                            'volume_24h': volume_24h,
                            'change_24h': price_change,
                            'tx_count': (pair.get('txns', {}).get('h24', {}).get('buys', 0) or 0) + 
                                       (pair.get('txns', {}).get('h24', {}).get('sells', 0) or 0),
                            'pair_url': pair.get('url', ''),
                            'is_new': is_new,
                            'appears_today': appears_today
                        })
                        
                        # 新合约添加到数据库
                        if is_new:
                            self.db.add(address, {
                                'name': pair.get('baseToken', {}).get('name', 'Unknown'),
                                'symbol': symbol,
                                'first_seen_price': float(pair.get('priceUsd', 0) or 0)
                            })
                
                # 按交易量排序
                filtered.sort(key=lambda x: x['volume_24h'], reverse=True)
                print(f"✅ 找到 {len(filtered)} 个符合条件的Meme币")
                return filtered[:10]
                
        except Exception as e:
            print(f"❌ 获取数据失败: {e}")
            # 返回演示数据
            return self._generate_demo_data()
    
    def _generate_demo_data(self) -> List[Dict]:
        """生成演示数据"""
        print("⚠️ 使用演示数据...")
        demo_tokens = [
            {'name': 'PepeBase', 'symbol': 'PEPEB', 'price': 0.00001234, 'liquidity': 150000, 'volume_24h': 85000, 'change_24h': 125.5, 'tx_count': 450, 'pair_url': 'https://dexscreener.com/base/0x123'},
            {'name': 'BaseDoge', 'symbol': 'BDOGE', 'price': 0.0005678, 'liquidity': 89000, 'volume_24h': 45000, 'change_24h': 45.2, 'tx_count': 320, 'pair_url': 'https://dexscreener.com/base/0x456'},
            {'name': 'MoonBase', 'symbol': 'MOON', 'price': 0.001234, 'liquidity': 67000, 'volume_24h': 23000, 'change_24h': -15.8, 'tx_count': 180, 'pair_url': 'https://dexscreener.com/base/0x789'},
            {'name': 'BaseAI', 'symbol': 'BAI', 'price': 0.002345, 'liquidity': 45000, 'volume_24h': 12000, 'change_24h': 78.9, 'tx_count': 95, 'pair_url': 'https://dexscreener.com/base/0xabc'},
        ]
        return demo_tokens
    
    def analyze_reason(self, token: Dict) -> str:
        """分析涨跌原因"""
        reasons = []
        change = token.get('change_24h', 0)
        volume = token.get('volume_24h', 0)
        liquidity = token.get('liquidity', 0)
        tx_count = token.get('tx_count', 0)
        
        # 价格原因
        if change > 100:
            reasons.append("🚀 超级暴涨(100%+)，可能重大利好/上所")
        elif change > 50:
            reasons.append("🌙 暴涨(50%+)，社区FOMO情绪严重")
        elif change > 20:
            reasons.append("📈 大幅上涨(20%+)，买盘强劲")
        elif change > 0:
            reasons.append("💹 稳步上涨，趋势良好")
        elif change > -20:
            reasons.append("📊 正常回调")
        else:
            reasons.append("💥 暴跌(-20%+)，可能rug pull/恐慌抛售")
        
        # 交易量原因
        volume_ratio = volume / liquidity if liquidity > 0 else 0
        if volume_ratio > 2:
            reasons.append(f"🔥 高换手率({volume_ratio:.1f}x)，极度活跃")
        elif volume_ratio > 0.5:
            reasons.append(f"⚡ 交易活跃(换手率{volume_ratio:.1f}x)")
        else:
            reasons.append(f"💤 交易清淡(换手率{volume_ratio:.1f}x)")
        
        # 交易笔数
        if tx_count > 300:
            reasons.append(f"👥 大量散户参与({tx_count}笔)")
        elif tx_count > 100:
            reasons.append(f"👤 社区活跃({tx_count}笔)")
        
        return " | ".join(reasons)
    
    def identify_hotspots(self, tokens: List[Dict]) -> Dict:
        """识别市场热点"""
        if not tokens:
            return {}
        
        hotspots = {
            'market_sentiment': '',
            'top_gainers': [],
            'top_volume': [],
            'hot_narratives': []
        }
        
        # 计算平均涨跌幅
        avg_change = sum(t.get('change_24h', 0) for t in tokens) / len(tokens)
        total_volume = sum(t.get('volume_24h', 0) for t in tokens)
        
        # 市场情绪
        if avg_change > 50:
            hotspots['market_sentiment'] = "🔥🔥🔥 极度狂热 - Base链meme币全面爆发！平均涨幅" + f"{avg_change:.0f}%"
        elif avg_change > 20:
            hotspots['market_sentiment'] = "🔥🔥 非常火热 - Base链meme币整体上涨，平均涨幅" + f"{avg_change:.0f}%"
        elif avg_change > 0:
            hotspots['market_sentiment'] = "🔥 温和上涨 - Base链meme币情绪积极，平均涨幅" + f"{avg_change:.0f}%"
        elif avg_change > -20:
            hotspots['market_sentiment'] = "📊 横盘整理 - Base链meme币情绪中性，平均跌幅" + f"{abs(avg_change):.0f}%"
        else:
            hotspots['market_sentiment'] = "❄️ 整体回调 - Base链meme币冷却，平均跌幅" + f"{abs(avg_change):.0f}%"
        
        # 涨幅榜TOP3
        sorted_by_change = sorted(tokens, key=lambda x: x.get('change_24h', 0), reverse=True)
        hotspots['top_gainers'] = sorted_by_change[:3]
        
        # 交易量榜TOP3
        sorted_by_volume = sorted(tokens, key=lambda x: x.get('volume_24h', 0), reverse=True)
        hotspots['top_volume'] = sorted_by_volume[:3]
        
        # 识别热门叙事
        hot_symbols = [t['symbol'] for t in sorted_by_change[:5]]
        if any('PEPE' in s or 'DOGE' in s for s in hot_symbols):
            hotspots['hot_narratives'].append("🐸 Meme文化币热度高")
        if any('AI' in s or 'GPT' in s for s in hot_symbols):
            hotspots['hot_narratives'].append("🤖 AI概念币受追捧")
        if any(t.get('change_24h', 0) > 100 for t in tokens):
            hotspots['hot_narratives'].append("🚀 多个币暴涨100%+，市场极度FOMO")
        
        return hotspots
    
    def generate_signal(self, token: Dict) -> Optional[Dict]:
        """生成交易信号"""
        score = 0
        reasons = []
        signal_type = "HOLD"
        
        change = token.get('change_24h', 0)
        volume = token.get('volume_24h', 0)
        liquidity = token.get('liquidity', 0)
        
        # 流动性评分
        if liquidity > 100000:
            score += 30
            reasons.append("💰 流动性优秀")
        elif liquidity > 50000:
            score += 20
            reasons.append("💧 流动性良好")
        elif liquidity > 10000:
            score += 10
            reasons.append("⚠️ 流动性一般")
        
        # 交易量评分
        volume_ratio = volume / liquidity if liquidity > 0 else 0
        if volume_ratio > 1:
            score += 25
            reasons.append("🔥 交易极度活跃")
        elif volume_ratio > 0.3:
            score += 15
            reasons.append("⚡ 交易活跃")
        
        # 价格趋势评分
        if 20 < change < 100:
            score += 20
            reasons.append("📈 健康上涨")
        elif change > 100:
            score += 5
            reasons.append("🚀 暴涨(高风险)")
        elif change < -30:
            score -= 20
            reasons.append("📉 大幅回调")
        
        # 信号判定
        if score >= 60:
            signal_type = "🟢 STRONG_BUY"
        elif score >= 40:
            signal_type = "🟡 BUY"
        elif score >= 25:
            signal_type = "🟠 WATCH"
        else:
            signal_type = "⚪ SKIP"
        
        if score >= 40:
            return {
                'symbol': token['symbol'],
                'score': score,
                'signal': signal_type,
                'reasons': reasons,
                'price': token['price'],
                'change': change
            }
        return None
    
    def generate_report(self) -> str:
        """生成完整监控报告"""
        tokens = self.get_base_hot_tokens()
        
        if not tokens:
            return "⚠️ 未能获取数据"
        
        lines = [
            "="*70,
            "🚀 Base链Meme币实时监控报告",
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "="*70,
            ""
        ]
        
        # 热点识别
        hotspots = self.identify_hotspots(tokens)
        lines.extend([
            "🔥 市场热点",
            "-"*70,
            f"{hotspots.get('market_sentiment', '')}",
            ""
        ])
        
        # 涨幅榜
        if hotspots.get('top_gainers'):
            lines.extend([
                "📈 涨幅榜TOP3",
                "-"*70
            ])
            for i, t in enumerate(hotspots['top_gainers'][:3], 1):
                emoji = "🥇" if i==1 else "🥈" if i==2 else "🥉"
                lines.append(f"{emoji} {t['symbol']}: {t['change_24h']:+.2f}% | 💧${t['liquidity']:,.0f} | 📊${t['volume_24h']:,.0f}")
            lines.append("")
        
        # 交易量榜
        if hotspots.get('top_volume'):
            lines.extend([
                "💧 交易量榜TOP3",
                "-"*70
            ])
            for i, t in enumerate(hotspots['top_volume'][:3], 1):
                lines.append(f"{i}. {t['symbol']}: ${t['volume_24h']:,.0f} | {t['change_24h']:+.2f}%")
            lines.append("")
        
        # 热门叙事
        if hotspots.get('hot_narratives'):
            lines.extend([
                "🎯 热门叙事",
                "-"*70
            ])
            for narrative in hotspots['hot_narratives']:
                lines.append(f"  {narrative}")
            lines.append("")
        
        # 详细代币分析
        lines.extend([
            "="*70,
            "📋 详细Meme币分析 (叙事 + 火爆原因)",
            "="*70,
            ""
        ])
        
        for i, token in enumerate(tokens[:5], 1):
            # 标记状态
            status_mark = ""
            if token.get('is_new'):
                status_mark = " 🆕【首次出现】"
            elif token.get('appears_today'):
                status_mark = " 🔁【今日多次】"
            
            lines.extend([
                f"\n{'─'*70}",
                f"#{i} {token['symbol']}{status_mark}",
                f"{'─'*70}",
                f"💰 价格: ${token['price']:.8f} | 24h: {token['change_24h']:+.2f}%",
                f"💧 流动性: ${token['liquidity']:,.0f} | 交易量: ${token['volume_24h']:,.0f}",
                f"🔄 交易笔数: {token.get('tx_count', 0)}",
                ""
            ])
            
            # 合约地址（新合约显示完整地址）
            if token.get('is_new'):
                lines.append(f"📄 合约: {token['address']}")
                lines.append("")
            
            # 原因分析
            reason = self.analyze_reason(token)
            lines.append(f"💡 原因: {reason}")
            
            lines.append(f"\n🔗 DexScreener: {token.get('pair_url', 'N/A')}")
        
        lines.extend([
            "",
            "⚠️ 风险提示: Meme币高风险，以上仅供参考，投资需谨慎",
            "="*70
        ])
        
        return "\n".join(lines)


def main():
    """主函数"""
    monitor = BaseMemeMonitor()
    report = monitor.generate_report()
    print(report)
    
    # 保存报告
    filename = f"/tmp/meme_monitor_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n💾 报告已保存: {filename}")


if __name__ == "__main__":
    main()
