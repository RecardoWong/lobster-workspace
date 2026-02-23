#!/usr/bin/env python3
"""
Twitter 每小时推送 + 自动记录
抓取4个账号的最新推文，翻译后推送到Telegram，并记录到文档
"""

import os
import sys
import json
import asyncio
import subprocess
from datetime import datetime, timezone, timedelta
from playwright.async_api import async_playwright

# 配置
MONITOR_ACCOUNTS = {
    'elonmusk': 'Elon Musk',
    'jdhasoptions': 'jdhasoptions',
    'xiaomucrypto': 'xiaomucrypto',
    'aistocksavvy': 'AI Stock Savvy',
    'BlueJay87476298': 'BlueJay'
}

SAVE_DIR = '/tmp/twitter_monitor'
LOG_DIR = '/root/.openclaw/workspace/memory/twitter_logs'
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

AUTH_TOKEN = os.getenv('TWITTER_AUTH_TOKEN', '5da5c73c3286e0c825c5a337eb60ffaf93f2620c')
CT0 = os.getenv('TWITTER_CT0', 'bb867bfa8ae5a410dec9e6537f8aa4f183c43b65c641f9b293a171e8eb8b1b9df359891c89b0e181f4c21bb6e292f422075b77ac3f51a0915fc5e82e2c69c9c5100c14355137082faa36804f10f18ebd')

def translate_text(text):
    """翻译文本：英文→中文，使用MyMemory免费API"""
    if not text:
        return ""
    
    # 如果已经有中文，直接返回
    if any('\u4e00' <= char <= '\u9fff' for char in text[:100]):
        return text
    
    # 使用MyMemory免费翻译API
    try:
        import urllib.request
        import urllib.parse
        
        # MyMemory免费API
        encoded_text = urllib.parse.quote(text[:500])
        url = f"https://api.mymemory.translated.net/get?q={encoded_text}&langpair=en|zh"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            translated = result.get('responseData', {}).get('translatedText', '')
            
            # 检查翻译质量（如果返回的是原文或错误，返回简化版）
            if translated and translated.lower() != text.lower()[:100]:
                return translated[:200] + "..." if len(translated) > 200 else translated
    except Exception as e:
        print(f"  翻译API失败: {e}")
    
    # 回退：返回原文+提示
    return text[:150] + "...[待翻译]" if len(text) > 150 else text + "[待翻译]"

def get_time_ago(time_str):
    """计算相对时间"""
    try:
        tweet_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        diff = now - tweet_time
        if diff.days > 0:
            return f"{diff.days}天前"
        hours = diff.seconds // 3600
        if hours > 0:
            return f"{hours}小时前"
        minutes = (diff.seconds % 3600) // 60
        return f"{minutes}分钟前"
    except:
        return "未知"

def save_to_daily_log(tweets):
    """保存到每日Markdown日志"""
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = f"{LOG_DIR}/{today}.md"
    
    now = datetime.now().strftime('%H:%M')
    
    # 如果文件不存在，创建表头
    if not os.path.exists(log_file):
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"# Twitter 抓取记录 - {today}\n\n")
            f.write(f"监控账号: elonmusk, jdhasoptions, xiaomucrypto, aistocksavvy\n\n")
            f.write("---\n\n")
    
    # 追加本次抓取记录
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"## [{now}] 第{len(tweets)}条新推文\n\n")
        for t in tweets:
            f.write(f"### {t['name']} (@{t['author']})\n")
            f.write(f"- 时间: {t['time']} ({t['time_ago']})\n")
            f.write(f"- 原文: {t['text']}\n")
            f.write(f"- 翻译: {t['translate']}\n")
            f.write(f"- 链接: {t['url']}\n\n")
        f.write("---\n\n")
    
    print(f"✅ 已记录到 {log_file}")

def save_to_json(tweets):
    """保存到JSON供复盘使用"""
    today = datetime.now().strftime('%Y%m%d')
    json_file = f"{SAVE_DIR}/daily_{today}.json"
    
    existing = []
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except:
            pass
    
    # 去重合并
    seen_keys = {f"{t['author']}:{t['time']}" for t in existing}
    for t in tweets:
        key = f"{t['author']}:{t['time']}"
        if key not in seen_keys:
            existing.append(t)
            seen_keys.add(key)
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    return existing

async def fetch_user_tweets(username, name):
    """抓取单个用户的最新推文"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        
        await context.add_cookies([
            {'name': 'auth_token', 'value': AUTH_TOKEN, 'domain': '.x.com', 'path': '/'},
            {'name': 'ct0', 'value': CT0, 'domain': '.x.com', 'path': '/'}
        ])
        
        page = await context.new_page()
        
        try:
            await page.goto(f'https://x.com/{username}', timeout=30000)
            await asyncio.sleep(5)
            
            tweets_data = []
            tweets = await page.query_selector_all('[data-testid="tweet"]')
            
            for tweet in tweets[:3]:  # 只取前3条
                try:
                    text_elem = await tweet.query_selector('[data-testid="tweetText"]')
                    text = await text_elem.inner_text() if text_elem else ''
                    
                    time_elem = await tweet.query_selector('time')
                    time_str = await time_elem.get_attribute('datetime') if time_elem else ''
                    
                    # 只保留6小时内的新推文
                    try:
                        tweet_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                        age_hours = (datetime.now(timezone.utc) - tweet_time).total_seconds() / 3600
                        if age_hours > 6:
                            continue
                    except:
                        pass
                    
                    tweets_data.append({
                        'author': username,
                        'name': name,
                        'text': text,
                        'translate': translate_text(text),
                        'time': time_str,
                        'time_ago': get_time_ago(time_str),
                        'url': f'https://x.com/{username}',
                        'captured_at': datetime.now().isoformat()
                    })
                except:
                    continue
            
            await browser.close()
            return tweets_data
            
        except Exception as e:
            await browser.close()
            return []

async def fetch_all():
    """抓取所有账号"""
    all_new_tweets = []
    
    for username, name in MONITOR_ACCOUNTS.items():
        tweets = await fetch_user_tweets(username, name)
        all_new_tweets.extend(tweets)
    
    return all_new_tweets

def format_push_message(tweets):
    """格式化推送消息"""
    if not tweets:
        return None
    
    lines = [
        "🐦 Twitter 更新",
        f"📅 {datetime.now().strftime('%H:%M')}",
        "=" * 30,
        ""
    ]
    
    for t in tweets[:5]:
        lines.extend([
            f"👤 {t['name']} @{t['author']}",
            f"⏰ {t['time_ago']}",
            f"💬 {t['text'][:150]}...",
            f"📝 {t['translate'][:100]}..." if len(t['translate']) > 100 else f"📝 {t['translate']}",
            ""
        ])
    
    lines.append("=" * 30)
    return "\n".join(lines)

def send_to_telegram(message):
    """发送到Telegram"""
    try:
        cmd = ['openclaw', 'message', 'send', '--channel', 'telegram', '--target', '5440939697', '--message', message]
        subprocess.run(cmd, capture_output=True, timeout=30)
        return True
    except:
        return False

async def main():
    print(f"[{datetime.now().strftime('%H:%M')}] 开始抓取Twitter...")
    
    tweets = await fetch_all()
    
    if tweets:
        # 1. 保存到Markdown日志
        save_to_daily_log(tweets)
        
        # 2. 保存到JSON
        all_today = save_to_json(tweets)
        
        # 3. 推送消息
        message = format_push_message(tweets)
        if message:
            print(f"发现 {len(tweets)} 条新推文，正在推送...")
            send_to_telegram(message)
        
        print(f"✅ 今日累计: {len(all_today)} 条")
    else:
        print("没有新推文")

if __name__ == '__main__':
    asyncio.run(main())
