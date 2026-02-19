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
from datetime import datetime, timezone, timedelta

def translate_text(text):
    """翻译文本 - 使用 MyMemory API (免费)"""
    if not text:
        return ""
    
    # 如果已经是中文，直接返回
    if any('\u4e00' <= char <= '\u9fff' for char in text[:50]):
        return text
    
    # 预定义翻译（常用短语）
    translations = {
        "Cybercab, which has no pedals or steering wheel, starts production in April": "Cybercab无人驾驶出租车将于4月投产",
        "The Meaning of Life": "生命的意义",
        "After-market buzz": "盘后热点",
        "After-Market Earnings Recap": "盘后财报回顾",
    }
    
    # 检查预定义
    for key, value in translations.items():
        if key.lower() in text.lower() or text.lower() in key.lower():
            return value
    
    # 使用 MyMemory API 翻译
    try:
        encoded_text = urllib.parse.quote(text[:300])
        url = f"https://api.mymemory.translated.net/get?q={encoded_text}&langpair=en|zh-CN"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('responseStatus') == 200:
                translated = data.get('responseData', {}).get('translatedText', '')
                if translated and translated != text:
                    return translated
    except Exception as e:
        print(f"  翻译API失败: {e}")
    
    # 回退：返回原文摘要
    return text[:100] + "..." if len(text) > 100 else text

# 配置
MONITOR_ACCOUNTS = {
    'elonmusk': 'Elon Musk',
    'jdhasoptions': 'jdhasoptions', 
    'xiaomucrypto': 'xiaomucrypto',
    'aistocksavvy': 'AI Stock Savvy'
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
    """保存并部署"""
    output = {
        'update_time': datetime.now().isoformat(),
        'tweets': tweets_data
    }
    
    os.makedirs(os.path.dirname(DASHBOARD_DATA), exist_ok=True)
    with open(DASHBOARD_DATA, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存")
    
    # 部署到服务器
    print("🚀 部署到服务器...")
    deploy_cmd = """
    cd /root/.openclaw/workspace/lobster-workspace && 
    scp -i /root/.ssh/lobster_deploy -o StrictHostKeyChecking=no dashboard/data/twitter_translated.json ubuntu@43.160.229.161:/home/ubuntu/ 2>/dev/null &&
    ssh -i /root/.ssh/lobster_deploy -o StrictHostKeyChecking=no ubuntu@43.160.229.161 'sudo cp /home/ubuntu/twitter_translated.json /var/www/html/data/ && sudo chown www-data:www-data /var/www/html/data/twitter_translated.json' 2>/dev/null
    """
    
    try:
        result = subprocess.run(deploy_cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ 部署成功!")
        else:
            print(f"⚠️ 部署问题")
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
