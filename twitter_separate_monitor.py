#!/usr/bin/env python3
"""
🐦 Twitter监控脚本 - 单独发送版
每条推文单独发，避免截断
"""

import requests
import re
from datetime import datetime
from typing import List, Dict

class TwitterSeparateMonitor:
    """Twitter监控类 - 单独发送版"""
    
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
            {"username": "xiaomucrypto", "name": "xiaomucrypto"},
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
    
    def clean_text(self, text: str) -> str:
        """清理推文文本"""
        text = re.sub(r'https?://\S+', '', text)
        text = ' '.join(text.split())
        return text.strip()
    
    def translate_simple(self, text: str) -> str:
        """简单翻译"""
        # 如果已经是中文，直接返回
        if any('\u4e00' <= c <= '\u9fff' for c in text):
            return ""
        
        # 关键词翻译
        phrases = {
            'xAI': 'xAI',
            'SpaceX': 'SpaceX',
            'is going for the endgame win': '正在为终局胜利而努力',
            'building the Dyson swarm factory': '建造戴森球工厂',
            'is the set of all things': '是所有事物的集合',
            'Some good lists': '一些不错的列表',
            'semiconductor': '半导体',
            'bullish': '看涨',
            'options': '期权',
            'calls': '看涨期权',
            'Keynesian economists': '凯恩斯主义经济学家',
        }
        
        result = text
        for en, cn in phrases.items():
            result = result.replace(en, cn)
        
        if result == text:
            return ""
        return result
    
    def generate_messages(self) -> List[str]:
        """生成每条推文的消息列表"""
        messages = []
        
        for user_info in self.watch_users:
            username = user_info['username']
            name = user_info['name']
            
            tweets = self.get_user_tweets(username, limit=5)
            
            if not tweets:
                continue
            
            # 添加用户标题
            messages.append(f"📊 @{username} ({name}) 最新推文")
            
            for i, tweet in enumerate(tweets[:5], 1):
                text = tweet.get("text", "")
                tweet_id = tweet.get("id", "")
                
                # 清理文本
                clean_text = self.clean_text(text)
                
                # 翻译
                translation = self.translate_simple(clean_text)
                
                # 生成推文链接
                tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"
                
                # 构建消息
                msg_lines = [f"\n{i}. {clean_text}"]
                if translation:
                    msg_lines.append(f"翻译: {translation}")
                msg_lines.append(f"链接: {tweet_url}")
                
                messages.append("\n".join(msg_lines))
        
        return messages
    
    def run(self):
        """运行监控并输出消息列表"""
        messages = self.generate_messages()
        
        # 打印所有消息
        for msg in messages:
            print(msg)
            print("\n" + "="*60 + "\n")
        
        # 保存到文件
        with open(f"/tmp/twitter_separate_{datetime.now().strftime('%H%M')}.txt", 'w', encoding='utf-8') as f:
            for msg in messages:
                f.write(msg + "\n\n" + "="*60 + "\n\n")


if __name__ == "__main__":
    monitor = TwitterSeparateMonitor()
    monitor.run()
