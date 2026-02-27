#!/usr/bin/env python3
"""
A股财报数据抓取器 (基于akshare + 巨潮资讯网)
获取A股公司公告、财务数据
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class AShareEarningsReader:
    """A股财报数据读取器"""
    
    def __init__(self):
        pass
    
    def get_company_info(self, stock_code: str) -> Dict:
        """获取公司基本信息"""
        try:
            # 使用东方财富获取实时行情
            df = ak.stock_zh_a_spot_em()
            company = df[df['代码'] == stock_code]
            
            if company.empty:
                return {'error': '未找到公司信息'}
            
            row = company.iloc[0]
            return {
                'code': stock_code,
                'name': row.get('名称', ''),
                'price': row.get('最新价', 0),
                'change_pct': row.get('涨跌幅', 0),
                'market_cap': row.get('总市值', 0),
                'pe_ratio': row.get('市盈率-动态', None),
                'pb_ratio': row.get('市净率', None),
                'source': '东方财富'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_dividend_history(self, stock_code: str) -> pd.DataFrame:
        """获取分红历史 (巨潮资讯网)"""
        try:
            df = ak.stock_dividend_cninfo(symbol=stock_code)
            return df
        except Exception as e:
            return pd.DataFrame({'error': [str(e)]})
    
    def get_allotment_history(self, stock_code: str) -> pd.DataFrame:
        """获取配股历史 (巨潮资讯网)"""
        try:
            df = ak.stock_allotment_cninfo(symbol=stock_code)
            return df
        except Exception as e:
            return pd.DataFrame({'error': [str(e)]})
    
    def get_stock_hold_change(self, stock_code: str) -> pd.DataFrame:
        """获取持股变动 (巨潮资讯网)"""
        try:
            # 这个接口可能不需要symbol参数，获取全部数据后筛选
            df = ak.stock_hold_change_cninfo()
            if 'code' in df.columns:
                df = df[df['code'] == stock_code]
            return df
        except Exception as e:
            return pd.DataFrame({'error': [str(e)]})
    
    def get_financial_report(self, stock_code: str, report_type: str = 'balance') -> pd.DataFrame:
        """
        获取财务报表
        
        Args:
            stock_code: 股票代码
            report_type: 'balance' (资产负债表), 'income' (利润表), 'cashflow' (现金流量表)
        """
        try:
            if report_type == 'balance':
                df = ak.stock_balance_sheet_by_report_em(symbol=stock_code)
            elif report_type == 'income':
                df = ak.stock_profit_sheet_by_report_em(symbol=stock_code)
            elif report_type == 'cashflow':
                df = ak.stock_cash_flow_sheet_by_report_em(symbol=stock_code)
            else:
                return pd.DataFrame({'error': ['未知报表类型']})
            return df
        except Exception as e:
            return pd.DataFrame({'error': [str(e)]})
    
    def get_main_indicators(self, stock_code: str) -> pd.DataFrame:
        """获取主要财务指标"""
        try:
            df = ak.stock_financial_analysis_indicator(symbol=stock_code)
            return df
        except Exception as e:
            return pd.DataFrame({'error': [str(e)]})
    
    def format_summary(self, stock_code: str) -> str:
        """格式化输出公司摘要"""
        # 基本信息
        info = self.get_company_info(stock_code)
        
        if 'error' in info:
            return f"❌ 获取失败: {info['error']}"
        
        lines = [
            f"📊 {info['name']} ({stock_code}) A股摘要",
            f"📅 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 60,
            ""
        ]
        
        # 实时行情
        lines.extend([
            "💹 实时行情 (东方财富)",
            f"   价格: ¥{info['price']}",
            f"   涨跌: {info['change_pct']}%",
            f"   市值: ¥{info['market_cap']:,.0f}" if info['market_cap'] else "   市值: N/A",
            f"   PE: {info['pe_ratio']}" if info['pe_ratio'] else "   PE: N/A",
            f"   PB: {info['pb_ratio']}" if info['pb_ratio'] else "   PB: N/A",
            ""
        ])
        
        # 分红历史
        dividend_df = self.get_dividend_history(stock_code)
        if not dividend_df.empty and 'error' not in dividend_df.columns:
            lines.append("💰 分红历史 (巨潮资讯网):")
            lines.append(f"   共 {len(dividend_df)} 次分红")
            if '实施方案分红说明' in dividend_df.columns:
                latest = dividend_df.iloc[0]
                lines.append(f"   最新: {latest.get('实施方案分红说明', 'N/A')}")
            lines.append("")
        
        # 财务指标
        indicator_df = self.get_main_indicators(stock_code)
        if not indicator_df.empty and 'error' not in indicator_df.columns:
            lines.append("📈 主要财务指标:")
            latest = indicator_df.iloc[0]
            if '净资产收益率' in latest:
                lines.append(f"   ROE: {latest['净资产收益率']}")
            if '销售毛利率' in latest:
                lines.append(f"   毛利率: {latest['销售毛利率']}")
            lines.append("")
        
        lines.append("=" * 60)
        return "\n".join(lines)


def main():
    """测试A股数据抓取"""
    print("=" * 60)
    print("📊 A股财报数据抓取器 (akshare + 巨潮资讯网)")
    print("=" * 60)
    
    reader = AShareEarningsReader()
    
    # 测试平安银行
    print("\n测试平安银行(000001):")
    print(reader.format_summary('000001'))
    
    print("\n" + "=" * 60)
    print("测试贵州茅台(600519):")
    print(reader.format_summary('600519'))
    
    print("\n" + "=" * 60)
    print("✅ akshare + 巨潮资讯网 数据抓取测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
