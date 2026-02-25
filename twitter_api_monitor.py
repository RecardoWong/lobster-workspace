#!/usr/bin/env python3
"""
Twitter 监控 - TwitterAPI.io 版
恢复使用真实 API 数据
"""
import os
import requests
from datetime import datetime

API_KEY = os.getenv('TWITTERAPI_IO_KEY')
if not API_KEY:
    print("❌ 请设置 TWITTERAPI_IO_KEY 环境变量")
    exit(1)

BASE_URL = "https://api.twitterapi.io"

USERS = [
    {"username": "elonmusk", "name": "Elon Musk"},
    {"username": "jdhasoptions", "name": "JD"},
    {"username": "xiaomucrypto", "name": "小木Crypto"},
]

def get_tweets(username):
    """获取用户最新推文"""
    try:
        url = f"{BASE_URL}/twitter/user/last_tweets"
        headers = {"X-API-Key": API_KEY}
        params = {"userName": username, "limit": 3}
        
        r = requests.get(url, headers=headers, params=params, timeout=15)
        data = r.json()
        
        if data.get("status") == "success":
            tweets = data.get("data", {}).get("tweets", [])
            return [
                {
                    "text": t.get("text", "")[:100] + "..." if len(t.get("text", "")) > 100 else t.get("text", ""),
                    "likes": t.get("likeCount", 0),
                    "time": t.get("createdAt", "")[4:16]  # 简化为月日时分
                }
                for t in tweets[:2]  # 只取前2条
            ]
        return []
    except Exception as e:
        print(f"Error fetching {username}: {e}")
        return []

def main():
    print("🐦 Twitter 重点动态")
    print("-" * 50)
    
    for user in USERS:
        tweets = get_tweets(user["username"])
        if tweets:
            print(f"\n@{user['username']} ({user['name']}):")
            for t in tweets:
                print(f"  • {t['text']}")
                print(f"    👍 {t['likes']} | {t['time']}")
    
    print("-" * 50)
    print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("数据来源: TwitterAPI.io")

if __name__ == '__main__':
    main()
