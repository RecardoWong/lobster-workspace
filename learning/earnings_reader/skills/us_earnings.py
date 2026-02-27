#!/usr/bin/env python3
"""
美股财报抓取器 - Alpha Vantage版 (替换yfinance)
免费额度: 500次/天
"""

import os
import requests
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class USEarningsData:
    """美股财报数据结构"""
    ticker: str
    company_name: str
    market_cap: float  # 市值(亿美元)
    
    # 财务指标
    revenue: Optional[float] = None  # 营收(亿美元)
    revenue_growth: Optional[float] = None  # 营收增长%
    net_income: Optional[float] = None  # 净利润
    eps: Optional[float] = None  # EPS
    
    # 盈利能力
    gross_margin: Optional[float] = None  # 毛利率%
    operating_margin: Optional[float] = None  # 经营利润率%
    net_margin: Optional[float] = None  # 净利率%
    roe: Optional[float] = None  # ROE%
    roa: Optional[float] = None  # ROA%
    
    # 估值
    pe_trailing: Optional[float] = None  # 市盈率
    pb: Optional[float] = None  # 市净率
    ps: Optional[float] = None  # 市销率
    
    # 其他
    dividend_yield: Optional[float] = None  # 股息率%
    _52_week_high: Optional[float] = None
    _52_week_low: Optional[float] = None
    
    # 元数据
    data_source: str = "alpha_vantage"
    data_time: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'ticker': self.ticker,
            'company_name': self.company_name,
            'market_cap': self.market_cap,
            'revenue': self.revenue,
            'revenue_growth': self.revenue_growth,
            'net_income': self.net_income,
            'eps': self.eps,
            'gross_margin': self.gross_margin,
            'operating_margin': self.operating_margin,
            'net_margin': self.net_margin,
            'roe': self.roe,
            'roa': self.roa,
            'pe': self.pe_trailing,
            'pb': self.pb,
            'ps': self.ps,
            'dividend_yield': self.dividend_yield,
            'data_source': self.data_source,
            'data_time': self.data_time
        }


class USEarningsFetcher:
    """美股财报获取器 - Alpha Vantage"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_KEY')
        if not self.api_key:
            raise ValueError("需要提供Alpha Vantage API Key，或设置ALPHA_VANTAGE_KEY环境变量")
        self._last_request_time = 0
        self._min_interval = 1.2  # 每秒最多1次，留点余量
    
    def _rate_limit(self):
        """速率限制 - Alpha Vantage免费版限制每秒1次"""
        import time
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.time()
    
    def _rate_limit(self):
        """Alpha Vantage免费版限制：每秒1次请求"""
        import time
        elapsed = time.time() - self._last_request_time
        if elapsed < 1.2:  # 留点余量，用1.2秒
            time.sleep(1.2 - elapsed)
        self._last_request_time = time.time()
    
    def fetch(self, ticker: str) -> Optional[USEarningsData]:
        """
        获取美股财报数据
        
        Args:
            ticker: 股票代码，如 "AAPL", "NVDA"
            
        Returns:
            USEarningsData对象，失败返回None
        """
        # 速率限制
        self._rate_limit()
        
        try:
            # 获取公司概况
            params = {
                'function': 'OVERVIEW',
                'symbol': ticker,
                'apikey': self.api_key
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=15)
            data = response.json()
            
            if 'Symbol' not in data:
                error_msg = data.get('Note', data.get('Information', 'Unknown error'))
                print(f"[错误] 无法获取 {ticker} 数据: {error_msg}")
                return None
            
            # 解析数据
            def safe_float(value, default=0.0):
                """安全转换为float"""
                if value is None or value == 'None' or value == '':
                    return default
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return default
            
            market_cap = safe_float(data.get('MarketCapitalization'), 0) / 1e9
            
            result = USEarningsData(
                ticker=data.get('Symbol', ticker),
                company_name=data.get('Name', ticker),
                market_cap=market_cap,
                pe_trailing=safe_float(data.get('PERatio')) if data.get('PERatio') and data.get('PERatio') != 'None' else None,
                eps=safe_float(data.get('EPS')) if data.get('EPS') and data.get('EPS') != 'None' else None,
                pb=safe_float(data.get('PriceToBookRatio')) if data.get('PriceToBookRatio') and data.get('PriceToBookRatio') != 'None' else None,
                ps=safe_float(data.get('PriceToSalesRatioTTM')) if data.get('PriceToSalesRatioTTM') and data.get('PriceToSalesRatioTTM') != 'None' else None,
                roe=safe_float(data.get('ReturnOnEquityTTM'), 0) * 100 if data.get('ReturnOnEquityTTM') and data.get('ReturnOnEquityTTM') != 'None' else None,
                roa=safe_float(data.get('ReturnOnAssetsTTM'), 0) * 100 if data.get('ReturnOnAssetsTTM') and data.get('ReturnOnAssetsTTM') != 'None' else None,
                gross_margin=safe_float(data.get('GrossProfitTTM'), 0) / safe_float(data.get('RevenueTTM'), 1) * 100 
                    if data.get('GrossProfitTTM') and data.get('RevenueTTM') 
                    and data.get('GrossProfitTTM') != 'None' and data.get('RevenueTTM') != 'None' else None,
                operating_margin=safe_float(data.get('OperatingMarginTTM'), 0) * 100 
                    if data.get('OperatingMarginTTM') and data.get('OperatingMarginTTM') != 'None' else None,
                net_margin=safe_float(data.get('ProfitMargin'), 0) * 100 
                    if data.get('ProfitMargin') and data.get('ProfitMargin') != 'None' else None,
                dividend_yield=safe_float(data.get('DividendYield'), 0) * 100 
                    if data.get('DividendYield') and data.get('DividendYield') != 'None' else None,
                _52_week_high=safe_float(data.get('52WeekHigh')) if data.get('52WeekHigh') and data.get('52WeekHigh') != 'None' else None,
                _52_week_low=safe_float(data.get('52WeekLow')) if data.get('52WeekLow') and data.get('52WeekLow') != 'None' else None,
                data_time=datetime.now().isoformat()
            )
            
            print(f"[美股财报] {ticker} - {result.company_name} 数据获取成功")
            return result
            
        except Exception as e:
            print(f"[错误] 获取 {ticker} 财报失败: {e}")
            return None


# 测试
if __name__ == "__main__":
    import sys
    
    try:
        fetcher = USEarningsFetcher()
        
        # 测试几只股票
        test_tickers = ["AAPL", "NVDA", "TSLA"]
        
        for ticker in test_tickers:
            print(f"\n{'='*50}")
            data = fetcher.fetch(ticker)
            if data:
                print(f"公司: {data.company_name}")
                print(f"市值: ${data.market_cap:.1f}B")
                print(f"PE: {data.pe_trailing}")
                print(f"EPS: ${data.eps}")
                print(f"ROE: {data.roe:.1f}%" if data.roe else "ROE: N/A")
            else:
                print(f"获取 {ticker} 失败")
                
    except ValueError as e:
        print(f"配置错误: {e}")
        sys.exit(1)
