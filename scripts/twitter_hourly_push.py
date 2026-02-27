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
    'BlueJay87476298': 'BlueJay',
    'QQ_Timmy': 'QQ_Timmy',
    'jukan05': 'jukan05'
}

SAVE_DIR = '/tmp/twitter_monitor'
LOG_DIR = '/root/.openclaw/workspace/memory/twitter_logs'
PUSHED_DIR = '/root/.openclaw/workspace/memory/twitter_pushed'  # 已推送记录
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(PUSHED_DIR, exist_ok=True)

AUTH_TOKEN = os.getenv('TWITTER_AUTH_TOKEN', '5da5c73c3286e0c825c5a337eb60ffaf93f2620c')
CT0 = os.getenv('TWITTER_CT0', 'bb867bfa8ae5a410dec9e6537f8aa4f183c43b65c641f9b293a171e8eb8b1b9df359891c89b0e181f4c21bb6e292f422075b77ac3f51a0915fc5e82e2c69c9c5100c14355137082faa36804f10f18ebd')

# 初始化繁简转换器
try:
    import opencc
    _t2s_converter = opencc.OpenCC('t2s')  # 繁体转简体
except:
    _t2s_converter = None

def convert_to_simplified(text):
    """繁体中文转简体中文"""
    if not text:
        return text
    if _t2s_converter:
        return _t2s_converter.convert(text)
    return text

def translate_text(text):
    """翻译文本：英文→简体中文，繁体→简体"""
    if not text:
        return ""
    
    # 先检查是否有繁体中文，有则转换为简体
    text = convert_to_simplified(text)
    
    # 如果已经有中文（简体），直接返回
    if any('\u4e00' <= char <= '\u9fff' for char in text[:100]):
        return text
    
    # 使用Google Translate免费API（英文→简体中文）
    try:
        import urllib.request
        import urllib.parse
        
        encoded_text = urllib.parse.quote(text[:500])
        # Google Translate免费API (client=gtx是Google Translate扩展的客户端标识)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q={encoded_text}"
        
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            # Google Translate返回格式: [[["翻译结果","原文",...]],...]
            if result and len(result) > 0 and len(result[0]) > 0:
                translated = result[0][0][0]
                
                # 确保翻译结果是简体中文（再次转换以防万一）
                translated = convert_to_simplified(translated)
                
                # 检查翻译质量
                if translated and translated.lower() != text.lower()[:100]:
                    return translated[:200] + "..." if len(translated) > 200 else translated
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print(f"  Google翻译API限流(429)，稍后重试")
        else:
            print(f"  Google翻译API错误: HTTP {e.code}")
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
    """获取已推送的推文ID列表（最近24小时）- 扩展为包含内容指纹"""
    pushed_ids = set()
    
    # 检查最近2天的记录文件（避免重复）
    for i in range(2):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        pushed_file = f"{PUSHED_DIR}/{date}.json"
        
        if os.path.exists(pushed_file):
            try:
                with open(pushed_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 读取tweet_ids
                    pushed_ids.update(data.get('tweet_ids', []))
                    # 读取内容指纹（text-based keys）
                    pushed_ids.update(data.get('content_keys', []))
            except:
                pass
    
    return pushed_ids

def record_pushed_tweets(tweets):
    """记录已推送的推文ID和内容指纹"""
    today = datetime.now().strftime('%Y-%m-%d')
    pushed_file = f"{PUSHED_DIR}/{today}.json"
    
    # 读取现有记录
    existing_ids = set()
    existing_content_keys = set()
    if os.path.exists(pushed_file):
        try:
            with open(pushed_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                existing_ids = set(data.get('tweet_ids', []))
                existing_content_keys = set(data.get('content_keys', []))
        except:
            pass
    
    # 添加新推送的tweet_id和内容指纹
    for t in tweets:
        tweet_id = t.get('tweet_id', '')
        text = t.get('text', '')
        author = t.get('author', '')
        
        if tweet_id:
            existing_ids.add(tweet_id)
        
        # 同时保存内容指纹（用于无tweet_id时的去重）
        if text and author:
            content_key = f"{author}:{text[:50]}"
            existing_content_keys.add(content_key)
    
    # 保存
    with open(pushed_file, 'w', encoding='utf-8') as f:
        json.dump({
            'date': today,
            'tweet_ids': list(existing_ids),
            'content_keys': list(existing_content_keys),
            'count': len(existing_ids) + len(existing_content_keys)
        }, f, ensure_ascii=False, indent=2)

def filter_already_pushed(tweets):
    """过滤掉已经推送过的推文 - 严格去重"""
    pushed_ids = get_pushed_tweet_ids()
    
    new_tweets = []
    skipped = 0
    
    for t in tweets:
        tweet_id = t.get('tweet_id', '')
        text = t.get('text', '')
        author = t.get('author', '')
        
        # 检查1: 有tweet_id且已推送
        if tweet_id and tweet_id in pushed_ids:
            skipped += 1
            continue
        
        # 检查2: 用text+author作为唯一标识（防止tweet_id为空时重复）
        content_key = f"{author}:{text[:50]}"
        if content_key in pushed_ids:
            skipped += 1
            continue
        
        new_tweets.append(t)
    
    if skipped > 0:
        print(f"  跳过 {skipped} 条已推送过的推文")
    
    return new_tweets

def save_to_daily_log(tweets):
    """保存到每日Markdown日志 - 美化版"""
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = f"{LOG_DIR}/{today}.md"
    
    now = datetime.now().strftime('%H:%M')
    
    # 如果文件不存在，创建表头
    if not os.path.exists(log_file):
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"# 🐦 Twitter 抓取记录 - {today}\n\n")
            f.write("📊 监控账号: Elon Musk · jdhasoptions · xiaomucrypto · AI Stock Savvy · BlueJay · QQ_Timmy\n\n")
            f.write("---\n\n")
    
    # 按账号分组
    tweets_by_author = {}
    for t in tweets:
        author = t.get('author', 'unknown')
        if author not in tweets_by_author:
            tweets_by_author[author] = []
        tweets_by_author[author].append(t)
    
    # 追加本次抓取记录
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n## 📅 {now} 更新 · {len(tweets)} 条新推文\n\n")
        
        for author, author_tweets in tweets_by_author.items():
            name = author_tweets[0].get('name', author)
            f.write(f"### 👤 {name} `@{author}`\n\n")
            
            for i, t in enumerate(author_tweets, 1):
                time_display = t.get('time_ago', t.get('time', '未知'))
                text = t.get('text', '')
                translate = t.get('translate', '')
                url = t.get('url', f'https://x.com/{author}')
                
                f.write(f"**{i}.** [{time_display}]({url})\n")
                f.write(f"> 📝 {text}\n")
                if translate and translate != text:
                    f.write(f"> 🈯 {translate}\n")
                f.write("\n")
            
            f.write("\n")
        
        f.write("---\n")
    
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
    # 设置环境变量避免EPIPE错误
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '0'
    os.environ['PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD'] = '0'
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(
                headless=True, 
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
        except Exception as e:
            print(f"[警告] 启动浏览器失败: {e}")
            print("[提示] 尝试重新安装Playwright浏览器...")
            # 如果启动失败，返回空数据
            return []
        
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
                    # 1. 先获取初始文本
                    text_elem = await tweet.query_selector('[data-testid="tweetText"]')
                    text = await text_elem.inner_text() if text_elem else ''
                    
                    # 2. 检查是否有"显示更多"按钮，有则点击
                    try:
                        # Twitter/X 的"显示更多"按钮通常是展开被截断的推文
                        # 尝试查找并点击
                        show_more_selectors = [
                            'button:has-text("显示更多")',
                            'button:has-text("Show more")',
                            '[role="button"]:has-text("显示更多")',
                            'button[aria-expanded="false"]',
                            'a[href="#"]:has-text("...")'
                        ]
                        
                        for selector in show_more_selectors:
                            try:
                                show_more_btn = await tweet.query_selector(selector)
                                if show_more_btn:
                                    # 检查按钮是否可见
                                    is_visible = await show_more_btn.is_visible()
                                    if is_visible:
                                        print(f"  发现'显示更多'按钮，正在点击...")
                                        await show_more_btn.click()
                                        await asyncio.sleep(1)  # 等待内容展开
                                        # 重新获取完整文本
                                        text_elem = await tweet.query_selector('[data-testid="tweetText"]')
                                        text = await text_elem.inner_text() if text_elem else text
                                        print(f"  已获取完整内容 ({len(text)}字符)")
                                        break
                            except:
                                continue
                    except Exception as e:
                        print(f"  展开完整推文失败: {e}")
                    
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

async def fetch_user_tweets_optimized(page, username, name):
    """在已有页面上下文中抓取单个用户的最新推文"""
    try:
        await page.goto(f'https://x.com/{username}', timeout=30000)
        await asyncio.sleep(3)  # 减少等待时间
        
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
        
        return tweets_data
        
    except Exception as e:
        print(f"  [错误] 抓取 @{username} 失败: {e}")
        return []

async def fetch_all():
    """抓取所有账号 - 使用单一浏览器实例优化"""
    all_new_tweets = []
    
    # 设置环境变量
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '0'
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(
                headless=True, 
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
        except Exception as e:
            print(f"[错误] 启动浏览器失败: {e}")
            return []
        
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        
        await context.add_cookies([
            {'name': 'auth_token', 'value': AUTH_TOKEN, 'domain': '.x.com', 'path': '/'},
            {'name': 'ct0', 'value': CT0, 'domain': '.x.com', 'path': '/'}
        ])
        
        page = await context.new_page()
        
        # 依次抓取所有账号
        for username, name in MONITOR_ACCOUNTS.items():
            print(f"  正在抓取 @{username}...")
            tweets = await fetch_user_tweets_optimized(page, username, name)
            all_new_tweets.extend(tweets)
            if tweets:
                print(f"    ✓ 获取 {len(tweets)} 条推文")
        
        await browser.close()
    
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

def classify_tweet(text):
    """智能分类推文类型"""
    text_lower = text.lower()
    
    # 分类规则
    if any(k in text_lower for k in ['fed', 'fomc', 'cpi', 'ppi', '通胀', '利率', '降息', ' Powell']):
        return "📊 宏观"
    if any(k in text_lower for k in ['$tsla', 'tesla', '特斯拉', '马斯克']):
        return "🚗 特斯拉"
    if any(k in text_lower for k in ['$nvda', 'nvidia', '英伟达', '财报', 'earnings']):
        return "💰 财报"
    if any(k in text_lower for k in ['ai', '芯片', '半导体', '$amd', '$intc']):
        return "🤖 AI/芯片"
    if any(k in text_lower for k in ['存储', '海力士', '三星', 'hbm', 'memory']):
        return "💾 存储"
    if any(k in text_lower for k in ['btc', 'bitcoin', 'eth', 'crypto', '加密货币']):
        return "₿ 加密"
    
    return "📰 资讯"

def extract_tickers(text):
    """提取股票代码"""
    import re
    tickers = re.findall(r'\$[A-Z]{1,5}', text.upper())
    return list(set(tickers))[:3]  # 最多3个

def extract_key_point(text):
    """提取核心观点（一句话）- 保留更多内容"""
    # 清理文本
    text = text.replace('\n', ' ').strip()
    
    # 优先找有数字/百分比的句子（通常是要点）
    import re
    sentences = re.split(r'[。！.!?]', text)
    
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        # 包含数字/金额/百分比的优先
        if re.search(r'\d+%|\$\d+|\d+亿|\d+万|\d+倍| billion| million', s, re.IGNORECASE):
            if len(s) > 10:
                return s[:280] + "…" if len(s) > 280 else s
    
    # 其次找包含股票代码的句子
    for s in sentences:
        s = s.strip()
        if re.search(r'\$[A-Z]{1,5}', s) and len(s) > 15:
            return s[:280] + "…" if len(s) > 280 else s
    
    # 否则返回最长的一句（通常信息最多）
    longest = max([s.strip() for s in sentences if s.strip()], key=len, default=text)
    return longest[:350] + "…" if len(longest) > 350 else longest

def format_push_message(tweets):
    """格式化推送消息 - 一眼get重点版"""
    if not tweets:
        return None
    
    lines = [
        f"🐦 Twitter {datetime.now().strftime('%H:%M')}",
        ""
    ]
    
    # 最多显示5条，按重要性排序
    for i, t in enumerate(tweets[:5], 1):
        text = t.get('text', '')
        translate = t.get('translate', '') or text
        author = t.get('author', 'unknown')
        name = t.get('name', author)
        time_ago = t.get('time_ago', '')
        tweet_link = t.get('url', f"https://x.com/{author}")
        
        # 用中文内容分析（优先翻译）
        content_for_analysis = translate if translate and translate != text else text
        
        # 1. 分类标签
        tag = classify_tweet(content_for_analysis)
        
        # 2. 股票代码
        tickers = extract_tickers(text)
        ticker_str = " ".join(tickers) if tickers else ""
        
        # 3. 核心观点
        key_point = extract_key_point(content_for_analysis)
        
        # 格式化输出
        lines.append(f"{tag} {'|' if ticker_str else ''} {ticker_str}")
        lines.append(f"💡 {key_point}")
        lines.append(f"↳ {name} · [{time_ago}]({tweet_link}) · [查看完整推文]({tweet_link})")
        lines.append("")
    
    # 如果有更多
    if len(tweets) > 5:
        lines.append(f"_…还有 {len(tweets) - 5} 条_")
    
    message = "\n".join(lines)
    if len(message) > 3800:
        message = message[:3800] + "\n…"
    
    return message

def send_to_telegram(message):
    """发送到Telegram"""
    try:
        # 设置环境变量
        env = os.environ.copy()
        env['PATH'] = '/root/.nvm/versions/node/v22.22.0/bin:' + env.get('PATH', '')
        
        cmd = ['/root/.nvm/versions/node/v22.22.0/bin/openclaw', 'message', 'send', '--channel', 'telegram', '--target', '5440939697', '--message', message]
        result = subprocess.run(cmd, capture_output=True, timeout=30, env=env)
        if result.returncode == 0:
            print(f"  ✅ Telegram 推送成功")
        else:
            err = result.stderr.decode()[:100] if result.stderr else '未知错误'
            print(f"  ⚠️ Telegram 推送失败: {err}")
        return result.returncode == 0
    except Exception as e:
        print(f"  ❌ Telegram 推送异常: {e}")
        return False

async def main():
    print(f"[{datetime.now().strftime('%H:%M')}] 开始抓取Twitter...")
    
    tweets = await fetch_all()
    
    if tweets:
        # 0. 过滤空推文
        valid_tweets = [t for t in tweets if t.get('text')]
        
        if not valid_tweets:
            print(f"发现 {len(tweets)} 条推文，但全部为空，跳过")
            return
        
        # 1. 去重 - 过滤已推送的推文（关键修复！）
        new_tweets = filter_already_pushed(valid_tweets)
        
        if not new_tweets:
            print(f"发现 {len(valid_tweets)} 条推文，但全部已推送过，跳过")
            return
        
        print(f"发现 {len(tweets)} 条推文，其中 {len(new_tweets)} 条是真正的新推文")
        
        # 2. 保存所有到Markdown日志（记录用）
        save_to_daily_log(valid_tweets)
        
        # 3. 保存所有到JSON（记录用）
        all_today = save_to_json(valid_tweets)
        
        # 4. 推送新推文（已去重）
        message = format_push_message(new_tweets)
        if message:
            print(f"推送 {len(new_tweets)} 条新推文...")
            send_to_telegram(message)
            # 5. 记录已推送的推文
            record_pushed_tweets(new_tweets)
    else:
        print("没有新推文")

if __name__ == '__main__':
    asyncio.run(main())

# Playwright EPIPE错误修复 - 设置Node.js内存限制
import os
os.environ['NODE_OPTIONS'] = '--max-old-space-size=4096'
os.environ['PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD'] = '0'
