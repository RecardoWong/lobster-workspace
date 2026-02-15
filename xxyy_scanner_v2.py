#!/usr/bin/env python3
"""
🪙 XXYY.io Meme币扫描 - 简化版
只推holder≥100的币
"""

import subprocess
import re
import requests
import json
from datetime import datetime
from typing import List, Dict, Tuple

class XXYYScanner:
    def __init__(self):
        self.url = "https://www.xxyy.io/meme?chainId=sol"
        self.timeout = 30
        self.min_holders = 100  # holder阈值
        
        self.narratives = {
            'ai': {'keywords': ['ai', 'grok', 'gpt', 'tech'], 'emoji': '🤖', 'name': 'AI科技'},
            'celebrity': {'keywords': ['elon', 'musk', 'trump'], 'emoji': '⭐', 'name': '名人'},
            'animal': {'keywords': ['cat', 'dog', 'frog', 'bear'], 'emoji': '🐱', 'name': '动物币'},
            'meme': {'keywords': ['meme', 'pepe', 'wojak'], 'emoji': '🐸', 'name': 'Meme'},
            'money': {'keywords': ['money', 'cash', 'rich'], 'emoji': '💰', 'name': '金钱'},
        }
    
    def analyze_narrative(self, symbol: str, name: str) -> Tuple[str, str, int]:
        text = f"{symbol} {name}".lower()
        for nar_id, info in self.narratives.items():
            if any(kw in text for kw in info['keywords']):
                return info['emoji'], info['name'], 1
        return '❓', '其他', 0
    
    def get_holders(self, address: str) -> int:
        """查询DexScreener获取holder数量"""
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            data = r.json()
            
            pairs = data.get('pairs', [])
            if pairs:
                # 取第一个交易对的holder数
                return pairs[0].get('holders', 0) or 0
            return 0
        except:
            return 0
    
    def scan_page(self) -> List[Dict]:
        print("🪙 扫描 xyy.io/meme...")
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
                            'emoji': emoji,
                            'narrative': narrative,
                            'address_full': None,
                        }
                        
                        # 查找链接
                        j = i + 1
                        while j < len(lines) and j < i + 15:
                            next_line = lines[j].strip()
                            if '/url:' in next_line and 'pump.fun' in next_line:
                                url_match = re.search(r'/url:\s*(https://[^\s]+)', next_line)
                                if url_match:
                                    url = url_match.group(1)
                                    addr_match = re.search(r'/coin/([A-Za-z0-9]+)', url)
                                    if addr_match:
                                        token['address_full'] = addr_match.group(1)
                            j += 1
                        
                        # 只保留发射>60秒且有完整地址的
                        if time_seconds > 60 and token.get('address_full'):
                            tokens.append(token)
                
                i += 1
            
            # 去重
            seen = set()
            unique = []
            for t in tokens:
                if t['address_full'] not in seen:
                    seen.add(t['address_full'])
                    unique.append(t)
            
            return unique[:15]  # 只处理前15个，避免超时
            
        except Exception as e:
            print(f"扫描失败: {e}")
            return []
    
    def filter_by_holders(self, tokens: List[Dict]) -> List[Dict]:
        """过滤holder≥100的币"""
        print(f"\n🔍 查询DexScreener holder数量（阈值: {self.min_holders}）...\n")
        
        qualified = []
        for i, token in enumerate(tokens, 1):
            print(f"{i}/{len(tokens)} 查询 {token['symbol']}...", end=' ')
            
            holders = self.get_holders(token['address_full'])
            token['holders'] = holders
            
            if holders >= self.min_holders:
                print(f"✅ holder: {holders}")
                qualified.append(token)
            else:
                print(f"❌ holder: {holders} (低于阈值)")
        
        return qualified
    
    def generate_report(self, tokens: List[Dict]) -> str:
        now = datetime.now()
        
        lines = [
            f"🪙 XXYY.io Meme扫描 | holder≥{self.min_holders}",
            f"⏰ {now.strftime('%Y-%m-%d %H:%M')}",
        ]
        
        if not tokens:
            lines.append(f"\n📭 暂无holder≥{self.min_holders}的代币")
            return "\n".join(lines)
        
        lines.append(f"\n📊 {len(tokens)}个达标:\n")
        
        # 按叙事分类
        for narrative in ['AI科技', '名人', '动物币', 'Meme', '金钱', '其他']:
            nar_tokens = [t for t in tokens if t['narrative'] == narrative]
            if nar_tokens:
                emoji = nar_tokens[0]['emoji']
                lines.append(f"{emoji} {narrative}")
                for t in nar_tokens[:3]:  # 每类最多3个
                    lines.append(f"• {t['symbol']} - {t['name']}")
                    lines.append(f"  发射: {t['time_ago']} | holder: {t['holders']}")
                    lines.append(f"  CA: {t['address_full'][:25]}...")
                lines.append("")
        
        lines.append("⚠️ holder数量仅作参考，DYOR")
        return "\n".join(lines)
    
    def run(self):
        print("🚀 启动 XXYY.io 扫描（holder过滤版）\n")
        
        tokens = self.scan_page()
        if not tokens:
            print("❌ 无代币数据")
            return []
        
        print(f"✅ 从xxyy.io获取 {len(tokens)} 个代币\n")
        
        qualified = self.filter_by_holders(tokens)
        report = self.generate_report(qualified)
        
        print(report)
        
        # 保存报告
        with open(f"/tmp/xxyy_holder_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", 'w') as f:
            f.write(report)
        
        return qualified


if __name__ == "__main__":
    scanner = XXYYScanner()
    scanner.run()
