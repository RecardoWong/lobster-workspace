#!/usr/bin/env python3
"""
🐦 Twitter监控脚本 - Agent Browser完整版
结合TwitterAPI.io + Agent Browser获取完整推文
"""

import requests
import json
import subprocess
from datetime import datetime
from typing import List, Dict

class TwitterFullMonitor:
    """Twitter监控类 - 完整版"""
    
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
    
    def get_user_tweets_api(self, username: str, limit: int = 5) -> List[Dict]:
        """用TwitterAPI.io获取推文列表"""
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
            print(f"API请求失败: {e}")
            return []
    
    def get_full_tweet_browser(self, tweet_id: str) -> str:
        """用Agent Browser获取完整推文内容"""
        try:
            # 打开推文页面
            url = f"https://twitter.com/i/web/status/{tweet_id}"
            result = subprocess.run(
                ['agent-browser', 'open', url],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                return None
            
            # 获取页面内容
            result = subprocess.run(
                ['agent-browser', 'snapshot', '-c'],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                return None
            
            # 解析文本内容（简单提取）
            output = result.stdout
            # 查找推文文本（在article标签内）
            lines = output.split('\n')
            for i, line in enumerate(lines):
                if 'text:' in line and i > 0:
                    # 提取推文文本行
                    text_line = line.strip().replace('- text:', '').strip()
                    if len(text_line) > 20:  # 过滤短文本
                        return text_line
            
            return None
        except Exception as e:
            print(f"Browser获取失败: {e}")
            return None
    
    def analyze_tweet_simple(self, text: str) -> Dict:
        """简单情绪分析"""
        text_lower = text.lower()
        
        positive = ['good', 'great', 'amazing', 'excellent', 'love', 'best', 'bullish', 'moon', 'win', 'exciting']
        negative = ['bad', 'terrible', 'worst', 'hate', 'bearish', 'crash', 'scam', 'lose', 'unfortunately']
        
        pos_count = sum(1 for p in positive if p in text_lower)
        neg_count = sum(1 for n in negative if n in text_lower)
        
        if pos_count > neg_count:
            sentiment = "🟢看涨"
        elif neg_count > pos_count:
            sentiment = "🔴看跌"
        else:
            sentiment = "⚪中性"
        
        return {
            'sentiment': sentiment,
            'score': pos_count - neg_count
        }
    
    def monitor_user(self, user_info: Dict) -> str:
        """监控单个用户"""
        username = user_info['username']
        name = user_info['name']
        
        lines = [f"\n📊 @{username} ({name})", "-" * 50]
        
        # 获取推文列表
        tweets = self.get_user_tweets_api(username, limit=5)
        
        if not tweets:
            lines.append("⚠️ 暂无推文数据")
            return "\n".join(lines)
        
        for i, tweet in enumerate(tweets[:5], 1):
            text = tweet.get("text", "")
            tweet_id = tweet.get("id", "")
            
            # 如果文本被截断，尝试用Browser获取完整内容
            if text.endswith('...') or len(text) < 50:
                full_text = self.get_full_tweet_browser(tweet_id)
                if full_text:
                    text = full_text
            
            # 分析情绪
            analysis = self.analyze_tweet_simple(text)
            
            # 格式化输出
            likes = tweet.get("likeCount", 0)
            retweets = tweet.get("retweetCount", 0)
            
            lines.append(f"\n{i}. {analysis['sentiment']} {text[:150]}{'...' if len(text) > 150 else ''}")
            lines.append(f"   ❤️{likes} | 🔄{retweets}")
        
        return "\n".join(lines)
    
    def run(self) -> str:
        """运行监控"""
        lines = [
            "=" * 60,
            f"🐦 Twitter监控报告 | {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 60,
        ]
        
        for user_info in self.watch_users:
            lines.append(self.monitor_user(user_info))
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)


if __name__ == "__main__":
    monitor = TwitterFullMonitor()
    report = monitor.run()
    print(report)
    
    # 保存到文件
    with open(f"/tmp/twitter_full_{datetime.now().strftime('%H%M')}.txt", 'w') as f:
        f.write(report)
