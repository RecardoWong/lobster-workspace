#!/usr/bin/env python3
"""
财报深度研究 - 使用 Brave Search API
"""

import sys
import os
sys.path.insert(0, '/root/.openclaw/workspace/utils')

from brave_search import BraveSearchClient
from datetime import datetime, timedelta
import subprocess

def send_report(message):
    """发送报告到 Telegram"""
    escaped = message.replace('"', '\\"')[:4000]
    cmd = f'openclaw message send -t "5440939697" -m "{escaped}"'
    try:
        subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
    except:
        pass

def main():
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        client = BraveSearchClient()
        
        # 搜索昨日财报
        news = client.search_earnings(yesterday)
        
        if not news:
            report = f"📊 **财报深度研究 - {yesterday}**\n\n未找到昨日财报相关新闻"
        else:
            report = f"📊 **财报深度研究 - {yesterday}**\n\n🔍 找到 {len(news)} 条财报相关新闻\n\n"
            
            for i, item in enumerate(news[:10], 1):
                title = item['title'][:80]
                desc = item['description'][:100] if item['description'] else ''
                report += f"{i}. **{title}...**\n"
                if desc:
                    report += f"   {desc}...\n"
                report += f"   🔗 {item['url'][:60]}...\n\n"
        
        print(report)
        send_report(report)
        
    except Exception as e:
        error_msg = f"📊 **财报深度研究**\n\n❌ 执行出错: {str(e)[:200]}"
        print(error_msg)
        send_report(error_msg)

if __name__ == '__main__':
    main()
