#!/usr/bin/env python3
"""
Twitter 监控脚本 - 使用 patchright 绕过反爬虫检测
修复版：正确处理 Twitter 页面结构
"""
import asyncio
import json
import re
from patchright.async_api import async_playwright
from datetime import datetime

class TwitterMonitor:
    def __init__(self):
        self.browser = None
        self.page = None
        
    async def start(self):
        """启动浏览器"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            executable_path='/opt/chromium/chrome',
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        self.page = await context.new_page()
        
    async def fetch_user_tweets(self, user_info, limit=3):
        """获取用户推文"""
        username = user_info['username']
        url = f'https://twitter.com/{username}'
        print(f"\n正在访问: {url}")
        
        try:
            # 访问页面
            await self.page.goto(url, wait_until='domcontentloaded', timeout=60000)
            await self.page.wait_for_timeout(5000)
            
            # 截图查看
            await self.page.screenshot(path=f'/root/.openclaw/workspace/twitter_{username}.png')
            
            # 获取页面HTML内容
            html_content = await self.page.content()
            
            # 从HTML中提取推文链接
            tweet_pattern = r'href="(/' + username + r'/status/(\d+))"'
            tweet_matches = re.findall(tweet_pattern, html_content)
            
            # 去重并限制数量
            seen_ids = set()
            unique_tweets = []
            for link, tweet_id in tweet_matches:
                if tweet_id not in seen_ids:
                    seen_ids.add(tweet_id)
                    unique_tweets.append((link, tweet_id))
                if len(unique_tweets) >= limit:
                    break
            
            user_tweets = []
            for link, tweet_id in unique_tweets:
                tweet_url = f"https://twitter.com{link}"
                
                # 尝试从页面中提取推文文本
                # 查找推文文本的多种可能模式
                text = None
                
                # 方法1: 查找 tweetText 数据测试ID
                text_pattern = r'data-testid="tweetText"[^>]*>(.*?)</div>'
                text_matches = re.findall(text_pattern, html_content, re.DOTALL)
                if text_matches:
                    # 清理HTML标签
                    text = re.sub(r'<[^>]+>', '', text_matches[len(user_tweets)])
                    text = text.strip()
                
                # 方法2: 如果上面的方法失败，尝试其他模式
                if not text or len(text) < 5:
                    # 尝试从页面中直接获取可见文本
                    try:
                        # 使用JavaScript获取推文文本
                        tweets_data = await self.page.evaluate('''() => {
                            const tweets = [];
                            const articles = document.querySelectorAll('article[data-testid="tweet"]');
                            for (let i = 0; i < articles.length && i < 3; i++) {
                                const textEl = articles[i].querySelector('[data-testid="tweetText"]');
                                if (textEl) {
                                    tweets.push(textEl.innerText);
                                }
                            }
                            return tweets;
                        }''')
                        if tweets_data and len(user_tweets) < len(tweets_data):
                            text = tweets_data[len(user_tweets)]
                    except:
                        pass
                
                # 如果还是获取不到，使用占位符
                if not text or len(text) < 3:
                    text = f'推文来自 @{username}'
                
                # 限制文本长度
                text = text[:280] if len(text) > 280 else text
                
                user_tweets.append({
                    'author': user_info['name'],
                    'username': username,
                    'text': text,
                    'url': tweet_url,
                    'time': datetime.now().isoformat()
                })
            
            print(f"找到 {len(user_tweets)} 条推文")
            return user_tweets
            
        except Exception as e:
            print(f"获取 @{username} 失败: {e}")
            return []
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

async def main():
    print(f"🐦 Twitter 监控启动 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*50)
    
    monitor = TwitterMonitor()
    await monitor.start()
    
    WATCH_USERS = [
        {'username': 'elonmusk', 'name': 'Elon Musk'},
        {'username': 'jdhasoptions', 'name': 'JD'},
    ]
    
    all_tweets = []
    
    try:
        for user in WATCH_USERS:
            print(f"\n正在抓取 @{user['username']}...")
            tweets = await monitor.fetch_user_tweets(user)
            all_tweets.extend(tweets)
            print(f"✅ 获取 {len(tweets)} 条推文")
            
        # 保存结果
        result_file = '/root/.openclaw/workspace/reports/twitter_undetected_latest.json'
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(all_tweets, f, ensure_ascii=False, indent=2)
        
        print("\n" + "="*50)
        print(f"📊 共获取 {len(all_tweets)} 条推文")
        for i, tweet in enumerate(all_tweets[:5]):
            print(f"\n{i+1}. @{tweet['username']}")
            print(f"   {tweet['url']}")
        
        print(f"\n💾 结果已保存: {result_file}")
        
    finally:
        await monitor.close()

if __name__ == '__main__':
    asyncio.run(main())
