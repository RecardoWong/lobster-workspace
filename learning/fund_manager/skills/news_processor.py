#!/usr/bin/env python3
"""
新闻处理器
整合NewsAPI获取 + VADER情感分析
生成每日市场新闻摘要
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skills.news_fetcher import NewsFetcher, NewsArticle
from skills.sentiment_analyzer import SentimentAnalyzer
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import Counter


class NewsProcessor:
    """新闻处理器"""
    
    def __init__(self, news_api_key: Optional[str] = None):
        """
        初始化
        
        Args:
            news_api_key: NewsAPI Key (可选，免费申请)
        """
        self.fetcher = NewsFetcher(api_key=news_api_key)
        self.analyzer = SentimentAnalyzer()
    
    def process_daily_news(
        self,
        keywords: Optional[List[str]] = None,
        days_back: int = 1,
        max_articles: int = 20
    ) -> Dict:
        """
        处理每日新闻
        
        Args:
            keywords: 搜索关键词，None使用默认财经词
            days_back: 往前查几天
            max_articles: 最大文章数
            
        Returns:
            处理结果字典
        """
        # 时间范围
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)
        
        # 获取新闻
        articles = self.fetcher.fetch_financial_news(
            keywords=keywords,
            from_date=from_date,
            to_date=to_date,
            page_size=max_articles
        )
        
        if not articles:
            return {
                'status': 'no_data',
                'message': '未获取到新闻数据',
                'articles': [],
                'sentiment_summary': {}
            }
        
        # 情感分析
        analyzed_articles = []
        for article in articles:
            # 分析标题+描述的情感
            text = f"{article.title} {article.description or ''}"
            sentiment = self.analyzer.analyze(text)
            
            article.sentiment = sentiment.sentiment
            article.sentiment_score = sentiment.score
            
            analyzed_articles.append({
                'title': article.title,
                'source': article.source,
                'url': article.url,
                'published_at': article.published_at.strftime('%Y-%m-%d %H:%M'),
                'sentiment': sentiment.sentiment,
                'sentiment_score': round(sentiment.score, 3),
                'confidence': round(sentiment.confidence, 2)
            })
        
        # 生成情感摘要
        sentiment_summary = self._generate_sentiment_summary(analyzed_articles)
        
        # 提取热门主题
        hot_topics = self._extract_topics(articles)
        
        return {
            'status': 'success',
            'date': to_date.strftime('%Y-%m-%d'),
            'total_articles': len(analyzed_articles),
            'articles': analyzed_articles,
            'sentiment_summary': sentiment_summary,
            'hot_topics': hot_topics
        }
    
    def _generate_sentiment_summary(self, articles: List[Dict]) -> Dict:
        """生成情感摘要"""
        if not articles:
            return {}
        
        scores = [a['sentiment_score'] for a in articles]
        sentiments = [a['sentiment'] for a in articles]
        
        # 统计
        counter = Counter(sentiments)
        avg_score = sum(scores) / len(scores)
        
        # 确定总体情感
        if avg_score >= 0.1:
            overall = 'positive'
            mood = '乐观'
        elif avg_score <= -0.1:
            overall = 'negative'
            mood = '悲观'
        else:
            overall = 'neutral'
            mood = '中性'
        
        # 找最正面和最负面的文章
        sorted_by_score = sorted(articles, key=lambda x: x['sentiment_score'], reverse=True)
        most_positive = sorted_by_score[0] if sorted_by_score else None
        most_negative = sorted_by_score[-1] if sorted_by_score else None
        
        return {
            'overall_sentiment': overall,
            'mood': mood,
            'average_score': round(avg_score, 3),
            'distribution': dict(counter),
            'positive_ratio': round(counter.get('positive', 0) / len(articles) * 100, 1),
            'negative_ratio': round(counter.get('negative', 0) / len(articles) * 100, 1),
            'most_positive_article': most_positive,
            'most_negative_article': most_negative
        }
    
    def _extract_topics(self, articles: List[NewsArticle], top_n: int = 5) -> List[Dict]:
        """提取热门主题 (简单关键词统计)"""
        # 财经关键词池
        topic_keywords = {
            'AI/科技': ['AI', 'artificial intelligence', 'tech', 'technology', 'chip', '半导体'],
            '美联储/利率': ['Fed', 'Federal Reserve', 'interest rate', ' Powell', '加息', '降息'],
            '美股': ['S&P 500', 'Nasdaq', 'Dow', 'stock market', '华尔街'],
            '加密货币': ['Bitcoin', 'BTC', 'crypto', 'blockchain', '加密货币'],
            '中概股': ['China', 'Chinese', '中概', '港股'],
            '能源': ['oil', 'energy', 'gas', '石油', '能源'],
            '房地产': ['real estate', 'housing', 'property', '房地产'],
            '地缘风险': ['war', 'conflict', 'geopolitical', '制裁', '冲突']
        }
        
        topic_counts = {topic: 0 for topic in topic_keywords}
        
        for article in articles:
            text = f"{article.title} {article.description or ''}".lower()
            for topic, keywords in topic_keywords.items():
                if any(kw.lower() in text for kw in keywords):
                    topic_counts[topic] += 1
        
        # 排序返回
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [
            {'topic': topic, 'count': count}
            for topic, count in sorted_topics[:top_n] if count > 0
        ]
    
    def print_report(self, result: Dict):
        """打印新闻报告"""
        if result['status'] != 'success':
            print(f"❌ {result['message']}")
            return
        
        print("\n" + "="*60)
        print(f"📰 每日新闻摘要 - {result['date']}")
        print("="*60)
        
        summary = result['sentiment_summary']
        print(f"\n🎭 市场情绪: {summary['mood']} (平均分: {summary['average_score']:+.3f})")
        print(f"📊 情感分布:")
        print(f"   正面: {summary['positive_ratio']}%")
        print(f"   负面: {summary['negative_ratio']}%")
        print(f"   中性: {100 - summary['positive_ratio'] - summary['negative_ratio']:.1f}%")
        
        # 热门主题
        if result['hot_topics']:
            print(f"\n🔥 热门主题:")
            for topic in result['hot_topics'][:5]:
                print(f"   • {topic['topic']}: {topic['count']}篇")
        
        # 典型文章
        if summary.get('most_positive_article'):
            pos = summary['most_positive_article']
            print(f"\n📈 最正面新闻 ({pos['sentiment_score']:+.3f}):")
            print(f"   {pos['title'][:60]}...")
            print(f"   来源: {pos['source']}")
        
        if summary.get('most_negative_article'):
            neg = summary['most_negative_article']
            print(f"\n📉 最负面新闻 ({neg['sentiment_score']:+.3f}):")
            print(f"   {neg['title'][:60]}...")
            print(f"   来源: {neg['source']}")
        
        print(f"\n📄 共分析 {result['total_articles']} 条新闻")
        print("="*60)


# 命令行入口
if __name__ == "__main__":
    print("🚀 新闻处理器测试")
    print("="*60)
    
    # 使用demo key (功能受限)
    processor = NewsProcessor(news_api_key="demo")
    
    print("\n[提示] 使用真实NewsAPI Key可获取更多数据")
    print("申请地址: https://newsapi.org/register (免费100次/天)\n")
    
    # 处理今日新闻
    result = processor.process_daily_news(days_back=1, max_articles=10)
    processor.print_report(result)
