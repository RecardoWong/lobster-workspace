#!/usr/bin/env python3
"""
🪙 XXYY.io Meme币扫描 - Monty AI分析版
用 Monty 安全执行 AI 生成的分析代码
"""

import subprocess
import re
from monty_analyzer import analyze_tokens, MontyAnalyzer
import json
from datetime import datetime
from typing import List, Dict, Tuple

class XXYYScannerWithMonty:
    """XXYY.io + Monty AI分析"""
    
    def __init__(self):
        platforms = "pump,letsbonk,bags"
        self.url = f"https://www.xxyy.io/meme?chainId=sol&platform={platforms}"
        self.timeout = 30
        self.min_holders = 100
        
        self.narratives = {
            'ai': {'keywords': ['ai', 'grok', 'gpt', 'tech', 'claude'], 'emoji': '🤖', 'name': 'AI科技'},
            'animal': {'keywords': ['cat', 'dog', 'frog', 'bear', 'inu'], 'emoji': '🐱', 'name': '动物币'},
            'gamble': {'keywords': ['casino', 'bet', 'gamble', 'tired'], 'emoji': '🎰', 'name': '赌博/博彩'},
            'gaming': {'keywords': ['pokemon', 'diglett', 'game'], 'emoji': '🎮', 'name': '游戏/动漫'},
            'religion': {'keywords': ['pope', 'god', 'jesus', 'church'], 'emoji': '⛪', 'name': '宗教/信仰'},
            'gym': {'keywords': ['mog', 'gym', 'fitness'], 'emoji': '💪', 'name': '健身/Gymbro'},
            'controversial': {'keywords': ['porn', 'sex', 'caveman'], 'emoji': '⚠️', 'name': '敏感/争议'},
            'money': {'keywords': ['bank', 'cash', 'rich', 'money'], 'emoji': '💰', 'name': '金钱/财富'},
            'holiday': {'keywords': ['valentine', 'christmas'], 'emoji': '🎄', 'name': '节日/情绪'},
        }
    
    def analyze_narrative(self, symbol: str, name: str) -> Tuple[str, str, int, str]:
        """分析叙事"""
        text = f"{symbol} {name}".lower()
        
        # 特殊叙事
        if 'claire' in text:
            return '🤖', 'AI科技', 3, 'AI助手/Claude谐音梗'
        elif 'mogger' in text or 'mog' in text:
            return '💪', '健身/Gymbro', 4, 'Gymbro文化，碾压别人'
        elif 'diglett' in text:
            return '🎮', '游戏/动漫', 4, '宝可梦地鼠IP，童年怀旧'
        elif 'caveman' in text or 'cmp' == symbol.lower():
            return '⚠️', '敏感/争议', 5, '原始人+色情，猎奇吸睛，高风险'
        elif 'inu' in text and 'bank' in text:
            return '🐱', '动物币+金融', 4, '日语狗+银行，狗币DeFi'
        elif 'pope' in text:
            return '⛪', '宗教/信仰', 3, '教皇/宗教梗'
        elif 'noval' in text or 'valentine' in text:
            return '🎄', '节日/情绪', 3, '反情人节主题'
        elif 'letired' in text:
            return '🎰', '赌博/博彩', 3, '"累了"法语梗，赌狗疲惫'
        elif 'blackrock' in text:
            return '💰', '金钱/财富', 4, '蹭贝莱德BlackRock'
        
        # 通用匹配
        for nar_id, info in self.narratives.items():
            if any(kw in text for kw in info['keywords']):
                return info['emoji'], info['name'], 2, f'关键词: {nar_id}'
        
        return '❓', '其他', 1, '无明显叙事'
    
    def scan_page(self) -> List[Dict]:
        """扫描页面"""
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
                        
                        emoji, narrative, strength, analysis = self.analyze_narrative(symbol, name)
                        
                        token = {
                            'symbol': symbol,
                            'name': name,
                            'time_ago': f"{time_val}{time_unit}",
                            'time_seconds': time_seconds,
                            'emoji': emoji,
                            'narrative': narrative,
                            'analysis': analysis,
                            'address_full': None,
                            'holders': 0,
                            'mc': 0,
                        }
                        
                        # 抓取数据
                        j = i + 1
                        while j < len(lines) and j < i + 25:
                            next_line = lines[j].strip()
                            if 'text:' in next_line and 'pump' in next_line:
                                break
                            
                            if '/url:' in next_line:
                                url_match = re.search(r'/url:\s*(https://[^\s]+)', next_line)
                                if url_match and 'pump.fun' in url_match.group(1):
                                    addr_match = re.search(r'/coin/([A-Za-z0-9]+)', url_match.group(1))
                                    if addr_match:
                                        token['address_full'] = addr_match.group(1)
                            
                            if next_line == '- term: ' and j + 1 < len(lines):
                                holder_match = re.search(r'definition:\s*"(\d+)"', lines[j + 1])
                                if holder_match:
                                    token['holders'] = int(holder_match.group(1))
                            
                            if next_line == '- term: MC' and j + 1 < len(lines):
                                mc_match = re.search(r'definition:\s*\$([0-9.]+)([KMB]?)', lines[j + 1])
                                if mc_match:
                                    mc_val = float(mc_match.group(1))
                                    unit = mc_match.group(2)
                                    if unit == 'K': token['mc'] = mc_val * 1000
                                    elif unit == 'M': token['mc'] = mc_val * 1000000
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
    
    def monty_analyze(self, tokens: List[Dict]) -> Dict:
        """使用通用 Monty 工具分析代币"""
        # 准备简化数据
        simple_tokens = []
        for t in tokens:
            simple_tokens.append({
                'symbol': t['symbol'],
                'holders': t['holders'],
                'mc': t['mc'],
                'narrative': t['narrative'],
            })
        
        # 调用通用工具
        result = analyze_tokens(simple_tokens)
        return result.get('result', {}) if result.get('success') else {}
    
    def generate_report(self, tokens: List[Dict], monty_stats: Dict) -> str:
        """生成报告 - 只显示MC >= $35K的代币"""
        now = datetime.now()
        
        # 过滤MC >= $35K的代币
        filtered_tokens = [t for t in tokens if t.get('mc', 0) >= 35000]
        
        # 如果没有达标的，生成简化报告
        if not filtered_tokens:
            lines = [
                f"🪙 XXYY.io Meme扫描 | Monty AI分析",
                f"⏰ {now.strftime('%Y-%m-%d %H:%M')}",
                f"📊 无达标代币",
                "",
                f"本次扫描 {len(tokens)} 个代币，",
                f"没有 MC ≥ $35K 的代币。",
                "",
                "最高MC: " + (f"${max(t.get('mc',0) for t in tokens)/1000:.1f}K" if tokens else "N/A")
            ]
            return "\n".join(lines)
        
        lines = [
            f"🪙 XXYY.io Meme扫描 | Monty AI分析",
            f"⏰ {now.strftime('%Y-%m-%d %H:%M')}",
            f"📊 {len(filtered_tokens)} 个达标代币 | MC≥$35K",
            ""
        ]
        
        # Monty AI 分析结果（基于过滤后的数据）
        if monty_stats:
            lines.append("### 🤖 Monty AI 分析")
            lines.append("")
            lines.append(f"• 总代币数: {len(filtered_tokens)} (MC≥$35K)")
            lines.append(f"• 平均 holders: {monty_stats.get('avg_holders', 0):.1f}")
            lines.append(f"• 平均 MC: ${monty_stats.get('avg_mc', 0)/1000:.1f}K")
            lines.append(f"• 最热门: {monty_stats.get('hottest_token', 'N/A')} ({monty_stats.get('hottest_holders', 0)} holders)")
            
            # 只统计过滤后列表中的热门币
            hot_in_filtered = [t['symbol'] for t in filtered_tokens if t['holders'] >= 200]
            if hot_in_filtered:
                lines.append(f"• 🔥 热门币 (≥200 holders): {', '.join(hot_in_filtered)}")
            
            lines.append("")
        
        # 代币详情 - 只显示MC>=35K的
        lines.append("### 📋 代币详情 (MC≥$35K)")
        lines.append("")
        
        for t in filtered_tokens[:15]:  # 显示前15个
            mc_str = f"${t['mc']/1000:.1f}K" if t['mc'] < 1000000 else f"${t['mc']/1000000:.2f}M"
            hot_marker = "🔥" if t['holders'] >= 200 else ""
            
            lines.append(f"{hot_marker} **{t['symbol']}** - {t['name']}")
            lines.append(f"  • 叙事: {t['analysis']}")
            lines.append(f"  • 数据: 👥{t['holders']} | MC:{mc_str} | {t['time_ago']}")
            lines.append(f"  • CA: `{t['address_full']}`")
            lines.append("")
        
        lines.append("⚠️ DYOR - 即使MC≥$35K仍可能归零")
        
        return "\n".join(lines)
    
    def run(self):
        """运行扫描+Monty分析"""
        print("🚀 启动 XXYY.io + Monty AI 分析\n")
        
        # 1. 扫描代币
        tokens = self.scan_page()
        if not tokens:
            print("❌ 无代币数据")
            return []
        
        print(f"✅ 获取 {len(tokens)} 个代币\n")
        
        # 2. Monty AI 分析
        print("🤖 Monty AI 分析中...")
        monty_stats = self.monty_analyze(tokens)
        print(f"✅ 分析完成\n")
        
        # 3. 生成报告
        report = self.generate_report(tokens, monty_stats)
        print(report)
        
        # 保存
        with open(f"/tmp/xxyy_monty_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", 'w') as f:
            f.write(report)
        
        return tokens


if __name__ == "__main__":
    scanner = XXYYScannerWithMonty()
    scanner.run()
