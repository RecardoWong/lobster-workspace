#!/usr/bin/env python3
"""
爆款公式库自动更新器
分析采集的数据，提炼和更新爆款公式
"""

import json
from datetime import datetime
from typing import Dict, List
from collections import Counter

class FormulaUpdater:
    """爆款公式库更新器"""
    
    def __init__(self):
        self.formula_db_path = "/root/.openclaw/workspace/content_analyzer/CONTENT_FORMULAS.md"
        self.data_path = "/root/.openclaw/workspace/content_analyzer/data/"
    
    def load_collected_data(self) -> List[Dict]:
        """加载采集的数据"""
        import os
        import glob
        
        # 找最新的数据文件
        files = glob.glob(f"{self.data_path}/x_posts_*.json")
        if not files:
            return []
        
        latest_file = max(files, key=os.path.getctime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def analyze_title_patterns(self, posts: List[Dict]) -> Dict:
        """分析标题模式"""
        first_lines = [p['content'].split('\n')[0] for p in posts]
        
        patterns = {
            'number_type': 0,
            'question_type': 0,
            'how_to_type': 0,
            'statement_type': 0,
            'list_type': 0
        }
        
        for line in first_lines:
            # 数字式
            if any(c.isdigit() for c in line[:20]):
                patterns['number_type'] += 1
            # 提问式
            elif '?' in line or '？' in line or line.startswith(('为什么', '如何', '怎么')):
                patterns['question_type'] += 1
            # 教程式
            elif line.startswith(('How to', '如何', '怎么', '教你')):
                patterns['how_to_type'] += 1
            # 清单式
            elif 'things' in line.lower() or 'ways' in line.lower() or '个' in line:
                patterns['list_type'] += 1
            else:
                patterns['statement_type'] += 1
        
        return patterns
    
    def analyze_structure_patterns(self, posts: List[Dict]) -> Dict:
        """分析结构模式"""
        structures = []
        
        for post in posts:
            content = post['content']
            
            # Thread格式
            if '🧵' in content or 'thread' in content.lower():
                structures.append('thread')
            # 清单格式 (1. 2. 3.)
            elif any(f'{i}.' in content for i in range(1, 10)):
                structures.append('listicle')
            # 短段落格式
            elif content.count('\n\n') >= 3:
                structures.append('short_paragraphs')
            else:
                structures.append('standard')
        
        return dict(Counter(structures))
    
    def analyze_engagement_factors(self, posts: List[Dict]) -> Dict:
        """分析高互动因素"""
        high_engagement = [p for p in posts if p['metrics']['engagement_rate'] > 0.04]
        
        factors = {
            'has_numbers': 0,
            'has_personal_story': 0,
            'has_data': 0,
            'has_controversy': 0,
            'has_call_to_action': 0
        }
        
        for post in high_engagement:
            content = post['content'].lower()
            
            if any(c.isdigit() for c in content):
                factors['has_numbers'] += 1
            if any(word in content for word in ['i ', 'my ', 'me ', '我', '我的']):
                factors['has_personal_story'] += 1
            if any(word in content for word in ['%', 'data', 'study', 'research', '数据']):
                factors['has_data'] += 1
            if any(word in content for word in ['but', 'however', 'vs', '对比', '但是']):
                factors['has_controversy'] += 1
            if any(word in content for word in ['comment', 'share', 'follow', '评论', '关注']):
                factors['has_call_to_action'] += 1
        
        return factors
    
    def generate_new_formulas(self, posts: List[Dict]) -> str:
        """生成新的公式建议"""
        title_patterns = self.analyze_title_patterns(posts)
        structure_patterns = self.analyze_structure_patterns(posts)
        engagement_factors = self.analyze_engagement_factors(posts)
        
        report = f"""
# 📊 爆款公式库更新报告 ({datetime.now().strftime('%Y-%m-%d')})

## 数据统计
- 分析样本: {len(posts)} 条爆款帖子
- 分类: Finance {sum(1 for p in posts if p['category']=='finance')}条, 
        Tech {sum(1 for p in posts if p['category']=='tech')}条, 
        Crypto {sum(1 for p in posts if p['category']=='crypto')}条

## 标题模式分析
- 数字式: {title_patterns['number_type']} ({title_patterns['number_type']/len(posts)*100:.0f}%)
- 提问式: {title_patterns['question_type']} ({title_patterns['question_type']/len(posts)*100:.0f}%)
- 教程式: {title_patterns['how_to_type']} ({title_patterns['how_to_type']/len(posts)*100:.0f}%)
- 清单式: {title_patterns['list_type']} ({title_patterns['list_type']/len(posts)*100:.0f}%)
- 陈述式: {title_patterns['statement_type']} ({title_patterns['statement_type']/len(posts)*100:.0f}%)

## 结构模式分析
"""
        for struct, count in structure_patterns.items():
            report += f"- {struct}: {count}\n"
        
        report += f"""
## 高互动因素 (Top 20%爆款)
"""
        for factor, count in engagement_factors.items():
            report += f"- {factor}: {count}\n"
        
        report += f"""
## 💡 新发现的有效模式

### 标题公式更新
"""
        
        # 根据数据生成具体建议
        if title_patterns['number_type'] >= len(posts) * 0.4:
            report += """
**强调: 数字式标题效果突出**
- 使用场景: 经验总结、方法论、数据分享
- 公式: [数字] + [极端结果] + [转折词]
- 例: "3年亏掉100万后，我悟到的5个真相"
"""
        
        if engagement_factors['has_personal_story'] > len(posts) * 0.3:
            report += """
**强调: 个人故事增强信任感**
- 使用场景: 经验分享、教训总结
- 公式: [我的经历] + [数据/结果] + [洞察]
- 例: "我在凌晨3点盯着账户..."
"""
        
        report += f"""

### 结构公式更新
"""
        
        if 'listicle' in structure_patterns and structure_patterns['listicle'] >= 2:
            report += """
**清单式结构 (Listicle)**
- 适用: 教程、经验总结、资源分享
- 优势: 易读、易传播、易收藏
- 最佳实践:
  1. 3-5条为佳，不超过7条
  2. 每条配1个故事/数据/案例
  3. 最后一条放金句/升华
"""
        
        if 'thread' in structure_patterns:
            report += """
**Thread格式 (🧵)**
- 适用: Twitter深度内容
- 优势: 系统性强、专业感强
- 最佳实践:
  1. 开头用钩子吸引
  2. 每段1个观点+支撑
  3. 结尾CTA引导互动
"""
        
        return report
    
    def update_formula_database(self):
        """更新公式库"""
        posts = self.load_collected_data()
        
        if not posts:
            print("❌ 没有数据可分析")
            return
        
        report = self.generate_new_formulas(posts)
        
        # 保存报告
        report_file = f"/root/.openclaw/workspace/content_analyzer/reports/formula_update_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 公式库更新报告已生成: {report_file}")
        print("\n" + "="*70)
        print(report)

if __name__ == '__main__':
    updater = FormulaUpdater()
    updater.update_formula_database()
