#!/usr/bin/env python3
"""
代码文档巡查脚本 - 每日自动扫描（增强版）
检测：硬编码密钥、缺失文档、代码质量问题
"""

import os
import sys
import re
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = "/root/.openclaw/workspace"
ISSUES_DIR = f"{WORKSPACE}/.issues"
TELEGRAM_CHAT_ID = "5440939697"

def send_telegram(message):
    """发送消息到 Telegram"""
    try:
        escaped = message.replace('"', '\\"').replace("'", "\\'")[:3800]
        cmd = f'openclaw message send --channel telegram --target "{TELEGRAM_CHAT_ID}" --message "{escaped}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        print(f"推送失败: {e}")
        return False

def scan_files():
    """扫描工作目录文件"""
    stats = {"python": 0, "javascript": 0, "markdown": 0, "shell": 0, "total": 0}
    py_files = []
    js_files = []
    md_files = []
    
    for root, dirs, files in os.walk(WORKSPACE):
        dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', '.git', 'archive', '.openclaw']]
        
        for file in files:
            filepath = os.path.join(root, file)
            stats["total"] += 1
            if file.endswith('.py'):
                stats["python"] += 1
                py_files.append(filepath)
            elif file.endswith('.js'):
                stats["javascript"] += 1
                js_files.append(filepath)
            elif file.endswith('.md'):
                stats["markdown"] += 1
                md_files.append(filepath)
            elif file.endswith('.sh'):
                stats["shell"] += 1
    
    return stats, py_files, js_files, md_files

def check_hardcoded_secrets(py_files, js_files):
    """检查硬编码密钥"""
    issues = []
    patterns = [
        (r'auth_token\s*=\s*["\']([^"\']+)["\']', 'Twitter Auth Token'),
        (r'ct0\s*=\s*["\']([^"\']+)["\']', 'Twitter CT0'),
        (r'api_key\s*=\s*["\']([^"\']+)["\']', 'API Key'),
        (r'API_KEY\s*=\s*["\']([^"\']+)["\']', 'API Key'),
        (r'token\s*=\s*["\']([a-zA-Z0-9_]{20,})["\']', 'Token'),
        (r'password\s*=\s*["\']([^"\']+)["\']', 'Password'),
        (r'secret\s*=\s*["\']([^"\']+)["\']', 'Secret'),
    ]
    
    for filepath in py_files + js_files:
        # 跳过已经检查过的文件
        if 'test_' in filepath or 'example' in filepath.lower():
            continue
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                for pattern, secret_type in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # 检查是否在 .env 文件中
                        if '.env' not in filepath:
                            # 检查是否是环境变量读取
                            line_start = content.rfind('\n', 0, match.start()) + 1
                            line = content[line_start:match.end()]
                            if 'os.getenv' not in line and 'process.env' not in line:
                                issues.append({
                                    'file': filepath.replace(WORKSPACE, ''),
                                    'type': secret_type,
                                    'line': content[:match.start()].count('\n') + 1
                                })
        except:
            pass
    
    return issues

def check_missing_skill_docs():
    """检查缺失的SKILL.md"""
    missing = []
    learning_dir = f"{WORKSPACE}/learning"
    if os.path.exists(learning_dir):
        for item in os.listdir(learning_dir):
            item_path = os.path.join(learning_dir, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                skill_md = os.path.join(item_path, 'SKILL.md')
                if not os.path.exists(skill_md):
                    missing.append(item)
    return missing

def check_cron_health():
    """检查定时任务健康度"""
    issues = []
    try:
        result = subprocess.run('crontab -l', shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            cron_content = result.stdout
            # 检查是否有 node 命令但没有完整路径
            if 'node ' in cron_content and '/bin/node' not in cron_content:
                # 检查是否已修复
                if '/.nvm/versions/' not in cron_content:
                    issues.append("Cron任务中node命令可能没有完整路径")
    except:
        pass
    return issues

def check_issues_todo():
    """检查待处理Issue详情"""
    todo_dir = f"{ISSUES_DIR}/todo"
    issues = []
    if os.path.exists(todo_dir):
        for f in sorted(os.listdir(todo_dir)):
            if f.endswith('.md'):
                filepath = os.path.join(todo_dir, f)
                try:
                    with open(filepath, 'r') as file:
                        first_line = file.readline().strip()
                        issues.append({
                            'file': f,
                            'title': first_line.replace('# ', '') if first_line.startswith('# ') else f
                        })
                except:
                    issues.append({'file': f, 'title': f})
    return issues

def generate_report():
    """生成巡查报告并推送"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    stats, py_files, js_files, md_files = scan_files()
    
    # 执行各项检查
    hardcoded_issues = check_hardcoded_secrets(py_files, js_files)
    missing_skills = check_missing_skill_docs()
    cron_issues = check_cron_health()
    todo_issues = check_issues_todo()
    
    # 生成报告文件
    report_file = f"{WORKSPACE}/memory/code_audit_{datetime.now().strftime('%Y-%m-%d')}.md"
    
    report = f"""# 代码文档巡查报告 - {now}

## 📊 执行摘要

**巡查时间**: {now} UTC  
**扫描范围**: {WORKSPACE}  
**文件统计**: {stats['total']} 个文件  
- Python: {stats['python']}  
- JavaScript: {stats['javascript']}  
- Markdown: {stats['markdown']}  
- Shell: {stats['shell']}  

## 🔴 发现的问题

### 1. 硬编码密钥 ({len(hardcoded_issues)} 项)
"""
    
    if hardcoded_issues:
        for issue in hardcoded_issues[:10]:  # 只显示前10个
            report += f"- **{issue['type']}**: `{issue['file']}` 第{issue['line']}行\n"
        if len(hardcoded_issues) > 10:
            report += f"- ... 还有 {len(hardcoded_issues) - 10} 项\n"
    else:
        report += "✅ 未发现硬编码密钥问题\n"
    
    report += f"""
### 2. 缺失 SKILL.md ({len(missing_skills)} 项)
"""
    if missing_skills:
        for skill in missing_skills:
            report += f"- `learning/{skill}/SKILL.md`\n"
    else:
        report += "✅ 所有模块都有 SKILL.md\n"
    
    report += f"""
### 3. 定时任务检查
"""
    if cron_issues:
        for issue in cron_issues:
            report += f"- ⚠️ {issue}\n"
    else:
        report += "✅ 定时任务配置正常\n"
    
    report += f"""
### 4. 待处理 Issue ({len(todo_issues)} 项)
"""
    if todo_issues:
        for issue in todo_issues:
            report += f"- **{issue['title']}** (`{issue['file']}`)\n"
    else:
        report += "✅ 没有待处理 Issue\n"
    
    report += "\n---\n\n*报告生成时间: " + now + "*\n"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    # 生成 Telegram 推送（问题聚焦版）
    telegram_msg = f"""📋 **代码巡查报告** - {now}

"""
    
    # 如果有问题，详细列出
    has_issues = False
    
    if hardcoded_issues:
        has_issues = True
        telegram_msg += f"🔴 **硬编码密钥** ({len(hardcoded_issues)} 项，需整改)\n"
        for issue in hardcoded_issues[:5]:  # 显示前5个
            telegram_msg += f"  • `{issue['file']}` 第{issue['line']}行\n"
        if len(hardcoded_issues) > 5:
            telegram_msg += f"  ... 还有 {len(hardcoded_issues) - 5} 项\n"
        telegram_msg += "\n"
    
    if missing_skills:
        has_issues = True
        telegram_msg += f"🔴 **缺失 SKILL.md** ({len(missing_skills)} 项)\n"
        for skill in missing_skills:
            telegram_msg += f"  • `learning/{skill}/`\n"
        telegram_msg += "\n"
    
    if todo_issues:
        has_issues = True
        telegram_msg += f"📋 **待处理 Issue** ({len(todo_issues)} 项)\n"
        for issue in todo_issues[:3]:
            telegram_msg += f"  • {issue['title']}\n"
        if len(todo_issues) > 3:
            telegram_msg += f"  ... 还有 {len(todo_issues) - 3} 项\n"
        telegram_msg += "\n"
    
    if cron_issues:
        has_issues = True
        telegram_msg += f"⚠️ **定时任务问题**\n"
        for issue in cron_issues:
            telegram_msg += f"  • {issue}\n"
        telegram_msg += "\n"
    
    if not has_issues:
        telegram_msg += "✅ **今日无问题，一切正常！**\n\n"
    
    telegram_msg += f"📄 完整报告: `memory/code_audit_{datetime.now().strftime('%Y-%m-%d')}.md`"
    
    # 推送
    print("正在推送报告...")
    if send_telegram(telegram_msg):
        print("✅ 推送成功")
    else:
        print("❌ 推送失败")
    
    print(f"✅ 巡查完成: {report_file}")
    return report

if __name__ == '__main__':
    generate_report()
