#!/usr/bin/env python3
"""
Twitter Dashboard 更新脚本
使用 twitterapi.io API 获取四个账号的最新推文
"""
import urllib.request
import urllib.parse
import json
import os
from datetime import datetime

API_KEY = "new1_47751911508746daafaf9194b664aaed"
BASE_URL = "https://api.twitterapi.io/twitter"

DATA_FILE = '/root/.openclaw/workspace/lobster-workspace/dashboard/data/twitter_data.json'
LOG_FILE = '/root/.openclaw/workspace/lobster-workspace/logs/twitter_monitor.log'

# 监控账号
ACCOUNTS = {
    'elonmusk': 'Elon Musk',
    'jdhasoptions': 'JD',
    'xiaomucrypto': 'xiaomucrypto',
    'aistocksavvy': 'AI Stock Savvy'
}

def log_message(msg):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {msg}"
    print(log_line)
    # 确保日志目录存在
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_line + '\n')

def make_request(endpoint, params=None):
    """发送API请求"""
    url = f"{BASE_URL}{endpoint}"
    if params:
        query = '&'.join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])
        url = f"{url}?{query}"
    
    headers = {'X-API-Key': API_KEY, 'User-Agent': 'TwitterDashboard/1.0'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return {'error': str(e)}

def get_user_tweets(username, max_results=5):
    """获取用户最新推文"""
    endpoint = "/user/last_tweets"
    params = {
        'userName': username,
        'count': max_results
    }
    result = make_request(endpoint, params)
    
    if 'error' in result:
        log_message(f"⚠️ @{username} API错误: {result['error'][:80]}")
        return []
    
    tweets = result.get('data', {}).get('tweets', [])
    return tweets

def load_existing_data():
    """加载现有数据"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {'update_time': datetime.now().isoformat(), 'tweets': {}}

def save_data(data):
    """保存数据"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def format_tweet(tweet, username):
    """格式化推文数据"""
    created_at = tweet.get('createdAt', '')
    # 转换时间格式
    try:
        # 解析 Twitter 时间格式
        dt = datetime.strptime(created_at, '%a %b %d %H:%M:%S %z %Y')
        time_str = dt.isoformat()
    except:
        time_str = created_at
    
    return {
        'author': username,
        'text': tweet.get('text', '')[:500],
        'time': time_str,
        'fetched_at': datetime.now().isoformat(),
        'likes': tweet.get('likeCount', 0),
        'retweets': tweet.get('retweetCount', 0),
        'replies': tweet.get('replyCount', 0)
    }

def main():
    log_message("=" * 60)
    log_message("🐦 Twitter Dashboard 数据更新开始")
    log_message("=" * 60)
    
    # 加载现有数据
    data = load_existing_data()
    
    all_tweets_count = 0
    
    for username, name in ACCOUNTS.items():
        log_message(f"\n📱 获取 @{username} ({name})...")
        
        tweets = get_user_tweets(username, max_results=5)
        
        if tweets:
            formatted_tweets = [format_tweet(t, username) for t in tweets]
            data['tweets'][username] = formatted_tweets
            log_message(f"   ✅ 获取 {len(formatted_tweets)} 条推文")
            for i, t in enumerate(formatted_tweets[:2], 1):
                preview = t['text'][:60] + '...' if len(t['text']) > 60 else t['text']
                log_message(f"   {i}. {preview}")
            all_tweets_count += len(formatted_tweets)
        else:
            log_message(f"   ⚠️ 未获取到新推文，保留现有数据")
        
        # 避免请求过快
        import time
        time.sleep(1)
    
    # 更新时间戳
    data['update_time'] = datetime.now().isoformat()
    
    # 保存数据
    save_data(data)
    
    log_message("\n" + "=" * 60)
    log_message(f"✅ 更新完成 - 本次获取 {all_tweets_count} 条推文")
    log_message(f"💾 数据已保存: {DATA_FILE}")
    log_message(f"🕐 更新时间: {data['update_time']}")
    log_message("=" * 60)

if __name__ == '__main__':
    main()
