#!/usr/bin/env python3
"""
Skill 1: 爆款标题分析器
分析标题结构、情绪强度、传播潜力
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class TitleType(Enum):
    QUESTION = "提问式"      # 为什么/如何...
    NUMBER = "数字式"        # 5个方法/3年经验
    CONTRAST = "对比式"      # A vs B
    EMOTION = "情绪式"       # 震惊/泪目
    SUSPENSE = "悬念式"      # 没想到/原来
    IDENTITY = "身份式"      # 基金经理/创业者
    HOW_TO = "教程式"        # 如何/怎么
    LIST = "清单式"          # 盘点/合集

@dataclass
class TitleAnalysis:
    title: str
    title_type: TitleType
    type_confidence: float  # 0-1
    
    # 评分维度
    curiosity_score: int    # 好奇心激发 (0-100)
    emotion_score: int      # 情绪强度 (0-100)
    specificity_score: int  # 具体性 (0-100)
    brevity_score: int      # 简洁度 (0-100)
    overall_score: int      # 综合评分 (0-100)
    
    # 关键词
    keywords: List[str]
    emotion_words: List[str]
    power_words: List[str]
    
    # 建议
    improvements: List[str]
    alternative_titles: List[str]

class TitleAnalyzer:
    """爆款标题分析器"""
    
    def __init__(self):
        # 情绪词库
        self.emotion_words = {
            'high': ['震惊', '恐怖', '疯了', '炸裂', '泪目', '破防', '扎心', '太真实'],
            'medium': ['注意', '警惕', '小心', '重要', '关键', '秘密', '真相'],
            'low': ['分享', '推荐', '介绍', '说明', '浅析']
        }
        
        # 强力词库
        self.power_words = [
            '独家', '揭秘', '曝光', '内幕', '秘籍', '绝招', '神操作',
            '血亏', '暴富', '逆袭', '翻盘', '绝杀', '王炸',
            '99%', '100%', '所有人', '永远', '绝对', '必须'
        ]
        
        # 数字模式
        self.number_pattern = re.compile(r'(\d+)[个条种类位年天万亿]')
        
    def analyze(self, title: str) -> TitleAnalysis:
        """分析标题"""
        # 1. 识别标题类型
        title_type, confidence = self._identify_type(title)
        
        # 2. 计算各维度评分
        curiosity = self._score_curiosity(title, title_type)
        emotion = self._score_emotion(title)
        specificity = self._score_specificity(title)
        brevity = self._score_brevity(title)
        overall = self._calculate_overall(curiosity, emotion, specificity, brevity, title_type)
        
        # 3. 提取关键词
        keywords = self._extract_keywords(title)
        emotion_words = self._extract_emotion_words(title)
        power_words = self._extract_power_words(title)
        
        # 4. 生成改进建议
        improvements = self._generate_improvements(title, title_type, curiosity, emotion)
        alternatives = self._generate_alternatives(title, title_type)
        
        return TitleAnalysis(
            title=title,
            title_type=title_type,
            type_confidence=confidence,
            curiosity_score=curiosity,
            emotion_score=emotion,
            specificity_score=specificity,
            brevity_score=brevity,
            overall_score=overall,
            keywords=keywords,
            emotion_words=emotion_words,
            power_words=power_words,
            improvements=improvements,
            alternative_titles=alternatives
        )
    
    def _identify_type(self, title: str) -> Tuple[TitleType, float]:
        """识别标题类型"""
        title_lower = title.lower()
        scores = {}
        
        # 提问式
        if any(w in title for w in ['为什么', '如何', '怎么', '什么', '吗？', '呢？']):
            scores[TitleType.QUESTION] = 0.9
        
        # 数字式
        if self.number_pattern.search(title) or re.search(r'[一二三四五六七八九十]', title):
            scores[TitleType.NUMBER] = 0.85
        
        # 对比式
        if any(w in title for w in ['vs', '对比', '差距', '区别', ' PK ', '不如', '超过']):
            scores[TitleType.CONTRAST] = 0.9
        
        # 情绪式
        emotion_count = sum(1 for w in self.emotion_words['high'] if w in title)
        if emotion_count >= 1:
            scores[TitleType.EMOTION] = 0.8 + emotion_count * 0.05
        
        # 悬念式
        if any(w in title for w in ['没想到', '原来', '竟然', '才发现', '真相是']):
            scores[TitleType.SUSPENSE] = 0.85
        
        # 身份式
        if any(w in title for w in ['基金经理', '投资人', '创业者', '老板', '高管', '专家']):
            scores[TitleType.IDENTITY] = 0.8
        
        # 教程式
        if any(w in title for w in ['如何', '怎么', '教程', '攻略', '指南', '手把手']):
            scores[TitleType.HOW_TO] = 0.85
        
        # 清单式
        if any(w in title for w in ['盘点', '合集', '清单', '汇总', '大全']):
            scores[TitleType.LIST] = 0.85
        
        if not scores:
            return TitleType.QUESTION, 0.3  # 默认
        
        best_type = max(scores, key=scores.get)
        return best_type, scores[best_type]
    
    def _score_curiosity(self, title: str, title_type: TitleType) -> int:
        """评分好奇心激发 (0-100)"""
        score = 50
        
        # 提问式天然好奇
        if title_type == TitleType.QUESTION:
            score += 20
        
        # 悬念词
        if any(w in title for w in ['为什么', '如何', '秘密', '真相', '内幕']):
            score += 15
        
        # 信息缺口
        if '...' in title or '?' in title:
            score += 10
        
        # 反常识
        if any(w in title for w in ['却', '反而', '竟然', '居然']):
            score += 15
        
        return min(score, 100)
    
    def _score_emotion(self, title: str) -> int:
        """评分情绪强度 (0-100)"""
        score = 30
        
        # 高强度情绪词
        for word in self.emotion_words['high']:
            if word in title:
                score += 20
        
        # 中强度情绪词
        for word in self.emotion_words['medium']:
            if word in title:
                score += 10
        
        # 强力词
        for word in self.power_words:
            if word in title:
                score += 5
        
        # 感叹号
        score += title.count('！') * 5
        
        return min(score, 100)
    
    def _score_specificity(self, title: str) -> int:
        """评分具体性 (0-100)"""
        score = 40
        
        # 数字
        if self.number_pattern.search(title):
            score += 20
        
        # 时间/金额具体
        if re.search(r'\d+[年天月亿万千元]', title):
            score += 15
        
        # 身份具体
        if any(w in title for w in ['我', '你', '他', '我们', '大家']):
            score += 10
        
        # 场景具体
        if any(w in title for w in ['凌晨', '深夜', '早上', '第一次', '终于']):
            score += 10
        
        return min(score, 100)
    
    def _score_brevity(self, title: str) -> int:
        """评分简洁度 (0-100)"""
        length = len(title)
        
        # 最佳长度 15-25字
        if 15 <= length <= 25:
            return 90
        elif 10 <= length < 15 or 25 < length <= 30:
            return 70
        elif length < 10:
            return 50  # 太短
        else:
            return max(100 - (length - 30) * 2, 30)  # 太长扣分
    
    def _calculate_overall(self, curiosity: int, emotion: int, 
                          specificity: int, brevity: int, title_type: TitleType) -> int:
        """计算综合评分"""
        # 权重
        weights = {
            TitleType.QUESTION: {'curiosity': 0.35, 'emotion': 0.20, 'specificity': 0.25, 'brevity': 0.20},
            TitleType.NUMBER: {'curiosity': 0.25, 'emotion': 0.15, 'specificity': 0.35, 'brevity': 0.25},
            TitleType.EMOTION: {'curiosity': 0.25, 'emotion': 0.40, 'specificity': 0.20, 'brevity': 0.15},
            TitleType.SUSPENSE: {'curiosity': 0.40, 'emotion': 0.25, 'specificity': 0.20, 'brevity': 0.15},
            TitleType.IDENTITY: {'curiosity': 0.25, 'emotion': 0.20, 'specificity': 0.30, 'brevity': 0.25},
        }
        
        w = weights.get(title_type, {'curiosity': 0.30, 'emotion': 0.25, 'specificity': 0.25, 'brevity': 0.20})
        
        overall = (
            curiosity * w['curiosity'] +
            emotion * w['emotion'] +
            specificity * w['specificity'] +
            brevity * w['brevity']
        )
        
        return int(overall)
    
    def _extract_keywords(self, title: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取 (实际可用jieba分词)
        # 这里用简单规则
        words = []
        
        # 提取名词性短语 (简化版)
        patterns = [
            r'(\w+)(?:方法|技巧|策略|经验|教训|秘密|真相|规律)',
            r'(\w+)(?:心得|感悟|思考|分析|解读|揭秘)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, title)
            words.extend(matches)
        
        return words[:5]
    
    def _extract_emotion_words(self, title: str) -> List[str]:
        """提取情绪词"""
        found = []
        for category in self.emotion_words.values():
            for word in category:
                if word in title:
                    found.append(word)
        return found
    
    def _extract_power_words(self, title: str) -> List[str]:
        """提取强力词"""
        return [w for w in self.power_words if w in title]
    
    def _generate_improvements(self, title: str, title_type: TitleType, 
                               curiosity: int, emotion: int) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if curiosity < 60:
            suggestions.append("建议增加好奇心钩子，如使用'为什么/如何'开头")
        
        if emotion < 50:
            suggestions.append("情绪强度不足，可加入'震惊/注意/警惕'等词")
        
        if len(title) > 30:
            suggestions.append("标题过长，建议控制在25字以内")
        elif len(title) < 12:
            suggestions.append("标题过短，建议补充具体信息")
        
        if not self.number_pattern.search(title) and title_type != TitleType.EMOTION:
            suggestions.append("可考虑加入数字，如'3个方法/5年经验'")
        
        return suggestions
    
    def _generate_alternatives(self, title: str, title_type: TitleType) -> List[str]:
        """生成替代标题"""
        alternatives = []
        
        # 提问式变体
        if title_type != TitleType.QUESTION:
            alternatives.append(f"为什么{title.replace('？', '')}？")
        
        # 数字变体
        if not self.number_pattern.search(title):
            alternatives.append(f"3个{title}")
        
        # 情绪变体
        if '震惊' not in title and '注意' not in title:
            alternatives.append(f"震惊！{title}")
        
        return alternatives[:3]

# 测试
if __name__ == '__main__':
    analyzer = TitleAnalyzer()
    
    test_titles = [
        "3年亏掉100万后，我总结出的5条投资铁律",
        "为什么你越努力越穷？答案藏在这个被忽视的数据里",
        "基金经理私下告诉我：散户永远别碰这3类股票",
        "震惊！凌晨3点，我终于理解了什么是真正的财务自由",
        "投资入门指南"
    ]
    
    print("="*70)
    print("📝 爆款标题分析器")
    print("="*70)
    
    for title in test_titles:
        result = analyzer.analyze(title)
        
        print(f"\n📌 原标题: {result.title}")
        print(f"   类型: {result.title_type.value} (置信度{result.type_confidence*100:.0f}%)")
        print(f"   综合评分: {result.overall_score}/100")
        print(f"   维度: 好奇{result.curiosity_score} | 情绪{result.emotion_score} | 具体{result.specificity_score} | 简洁{result.brevity_score}")
        
        if result.emotion_words:
            print(f"   情绪词: {', '.join(result.emotion_words)}")
        
        if result.improvements:
            print(f"   建议: {' | '.join(result.improvements[:2])}")
        
        if result.alternative_titles:
            print(f"   替代: {result.alternative_titles[0]}")
    
    print("\n" + "="*70)
