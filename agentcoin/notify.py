#!/usr/bin/env python3
"""
AgentCoin 挖矿通知脚本
通过 OpenClaw Gateway 发送 Telegram 消息
"""

import urllib.request
import urllib.parse
import json
import sys

def send_notification(message):
    """发送通知到 Telegram"""
    try:
        # 使用 OpenClaw 的消息功能
        # 这里我们创建一个简单的 HTTP 请求到本地 Gateway
        gateway_url = "http://127.0.0.1:18789/message"
        
        data = json.dumps({
            "action": "send",
            "target": "5440939697",
            "message": message
        }).encode('utf-8')
        
        req = urllib.request.Request(
            gateway_url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + get_token()
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
            
    except Exception as e:
        # 备用：直接调用 Telegram API (需要 token)
        print(f"通知发送失败: {e}")
        return False

def get_token():
    """读取 gateway token"""
    try:
        with open('/root/.openclaw/openclaw.json', 'r') as f:
            import json
            config = json.load(f)
            return config.get('gateway', {}).get('auth', {}).get('token', '')
    except:
        return ''

if __name__ == '__main__':
    if len(sys.argv) > 1:
        send_notification(sys.argv[1])
    else:
        print("用法: python3 notify.py '消息内容'")
