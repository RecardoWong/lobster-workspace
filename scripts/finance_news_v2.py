#!/usr/bin/env python3
"""
财经新闻聚合器 - 多源 + 数据中心专题
"""

import urllib.request
import json
import re
from datetime import datetime
import random

def fetch_with_timeout(url, headers, timeout=8):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode('utf-8')
    except:
        return None

def fetch_sina():
    """新浪财经 - 美股/财经"""
    try:
        url = 'https://feed.sina.com.cn/api/roll/get?pageid=153&lid=2516&num=10'
        data = fetch_with_timeout(url, {'User-Agent': 'Mozilla/5.0'})
        if data:
            parsed = json.loads(data)
            items = []
            if 'result' in parsed and 'data' in parsed['result']:
                for item in parsed['result']['data'][:4]:
                    items.append({
                        'title': item.get('title', ''),
                        'source': '新浪财经',
                        'url': item.get('url', ''),
                        'time': '刚刚',
                        'tag': '财经',
                        'tagColor': '#ef4444'
                    })
            return items
    except:
        pass
    return []

def fetch_36kr():
    """36氪 - 科技/AI/数据中心"""
    try:
        url = 'https://36kr.com/api/newsflash/catalog'
        data = fetch_with_timeout(url, {'User-Agent': 'Mozilla/5.0'})
        if data:
            parsed = json.loads(data)
            items = []
            if parsed.get('data') and parsed['data'].get('newsflashList'):
                for item in parsed['data']['newsflashList'][:4]:
                    title = item.get('title', '')
                    # 优先数据中心关键词
                    dc_keywords = ['数据中心', 'IDC', '算力', '服务器', 'AI', '人工智能', '云计算', 'GPU']
                    is_dc = any(kw in title for kw in dc_keywords)
                    
                    items.append({
                        'title': title,
                        'source': '36氪',
                        'url': f"https://36kr.com/newsflashes/{item.get('id', '')}",
                        'time': '刚刚',
                        'tag': '数据中心' if is_dc else '科技',
                        'tagColor': '#8b5cf6' if is_dc else '#f59e0b'
                    })
            return items
    except:
        pass
    return []

def fetch_wallstreet():
    """华尔街见闻"""
    try:
        url = 'https://api.wallstcn.com/apiv1/content/articles?page=1&limit=10'
        data = fetch_with_timeout(url, {'User-Agent': 'Mozilla/5.0'})
        if data:
            parsed = json.loads(data)
            items = []
            if parsed.get('data') and parsed['data'].get('items'):
                for item in parsed['data']['items'][:3]:
                    title = item.get('title', '')
                    dc_keywords = ['数据', '算力', 'AI', '数据中心', 'IDC', '云计算', '服务器']
                    is_dc = any(kw in title for kw in dc_keywords)
                    
                    items.append({
                        'title': title,
                        'source': '华尔街见闻',
                        'url': f"https://wallstreetcn.com/articles/{item.get('id', '')}",
                        'time': '刚刚',
                        'tag': '数据中心' if is_dc else '全球',
                        'tagColor': '#8b5cf6' if is_dc else '#10b981'
                    })
            return items
    except:
        pass
    return []

def aggregate():
    print(f'🚀 抓取新闻... {datetime.now().strftime("%H:%M")}')
    
    # 并行获取
    sina = fetch_sina()
    kr36 = fetch_36kr()
    wscn = fetch_wallstreet()
    
    # 合并 - 数据中心优先
    all_news = kr36 + wscn + sina  # 科技/数据中心新闻放前面
    
    # 去重
    seen = set()
    unique = []
    dc_count = 0
    for news in all_news:
        key = news['title'][:25]
        if key not in seen:
            seen.add(key)
            unique.append(news)
            if news['tag'] in ['数据中心', '算力', 'IDC']:
                dc_count += 1
    
    # 过滤：只保留有真实URL链接的新闻（没有链接=假新闻）
    valid_news = []
    for news in unique:
        url = news.get('url', '')
        # 必须是非空的、不是#占位符的、以http开头的真实链接
        if url and url != '#' and url.startswith('http'):
            valid_news.append(news)
        else:
            print(f'⚠️ 过滤掉无来源的新闻: {news.get("title", "")[:30]}...')
    
    final_news = valid_news[:12]
    
    output = {
        'update_time': datetime.now().isoformat(),
        'source_count': 3,
        'total_count': len(final_news),
        'news': final_news
    }
    
    import os
    os.makedirs('/root/.openclaw/workspace/lobster-workspace/dashboard/data', exist_ok=True)
    
    with open('/root/.openclaw/workspace/lobster-workspace/dashboard/data/finance_news.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f'✅ 更新 {len(final_news)} 条 (数据中心: {dc_count} 条)')
    return final_news

if __name__ == '__main__':
    aggregate()
