#!/usr/bin/env python3
"""
🦞 龙虾Agent自主创造：智能监控仪表盘
实时监控所有系统状态，主动发现问题
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List

class LobsterDashboard:
    """自主创造：龙虾智能仪表盘"""
    
    def __init__(self):
        self.status_file = "/tmp/lobster_dashboard_status.json"
        self.check_interval = 300  # 5分钟
    
    def scan_all_monitors(self) -> Dict:
        """自主扫描所有监控状态"""
        monitors = {
            'elon_musk': {
                'file': '/tmp/elon_last_check.json',
                'desc': 'Elon Musk推特监控',
                'last_check': None,
                'status': 'unknown'
            },
            'clanker': {
                'file': '/tmp/clanker_last_check.json',
                'desc': 'Clanker/Bankr监控',
                'last_check': None,
                'status': 'unknown'
            },
            'twitter_assistant': {
                'file': '/tmp/twitter_assistant_last.json',
                'desc': 'Twitter个人助手',
                'last_check': None,
                'status': 'unknown'
            },
            'moltbook': {
                'file': '/tmp/moltbook_last_check.json',
                'desc': 'Moltbook学习',
                'last_check': None,
                'status': 'unknown'
            }
        }
        
        for name, config in monitors.items():
            if os.path.exists(config['file']):
                try:
                    with open(config['file'], 'r') as f:
                        data = json.load(f)
                        last_check = data.get('last_check', '')
                        monitors[name]['last_check'] = last_check
                        
                        # 检查是否超时
                        if last_check:
                            try:
                                check_time = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
                                if datetime.now() - check_time < timedelta(minutes=70):
                                    monitors[name]['status'] = 'active'
                                else:
                                    monitors[name]['status'] = 'stale'
                            except:
                                monitors[name]['status'] = 'unknown'
                        else:
                            monitors[name]['status'] = 'no_data'
                except:
                    monitors[name]['status'] = 'error'
            else:
                monitors[name]['status'] = 'not_initialized'
        
        return monitors
    
    def check_disk_space(self) -> Dict:
        """自主检查磁盘空间"""
        import shutil
        
        stat = shutil.disk_usage('/')
        free_gb = stat.free / (1024**3)
        total_gb = stat.total / (1024**3)
        used_percent = (stat.used / stat.total) * 100
        
        return {
            'total_gb': round(total_gb, 1),
            'free_gb': round(free_gb, 1),
            'used_percent': round(used_percent, 1),
            'status': 'critical' if used_percent > 90 else 'warning' if used_percent > 80 else 'healthy'
        }
    
    def check_memory(self) -> Dict:
        """自主检查内存"""
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
            
            mem_info = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':')
                    mem_info[key.strip()] = int(value.split()[0])
            
            total = mem_info.get('MemTotal', 0) / 1024 / 1024  # GB
            available = mem_info.get('MemAvailable', 0) / 1024 / 1024
            
            return {
                'total_gb': round(total, 1),
                'available_gb': round(available, 1),
                'status': 'healthy' if available > 0.5 else 'warning'
            }
        except:
            return {'status': 'unknown'}
    
    def generate_dashboard(self) -> str:
        """自主生成仪表盘报告"""
        lines = [
            "🦞 龙虾智能仪表盘",
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            ""
        ]
        
        # 系统状态
        lines.append("📊 系统状态")
        lines.append("-" * 40)
        
        disk = self.check_disk_space()
        memory = self.check_memory()
        
        disk_emoji = "🟢" if disk['status'] == 'healthy' else "🟡" if disk['status'] == 'warning' else "🔴"
        lines.append(f"{disk_emoji} 磁盘: {disk['used_percent']}% 使用 ({disk['free_gb']}GB 剩余)")
        lines.append(f"💾 内存: {memory.get('available_gb', '?')}GB 可用")
        lines.append("")
        
        # 监控状态
        lines.append("📡 监控状态")
        lines.append("-" * 40)
        
        monitors = self.scan_all_monitors()
        for name, info in monitors.items():
            status_emoji = {
                'active': '🟢', 'stale': '🟡', 'error': '🔴',
                'unknown': '⚪', 'not_initialized': '⚪', 'no_data': '⚪'
            }.get(info['status'], '⚪')
            
            lines.append(f"{status_emoji} {info['desc']}")
            lines.append(f"   状态: {info['status']}")
            if info['last_check']:
                lines.append(f"   最后检查: {info['last_check'][:16]}")
        
        lines.append("")
        
        # 自主发现的问题
        lines.append("🔍 自主发现")
        lines.append("-" * 40)
        
        issues = []
        for name, info in monitors.items():
            if info['status'] == 'stale':
                issues.append(f"⚠️ {info['desc']} 超过1小时未更新")
            elif info['status'] == 'error':
                issues.append(f"❌ {info['desc']} 运行错误")
        
        if disk['status'] != 'healthy':
            issues.append(f"{'⚠️' if disk['status'] == 'warning' else '🔴'} 磁盘空间紧张")
        
        if issues:
            for issue in issues:
                lines.append(issue)
        else:
            lines.append("✅ 所有系统正常运行")
        
        lines.append("")
        lines.append("=" * 60)
        lines.append("🦞 自主创造 by 龙虾Agent")
        
        return "\n".join(lines)
    
    def auto_fix_issues(self) -> List[str]:
        """自主修复发现的问题"""
        fixes = []
        
        monitors = self.scan_all_monitors()
        
        # 检查是否需要清理日志
        log_size = 0
        for root, dirs, files in os.walk('/tmp'):
            for f in files:
                if f.startswith('elon_') or f.startswith('clanker_') or f.startswith('twitter_'):
                    try:
                        log_size += os.path.getsize(os.path.join(root, f))
                    except:
                        pass
        
        if log_size > 100 * 1024 * 1024:  # 100MB
            fixes.append("日志文件过大，建议清理旧日志")
        
        return fixes


def main():
    """测试仪表盘"""
    dashboard = LobsterDashboard()
    report = dashboard.generate_dashboard()
    print(report)
    
    # 保存状态
    with open('/tmp/lobster_dashboard_latest.txt', 'w') as f:
        f.write(report)
    
    print("\n💾 仪表盘已保存到 /tmp/lobster_dashboard_latest.txt")


if __name__ == "__main__":
    main()
