#!/usr/bin/env python3
"""
新浪财经港股数据连接器
从新浪财经获取港股实时行情和财报数据
"""

import json
import urllib.request
from datetime import datetime
from typing import Dict, List, Optional

class SinaFinanceConnector:
    """新浪财经数据连接器"""
    
    def __init__(self):
        self.base_url = "https://hq.sinajs.cn"
    
    def get_hk_stock_quote(self, stock_code: str) -> Dict:
        """
        获取港股实时行情
        新浪港股代码格式: hk02577
        """
        try:
            url = f"{self.base_url}/list=hk{stock_code}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://finance.sina.com.cn'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode('gb2312', errors='ignore')
            
            # 解析数据
            # 格式: var hq_str_hk02577="英诺赛科,30.750,31.000,30.450,31.450,30.450,30.750,30.800,1864877.000,58250682.000,145000,30.750,10000,30.700,197000,30.650,20000,30.600,94000,30.550,2000,30.800,32000,30.850,2000,30.900,8000,30.950,18000,31.000,2025-02-21,16:08:54,00";
            
            if 'hq_str_hk' in data and '"' in data:
                # 提取引号内的数据
                start = data.find('"') + 1
                end = data.rfind('"')
                content = data[start:end]
                
                parts = content.split(',')
                if len(parts) >= 30:
                    return {
                        "code": stock_code,
                        "name": parts[0],
                        "price": float(parts[6]) if parts[6] else 0,  # 最新价
                        "open": float(parts[2]) if parts[2] else 0,
                        "high": float(parts[4]) if parts[4] else 0,
                        "low": float(parts[5]) if parts[5] else 0,
                        "prev_close": float(parts[3]) if parts[3] else 0,
                        "change": float(parts[6]) - float(parts[3]) if parts[6] and parts[3] else 0,
                        "change_pct": (float(parts[6]) - float(parts[3])) / float(parts[3]) * 100 if parts[6] and parts[3] and float(parts[3]) != 0 else 0,
                        "volume": int(float(parts[12])) if parts[12] else 0,
                        "turnover": float(parts[11]) if parts[11] else 0,
                        "date": parts[30] if len(parts) > 30 else '',
                        "time": parts[31] if len(parts) > 31 else '',
                        "source": "新浪财经",
                        "update_time": datetime.now().isoformat()
                    }
            
            return {"error": "无法解析数据", "raw": data[:200], "code": stock_code}
            
        except Exception as e:
            return {"error": str(e), "code": stock_code}
    
    def get_us_stock_quote(self, symbol: str) -> Dict:
        """
        获取美股实时行情
        新浪美股代码格式: gb_nvda
        """
        try:
            url = f"{self.base_url}/list=gb_{symbol.lower()}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://finance.sina.com.cn'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode('gb2312', errors='ignore')
            
            # 解析美股数据
            if 'hq_str_gb_' in data and '"' in data:
                start = data.find('"') + 1
                end = data.rfind('"')
                content = data[start:end]
                parts = content.split(',')
                
                if len(parts) >= 5:
                    return {
                        "symbol": symbol.upper(),
                        "name": parts[0],
                        "price": float(parts[1]) if parts[1] else 0,
                        "change": float(parts[2]) if parts[2] else 0,
                        "change_pct": float(parts[3]) if parts[3] else 0,
                        "volume": int(float(parts[4])) if parts[4] else 0,
                        "source": "新浪财经",
                        "update_time": datetime.now().isoformat()
                    }
            
            return {"error": "无法解析数据", "raw": data[:200], "symbol": symbol}
            
        except Exception as e:
            return {"error": str(e), "symbol": symbol}
    
    def get_index_quote(self, index_code: str) -> Dict:
        """
        获取指数行情
        """
        try:
            # 指数代码映射
            index_map = {
                "nasdaq": "ixic",    # 纳斯达克
                "dji": "dji",        # 道琼斯
                "sp500": "inx",      # 标普500
                "hsi": "hsi",        # 恒生指数
            }
            
            code = index_map.get(index_code.lower(), index_code.lower())
            url = f"{self.base_url}/list={code}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://finance.sina.com.cn'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode('gb2312', errors='ignore')
            
            # 解析指数数据
            if 'hq_str_' in data and '"' in data:
                start = data.find('"') + 1
                end = data.rfind('"')
                content = data[start:end]
                parts = content.split(',')
                
                if len(parts) >= 3:
                    return {
                        "index": index_code,
                        "name": parts[0],
                        "price": float(parts[1]) if parts[1] else 0,
                        "change": float(parts[2]) if parts[2] else 0,
                        "change_pct": float(parts[3]) if len(parts) > 3 and parts[3] else 0,
                        "source": "新浪财经",
                        "update_time": datetime.now().isoformat()
                    }
            
            return {"error": "无法解析数据", "raw": data[:200], "index": index_code}
            
        except Exception as e:
            return {"error": str(e), "index": index_code}
    
    def get_batch_quotes(self, stock_codes: List[str], market: str = "hk") -> List[Dict]:
        """
        批量获取行情
        """
        results = []
        
        if market == "hk":
            for code in stock_codes:
                quote = self.get_hk_stock_quote(code)
                results.append(quote)
        elif market == "us":
            for symbol in stock_codes:
                quote = self.get_us_stock_quote(symbol)
                results.append(quote)
        
        return results


def main():
    """测试新浪财经数据连接器"""
    print("=" * 60)
    print("📊 新浪财经数据连接器")
    print("=" * 60)
    
    connector = SinaFinanceConnector()
    
    # 测试港股
    print("\n📈 港股实时行情:")
    hk_stocks = ["02577", "00700", "09988", "03690", "01810"]
    
    for code in hk_stocks:
        quote = connector.get_hk_stock_quote(code)
        if "error" not in quote:
            change_pct = quote.get('change_pct', 0)
            emoji = "🟢" if change_pct > 0 else "🔴" if change_pct < 0 else "⚪"
            print(f"  {emoji} {quote['name']}({code}): ${quote['price']:.3f} ({change_pct:+.2f}%)")
        else:
            print(f"  ⚠️ {code}: {quote.get('error', 'Unknown')}")
    
    # 测试美股
    print("\n💹 美股实时行情:")
    us_stocks = ["NVDA", "AMD", "TSLA", "AAPL", "MSFT"]
    
    for symbol in us_stocks:
        quote = connector.get_us_stock_quote(symbol)
        if "error" not in quote:
            change_pct = quote.get('change_pct', 0)
            emoji = "🟢" if change_pct > 0 else "🔴" if change_pct < 0 else "⚪"
            print(f"  {emoji} {quote['name']}({symbol}): ${quote['price']:.2f} ({change_pct:+.2f}%)")
        else:
            print(f"  ⚠️ {symbol}: {quote.get('error', 'Unknown')}")
    
    # 测试指数
    print("\n📊 指数行情:")
    indices = ["nasdaq", "dji", "hsi"]
    
    for idx in indices:
        quote = connector.get_index_quote(idx)
        if "error" not in quote:
            change_pct = quote.get('change_pct', 0)
            emoji = "🟢" if change_pct > 0 else "🔴" if change_pct < 0 else "⚪"
            print(f"  {emoji} {quote['name']}: {quote['price']:,.2f} ({change_pct:+.2f}%)")
        else:
            print(f"  ⚠️ {idx}: {quote.get('error', 'Unknown')}")
    
    # 保存数据
    print("\n💾 保存数据...")
    import os
    output_dir = "/root/.openclaw/workspace/learning/fund_manager/data"
    os.makedirs(output_dir, exist_ok=True)
    
    data = {
        "hk_stocks": [connector.get_hk_stock_quote(c) for c in hk_stocks],
        "us_stocks": [connector.get_us_stock_quote(s) for s in us_stocks],
        "indices": [connector.get_index_quote(i) for i in indices],
        "update_time": datetime.now().isoformat()
    }
    
    output_path = f"{output_dir}/sina_finance_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存: {output_path}")


if __name__ == "__main__":
    main()
