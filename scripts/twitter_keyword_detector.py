#!/usr/bin/env python3
"""
Twitter 关键词检测与标记
自动检测推文中是否包含关注的关键词
"""
import json
import re
from datetime import datetime

# 加载关键词配置
with open('/root/.openclaw/workspace/config/twitter_keywords.json', 'r') as f:
    config = json.load(f)

KEYWORDS = {k['word'].lower(): k for k in config['keywords']}

def detect_keywords(text):
    """检测推文中的关键词"""
    if not text:
        return []
    
    text_lower = text.lower()
    matches = []
    
    for keyword, info in KEYWORDS.items():
        # 使用单词边界匹配
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, text_lower):
            matches.append({
                'word': info['word'],
                'priority': info['priority'],
                'category': info['category']
            })
    
    # 按优先级排序
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    matches.sort(key=lambda x: priority_order.get(x['priority'], 3))
    
    return matches

def process_tweets():
    """处理推文并标记关键词"""
    # 读取最新推文
    with open('/root/.openclaw/workspace/reports/twitter_undetected_latest.json', 'r') as f:
        tweets = json.load(f)
    
    high_priority_count = 0
    
    for tweet in tweets:
        text = tweet.get('text', '')
        matches = detect_keywords(text)
        
        if matches:
            tweet['keywords_detected'] = matches
            tweet['has_keywords'] = True
            
            # 检查是否有高优先级关键词
            if any(m['priority'] == 'high' for m in matches):
                tweet['alert'] = True
                high_priority_count += 1
        else:
            tweet['has_keywords'] = False
    
    # 保存处理后的推文
    with open('/root/.openclaw/workspace/reports/twitter_undetected_latest.json', 'w', encoding='utf-8') as f:
        json.dump(tweets, f, ensure_ascii=False, indent=2)
    
    # 生成关键词统计
    summary = {
        'last_update': datetime.now().isoformat(),
        'total_tweets': len(tweets),
        'tweets_with_keywords': sum(1 for t in tweets if t.get('has_keywords')),
        'high_priority_alerts': high_priority_count,
        'keywords_found': []
    }
    
    # 统计关键词出现次数
    keyword_counts = {}
    for tweet in tweets:
        for match in tweet.get('keywords_detected', []):
            word = match['word']
            keyword_counts[word] = keyword_counts.get(word, 0) + 1
    
    summary['keywords_found'] = [
        {'word': k, 'count': v} 
        for k, v in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
    ]
    
    with open('/root/.openclaw/workspace/reports/twitter_keywords_summary.json', 'w') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 关键词检测完成")
    print(f"   总推文: {summary['total_tweets']}")
    print(f"   含关键词: {summary['tweets_with_keywords']}")
    print(f"   高优先级: {summary['high_priority_alerts']}")
    if summary['keywords_found']:
        top_keywords = summary['keywords_found'][:5]
        kw_str = ', '.join([f"{k['word']}({k['count']})" for k in top_keywords])
        print(f"   检测到: {kw_str}")

if __name__ == '__main__':
    process_tweets()
