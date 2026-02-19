#!/usr/bin/env python3
"""
财经新闻聚合器 - 包含数据中心/算力/IDC专题
"""

import urllib.request
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
            url = 'https://feed.sina.com.cn/api/roll/get?pageid=153&lid=2516&num=15'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
                news_items = []
                if 'result' in data and 'data' in data['result']:
                    for item in data['result']['data'][:6]:
                        news_items.append({
                            'title': item.get('title', ''),
                            'source': '新浪财经',
                            'url': item.get('url', ''),
                            'time': '刚刚',
                            'tag': '财经',
                            'tagColor': '#ef4444'
                        })
                print(f'✅ 新浪财经: {len(news_items)} 条')
                return news_items
        except Exception as e:
            print(f'❌ 新浪财经: {e}')
            return []
    
    def fetch_36kr(self):
        """36氪 - 科技/数据中心"""
        try:
            url = 'https://36kr.com/api/newsflash/catalog'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
                news_items = []
                if data.get('data') and data['data'].get('newsflashList'):
                    for item in data['data']['newsflashList'][:4]:
                        title = item.get('title', '')
                        # 优先选择数据中心相关新闻
                        keywords = ['数据中心', 'IDC', '算力', '服务器', 'AI', '人工智能', '云计算', 'GPU']
                        is_dc_related = any(kw in title for kw in keywords)
                        
                        news_items.append({
                            'title': title,
                            'source': '36氪',
                            'url': f"https://36kr.com/newsflashes/{item.get('id', '')}",
                            'time': '刚刚',
                            'tag': '数据中心' if is_dc_related else '科技',
                            'tagColor': '#8b5cf6' if is_dc_related else '#f59e0b'
                        })
                print(f'✅ 36氪: {len(news_items)} 条')
                return news_items
        except Exception as e:
            print(f'❌ 36氪: {e}')
            return []
    
    def fetch_wallstreet(self):
        """华尔街见闻"""
        try:
            url = 'https://api.wallstcn.com/apiv1/content/articles?page=1&limit=15'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
                news_items = []
                if data.get('data') and data['data'].get('items'):
                    for item in data['data']['items'][:4]:
                        title = item.get('title', '')
                        # 检查是否数据中心相关
                        keywords = ['数据', '算力', 'AI', '数据中心', 'IDC', '云计算', '服务器']
                        is_dc_related = any(kw in title for kw in keywords)
                        
                        news_items.append({
                            'title': title,
                            'source': '华尔街见闻',
                            'url': f"https://wallstreetcn.com/articles/{item.get('id', '')}",
                            'time': '刚刚',
                            'tag': '数据中心' if is_dc_related else '全球',
                            'tagColor': '#8b5cf6' if is_dc_related else '#10b981'
                        })
                print(f'✅ 华尔街见闻: {len(news_items)} 条')
                return news_items
        except Exception as e:
            print(f'❌ 华尔街见闻: {e}')
            return []
    
    def fetch_itnews(self):
        """IT之家 - 数据中心/科技"""
        try:
            url = 'https://api.ithome.com/json/newslist/news?r=0'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
                news_items = []
                if data.get('newslist'):
                    count = 0
                    for item in data['newslist']:
                        if count >= 4:
                            break
                        title = item.get('title', '')
                        # 只选择数据中心/科技相关
                        keywords = ['数据', '算力', '服务器', 'IDC', 'AI', '云计算', 'GPU', '芯片']
                        if any(kw in title for kw in keywords):
                            news_items.append({
                                'title': title,
                                'source': 'IT之家',
                                'url': item.get('url', ''),
                                'time': '刚刚',
                                'tag': '数据中心',
                                'tagColor': '#8b5cf6'
                            })
                            count += 1
                print(f'✅ IT之家: {len(news_items)} 条')
                return news_items
        except Exception as e:
            print(f'❌ IT之家: {e}')
            return []
    
    def aggregate(self):
        print(f'\n🚀 抓取财经新闻... {datetime.now().strftime("%Y-%m-%d %H:%M")}')
        print('=' * 60)
        
        sina_news = self.fetch_sina()
        kr36_news = self.fetch_36kr()
        wallstreet_news = self.fetch_wallstreet()
        itnews = self.fetch_itnews()
        
        # 合并，去重
        all_news = itnews + kr36_news + wallstreet_news + sina_news
        
        seen = set()
        unique_news = []
        dc_count = 0
        
        for news in all_news:
            key = news['title'][:30]
            if key not in seen:
                seen.add(key)
                unique_news.append(news)
                if news['tag'] == '数据中心':
                    dc_count += 1
        
        self.news_list = unique_news[:15]  # 最多15条
        
        print(f'\n📊 总计: {len(self.news_list)} 条 (数据中心: {dc_count} 条)')
        return self.news_list
    
    def save(self):
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
        
        print(f'💾 已保存: {self.output_file}')
        return self.output_file

def main():
    aggregator = NewsAggregator()
    aggregator.aggregate()
    aggregator.save()
    print('\n✅ 完成!')

if __name__ == '__main__':
    main()
