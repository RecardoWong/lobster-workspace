#!/usr/bin/env python3
"""
Twitter KOL 学习监控 - @YuLin807
学习目标：交易分析、市场洞察、方法论
"""

import os
import re
import json
from datetime import datetime
from typing import List, Dict

class YuLin807Learner:
    """YuLin807 学习分析器"""
    
    def __init__(self):
        self.target_user = "YuLin807"
        self.learning_file = "/tmp/yulin807_learning.json"
        
        # 学习维度
        self.dimensions = {
            'market_analysis': '市场分析能力',
            'trading_psychology': '交易心理',
            'risk_management': '风险管理',
            'technical_skills': '技术分析',
            'narrative_sensing': '叙事感知',
            'sentiment_analysis': '情绪判断'
        }
        
        # 积累的知识库
        self.knowledge_base = {
            'patterns': [],  # 发现的模式
            'quotes': [],    # 经典语录
            'methods': [],   # 方法论
            'warnings': [],  # 风险提醒
            'insights': []   # 洞察
        }
    
    def analyze_tweet_for_learning(self, tweet_text: str, metadata: Dict = None) -> Dict:
        """从推文学习"""
        
        analysis = {
            'raw_text': tweet_text,
            'timestamp': datetime.now().isoformat(),
            'learning_points': [],
            'category': 'general',
            'key_insights': [],
            'actionable_items': [],
            'my_reflection': ''
        }
        
        text_lower = tweet_text.lower()
        
        # 1. 识别内容类型
        if any(w in text_lower for w in ['btc', 'bitcoin', 'eth', 'ethereum', 'crypto', 'coin']):
            analysis['category'] = 'market_analysis'
        elif any(w in text_lower for w in ['psychology', 'emotion', 'fomo', 'fear', 'greed']):
            analysis['category'] = 'trading_psychology'
        elif any(w in text_lower for w in ['risk', 'stop loss', 'position', 'size']):
            analysis['category'] = 'risk_management'
        elif any(w in text_lower for w in ['chart', 'pattern', 'support', 'resistance', 'ta']):
            analysis['category'] = 'technical_skills'
        elif any(w in text_lower for w in ['narrative', 'story', 'theme', 'trend']):
            analysis['category'] = 'narrative_sensing'
        
        # 2. 提取学习方法论
        # 寻找"如何..."、"为什么..."、"关键是..."等句式
        teaching_patterns = [
            r'(?:关键|要点|核心)是[：:]\s*([^。\n]+)',
            r'(?:学会|掌握|理解)[了]?\s*([^，。\n]+)',
            r'(?:记住|牢记)[：:]\s*([^。\n]+)',
            r'(?:原因|理由)是[：:]\s*([^。\n]+)',
            r'(?:建议|提醒)[：:]\s*([^。\n]+)',
        ]
        
        for pattern in teaching_patterns:
            matches = re.findall(pattern, tweet_text, re.IGNORECASE)
            for match in matches:
                analysis['learning_points'].append({
                    'type': 'methodology',
                    'content': match.strip(),
                    'source_quote': tweet_text[max(0, tweet_text.find(match)-20):tweet_text.find(match)+len(match)+20]
                })
        
        # 3. 提取风险提醒
        risk_keywords = ['风险', '小心', '注意', '警告', 'avoid', '小心', '谨慎', 'risk', 'warning']
        if any(kw in text_lower for kw in risk_keywords):
            analysis['learning_points'].append({
                'type': 'risk_warning',
                'content': '包含风险提醒',
                'full_context': tweet_text
            })
        
        # 4. 提取洞察
        insight_patterns = [
            r'(?:发现|意识到|明白)[了]?\s*([^。\n]+)',
            r'(?:原来|其实)[，]?\s*([^。\n]+)',
            r'(?:真相|本质)是[：:]\s*([^。\n]+)',
        ]
        
        for pattern in insight_patterns:
            matches = re.findall(pattern, tweet_text, re.IGNORECASE)
            for match in matches:
                analysis['key_insights'].append(match.strip())
        
        # 5. 生成我的反思
        analysis['my_reflection'] = self._generate_reflection(analysis)
        
        # 6. 可执行项
        analysis['actionable_items'] = self._extract_actionable_items(tweet_text)
        
        return analysis
    
    def _generate_reflection(self, analysis: Dict) -> str:
        """生成学习反思"""
        reflections = []
        
        category = analysis['category']
        learning_points = analysis['learning_points']
        
        if category == 'market_analysis':
            reflections.append("市场分析要点：如何解读当前行情")
        elif category == 'trading_psychology':
            reflections.append("交易心理：情绪管理的重要性")
        elif category == 'risk_management':
            reflections.append("风险管理：保护本金是第一要务")
        elif category == 'narrative_sensing':
            reflections.append("叙事感知：抓住市场主线")
        
        if learning_points:
            reflections.append(f"学到 {len(learning_points)} 个知识点")
        
        return "；".join(reflections) if reflections else "持续学习中"
    
    def _extract_actionable_items(self, text: str) -> List[str]:
        """提取可执行的建议"""
        items = []
        
        # 寻找建议性语句
        patterns = [
            r'(?:建议|应该|可以|试试)[：:]?\s*([^。\n]+)',
            r'(?:关注|观察|注意)[：:]?\s*([^。\n]+)',
            r'(?:不要|避免|切勿)\s*([^。\n]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                items.append(match.strip())
        
        return items[:3]  # 最多3条
    
    def generate_learning_report(self, analyses: List[Dict]) -> str:
        """生成学习报告"""
        lines = [
            "📚 YuLin807 学习笔记",
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 60,
            ""
        ]
        
        # 按类别分组
        by_category = {}
        for a in analyses:
            cat = a['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(a)
        
        # 各分类总结
        for cat, items in by_category.items():
            cat_name = self.dimensions.get(cat, cat)
            lines.append(f"\n🎯 {cat_name} ({len(items)}条)")
            lines.append("-" * 40)
            
            for i, item in enumerate(items[:3], 1):  # 每类最多3条
                lines.append(f"\n  {i}. 原文摘录:")
                lines.append(f"     {item['raw_text'][:100]}...")
                
                if item['learning_points']:
                    lines.append(f"     💡 学习点:")
                    for lp in item['learning_points'][:2]:
                        lines.append(f"        • {lp['content'][:60]}")
                
                if item['key_insights']:
                    lines.append(f"     🔍 洞察:")
                    for insight in item['key_insights'][:2]:
                        lines.append(f"        • {insight[:60]}")
                
                if item['actionable_items']:
                    lines.append(f"     ✅ 可执行:")
                    for action in item['actionable_items']:
                        lines.append(f"        → {action[:60]}")
        
        # 总体反思
        lines.append(f"\n{'='*60}")
        lines.append("🤔 我的总体反思:")
        
        all_insights = []
        for a in analyses:
            all_insights.extend(a['key_insights'])
        
        if all_insights:
            lines.append("从YuLin807的推文学到的核心洞察:")
            for insight in all_insights[:5]:
                lines.append(f"  • {insight}")
        else:
            lines.append("持续观察中，积累更多市场智慧...")
        
        lines.append(f"\n{'='*60}")
        lines.append("💭 学习方法: 记录-反思-实践-复盘")
        
        return "\n".join(lines)
    
    def save_learning(self, analysis: Dict):
        """保存学习内容"""
        learnings = []
        if os.path.exists(self.learning_file):
            try:
                with open(self.learning_file, 'r') as f:
                    learnings = json.load(f)
            except:
                pass
        
        learnings.append(analysis)
        
        with open(self.learning_file, 'w') as f:
            json.dump(learnings[-50:], f, indent=2)  # 保留最近50条
    
    def get_learning_summary(self) -> str:
        """获取学习总结"""
        if not os.path.exists(self.learning_file):
            return "暂无学习记录"
        
        try:
            with open(self.learning_file, 'r') as f:
                learnings = json.load(f)
            
            total = len(learnings)
            categories = {}
            for l in learnings:
                cat = l['category']
                categories[cat] = categories.get(cat, 0) + 1
            
            lines = [
                f"📊 YuLin807 学习统计",
                f"总学习推文: {total}",
                f"分类分布:"
            ]
            
            for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
                cat_name = self.dimensions.get(cat, cat)
                lines.append(f"  • {cat_name}: {count}")
            
            return "\n".join(lines)
        except:
            return "学习记录读取失败"


def main():
    """测试学习分析"""
    learner = YuLin807Learner()
    
    # 模拟测试推文
    test_tweets = [
        "关键是控制风险，永远不要把所有资金放在一个仓位上",
        "FOMO情绪是最危险的，记住：市场永远有机会",
        "这个叙事不错，但需要观察成交量是否配合",
        "建议关注BTC在4万美金的支撑情况"
    ]
    
    analyses = []
    for tweet in test_tweets:
        analysis = learner.analyze_tweet_for_learning(tweet)
        analyses.append(analysis)
        learner.save_learning(analysis)
    
    report = learner.generate_learning_report(analyses)
    print(report)
    
    print("\n" + "="*60)
    print(learner.get_learning_summary())


if __name__ == "__main__":
    main()
