#!/usr/bin/env python3
"""
Twitter 每日总结
每天早上8点推送昨天所有推文的总结
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

SAVE_DIR = '/tmp/twitter_monitor'

def get_yesterday_tweets():
    """获取昨天的所有推文"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    daily_file = f"{SAVE_DIR}/daily_{yesterday}.json"
    
    if not os.path.exists(daily_file):
        return []
    
    with open(daily_file, 'r') as f:
        return json.load(f)

def summarize_tweets(tweets):
    """总结推文内容"""
    if not tweets:
        return None
    
    # 按作者分组
    by_author = {}
    for t in tweets:
        author = t.get('author', 'unknown')
        if author not in by_author:
            by_author[author] = []
        by_author[author].append(t)
    
    lines = [
        "📊 Twitter 昨日总结",
        f"📅 {(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')}",
        f"📈 共 {len(tweets)} 条推文",
        "=" * 40,
        ""
    ]
    
    for author, author_tweets in by_author.items():
        name = author_tweets[0].get('name', author)
        lines.extend([
            f"👤 {name} (@{author}) - {len(author_tweets)}条",
            ""
        ])
        
        for i, t in enumerate(author_tweets[:3], 1):  # 每人最多3条
            text = t.get('text', '')[:100]
            lines.append(f"  {i}. {text}...")
        
        lines.append("")
    
    # 简单趋势判断
    total = len(tweets)
    if total > 20:
        lines.append("🔥 昨日推文旅密度高，市场可能有重要事件")
    elif total > 10:
        lines.append("📢 昨日推文旅密度中等，关注相关动态")
    else:
        lines.append("📌 昨日推文旅密度较低，市场相对平静")
    
    lines.extend([
        "",
        "=" * 40,
        "💡 建议关注今日美股开盘情况"
    ])
    
    return "\n".join(lines)

def main():
    print(f"[{datetime.now().strftime('%H:%M')}] 生成昨日Twitter总结...")
    
    tweets = get_yesterday_tweets()
    
    if tweets:
        summary = summarize_tweets(tweets)
        print(summary)
    else:
        print("昨天没有抓取到推文")

if __name__ == '__main__':
    main()
