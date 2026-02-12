#!/usr/bin/env python3
"""
🕷️ XXYY.io Meme币扫描 + DexScreener MC查询
第一步：从xxyy.io获取代币列表
第二步：用DexScreener API查MC、交易量、流动性
第三步：只推送MC>$35K的币
"""

import subprocess
import re
import requests
import json
from datetime import datetime
from typing import List, Dict, Tuple
import time

class XXYYScannerWithMC:
    """XXYY.io + DexScreener MC查询"""
    
    def __init__(self):
        self.url = "https://www.xxyy.io/meme?chainId=sol"
        self.timeout = 30
        self.mc_threshold = 35000  # $35K
        
        self.narratives = {
            'ai': {'keywords': ['ai', 'xai', 'grok', 'gpt', 'tech'], 'emoji': '🤖', 'name': 'AI科技'},
            'celebrity': {'keywords': ['speed', 'elon', 'musk', 'trump', 'star'], 'emoji': '⭐', 'name': '名人/网红'},
            'animal': {'keywords': ['cat', 'dog', 'duck', 'bunny', 'frog'], 'emoji': '🐱', 'name': '动物币'},
            'food': {'keywords': ['hotdog', 'pizza', 'burger', 'food'], 'emoji': '🌭', 'name': '食物'},
            'gamble': {'keywords': ['casino', 'bet', 'gamble', 'lottery'], 'emoji': '🎰', 'name': '赌博/博彩'},
            'meme': {'keywords': ['meme', 'pepe', 'wojak', 'chad'], 'emoji': '🐸', 'name': '经典Meme'},
            'money': {'keywords': ['money', 'cash', 'rich', 'wealth'], 'emoji': '💰', 'name': '金钱/财富'},
            'controversial': {'keywords': ['sex', 'porn', 'hitler'], 'emoji': '⚠️', 'name': '敏感/争议'},
        }
    
    def analyze_narrative(self, symbol: str, name: str) -> Tuple[str, str, int]:
        text = f"{symbol} {name}".lower()
        scores = {}
        for nar_id, nar_info in self.narratives.items():
            score = sum(2 if keyword in symbol.lower() else 1 
                       for keyword in nar_info['keywords'] if keyword in text)
            if score > 0:
                scores[nar_id] = score
        
        if scores:
            best = max(scores, key=scores.get)
            return self.narratives[best]['emoji'], self.narratives[best]['name'], scores[best]
        return '❓', '其他', 0
    
    def scan_xxyy(self) -> List[Dict]:
        """扫描xxyy.io获取代币列表"""
        print("🕷️ 扫描 xyy.io/meme...")
        
        tokens = []
        try:
            cmd = f"agent-browser snapshot '{self.url}' --timeout {self.timeout}000"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            content = result.stdout
            lines = content.split('\n')
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                if 'text:' in line and 'pump' in line and '...' in line:
                    text_content = line.replace('- text:', '').strip()
                    match = re.search(r'([A-Za-z0-9]+)\s+([^]+)\s*(\d+)([smhd])\s+([A-Za-z0-9]+\.\.\.pump)', text_content)
                    
                    if match:
                        symbol = match.group(1).strip()
                        name = match.group(2).strip()
                        time_val = match.group(3)
                        time_unit = match.group(4)
                        address_short = match.group(5)
                        
                        time_seconds = int(time_val)
                        if time_unit == 'm': time_seconds *= 60
                        elif time_unit == 'h': time_seconds *= 3600
                        elif time_unit == 'd': time_seconds *= 86400
                        
                        emoji, narrative, strength = self.analyze_narrative(symbol, name)
                        
                        token = {
                            'symbol': symbol,
                            'name': name,
                            'time_ago': f"{time_val}{time_unit}",
                            'time_seconds': time_seconds,
                            'address_short': address_short,
                            'emoji': emoji,
                            'narrative': narrative,
                            'strength': strength,
                            'address_full': None,
                            'chain': 'sol'
                        }
                        
                        # 查找Pump链接获取完整地址
                        j = i + 1
                        while j < len(lines) and j < i + 15:
                            next_line = lines[j].strip()
                            if 'text:' in next_line and 'pump' in next_line and '...' in next_line:
                                break
                            
                            if '/url:' in next_line and 'pump.fun' in next_line:
                                url_match = re.search(r'/url:\s*(https://[^\s]+)', next_line)
                                if url_match:
                                    url = url_match.group(1)
                                    addr_match = re.search(r'/coin/([A-Za-z0-9]+)', url)
                                    if addr_match:
                                        token['address_full'] = addr_match.group(1)
                                        token['pump_url'] = url
                            
                            j += 1
                        
                        # 只保留发射>60秒且有完整地址的
                        if time_seconds > 60 and token.get('address_full'):
                            tokens.append(token)
                
                i += 1
            
            # 去重
            seen = set()
            unique = []
            for t in tokens:
                key = t['address_full']
                if key and key not in seen:
                    seen.add(key)
                    unique.append(t)
            
            return unique
            
        except Exception as e:
            print(f"❌ xxyy扫描失败: {e}")
            return []
    
    def query_dexscreener(self, address: str) -> Dict:
        """查询DexScreener获取MC数据"""
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            data = r.json()
            
            pairs = data.get('pairs', [])
            if not pairs:
                return {'mc': 0, 'volume': 0, 'liquidity': 0, 'price': 0}
            
            # 取第一个交易对的数据
            pair = pairs[0]
            
            # 计算MC
            price = float(pair.get('priceUsd') or 0)
            # 尝试获取总供应量计算MC
            mc = float(pair.get('marketCap') or 0)
            if not mc:
                # 如果没有marketCap，用liquidity估算
                liquidity = float(pair.get('liquidity', {}).get('usd') or 0)
                mc = liquidity * 2  # 粗略估算
            
            return {
                'mc': mc,
                'volume_24h': float(pair.get('volume', {}).get('h24') or 0),
                'liquidity': float(pair.get('liquidity', {}).get('usd') or 0),
                'price': price,
                'dex': pair.get('dexId', 'Unknown'),
                'pair_url': pair.get('url', '')
            }
            
        except Exception as e:
            print(f"  ⚠️ DexScreener查询失败: {e}")
            return {'mc': 0, 'volume': 0, 'liquidity': 0, 'price': 0}
    
    def filter_by_mc(self, tokens: List[Dict]) -> List[Dict]:
        """过滤MC>$35K的币"""
        print(f"\n🔍 查询DexScreener获取MC数据 (阈值: ${self.mc_threshold/1000:.0f}K)...\n")
        
        qualified = []
        
        for i, token in enumerate(tokens[:20], 1):  # 只查前20个避免超时
            print(f"{i}/{min(20, len(tokens))} 查询 {token['symbol']}...", end=' ')
            
            dex_data = self.query_dexscreener(token['address_full'])
            time.sleep(0.5)  # 避免请求过快
            
            token['mc'] = dex_data['mc']
            token['volume_24h'] = dex_data['volume_24h']
            token['liquidity'] = dex_data['liquidity']
            token['price'] = dex_data['price']
            token['dex'] = dex_data['dex']
            token['pair_url'] = dex_data['pair_url']
            
            if dex_data['mc'] >= self.mc_threshold:
                print(f"✅ MC: ${dex_data['mc']/1000:.1f}K (合格)")
                qualified.append(token)
            else:
                print(f"❌ MC: ${dex_data['mc']/1000:.1f}K (低于阈值)")
        
        return qualified
    
    def generate_report(self, tokens: List[Dict]) -> str:
        """生成报告"""
        now = datetime.now()
        
        lines = [
            "🕷️ XXYY.io + DexScreener MC筛选报告",
            f"⏰ {now.strftime('%Y-%m-%d %H:%M')}",
            f"🎯 筛选条件: MC > ${self.mc_threshold/1000:.0f}K",
            "=" * 75,
            ""
        ]
        
        if not tokens:
            lines.append("📭 暂无MC>$35K的合格代币")
            lines.append("\n💡 提示: 市场较冷，或新币尚未积累足够流动性")
            return "\n".join(lines)
        
        lines.append(f"📊 发现 {len(tokens)} 个MC>${self.mc_threshold/1000:.0f}K的代币\n")
        
        # 按MC排序
        sorted_tokens = sorted(tokens, key=lambda x: x.get('mc', 0), reverse=True)
        
        for i, t in enumerate(sorted_tokens[:10], 1):
            lines.append(f"{i}. {t['emoji']} **{t['symbol']}** - {t['name']}")
            lines.append(f"   💰 MC: ${t['mc']/1000:.1f}K | 💧 流动性: ${t['liquidity']/1000:.1f}K")
            lines.append(f"   📈 24h交易量: ${t['volume_24h']/1000:.1f}K | 价格: ${t['price']:.10f}")
            lines.append(f"   ⏱️ 发射: {t['time_ago']} | 叙事: {t['narrative']} (强度{t['strength']}/10)")
            lines.append(f"   🔗 {t['pair_url']}")
            lines.append(f"   📍 合约: {t['address_full'][:20]}...")
            lines.append("")
        
        # 叙事统计
        narrative_counts = {}
        for t in tokens:
            nar = t.get('narrative', '其他')
            narrative_counts[nar] = narrative_counts.get(nar, 0) + 1
        
        lines.append("=" * 75)
        lines.append("📈 **叙事分布：**")
        for nar, count in sorted(narrative_counts.items(), key=lambda x: x[1], reverse=True):
            emoji = next((t['emoji'] for t in tokens if t['narrative'] == nar), '•')
            lines.append(f"  {emoji} {nar}: {count}个")
        
        lines.append("\n⚠️ **风险提示：**")
        lines.append("  • 即使MC>$35K，新币仍可能快速归零")
        lines.append("  • 建议进一步检查: 合约安全/团队背景/社区活跃度")
        
        return "\n".join(lines)
    
    def run(self):
        """运行完整流程"""
        print("🚀 启动 XXYY.io + DexScreener MC筛选\n")
        
        # 第一步：扫描xxyy.io
        tokens = self.scan_xxyy()
        print(f"\n✅ 从xxyy.io获取 {len(tokens)} 个已发射代币\n")
        
        if not tokens:
            print("❌ 无代币数据")
            return []
        
        # 第二步：查询DexScreener，过滤MC>$35K
        qualified = self.filter_by_mc(tokens)
        
        # 第三步：生成报告
        report = self.generate_report(qualified)
        print("\n" + report)
        
        # 保存
        report_file = f"/tmp/xxyy_mc_filtered_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n💾 报告已保存: {report_file}")
        
        return qualified


def main():
    scanner = XXYYScannerWithMC()
    scanner.run()


if __name__ == "__main__":
    main()
