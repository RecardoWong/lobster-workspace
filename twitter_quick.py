#!/usr/bin/env python3
import os
import urllib.request
import urllib.parse
import json
from datetime import datetime
import socket

socket.setdefaulttimeout(10)

API_KEY = os.getenv('TWITTERAPI_IO_KEY')
if not API_KEY:
    print("❌ 请设置 TWITTERAPI_IO_KEY 环境变量")
    exit(1)

BASE_URL = "https://api.twitterapi.io/twitter"

def make_request(endpoint, params=None):
    url = f"{BASE_URL}{endpoint}"
    if params:
        query = '&'.join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])
        url = f"{url}?{query}"
    
    headers = {'X-API-Key': API_KEY, 'User-Agent': 'ClankerMonitor/1.0'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return {'error': str(e)}

def search_tweets(query, max_results=10):
    endpoint = "/tweet/advanced_search"
    params = {'query': query, 'queryType': 'Latest'}
    result = make_request(endpoint, params)
    tweets = result.get('tweets', [])
    return tweets[:max_results]

print("="*60)
print(f"🐦 Twitter热门监控 | @{datetime.now().strftime('%H:%M')}")
print("="*60)
print()

keywords = ['clanker', 'bankr', 'base chain']
all_tweets = []

for kw in keywords:
    try:
        tweets = search_tweets(kw, max_results=5)
        if 'error' not in tweets:
            all_tweets.extend(tweets)
    except:
        pass

# 去重
seen = set()
unique = []
for t in all_tweets:
    if isinstance(t, dict):
        tid = t.get('id')
        if tid and tid not in seen:
            seen.add(tid)
            unique.append(t)

hot = sorted(unique, key=lambda x: x.get('likeCount', 0) + x.get('retweetCount', 0), reverse=True)

if hot:
    print(f"📊 监控关键词: clanker, bankr, base chain")
    print(f"找到 {len(hot)} 条相关推文\n")
    print("🔥 热度排行:")
    print("-"*40)
    
    for i, t in enumerate(hot[:5], 1):
        user = t.get('author', {}).get('userName', 'unknown')
        text = t.get('text', '')[:200]
        likes = t.get('likeCount', 0)
        retweets = t.get('retweetCount', 0)
        print(f"\n{i}. @{user}")
        print(f"   📝 {text}")
        print(f"   ❤️ {likes} | 🔄 {retweets}")
else:
    print("📭 暂无热门内容")

print("\n" + "="*60)
print("💡 本报告每小时自动生成")
print("="*60)
