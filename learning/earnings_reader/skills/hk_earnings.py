#!/usr/bin/env python3
"""
港股财报抓取器 - 基于AkShare
完全免费，无需API Key
"""

import akshare as ak
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import time

@dataclass
class HKEarningsData:
    """港股财报数据结构"""
    code: str  # 港股代码，如 "00700"
    name: str  # 中文名称
    
    # 利润表
    revenue: Optional[float] = None  # 营收(亿港元)
    revenue_growth: Optional[float] = None  # 营收同比增长%
    net_profit: Optional[float] = None  # 净利润
    eps: Optional[float] = None  # EPS
    
    # 盈利能力
    gross_margin: Optional[float] = None  # 毛利率%
    net_margin: Optional[float] = None  # 净利率%
    roe: Optional[float] = None  # ROE%
    
    # 现金流
    operating_cash_flow: Optional[float] = None  # 经营现金流
    
    # 资产负债
    total_assets: Optional[float] = None  # 总资产
    total_liabilities: Optional[float] = None  # 总负债
    equity: Optional[float] = None  # 股东权益
    
    # 估值
    pe: Optional[float] = None  # 市盈率
    pb: Optional[float] = None  # 市净率
    market_cap: Optional[float] = None  # 市值(亿港元)
    
    # 元数据
    fiscal_year: str = ""  # 财年
    report_type: str = ""  # 报告类型(年报/中报/季报)
    data_source: str = "akshare"
    
    def to_dict(self) -> Dict:
        return {
            'code': self.code,
            'name': self.name,
            'revenue': self.revenue,
            'revenue_growth': self.revenue_growth,
            'net_profit': self.net_profit,
            'eps': self.eps,
            'gross_margin': self.gross_margin,
            'net_margin': self.net_margin,
            'roe': self.roe,
            'operating_cash_flow': self.operating_cash_flow,
            'total_assets': self.total_assets,
            'total_liabilities': self.total_liabilities,
            'equity': self.equity,
            'pe': self.pe,
            'pb': self.pb,
            'market_cap': self.market_cap,
            'fiscal_year': self.fiscal_year,
            'report_type': self.report_type,
            'data_source': self.data_source
        }


class HKEarningsFetcher:
    """港股财报获取器"""
    
    def __init__(self, rate_limit_delay: float = 1.0):
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0
    
    def _rate_limit(self):
        """速率限制"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()
    
    def fetch(self, code: str) -> Optional[HKEarningsData]:
        """
        获取港股财报数据
        
        Args:
            code: 港股代码，如 "00700"(腾讯), "09988"(阿里)
            
        Returns:
            HKEarningsData对象，失败返回None
        """
        try:
            self._rate_limit()
            
            # 确保代码格式正确 (去除.HK后缀)
            code = code.replace('.HK', '').replace('.hk', '')
            
            # 获取股票基本信息
            try:
                stock_info = ak.stock_hk_ggt_components_em()
                stock_row = stock_info[stock_info['代码'] == code]
                if not stock_row.empty:
                    name = stock_row.iloc[0].get('名称', code)
                else:
                    name = code
            except:
                name = code
            
            data = HKEarningsData(code=code, name=name)
            
            # 获取财务指标
            try:
                self._rate_limit()
                financial = ak.stock_financial_hk_em(symbol=code)
                if financial is not None and len(financial) > 0:
                    latest = financial.iloc[0]
                    data.fiscal_year = str(latest.get('报告期', ''))
                    data.report_type = str(latest.get('报表类型', ''))
                    
                    # 提取关键指标 (单位转换: 元→亿港元)
                    data.revenue = self._safe_float(latest.get('营业收入')) / 1e8 if latest.get('营业收入') else None
                    data.net_profit = self._safe_float(latest.get('净利润')) / 1e8 if latest.get('净利润') else None
                    data.eps = self._safe_float(latest.get('基本每股收益'))
                    data.total_assets = self._safe_float(latest.get('资产总额')) / 1e8 if latest.get('资产总额') else None
                    data.total_liabilities = self._safe_float(latest.get('负债总额')) / 1e8 if latest.get('负债总额') else None
                    data.equity = self._safe_float(latest.get('所有者权益')) / 1e8 if latest.get('所有者权益') else None
            except Exception as e:
                print(f"[警告] 获取财务数据失败: {e}")
            
            # 获取估值指标
            try:
                self._rate_limit()
                valuation = ak.stock_hk_valuation_em()
                stock_val = valuation[valuation['代码'] == code]
                if not stock_val.empty:
                    data.pe = self._safe_float(stock_val.iloc[0].get('市盈率'))
                    data.pb = self._safe_float(stock_val.iloc[0].get('市净率'))
                    data.market_cap = self._safe_float(stock_val.iloc[0].get('总市值')) / 1e8  # 转换为亿港元
            except Exception as e:
                print(f"[警告] 获取估值数据失败: {e}")
            
            # 计算衍生指标
            self._calculate_derived_metrics(data)
            
            print(f"[港股财报] {code} - {data.name} 数据获取成功")
            return data
            
        except Exception as e:
            print(f"[错误] 获取 {code} 港股财报失败: {e}")
            return None
    
    def _safe_float(self, value) -> Optional[float]:
        """安全转换为浮点数"""
        if value is None or value == '-' or value == '':
            return None
        try:
            return float(value)
        except:
            return None
    
    def _calculate_derived_metrics(self, data: HKEarningsData):
        """计算衍生指标"""
        # ROE = 净利润 / 股东权益
        if data.net_profit and data.equity and data.equity != 0:
            data.roe = (data.net_profit / data.equity) * 100
        
        # 净利率 = 净利润 / 营收
        if data.net_profit and data.revenue and data.revenue != 0:
            data.net_margin = (data.net_profit / data.revenue) * 100


# 测试运行
if __name__ == "__main__":
    fetcher = HKEarningsFetcher(rate_limit_delay=2.0)
    
    # 测试港股
    test_codes = ["00700", "09988"]  # 腾讯, 阿里
    
    for code in test_codes:
        print(f"\n{'='*50}")
        data = fetcher.fetch(code)
        if data:
            print(f"公司: {data.name} ({data.code})")
            print(f"市值: {data.market_cap:.0f}亿港元" if data.market_cap else "市值: N/A")
            print(f"PE: {data.pe}")
            print(f"PB: {data.pb}")
            print(f"营收: {data.revenue:.2f}亿港元" if data.revenue else "营收: N/A")
        else:
            print(f"获取 {code} 失败")
