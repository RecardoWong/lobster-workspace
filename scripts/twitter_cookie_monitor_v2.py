#!/usr/bin/env python3
"""
Twitter Cookie 监控 - Playwright 完整版
定时抓取指定用户推文
"""

import os
import json
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
from pathlib import Path

# Cookie 配置
AUTH_TOKEN = os.getenv('TWITTER_AUTH_TOKEN', '5da5c73c3286e0c825c5a337eb60ffaf93f2620c')
CT0 = os.getenv('TWITTER_CT0', 'bb867bfa8ae5a410dec9e6537f8aa4f183c43b65c641f9b293a171e8eb8b1b9df359891c89b0e181f4c21bb6e292f422075b77ac3f51a0915fc5e82e2c69c9c5100c14355137082faa36804f10f18ebd')

# 监控账号
MONITOR_ACCOUNTS = {
    'elonmusk': 'Elon Musk',
    'jdhasoptions': 'jdhasoptions',
    'xiaomucrypto': 'xiaomucrypto',
    'aistocksavvy': 'AI Stock Savvy',
    'QQ_Timmy': 'QQ_Timmy'
}

SAVE_DIR = '/tmp/twitter_monitor'
os.makedirs(SAVE_DIR, exist_ok=True)

async def fetch_user_tweets(username, name):
    """抓取指定用户的推文"""
    print(f"\n📱 抓取 @{username} ({name})...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-gpu']
        )
        
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        
        # 添加 cookie
        await context.add_cookies([
            {'name': 'auth_token', 'value': AUTH_TOKEN, 'domain': '.x.com', 'path': '/'},
            {'name': 'ct0', 'value': CT0, 'domain': '.x.com', 'path': '/'}
        ])
        
        page = await context.new_page()
        
        try:
            # 访问用户主页
            await page.goto(f'https://x.com/{username}', timeout=30000)
            await asyncio.sleep(5)  # 等待加载
            
            tweets_data = []
            
            # 获取推文
            tweets = await page.query_selector_all('[data-testid="tweet"]')
            print(f"   找到 {len(tweets)} 条推文")
            
            for i, tweet in enumerate(tweets[:5], 1):  # 只取前5条
                try:
                    # 推文文本
                    text_elem = await tweet.query_selector('[data-testid="tweetText"]')
                    text = await text_elem.inner_text() if text_elem else ''
                    
                    # 时间
                    time_elem = await tweet.query_selector('time')
                    time_str = await time_elem.get_attribute('datetime') if time_elem else ''
                    
                    # 获取推文ID和URL
                    tweet_id = ''
                    tweet_url = f'https://x.com/{username}'
                    
                    # 尝试从time元素的父链接获取推文ID
                    if time_elem:
                        try:
                            parent_link = await time_elem.evaluate('el => el.closest("a")?.getAttribute("href")')
                            if parent_link and '/status/' in parent_link:
                                tweet_id = parent_link.split('/status/')[-1].split('?')[0]
                                tweet_url = f'https://x.com/{username}/status/{tweet_id}'
                        except:
                            pass
                    
                    # 作者
                    author_elem = await tweet.query_selector('[data-testid="User-Names"]')
                    author = await author_elem.inner_text() if author_elem else username
                    
                    if text:
                        tweets_data.append({
                            'author': author.split('\n')[0] if '\n' in author else author,
                            'text': text[:300],  # 限制长度
                            'time': time_str,
                            'id': tweet_id,
                            'url': tweet_url,
                            'fetched_at': datetime.now().isoformat()
                        })
                        print(f"   {i}. {text[:60]}...")
                        print(f"      🔗 {tweet_url}")
                        
                except Exception as e:
                    continue
            
            # 保存数据
            save_file = f'{SAVE_DIR}/{username}_{datetime.now().strftime("%Y%m%d_%H%M")}.json'
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'username': username,
                    'name': name,
                    'fetch_time': datetime.now().isoformat(),
                    'tweets': tweets_data
                }, f, ensure_ascii=False, indent=2)
            
            print(f"   ✅ 已保存到 {save_file}")
            return tweets_data
            
        except Exception as e:
            print(f"   ❌ 抓取失败: {str(e)[:80]}")
            return []
            
        finally:
            await browser.close()

async def main():
    """主函数"""
    print(f"🐦 Twitter Cookie 监控 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    all_tweets = {}
    
    for username, name in MONITOR_ACCOUNTS.items():
        tweets = await fetch_user_tweets(username, name)
        all_tweets[username] = tweets
        await asyncio.sleep(2)  # 避免请求过快
    
    # 保存汇总
    summary_file = f'{SAVE_DIR}/summary_{datetime.now().strftime("%Y%m%d_%H%M")}.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(all_tweets, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 监控完成！汇总保存到 {summary_file}")
    print("=" * 60)

if __name__ == '__main__':
    asyncio.run(main())
