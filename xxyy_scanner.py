#!/usr/bin/env python3
"""
🪙 XXYY.io Meme币扫描 - 叙事分析版
筛选Pump+LetsBonk+Bags，holder≥100，带详细叙事分析
"""

import subprocess
import re
import json
from datetime import datetime
from typing import List, Dict, Tuple

class XXYYScanner:
    def __init__(self):
        # 筛选特定平台: Pump + LetsBonk + Bags
        platforms = "pump,letsbonk,bags"
        self.url = f"https://www.xxyy.io/meme?chainId=sol&platform={platforms}"
        self.timeout = 30
        self.min_holders = 100
        
        self.narratives = {
            'ai': {'keywords': ['ai', 'grok', 'gpt', 'tech', 'claude'], 'emoji': '🤖', 'name': 'AI科技'},
            'celebrity': {'keywords': ['elon', 'musk', 'trump', 'star'], 'emoji': '⭐', 'name': '名人/网红'},
            'animal': {'keywords': ['cat', 'dog', 'frog', 'bear', 'inu', 'wojak'], 'emoji': '🐱', 'name': '动物币'},
            'food': {'keywords': ['hotdog', 'pizza', 'burger', 'food'], 'emoji': '🌭', 'name': '食物'},
            'gamble': {'keywords': ['casino', 'bet', 'gamble', 'lottery', 'tired'], 'emoji': '🎰', 'name': '赌博/博彩'},
            'meme': {'keywords': ['meme', 'pepe', 'chad'], 'emoji': '🐸', 'name': '经典Meme'},
            'gaming': {'keywords': ['pokemon', 'diglett', 'game', 'mario'], 'emoji': '🎮', 'name': '游戏/动漫'},
            'religion': {'keywords': ['pope', 'god', 'jesus', 'church'], 'emoji': '⛪', 'name': '宗教/信仰'},
            'gym': {'keywords': ['mog', 'gym', 'fitness', 'alpha'], 'emoji': '💪', 'name': '健身/Gymbro'},
            'controversial': {'keywords': ['porn', 'sex', 'caveman'], 'emoji': '⚠️', 'name': '敏感/争议'},
            'money': {'keywords': ['bank', 'cash', 'rich', 'money'], 'emoji': '💰', 'name': '金钱/财富'},
            'holiday': {'keywords': ['valentine', 'christmas', 'halloween'], 'emoji': '🎄', 'name': '节日/情绪'},
        }
    
    def analyze_narrative(self, symbol: str, name: str) -> Tuple[str, str, int, str]:
        """分析叙事，返回(emoji, 分类名, 强度, 分析描述)"""
        text = f"{symbol} {name}".lower()
        
        # 特殊叙事分析
        if 'claire' in text:
            return '🤖', 'AI科技', 3, 'AI助手/Claude谐音梗'
        elif 'mogger' in text or 'mog' in text:
            return '💪', '健身/Gymbro', 4, '"Mog"网络用语=碾压别人，Gymbro文化'
        elif 'diglett' in text:
            return '🎮', '游戏/动漫', 4, '宝可梦地鼠IP，蹭童年怀旧'
        elif 'caveman' in text or 'cmp' == symbol.lower():
            return '⚠️', '敏感/争议', 5, '原始人+色情，猎奇吸睛，高风险'
        elif 'inu' in text and 'bank' in text:
            return '🐱', '动物币+金融', 4, '日语"狗"+银行，狗币DeFi概念'
        elif 'pope' in text:
            return '⛪', '宗教/信仰', 3, '教皇/宗教梗，可能蹭宗教事件'
        elif 'noval' in text or 'valentine' in text:
            return '🎄', '节日/情绪', 3, '反情人节主题，"No Valentine"情绪'
        elif 'letired' in text or 'tired' in text:
            return '🎰', '赌博/博彩', 3, '"累了"法语梗，赌狗疲惫感'
        elif 'blackrock' in text:
            return '💰', '金钱/财富', 4, '蹭贝莱德BlackRock，传统金融梗'
        
        # 通用关键词匹配
        for nar_id, info in self.narratives.items():
            if any(kw in text for kw in info['keywords']):
                return info['emoji'], info['name'], 2, f'关键词匹配: {nar_id}'
        
        return '❓', '其他', 1, '无明显叙事，纯meme'
    
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
                        
                        time_ago = f"{time_val}{time_unit}"
                        
                        emoji, narrative, strength, analysis = self.analyze_narrative(symbol, name)
                        
                        token = {
                            'symbol': symbol,
                            'name': name,
                            'time_ago': time_ago,
                            'time_seconds': time_seconds,
                            'emoji': emoji,
                            'narrative': narrative,
                            'analysis': analysis,
                            'strength': strength,
                            'address_full': None,
                            'holders': 0,
                            'mc': 0,
                        }
                        
                        # 查找链接和holder数据
                        j = i + 1
                        while j < len(lines) and j < i + 25:
                            next_line = lines[j].strip()
                            if 'text:' in next_line and 'pump' in next_line and '...' in next_line:
                                break
                            
                            if '/url:' in next_line:
                                url_match = re.search(r'/url:\s*(https://[^\s]+)', next_line)
                                if url_match:
                                    url = url_match.group(1)
                                    if 'pump.fun' in url:
                                        addr_match = re.search(r'/coin/([A-Za-z0-9]+)', url)
                                        if addr_match:
                                            token['address_full'] = addr_match.group(1)
                            
                            # 抓取holder数量
                            if next_line == '- term: ':
                                if j + 1 < len(lines):
                                    def_line = lines[j + 1].strip()
                                    holder_match = re.search(r'definition:\s*"(\d+)"', def_line)
                                    if holder_match:
                                        token['holders'] = int(holder_match.group(1))
                            
                            # 抓取MC
                            if next_line == '- term: MC':
                                if j + 1 < len(lines):
                                    def_line = lines[j + 1].strip()
                                    mc_match = re.search(r'definition:\s*\$([0-9.]+)([KMB]?)', def_line)
                                    if mc_match:
                                        mc_val = float(mc_match.group(1))
                                        mc_unit = mc_match.group(2)
                                        if mc_unit == 'K': token['mc'] = mc_val * 1000
                                        elif mc_unit == 'M': token['mc'] = mc_val * 1000000
                                        elif mc_unit == 'B': token['mc'] = mc_val * 1000000000
                                        else: token['mc'] = mc_val
                            j += 1
                        
                        if time_seconds > 60 and token.get('address_full') and token.get('holders', 0) >= self.min_holders:
                            tokens.append(token)
                
                i += 1
            
            # 去重
            seen = set()
            unique = []
            for t in tokens:
                if t['address_full'] not in seen:
                    seen.add(t['address_full'])
                    unique.append(t)
            
            return unique
            
        except Exception as e:
            print(f"扫描失败: {e}")
            return []
    
    def generate_report(self, tokens: List[Dict]) -> str:
        now = datetime.now()
        
        lines = [
            f"🪙 XXYY.io Meme扫描 | holder≥{self.min_holders}",
            f"⏰ {now.strftime('%Y-%m-%d %H:%M')}",
            f"📊 发现 {len(tokens)} 个达标代币",
            ""
        ]
        
        if not tokens:
            lines.append("📭 暂无holder≥100的代币")
            return "\n".join(lines)
        
        # 按叙事分类
        narrative_order = ['AI科技', '名人/网红', '动物币', '动物币+金融', '经典Meme', '赌博/博彩', '游戏/动漫', '健身/Gymbro', '宗教/信仰', '节日/情绪', '敏感/争议', '金钱/财富', '其他']
        
        for narrative in narrative_order:
            nar_tokens = [t for t in tokens if t['narrative'] == narrative]
            if nar_tokens:
                emoji = nar_tokens[0]['emoji']
                lines.append(f"### {emoji} {narrative}")
                lines.append("")
                
                for t in nar_tokens[:4]:  # 每类最多4个
                    mc_str = f"${t['mc']/1000:.1f}K" if t['mc'] < 1000000 else f"${t['mc']/1000000:.2f}M" if t['mc'] > 0 else "$0.0K"
                    lines.append(f"**{t['symbol']}** - {t['name']}")
                    lines.append(f"• 叙事: {t['analysis']}")
                    lines.append(f"• 数据: 👥{t['holders']} | MC:{mc_str} | 发射:{t['time_ago']}")
                    lines.append(f"• CA: `{t['address_full']}`")
                    lines.append("")
        
        # 热度排名
        lines.append("---")
        lines.append("### 🏆 叙事热度排名")
        lines.append("")
        sorted_tokens = sorted(tokens, key=lambda x: x['holders'], reverse=True)[:5]
        for i, t in enumerate(sorted_tokens, 1):
            risk = "⚠️ 高风险" if t['narrative'] == '敏感/争议' else "🟡 中风险" if t['holders'] < 150 else "🟢 较稳"
            lines.append(f"{i}. **{t['symbol']}** ({t['narrative']}) | 👥{t['holders']} | {risk}")
        
        lines.append("")
        lines.append("⚠️ 提示: 大部分仍可能归零，DYOR")
        
        return "\n".join(lines)
    
    def run(self):
        print("🚀 启动 XXYY.io 扫描（叙事分析版）\n")
        
        tokens = self.scan_page()
        report = self.generate_report(tokens)
        
        print(report)
        
        # 保存报告
        with open(f"/tmp/xxyy_narrative_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", 'w', encoding='utf-8') as f:
            f.write(report)
        
        return tokens


if __name__ == "__main__":
    scanner = XXYYScanner()
    scanner.run()
