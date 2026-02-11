#!/usr/bin/env python3
"""
Clanker/Bankr Meme币监控系统 v5.0
- 通过Clanker API获取最新代币（100%准确）
- 用DexScreener查价格/交易量
- 标记合约特征（b07结尾等）
- 只监控Clanker/Bankr发的币
"""

import urllib.request
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional

from smart_database import SmartDatabase

class ClankerMonitor:
    """Clanker/Bankr币监控器"""
    
    def __init__(self):
        self.db = SmartDatabase()  # 使用新的SQLite数据库
        self.clanker_api = "https://www.clanker.world/api/tokens"
    
    def get_clanker_tokens(self) -> List[Dict]:
        """从Clanker API获取最新代币"""
        print("🔍 正在获取Clanker/Bankr最新代币...")
        
        try:
            req = urllib.request.Request(
                f"{self.clanker_api}?limit=20",
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                tokens = data.get('data', [])
                
                processed = []
                for token in tokens:
                    contract = token.get('contract_address', '')
                    
                    # 检查是否为新币（使用新的SQLite数据库）
                    is_new = self.db.is_new_token(contract)
                    
                    # 添加到数据库（新的方法）
                    if is_new:
                        narrative = self._extract_narrative(token.get('name', ''), 
                                                            token.get('symbol', ''), 
                                                            token.get('description', ''))
                        self.db.add_token(
                            contract=contract,
                            symbol=token.get('symbol', '???'),
                            name=token.get('name', 'Unknown'),
                            token_type=token.get('type', 'unknown'),
                            is_honeypot=False,  # 稍后检测
                            narrative=narrative
                        )
                    
                    # 检查今天是否已出现过（通过seen_count）
                    seen_today = not is_new  # 如果不是新的，就是今天见过的
                    
                    # 获取DexScreener数据
                    dex_data = self.get_dexscreener_data(contract)
                    
                    processed.append({
                        'symbol': token.get('symbol', '???'),
                        'name': token.get('name', 'Unknown'),
                        'contract': contract,
                        'type': token.get('type', 'unknown'),  # clanker_v4 / bankr
                        'description': token.get('description', ''),
                        'created_at': token.get('created_at', ''),
                        'is_new': is_new,
                        'seen_today': seen_today,
                        'contract_feature': self._analyze_contract(contract),
                        'dex_data': dex_data
                    })
                
                # 按创建时间排序（最新的在前）
                processed.sort(key=lambda x: x['created_at'], reverse=True)
                print(f"✅ 找到 {len(processed)} 个Clanker/Bankr代币")
                return processed[:10]
                
        except Exception as e:
            print(f"❌ 获取Clanker数据失败: {e}")
            return []
    
    def get_dexscreener_data(self, contract: str) -> Dict:
        """从DexScreener获取价格数据"""
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{contract}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                pairs = data.get('pairs', [])
                
                if pairs:
                    pair = pairs[0]  # 取第一个交易对
                    return {
                        'price': float(pair.get('priceUsd', 0) or 0),
                        'liquidity': float(pair.get('liquidity', {}).get('usd', 0) or 0),
                        'volume_24h': float(pair.get('volume', {}).get('h24', 0) or 0),
                        'change_24h': float(pair.get('priceChange', {}).get('h24', 0) or 0),
                        'tx_count': (pair.get('txns', {}).get('h24', {}).get('buys', 0) or 0) + 
                                   (pair.get('txns', {}).get('h24', {}).get('sells', 0) or 0),
                        'pair_url': pair.get('url', '')
                    }
        except Exception as e:
            pass
        
        return {
            'price': 0,
            'liquidity': 0,
            'volume_24h': 0,
            'change_24h': 0,
            'tx_count': 0,
            'pair_url': ''
        }
    
    def _analyze_contract(self, contract: str) -> str:
        """分析合约地址特征"""
        features = []
        
        if contract.lower().endswith('0b07'):
            features.append("🎯 0b07结尾（Clanker典型特征）")
        elif contract.lower().endswith('b07'):
            features.append("🎯 b07结尾（Clanker特征）")
        
        # 检查是否为Bankr
        if 'bankr' in contract.lower():
            features.append("🏦 Bankr相关")
        
        return " | ".join(features) if features else ""
    
    def check_honeypot(self, contract: str) -> Dict:
        """检测是否为貔貅币（Honeypot）"""
        result = {
            'is_honeypot': False,
            'risk_level': 'low',
            'reason': ''
        }
        
        try:
            # 使用Honeypot.is API检测（Base链ID=8453）
            url = f"https://api.honeypot.is/v2/IsHoneypot?address={contract}&chainID=8453"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                
                # 检查是否是貔貅
                if data.get('isHoneypot', False):
                    result['is_honeypot'] = True
                    result['risk_level'] = 'high'
                    result['reason'] = 'API检测为貔貅'
                
                # 检查买入/卖出税是否异常
                buy_tax = data.get('buyTax', 0)
                sell_tax = data.get('sellTax', 0)
                
                if sell_tax > 90:  # 卖出税超过90%，可能是貔貅
                    result['is_honeypot'] = True
                    result['risk_level'] = 'high'
                    result['reason'] = f'卖出税过高: {sell_tax}%'
                elif sell_tax > 50:
                    result['risk_level'] = 'medium'
                    result['reason'] = f'卖出税较高: {sell_tax}%'
                    
        except Exception as e:
            # API失败时返回未知
            result['risk_level'] = 'unknown'
            result['reason'] = '检测失败'
        
        return result
    
    def identify_launcher(self, token: Dict) -> str:
        """识别是哪个平台发的币"""
        token_type = token.get('type', '').lower()
        desc = token.get('description', '').lower()
        
        if 'bankr' in desc or 'bankrbot' in desc:
            return "🏦 Bankr"
        elif 'clanker' in token_type or 'clanker' in desc:
            return "🔧 Clanker"
        else:
            return "🔧 Clanker"
    
    def _extract_narrative(self, name: str, symbol: str, desc: str) -> str:
        """提取叙事关键词"""
        text = (name + " " + symbol + " " + desc).lower()
        
        narratives = []
        if any(k in text for k in ['ai', 'agent', 'bot', 'gpt']):
            narratives.append("AI")
        if any(k in text for k in ['claw', 'molt']):
            narratives.append("Claw生态")
        if any(k in text for k in ['meme', 'pepe', 'doge']):
            narratives.append("Meme")
        if any(k in text for k in ['defi', 'yield', 'staking']):
            narratives.append("DeFi")
            
        return ", ".join(narratives) if narratives else "未分类"

    def analyze_narrative_detailed(self, name: str, symbol: str, desc: str, token_type: str) -> Dict:
        """详细叙事分析"""
        text = (name + " " + symbol + " " + desc + " " + token_type).lower()
        
        analysis = {
            'primary': '',
            'secondary': [],
            'utility': '',
            'community': '',
            'risk_signals': []
        }
        
        # 主要叙事识别
        if any(k in text for k in ['ai agent', 'agent', 'gpt', 'llm', 'autonomous']):
            analysis['primary'] = "🤖 AI Agent - 自主执行任务的AI代理"
            if 'trading' in text or 'trade' in text:
                analysis['utility'] = "💼 实用功能：自动交易/市场分析"
            elif 'social' in text or 'twitter' in text:
                analysis['utility'] = "💬 实用功能：社交媒体管理/内容生成"
            elif 'coding' in text or 'dev' in text:
                analysis['utility'] = "💻 实用功能：编程辅助/代码生成"
            else:
                analysis['utility'] = "🔧 实用功能：通用AI任务执行"
                
        elif any(k in text for k in ['defi', 'yield', 'staking', 'farm']):
            analysis['primary'] = "💰 DeFi协议 - 去中心化金融应用"
            analysis['utility'] = "📈 实用功能：收益耕作/流动性挖矿"
            
        elif any(k in text for k in ['game', 'gaming', 'play', 'nft']):
            analysis['primary'] = "🎮 GameFi - 区块链游戏"
            analysis['utility'] = "🎯 实用功能：游戏内经济/NFT交易"
            
        elif any(k in text for k in ['meme', 'pepe', 'doge', 'culture']):
            analysis['primary'] = "🐸 Meme文化币 - 社区驱动"
            analysis['utility'] = "😂 纯社区/文化价值，无实用功能"
            
        elif any(k in text for k in ['claw', 'molt', 'molty', 'openclaw']):
            analysis['primary'] = "🦞 OpenClaw生态 - Moltbook/Claw相关"
            analysis['utility'] = "🔗 实用功能：AI代理经济系统"
            
        elif any(k in text for k in ['base', 'based']):
            analysis['primary'] = "🏗️ Base生态币 - Base链基础设施"
            analysis['utility'] = "🔧 实用功能：Base链工具/服务"
            
        else:
            analysis['primary'] = "📊 未分类 - 需要进一步观察"
            analysis['utility'] = "❓ 用途待明确"
        
        # 次要叙事
        if 'claw' in text or 'molt' in text:
            analysis['secondary'].append("🦞 OpenClaw生态关联")
        if 'bankr' in text:
            analysis['secondary'].append("🏦 Bankr生态关联")
        if 'clanker' in text:
            analysis['secondary'].append("🔧 Clanker平台发行")
        if 'moon' in text or 'lambo' in text or 'rich' in text:
            analysis['secondary'].append("🚀 暴富叙事")
            analysis['risk_signals'].append("⚠️ 暴富叙事通常是高风险信号")
        if 'community' in text or 'dao' in text:
            analysis['secondary'].append("💪 强调社区驱动")
        
        # 社区活跃度判断（基于描述）
        if any(k in text for k in ['viral', 'trending', 'hype', 'fomo']):
            analysis['community'] = "🔥 极度FOMO，病毒式传播"
        elif any(k in text for k in ['organic', 'growing', 'active']):
            analysis['community'] = "📈 自然增长，社区活跃"
        elif 'quiet' in text or 'stealth' in text:
            analysis['community'] = "🤫  stealth发射，低调积累"
        else:
            analysis['community'] = "👀 新发射，社区状态待观察"
        
        # 额外风险信号
        if 'dev' in text and 'rug' in text:
            analysis['risk_signals'].append("🚨 描述中提到rug风险")
        if 'honeypot' in text:
            analysis['risk_signals'].append("🚨 疑似貔貅盘")
        if text.count('$') > 5:
            analysis['risk_signals'].append("⚠️ 描述中过多金钱符号，营销话术重")
            
        return analysis
    
    def format_narrative_report(self, analysis: Dict) -> str:
        """格式化叙事报告"""
        lines = []
        lines.append(f"📖 叙事: {analysis['primary']}")
        lines.append(f"   {analysis['utility']}")
        
        if analysis['secondary']:
            lines.append(f"   关联: {' | '.join(analysis['secondary'])}")
        
        lines.append(f"   社区: {analysis['community']}")
        
        if analysis['risk_signals']:
            lines.append(f"   {' | '.join(analysis['risk_signals'])}")
            
        return '\n'.join(lines)
    
    def generate_report(self) -> str:
        """生成监控报告"""
        tokens = self.get_clanker_tokens()
        
        # 过滤掉交易量为0的币
        tokens = [t for t in tokens if t.get('dex_data', {}).get('volume_24h', 0) > 0]
        
        # 检测并过滤貔貅币
        filtered_tokens = []
        honeypot_count = 0
        for t in tokens:
            contract = t.get('contract', '')
            honeypot_check = self.check_honeypot(contract)
            if honeypot_check.get('is_honeypot', False):
                honeypot_count += 1
                print(f"🚫 过滤貔貅币: {t.get('symbol')} - {honeypot_check.get('reason', '')}")
                continue
            t['honeypot_check'] = honeypot_check
            filtered_tokens.append(t)
        
        tokens = filtered_tokens
        
        # 按交易量排序，取最热的5个
        tokens.sort(key=lambda x: x.get('dex_data', {}).get('volume_24h', 0), reverse=True)
        tokens = tokens[:5]
        
        if not tokens:
            msg = "📭 当前无活跃交易的Clanker/Bankr代币（交易量>0）"
            if honeypot_count > 0:
                msg += f"\n   (已过滤 {honeypot_count} 个貔貅币)"
            return msg
        
        lines = [
            "="*70,
            "🦞 Clanker/Bankr 热门币TOP5",
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "="*70,
            ""
        ]
        
        if honeypot_count > 0:
            lines.append(f"🚫 已过滤 {honeypot_count} 个貔貅币")
            lines.append("")
        
        # 新币预警 - 更醒目，去掉合约地址
        new_tokens = [t for t in tokens if t.get('is_new')]
        if new_tokens:
            lines.extend([
                "🚨🚨🚨 新币预警（首次出现）🚨🚨🚨",
                "-"*70,
            ])
            for t in new_tokens[:3]:
                dex = t.get('dex_data', {})
                lines.append(f"⚠️ {t['symbol']} 新发")
                # 显示价格和交易量
                lines.append(f"   💰 ${dex.get('price', 0):.8f} | 📊 ${dex.get('volume_24h', 0):,.0f}")
            lines.append("")
        
        # 详细分析 - 只显示最热的5个
        lines.extend([
            "="*70,
            "📋 热门币详细分析 (TOP5)",
            "="*70,
            ""
        ])
        
        for i, token in enumerate(tokens, 1):
            # 标记状态 - 首次出现更醒目
            status_mark = ""
            if token.get('is_new'):
                status_mark = " 🚨🆕【首次出现】🚨"  # 更醒目的标记
            elif token.get('seen_today'):
                status_mark = " 🔁【今日多次】"
            
            launcher = self.identify_launcher(token)
            dex = token.get('dex_data', {})
            
            lines.extend([
                f"\n{'─'*70}",
                f"#{i} {token['symbol']}{status_mark}",
                f"{'─'*70}",
                f"💰 价格: ${dex.get('price', 0):.8f} | 24h: {dex.get('change_24h', 0):+.2f}%",
                f"💎 市值: ${dex.get('market_cap', dex.get('fdv', 0)):,.0f} | 📊 交易量: ${dex.get('volume_24h', 0):,.0f}",
                f"💧 流动性: ${dex.get('liquidity', 0):,.0f} | 🔄 交易笔数: {dex.get('tx_count', 0)}",
                ""
            ])
            
            # 只显示特征，不显示合约地址
            lines.append("")
            
            # 详细叙事分析
            narrative = self.analyze_narrative_detailed(token['name'], token['symbol'], token.get('description', ''), token.get('type', ''))
            lines.append(self.format_narrative_report(narrative))
            
            # 创建时间
            created = token.get('created_at', '')
            if created:
                try:
                    created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    minutes_ago = int((datetime.now(created_dt.tzinfo) - created_dt).total_seconds() / 60)
                    lines.append(f"⏰ 创建时间: {minutes_ago}分钟前")
                except:
                    pass
            
            if dex.get('pair_url'):
                lines.append(f"\n🔗 DexScreener: {dex['pair_url']}")
        
        lines.extend([
            "",
            "="*70,
            "⚠️ 风险提示: Clanker/Bankr新币风险极高，以上数据仅供参考，DYOR",
            "="*70
        ])
        
        return "\n".join(lines)


def main():
    """主函数 - 带智能推送调节"""
    from smart_scheduler import SmartScheduler
    
    monitor = ClankerMonitor()
    scheduler = SmartScheduler()
    
    # 获取代币数据
    tokens = monitor.get_clanker_tokens()
    
    # 过滤貔貅币
    filtered_tokens = []
    honeypot_count = 0
    for t in tokens:
        contract = t.get('contract', '')
        honeypot_check = monitor.check_honeypot(contract)
        if honeypot_check.get('is_honeypot', False):
            honeypot_count += 1
            print(f"🚫 过滤貔貅币: {t.get('symbol')} - {honeypot_check.get('reason', '')}")
            continue
        t['honeypot_check'] = honeypot_check
        filtered_tokens.append(t)
    
    # 过滤无交易量
    active_tokens = [t for t in filtered_tokens if t.get('dex_data', {}).get('volume_24h', 0) > 0]
    
    # 智能决策
    should_push = scheduler.should_push(len(active_tokens))
    status = scheduler.get_status()
    
    print(f"\n📊 市场状态: {status}")
    print(f"活跃代币: {len(active_tokens)} | 貔貅过滤: {honeypot_count}")
    print(f"是否推送: {'✅ 是' if should_push else '❌ 否'}")
    
    if not should_push:
        print(f"\n💤 静默中... 下次检查再决定")
        return
    
    # 生成并发送报告
    report = monitor.generate_report()
    print(report)
    
    # 标记已推送
    scheduler.mark_pushed()
    
    # 保存报告
    filename = f"/tmp/clanker_monitor_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n💾 报告已保存: {filename}")


if __name__ == "__main__":
    main()
