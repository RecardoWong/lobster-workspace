#!/usr/bin/env python3
"""
财报深度研究系统
每天早上8点自动分析前一天发布的所有重要财报
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import sys
sys.path.insert(0, '/root/.openclaw/workspace/learning/earnings_reader/skills')

class EarningsResearchSystem:
    """财报深度研究系统"""
    
    def __init__(self):
        # 重点关注的行业/板块
        self.priority_sectors = {
            '半导体': ['688981', '603501', '002371'],  # 中芯国际、韦尔、北方华创
            '新能源': ['300750', '002594', '601012'],  # 宁德时代、比亚迪、隆基
            'AI算力': ['02577'],  # 英诺赛科
            '白酒': ['600519', '000858'],  # 茅台、五粮液
            '银行': ['000001', '600036'],  # 平安、招行
        }
    
    def get_yesterday_announcements(self) -> pd.DataFrame:
        """获取昨天发布的重要公告"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        
        # 获取全市场昨天的公告（通过akshare）
        all_announcements = []
        
        # 尝试获取公告
        try:
            # 通过东方财富获取昨日公告
            df = ak.stock_zt_pool_em(date=yesterday)
            if not df.empty:
                all_announcements.append(df)
        except:
            pass
        
        # 或者通过个股逐个查询
        for sector, stocks in self.priority_sectors.items():
            for stock in stocks:
                try:
                    df = ak.stock_zh_a_disclosure_report_cninfo(
                        symbol=stock,
                        start_date=yesterday,
                        end_date=yesterday
                    )
                    if not df.empty:
                        df['sector'] = sector
                        all_announcements.append(df)
                except:
                    continue
        
        if all_announcements:
            return pd.concat(all_announcements, ignore_index=True)
        return pd.DataFrame()
    
    def analyze_earnings_report(self, symbol: str, title: str) -> Dict:
        """深度分析一份财报"""
        analysis = {
            'symbol': symbol,
            'title': title,
            'type': self._classify_report(title),
            'key_points': [],
            'risks': [],
            'recommendation': ''
        }
        
        # 1. 分类报告类型
        report_type = analysis['type']
        
        # 2. 提取关键信息（基于标题关键词）
        if '预增' in title or '增长' in title:
            analysis['key_points'].append('✅ 业绩预增，可能超预期')
        elif '预减' in title or '下滑' in title:
            analysis['key_points'].append('⚠️ 业绩预减，需关注原因')
        elif '亏损' in title:
            analysis['key_points'].append('🚨 出现亏损，风险较高')
        
        if '分红' in title or '派息' in title:
            analysis['key_points'].append('💰 有分红方案，关注股息率')
        
        if '增发' in title or '融资' in title:
            analysis['key_points'].append('📈 融资计划，关注资金用途')
        
        if '并购' in title or '收购' in title:
            analysis['key_points'].append('🔄 并购事项，关注协同效应')
        
        if '减持' in title:
            analysis['risks'].append('⚠️ 股东减持，短期承压')
        
        if '质押' in title:
            analysis['risks'].append('⚠️ 股权质押，关注风险')
        
        # 3. 生成建议
        if len(analysis['key_points']) > len(analysis['risks']):
            analysis['recommendation'] = '值得关注'
        elif len(analysis['risks']) > 0:
            analysis['recommendation'] = '谨慎观察'
        else:
            analysis['recommendation'] = '中性'
        
        return analysis
    
    def _classify_report(self, title: str) -> str:
        """分类报告类型"""
        if '年报' in title:
            return '年报'
        elif '半年报' in title or '中报' in title:
            return '半年报'
        elif '一季报' in title or 'Q1' in title:
            return '一季报'
        elif '三季报' in title or 'Q3' in title:
            return '三季报'
        elif '业绩预告' in title:
            return '业绩预告'
        elif '业绩快报' in title:
            return '业绩快报'
        elif '分红' in title or '派息' in title:
            return '分红方案'
        elif '增减持' in title or '减持' in title:
            return '增减持'
        elif '质押' in title:
            return '股权质押'
        elif '增发' in title or '融资' in title:
            return '融资计划'
        else:
            return '其他公告'
    
    def generate_daily_report(self) -> str:
        """生成每日财报研究报告"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        lines = [
            f"📊 财报深度研究报告",
            f"📅 日期：{yesterday}",
            f"⏰ 生成时间：{datetime.now().strftime('%H:%M')}",
            f"{'='*70}",
            ""
        ]
        
        # 获取昨天公告
        df = self.get_yesterday_announcements()
        
        if df.empty:
            lines.extend([
                "📭 昨日无重要财报公告",
                "",
                f"{'='*70}"
            ])
            return "\n".join(lines)
        
        # 按类型分类
        important_types = ['年报', '半年报', '业绩预告', '分红方案']
        
        lines.append(f"📈 昨日共发现 {len(df)} 条公告\n")
        
        # 重点分析重要公告
        for _, row in df.iterrows():
            symbol = row.get('代码', 'N/A')
            title = row.get('公告标题', 'N/A')
            sector = row.get('sector', '其他')
            
            analysis = self.analyze_earnings_report(symbol, title)
            
            # 只输出重要类型的详细分析
            if analysis['type'] in important_types:
                lines.extend([
                    f"\n🔍 {symbol} ({sector}) - {analysis['type']}",
                    f"   标题：{title[:60]}",
                    f"   亮点："
                ])
                
                for point in analysis['key_points'][:3]:
                    lines.append(f"      {point}")
                
                if analysis['risks']:
                    lines.append(f"   风险：")
                    for risk in analysis['risks'][:2]:
                        lines.append(f"      {risk}")
                
                lines.append(f"   建议：{analysis['recommendation']}")
                lines.append(f"   {'-'*60}")
        
        lines.extend([
            "",
            f"{'='*70}",
            "💡 今日操作建议：",
            "   1. 关注业绩预增个股的机会",
            "   2. 避开业绩暴雷或大股东减持的个股",
            "   3. 年报季重点关注分红方案",
            f"{'='*70}"
        ])
        
        return "\n".join(lines)


def main():
    """主函数 - 每天早上运行"""
    print("=" * 70)
    print("📊 财报深度研究系统")
    print("=" * 70)
    
    research = EarningsResearchSystem()
    report = research.generate_daily_report()
    
    print(report)
    
    # 保存到文件
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    filename = f"/root/.openclaw/workspace/memory/earnings_research_{yesterday}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n💾 报告已保存: {filename}")


if __name__ == "__main__":
    main()
