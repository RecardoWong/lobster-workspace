#!/usr/bin/env python3
"""
财经新闻聚合器 - 多源
整合：新浪财经、东方财富、财联社、华尔街见闻
"""

import requests
import json
import re
from datetime import datetime

class NewsAggregator:
    def __init__(self):
        self.output_file = '/root/.openclaw/workspace/lobster-workspace/dashboard/data/finance_news.json'
        self.news_list = []
        
    def fetch_sina(self):
        """新浪财经"""
        try:
            url = 'https://feed.sina.com.cn/api/roll/get?pageid=153&lid=2516&num=10'
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            data = response.json()
            
            news_items = []
            if 'result' in data and 'data' in data['result']:
                for item in data['result']['data'][:5]:
                    news_items.append({
                        'title': item.get('title', ''),
                        'source': '新浪财经',
                        'url': item.get('url', ''),
                        'time': '刚刚',
                        'tag': '美股',
                        'tagColor': '#ef4444'
                    })
            print(f'✅ 新浪财经: {len(news_items)} 条')
            return news_items
        except Exception as e:
            print(f'❌ 新浪财经: {str(e)[:50]}')
            return []
    
    def fetch_eastmoney(self):
        """东方财富"""
        try:
            url = 'https://np-anotice-stock.eastmoney.com/api/security/ann?page_size=20&page_index=1'
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            data = response.json()
            
            news_items = []
            if data.get('data') and data['data'].get('list'):
                for item in data['data']['list'][:3]:
                    news_items.append({
                        'title': item.get('announcement_title', ''),
                        'source': '东方财富',
                        'url': f"https://data.eastmoney.com/notices/detail/{item.get('codes', '')}/{item.get('notice_id', '')}.html",
                        'time': '刚刚',
                        'tag': 'A股',
                        'tagColor': '#10b981'
                    })
            print(f'✅ 东方财富: {len(news_items)} 条')
            return news_items
        except Exception as e:
            print(f'❌ 东方财富: {str(e)[:50]}')
            return []
    
    def fetch_wallstreet(self):
        """华尔街见闻"""
        try:
            url = 'https://api.wallstcn.com/apiv1/content/articles?page=1&limit=10'
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            data = response.json()
            
            news_items = []
            if data.get('data') and data['data'].get('items'):
                for item in data['data']['items'][:3]:
                    news_items.append({
                        'title': item.get('title', ''),
                        'source': '华尔街见闻',
                        'url': f"https://wallstreetcn.com/articles/{item.get('id', '')}",
                        'time': '刚刚',
                        'tag': '全球',
                        'tagColor': '#8b5cf6'
                    })
            print(f'✅ 华尔街见闻: {len(news_items)} 条')
            return news_items
        except Exception as e:
            print(f'❌ 华尔街见闻: {str(e)[:50]}')
            return []
    
    def fetch_36kr(self):
        """36氪 - 科技财经"""
        try:
            url = 'https://36kr.com/api/newsflash/catalog'
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            data = response.json()
            
            news_items = []
            if data.get('data') and data['data'].get('newsflashList'):
                for item in data['data']['newsflashList'][:3]:
                    news_items.append({
                        'title': item.get('title', ''),
                        'source': '36氪',
                        'url': f"https://36kr.com/newsflashes/{item.get('id', '')}",
                        'time': '刚刚',
                        'tag': '科技',
                        'tagColor': '#f59e0b'
                    })
            print(f'✅ 36氪: {len(news_items)} 条')
            return news_items
        except Exception as e:
            print(f'❌ 36氪: {str(e)[:50]}')
            return []
    
    def aggregate(self):
        """聚合所有新闻"""
        print(f'\n🚀 开始抓取财经新闻... {datetime.now().strftime("%Y-%m-%d %H:%M")}')
        print('=' * 60)
        
        # 获取各源新闻
        sina_news = self.fetch_sina()
        eastmoney_news = self.fetch_eastmoney()
        wallstreet_news = self.fetch_wallstreet()
        kr36_news = self.fetch_36kr()
        
        # 合并
        all_news = sina_news + eastmoney_news + wallstreet_news + kr36_news
        
        # 去重
        seen = set()
        unique_news = []
        for news in all_news:
            key = news['title'][:30]
            if key not in seen:
                seen.add(key)
                unique_news.append(news)
        
        self.news_list = unique_news[:12]  # 最多12条
        
        print(f'\n📊 总计: {len(self.news_list)} 条不重复新闻')
        return self.news_list
    
    def save(self):
        """保存为JSON"""
        output = {
            'update_time': datetime.now().isoformat(),
            'source_count': 4,
            'total_count': len(self.news_list),
            'news': self.news_list
        }
        
        import os
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f'\n💾 已保存: {self.output_file}')
        return self.output_file

def main():
    aggregator = NewsAggregator()
    aggregator.aggregate()
    aggregator.save()
    print('\n✅ 财经新闻聚合完成!')

if __name__ == '__main__':
    main()
