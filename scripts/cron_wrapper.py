#!/usr/bin/env python3
"""
Cron任务包装器 - 执行任务并推送结果到Telegram
"""

import subprocess
import sys
import os

CHAT_ID = "5440939697"

def send_message(text):
    """发送消息到Telegram"""
    escaped = text.replace('"', '\\"').replace("'", "\\'")[:4000]
    cmd = f'openclaw message send -t "{CHAT_ID}" -m "{escaped}"'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def run_with_notify(task_name, command):
    """运行命令并推送结果"""
    print(f"[{task_name}] 开始执行...")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        output = result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout
        
        if result.returncode == 0:
            message = f"✅ **{task_name} 完成**\n\n```\n{output[:500]}...\n```\n\n完整输出请查看服务器日志"
        else:
            message = f"⚠️ **{task_name} 执行出错**\n\n```\n{result.stderr[:500]}\n```"
        
        send_message(message)
        return result.returncode
        
    except subprocess.TimeoutExpired:
        send_message(f"⏱️ **{task_name} 超时**\n\n执行超过5分钟")
        return 1
    except Exception as e:
        send_message(f"❌ **{task_name} 异常**\n\n{str(e)[:200]}")
        return 1

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python3 cron_wrapper.py '任务名' '命令'")
        sys.exit(1)
    
    task_name = sys.argv[1]
    command = sys.argv[2]
    
    exit_code = run_with_notify(task_name, command)
    sys.exit(exit_code)
