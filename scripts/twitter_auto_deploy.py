#!/usr/bin/env python3
"""
Twitter 自动监控 + 翻译 + 部署
每小时自动运行，无需人工干预
"""

import os
import json
import asyncio
import subprocess
import urllib.request
import urllib.parse
import re
from datetime import datetime, timezone, timedelta

def translate_text(text):
    """翻译文本 - 使用本地 Ollama"""
    if not text:
        return ""
    
    # 如果已经是中文，直接返回
    if any('\u4e00' <= char <= '\u9fff' for char in text[:50]):
        return text
    
    # 使用 Ollama 本地翻译
    try:
        import urllib.request
        prompt = f"Translate to Chinese (only output translation, no explanation): \"{text[:500]}\""
        data = json.dumps({
            "model": "qwen2.5:0.5b",
            "prompt": prompt,
            "stream": False
        }).encode('utf-8')
        
        req = urllib.request.Request(
            'http://127.0.0.1:11434/api/generate',
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            translated = result.get('response', '').strip().strip('"').strip("'")
            if translated and translated != text:
                return translated
    except Exception as e:
        print(f"  Ollama翻译失败: {e}")
    
    # 回退：返回原文摘要
    return text[:100] + "..." if len(text) > 100 else text

# 配置
MONITOR_ACCOUNTS = {
    'elonmusk': 'Elon Musk',
    'jdhasoptions': 'jdhasoptions', 
    'xiaomucrypto': 'xiaomucrypto',
    'aistocksavvy': 'AI Stock Savvy',
    'QQ_Timmy': 'QQ_Timmy'
}

SAVE_DIR = '/tmp/twitter_monitor'
DASHBOARD_DATA = '/root/.openclaw/workspace/lobster-workspace/dashboard/data/twitter_translated.json'

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
        return "刚刚"
    except:
        return "未知"

async def fetch_tweets():
    """读取抓取的数据文件"""
    print("🐦 读取 Twitter 数据...")
    
    all_tweets = {}
    for username, name in MONITOR_ACCOUNTS.items():
        import glob
        files = glob.glob(f"{SAVE_DIR}/{username}_*.json")
        
        if not files:
            print(f"   ⚠️ {name}: 无文件")
            continue
        
        # 找最新且有数据的文件
        files.sort(key=os.path.getctime, reverse=True)
        latest = None
        for f in files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                if len(data.get('tweets', [])) > 0:
                    latest = f
                    break
            except:
                continue
        
        if not latest:
            print(f"   ⚠️ {name}: 无有效数据")
            continue
        
        try:
            with open(latest, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tweets_data = data.get('tweets', [])
            tweets = []
            for item in tweets_data[:3]:
                text = item.get('text', '')
                tweet_id = str(item.get('id', ''))
                tweets.append({
                    'author': username,
                    'name': name,
                    'text': text[:150] + "..." if len(text) > 150 else text,
                    'translate': translate_text(text),
                    'time': item.get('time', ''),
                    'time_ago': get_time_ago(item.get('time', '')),
                    'url': f"https://x.com/{username}/status/{tweet_id}" if tweet_id else f"https://x.com/{username}"
                })
            
            all_tweets[username] = tweets
            print(f"  ✅ {name}: {len(tweets)} 条 ({os.path.basename(latest)})")
            
        except Exception as e:
            print(f"  ❌ {name}: {e}")
    
    return all_tweets

def save_and_deploy(tweets_data):
    """保存 JSON 并更新 HTML 静态嵌入"""
    now = datetime.now()
    output = {
        'update_time': now.isoformat(),
        'tweets': tweets_data
    }
    
    # 保存 JSON
    os.makedirs(os.path.dirname(DASHBOARD_DATA), exist_ok=True)
    with open(DASHBOARD_DATA, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON 已保存")
    
    # 生成 HTML 嵌入内容
    html_content = generate_twitter_html(tweets_data, now)
    
    # 更新 Dashboard HTML
    update_dashboard_html(html_content, now)
    
    # 部署到服务器
    print("🚀 部署到服务器...")
    deploy_dashboard()

def generate_twitter_html(tweets_data, now):
    """生成 Twitter HTML 嵌入内容 - 只显示前5条+查看更多"""
    # 合并所有推文
    all_tweets = []
    for username, tweets in tweets_data.items():
        for tweet in tweets:
            tweet['_author'] = username
            all_tweets.append(tweet)
    
    # 按时间排序（最新的在前）
    all_tweets.sort(key=lambda x: x.get('time', ''), reverse=True)
    
    # 只取前5条
    top5 = all_tweets[:5]
    
    html_parts = []
    for i, tweet in enumerate(top5, 1):
        # 转义 HTML 特殊字符
        text = tweet['text'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        translate = tweet['translate'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        
        html_parts.append(f"""
<a href="{tweet['url']}" target="_blank" style="text-decoration: none; color: inherit; display: block; margin-bottom: 12px; padding: 12px; border-radius: 8px; transition: background 0.2s; border-left: 3px solid #3b82f6;" class="tweet-link">
<div class="tweet-item" style="cursor: pointer;">
<div class="tweet-author">
<span style="background: #3b82f6; color: white; font-size: 11px; padding: 2px 6px; border-radius: 4px; margin-right: 6px;">#{i}</span>
<span class="tweet-author-name">{tweet['name']}</span>
<span class="tweet-author-handle">@{tweet['author']}</span>
<span class="tweet-time" style="color: #ef4444; font-weight: 500;">{tweet['time_ago']}</span>
</div>
<div class="tweet-text">{text}</div>
<div class="tweet-translate"><span style="color: #3b82f6; font-size: 11px;">[中文翻译]</span> {translate}</div>
<div style="margin-top: 8px; font-size: 11px; color: #9ca3af; text-align: right;">🔗 点击查看原推文 →</div>
</div>
</a>""")
    
    # 添加"查看更多"按钮
    more_link = """
<a href="tweets.html" style="display: block; text-align: center; padding: 12px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 8px; font-weight: 500; margin-top: 8px; transition: opacity 0.2s;">
    查看更多推文 →
</a>"""
    html_parts.append(more_link)
    
    return '\n'.join(html_parts)

def update_dashboard_html(twitter_html, now):
    """更新 Dashboard HTML 文件"""
    html_path = '/root/.openclaw/workspace/lobster-workspace/dashboard/index.html'
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新时间标签
    time_str = now.strftime('%Y-%m-%d %H:%M')
    content = re.sub(
        r'(<span[^>]*id="twitterUpdateTime"[^>]*>)更新于: [^<]+</span>',
        f'\\g<1>更新于: {time_str}</span>',
        content
    )
    
    # 更新 Twitter 内容区域 (在 id="twitterContainer" 的 div 中)
    # 新的HTML结构：直接替换 twitterContainer 中的所有内容直到 </div>
    pattern = r'(<div class="card-body" id="twitterContainer">)[\s\S]*?(</div>\s*</div>\s*<!-- 第三栏)'
    replacement = f'\\g<1>{twitter_html}\\n            </div>\\n            <!-- 第三栏'
    content = re.sub(pattern, replacement, content, count=1)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ HTML 已更新 ({time_str})")

def deploy_dashboard():
    """部署 Dashboard"""
    deploy_cmd = """
    cd /root/.openclaw/workspace/lobster-workspace/dashboard && 
    scp -i /root/.ssh/lobster_deploy -o StrictHostKeyChecking=no index.html ubuntu@43.160.229.161:/home/ubuntu/ 2>/dev/null &&
    scp -i /root/.ssh/lobster_deploy -o StrictHostKeyChecking=no data/twitter_translated.json ubuntu@43.160.229.161:/home/ubuntu/ 2>/dev/null &&
    ssh -i /root/.ssh/lobster_deploy -o StrictHostKeyChecking=no ubuntu@43.160.229.161 'sudo cp /home/ubuntu/index.html /var/www/html/ && sudo cp /home/ubuntu/twitter_translated.json /var/www/html/data/ && sudo chown www-data:www-data /var/www/html/index.html /var/www/html/data/twitter_translated.json' 2>/dev/null
    """
    
    try:
        result = subprocess.run(deploy_cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ 部署成功!")
        else:
            print(f"⚠️ 部署警告")
    except Exception as e:
        print(f"❌ 部署失败: {e}")

async def main():
    print(f"\n{'='*60}")
    print(f"🐦 Twitter 自动更新 - {datetime.now().strftime('%H:%M')}")
    print(f"{'='*60}")
    
    tweets = await fetch_tweets()
    if tweets:
        save_and_deploy(tweets)
        total = sum(len(v) for v in tweets.values())
        print(f"✅ 总计: {total} 条推文")
    else:
        print("⚠️ 无数据")
    
    print(f"{'='*60}\n")

if __name__ == '__main__':
    asyncio.run(main())
