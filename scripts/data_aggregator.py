#!/usr/bin/env python3
"""
数据聚合脚本 - 每5分钟运行一次
同时抓取Twitter和智通财经数据
"""
import asyncio
import json
import subprocess
from datetime import datetime

async def fetch_all_data():
    """并行抓取所有数据源"""
    print(f"🔄 数据聚合开始 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*50)
    
    # 抓取Twitter
    try:
        print("\n📱 抓取Twitter...")
        result = subprocess.run(
            ['python3', '/root/.openclaw/workspace/scripts/twitter_undetected_monitor.py'],
            capture_output=True, text=True, timeout=180
        )
        if result.returncode == 0:
            print("✅ Twitter抓取成功")
        else:
            print(f"⚠️ Twitter: {result.stderr[:100]}")
    except Exception as e:
        print(f"❌ Twitter失败: {e}")
    
    # 抓取智通财经
    try:
        print("\n📊 抓取智通财经...")
        result = subprocess.run(
            ['python3', '/root/.openclaw/workspace/scripts/zhitong_undetected_monitor.py'],
            capture_output=True, text=True, timeout=180
        )
        if result.returncode == 0:
            print("✅ 智通财经抓取成功")
        else:
            print(f"⚠️ 智通财经: {result.stderr[:100]}")
    except Exception as e:
        print(f"❌ 智通财经失败: {e}")
    
    # 合并数据摘要
    summary = {
        'last_update': datetime.now().isoformat(),
        'twitter': [],
        'zhitong': []
    }
    
    try:
        with open('/root/.openclaw/workspace/reports/twitter_undetected_latest.json', 'r') as f:
            summary['twitter'] = json.load(f)
    except:
        pass
    
    try:
        with open('/root/.openclaw/workspace/reports/zhitong_undetected_latest.json', 'r') as f:
            summary['zhitong'] = json.load(f)
    except:
        pass
    
    # 保存摘要
    with open('/root/.openclaw/workspace/reports/data_summary.json', 'w') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*50)
    print(f"📈 Twitter: {len(summary['twitter'])} 条")
    print(f"📰 智通财经: {len(summary['zhitong'])} 条")
    print(f"💾 摘要已保存: reports/data_summary.json")
    print(f"🕐 下次更新: 5分钟后")

if __name__ == '__main__':
    asyncio.run(fetch_all_data())
