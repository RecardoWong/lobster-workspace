#!/usr/bin/env python3
"""
监控特定Twitter用户: @jdhasoptions
每小时搜索他的最新推文
"""

import os
import urllib.request
import urllib.parse
import json
from datetime import datetime

class UserMonitor:
    def __init__(self):
        self.api_key = os.environ.get('TWITTERAPI_IO_KEY') or "new1_47751911508746daafaf9194b664aaed"
        self.base_url = "https://api.twitterapi.io/twitter"
        self.target_user = "jdhasoptions"
    
    def _make_request(self, endpoint: str, params: dict = None) -> dict:
        url = f"{self.base_url}{endpoint}"
        if params:
            query = '&'.join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])
            url = f"{url}?{query}"
        
        headers = {
            'X-API-Key': self.api_key,
            'User-Agent': 'ClankerMonitor/1.0'
        }
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            return {'error': str(e)}
    
    def search_user_tweets(self) -> list:
        """搜索用户相关推文"""
        # 搜索包含用户名或from该用户的推文
        queries = [
            f"from:{self.target_user}",
            f"@{self.target_user}",
            "jdhasoptions"
        ]
        
        all_tweets = []
        for query in queries:
            try:
                result = self._make_request("/tweet/advanced_search", {
                    'query': query,
                    'queryType': 'Latest',
                    'count': 10
                })
                tweets = result.get('tweets', [])
                all_tweets.extend(tweets)
            except:
                pass
        
        # 去重
        seen = set()
        unique = []
        for t in all_tweets:
            tid = t.get('id')
            if tid and tid not in seen:
                seen.add(tid)
                unique.append(t)
        
        return unique
    
    def generate_report(self) -> str:
        tweets = self.search_user_tweets()
        
        lines = [
            "="*60,
            f"👤 @{self.target_user} 监控报告",
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "="*60,
            ""
        ]
        
        if tweets:
            lines.append(f"📝 发现 {len(tweets)} 条相关推文:\n")
            lines.append("-"*60)
            
            for i, t in enumerate(tweets[:5], 1):
                user = t.get('author', {}).get('userName', 'unknown')
                text = t.get('text', '')
                likes = t.get('likeCount', 0)
                retweets = t.get('retweetCount', 0)
                created = t.get('createdAt', '')[:16]
                
                lines.append(f"\n{i}. @{user} | {created}")
                lines.append(f"   {text[:200]}..." if len(text) > 200 else f"   {text}")
                lines.append(f"   ❤️ {likes} | 🔄 {retweets}")
        else:
            lines.append("📭 未找到新推文")
        
        lines.append(f"\n{'='*60}")
        return "\n".join(lines)

def main():
    monitor = UserMonitor()
    report = monitor.generate_report()
    print(report)
    
    # 保存报告
    filename = f"/tmp/jdhasoptions_monitor_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n💾 报告已保存: {filename}")

if __name__ == "__main__":
    main()
