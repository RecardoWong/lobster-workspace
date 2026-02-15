#!/usr/bin/env python3
"""
🚀 Elon Musk 推文内容分析系统（极简版）
早晚两次报告（08:00 & 21:00）
只展示推文内容分类，无数据、无投资建议
"""

import json
from datetime import datetime
from typing import List, Dict

class ElonContentAnalyzer:
    """Elon内容分析师 - 极简版"""
    
    def __init__(self):
        # 移除Dogecoin，只保留核心产业
        self.industries = {
            'tesla': {
                'name': '🚗 Tesla',
                'keywords': ['tesla', 'tsla', 'cybertruck', 'autopilot', 'fsd', 'model s', 'model 3', 'model x', 'model y'],
                'focus': '电动车产品、自动驾驶技术、工厂产能'
            },
            'spacex': {
                'name': '🚀 SpaceX',
                'keywords': ['spacex', 'starship', 'falcon', 'starlink', 'mars', 'rocket', 'launch'],
                'focus': '星舰试飞、星链服务、太空任务'
            },
            'xai': {
                'name': '🤖 xAI',
                'keywords': ['xai', 'grok', 'ai', 'artificial intelligence', 'agi'],
                'focus': 'AI技术、Grok产品、研发进展'
            },
            'twitter': {
                'name': '🐦 X',
                'keywords': ['x', 'twitter', 'tweet', 'platform'],
                'focus': '平台功能、内容政策、产品更新'
            },
            'neuralink': {
                'name': '🧠 Neuralink',
                'keywords': ['neuralink', 'brain', 'neural'],
                'focus': '脑机接口、临床试验、技术突破'
            },
            'boring': {
                'name': '🚇 Boring',
                'keywords': ['boring', 'tunnel', 'hyperloop'],
                'focus': '隧道工程、交通项目'
            },
            'other': {
                'name': '📝 其他',
                'keywords': [],
                'focus': '个人动态、社会话题、其他内容'
            }
        }
    
    def analyze_content(self, text: str) -> List[str]:
        """分析推文内容涉及的产业"""
        if not text:
            return ['other']
        
        text_lower = text.lower()
        matched = []
        
        for ind_id, info in self.industries.items():
            if ind_id == 'other':
                continue
            for keyword in info['keywords']:
                if keyword in text_lower:
                    matched.append(ind_id)
                    break
        
        return matched if matched else ['other']
    
    def clean_text(self, text: str) -> str:
        """清理推文内容"""
        # 去除链接
        text = text.split('http')[0]
        # 去除@mention
        words = text.split()
        clean_words = [w for w in words if not w.startswith('@')]
        return ' '.join(clean_words).strip()
    
    def generate_report(self, tweets: List[Dict]) -> str:
        """生成极简内容报告"""
        now = datetime.now()
        period = "早報" if now.hour < 12 else "晚報"
        
        lines = [
            f"🚀 Elon Musk | {period}",
            f"📅 {now.strftime('%m月%d日')}",
            "=" * 40,
            ""
        ]
        
        if not tweets:
            lines.append("📭 本时段无新推文")
            return "\n".join(lines)
        
        # 按产业分类
        industry_content = {ind_id: [] for ind_id in self.industries.keys()}
        
        for tweet in tweets:
            text = tweet.get('text', '').strip()
            if not text:
                continue
            
            industries = self.analyze_content(text)
            clean = self.clean_text(text)
            
            if clean:
                for ind_id in industries:
                    if clean not in industry_content[ind_id]:
                        industry_content[ind_id].append(clean)
        
        # 生成报告 - 按优先级
        has_content = False
        priority = ['tesla', 'spacex', 'xai', 'twitter', 'neuralink', 'boring', 'other']
        
        for ind_id in priority:
            contents = industry_content.get(ind_id, [])
            if not contents:
                continue
            
            has_content = True
            info = self.industries[ind_id]
            
            # 产业标题
            lines.append(f"\n{info['name']} | {info['focus']}")
            lines.append("─" * 40)
            
            # 列出内容（去重，最多3条）
            for content in contents[:3]:
                lines.append(f"• {content[:100]}")
        
        if not has_content:
            lines.append("\n📭 本时段无相关内容")
        
        lines.append("\n" + "=" * 40)
        
        return "\n".join(lines)


def main():
    """主函数"""
    analyzer = ElonContentAnalyzer()
    
    # 模拟数据
    sample = [
        {'text': 'Tesla FSD v12 is amazing!'},
        {'text': 'Starship launch next week'},
        {'text': 'Grok is learning fast'},
        {'text': 'Great progress at xAI'},
    ]
    
    print(analyzer.generate_report(sample))


if __name__ == "__main__":
    main()
