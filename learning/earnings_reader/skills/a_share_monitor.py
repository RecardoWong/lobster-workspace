#!/usr/bin/env python3
"""
A股公告监控方案
使用东方财富作为巨潮资讯网的替代方案
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

class AShareNewsMonitor:
    """A股公告监控器"""
    
    def __init__(self):
        pass
    
    def get_company_news(self, stock_code: str) -> pd.DataFrame:
        """
        获取公司新闻 (东方财富)
        """
        try:
            df = ak.stock_news_em(symbol=stock_code)
            return df
        except Exception as e:
            print(f"获取新闻失败: {e}")
            return pd.DataFrame()
    
    def get_stock_changes(self, stock_code: str) -> pd.DataFrame:
        """
        获取龙虎榜数据 (东方财富)
        显示机构/游资买卖情况
        """
        try:
            df = ak.stock_lhb_detail_daily_sina()
            # 筛选该股票
            if '代码' in df.columns:
                df = df[df['代码'] == stock_code]
            return df
        except Exception as e:
            return pd.DataFrame()
    
    def get_institutional_holdings(self, stock_code: str) -> pd.DataFrame:
        """
        获取机构持仓 (东方财富)
        """
        try:
            df = ak.stock_institute_hold(symbol=stock_code)
            return df
        except Exception as e:
            return pd.DataFrame()
    
    def get_main_indicators(self, stock_code: str) -> dict:
        """
        获取主要指标摘要
        """
        try:
            df = ak.stock_zh_a_spot_em()
            company = df[df['代码'] == stock_code]
            
            if company.empty:
                return {'error': '未找到公司'}
            
            row = company.iloc[0]
            return {
                '代码': stock_code,
                '名称': row.get('名称', ''),
                '价格': row.get('最新价', 0),
                '涨跌': row.get('涨跌幅', 0),
                '市值': row.get('总市值', 0),
                'PE': row.get('市盈率-动态', None),
                'PB': row.get('市净率', None),
                '换手率': row.get('换手率', 0),
                '成交额': row.get('成交额', 0)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def format_monitor_report(self, stock_code: str) -> str:
        """格式化监控报告"""
        # 基本信息
        info = self.get_main_indicators(stock_code)
        
        if 'error' in info:
            return f"❌ {info['error']}"
        
        lines = [
            f"📊 {info['名称']} ({stock_code}) 监控报告",
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 60,
            ""
        ]
        
        # 实时行情
        lines.extend([
            "💹 实时行情 (东方财富)",
            f"   价格: ¥{info['价格']}",
            f"   涨跌: {info['涨跌']}%",
            f"   市值: ¥{info['市值']:,.0f}" if info['市值'] else "   市值: N/A",
            f"   PE: {info['PE']}" if info['PE'] else "   PE: N/A",
            f"   换手率: {info['换手率']}%",
            ""
        ])
        
        # 新闻
        news_df = self.get_company_news(stock_code)
        if not news_df.empty:
            lines.append("📰 最新新闻:")
            for _, row in news_df.head(3).iterrows():
                title = row.get('新闻标题', '')[:45]
                lines.append(f"   • {title}")
            lines.append("")
        
        lines.append("=" * 60)
        return "\n".join(lines)


def main():
    """测试"""
    print("=" * 60)
    print("📊 A股监控方案 (东方财富数据源)")
    print("=" * 60)
    
    monitor = AShareNewsMonitor()
    
    # 测试
    print("\n📈 平安银行 (000001):")
    print(monitor.format_monitor_report('000001'))
    
    print("\n📈 宁德时代 (300750):")
    print(monitor.format_monitor_report('300750'))
    
    print("\n" + "=" * 60)
    print("💡 说明:")
    print("   巨潮资讯网API需要登录态")
    print("   使用东方财富作为替代方案")
    print("=" * 60)


if __name__ == "__main__":
    main()
