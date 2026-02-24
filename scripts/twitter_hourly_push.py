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
PUSHED_DIR = '/root/.openclaw/workspace/memory/twitter_pushed'  # 已推送记录
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(PUSHED_DIR, exist_ok=True)

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

def get_pushed_tweet_ids():
    """获取已推送的推文ID列表（最近7天）"""
    pushed_ids = set()
    
    # 检查最近7天的记录文件
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        pushed_file = f"{PUSHED_DIR}/{date}.json"
        
        if os.path.exists(pushed_file):
            try:
                with open(pushed_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    pushed_ids.update(data.get('tweet_ids', []))
            except:
                pass
    
    return pushed_ids

def record_pushed_tweets(tweets):
    """记录已推送的推文ID"""
    today = datetime.now().strftime('%Y-%m-%d')
    pushed_file = f"{PUSHED_DIR}/{today}.json"
    
    # 读取现有记录
    existing_ids = set()
    if os.path.exists(pushed_file):
        try:
            with open(pushed_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                existing_ids = set(data.get('tweet_ids', []))
        except:
            pass
    
    # 添加新推送的tweet_id
    for t in tweets:
        tweet_id = t.get('tweet_id', '')
        if tweet_id:
            existing_ids.add(tweet_id)
    
    # 保存
    with open(pushed_file, 'w', encoding='utf-8') as f:
        json.dump({
            'date': today,
            'tweet_ids': list(existing_ids),
            'count': len(existing_ids)
        }, f, ensure_ascii=False, indent=2)

def filter_already_pushed(tweets):
    """过滤掉已经推送过的推文"""
    pushed_ids = get_pushed_tweet_ids()
    
    new_tweets = []
    skipped = 0
    
    for t in tweets:
        tweet_id = t.get('tweet_id', '')
        # 如果没有tweet_id，用author+time组合作为唯一标识
        unique_key = tweet_id if tweet_id else f"{t.get('author')}:{t.get('time')}"
        
        if tweet_id and tweet_id in pushed_ids:
            skipped += 1
            continue
        
        new_tweets.append(t)
    
    if skipped > 0:
        print(f"  跳过 {skipped} 条已推送过的推文")
    
    return new_tweets
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
            f.write(f"- 🔗 [点击打开推文]({t['url']})\n\n")
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
                    
                    # 尝试获取推文ID
                    tweet_id = ''
                    try:
                        # 从推文元素的链接中提取ID
                        link_elem = await tweet.query_selector('a[href*="/status/"]')
                        if link_elem:
                            href = await link_elem.get_attribute('href')
                            if href and '/status/' in href:
                                tweet_id = href.split('/status/')[-1].split('?')[0]
                    except:
                        pass
                    
                    # 构建完整推文链接
                    if tweet_id:
                        tweet_url = f'https://x.com/{username}/status/{tweet_id}'
                    else:
                        tweet_url = f'https://x.com/{username}'
                    
                    tweets_data.append({
                        'author': username,
                        'name': name,
                        'text': text,
                        'translate': translate_text(text),
                        'time': time_str,
                        'time_ago': get_time_ago(time_str),
                        'tweet_id': tweet_id,
                        'url': tweet_url,
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

def filter_important_tweets(tweets):
    """
    筛选重要推文
    只返回我判断值得推送的内容
    """
    important_keywords = [
        'AI', 'artificial intelligence', 'artificialintelligence',
        '芯片', 'chip', 'semiconductor', '半导体',
        '特斯拉', 'Tesla', 'TSLA',
        '自动驾驶', 'autopilot', 'FSD', 'self-driving',
        '英伟达', 'NVIDIA', 'NVDA',
        '英诺赛科', 'Innoscience',
        'CoWoS', '封装', '先进封装',
        '美联储', 'Fed', 'Fed ', '利率', 'rate ', 'inflation', 'CPI',
        '比特币', 'BTC', 'bitcoin', '加密货币', 'crypto',
        '财报', 'earnings', '业绩', 'revenue', 'profit',
        '机器人', 'robot', '机器人', 'robotics',
        '大模型', 'LLM', 'GPT', 'ChatGPT',
        '数据中心', 'data center', 'datacenter',
        '新能源', 'EV', 'electric vehicle',
        'SpaceX', '星舰', 'Starship',
        '脑机接口', 'Neuralink',
        '推特', 'Twitter', 'X ', 'x.com',
        'OpenAI', 'ChatGPT', 'Claude',
        'Grok', 'xAI',
        'vision', '视频生成', 'video generation',
    ]
    
    important_accounts = ['elonmusk', 'BlueJay87476298']  # 这些账号的内容更重要
    
    filtered = []
    for t in tweets:
        text = t.get('text', '').lower()
        author = t.get('author', '').lower()
        
        # 规则1: 重要账号的内容（降低门槛）
        if author in ['elonmusk', 'bluejay87476298']:
            # 即使重要账号，也过滤掉太水的内容
            if len(t.get('text', '')) > 20:  # 至少20个字符
                filtered.append(t)
                continue
        
        # 规则2: 包含关键词
        for keyword in important_keywords:
            if keyword.lower() in text:
                filtered.append(t)
                break
    
    return filtered

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
        # 添加可点击的推文链接
        tweet_link = t.get('url', f"https://x.com/{t['author']}")
        lines.extend([
            f"👤 {t['name']} @{t['author']}",
            f"⏰ {t['time_ago']}",
            f"💬 {t['text'][:150]}...",
            f"📝 {t['translate'][:100]}..." if len(t['translate']) > 100 else f"📝 {t['translate']}",
            f"🔗 {tweet_link}",
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
        # 0. 先过滤掉已经推送过的（关键！防止重复推送）
        new_tweets = filter_already_pushed(tweets)
        
        if not new_tweets:
            print(f"发现 {len(tweets)} 条推文，但全部已推送过，跳过")
            return
        
        print(f"发现 {len(tweets)} 条推文，其中 {len(new_tweets)} 条是新推文")
        
        # 1. 筛选重要推文（只推送这些）
        important_tweets = filter_important_tweets(new_tweets)
        
        # 2. 保存所有到Markdown日志（记录用）
        save_to_daily_log(new_tweets)
        
        # 3. 保存所有到JSON（记录用）
        all_today = save_to_json(new_tweets)
        
        # 4. 只推送重要的
        if important_tweets:
            message = format_push_message(important_tweets)
            if message:
                print(f"推送 {len(important_tweets)} 条重要推文...")
                send_to_telegram(message)
                # 5. 记录已推送的推文（关键！防止下次重复）
                record_pushed_tweets(important_tweets)
        else:
            print(f"新推文中没有重要内容，跳过推送")
            # 即使没有重要内容，也记录已查看，防止下次重复抓取
            record_pushed_tweets(new_tweets)
    else:
        print("没有新推文")

if __name__ == '__main__':
    asyncio.run(main())
