#!/usr/bin/env python3
"""
Twitter个人助手 - @Wiman23专属
功能：
1. 搜索热门内容（替代时间线，因OAuth问题）
2. 检测热点时自动发推提醒
3. 监控@提到通知
"""

import os
import urllib.request
import urllib.parse
import json
from datetime import datetime
from typing import List, Dict

class TwitterPersonalAssistant:
    """Twitter个人助手"""
    
    def __init__(self):
        self.api_key = os.environ.get('TWITTERAPI_IO_KEY') or "new1_47751911508746daafaf9194b664aaed"
        self.base_url = "https://api.twitterapi.io/twitter"
    
    def _quick_translate(self, text: str) -> str:
        """快速翻译推文（简单术语映射+常见句式）"""
        import re
        
        # 如果已经是中文或太短，不翻译
        if len(text) < 10 or any('\u4e00' <= char <= '\u9fff' for char in text):
            return ""
            
        # 术语映射表
        terms = {
            'clanker': 'Clanker',
            'bankr': 'Bankr',
            'token': '代币',
            'tokens': '代币',
            'launch': '发行',
            'launched': '已发行',
            'meme coin': '模因币',
            'base chain': 'Base链',
            'crypto': '加密货币',
            'airdrop': '空投',
            'rug': '跑路',
            'pump': '拉盘',
            'dump': '砸盘',
            'moon': '暴涨',
            'mooning': '暴涨中',
            'bearish': '看跌',
            'bullish': '看涨',
            'hodl': '持有',
            'gm': '早上好',
            'gn': '晚安',
            'wagmi': '我们会成功的',
            'ngmi': '我们不会成功的',
            'ser': '先生',
            'anon': '匿名者',
            'alpha': '内幕消息',
            'degen': '赌徒',
            'dyor': '自己做好研究',
            'rewards': '奖励',
            'claimed': '领取',
            'claim': '领取',
            'unclaimed': '未领取',
            'fees': '费用',
            'deployments': '部署',
            'beneficiary': '受益人',
            'leaderboard': '排行榜',
            'available': '可用',
            'transactions': '交易',
            'sponsored': '赞助的',
            'cost': '花费',
            'collect': '收集',
            'waiting': '等待',
            'breakdown': '明细',
            'total': '总计',
            'across': '横跨',
            'found': '找到',
            'checked': '已检查',
            'handle': '处理',
            'remember': '记住',
            'anything': '任何东西',
            'bulk': '大部分',
            'sitting': '存放在',
            'want': '想要',
            'just': '只要',
            'let me know': '告诉我',
            "you've got": '你有',
            'some': '一些',
            'here': '这里',
            'your': '你的',
            'and': '和',
            'are': '是',
            'for': '为了',
            'the': '',
            'to': '去',
            'of': '的',
            'in': '在',
            'on': '在',
            'is': '是',
            'it': '它',
            'so': '所以',
            'if': '如果',
            'will': '将会',
            "won't": '不会',
            "don't": '不要',
            'do not': '不要',
            'buy': '购买',
            'this': '这个',
        }
        
        translated = text.lower()
        for eng, chn in terms.items():
            if chn:  # 非空才替换
                translated = re.sub(r'\b' + re.escape(eng.lower()) + r'\b', chn, translated)
        
        # 清理多余空格
        translated = re.sub(r'\s+', ' ', translated).strip()
        
        return translated if translated != text.lower() else ""
    
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
    
    def generate_timeline_report(self) -> str:
        """生成热门内容报告 - 用搜索替代时间线"""
        lines = [
            "="*60,
            f"🐦 Twitter热门监控 | @{datetime.now().strftime('%H:%M')}",
            "="*60,
            ""
        ]
        
        # 搜索热门关键词
        keywords = ['clanker', 'bankr', 'base chain', 'meme coin']
        all_tweets = []
        
        for kw in keywords:
            try:
                tweets = self.search_tweets(kw, max_results=5)
                all_tweets.extend(tweets)
            except:
                pass
        
        # 高级去重策略
        seen_ids = set()  # 按ID去重
        seen_content = {}  # 按内容相似度去重 (前50字符)
        user_counts = {}  # 用户发帖计数
        unique = []
        
        for t in all_tweets:
            if not isinstance(t, dict):
                continue
                
            tid = t.get('id')
            text = t.get('text', '').strip()
            user = t.get('author', {}).get('userName', 'unknown')
            
            # 1. ID去重
            if not tid or tid in seen_ids:
                continue
            seen_ids.add(tid)
            
            # 2. 内容去重 (相似内容)
            content_key = text[:50].lower().replace(' ', '')
            if content_key in seen_content:
                continue
            seen_content[content_key] = True
            
            # 3. 限制每个用户最多2条推文 (防刷屏)
            user_counts[user] = user_counts.get(user, 0) + 1
            if user_counts[user] > 2:
                continue
            
            # 4. 过滤垃圾信息 (交易信号/外汇/诈骗等)
            spam_keywords = [
                # 交易信号/外汇
                'XAUUSD', 'gold signals', 'forex', 'free signals', 'trading group',
                'fx signals', 'pips', 'profit guarantee', 'daily signals',
                # 诈骗/虚假承诺
                'guaranteed profit', '100% profit', 'get rich quick', 
                'make money fast', 'earn daily', 'no loss trading',
                # 付费群组/课程
                'join my vip', 'premium signals', 'paid group', 'course',
                'mentorship', 'trading academy', 'learn to trade',
                # 机器人/自动化
                'trading bot', 'auto trader', 'copy trading', 'mirror trading',
                # 赌博相关
                'casino', 'betting', 'gambling', 'lottery',
            ]
            if any(kw.lower() in text.lower() for kw in spam_keywords):
                likes = t.get('likeCount', 0)
                if likes < 10:  # 低互动垃圾信息直接过滤
                    continue
            
            # 5. 🚫 过滤空投相关内容 (用户要求屏蔽)
            airdrop_keywords = [
                'airdrop', '空投', 'claim', '领取', 'free tokens', '免费代币', 
                'token drop', '代币空投', 'reward', 'rewards', '奖励',
                'air drop', 'get free', 'claim now', 'limited time',
            ]
            if any(kw.lower() in text.lower() for kw in airdrop_keywords):
                continue
            
            # 6. 🚫 过滤推广/广告 (用户要求)
            promo_keywords = [
                'promote', 'promotion', '广告', '推广', 'sponsored',
                'ad ', 'advertisement', 'click link', 'click here',
                'bio link', 'link in bio', 'dm me', 'message me',
                'follow for follow', 'f4f', 'follow back',
            ]
            if any(kw.lower() in text.lower() for kw in promo_keywords):
                likes = t.get('likeCount', 0)
                if likes < 20:  # 低互动广告过滤
                    continue
            
            unique.append(t)
        
        hot = sorted(unique, key=lambda x: x.get('likeCount', 0) + x.get('retweetCount', 0), reverse=True)
        
        if hot:
            lines.append(f"📊 监控关键词: clanker, bankr, base chain, meme coin")
            lines.append(f"找到 {len(hot)} 条相关推文\n")
            lines.append("🔥 热度排行:")
            lines.append("-"*40)
            
            for i, t in enumerate(hot[:5], 1):
                user = t.get('author', {}).get('userName', 'unknown')
                text = t.get('text', '')
                likes = t.get('likeCount', 0)
                retweets = t.get('retweetCount', 0)
                created = t.get('createdAt', '')[:10]
                # 简单翻译映射（常见clanker相关术语）
                translated = self._quick_translate(text)
                lines.append(f"\n{i}. @{user} | {created}")
                lines.append(f"   📝 {text}")
                if translated != text:
                    lines.append(f"   🌐 {translated}")
                lines.append(f"   ❤️ {likes} | 🔄 {retweets}")
        else:
            lines.append("📭 暂无热门内容")
        
        lines.append("="*60)
        return "\n".join(lines)
    
    def get_user_info(self, username: str) -> Dict:
        """获取用户信息"""
        # 去掉@前缀
        username = username.lstrip('@')
        endpoint = "/user/info"
        params = {'userName': username}
        return self._make_request(endpoint, params)
    
    def get_user_tweets(self, username: str, max_results: int = 10) -> List[Dict]:
        """获取用户最新推文"""
        username = username.lstrip('@')
        endpoint = "/user/last_tweets"
        params = {
            'userName': username,
            'count': max_results
        }
        result = self._make_request(endpoint, params)
        tweets = result.get('data', {}).get('tweets', []) if isinstance(result, dict) else []
        return tweets
    
    def monitor_user(self, username: str) -> str:
        """监控特定用户"""
        username = username.lstrip('@')
        lines = [
            f"\n{'='*60}",
            f"👤 用户监控: @{username}",
            f"{'='*60}"
        ]
        
        # 获取用户信息
        user_info = self.get_user_info(username)
        if 'error' in user_info:
            lines.append(f"❌ 无法获取用户信息: {user_info.get('error')}")
            return "\n".join(lines)
        
        data = user_info.get('data', {})
        name = data.get('name', 'Unknown')
        followers = data.get('followers', 0)
        following = data.get('following', 0)
        description = data.get('description', '')
        
        lines.append(f"\n📋 基本信息:")
        lines.append(f"   名称: {name}")
        lines.append(f"   简介: {description[:100]}..." if len(description) > 100 else f"   简介: {description}")
        lines.append(f"   粉丝: {followers:,} | 关注: {following:,}")
        
        # 获取最新推文
        tweets = self.get_user_tweets(username, max_results=5)
        if tweets:
            lines.append(f"\n📝 最新推文 ({len(tweets)}条):")
            lines.append("-" * 40)
            
            for i, t in enumerate(tweets[:5], 1):
                text = t.get('text', '')
                likes = t.get('like_count', 0)
                retweets = t.get('retweet_count', 0)
                created = t.get('created_at', '')[:10]
                
                lines.append(f"\n{i}. {created}")
                lines.append(f"   {text[:150]}..." if len(text) > 150 else f"   {text}")
                lines.append(f"   ❤️ {likes} | 🔄 {retweets}")
        else:
            lines.append("\n📭 暂无推文或获取失败")
        
        lines.append(f"\n{'='*60}")
        return "\n".join(lines)
    
    def check_and_post_hot(self) -> str:
        """检查热点并决定是否发推"""
        tweets = self.search_tweets('clanker', max_results=10)
        
        hot_tweets = []
        for tweet in tweets:
            if isinstance(tweet, str) or 'error' in tweet:
                continue
            likes = tweet.get('likeCount', 0)
            retweets = tweet.get('retweetCount', 0)
            if likes > 10 or retweets > 5:
                hot_tweets.append(tweet)
        
        if hot_tweets:
            top_tweet = hot_tweets[0]
            full_text = top_tweet.get('text', '')
            text = f"🔥 Clanker热点 | {datetime.now().strftime('%H:%M')}\n\n"
            text += f"@{top_tweet.get('author', {}).get('userName', 'unknown')}:\n"
            text += f"{full_text}\n\n"
            text += f"❤️ {top_tweet.get('likeCount', 0)} | 🔄 {top_tweet.get('retweetCount', 0)}\n"
            text += "#Clanker #Base"
            return f"✅ 检测到热点:\n{text}\n\n(已准备发推)"
        else:
            return "📭 暂无热点 (无高互动推文)"
    
    def generate_report(self) -> str:
        """生成完整报告"""
        lines = [
            "="*60,
            "🐦 Twitter个人助手报告",
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "="*60,
            ""
        ]
        
        # 热门内容监控
        lines.append("📈 热门内容监控")
        lines.append("-"*60)
        lines.append(self.generate_timeline_report())
        
        lines.append("\n")
        lines.append("🔥 热点检测")
        lines.append("-"*60)
        lines.append(self.check_and_post_hot())
        
        lines.append("\n")
        lines.append("💡 说明")
        lines.append("-"*60)
        lines.append("当前使用搜索模式获取热门内容")
        lines.append("时间线功能待OAuth修复后恢复")
        
        lines.extend(["", "="*60])
        
        return "\n".join(lines)


def main():
    """主函数"""
    assistant = TwitterPersonalAssistant()
    report = assistant.generate_report()
    print(report)
    
    # 保存报告
    filename = f"/tmp/twitter_assistant_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n💾 报告已保存: {filename}")


if __name__ == "__main__":
    main()
