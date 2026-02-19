#!/usr/bin/env python3
"""
Twitter 自动监控 + 翻译 + 部署
每小时自动运行，无需人工干预
"""

import os
import json
import asyncio
import subprocess
from datetime import datetime, timezone, timedelta

# 配置
MONITOR_ACCOUNTS = {
    'elonmusk': 'Elon Musk',
    'jdhasoptions': 'jdhasoptions', 
    'xiaomucrypto': 'xiaomucrypto',
    'aistocksavvy': 'AI Stock Savvy'
}

SAVE_DIR = '/tmp/twitter_monitor'
DASHBOARD_DATA = '/root/.openclaw/workspace/lobster-workspace/dashboard/data/twitter_translated.json'

def translate_text(text):
    """简单翻译（实际应该用翻译API）"""
    # 这里使用预定义的翻译或返回原文
    translations = {
        "Cybercab, which has no pedals or steering wheel, starts production in April": "Cybercab（无人驾驶出租车，无踏板和方向盘）将于4月开始生产",
        "If you're in Korea and want to work on chip design, fabrication or AI software, join Tesla!": "如果你在韩国，想从事芯片设计、制造或AI软件工作，加入特斯拉！",
        "Model S & X are great cars! Order yours before we sunset the program in a few months.": "Model S和X是好车！在几个月后停产前赶紧下单。",
    }
    return translations.get(text, text)

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
        if minutes > 0:
            return f"{minutes}分钟前"
        return "刚刚"
    except:
        return "未知"

async def fetch_tweets():
    """抓取推文（简化版，实际需要浏览器）"""
    print("🐦 开始抓取 Twitter 数据...")
    
    # 读取最新的抓取文件
    all_tweets = {}
    for username, name in MONITOR_ACCOUNTS.items():
        # 查找最新的抓取文件
        import glob
        files = glob.glob(f"{SAVE_DIR}/{username}_*.json")
        if files:
            latest = max(files, key=os.path.getctime)
            try:
                with open(latest, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    tweets = []
                    # 文件格式是 {tweets: [{text, time, ...}]}
                    for item in data.get('tweets', [])[:3]:  # 只取最新3条
                        tweet_id = item.get('id', '')
                        tweet = {
                            'author': username,
                            'name': name,
                            'text': item.get('text', ''),
                            'translate': translate_text(item.get('text', '')),
                            'time': item.get('time', ''),
                            'time_ago': get_time_ago(item.get('time', '')),
                            'url': f"https://x.com/{username}/status/{tweet_id}" if tweet_id else f"https://x.com/{username}"
                        }
                        tweets.append(tweet)
                    all_tweets[username] = tweets
                    print(f"  ✅ {name}: {len(tweets)} 条")
            except Exception as e:
                print(f"  ❌ {name}: {e}")
    
    return all_tweets

def save_and_deploy(tweets_data):
    """保存并部署"""
    # 保存到 dashboard
    output = {
        'update_time': datetime.now().isoformat(),
        'tweets': tweets_data
    }
    
    os.makedirs(os.path.dirname(DASHBOARD_DATA), exist_ok=True)
    with open(DASHBOARD_DATA, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存: {DASHBOARD_DATA}")
    
    # 部署到服务器
    print("🚀 部署到服务器...")
    deploy_cmd = """
    cd /root/.openclaw/workspace/lobster-workspace && 
    scp -i /root/.ssh/lobster_deploy -o StrictHostKeyChecking=no dashboard/data/twitter_translated.json ubuntu@43.160.229.161:/home/ubuntu/ &&
    ssh -i /root/.ssh/lobster_deploy -o StrictHostKeyChecking=no ubuntu@43.160.229.161 'sudo cp /home/ubuntu/twitter_translated.json /var/www/html/data/ && sudo chown www-data:www-data /var/www/html/data/twitter_translated.json'
    """
    
    try:
        result = subprocess.run(deploy_cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ 部署成功!")
        else:
            print(f"⚠️ 部署警告: {result.stderr}")
    except Exception as e:
        print(f"❌ 部署失败: {e}")

async def main():
    print(f"\n{'='*60}")
    print(f"🐦 Twitter 自动监控 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    
    tweets = await fetch_tweets()
    if tweets:
        save_and_deploy(tweets)
    else:
        print("⚠️ 没有新数据")
    
    print(f"{'='*60}\n")

if __name__ == '__main__':
    asyncio.run(main())
