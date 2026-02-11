#!/usr/bin/env python3
"""
🦞 龙虾Agent自主创造的实用工具箱
不需要等别人给，自己造！
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

class LobsterToolkit:
    """龙虾工具箱 - 自主创造"""
    
    def __init__(self):
        self.created_at = datetime.now().isoformat()
        self.version = "1.0.0"
    
    # ========== 工具1: 快速价格查询 ==========
    def get_token_price(self, chain: str, address: str) -> Dict:
        """自主创造：快速查币价"""
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            if data.get('pairs'):
                pair = data['pairs'][0]
                return {
                    'symbol': pair['baseToken']['symbol'],
                    'price': pair['priceUsd'],
                    'change_24h': pair.get('priceChange', {}).get('h24', 0),
                    'volume_24h': pair.get('volume', {}).get('h24', 0),
                    'liquidity': pair.get('liquidity', {}).get('usd', 0),
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
            return {'error': 'No pairs found'}
        except Exception as e:
            return {'error': str(e)}
    
    # ========== 工具2: 貔貅检测 ==========
    def check_honeypot(self, chain_id: str, address: str) -> Dict:
        """自主创造：快速貔貅检测"""
        try:
            url = f"https://api.honeypot.is/v2/IsHoneypot?address={address}&chainID={chain_id}"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            flags = data.get('flags', [])
            summary = data.get('summary', {})
            
            return {
                'is_safe': len(flags) == 0,
                'risk_level': summary.get('risk', 'unknown'),
                'flags': flags,
                'holder_analysis': data.get('holderAnalysis', {}),
                'verified': data.get('contractCode', {}).get('openSource', False)
            }
        except Exception as e:
            return {'error': str(e)}
    
    # ========== 工具3: 市场情绪快照 ==========
    def market_sentiment_snapshot(self) -> Dict:
        """自主创造：市场情绪快照"""
        try:
            # 获取BTC和ETH数据作为市场情绪指标
            btc = self.get_token_price('ethereum', '0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c')  # BTCB
            eth = self.get_token_price('ethereum', '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')  # WETH
            
            return {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'btc_change': btc.get('change_24h', 0),
                'eth_change': eth.get('change_24h', 0),
                'sentiment': 'bullish' if btc.get('change_24h', 0) > 5 else 'bearish' if btc.get('change_24h', 0) < -5 else 'neutral'
            }
        except:
            return {'sentiment': 'unknown'}
    
    # ========== 工具4: 智能推送格式化 ==========
    def format_alert(self, title: str, data: Dict, level: str = 'info') -> str:
        """自主创造：美观的推送格式化"""
        emoji_map = {
            'high': '🚨', 'medium': '⚠️', 'low': 'ℹ️', 'info': 'ℹ️',
            'success': '✅', 'error': '❌', 'warning': '⚡'
        }
        
        emoji = emoji_map.get(level, 'ℹ️')
        lines = [
            f"{emoji} {title}",
            f"⏰ {datetime.now().strftime('%H:%M:%S')}",
            "=" * 50
        ]
        
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"\n📊 {key}:")
                for k, v in value.items():
                    lines.append(f"  • {k}: {v}")
            else:
                lines.append(f"  {key}: {value}")
        
        return "\n".join(lines)
    
    # ========== 工具5: 快速笔记 ==========
    def quick_note(self, category: str, content: str, tags: List[str] = None) -> str:
        """自主创造：快速记录笔记"""
        note = {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'content': content,
            'tags': tags or []
        }
        
        # 保存到文件
        import os
        note_file = f"/tmp/lobster_notes_{datetime.now().strftime('%Y%m%d')}.json"
        
        notes = []
        if os.path.exists(note_file):
            try:
                with open(note_file, 'r') as f:
                    notes = json.load(f)
            except:
                pass
        
        notes.append(note)
        
        with open(note_file, 'w') as f:
            json.dump(notes[-100:], f, indent=2)  # 保留最近100条
        
        return f"✅ 笔记已保存 ({len(notes)}条)"
    
    # ========== 工具6: 系统健康检查 ==========
    def system_health(self) -> Dict:
        """自主创造：系统健康检查"""
        import os
        import subprocess
        
        health = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'disk_usage': 'unknown',
            'memory': 'unknown',
            'scripts_count': 0,
            'status': 'healthy'
        }
        
        try:
            # 磁盘
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            health['disk_usage'] = result.stdout.split('\n')[1].split()[4]
            
            # 内存
            result = subprocess.run(['free', '-h'], capture_output=True, text=True)
            mem_line = result.stdout.split('\n')[1]
            health['memory'] = mem_line.split()[1]
            
            # 脚本数量
            scripts = [f for f in os.listdir('/root/.openclaw/workspace') if f.endswith('.py')]
            health['scripts_count'] = len(scripts)
            
        except Exception as e:
            health['status'] = f'check_error: {str(e)[:30]}'
        
        return health


# ========== 立即测试自主创造的工具 ==========
if __name__ == "__main__":
    toolkit = LobsterToolkit()
    
    print("🦞 龙虾工具箱测试")
    print("=" * 50)
    
    # 测试1: 系统健康
    print("\n1️⃣ 系统健康检查:")
    health = toolkit.system_health()
    print(f"   磁盘使用: {health['disk_usage']}")
    print(f"   内存: {health['memory']}")
    print(f"   脚本数: {health['scripts_count']}")
    
    # 测试2: 市场情绪
    print("\n2️⃣ 市场情绪快照:")
    sentiment = toolkit.market_sentiment_snapshot()
    print(f"   情绪: {sentiment.get('sentiment')}")
    
    # 测试3: 快速笔记
    print("\n3️⃣ 快速笔记:")
    result = toolkit.quick_note('test', '龙虾工具箱测试成功', ['test', 'autonomy'])
    print(f"   {result}")
    
    # 测试4: 格式化推送
    print("\n4️⃣ 推送格式化:")
    alert = toolkit.format_alert('测试警报', {'测试项': '成功', '数值': 100}, 'success')
    print(alert)
    
    print("\n" + "=" * 50)
    print("✅ 所有工具创造完成！ lobster-toolkit v1.0 就绪！")
