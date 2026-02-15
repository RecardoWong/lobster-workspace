#!/usr/bin/env python3
"""
Twitter 监控脚本 - 使用 patchright 绕过反爬虫检测
基于 playwright-undetected-skill
"""
import asyncio
import json
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
                '--disable-features=IsolateOrigins,site-per-process',
            ]
        )
        self.page = await self.browser.new_page()
        
    async def fetch_user_tweets(self, username, limit=5):
        """获取用户推文"""
        url = f'https://twitter.com/{username}'
        print(f"正在访问: {url}")
        
        await self.page.goto(url, wait_until='domcontentloaded')
        await self.page.wait_for_timeout(5000)  # 等待 JavaScript 加载
        
        # 截图查看页面状态
        await self.page.screenshot(path=f'/root/.openclaw/workspace/twitter_{username}.png')
        print(f"已截图: twitter_{username}.png")
        
        # 获取页面标题
        title = await self.page.title()
        print(f"页面标题: {title}")
        
        # 尝试多种选择器获取推文
        selectors = [
            'article[data-testid="tweet"]',
            '[data-testid="tweetText"]',
            'article[role="article"]',
        ]
        
        tweets = []
        for selector in selectors:
            elements = await self.page.query_selector_all(selector)
            if elements:
                print(f"使用选择器 '{selector}' 找到 {len(elements)} 个元素")
                for i, elem in enumerate(elements[:limit]):
                    try:
                        text = await elem.inner_text()
                        if text and len(text) > 10:
                            tweets.append({
                                'author': username,
                                'text': text[:200],
                                'time': datetime.now().isoformat()
                            })
                    except:
                        pass
                if tweets:
                    break
        
        return tweets
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

async def main():
    monitor = TwitterMonitor()
    await monitor.start()
    
    try:
        # 监控多个账号
        users = ['elonmusk', 'jdhasoptions']
        all_tweets = []
        
        for user in users:
            print(f"\n{'='*50}")
            print(f"获取 @{user} 的推文...")
            tweets = await monitor.fetch_user_tweets(user)
            all_tweets.extend(tweets)
            
            for i, tweet in enumerate(tweets[:3]):
                print(f"\n[推文 {i+1}]")
                print(f"作者: @{tweet['author']}")
                print(f"内容: {tweet['text']}")
        
        # 保存结果
        with open('/root/.openclaw/workspace/twitter_monitor_result.json', 'w', encoding='utf-8') as f:
            json.dump(all_tweets, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*50}")
        print(f"共获取 {len(all_tweets)} 条推文")
        print("结果已保存到: twitter_monitor_result.json")
        
    finally:
        await monitor.close()

if __name__ == '__main__':
    asyncio.run(main())
