#!/usr/bin/env python3
"""
Twitter 抓取测试 - 使用 patchright 绕过反爬虫
"""
import asyncio
from patchright.async_api import async_playwright

async def fetch_twitter():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path='/opt/chromium/chrome',
            args=['--disable-blink-features=AutomationControlled']
        )
        page = await browser.new_page()
        
        # 访问 Twitter
        await page.goto('https://twitter.com/elonmusk', wait_until='networkidle')
        
        # 等待页面加载
        await page.wait_for_timeout(3000)
        
        # 获取页面标题
        title = await page.title()
        print(f"页面标题: {title}")
        
        # 获取推文内容
        tweets = await page.query_selector_all('[data-testid="tweet"]')
        print(f"找到 {len(tweets)} 条推文")
        
        for i, tweet in enumerate(tweets[:3]):
            text = await tweet.inner_text()
            print(f"\n推文 {i+1}:")
            print(text[:200] + "..." if len(text) > 200 else text)
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(fetch_twitter())
