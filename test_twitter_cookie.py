#!/usr/bin/env python3
"""测试 Twitter Cookie 是否有效"""

import asyncio
import os
from playwright.async_api import async_playwright

# Cookie 配置
AUTH_TOKEN = '5da5c73c3286e0c825c5a337eb60ffaf93f2620c'
CT0 = 'bb867bfa8ae5a410dec9e6537f8aa4f183c43b65c641f9b293a171e8eb8b1b9df359891c89b0e181f4c21bb6e292f422075b77ac3f51a0915fc5e82e2c69c9c5100c14355137082faa36804f10f18ebd'

async def test_twitter():
    """测试 Twitter 抓取"""
    async with async_playwright() as p:
        # 连接到 Steel Browser
        browser = await p.chromium.connect_over_cdp('ws://localhost:3000/')
        
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        
        # 添加 Cookie
        await context.add_cookies([
            {'name': 'auth_token', 'value': AUTH_TOKEN, 'domain': '.x.com', 'path': '/'},
            {'name': 'ct0', 'value': CT0, 'domain': '.x.com', 'path': '/'}
        ])
        
        page = await context.new_page()
        
        try:
            # 访问 Twitter
            print("🐦 测试访问 @elonmusk...")
            await page.goto('https://x.com/elonmusk', timeout=30000)
            await page.wait_for_timeout(5000)
            
            # 获取页面标题
            title = await page.title()
            print(f"页面标题: {title}")
            
            # 获取推文
            tweets = await page.locator('article[data-testid="tweet"]').count()
            print(f"找到推文: {tweets} 条")
            
            if tweets > 0:
                print("✅ Cookie 有效！")
            else:
                print("❌ 没有找到推文")
                # 检查是否有登录提示
                content = await page.content()
                if 'Log in' in content or 'Sign in' in content:
                    print("⚠️ 检测到登录提示，Cookie 可能已失效")
                elif 'Something went wrong' in content:
                    print("⚠️ Twitter 显示错误页面（可能是反爬）")
                else:
                    print("⚠️ 可能是页面加载问题或反爬机制")
            
        except Exception as e:
            print(f"❌ 错误: {e}")
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_twitter())
