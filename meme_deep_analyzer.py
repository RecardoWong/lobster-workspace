#!/usr/bin/env python3
"""
Meme币深度分析系统 v4.0
功能：
1. 识别新出现的合约（首次出现）
2. 分析土狗叙事（故事/概念）
3. 分析火的原因（交易量/价格/社媒）
"""

import urllib.request
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Set

class ContractDatabase:
    """合约数据库 - 记录历史合约"""
    
    def __init__(self, db_file: str = "/tmp/meme_contracts_db.json"):
        self.db_file = db_file
        self.known_contracts: Set[str] = set()
        self.contract_history: Dict = {}
        self.load()
    
    def load(self):
        """加载历史数据"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
                    self.known_contracts = set(data.get('contracts', []))
                    self.contract_history = data.get('history', {})
            except:
                pass
    
    def save(self):
        """保存数据"""
        data = {
            'contracts': list(self.known_contracts),
            'history': self.contract_history,
            'last_update': datetime.now().isoformat()
        }
        with open(self.db_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def is_new(self, address: str) -> bool:
        """检查是否为新合约"""
        return address.lower() not in self.known_contracts
    
    def add(self, address: str, info: Dict):
        """添加合约"""
        self.known_contracts.add(address.lower())
        self.contract_history[address.lower()] = {
            'first_seen': datetime.now().isoformat(),
            'info': info
        }
        self.save()


class NarrativeAnalyzer:
    """叙事分析器 - 分析土狗的故事和概念"""
    
    # 叙事模式库
    NARRATIVES = {
        'meme_culture': {
            'keywords': ['pepe', 'doge', 'shib', 'wojak', 'chad', 'based'],
            'description': '🐸 Meme文化币 - 依靠社区传播和表情包驱动'
        },
        'ai_concept': {
            'keywords': ['ai', 'gpt', 'bot', 'neural', 'intelligence', 'robot'],
            'description': '🤖 AI概念币 - 蹭AI热度，声称有技术或应用场景'
        },
        'celebrity': {
            'keywords': ['elon', 'musk', 'trump', 'elmo', 'donald', 'musk'],
            'description': '🚀 名人概念币 - 蹭名人/政客热度'
        },
        'animal': {
            'keywords': ['cat', 'dog', 'frog', 'bird', 'wolf', 'bear', 'bull'],
            'description': '🐕 动物币 - 可爱动物形象，容易传播'
        },
        'moon_money': {
            'keywords': ['moon', 'mars', 'rocket', 'lambo', 'rich', 'money', 'wealth'],
            'description': '🌙 暴富概念币 - 强调暴富、上月球等财富自由叙事'
        },
        'community': {
            'keywords': ['community', 'dao', 'together', 'united', 'hold', 'army'],
            'description': '💪 社区驱动币 - 强调社区力量、团结持币'
        },
        'base_ecosystem': {
            'keywords': ['base', 'build', 'onbase', 'basechain'],
            'description': '🏗️ Base生态币 - 强调在Base链上构建生态'
        },
        'gaming': {
            'keywords': ['game', 'gaming', 'play', 'nft', 'metaverse', 'pvp'],
            'description': '🎮 游戏概念币 - GameFi或元宇宙相关'
        }
    }
    
    def analyze(self, name: str, symbol: str) -> List[Dict]:
        """分析代币叙事"""
        text = (name + " " + symbol).lower()
        narratives = []
        
        for key, data in self.NARRATIVES.items():
            match_score = sum(1 for keyword in data['keywords'] if keyword in text)
            if match_score > 0:
                narratives.append({
                    'type': key,
                    'description': data['description'],
                    'match_score': match_score,
                    'matched_keywords': [k for k in data['keywords'] if k in text]
                })
        
        # 按匹配度排序
        narratives.sort(key=lambda x: x['match_score'], reverse=True)
        return narratives
    
    def generate_story(self, name: str, symbol: str, narratives: List[Dict]) -> str:
        """生成代币故事"""
        if not narratives:
            return f"📖 {symbol} - 暂无明确叙事，可能是实验性项目或等待社区发现价值"
        
        top_narrative = narratives[0]
        story = f"📖 {symbol} ({name})\n"
        story += f"   核心叙事: {top_narrative['description']}\n"
        
        if len(narratives) > 1:
            story += f"   次要叙事: {narratives[1]['description']}\n"
        
        # 根据叙事生成预期
        if top_narrative['type'] == 'meme_culture':
            story += "   📈 爆发潜力: 依赖KOL喊单和社区传播，可能快速暴涨但持续性差"
        elif top_narrative['type'] == 'ai_concept':
            story += "   📈 爆发潜力: AI热度持续，如有实际应用场景可能长期上涨"
        elif top_narrative['type'] == 'celebrity':
            story += "   ⚠️ 风险提示: 名人概念币容易因名人一句话暴涨暴跌"
        elif top_narrative['type'] == 'moon_money':
            story += "   ⚠️ 风险提示: 暴富叙事通常是割韭菜信号，需警惕"
        
        return story


class HypeAnalyzer:
    """火爆原因分析器"""
    
    def analyze(self, token: Dict) -> Dict:
        """分析为什么火"""
        reasons = []
        indicators = {
            'volume_explosion': False,
            'price_pump': False,
            'new_listing': False,
            'whale_activity': False,
            'social_hype': False
        }
        
        change = token.get('change_24h', 0)
        volume = token.get('volume_24h', 0)
        liquidity = token.get('liquidity', 0)
        tx_count = token.get('tx_count', 0)
        
        # 1. 交易量爆发
        volume_ratio = volume / liquidity if liquidity > 0 else 0
        if volume_ratio > 5:
            reasons.append("🔥🔥🔥 交易量极度爆发 - 资金疯狂涌入，可能重大利好")
            indicators['volume_explosion'] = True
        elif volume_ratio > 2:
            reasons.append("🔥🔥 交易量激增 - 关注度快速提升")
            indicators['volume_explosion'] = True
        elif volume_ratio > 1:
            reasons.append("🔥 交易活跃 - 正常热度")
        
        # 2. 价格暴涨
        if change > 500:
            reasons.append("🚀🚀🚀 超级暴涨(500%+) - 可能是上所/重大合作/病毒式传播")
            indicators['price_pump'] = True
        elif change > 200:
            reasons.append("🚀🚀 暴涨(200%+) - KOL喊单或社区FOMO")
            indicators['price_pump'] = True
        elif change > 100:
            reasons.append("🚀 大幅上涨(100%+) - 买盘强劲")
            indicators['price_pump'] = True
        
        # 3. 新币上线特征
        if liquidity < 50000 and volume > liquidity * 3:
            reasons.append("🆕 疑似新币上线 - 刚发射就被大量买入，早期机会但风险极高")
            indicators['new_listing'] = True
        
        # 4. 鲸鱼活动特征
        if tx_count < 50 and volume > 100000:
            reasons.append("🐋 鲸鱼控盘迹象 - 交易笔数少但金额大，大户在操盘")
            indicators['whale_activity'] = True
        
        # 5. 散户FOMO
        if tx_count > 500 and change > 50:
            reasons.append("👥 散户FOMO严重 - 大量小单买入，社区情绪狂热")
            indicators['social_hype'] = True
        
        # 综合判断
        if not reasons:
            if change > 0:
                reasons.append("📊 温和上涨 - 正常市场波动")
            else:
                reasons.append("📉 回调中 - 获利盘出货或市场情绪转冷")
        
        return {
            'reasons': reasons,
            'indicators': indicators,
            'hype_score': self._calculate_hype_score(indicators, change, volume_ratio)
        }
    
    def _calculate_hype_score(self, indicators: Dict, change: float, volume_ratio: float) -> int:
        """计算热度分数"""
        score = 0
        if indicators['volume_explosion']: score += 30
        if indicators['price_pump']: score += 30
        if indicators['new_listing']: score += 20
        if indicators['whale_activity']: score += 10
        if indicators['social_hype']: score += 10
        
        # 价格加成
        if change > 200: score += 20
        elif change > 100: score += 15
        elif change > 50: score += 10
        
        # 交易量加成
        if volume_ratio > 5: score += 10
        elif volume_ratio > 2: score += 5
        
        return min(100, score)


class MemeCoinDeepAnalyzer:
    """Meme币深度分析器"""
    
    def __init__(self):
        self.db = ContractDatabase()
        self.narrative = NarrativeAnalyzer()
        self.hype = HypeAnalyzer()
    
    def get_base_tokens(self) -> List[Dict]:
        """获取Base链代币"""
        try:
            url = "https://api.dexscreener.com/latest/dex/search?q=base%20chain"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                pairs = data.get('pairs', [])
                
                tokens = []
                seen = set()
                
                for pair in pairs:
                    if pair.get('chainId', '').lower() != 'base':
                        continue
                    
                    symbol = pair.get('baseToken', {}).get('symbol', '???')
                    address = pair.get('baseToken', {}).get('address', '')
                    
                    if symbol in seen or symbol == '???':
                        continue
                    seen.add(symbol)
                    
                    liquidity = float(pair.get('liquidity', {}).get('usd', 0) or 0)
                    if liquidity > 5000:  # 至少$5K流动性
                        tokens.append({
                            'name': pair.get('baseToken', {}).get('name', 'Unknown'),
                            'symbol': symbol,
                            'address': address,
                            'price': float(pair.get('priceUsd', 0) or 0),
                            'liquidity': liquidity,
                            'volume_24h': float(pair.get('volume', {}).get('h24', 0) or 0),
                            'change_24h': float(pair.get('priceChange', {}).get('h24', 0) or 0),
                            'tx_count': (pair.get('txns', {}).get('h24', {}).get('buys', 0) or 0) + 
                                       (pair.get('txns', {}).get('h24', {}).get('sells', 0) or 0),
                            'pair_url': pair.get('url', ''),
                            'is_new': self.db.is_new(address)
                        })
                
                # 按交易量排序
                tokens.sort(key=lambda x: x['volume_24h'], reverse=True)
                
                # 新合约添加到数据库
                for t in tokens:
                    if t['is_new']:
                        self.db.add(t['address'], {
                            'name': t['name'],
                            'symbol': t['symbol'],
                            'first_seen_price': t['price']
                        })
                
                return tokens[:10]
                
        except Exception as e:
            print(f"❌ 获取数据失败: {e}")
            return []
    
    def generate_report(self) -> str:
        """生成深度分析报告"""
        print("🔍 正在深度分析Base链Meme币...")
        tokens = self.get_base_tokens()
        
        if not tokens:
            return "⚠️ 未能获取数据"
        
        lines = [
            "="*70,
            "🚀 Base链Meme币深度分析报告",
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "="*70,
            ""
        ]
        
        # 新合约预警
        new_tokens = [t for t in tokens if t['is_new']]
        if new_tokens:
            lines.extend([
                "🆕 新合约预警（首次出现）",
                "-"*70,
            ])
            for t in new_tokens[:3]:
                lines.append(f"⚠️ {t['symbol']} - 今日首次出现！")
                lines.append(f"   合约: {t['address'][:20]}...")
                lines.append(f"   价格: ${t['price']:.8f} | 流动性: ${t['liquidity']:,.0f}")
            lines.append("")
        
        # 详细分析每只币
        lines.extend([
            "="*70,
            "📋 深度分析：叙事 + 火爆原因",
            "="*70,
            ""
        ])
        
        for i, token in enumerate(tokens[:5], 1):
            # 基本信息
            new_flag = " 🆕新" if token['is_new'] else ""
            lines.extend([
                f"\n{'─'*70}",
                f"#{i} {token['symbol']}{new_flag} ({token['name']})",
                f"{'─'*70}",
                f"💰 价格: ${token['price']:.8f} | 24h: {token['change_24h']:+.2f}%",
                f"💧 流动性: ${token['liquidity']:,.0f} | 交易量: ${token['volume_24h']:,.0f}",
                ""
            ])
            
            # 叙事分析
            narratives = self.narrative.analyze(token['name'], token['symbol'])
            story = self.narrative.generate_story(token['name'], token['symbol'], narratives)
            lines.append(story)
            lines.append("")
            
            # 火爆原因分析
            hype = self.hype.analyze(token)
            lines.append("🔥 火爆原因分析:")
            for reason in hype['reasons']:
                lines.append(f"   {reason}")
            lines.append(f"\n   📊 热度评分: {hype['hype_score']}/100")
            
            # 交易建议
            if hype['hype_score'] >= 80:
                lines.append("\n   🎯 建议: 极度火爆，可小仓位参与但设好止损")
            elif hype['hype_score'] >= 60:
                lines.append("\n   🎯 建议: 热度较高，可观察等待回调")
            elif hype['hype_score'] >= 40:
                lines.append("\n   🎯 建议: 温和热度，适合埋伏")
            else:
                lines.append("\n   🎯 建议: 热度较低，观望为主")
            
            lines.append(f"\n🔗 {token['pair_url']}")
        
        lines.extend([
            "",
            "="*70,
            "⚠️ 风险提示: Meme币高风险，以上分析仅供参考",
            "="*70
        ])
        
        return "\n".join(lines)


def main():
    """主函数"""
    analyzer = MemeCoinDeepAnalyzer()
    report = analyzer.generate_report()
    print(report)
    
    # 保存报告
    filename = f"/tmp/meme_deep_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n💾 报告已保存: {filename}")


if __name__ == "__main__":
    main()
