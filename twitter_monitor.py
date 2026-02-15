#!/usr/bin/env python3
"""
Twitter/X 监控系统 (TwitterAPI.io版本)
用于追踪KOL动态和话题热度
"""

import os
import urllib.request
import urllib.parse
import json
from datetime import datetime
from typing import List, Dict, Optional

class TwitterMonitor:
    """Twitter监控器 - 使用TwitterAPI.io"""
    
    def __init__(self):
        self.api_key = os.environ.get('TWITTERAPI_IO_KEY')
        self.base_url = "https://api.twitterapi.io/twitter"
        
        if not self.api_key:
            self._load_from_env_file()
    
    def _load_from_env_file(self):
        """从.env文件加载"""
        env_path = "/root/.openclaw/workspace/.env"
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('TWITTERAPI_IO_KEY='):
                        self.api_key = line.split('=', 1)[1].strip()
                        break
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """发送API请求"""
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
        except urllib.error.HTTPError as e:
            return {'error': f'HTTP {e.code}: {e.reason}', 'body': e.read().decode()}
        except Exception as e:
            return {'error': str(e)}
    
    def search_tweets(self, query: str, query_type: str = "Latest", max_results: int = 10) -> List[Dict]:
        """搜索推文"""
        endpoint = "/tweet/advanced_search"
        params = {
            'query': query,
            'queryType': query_type,
        }
        
        result = self._make_request(endpoint, params)
        tweets = result.get('tweets', [])
        return tweets[:max_results]
    
    def get_user_tweets(self, username: str, max_results: int = 5) -> List[Dict]:
        """获取用户推文"""
        endpoint = "/user/last_tweets"
        params = {
            'username': username,
        }
        
        result = self._make_request(endpoint, params)
        tweets = result.get('tweets', [])
        return tweets[:max_results]
    
    def get_user_by_username(self, username: str) -> Dict:
        """获取用户信息"""
        endpoint = "/user/by/username"
        params = {
            'username': username,
        }
        
        return self._make_request(endpoint, params)
    
    def search_clanker_related(self) -> Dict:
        """搜索Clanker相关内容"""
        queries = {
            'clanker': 'clanker',
            'bankr': 'bankr',
            'clanker_token': 'clanker token',
            'base_meme': 'base meme coin',
        }
        
        results = {}
        for name, query in queries.items():
            try:
                tweets = self.search_tweets(query, max_results=5)
                results[name] = tweets
            except Exception as e:
                results[name] = [{'error': str(e)}]
        
        return results
    
    def generate_report(self) -> str:
        """生成监控报告"""
        lines = [
            "="*60,
            "🐦 Twitter KOL 监控报告",
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "="*60,
            ""
        ]
        
        if not self.api_key:
            lines.append("⚠️ TwitterAPI.io Key 未配置")
            return "\n".join(lines)
        
        # 搜索Clanker相关内容
        lines.append("🔍 Clanker相关推文")
        lines.append("-"*60)
        
        search_results = self.search_clanker_related()
        
        total_found = 0
        for category, tweets in search_results.items():
            lines.append(f"\n📌 {category}:")
            if tweets and 'error' not in tweets[0]:
                lines.append(f"   找到 {len(tweets)} 条推文")
                total_found += len(tweets)
                for tweet in tweets[:2]:  # 只显示前2条
                    text = tweet.get('text', '')[:80]
                    if len(tweet.get('text', '')) > 80:
                        text += "..."
                    author = tweet.get('author', {}).get('userName', 'unknown')
                    likes = tweet.get('likeCount', 0)
                    retweets = tweet.get('retweetCount', 0)
                    lines.append(f"   • @{author}: {text}")
                    lines.append(f"     ❤️ {likes} | 🔄 {retweets}")
            elif tweets and 'error' in tweets[0]:
                lines.append(f"   错误: {tweets[0].get('error', 'Unknown')}")
            else:
                lines.append("   暂无推文")
        
        lines.append("")
        lines.append(f"📊 总计找到 {total_found} 条相关推文")
        
        # 获取特定用户推文（如果有重要KOL）
        lines.append("")
        lines.append("👤 监控用户动态")
        lines.append("-"*60)
        
        kols = ['clanker']  # 可以添加更多KOL
        for username in kols:
            user_tweets = self.get_user_tweets(username, max_results=3)
            if user_tweets and 'error' not in user_tweets[0]:
                lines.append(f"\n@{username}:")
                for tweet in user_tweets[:2]:
                    text = tweet.get('text', '')[:60]
                    if len(tweet.get('text', '')) > 60:
                        text += "..."
                    lines.append(f"   • {text}")
        
        lines.extend([
            "",
            "="*60,
            "💡 数据来源: TwitterAPI.io",
            "="*60
        ])
        
        return "\n".join(lines)


def main():
    """主函数"""
    monitor = TwitterMonitor()
    report = monitor.generate_report()
    print(report)
    
    # 保存报告
    filename = f"/tmp/twitter_monitor_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n💾 报告已保存: {filename}")


if __name__ == "__main__":
    main()
