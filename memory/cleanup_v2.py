#!/usr/bin/env python3
"""
记忆淘汰脚本 - 按用户指定逻辑
- P0: 永不淘汰
- P2: 超过30天移到归档
- P1: 超过90天移到归档
- 总行数>200: 按日期排序P1，从最旧的移到归档
"""

import re
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# 淘汰规则（天数）
RETENTION_DAYS = {
    'P0': None,   # 永不淘汰
    'P1': 90,     # 90天
    'P2': 30,     # 30天
}

MAX_LINES = 200  # 行数上限

def parse_entry(line):
    """解析记忆条目"""
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

def is_header_or_separator(line):
    """判断是否是标题或分隔符（非条目行）"""
    stripped = line.strip()
    return (stripped.startswith('#') or 
            stripped.startswith('---') or
            stripped.startswith('===') or
            stripped == '' or
            not stripped.startswith('-'))

def process_memory_file(file_path, archive_path, reference_date=None, dry_run=True):
    """处理记忆文件"""
    file_path = Path(file_path)
    archive_path = Path(archive_path)
    
    if reference_date is None:
        reference_date = datetime.now()
    
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 分类
    entries = []           # 带标签的记忆条目
    non_entries = []       # 标题、分隔符等非条目行
    
    for i, line in enumerate(lines):
        entry = parse_entry(line)
        if entry:
            entries.append({**entry, 'index': i})
        else:
            non_entries.append({'line': line, 'index': i})
    
    # 按优先级分组
    p0_entries = [e for e in entries if e['priority'] == 'P0']
    p1_entries = [e for e in entries if e['priority'] == 'P1']
    p2_entries = [e for e in entries if e['priority'] == 'P2']
    
    # 初始化结果
    keep_entries = []
    archive_entries = []
    
    # 1. P0 - 永不淘汰
    keep_entries.extend(p0_entries)
    
    # 2. P2 - 超过30天移到归档
    for e in p2_entries:
        age = (reference_date - e['date']).days
        if age > RETENTION_DAYS['P2']:
            archive_entries.append({**e, 'reason': f'P2超过{RETENTION_DAYS["P2"]}天'})
        else:
            keep_entries.append(e)
    
    # 3. P1 - 超过90天移到归档
    active_p1 = []
    for e in p1_entries:
        age = (reference_date - e['date']).days
        if age > RETENTION_DAYS['P1']:
            archive_entries.append({**e, 'reason': f'P1超过{RETENTION_DAYS["P1"]}天'})
        else:
            active_p1.append(e)
    
    keep_entries.extend(active_p1)
    
    # 4. 行数上限检查
    total_lines = len(non_entries) + len(keep_entries)
    
    if total_lines > MAX_LINES:
        # 按日期排序P1（最旧的在前）
        p1_to_sort = [e for e in keep_entries if e['priority'] == 'P1']
        other_keep = [e for e in keep_entries if e['priority'] != 'P1']
        
        # 按日期排序
        p1_to_sort.sort(key=lambda x: x['date'])
        
        # 计算需要移出多少行
        excess = total_lines - MAX_LINES
        
        # 从最旧的P1开始移到归档
        for e in p1_to_sort[:excess]:
            archive_entries.append({**e, 'reason': '超出行数上限'})
        
        # 保留剩下的
        keep_entries = other_keep + p1_to_sort[excess:]
    
    # 按原始顺序排序
    keep_entries.sort(key=lambda x: x['index'])
    archive_entries.sort(key=lambda x: x['index'])
    
    # 输出统计
    print(f"\n📊 淘汰统计 ({file_path.name}):")
    print("-" * 60)
    print(f"  原文件总行数: {len(lines)}")
    print(f"  非条目行: {len(non_entries)}")
    print(f"  P0条目: {len(p0_entries)} (全部保留)")
    print(f"  P1条目: {len(p1_entries)} (保留 {len([e for e in keep_entries if e['priority']=='P1'])}, 归档 {len([e for e in archive_entries if e['priority']=='P1'])})")
    print(f"  P2条目: {len(p2_entries)} (保留 {len([e for e in keep_entries if e['priority']=='P2'])}, 归档 {len([e for e in archive_entries if e['priority']=='P2'])})")
    print("-" * 60)
    print(f"  保留行数: {len(non_entries) + len(keep_entries)}")
    print(f"  归档行数: {len(archive_entries)}")
    print("-" * 60)
    
    # 显示归档条目
    if archive_entries:
        print("\n🗂️  归档条目:")
        for e in archive_entries[:5]:  # 只显示前5条
            preview = e['line'].strip()[:50] + "..." if len(e['line']) > 50 else e['line'].strip()
            print(f"   [{e['priority']}][{e['raw_date']}] {e['reason']}")
            print(f"      {preview}")
        if len(archive_entries) > 5:
            print(f"   ... 还有 {len(archive_entries)-5} 条")
        print()
    
    # 执行写入
    if not dry_run:
        # 构建保留文件内容
        keep_content = []
        
        # 按原始顺序重组：非条目行 + 保留的条目
        all_keep = sorted(non_entries + keep_entries, key=lambda x: x['index'])
        for item in all_keep:
            keep_content.append(item['line'])
        
        # 写回记忆文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(keep_content)
        
        # 追加到归档文件
        archive_content = []
        if archive_path.exists():
            with open(archive_path, 'r', encoding='utf-8') as f:
                archive_content = f.readlines()
        
        # 添加时间戳头
        archive_content.append(f"\n# 归档于 {reference_date.strftime('%Y-%m-%d %H:%M')}\n")
        for e in archive_entries:
            archive_content.append(e['line'])
        
        with open(archive_path, 'w', encoding='utf-8') as f:
            f.writelines(archive_content)
        
        print(f"✅ 已更新: {file_path}")
        print(f"💾 已归档: {archive_path} ({len(archive_entries)} 条)")
    else:
        print("🔍 试运行模式 - 未实际执行（加 --apply 执行）\n")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='记忆淘汰脚本')
    parser.add_argument('file', help='记忆文件路径')
    parser.add_argument('--archive', default='archive.md', help='归档文件路径')
    parser.add_argument('--dry-run', action='store_true', help='预览模式（默认，不实际执行）')
    parser.add_argument('--apply', action='store_true', help='实际执行淘汰')
    parser.add_argument('--before', help='参考日期 (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    reference_date = datetime.now()
    if args.before:
        reference_date = datetime.strptime(args.before, '%Y-%m-%d')
    
    # 执行模式判断：默认是 dry-run
    is_dry_run = not args.apply
    
    # 安全提示
    if args.apply:
        print("⚠️  警告: 你正在执行实际淘汰操作！")
        print("   建议先运行预览模式检查会淘汰什么。\n")
    else:
        print("🔍 预览模式 - 不会实际删除任何内容")
        print("   确认无误后加 --apply 执行\n")
    
    print("🧹 记忆淘汰脚本启动")
    print(f"📅 参考日期: {reference_date.strftime('%Y-%m-%d')}")
    print(f"📋 规则: P0=永久, P1=90天, P2=30天, 上限={MAX_LINES}行")
    print("=" * 60)
    
    process_memory_file(args.file, args.archive, reference_date, dry_run=is_dry_run)

if __name__ == '__main__':
    main()
