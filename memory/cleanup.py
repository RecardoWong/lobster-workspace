#!/usr/bin/env python3
"""
记忆淘汰脚本
根据优先级和日期自动清理过期记忆条目

淘汰规则：
- P0: 永久保留（核心设定）
- P1: 保留180天（6个月），项目相关
- P2: 保留30天（1个月），临时记录
"""

import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 淘汰规则（天数）
RETENTION_RULES = {
    'P0': None,      # 永久保留
    'P1': 180,       # 6个月
    'P2': 30,        # 1个月
}

def parse_memory_line(line):
    """解析单行记忆条目，提取优先级和日期"""
    # 匹配 [Px][YYYY-MM-DD] 格式
    pattern = r'\[(P[0-2])\]\[(\d{4}-\d{2}-\d{2})\]'
    match = re.search(pattern, line)
    
    if match:
        priority = match.group(1)
        date_str = match.group(2)
        try:
            entry_date = datetime.strptime(date_str, '%Y-%m-%d')
            return {
                'line': line,
                'priority': priority,
                'date': entry_date,
                'raw_date': date_str
            }
        except ValueError:
            return None
    return None

def should_retain(entry, reference_date=None):
    """判断条目是否应该保留"""
    if reference_date is None:
        reference_date = datetime.now()
    
    priority = entry['priority']
    retention_days = RETENTION_RULES.get(priority)
    
    # P0 永久保留
    if retention_days is None:
        return True
    
    # 计算是否过期
    entry_date = entry['date']
    expiration_date = entry_date + timedelta(days=retention_days)
    
    return reference_date <= expiration_date

def process_memory_file(file_path, dry_run=True):
    """处理记忆文件，执行淘汰"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    retained_lines = []
    removed_entries = []
    stats = {'P0': {'keep': 0, 'remove': 0}, 
             'P1': {'keep': 0, 'remove': 0}, 
             'P2': {'keep': 0, 'remove': 0}}
    
    for line in lines:
        entry = parse_memory_line(line)
        
        if entry:
            if should_retain(entry):
                retained_lines.append(line)
                stats[entry['priority']]['keep'] += 1
            else:
                removed_entries.append(entry)
                stats[entry['priority']]['remove'] += 1
                
                # 保留标题行和空行
                if line.strip().startswith('#') or line.strip() == '':
                    retained_lines.append(line)
        else:
            # 非条目行（标题、分隔符等）保留
            retained_lines.append(line)
    
    # 输出统计
    print(f"\n📊 淘汰统计 ({file_path.name}):")
    print("-" * 50)
    for p in ['P0', 'P1', 'P2']:
        total = stats[p]['keep'] + stats[p]['remove']
        if total > 0:
            print(f"  {p}: 保留 {stats[p]['keep']} 条, 淘汰 {stats[p]['remove']} 条")
    print("-" * 50)
    print(f"  总计: 保留 {sum(stats[p]['keep'] for p in stats)} 条, 淘汰 {len(removed_entries)} 条\n")
    
    # 显示被淘汰的条目
    if removed_entries:
        print("🗑️  被淘汰的条目:")
        for entry in removed_entries:
            line_preview = entry['line'].strip()[:60] + "..." if len(entry['line']) > 60 else entry['line'].strip()
            print(f"   [{entry['priority']}][{entry['raw_date']}] {line_preview}")
        print()
    
    # 执行写入（如果不是 dry-run）
    if not dry_run and removed_entries:
        backup_path = file_path.with_suffix('.md.bak')
        
        # 备份原文件
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # 写入新文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(retained_lines)
        
        print(f"✅ 已更新: {file_path}")
        print(f"💾 备份: {backup_path}")
    elif dry_run:
        print("🔍 试运行模式 - 未实际删除（加 --apply 执行）")
    else:
        print("✨ 没有需要淘汰的条目")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='记忆淘汰脚本')
    parser.add_argument('files', nargs='+', help='记忆文件路径')
    parser.add_argument('--apply', action='store_true', help='实际执行淘汰（默认试运行）')
    parser.add_argument('--before', help='参考日期 (YYYY-MM-DD)，用于测试')
    
    args = parser.parse_args()
    
    print("🧹 记忆淘汰脚本启动")
    print(f"📅 参考日期: {args.before if args.before else datetime.now().strftime('%Y-%m-%d')}")
    print(f"📋 淘汰规则: P0=永久, P1=180天, P2=30天")
    print("=" * 50)
    
    for file_path in args.files:
        process_memory_file(file_path, dry_run=not args.apply)

if __name__ == '__main__':
    main()
