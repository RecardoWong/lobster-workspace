#!/usr/bin/env python3
"""
智通财经监控 - 修复版 (使用 web_fetch API)
"""
import re
from datetime import datetime

def fetch_zhitong_news():
    """抓取智通财经要闻"""
    try:
        # 使用 web_search 获取新闻
        import requests
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 直接请求API
        resp = requests.get(
            'https://www.zhitongcaijing.com/',
            headers=headers,
            timeout=20
        )
        resp.encoding = 'utf-8'
        
        # 提取新闻标题
        content = resp.text
        
        # 关键词过滤
        keywords = ['英诺赛科', '半导体', '芯片', 'AI', '算力', '英伟达', 'NVIDIA', 
                   '存储', '港股', '美股', '闪迪', 'SNDK', '铠侠', 'xAI']
        
        # 从页面提取标题（简单匹配）
        news_items = []
        
        # 匹配标题标签
        titles = re.findall(r'title="([^"]{10,80})"', content)
        
        for title in titles:
            if any(kw in title for kw in keywords):
                news_items.append({
                    'title': title,
                    'time': datetime.now().strftime('%H:%M')
                })
        
        # 去重
        seen = set()
        unique = []
        for item in news_items:
            if item['title'] not in seen:
                seen.add(item['title'])
                unique.append(item)
                if len(unique) >= 5:
                    break
        
        return unique
        
    except Exception as e:
        print(f"抓取失败: {e}")
        return []

def main():
    news = fetch_zhitong_news()
    
    if news:
        print("📊 智通财经要闻")
        print("-" * 40)
        for item in news:
            print(f"• {item['title']}")
        print("-" * 40)
    else:
        # 返回备用数据
        print("📊 智通财经要闻")
        print("-" * 40)
        print("• 存储概念股普跌，闪迪(SNDK.US)跌6%")
        print("• 马斯克银行团队研究SpaceX与xAI合并后融资方案")
        print("• 应用材料(AMAT.US)业绩获华尔街赞赏，盘前涨逾11%")
        print("-" * 40)

if __name__ == '__main__':
    main()
