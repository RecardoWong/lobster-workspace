#!/usr/bin/env python3
"""
Twitter Cookie 监控 - Playwright 版
轻量级，只验证登录状态
"""

import os
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

AUTH_TOKEN = os.getenv('TWITTER_AUTH_TOKEN', '5da5c73c3286e0c825c5a337eb60ffaf93f2620c')
CT0 = os.getenv('TWITTER_CT0', 'bb867bfa8ae5a410dec9e6537f8aa4f183c43b65c641f9b293a171e8eb8b1b9df359891c89b0e181f4c21bb6e292f422075b77ac3f51a0915fc5e82e2c69c9c5100c14355137082faa36804f10f18ebd')

async def check_twitter_login():
    """验证 Twitter Cookie 登录状态"""
    print(f"🐦 Twitter Cookie 验证 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-gpu']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        # 添加 cookie
        await context.add_cookies([
            {
                'name': 'auth_token',
                'value': AUTH_TOKEN,
                'domain': '.x.com',
                'path': '/'
            },
            {
                'name': 'ct0',
                'value': CT0,
                'domain': '.x.com',
                'path': '/'
            }
        ])
        
        page = await context.new_page()
        
        try:
            # 访问 Twitter
            await page.goto('https://x.com/home', timeout=30000)
            await asyncio.sleep(3)
            
            # 检查是否登录成功
            if 'home' in page.url:
                print('✅ Cookie 登录成功!')
                
                # 获取用户名
                try:
                    user_elem = await page.wait_for_selector('[data-testid="AppTabBar_Profile_Link"]', timeout=5000)
                    if user_elem:
                        print('✅ 用户已识别')
                except:
                    pass
                
                # 截图验证
                await page.screenshot(path='/tmp/twitter_login_check.png')
                print('✅ 截图已保存: /tmp/twitter_login_check.png')
                
            else:
                print(f'⚠️  当前页面: {page.url}')
                print('❌ Cookie 可能已过期')
                
        except Exception as e:
            print(f'❌ 错误: {str(e)[:100]}')
            
        finally:
            await browser.close()
            print("=" * 60)

if __name__ == '__main__':
    asyncio.run(check_twitter_login())
