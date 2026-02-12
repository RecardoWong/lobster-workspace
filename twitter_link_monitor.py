#!/usr/bin/env python3
"""
🐦 Twitter监控脚本 - 链接+翻译版
提供推文链接 + 中文摘要翻译
"""

import requests
import json
import re
from datetime import datetime
from typing import List, Dict

class TwitterLinkMonitor:
    """Twitter监控类 - 链接+翻译版"""
    
    def __init__(self):
        self.base_url = "https://api.twitterapi.io"
        self.api_key = "new1_47751911508746daafaf9194b664aaed"
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        self.watch_users = [
            {"username": "elonmusk", "name": "Elon Musk"},
            {"username": "jdhasoptions", "name": "JD"},
        ]
    
    def get_user_tweets(self, username: str, limit: int = 5) -> List[Dict]:
        """获取推文列表"""
        url = f"{self.base_url}/twitter/user/last_tweets"
        params = {"userName": username, "limit": limit}
        
        try:
            r = requests.get(url, headers=self.headers, params=params, timeout=10)
            data = r.json()
            
            if data.get("status") == "success":
                tweets_data = data.get("data", {})
                return tweets_data.get("tweets", [])
            return []
        except Exception as e:
            return []
    
    def translate_text(self, text: str) -> str:
        """简单英文到中文翻译（关键词对照）"""
        # 常见关键词翻译
        translations = {
            'bullish': '看涨',
            'bearish': '看跌',
            'moon': '暴涨',
            'pump': '拉升',
            'dump': '抛售',
            'buy': '买入',
            'sell': '卖出',
            'hodl': '持有',
            'xai': 'xAI',
            'spacex': 'SpaceX',
            'ai': 'AI',
            'endgame': '终局',
            'reorganized': '重组',
            'semiconductor': '半导体',
            'options': '期权',
            'calls': '看涨期权',
            'puts': '看跌期权',
        }
        
        # 简单替换
        result = text.lower()
        for en, cn in translations.items():
            result = result.replace(en, cn)
        
        return result[:100]  # 返回前100字符
    
    def extract_summary(self, text: str) -> str:
        """提取摘要"""
        # 去掉URL
        text = re.sub(r'https?://\S+', '', text)
        # 去掉@用户名
        text = re.sub(r'@\w+', '', text)
        # 清理多余空格
        text = ' '.join(text.split())
        
        # 取前80字符
        if len(text) > 80:
            return text[:80] + "..."
        return text
    
    def analyze_sentiment(self, text: str) -> str:
        """情绪分析"""
        text_lower = text.lower()
        
        positive = ['good', 'great', 'amazing', 'excellent', 'love', 'best', 'bullish', 'moon', 'win', 'exciting', 'incredible']
        negative = ['bad', 'terrible', 'worst', 'hate', 'bearish', 'crash', 'scam', 'lose', 'unfortunately', 'parting']
        
        pos_count = sum(1 for p in positive if p in text_lower)
        neg_count = sum(1 for n in negative if n in text_lower)
        
        if pos_count > neg_count:
            return "🟢 看涨"
        elif neg_count > pos_count:
            return "🔴 看跌"
        else:
            return "⚪ 中性"
    
    def monitor_user(self, user_info: Dict) -> str:
        """监控单个用户"""
        username = user_info['username']
        name = user_info['name']
        
        lines = [f"\n📊 @{username} ({name})", "-" * 50]
        
        tweets = self.get_user_tweets(username, limit=5)
        
        if not tweets:
            lines.append("暂无推文")
            return "\n".join(lines)
        
        for i, tweet in enumerate(tweets[:5], 1):
            text = tweet.get("text", "")
            tweet_id = tweet.get("id", "")
            likes = tweet.get("likeCount", 0)
            
            # 生成推文链接
            tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"
            
            # 提取摘要
            summary = self.extract_summary(text)
            
            # 情绪分析
            sentiment = self.analyze_sentiment(text)
            
            # 简单翻译关键词
            translated = self.translate_text(summary)
            
            lines.append(f"\n{i}. {sentiment}")
            lines.append(f"   原文: {summary}")
            if translated != summary.lower()[:100]:
                lines.append(f"   译文: {translated}")
            lines.append(f"   👉 {tweet_url}")
            lines.append(f"   ❤️ {likes}")
        
        return "\n".join(lines)
    
    def run(self) -> str:
        """运行监控"""
        lines = [
            "=" * 60,
            f"🐦 Twitter监控 | {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 60,
        ]
        
        for user_info in self.watch_users:
            lines.append(self.monitor_user(user_info))
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)


if __name__ == "__main__":
    monitor = TwitterLinkMonitor()
    report = monitor.run()
    print(report)
    
    # 保存到文件
    with open(f"/tmp/twitter_link_{datetime.now().strftime('%H%M')}.txt", 'w', encoding='utf-8') as f:
        f.write(report)
