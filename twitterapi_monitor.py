#!/usr/bin/env python3
"""
🐦 TwitterAPI.io 监控脚本 - Monty 情绪分析版
使用正确的 API Endpoint: /twitter/user/last_tweets
添加 Monty AI 情绪分析
"""

import requests
import json
from datetime import datetime
from monty_analyzer import analyze_sentiment

class TwitterAPIMonitor:
    """TwitterAPI.io 监控类"""
    
    def __init__(self):
        self.base_url = "https://api.twitterapi.io"
        self.api_key = "new1_47751911508746daafaf9194b664aaed"
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # 监控的用户列表
        self.watch_users = [
            "elonmusk",
            "jdhasoptions",
        ]
    
    def get_user_info(self, username: str) -> dict:
        """获取用户信息"""
        url = f"{self.base_url}/twitter/user/info"
        params = {"userName": username}
        
        try:
            r = requests.get(url, headers=self.headers, params=params, timeout=10)
            data = r.json()
            
            if data.get("status") == "success":
                return data.get("data", {})
            else:
                return {}
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return {}
    
    def get_user_tweets(self, username: str, limit: int = 5) -> list:
        """获取用户推文 - 使用正确的 endpoint"""
        url = f"{self.base_url}/twitter/user/last_tweets"
        params = {"userName": username, "limit": limit}
        
        try:
            r = requests.get(url, headers=self.headers, params=params, timeout=10)
            data = r.json()
            
            if data.get("status") == "success":
                tweets_data = data.get("data", {})
                return tweets_data.get("tweets", [])
            else:
                print(f"❌ 获取推文失败: {data.get('msg')}")
                return []
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return []
    
    def analyze_tweet(self, tweet: dict) -> dict:
        """分析单条推文 - 添加 Monty 情绪分析"""
        text = tweet.get("text", "")
        
        # Monty 情绪分析
        sentiment_result = analyze_sentiment(text)
        sentiment_data = sentiment_result.get('result', {}) if sentiment_result.get('success') else {}
        
        return {
            "id": tweet.get("id"),
            "text": text[:100],  # 截断显示
            "likes": tweet.get("likeCount", 0),
            "retweets": tweet.get("retweetCount", 0),
            "replies": tweet.get("replyCount", 0),
            "views": tweet.get("viewCount", 0),
            "created": tweet.get("createdAt", "")[:20],
            "url": tweet.get("url"),
            "is_reply": tweet.get("isReply", False),
            "is_retweet": tweet.get("retweeted_tweet") is not None,
            # Monty 情绪分析结果
            "sentiment": sentiment_data.get('sentiment', '未知'),
            "sentiment_score": sentiment_data.get('score', 0),
            "positive_count": sentiment_data.get('positive_count', 0),
            "negative_count": sentiment_data.get('negative_count', 0),
        }
    
    def monitor_user(self, username: str):
        """监控单个用户 - 显示情绪分析"""
        print(f"\n📊 @{username}")
        print("-" * 60)
        
        # 获取用户信息
        info = self.get_user_info(username)
        if info:
            print(f"👤 {info.get('name')} | {'✓蓝V' if info.get('isBlueVerified') else '普通'}")
            print(f"👥 粉丝: {info.get('followers', 0):,} | 📊 推文: {info.get('statusesCount', 0):,}")
        
        # 获取推文
        tweets = self.get_user_tweets(username, limit=5)
        if tweets:
            print(f"\n📝 最新 {len(tweets)} 条推文:")
            
            # 统计情绪
            bullish_count = 0
            bearish_count = 0
            
            for i, tweet in enumerate(tweets[:5], 1):
                analysis = self.analyze_tweet(tweet)
                
                # 情绪标记
                sentiment_marker = ""
                if analysis['sentiment'] == '看涨/积极':
                    sentiment_marker = "🟢看涨 "
                    bullish_count += 1
                elif analysis['sentiment'] == '看跌/消极':
                    sentiment_marker = "🔴看跌 "
                    bearish_count += 1
                
                rt_marker = "[RT] " if analysis["is_retweet"] else ""
                reply_marker = "[Reply] " if analysis["is_reply"] else ""
                
                print(f"\n  {i}. {sentiment_marker}{rt_marker}{reply_marker}{analysis['text']}...")
                print(f"     ❤️{analysis['likes']} | 🔄{analysis['retweets']} | 💬{analysis['replies']} | 👁️{analysis['views']:,}")
                if analysis['sentiment_score'] != 0:
                    print(f"     😊积极词:{analysis['positive_count']} | 😞消极词:{analysis['negative_count']} | 情绪分:{analysis['sentiment_score']:+d}")
                print(f"     🕐 {analysis['created']}")
            
            # 情绪总结
            print(f"\n  📊 情绪统计: 🟢看涨{bullish_count}条 | 🔴看跌{bearish_count}条 | ⚪中性{len(tweets)-bullish_count-bearish_count}条")
        else:
            print("\n⚠️ 暂无推文")
    
    def run(self):
        """运行监控"""
        print("=" * 60)
        print(f"🐦 TwitterAPI.io 监控报告 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)
        
        for username in self.watch_users:
            self.monitor_user(username)
        
        print("\n" + "=" * 60)


def main():
    monitor = TwitterAPIMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
