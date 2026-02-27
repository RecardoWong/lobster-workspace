#!/usr/bin/env python3
"""
美股财报抓取器 - 基于yfinance
完全免费，无需API Key
"""

import yfinance as yf
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
import time

@dataclass
class USEarningsData:
    """美股财报数据结构"""
    ticker: str
    company_name: str
    market_cap: float  # 市值(美元)
    
    # 利润表 (最近季度)
    revenue: Optional[float] = None  # 营收
    revenue_growth: Optional[float] = None  # 营收同比增长%
    net_income: Optional[float] = None  # 净利润
    eps: Optional[float] = None  # EPS
    eps_beat: Optional[float] = None  # EPS超预期
    
    # 盈利能力
    gross_margin: Optional[float] = None  # 毛利率%
    operating_margin: Optional[float] = None  # 经营利润率%
    net_margin: Optional[float] = None  # 净利率%
    roe: Optional[float] = None  # ROE%
    roa: Optional[float] = None  # ROA%
    
    # 现金流
    operating_cash_flow: Optional[float] = None  # 经营现金流
    free_cash_flow: Optional[float] = None  # 自由现金流
    
    # 估值
    pe_trailing: Optional[float] = None  # 市盈率(TTM)
    pe_forward: Optional[float] = None  # 预测市盈率
    pb: Optional[float] = None  # 市净率
    ps: Optional[float] = None  # 市销率
    
    # 财务健康
    total_debt: Optional[float] = None  # 总负债
    total_cash: Optional[float] = None  # 现金
    current_ratio: Optional[float] = None  # 流动比率
    
    # 元数据
    fiscal_quarter: str = ""  # 财报季度
    report_date: Optional[datetime] = None  # 报告日期
    data_source: str = "yfinance"
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'ticker': self.ticker,
            'company_name': self.company_name,
            'market_cap': self.market_cap,
            'revenue': self.revenue,
            'revenue_growth': self.revenue_growth,
            'net_income': self.net_income,
            'eps': self.eps,
            'eps_beat': self.eps_beat,
            'gross_margin': self.gross_margin,
            'operating_margin': self.operating_margin,
            'net_margin': self.net_margin,
            'roe': self.roe,
            'roa': self.roa,
            'operating_cash_flow': self.operating_cash_flow,
            'free_cash_flow': self.free_cash_flow,
            'pe_trailing': self.pe_trailing,
            'pe_forward': self.pe_forward,
            'pb': self.pb,
            'ps': self.ps,
            'total_debt': self.total_debt,
            'total_cash': self.total_cash,
            'current_ratio': self.current_ratio,
            'fiscal_quarter': self.fiscal_quarter,
            'data_source': self.data_source
        }


class USEarningsFetcher:
    """美股财报获取器"""
    
    def __init__(self, rate_limit_delay: float = 2.0):
        """
        初始化
        Args:
            rate_limit_delay: 请求间隔(秒)，避免触发限流
        """
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0
    
    def _rate_limit(self):
        """简单的速率限制"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()
    
    def fetch(self, ticker: str) -> Optional[USEarningsData]:
        """
        获取美股财报数据
        
        Args:
            ticker: 股票代码，如 "AAPL", "NVDA"
            
        Returns:
            USEarningsData对象，失败返回None
        """
        try:
            self._rate_limit()
            
            # 创建Ticker对象
            stock = yf.Ticker(ticker)
            
            # 获取基本信息
            info = stock.info
            if not info:
                print(f"[错误] 无法获取 {ticker} 的基本信息")
                return None
            
            # 创建数据对象
            data = USEarningsData(
                ticker=ticker.upper(),
                company_name=info.get('longName', ticker),
                market_cap=info.get('marketCap', 0)
            )
            
            # 利润表数据
            data.revenue = info.get('totalRevenue')
            data.net_income = info.get('netIncomeToCommon')
            data.eps = info.get('trailingEps')
            
            # 盈利能力
            data.gross_margin = info.get('grossMargins', 0) * 100 if info.get('grossMargins') else None
            data.operating_margin = info.get('operatingMargins', 0) * 100 if info.get('operatingMargins') else None
            data.net_margin = info.get('profitMargins', 0) * 100 if info.get('profitMargins') else None
            data.roe = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else None
            data.roa = info.get('returnOnAssets', 0) * 100 if info.get('returnOnAssets') else None
            
            # 现金流
            data.operating_cash_flow = info.get('operatingCashflow')
            data.free_cash_flow = info.get('freeCashflow')
            
            # 估值
            data.pe_trailing = info.get('trailingPE')
            data.pe_forward = info.get('forwardPE')
            data.pb = info.get('priceToBook')
            data.ps = info.get('priceToSalesTrailing12Months')
            
            # 财务健康
            data.total_debt = info.get('totalDebt')
            data.total_cash = info.get('totalCash')
            data.current_ratio = info.get('currentRatio')
            
            # 尝试获取季度财务数据
            self._enrich_with_quarterly_data(stock, data)
            
            print(f"[美股财报] {ticker} - {data.company_name} 数据获取成功")
            return data
            
        except Exception as e:
            print(f"[错误] 获取 {ticker} 财报失败: {e}")
            return None
    
    def _enrich_with_quarterly_data(self, stock: yf.Ticker, data: USEarningsData):
        """用季度财报数据补充信息"""
        try:
            # 获取季度利润表
            quarterly_financials = stock.quarterly_financials
            if quarterly_financials is not None and not quarterly_financials.empty:
                # 获取最近季度
                latest_quarter = quarterly_financials.columns[0]
                data.fiscal_quarter = str(latest_quarter)
                
                # 提取营收增长 (如果有多个季度数据)
                if len(quarterly_financials.columns) >= 2:
                    current_revenue = quarterly_financials.loc.get('Total Revenue', [None, None])[0]
                    prev_revenue = quarterly_financials.loc.get('Total Revenue', [None, None])[1]
                    if current_revenue and prev_revenue and prev_revenue != 0:
                        data.revenue_growth = ((current_revenue - prev_revenue) / prev_revenue) * 100
                        
        except Exception as e:
            print(f"[警告] 获取季度数据失败: {e}")


# 测试运行
if __name__ == "__main__":
    fetcher = USEarningsFetcher(rate_limit_delay=3.0)
    
    # 测试几只股票
    test_tickers = ["AAPL", "NVDA", "TSLA"]
    
    for ticker in test_tickers:
        print(f"\n{'='*50}")
        data = fetcher.fetch(ticker)
        if data:
            print(f"公司: {data.company_name}")
            print(f"市值: ${data.market_cap/1e9:.1f}B")
            print(f"PE: {data.pe_trailing}")
            print(f"EPS: ${data.eps}")
            print(f"毛利率: {data.gross_margin:.1f}%" if data.gross_margin else "毛利率: N/A")
        else:
            print(f"获取 {ticker} 失败")
