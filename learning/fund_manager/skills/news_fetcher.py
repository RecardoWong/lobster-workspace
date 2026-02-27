#!/usr/bin/env python3
"""
财经新闻获取器 - 基于NewsAPI
免费额度: 100次/天
"""

import requests
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import time

@dataclass
class NewsArticle:
    """新闻文章数据结构"""
    title: str
    description: str
    content: str
    url: str
    source: str
    published_at: datetime
    author: Optional[str] = None
    
    # 情感分析结果 (后续填充)
    sentiment: str = ""  # positive/negative/neutral
    sentiment_score: float = 0.0  # -1到1
    
    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'description': self.description,
            'content': self.content[:500] if self.content else '',  # 截断
            'url': self.url,
            'source': self.source,
            'published_at': self.published_at.isoformat(),
            'sentiment': self.sentiment,
            'sentiment_score': self.sentiment_score
        }


class NewsFetcher:
    """新闻获取器"""
    
    # NewsAPI 免费版限制: 100次/天
    BASE_URL = "https://newsapi.org/v2"
    
    # 默认财经关键词
    DEFAULT_KEYWORDS = [
        "stock market", "finance", "economy", "Federal Reserve", 
        "earnings", "investment", "trading"
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化
        
        Args:
            api_key: NewsAPI Key (免费申请: https://newsapi.org/)
                    如果没有，尝试从环境变量读取，否则使用 demo key (功能受限)
        """
        import os
        self.api_key = api_key or os.getenv('NEWSAPI_KEY', 'demo')
        self._request_count = 0
        self._max_requests = 100  # 免费版限制
    
    def fetch_financial_news(
        self, 
        keywords: Optional[List[str]] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page_size: int = 20,
        language: str = "en"
    ) -> List[NewsArticle]:
        """
        获取财经新闻
        
        Args:
            keywords: 关键词列表，默认使用财经通用词
            from_date: 起始日期
            to_date: 结束日期
            page_size: 每页数量 (最大100)
            language: 语言 (en/zh等)
            
        Returns:
            NewsArticle列表
        """
        if self._request_count >= self._max_requests:
            print("[警告] 已达到NewsAPI免费版每日限制(100次)")
            return []
        
        try:
            # 构建查询
            if keywords:
                query = " OR ".join(f'"{k}"' for k in keywords)
            else:
                query = " OR ".join(f'"{k}"' for k in self.DEFAULT_KEYWORDS)
            
            # 日期参数
            params = {
                'q': query,
                'language': language,
                'sortBy': 'publishedAt',  # 按时间排序
                'pageSize': min(page_size, 100),
                'apiKey': self.api_key
            }
            
            if from_date:
                params['from'] = from_date.strftime('%Y-%m-%d')
            if to_date:
                params['to'] = to_date.strftime('%Y-%m-%d')
            
            # 调用API
            url = f"{self.BASE_URL}/everything"
            response = requests.get(url, params=params, timeout=15)
            self._request_count += 1
            
            if response.status_code != 200:
                print(f"[错误] NewsAPI请求失败: {response.status_code}")
                print(f"响应: {response.text[:200]}")
                return []
            
            data = response.json()
            
            if data.get('status') != 'ok':
                print(f"[错误] NewsAPI返回错误: {data.get('message')}")
                return []
            
            articles = data.get('articles', [])
            print(f"[新闻获取] 获取到 {len(articles)} 条新闻")
            
            # 转换为NewsArticle对象
            result = []
            for article in articles:
                try:
                    # 解析日期
                    published_str = article.get('publishedAt', '')
                    if published_str:
                        published_at = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
                    else:
                        published_at = datetime.now()
                    
                    news = NewsArticle(
                        title=article.get('title', ''),
                        description=article.get('description', ''),
                        content=article.get('content', ''),
                        url=article.get('url', ''),
                        source=article.get('source', {}).get('name', 'Unknown'),
                        published_at=published_at,
                        author=article.get('author')
                    )
                    result.append(news)
                    
                except Exception as e:
                    print(f"[警告] 解析新闻失败: {e}")
                    continue
            
            return result
            
        except Exception as e:
            print(f"[错误] 获取新闻失败: {e}")
            return []
    
    def fetch_headlines(
        self,
        category: str = "business",
        country: str = "us",
        page_size: int = 20
    ) -> List[NewsArticle]:
        """
        获取头条新闻 (不需要搜索词)
        
        Args:
            category: 类别 (business/technology/etc)
            country: 国家代码 (us/gb/cn等)
            page_size: 数量
        """
        if self._request_count >= self._max_requests:
            print("[警告] 已达到NewsAPI免费版每日限制(100次)")
            return []
        
        try:
            params = {
                'category': category,
                'country': country,
                'pageSize': min(page_size, 100),
                'apiKey': self.api_key
            }
            
            url = f"{self.BASE_URL}/top-headlines"
            response = requests.get(url, params=params, timeout=15)
            self._request_count += 1
            
            if response.status_code != 200:
                print(f"[错误] NewsAPI请求失败: {response.status_code}")
                return []
            
            data = response.json()
            articles = data.get('articles', [])
            print(f"[头条新闻] 获取到 {len(articles)} 条")
            
            result = []
            for article in articles:
                try:
                    published_str = article.get('publishedAt', '')
                    published_at = datetime.fromisoformat(published_str.replace('Z', '+00:00')) if published_str else datetime.now()
                    
                    news = NewsArticle(
                        title=article.get('title', ''),
                        description=article.get('description', ''),
                        content=article.get('content', ''),
                        url=article.get('url', ''),
                        source=article.get('source', {}).get('name', 'Unknown'),
                        published_at=published_at,
                        author=article.get('author')
                    )
                    result.append(news)
                except:
                    continue
            
            return result
            
        except Exception as e:
            print(f"[错误] 获取头条失败: {e}")
            return []


# 测试运行
if __name__ == "__main__":
    print("NewsAPI测试 (使用demo key，功能受限)")
    print("="*50)
    
    fetcher = NewsFetcher(api_key="demo")
    
    # 测试头条新闻
    headlines = fetcher.fetch_headlines(category="business", page_size=5)
    
    print(f"\n获取到 {len(headlines)} 条商业头条:")
    for i, news in enumerate(headlines[:3], 1):
        print(f"\n{i}. {news.title}")
        print(f"   来源: {news.source}")
        print(f"   时间: {news.published_at.strftime('%Y-%m-%d %H:%M')}")
    
    print(f"\n[提示] 使用真实API Key可获取更多数据")
    print("申请地址: https://newsapi.org/register")
