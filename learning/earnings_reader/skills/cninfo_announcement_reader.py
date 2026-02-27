#!/usr/bin/env python3
"""
巨潮资讯网公告抓取器 (基于akshare)
抓取A股各类公告：定期报告、重大事项、股权变动等
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class CNInfoAnnoucementReader:
    """巨潮资讯网公告读取器"""
    
    def __init__(self):
        pass
    
    def get_announcements(self, stock_code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取公司公告
        
        Args:
            stock_code: 股票代码 (如 000001)
            start_date: 开始日期 (YYYY-MM-DD)，默认30天前
            end_date: 结束日期 (YYYY-MM-DD)，默认今天
            
        Returns:
            DataFrame
        """
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        try:
            df = ak.stock_zh_a_disclosure_report_cninfo(
                symbol=stock_code,
                start_date=start_date,
                end_date=end_date
            )
            return df
        except Exception as e:
            print(f"获取公告失败: {e}")
            return pd.DataFrame()
    
    def get_latest(self, stock_code: str, days: int = 7) -> pd.DataFrame:
        """获取最近N天的公告"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        return self.get_announcements(stock_code, start_date, end_date)
    
    def get_important_announcements(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        筛选重要公告
        包括：业绩报告、重大合同、股权变动、增减持、定增等
        """
        if df.empty or '公告标题' not in df.columns:
            return pd.DataFrame()
        
        keywords = [
            '年度报告', '半年度报告', '季度报告',
            '业绩', '净利润', '营收',
            '重大合同', '中标',
            '股权变动', '增持', '减持',
            '定向增发', '非公开发行',
            '收购', '重组', '合并',
            '停牌', '复牌',
            '分红', '送转',
            '关联交易'
        ]
        
        pattern = '|'.join(keywords)
        return df[df['公告标题'].str.contains(pattern, na=False, case=False)]
    
    def format_summary(self, stock_code: str, days: int = 7) -> str:
        """格式化输出公告摘要"""
        df = self.get_latest(stock_code, days)
        
        if df.empty:
            return f"📋 {stock_code} 最近{days}天无公告"
        
        # 获取公司名称
        company_name = df.iloc[0].get('简称', stock_code) if not df.empty else stock_code
        
        lines = [
            f"📋 {company_name} ({stock_code}) 最近公告 ({len(df)}条)",
            f"📅 {datetime.now().strftime('%Y-%m-%d')}",
            "=" * 60,
            ""
        ]
        
        # 重要公告
        important = self.get_important_announcements(df)
        if not important.empty:
            lines.append("🔔 重要公告:")
            for _, row in important.head(5).iterrows():
                title = row.get('公告标题', '')[:40]
                date = row.get('公告时间', 'N/A')
                if len(str(date)) > 10:
                    date = str(date)[:10]
                lines.append(f"   • [{date}] {title}")
            lines.append("")
        
        # 其他公告
        lines.append("📄 全部公告:")
        for _, row in df.head(5).iterrows():
            title = row.get('公告标题', '')[:40]
            date = row.get('公告时间', 'N/A')
            if len(str(date)) > 10:
                date = str(date)[:10]
            lines.append(f"   • [{date}] {title}")
        
        if len(df) > 5:
            lines.append(f"   ... 还有 {len(df) - 5} 条公告")
        
        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)


def main():
    """测试公告抓取"""
    print("=" * 70)
    print("📋 巨潮资讯网公告抓取器 (akshare)")
    print("=" * 70)
    
    reader = CNInfoAnnoucementReader()
    
    # 测试1: 平安银行
    print("\n📊 平安银行 (000001) 最近公告:")
    print("-" * 70)
    print(reader.format_summary('000001', days=30))
    
    # 测试2: 贵州茅台
    print("\n📊 贵州茅台 (600519) 最近公告:")
    print("-" * 70)
    print(reader.format_summary('600519', days=30))
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
