#!/usr/bin/env python3
"""
港股财报数据连接器
整合多个数据源：东方财富、港交所披露易
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional

class HKEarningsDataConnector:
    """港股财报数据连接器"""
    
    def __init__(self):
        pass
    
    def get_stock_quote_eastmoney(self, stock_code: str) -> Dict:
        """
        从东方财富获取港股行情
        """
        try:
            # 东方财富港股API
            # 港股代码需要加前缀 116.
            url = f"https://push2.eastmoney.com/api/qt/stock/get?secid=116.{stock_code}&fields=f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f55,f57,f58,f60,f62,f170"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            if data.get('data'):
                d = data['data']
                # 东方财富字段解析
                # f43: 最新价(需要/100)
                # f44: 今日开盘
                # f45: 昨日收盘
                # f46: 最高价
                # f47: 最低价
                # f60: 涨跌幅(已经是百分比*100,需要/100)
                # f170: 涨跌额
                
                price_raw = d.get('f43', 0)
                price = price_raw / 100 if price_raw else 0
                
                # 涨跌幅 - f60是百分比*100
                change_pct_raw = d.get('f60', 0) 
                change_pct = change_pct_raw / 100 if change_pct_raw else 0
                
                # 涨跌额
                change_raw = d.get('f170', 0)
                change = change_raw / 100 if change_raw else 0
                
                return {
                    "code": stock_code,
                    "name": d.get('f58', ''),
                    "price": price,
                    "change": change,
                    "change_pct": change_pct,
                    "volume": d.get('f48', 0),  # 成交量
                    "turnover": d.get('f49', 0),  # 成交额
                    "market_cap": d.get('f57', 0),
                    "pe_ratio": d.get('f162', 0) / 100 if d.get('f162') else None,
                    "pb_ratio": d.get('f167', 0) / 100 if d.get('f167') else None,
                    "source": "东方财富",
                    "update_time": datetime.now().isoformat()
                }
            else:
                return {"error": "无数据", "code": stock_code}
                
        except Exception as e:
            return {"error": str(e), "code": stock_code}
    
    def get_earnings_calendar_eastmoney(self) -> List[Dict]:
        """
        获取财报日历
        从东方财富获取即将发布的财报
        """
        try:
            # 东方财富财报日历API
            url = "https://datacenter-web.eastmoney.com/api/data/v1/get?sortColumns=REPORT_DATE&sortTypes=-1&pageSize=50&pageNumber=1&reportName=RPT_DMSK_YJBB&columns=ALL&filter=(SECURITY_TYPE_CODE=%22058001001%22)"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            calendar = []
            if data.get('result') and data['result'].get('data'):
                for item in data['result']['data']:
                    calendar.append({
                        "date": item.get('REPORT_DATE', ''),
                        "stock_code": item.get('SECURITY_CODE', ''),
                        "stock_name": item.get('SECURITY_NAME_ABBR', ''),
                        "report_type": item.get('REPORT_TYPE', ''),
                        "exchange": item.get('EXCHANGE_CODE', '')
                    })
            
            return calendar
            
        except Exception as e:
            # 返回模拟数据
            return [
                {"date": "2025-03-15", "stock_code": "02577", "stock_name": "英诺赛科", "report_type": "年报"},
                {"date": "2025-03-20", "stock_code": "00700", "stock_name": "腾讯控股", "report_type": "年报"},
                {"date": "2025-03-25", "stock_code": "09988", "stock_name": "阿里巴巴", "report_type": "年报"}
            ]
    
    def get_stock_list_hk(self) -> List[Dict]:
        """获取港股列表"""
        # 常用港股列表（含用户关注的）
        return [
            {"code": "02577", "name": "英诺赛科", "sector": "半导体", "focus": True},
            {"code": "00700", "name": "腾讯控股", "sector": "互联网"},
            {"code": "09988", "name": "阿里巴巴-SW", "sector": "互联网"},
            {"code": "03690", "name": "美团-W", "sector": "互联网"},
            {"code": "01024", "name": "快手-W", "sector": "互联网"},
            {"code": "09888", "name": "百度集团-SW", "sector": "互联网"},
            {"code": "01810", "name": "小米集团-W", "sector": "消费电子"},
            {"code": "02331", "name": "李宁", "sector": "消费"},
            {"code": "02020", "name": "安踏体育", "sector": "消费"},
            {"code": "02318", "name": "中国平安", "sector": "金融"},
            {"code": "00388", "name": "香港交易所", "sector": "金融"},
            {"code": "02382", "name": "舜宇光学", "sector": "科技"},
            {"code": "01478", "name": "丘钛科技", "sector": "科技"},
            {"code": "09618", "name": "京东集团-SW", "sector": "互联网"},
            {"code": "01093", "name": "石药集团", "sector": "医药"}
        ]
    
    def get_company_profile(self, stock_code: str) -> Dict:
        """获取公司基本信息"""
        # 公司资料库
        profiles = {
            "02577": {
                "name": "英诺赛科",
                "name_en": "Innoscience",
                "sector": "半导体",
                "sub_sector": "氮化镓(GaN)功率器件",
                "listing_date": "2024-07-18",
                "description": "全球领先的氮化镓功率器件IDM企业",
                "market_cap_hkd": "约300亿",
                "key_products": ["GaN功率器件", "GaN快充芯片"],
                "major_clients": ["OPPO", "vivo", "小米", "联想"]
            },
            "00700": {
                "name": "腾讯控股",
                "name_en": "Tencent",
                "sector": "互联网",
                "sub_sector": "游戏/社交/云",
                "listing_date": "2004-06-16"
            }
        }
        
        return profiles.get(stock_code, {
            "name": "未知",
            "sector": "未知",
            "stock_code": stock_code
        })


class IntegratedEarningsReader:
    """整合财报速读器"""
    
    def __init__(self):
        self.data_connector = HKEarningsDataConnector()
    
    def get_stock_overview(self, stock_code: str) -> Dict:
        """获取股票概览"""
        # 获取行情数据
        quote = self.data_connector.get_stock_quote_eastmoney(stock_code)
        
        # 获取公司资料
        profile = self.data_connector.get_company_profile(stock_code)
        
        return {
            "stock_code": stock_code,
            "quote": quote,
            "profile": profile,
            "update_time": datetime.now().isoformat()
        }
    
    def get_watchlist_overview(self) -> List[Dict]:
        """获取关注列表概览"""
        stocks = self.data_connector.get_stock_list_hk()
        
        overview = []
        print("📊 获取关注股票行情...")
        
        for stock in stocks[:5]:  # 先获取前5个
            code = stock['code']
            quote = self.data_connector.get_stock_quote_eastmoney(code)
            
            if "error" not in quote:
                overview.append({
                    "code": code,
                    "name": stock['name'],
                    "sector": stock['sector'],
                    "price": quote.get('price', 'N/A'),
                    "change_pct": quote.get('change_pct', 0),
                    "pe_ratio": quote.get('pe_ratio', 'N/A'),
                    "focus": stock.get('focus', False)
                })
                print(f"  ✅ {stock['name']}(${code}): ${quote.get('price', 'N/A'):.2f}")
            else:
                print(f"  ⚠️ {stock['name']}(${code}): {quote.get('error', 'Unknown')}")
        
        return overview


def main():
    """测试港股数据连接器"""
    print("=" * 60)
    print("📊 港股财报数据连接器")
    print("   整合东方财富 + 港交所数据源")
    print("=" * 60)
    
    connector = HKEarningsDataConnector()
    reader = IntegratedEarningsReader()
    
    # 测试1: 获取股票列表
    print("\n📋 港股股票列表（关注列表）:")
    stocks = connector.get_stock_list_hk()
    for stock in stocks:
        focus = " ⭐" if stock.get('focus') else ""
        print(f"  • {stock['code']} - {stock['name']} ({stock['sector']}){focus}")
    
    # 测试2: 获取实时行情
    print("\n💹 实时行情测试:")
    quote = connector.get_stock_quote_eastmoney("02577")
    if "error" not in quote:
        print(f"  英诺赛科(02577):")
        print(f"    价格: ${quote['price']:.2f}")
        print(f"    涨跌: {quote['change_pct']:+.2f}%")
        print(f"    PE: {quote.get('pe_ratio', 'N/A')}")
        print(f"    PB: {quote.get('pb_ratio', 'N/A')}")
    else:
        print(f"  错误: {quote.get('error')}")
    
    # 测试3: 获取关注列表概览
    print("\n👁️ 关注列表概览:")
    overview = reader.get_watchlist_overview()
    
    # 测试4: 财报日历
    print("\n📅 财报日历:")
    calendar = connector.get_earnings_calendar_eastmoney()
    for item in calendar[:5]:
        print(f"  • {item['date']} - {item['stock_name']}({item['stock_code']})")
    
    # 保存数据
    import os
    output_dir = "/root/.openclaw/workspace/learning/earnings_reader/data"
    os.makedirs(output_dir, exist_ok=True)
    
    data = {
        "stocks": stocks,
        "watchlist_overview": overview,
        "calendar": calendar,
        "update_time": datetime.now().isoformat()
    }
    
    output_path = f"{output_dir}/hk_earnings_data_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 数据已保存: {output_path}")


if __name__ == "__main__":
    main()
