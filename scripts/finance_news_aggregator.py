#!/usr/bin/env python3
"""
财经新闻聚合器
整合：智通财经、新浪财经、财联社
"""

import requests
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

class NewsAggregator:
    def __init__(self):
        self.output_file = '/root/.openclaw/workspace/lobster-workspace/dashboard/data/finance_news.json'
        self.news_list = []
        
    def fetch_zhitong(self):
        """获取智通财经新闻"""
        try:
            url = 'https://www.zhitongcaijing.com/content/recommend.html'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            # 提取新闻
            news_items = []
            # 简单正则提取标题和链接
            pattern = r'<a[^>]*href="([^"]*\/detail\/[^"]*)"[^>]*>\s*<[^>]*>\s*([^<]{10,})'
            matches = re.findall(pattern, response.text)
            
            for i, (link, title) in enumerate(matches[:5]):
                if 'zhitongcaijing.com' not in link:
                    link = 'https://www.zhitongcaijing.com' + link
                news_items.append({
                    'title': title.strip(),
                    'source': '智通财经',
                    'url': link,
                    'time': f'{i+1}小时前',
                    'tag': '港股',
                    'tagColor': '#3b82f6'
                })
            
            print(f'✅ 智通财经: {len(news_items)} 条')
            return news_items
        except Exception as e:
            print(f'❌ 智通财经获取失败: {str(e)[:50]}')
            return []
    
    def fetch_sina_finance(self):
        """获取新浪财经新闻"""
        try:
            # 新浪财经API
            url = 'https://feed.sina.com.cn/api/roll/get?pageid=153&lid=2516&k=&num=10&page=1&r=0.5'
            response = requests.get(url, timeout=10)
            data = response.json()
            
            news_items = []
            if 'result' in data and 'data' in data['result']:
                for item in data['result']['data'][:5]:
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
            print(f'❌ 新浪财经获取失败: {str(e)[:50]}')
            return []
    
    def fetch_cls(self):
        """获取财联社新闻"""
        try:
            # 财联社滚动新闻
            url = 'https://www.cls.cn/api/roll/get'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.cls.cn/'
            }
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            
            news_items = []
            if data.get('code') == 200 and 'data' in data:
                for item in data['data'][:5]:
                    news_items.append({
                        'title': item.get('title', ''),
                        'source': '财联社',
                        'url': f"https://www.cls.cn/detail/{item.get('id', '')}",
                        'time': '刚刚',
                        'tag': '快讯',
                        'tagColor': '#10b981'
                    })
            
            print(f'✅ 财联社: {len(news_items)} 条')
            return news_items
        except Exception as e:
            print(f'❌ 财联社获取失败: {str(e)[:50]}')
            return []
    
    def aggregate(self):
        """聚合所有新闻"""
        print(f'\n🚀 开始抓取财经新闻... {datetime.now().strftime("%Y-%m-%d %H:%M")}')
        print('=' * 60)
        
        # 获取各源新闻
        zhitong_news = self.fetch_zhitong()
        sina_news = self.fetch_sina_finance()
        cls_news = self.fetch_cls()
        
        # 合并并去重
        all_news = []
        seen_titles = set()
        
        for news in zhitong_news + sina_news + cls_news:
            title_key = news['title'][:20]  # 前20字作为去重key
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                all_news.append(news)
        
        # 取前10条
        self.news_list = all_news[:10]
        
        print(f'\n📊 总计: {len(self.news_list)} 条不重复新闻')
        return self.news_list
    
    def save(self):
        """保存为JSON"""
        output = {
            'update_time': datetime.now().isoformat(),
            'source_count': 3,
            'total_count': len(self.news_list),
            'news': self.news_list
        }
        
        # 确保目录存在
        Path(self.output_file).parent.mkdir(parents=True, exist_ok=True)
        
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
