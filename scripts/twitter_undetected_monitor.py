#!/usr/bin/env python3
"""
Twitter 监控 - 使用 patchright 绕过反爬虫 (无 API 版)
定时抓取推文并推送到 Telegram
"""
import asyncio
import json
import os
from patchright.async_api import async_playwright
from datetime import datetime

# 监控的用户列表
WATCH_USERS = [
    {'username': 'elonmusk', 'name': 'Elon Musk'},
    {'username': 'jdhasoptions', 'name': 'JD'},
    {'username': 'xiaomucrypto', 'name': '小木Crypto'},
]

class TwitterMonitor:
    def __init__(self):
        self.browser = None
        self.page = None
        self.results = []
        
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
            ]
        )
        self.page = await self.browser.new_page()
        
    async def fetch_user_tweets(self, user_info, limit=3):
        """获取用户最新推文"""
        username = user_info['username']
        url = f'https://twitter.com/{username}'
        
        try:
            await self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await self.page.wait_for_timeout(3000)
            
            # 获取推文
            tweets = await self.page.query_selector_all('article[data-testid="tweet"]')
            
            user_tweets = []
            for i, tweet in enumerate(tweets[:limit]):
                try:
                    text_elem = await tweet.query_selector('[data-testid="tweetText"]')
                    time_elem = await tweet.query_selector('time')
                    
                    text = await text_elem.inner_text() if text_elem else ''
                    time_str = await time_elem.get_attribute('datetime') if time_elem else ''
                    
                    if text and len(text) > 10:
                        user_tweets.append({
                            'author': user_info['name'],
                            'username': username,
                            'text': text[:150] + '...' if len(text) > 150 else text,
                            'time': time_str,
                            'fetched_at': datetime.now().isoformat()
                        })
                except:
                    continue
            
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
        
        # 输出摘要
        print("\n" + "="*50)
        print(f"📊 共获取 {len(all_tweets)} 条推文")
        print("\n最新推文摘要:")
        for i, tweet in enumerate(all_tweets[:5]):
            print(f"\n{i+1}. @{tweet['username']}")
            print(f"   {tweet['text'][:80]}...")
        
        print(f"\n💾 结果已保存: {result_file}")
        
    finally:
        await monitor.close()

if __name__ == '__main__':
    asyncio.run(main())
