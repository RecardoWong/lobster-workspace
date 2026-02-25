#!/usr/bin/env python3
"""
Twitter 推送 - 修复版
简单直接，确保推送成功
"""

import os
import sys
import json
import asyncio
import subprocess
from datetime import datetime
from playwright.async_api import async_playwright

# 设置环境
os.environ['PATH'] = '/root/.nvm/versions/node/v22.22.0/bin:' + os.environ.get('PATH', '')

AUTH_TOKEN = os.getenv('TWITTER_AUTH_TOKEN')
CT0 = os.getenv('TWITTER_CT0')
TELEGRAM_CHAT_ID = "5440939697"

MONITOR_ACCOUNTS = {
    'elonmusk': 'Elon Musk',
    'jdhasoptions': 'jdhasoptions',
    'xiaomucrypto': 'xiaomucrypto',
    'aistocksavvy': 'AI Stock Savvy',
    'BlueJay87476298': 'BlueJay',
    'QQ_Timmy': 'QQ_Timmy'
}

async def fetch_all():
    """抓取所有账号"""
    all_tweets = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        
        for username, name in MONITOR_ACCOUNTS.items():
            try:
                context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
                await context.add_cookies([
                    {'name': 'auth_token', 'value': AUTH_TOKEN, 'domain': '.x.com', 'path': '/'},
                    {'name': 'ct0', 'value': CT0, 'domain': '.x.com', 'path': '/'}
                ])
                
                page = await context.new_page()
                await page.goto(f'https://x.com/{username}', timeout=30000)
                await asyncio.sleep(3)
                
                tweets = await page.locator('article[data-testid="tweet"]').count()
                
                for i in range(min(tweets, 2)):  # 只取前2条
                    try:
                        tweet = await page.locator('article[data-testid="tweet"]').nth(i)
                        text_elem = await tweet.query_selector('[data-testid="tweetText"]')
                        text = await text_elem.inner_text() if text_elem else ''
                        
                        time_elem = await tweet.query_selector('time')
                        time_str = await time_elem.get_attribute('datetime') if time_elem else ''
                        
                        all_tweets.append({
                            'author': username,
                            'name': name,
                            'text': text[:100] if len(text) > 100 else text,
                            'time': time_str
                        })
                    except:
                        pass
                
                await context.close()
            except Exception as e:
                print(f"  抓取 {username} 失败: {e}")
        
        await browser.close()
    
    return all_tweets

def send_to_telegram_sync(message):
    """同步发送"""
    try:
        cmd = [
            '/root/.nvm/versions/node/v22.22.0/bin/openclaw',
            'message', 'send',
            '--channel', 'telegram',
            '--target', TELEGRAM_CHAT_ID,
            '--message', message
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        print(f"  推送失败: {e}")
        return False

async def main():
    print(f"[{datetime.now().strftime('%H:%M')}] 开始...")
    
    tweets = await fetch_all()
    
    if not tweets:
        print("没有推文")
        return
    
    print(f"发现 {len(tweets)} 条推文")
    
    # 格式化消息
    lines = ["🐦 Twitter 更新", f"📅 {datetime.now().strftime('%H:%M')}", ""]
    
    for t in tweets:
        lines.append(f"👤 {t['name']}")
        lines.append(f"💬 {t['text']}")
        lines.append(f"🔗 https://x.com/{t['author']}")
        lines.append("")
    
    message = "\n".join(lines)[:3500]  # 限制长度
    
    # 推送
    print(f"推送 {len(tweets)} 条...")
    if send_to_telegram_sync(message):
        print("✅ 推送成功")
    else:
        print("❌ 推送失败")

if __name__ == '__main__':
    asyncio.run(main())
