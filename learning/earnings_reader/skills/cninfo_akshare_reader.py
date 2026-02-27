#!/usr/bin/env python3
"""
巨潮资讯网公告抓取器 (基于 akshare)
无需 Cookie，无需登录
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class CNInfoAKShareReader:
    """巨潮资讯网公告读取器 (akshare版)"""
    
    def __init__(self):
        pass
    
    def get_announcements(self, stock_code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取公司公告
        
        Args:
            stock_code: 股票代码 (如 000001)
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
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
    
    def get_stock_dividend(self, stock_code: str) -> pd.DataFrame:
        """获取分红历史"""
        try:
            df = ak.stock_dividend_cninfo(symbol=stock_code)
            return df
        except Exception as e:
            return pd.DataFrame({'error': [str(e)]})
    
    def get_stock_allotment(self, stock_code: str) -> pd.DataFrame:
        """获取配股历史"""
        try:
            df = ak.stock_allotment_cninfo(symbol=stock_code)
            return df
        except Exception as e:
            return pd.DataFrame({'error': [str(e)]})
    
    def get_latest(self, stock_code: str, days: int = 30) -> pd.DataFrame:
        """获取最近N天的公告"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        return self.get_announcements(stock_code, start_date, end_date)
    
    def get_important_events(self, stock_code: str, days: int = 90) -> List[Dict]:
        """
        获取重大事项公告
        通过关键词筛选识别
        """
        df = self.get_announcements(stock_code, days=days)
        
        if df.empty:
            return []
        
        important_keywords = [
            '股权激励', '员工持股', '限制性股票',
            '增发', '发行', '可转债', '配股',
            '重大合同', '战略合作', '中标',
            '资产重组', '收购', '合并', '分立',
            '关联交易', '对外担保',
            '业绩预告', '业绩快报'
        ]
        
        events = []
        for _, row in df.iterrows():
            title = str(row.get('公告标题', ''))
            for keyword in important_keywords:
                if keyword in title:
                    events.append({
                        'date': row.get('公告时间', ''),
                        'title': title,
                        'type': keyword,
                        'link': row.get('公告链接', '')
                    })
                    break
        
        return events
    
    def get_equity_pledge(self, stock_code: str) -> pd.DataFrame:
        """获取股权质押信息"""
        try:
            # 通过公告筛选股权质押
            df = self.get_latest(stock_code, days=365)
            if df.empty:
                return df
            
            pledge_df = df[df['公告标题'].str.contains('质押', na=False)]
            return pledge_df
        except Exception as e:
            return pd.DataFrame()
    
    def format_report(self, stock_code: str, days: int = 30) -> str:
        """格式化输出报告"""
        df = self.get_latest(stock_code, days=days)
        
        if df.empty:
            return f"📋 {stock_code} 最近{days}天无公告"
        
        # 获取公司名称
        company_name = df.iloc[0].get('简称', stock_code) if not df.empty else stock_code
        
        lines = [
            f"📋 {company_name} ({stock_code}) 公告摘要",
            f"📅 {datetime.now().strftime('%Y-%m-%d')} | 共{len(df)}条",
            "=" * 60,
            ""
        ]
        
        # 重大事项
        events = self.get_important_events(stock_code, days)
        if events:
            lines.append(f"🔔 重大事项 ({len(events)}条):")
            for event in events[:5]:
                date = str(event['date'])[:10] if event['date'] else 'N/A'
                lines.append(f"   • [{date}] [{event['type']}] {event['title'][:40]}")
            lines.append("")
        
        # 最新公告
        lines.append("📄 最新公告:")
        for _, row in df.head(5).iterrows():
            date = str(row.get('公告时间', 'N/A'))[:10]
            title = row.get('公告标题', '')[:45]
            lines.append(f"   • [{date}] {title}")
        
        if len(df) > 5:
            lines.append(f"   ... 还有 {len(df) - 5} 条")
        
        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)


def main():
    """测试"""
    print("=" * 70)
    print("📋 巨潮资讯网公告抓取器 (akshare版)")
    print("   无需 Cookie，无需登录")
    print("=" * 70)
    
    reader = CNInfoAKShareReader()
    
    # 测试1: 平安银行
    print("\n📊 平安银行 (000001):")
    print("-" * 70)
    print(reader.format_report('000001', days=30))
    
    # 测试2: 分红历史
    print("\n💰 平安银行分红历史:")
    df = reader.get_stock_dividend('000001')
    if not df.empty:
        print(f"   共 {len(df)} 次分红")
        for _, row in df.head(3).iterrows():
            print(f"   • {row.get('报告时间', 'N/A')}: {row.get('实施方案分红说明', 'N/A')}")
    
    # 测试3: 宁德时代
    print("\n📊 宁德时代 (300750):")
    print("-" * 70)
    print(reader.format_report('300750', days=30))
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
