#!/usr/bin/env python3
"""
A股市场监控增强器 (基于 akshare)
整合龙虎榜、融资融券、资金流向、机构持仓等数据
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class AShareMarketMonitor:
    """A股市场监控增强器"""
    
    def __init__(self):
        pass
    
    # ========== 1. 龙虎榜数据 (游资/机构动向) ==========
    
    def get_dragon_tiger_list(self, date: str = None) -> pd.DataFrame:
        """
        获取龙虎榜数据
        看游资和机构的买卖动向
        """
        try:
            df = ak.stock_lhb_detail_daily_sina()
            return df
        except Exception as e:
            print(f"获取龙虎榜失败: {e}")
            return pd.DataFrame()
    
    def get_institution_trade(self, date: str = None) -> pd.DataFrame:
        """
        获取机构专用席位交易
        机构买卖动向
        """
        if not date:
            date = datetime.now().strftime('%Y%m%d')
        
        try:
            df = ak.stock_lhb_jgmx_sina(start_date=date, end_date=date)
            return df
        except Exception as e:
            return pd.DataFrame()
    
    # ========== 2. 融资融券数据 (市场情绪) ==========
    
    def get_margin_trading(self, market: str = 'szse') -> pd.DataFrame:
        """
        获取融资融券数据
        market: 'szse'=深市, 'sse'=沪市
        """
        try:
            if market == 'szse':
                df = ak.stock_margin_szse()
            else:
                df = ak.stock_margin_sse()
            return df
        except Exception as e:
            print(f"获取融资融券失败: {e}")
            return pd.DataFrame()
    
    def get_margin_detail(self, stock_code: str) -> pd.DataFrame:
        """获取个股融资融券明细"""
        try:
            if stock_code.startswith(('000', '001', '002', '300')):
                df = ak.stock_margin_detail_szse(date='')
            else:
                df = ak.stock_margin_detail_sse(date='')
            # 筛选该股票
            if '代码' in df.columns:
                df = df[df['代码'] == stock_code]
            return df
        except Exception as e:
            return pd.DataFrame()
    
    # ========== 3. 资金流向 (主力动向) ==========
    
    def get_fund_flow_industry(self) -> pd.DataFrame:
        """获取行业资金流向"""
        try:
            df = ak.stock_sector_fund_flow_rank()
            return df
        except Exception as e:
            print(f"获取行业资金流向失败: {e}")
            return pd.DataFrame()
    
    def get_fund_flow_stock(self, stock_code: str) -> pd.DataFrame:
        """获取个股资金流向"""
        try:
            df = ak.stock_individual_fund_flow(stock=stock_code, market="sh")
            return df
        except Exception as e:
            try:
                df = ak.stock_individual_fund_flow(stock=stock_code, market="sz")
                return df
            except:
                return pd.DataFrame()
    
    def get_main_fund_flow(self) -> pd.DataFrame:
        """获取主力资金流向"""
        try:
            df = ak.stock_main_fund_flow()
            return df
        except Exception as e:
            return pd.DataFrame()
    
    # ========== 4. 北向资金 (外资动向) ==========
    
    def get_northbound_fund_flow(self) -> pd.DataFrame:
        """获取北向资金流向 (沪深港通)"""
        try:
            df = ak.stock_hsgt_fund_flow_summary_em()
            return df
        except Exception as e:
            print(f"获取北向资金失败: {e}")
            return pd.DataFrame()
    
    # ========== 5. 大宗交易 (机构大额交易) ==========
    
    def get_block_trade(self) -> pd.DataFrame:
        """获取大宗交易数据"""
        try:
            df = ak.stock_dzjy_mrmx()
            return df
        except Exception as e:
            print(f"获取大宗交易失败: {e}")
            return pd.DataFrame()
    
    # ========== 6. 机构持仓 ==========
    
    def get_institute_hold(self, stock_code: str) -> pd.DataFrame:
        """获取机构持仓数据"""
        try:
            df = ak.stock_institute_hold(stock_code)
            return df
        except Exception as e:
            return pd.DataFrame()
    
    # ========== 7. 综合报告 ==========
    
    def get_market_sentiment_report(self) -> str:
        """获取市场情绪综合报告"""
        lines = [
            "📊 A股市场情绪报告",
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 60,
            ""
        ]
        
        # 1. 龙虎榜
        print("正在获取龙虎榜数据...")
        lhb = self.get_dragon_tiger_list()
        if not lhb.empty:
            lines.append(f"🔥 今日龙虎榜: {len(lhb)} 只股票上榜")
            lines.append("")
        
        # 2. 融资融券
        print("正在获取融资融券数据...")
        margin_sz = self.get_margin_trading('szse')
        if not margin_sz.empty:
            latest = margin_sz.iloc[0]
            lines.append(f"💰 深市融资融券:")
            lines.append(f"   融资余额: {latest.get('融资余额', 'N/A')}")
            lines.append(f"   融券余额: {latest.get('融券余额', 'N/A')}")
            lines.append("")
        
        # 3. 行业资金流向
        print("正在获取行业资金流向...")
        industry_flow = self.get_fund_flow_industry()
        if not industry_flow.empty:
            lines.append("📈 行业资金流向 (Top 5):")
            for _, row in industry_flow.head(5).iterrows():
                name = row.get('名称', 'N/A')
                flow = row.get('主力净流入', 'N/A')
                lines.append(f"   • {name}: {flow}")
            lines.append("")
        
        # 4. 北向资金
        print("正在获取北向资金...")
        northbound = self.get_northbound_fund_flow()
        if not northbound.empty:
            latest = northbound.iloc[0]
            lines.append("🌏 北向资金 (沪深港通):")
            lines.append(f"   净流入: {latest.get('净流入', 'N/A')}")
            lines.append("")
        
        lines.append("=" * 60)
        return "\n".join(lines)


def main():
    """测试"""
    print("=" * 70)
    print("📊 A股市场监控增强器 (akshare)")
    print("=" * 70)
    
    monitor = AShareMarketMonitor()
    
    # 市场情绪报告
    print("\n正在生成市场情绪报告...")
    print(monitor.get_market_sentiment_report())
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
