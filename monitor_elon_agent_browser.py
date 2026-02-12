#!/usr/bin/env python3
"""
Elon Musk 推文监控 - Agent Browser 方案
每小时抓取一次，检测新推文
"""

import subprocess
import json
import re
from datetime import datetime
from pathlib import Path

# 保存文件
SAVE_FILE = '/tmp/elon_tweets_last.json'

def fetch_elon_tweets():
    """使用 agent-browser 抓取 Elon 推文"""
    try:
        # 使用 agent-browser 获取页面内容
        result = subprocess.run([
            'agent-browser', 'snapshot', 
            'https://x.com/elonmusk',
            '--timeout', '20000'
        ], capture_output=True, text=True, timeout=30)
        
        output = result.stdout
        
        # 解析推文
        tweets = []
        
        # 提取置顶/最新推文
        # 匹配推文格式: article "..." [ref=e...]
        tweet_pattern = r'article "(.*?)" \[ref=e(\d+)\]'
        matches = re.findall(tweet_pattern, output)
        
        for match in matches[:5]:  # 只取前5条
            tweet_text = match[0]
            if 'Elon Musk' in tweet_text or '@elonmusk' in tweet_text:
                # 提取时间
                time_match = re.search(r'(\w{3} \d{1,2}|\d{4}|Apr \d{1,2}, \d{4}|Jul \d{1,2}, \d{4}|Feb \d{1,2})', output[:output.find(tweet_text) + 500])
                time_str = time_match.group(1) if time_match else 'Unknown'
                
                tweets.append({
                    'text': tweet_text[:200],
                    'time': time_str,
                    'fetched_at': datetime.now().isoformat()
                })
        
        return tweets
        
    except Exception as e:
        print(f"❌ 抓取失败: {e}")
        return []

def check_new_tweets():
    """检查新推文"""
    print(f"🔍 {datetime.now().strftime('%H:%M')} 检查 Elon 推文...\n")
    
    # 获取当前推文
    current_tweets = fetch_elon_tweets()
    
    if not current_tweets:
        print("📭 未获取到推文")
        return []
    
    # 读取上次保存的推文
    last_tweets = []
    if Path(SAVE_FILE).exists():
        with open(SAVE_FILE) as f:
            data = json.load(f)
            last_tweets = data.get('tweets', [])
    
    # 对比找出新推文
    new_tweets = []
    for t in current_tweets:
        if not any(lt.get('text') == t['text'] for lt in last_tweets):
            new_tweets.append(t)
    
    # 保存当前推文
    with open(SAVE_FILE, 'w') as f:
        json.dump({'tweets': current_tweets, 'updated': datetime.now().isoformat()}, f)
    
    return new_tweets

if __name__ == "__main__":
    new = check_new_tweets()
    
    if new:
        print(f"🚨 发现 {len(new)} 条新推文！\n")
        for t in new:
            print(f"📝 {t['text'][:100]}...")
            print(f"⏰ {t['time']}\n")
    else:
        print("📭 暂无新推文")
        print(f"💾 已保存 {len(fetch_elon_tweets())} 条推文到本地")
