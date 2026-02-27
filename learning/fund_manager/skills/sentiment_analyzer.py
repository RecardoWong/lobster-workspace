#!/usr/bin/env python3
"""
情感分析器 - 基于VADER
完全免费，本地运行，无需API Key

VADER (Valence Aware Dictionary and sEntiment Reasoner)
- 专门设计用于社交媒体文本的情感分析
- 对金融新闻也很有效
- 完全免费，本地运行
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
import re

# 尝试导入vaderSentiment，如果没有则使用简单实现
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print("[提示] vaderSentiment未安装，使用简化版情感分析")
    print("安装命令: pip install vaderSentiment")


@dataclass
class SentimentResult:
    """情感分析结果"""
    text: str
    sentiment: str  # positive/negative/neutral
    score: float    # -1 (最负面) 到 +1 (最正面)
    confidence: float  # 置信度 0-1
    
    # 详细分数
    positive: float  # 正面成分 0-1
    negative: float  # 负面成分 0-1
    neutral: float   # 中性成分 0-1


class SentimentAnalyzer:
    """情感分析器"""
    
    # 金融领域的正面/负面关键词 (简化版备用)
    POSITIVE_WORDS = {
        'surge', 'soar', 'jump', 'rally', 'gain', 'rise', 'up', 'higher', 'bullish',
        'beat', 'exceed', 'outperform', 'strong', 'growth', 'profit', 'boom',
        'recovery', 'optimistic', 'confident', 'success', 'breakthrough',
        '暴涨', '大涨', '上涨', '利好', '强劲', '超预期', '盈利', '增长'
    }
    
    NEGATIVE_WORDS = {
        'plunge', 'crash', 'drop', 'fall', 'decline', 'down', 'lower', 'bearish',
        'miss', 'underperform', 'weak', 'loss', 'recession', 'crisis', 'risk',
        'concern', 'worried', 'pessimistic', 'fail', 'bankruptcy', 'layoff',
        '暴跌', '大跌', '下跌', '利空', '疲软', '亏损', '衰退', '风险'
    }
    
    def __init__(self):
        """初始化情感分析器"""
        if VADER_AVAILABLE:
            self.analyzer = SentimentIntensityAnalyzer()
            self._use_vader = True
        else:
            self.analyzer = None
            self._use_vader = False
    
    def analyze(self, text: str) -> SentimentResult:
        """
        分析文本情感
        
        Args:
            text: 要分析的文本
            
        Returns:
            SentimentResult对象
        """
        if not text:
            return SentimentResult(
                text="",
                sentiment="neutral",
                score=0.0,
                confidence=0.0,
                positive=0.0,
                negative=0.0,
                neutral=1.0
            )
        
        if self._use_vader:
            return self._analyze_with_vader(text)
        else:
            return self._analyze_simple(text)
    
    def _analyze_with_vader(self, text: str) -> SentimentResult:
        """使用VADER分析"""
        scores = self.analyzer.polarity_scores(text)
        
        # VADER返回: neg, neu, pos, compound
        compound = scores['compound']  # -1到1
        
        # 确定情感类别
        if compound >= 0.05:
            sentiment = "positive"
        elif compound <= -0.05:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # 置信度 (基于极性强度)
        confidence = abs(compound)
        
        return SentimentResult(
            text=text[:100] + "..." if len(text) > 100 else text,
            sentiment=sentiment,
            score=compound,
            confidence=confidence,
            positive=scores['pos'],
            negative=scores['neg'],
            neutral=scores['neu']
        )
    
    def _analyze_simple(self, text: str) -> SentimentResult:
        """简化版情感分析 (无VADER时使用)"""
        text_lower = text.lower()
        
        # 统计关键词
        pos_count = sum(1 for word in self.POSITIVE_WORDS if word in text_lower)
        neg_count = sum(1 for word in self.NEGATIVE_WORDS if word in text_lower)
        total = pos_count + neg_count
        
        if total == 0:
            return SentimentResult(
                text=text[:100] + "..." if len(text) > 100 else text,
                sentiment="neutral",
                score=0.0,
                confidence=0.5,
                positive=0.33,
                negative=0.33,
                neutral=0.34
            )
        
        # 计算分数
        score = (pos_count - neg_count) / total
        
        if score > 0.1:
            sentiment = "positive"
        elif score < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # 置信度
        confidence = min(abs(score) * 2, 1.0)
        
        # 成分
        total_words = len(text_lower.split())
        positive = pos_count / max(total_words, 1)
        negative = neg_count / max(total_words, 1)
        neutral = 1 - positive - negative
        
        return SentimentResult(
            text=text[:100] + "..." if len(text) > 100 else text,
            sentiment=sentiment,
            score=score,
            confidence=confidence,
            positive=max(0, positive),
            negative=max(0, negative),
            neutral=max(0, neutral)
        )
    
    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """批量分析"""
        return [self.analyze(text) for text in texts]
    
    def get_aggregate_sentiment(self, results: List[SentimentResult]) -> Dict:
        """
        计算聚合情感
        
        Args:
            results: 多条情感分析结果
            
        Returns:
            聚合统计
        """
        if not results:
            return {
                'average_score': 0.0,
                'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
                'overall_sentiment': 'neutral'
            }
        
        # 平均分数
        avg_score = sum(r.score for r in results) / len(results)
        
        # 分布统计
        distribution = {'positive': 0, 'neutral': 0, 'negative': 0}
        for r in results:
            distribution[r.sentiment] += 1
        
        # 总体情感
        if avg_score >= 0.1:
            overall = 'positive'
        elif avg_score <= -0.1:
            overall = 'negative'
        else:
            overall = 'neutral'
        
        return {
            'average_score': round(avg_score, 3),
            'sentiment_distribution': distribution,
            'overall_sentiment': overall,
            'total_analyzed': len(results)
        }


# 测试运行
if __name__ == "__main__":
    print("情感分析器测试")
    print("="*50)
    
    analyzer = SentimentAnalyzer()
    
    # 测试文本
    test_texts = [
        "Apple stock surges 5% after beating earnings expectations!",
        "Market crashes as recession fears grow",
        "Federal Reserve announces steady interest rates",
        "Tech stocks rally on AI breakthrough news",
        "Company reports massive losses and layoffs"
    ]
    
    print(f"\n使用{'VADER' if VADER_AVAILABLE else '简化版'}分析:\n")
    
    results = []
    for text in test_texts:
        result = analyzer.analyze(text)
        results.append(result)
        
        emoji = {"positive": "📈", "negative": "📉", "neutral": "➡️"}[result.sentiment]
        print(f"{emoji} {result.sentiment.upper()}")
        print(f"   分数: {result.score:+.3f}")
        print(f"   文本: {result.text[:60]}...")
        print()
    
    # 聚合分析
    print("="*50)
    aggregate = analyzer.get_aggregate_sentiment(results)
    print("聚合情感分析:")
    print(f"  平均分: {aggregate['average_score']:+.3f}")
    print(f"  总体情感: {aggregate['overall_sentiment']}")
    print(f"  分布: {aggregate['sentiment_distribution']}")
