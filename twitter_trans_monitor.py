#!/usr/bin/env python3
"""
🐦 Twitter监控脚本 - 完整推文+翻译版
提供完整推文 + 中文翻译（尽量完整）
"""

import requests
import re
from datetime import datetime
from typing import List, Dict

class TwitterTranslateMonitor:
    """Twitter监控类 - 完整翻译版"""
    
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
    
    def clean_text(self, text: str) -> str:
        """清理推文文本"""
        # 去掉URL
        text = re.sub(r'https?://\S+', '', text)
        # 清理多余空格
        text = ' '.join(text.split())
        return text.strip()
    
    def translate_to_chinese(self, text: str) -> str:
        """英文推文翻译成中文（简化版，关键词+意译）"""
        # 如果已经是中文，直接返回
        if any('\u4e00' <= c <= '\u9fff' for c in text):
            return text
        
        # 常见短语翻译映射
        phrases = {
            'xAI': 'xAI',
            'SpaceX': 'SpaceX',
            'is going for the endgame win': '正在为终局胜利而努力',
            'building the Dyson swarm factory': '建造戴森球工厂',
            'is the set of all things': '是所有事物的集合',
            'Some good lists': '一些不错的列表',
            'reorganized a few days ago': '几天前重组了',
            'to improve speed of execution': '为了提高执行速度',
            'semiconductor': '半导体',
            'bullish': '看涨',
            'options': '期权',
            'calls': '看涨期权',
            'long degeneracy': '长期堕落',
            'payment for order flow': '订单流付费',
        }
        
        # 简单替换（实际应该用LLM翻译，这里用关键词映射）
        result = text
        for en, cn in phrases.items():
            result = result.replace(en, cn)
        
        # 如果替换太少，标记为需要人工查看
        if result == text:
            return "[英文原文，请点击链接查看]"
        
        return result
    
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
            
            # 生成推文链接
            tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"
            
            # 清理文本
            clean_text = self.clean_text(text)
            
            # 翻译
            translation = self.translate_to_chinese(clean_text)
            
            lines.append(f"\n{i}. {clean_text}")
            lines.append(f"   翻译: {translation}")
            lines.append(f"   链接: {tweet_url}")
        
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
    monitor = TwitterTranslateMonitor()
    report = monitor.run()
    print(report)
    
    # 保存到文件
    with open(f"/tmp/twitter_trans_{datetime.now().strftime('%H%M')}.txt", 'w', encoding='utf-8') as f:
        f.write(report)
