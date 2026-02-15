#!/usr/bin/env python3
"""
Dashboard 自动部署脚本
用于将本地 Dashboard 文件同步到腾讯云服务器
"""

import os
import subprocess
import datetime
import sys

# 配置
SERVER = "ubuntu@43.160.229.161"
REMOTE_DIR = "/var/www/html"
LOCAL_DIR = "/root/.openclaw/workspace/memory/dashboard"
SSH_KEY = os.path.expanduser("~/.ssh/dashboard_deploy_key")

# 需要部署的文件
FILES = [
    "index.html",
    "index_v2.html",
    "mobile.html",
    "twitter.html",
    "hello_dashboard.html",
    "lesson1.html",
    "lesson2.html"
]

def log(message):
    """打印日志"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_ssh_connection():
    """检查 SSH 连接是否可用"""
    try:
        result = subprocess.run(
            ["ssh", "-i", SSH_KEY, "-o", "ConnectTimeout=5", "-o", "StrictHostKeyChecking=no", 
             SERVER, "echo 'OK'"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0 and "OK" in result.stdout
    except Exception as e:
        log(f"SSH 检查失败: {e}")
        return False

def deploy_file(filename):
    """部署单个文件"""
    local_path = os.path.join(LOCAL_DIR, filename)
    
    if not os.path.exists(local_path):
        log(f"⚠️ 文件不存在: {filename}")
        return False
    
    try:
        # 先复制到用户目录，再用 sudo 移动到目标位置
        tmp_path = f"/tmp/{filename}"
        
        # Step 1: 复制到服务器 /tmp
        cmd1 = ["scp", "-i", SSH_KEY, "-o", "ConnectTimeout=5", "-o", "StrictHostKeyChecking=no",
                local_path, f"{SERVER}:{tmp_path}"]
        result1 = subprocess.run(cmd1, capture_output=True, text=True, timeout=30)
        
        if result1.returncode != 0:
            log(f"❌ {filename} 上传到/tmp失败: {result1.stderr}")
            return False
        
        # Step 2: 用 sudo 移动到 /var/www/html/
        cmd2 = ["ssh", "-i", SSH_KEY, "-o", "ConnectTimeout=5", "-o", "StrictHostKeyChecking=no",
                SERVER, f"sudo mv {tmp_path} {REMOTE_DIR}/ && sudo chmod 644 {REMOTE_DIR}/{filename}"]
        result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=30)
        
        if result2.returncode == 0:
            log(f"✅ {filename} 部署成功")
            return True
        else:
            log(f"❌ {filename} 移动到目标目录失败: {result2.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        log(f"⏱️ {filename} 部署超时")
        return False
    except Exception as e:
        log(f"❌ {filename} 部署异常: {e}")
        return False

def deploy_all():
    """部署所有文件"""
    log("🚀 Dashboard 自动部署开始...")
    log(f"📁 本地目录: {LOCAL_DIR}")
    log(f"🌐 服务器: {SERVER}:{REMOTE_DIR}")
    
    # 检查 SSH 连接
    if check_ssh_connection():
        log("✅ SSH 连接正常")
    else:
        log("⚠️ SSH 连接失败，将尝试继续部署...")
    
    # 部署每个文件
    success_count = 0
    fail_count = 0
    
    for filename in FILES:
        if deploy_file(filename):
            success_count += 1
        else:
            fail_count += 1
    
    # 输出结果
    log("")
    log("=" * 50)
    log(f"🎉 部署完成！成功: {success_count}, 失败: {fail_count}")
    log(f"🌐 访问地址: http://43.160.229.161/")
    log(f"🌐 新版地址: http://43.160.229.161/index_v2.html")
    log("=" * 50)
    
    # 记录部署日志
    log_file = os.path.join(LOCAL_DIR, "../deploy.log")
    with open(log_file, "a") as f:
        f.write(f"{datetime.datetime.now()}: Deployed {success_count} files\n")
    
    return fail_count == 0

def deploy_single(filename):
    """部署单个指定文件"""
    if not filename:
        print("用法: python3 deploy.py [文件名]")
        print(f"示例: python3 deploy.py index_v2.html")
        return False
    
    log(f"🚀 部署单个文件: {filename}")
    return deploy_file(filename)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 部署指定文件
        deploy_single(sys.argv[1])
    else:
        # 部署所有文件
        success = deploy_all()
        sys.exit(0 if success else 1)
