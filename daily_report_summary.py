#!/usr/bin/env python3
"""
📊 每日监控报告整理
早上8:30和晚上6:30发送整理好的报告
"""

import os
import glob
from datetime import datetime

class DailyReportSummary:
    """每日报告整理"""
    
    def __init__(self):
        self.report_parts = []
    
    def read_latest_file(self, pattern: str, title: str) -> str:
        """读取最新的监控文件"""
        files = glob.glob(f"/tmp/{pattern}_*.txt")
        if not files:
            return f"\n📌 {title}\n暂无数据\n"
        
        # 找最新的文件
        latest_file = max(files, key=os.path.getmtime)
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取关键信息
            lines = content.split('\n')
            key_info = []
            
            for line in lines:
                # 过滤掉分隔线和空行，保留关键内容
                if line.strip() and not line.startswith('=') and not line.startswith('-'):
                    key_info.append(line)
            
            result = f"\n📌 {title}\n"
            result += '\n'.join(key_info[:20])  # 取前20行
            return result
            
        except Exception as e:
            return f"\n📌 {title}\n读取失败: {e}\n"
    
    def generate_summary(self) -> str:
        """生成汇总报告"""
        now = datetime.now()
        
        lines = [
            "=" * 60,
            f"📊 每日监控报告 | {now.strftime('%Y-%m-%d %H:%M')}",
            "=" * 60,
        ]
        
        # 1. XXYY.io Meme扫描
        lines.append(self.read_latest_file("xxyy_result", "🪙 XXYY.io Meme扫描"))
        
        # 2. Twitter监控
        lines.append(self.read_latest_file("twitter_separate", "🐦 Twitter监控"))
        
        # 3. 智通财经快讯（合并版）
        lines.append(self.read_latest_file("zhitong_combined", "📊 智通财经市场快讯"))
        
        # 5. 英诺赛科（如果有）
        supplier_files = glob.glob("/tmp/supplier_report_*.txt")
        if supplier_files:
            lines.append(self.read_latest_file("supplier_report", "🏭 英诺赛科供应商"))
        
        lines.append("\n" + "=" * 60)
        lines.append("📌 下次报告: " + ("晚上18:30" if now.hour < 12 else "明天早上08:30"))
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def run(self):
        """运行并输出报告"""
        report = self.generate_summary()
        print(report)
        
        # 保存汇总报告
        with open(f"/tmp/daily_report_{datetime.now().strftime('%H%M')}.txt", 'w', encoding='utf-8') as f:
            f.write(report)


if __name__ == "__main__":
    summary = DailyReportSummary()
    summary.run()
