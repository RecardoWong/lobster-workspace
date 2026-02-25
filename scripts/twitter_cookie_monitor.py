#!/usr/bin/env python3
"""
Twitter Cookie 监控脚本
使用 auth_token 和 ct0 cookie 抓取推文
"""

import os
import json
import subprocess
from datetime import datetime

# 加载 cookie
AUTH_TOKEN = os.getenv('TWITTER_AUTH_TOKEN', '5da5c73c3286e0c825c5a337eb60ffaf93f2620c')
CT0 = os.getenv('TWITTER_CT0', 'bb867bfa8ae5a410dec9e6537f8aa4f183c43b65c641f9b293a171e8eb8b1b9df359891c89b0e181f4c21bb6e292f422075b77ac3f51a0915fc5e82e2c69c9c5100c14355137082faa36804f10f18ebd')

# 监控账号
MONITOR_ACCOUNTS = ['elonmusk', 'jdhasoptions', 'xiaomucrypto', 'aistocksavvy', 'QQ_Timmy']

def fetch_with_cookie(username):
    """使用 cookie 抓取推文"""
    try:
        # 使用 curl 带 cookie 请求
        url = f'https://x.com/{username}'
        
        cmd = [
            'curl', '-s', url,
            '-H', f'cookie: auth_token={AUTH_TOKEN}; ct0={CT0}',
            '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            '-H', 'Accept-Language: en-US,en;q=0.5',
            '-H', 'Accept-Encoding: gzip, deflate, br',
            '-H', 'DNT: 1',
            '-H', 'Connection: keep-alive',
            '--compressed',
            '--max-time', '30'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
        
        # 简单检查是否成功
        if 'data-testid="tweet"' in result.stdout or 'tweetText' in result.stdout:
            return {'status': 'success', 'content_length': len(result.stdout)}
        else:
            return {'status': 'failed', 'error': 'No tweet data found'}
            
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def main():
    """主函数"""
    print(f"🐦 Twitter Cookie 监控 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    for username in MONITOR_ACCOUNTS:
        result = fetch_with_cookie(username)
        status = '✅' if result['status'] == 'success' else '❌'
        print(f"{status} @{username}: {result.get('content_length', 0)} bytes")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
