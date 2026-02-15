# Dashboard 自动部署配置指南

## 🎯 目标
每次更新 Dashboard 代码后，自动同步到腾讯云服务器

## 📋 服务器信息
- **IP**: 43.160.229.161
- **用户**: ubuntu
- **Web目录**: /var/www/html
- **Web服务器**: Nginx

---

## 方案一：SSH 免密登录 + Rsync（推荐）

### 1. 生成 SSH 密钥（如果还没有）
```bash
ssh-keygen -t ed25519 -C "dashboard-deploy"
# 按回车使用默认路径
```

### 2. 复制公钥到服务器
```bash
ssh-copy-id ubuntu@43.160.229.161
# 输入服务器密码完成配置
```

### 3. 测试免密登录
```bash
ssh ubuntu@43.160.229.161 "echo '连接成功'"
```

### 4. 运行部署脚本
```bash
cd /root/.openclaw/workspace/memory/dashboard
chmod +x deploy.sh
./deploy.sh
```

---

## 方案二：Git 自动部署（Hook）

### 1. 在服务器上创建裸仓库
```bash
ssh ubuntu@43.160.229.161
mkdir -p ~/git/dashboard.git
cd ~/git/dashboard.git
git init --bare
```

### 2. 创建 post-receive hook
```bash
cd ~/git/dashboard.git/hooks
cat > post-receive << 'EOF'
#!/bin/bash
TARGET="/var/www/html"
git --work-tree=$TARGET --git-dir=$GIT_DIR checkout -f
echo "Deployed to $TARGET"
EOF
chmod +x post-receive
```

### 3. 本地添加远程仓库
```bash
cd /root/.openclaw/workspace/memory/dashboard
git remote add deploy ubuntu@43.160.229.161:~/git/dashboard.git
```

### 4. 部署命令
```bash
git push deploy main
```

---

## 方案三：Cron 定时自动同步

### 1. 编辑 crontab
```bash
crontab -e
```

### 2. 添加定时任务（每5分钟同步一次）
```cron
*/5 * * * * cd /root/.openclaw/workspace/memory/dashboard && rsync -avz index.html index_v2.html mobile.html twitter.html ubuntu@43.160.229.161:/var/www/html/ >> /tmp/dashboard-sync.log 2>&1
```

---

## 方案四：Python 自动部署脚本

```python
#!/usr/bin/env python3
import os
import subprocess
import datetime

SERVER = "ubuntu@43.160.229.161"
REMOTE_DIR = "/var/www/html"
LOCAL_DIR = "/root/.openclaw/workspace/memory/dashboard"
FILES = ["index.html", "index_v2.html", "mobile.html", "twitter.html"]

def deploy():
    print(f"🚀 开始部署... {datetime.datetime.now()}")
    
    for file in FILES:
        local_path = os.path.join(LOCAL_DIR, file)
        if os.path.exists(local_path):
            cmd = f"scp {local_path} {SERVER}:{REMOTE_DIR}/"
            result = subprocess.run(cmd, shell=True, capture_output=True)
            if result.returncode == 0:
                print(f"✅ {file} 部署成功")
            else:
                print(f"❌ {file} 部署失败: {result.stderr.decode()}")
    
    print("🎉 部署完成！")

if __name__ == "__main__":
    deploy()
```

---

## 🔧 当前状态检查

### 检查服务器连接
```bash
ssh -o ConnectTimeout=5 ubuntu@43.160.229.161 "ls -la /var/www/html/"
```

### 手动复制单个文件
```bash
scp /root/.openclaw/workspace/memory/dashboard/index_v2.html ubuntu@43.160.229.161:/var/www/html/
```

---

## 📁 本地文件结构

```
/root/.openclaw/workspace/memory/dashboard/
├── index.html              # 主页面 (当前版本)
├── index_v2.html           # 改进版本 (三标签页)
├── mobile.html             # 移动端适配
├── twitter.html            # Twitter监控页
├── hello_dashboard.html    # 入门示例
├── lesson1.html            # 教学1
├── lesson2.html            # 教学2
├── deploy.sh               # 部署脚本
└── README.md               # 说明文档
```

---

## 🚀 快速部署命令

```bash
# 一键部署最新版本
cd /root/.openclaw/workspace/memory/dashboard && ./deploy.sh

# 或者手动复制
cp index_v2.html index.html
scp index.html ubuntu@43.160.229.161:/var/www/html/
```

---

*最后更新: 2026-02-15*
