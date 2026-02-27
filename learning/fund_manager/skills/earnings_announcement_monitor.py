#!/usr/bin/env python3
"""
财报公告自动监控
监控定期报告：年报、半年报、季报、业绩预告
有新公告时自动推送
"""

import akshare as ak
import sys
sys.path.insert(0, '/root/.openclaw/workspace/learning/earnings_reader/skills')
from datetime import datetime, timedelta
from typing import List, Dict

class EarningsAnnouncementMonitor:
    """财报公告监控器"""
    
    def __init__(self):
        self.watchlist = [
            '000001',  # 平安银行
            '02577',   # 英诺赛科 (港股，但可通过其他方式)
            '300750',  # 宁德时代
            '600519',  # 贵州茅台
        ]
    
    def get_recent_announcements(self, symbol: str, days: int = 7) -> List[Dict]:
        """获取最近公告"""
        try:
            df = ak.stock_zh_a_disclosure_report_cninfo(
                symbol=symbol,
                start_date=(datetime.now() - timedelta(days=days)).strftime('%Y%m%d'),
                end_date=datetime.now().strftime('%Y%m%d')
            )
            
            if df.empty:
                return []
            
            # 筛选重要公告类型
            important_types = [
                '年报', '半年报', '季报', '业绩预告',
                '业绩快报', '权益分派', '股东大会',
                '增发', '配股', '解禁'
            ]
            
            announcements = []
            for _, row in df.iterrows():
                title = row.get('公告标题', '')
                # 检查是否重要类型
                is_important = any(t in title for t in important_types)
                
                announcements.append({
                    'date': row.get('公告时间', ''),
                    'title': title,
                    'type': '重要' if is_important else '一般',
                    'link': row.get('公告链接', '')
                })
            
            return announcements
            
        except Exception as e:
            print(f"获取{symbol}公告失败: {e}")
            return []
    
    def check_earnings_preview(self, symbol: str) -> Dict:
        """检查业绩预告"""
        try:
            # 通过公告筛选业绩预告
            announcements = self.get_recent_announcements(symbol, days=30)
            
            for ann in announcements:
                if '业绩预告' in ann['title']:
                    return {
                        'has_preview': True,
                        'date': ann['date'],
                        'title': ann['title'],
                        'type': '预增' if '增' in ann['title'] else '预减' if '减' in ann['title'] else '不确定'
                    }
            
            return {'has_preview': False}
            
        except Exception as e:
            return {'has_preview': False, 'error': str(e)}
    
    def monitor_all(self) -> str:
        """监控所有关注股票"""
        lines = [
            f"📊 财报公告监控 ({datetime.now().strftime('%Y-%m-%d %H:%M')})",
            "=" * 70,
            ""
        ]
        
        for symbol in self.watchlist:
            print(f"正在检查 {symbol}...")
            
            # 获取最近公告
            announcements = self.get_recent_announcements(symbol, days=7)
            
            if announcements:
                # 筛选重要公告
                important = [a for a in announcements if a['type'] == '重要']
                
                if important:
                    lines.append(f"🔔 {symbol} - 发现 {len(important)} 条重要公告:")
                    for ann in important[:3]:
                        date = str(ann['date'])[:10] if ann['date'] else 'N/A'
                        lines.append(f"   • [{date}] {ann['title'][:50]}")
                    lines.append("")
            
            # 检查业绩预告
            preview = self.check_earnings_preview(symbol)
            if preview.get('has_preview'):
                emoji = "🟢" if preview['type'] == '预增' else "🔴" if preview['type'] == '预减' else "🟡"
                lines.append(f"{emoji} {symbol} 业绩预告: {preview['title'][:40]}")
                lines.append("")
        
        if len(lines) <= 3:
            lines.append("📭 近7天无重要财报公告")
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def check_annual_report_season(self) -> str:
        """检查年报季（1-4月）"""
        now = datetime.now()
        month = now.month
        
        if month in [1, 2, 3, 4]:
            return f"📅 当前是年报季（{month}月），关注各公司年报披露"
        elif month in [7, 8]:
            return "📅 当前是中报季（7-8月），关注半年报披露"
        elif month in [10]:
            return "📅 当前是三季报季（10月），关注三季报披露"
        else:
            return "📅 当前非财报密集披露期"


def main():
    """测试监控"""
    print("=" * 70)
    print("📊 财报公告监控系统")
    print("=" * 70)
    
    monitor = EarningsAnnouncementMonitor()
    
    # 检查财报季
    print("\n" + monitor.check_annual_report_season())
    
    # 监控公告
    print("\n" + monitor.monitor_all())
    
    print("\n" + "=" * 70)
    print("💡 使用建议:")
    print("   1. 年报季（1-4月）：重点关注全年业绩")
    print("   2. 一季报（4月）：看开年景气度")
    print("   3. 半年报（7-8月）：看中期趋势")
    print("   4. 三季报（10月）：看全年预告")
    print("=" * 70)


if __name__ == "__main__":
    main()
