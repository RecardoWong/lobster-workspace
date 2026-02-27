#!/usr/bin/env python3
"""
A股财报抓取器 - 基于AkShare
完全免费，无需API Key
"""

import akshare as ak
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import time

@dataclass
class CNEarningsData:
    """A股财报数据结构"""
    code: str  # A股代码，如 "000001"
    name: str  # 中文名称
    
    # 利润表
    revenue: Optional[float] = None  # 营收(亿元)
    revenue_growth: Optional[float] = None  # 营收同比增长%
    net_profit: Optional[float] = None  # 净利润
    net_profit_growth: Optional[float] = None  # 净利润同比增长%
    eps: Optional[float] = None  # EPS
    
    # 盈利能力
    gross_margin: Optional[float] = None  # 毛利率%
    net_margin: Optional[float] = None  # 净利率%
    roe: Optional[float] = None  # ROE%
    roa: Optional[float] = None  # ROA%
    
    # 现金流
    operating_cash_flow: Optional[float] = None  # 经营现金流
    investing_cash_flow: Optional[float] = None  # 投资现金流
    financing_cash_flow: Optional[float] = None  # 筹资现金流
    
    # 资产负债
    total_assets: Optional[float] = None  # 总资产
    total_liabilities: Optional[float] = None  # 总负债
    equity: Optional[float] = None  # 股东权益
    current_ratio: Optional[float] = None  # 流动比率
    debt_ratio: Optional[float] = None  # 资产负债率%
    
    # 估值
    pe: Optional[float] = None  # 市盈率
    pb: Optional[float] = None  # 市净率
    market_cap: Optional[float] = None  # 市值(亿元)
    
    # 元数据
    fiscal_year: str = ""  # 财年
    report_type: str = ""  # 报告类型
    data_source: str = "akshare"
    
    def to_dict(self) -> Dict:
        return {
            'code': self.code,
            'name': self.name,
            'revenue': self.revenue,
            'revenue_growth': self.revenue_growth,
            'net_profit': self.net_profit,
            'net_profit_growth': self.net_profit_growth,
            'eps': self.eps,
            'gross_margin': self.gross_margin,
            'net_margin': self.net_margin,
            'roe': self.roe,
            'roa': self.roa,
            'operating_cash_flow': self.operating_cash_flow,
            'total_assets': self.total_assets,
            'debt_ratio': self.debt_ratio,
            'pe': self.pe,
            'pb': self.pb,
            'market_cap': self.market_cap,
            'data_source': self.data_source
        }


class CNEarningsFetcher:
    """A股财报获取器"""
    
    def __init__(self, rate_limit_delay: float = 1.0):
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0
    
    def _rate_limit(self):
        """速率限制"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()
    
    def fetch(self, code: str) -> Optional[CNEarningsData]:
        """
        获取A股财报数据
        
        Args:
            code: A股代码，如 "000001"(平安银行), "600519"(茅台)
            
        Returns:
            CNEarningsData对象，失败返回None
        """
        try:
            self._rate_limit()
            
            # 确保代码格式正确
            code = code.replace('.SH', '').replace('.SZ', '').replace('.sh', '').replace('.sz', '')
            
            # 判断市场
            if code.startswith('6'):
                market = 'sh'
            elif code.startswith('0') or code.startswith('3'):
                market = 'sz'
            else:
                market = 'sh'  # 默认
            
            full_code = f"{market}{code}"
            
            # 获取股票基本信息
            try:
                stock_info = ak.stock_zh_a_spot_em()
                stock_row = stock_info[stock_info['代码'] == code]
                if not stock_row.empty:
                    name = stock_row.iloc[0].get('名称', code)
                    data = CNEarningsData(
                        code=code,
                        name=name,
                        pe=self._safe_float(stock_row.iloc[0].get('市盈率')),
                        pb=self._safe_float(stock_row.iloc[0].get('市净率')),
                        market_cap=self._safe_float(stock_row.iloc[0].get('总市值')) / 1e8  # 转为亿元
                    )
                else:
                    data = CNEarningsData(code=code, name=code)
            except:
                data = CNEarningsData(code=code, name=code)
            
            # 获取财务指标 (主要)
            try:
                self._rate_limit()
                # 获取最新财务数据
                financial = ak.stock_financial_report_em(stock=code, symbol="主要指标")
                if financial is not None and len(financial) > 0:
                    latest = financial.iloc[0]
                    data.fiscal_year = str(latest.get('报告期', ''))
                    data.report_type = str(latest.get('报表类型', ''))
                    
                    # 提取关键指标 (单位: 元，需要转为亿元)
                    data.revenue = self._safe_float(latest.get('营业收入')) / 1e8 if latest.get('营业收入') else None
                    data.revenue_growth = self._safe_float(latest.get('营业收入同比增长率'))
                    data.net_profit = self._safe_float(latest.get('净利润')) / 1e8 if latest.get('净利润') else None
                    data.net_profit_growth = self._safe_float(latest.get('净利润同比增长率'))
                    data.eps = self._safe_float(latest.get('摊薄每股收益'))
                    data.roe = self._safe_float(latest.get('净资产收益率'))
                    data.net_margin = self._safe_float(latest.get('销售净利率'))
                    data.gross_margin = self._safe_float(latest.get('销售毛利率'))
                    data.debt_ratio = self._safe_float(latest.get('资产负债率'))
            except Exception as e:
                print(f"[警告] 获取财务指标失败: {e}")
            
            # 获取资产负债表数据
            try:
                self._rate_limit()
                balance = ak.stock_financial_report_em(stock=code, symbol="资产负债表")
                if balance is not None and len(balance) > 0:
                    latest = balance.iloc[0]
                    data.total_assets = self._safe_float(latest.get('资产总计')) / 1e8 if latest.get('资产总计') else None
                    data.total_liabilities = self._safe_float(latest.get('负债合计')) / 1e8 if latest.get('负债合计') else None
                    data.equity = self._safe_float(latest.get('所有者权益合计')) / 1e8 if latest.get('所有者权益合计') else None
            except Exception as e:
                print(f"[警告] 获取资产负债表失败: {e}")
            
            # 获取现金流数据
            try:
                self._rate_limit()
                cashflow = ak.stock_financial_report_em(stock=code, symbol="现金流量表")
                if cashflow is not None and len(cashflow) > 0:
                    latest = cashflow.iloc[0]
                    data.operating_cash_flow = self._safe_float(latest.get('经营活动产生的现金流量净额')) / 1e8 if latest.get('经营活动产生的现金流量净额') else None
            except Exception as e:
                print(f"[警告] 获取现金流失败: {e}")
            
            # 计算衍生指标
            self._calculate_derived_metrics(data)
            
            print(f"[A股财报] {code} - {data.name} 数据获取成功")
            return data
            
        except Exception as e:
            print(f"[错误] 获取 {code} A股财报失败: {e}")
            return None
    
    def _safe_float(self, value) -> Optional[float]:
        """安全转换为浮点数"""
        if value is None or value == '-' or value == '' or value == '—':
            return None
        try:
            return float(value)
        except:
            return None
    
    def _calculate_derived_metrics(self, data: CNEarningsData):
        """计算衍生指标"""
        # ROA = 净利润 / 总资产
        if data.net_profit and data.total_assets and data.total_assets != 0:
            data.roa = (data.net_profit / data.total_assets) * 100


# 测试运行
if __name__ == "__main__":
    fetcher = CNEarningsFetcher(rate_limit_delay=2.0)
    
    # 测试A股
    test_codes = ["600519", "000001"]  # 茅台, 平安银行
    
    for code in test_codes:
        print(f"\n{'='*50}")
        data = fetcher.fetch(code)
        if data:
            print(f"公司: {data.name} ({data.code})")
            print(f"市值: {data.market_cap:.0f}亿元" if data.market_cap else "市值: N/A")
            print(f"PE: {data.pe}")
            print(f"PB: {data.pb}")
            print(f"ROE: {data.roe:.2f}%" if data.roe else "ROE: N/A")
        else:
            print(f"获取 {code} 失败")
