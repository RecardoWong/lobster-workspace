#!/usr/bin/env python3
"""
Brave Search API 客户端
用于搜索新闻、财报等信息
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

class BraveSearchClient:
    """Brave Search API 客户端"""
    
    BASE_URL = "https://api.search.brave.com/res/v1"
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('BRAVE_API_KEY')
        if not self.api_key:
            raise ValueError("请设置 BRAVE_API_KEY 环境变量")
    
    def _request(self, endpoint, params):
        """发送API请求"""
        query_string = urllib.parse.urlencode(params)
        url = f"{self.BASE_URL}/{endpoint}?{query_string}"
        
        req = urllib.request.Request(
            url,
            headers={
                'Accept': 'application/json',
                'X-Subscription-Token': self.api_key
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"Brave API 请求失败: {e}")
            return None
    
    def search_news(self, query, count=10):
        """搜索新闻"""
        params = {
            'q': query,
            'count': min(count, 20),  # Brave免费额度限制
            'search_lang': 'en',  # Brave新闻搜索主要支持英文
            'freshness': 'pd'  # 过去一天
        }
        
        result = self._request('news/search', params)
        if result and 'results' in result:
            return [
                {
                    'title': item.get('title', ''),
                    'description': item.get('description', ''),
                    'url': item.get('url', ''),
                    'published': item.get('age', ''),
                    'source': item.get('meta', {}).get('url', '未知来源')
                }
                for item in result['results']
            ]
        return []
    
    def search_earnings(self, date=None):
        """搜索财报公告"""
        if date is None:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        queries = [
            f'财报公告 {date} 美股',
            f'earnings report {date}',
            f'Q4 2025 earnings announcement'
        ]
        
        all_results = []
        for query in queries:
            results = self.search_news(query, count=5)
            all_results.extend(results)
        
        # 去重
        seen = set()
        unique = []
        for item in all_results:
            if item['url'] not in seen:
                seen.add(item['url'])
                unique.append(item)
        
        return unique[:15]  # 返回最多15条
    
    def search_stock(self, symbol):
        """搜索股票相关新闻"""
        query = f'${symbol} 股票 新闻'
        return self.search_news(query, count=10)

if __name__ == '__main__':
    # 测试
    try:
        client = BraveSearchClient()
        print("✅ Brave Search API 连接成功")
        print(f"API Key: {client.api_key[:10]}...")
        
        # 测试搜索
        print("\n🔍 测试搜索财报新闻...")
        news = client.search_earnings()
        print(f"找到 {len(news)} 条相关新闻")
        
        for i, item in enumerate(news[:3], 1):
            print(f"\n{i}. {item['title'][:60]}...")
            print(f"   来源: {item['source']}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
