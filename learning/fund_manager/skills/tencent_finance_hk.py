#!/usr/bin/env python3
"""
腾讯财经港股数据获取
更稳定的港股数据源
"""

import urllib.request
from datetime import datetime

def get_hk_stock_quote_tencent(stock_code):
    """
    从腾讯财经获取港股行情
    """
    try:
        url = f"https://qt.gtimg.cn/q=hk{stock_code}"
        
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode('gbk', errors='ignore')
        
        # 解析数据
        # 格式: v_hk02577="100~英诺赛科~02577~61.600~62.800~63.000~...";
        if 'v_hk' in data and '"' in data:
            start = data.find('"') + 1
            end = data.rfind('"')
            content = data[start:end]
            parts = content.split('~')
            
            if len(parts) >= 35:
                # 安全获取字段
                def safe_float(parts, idx, default=0):
                    if idx < len(parts) and parts[idx]:
                        try:
                            return float(parts[idx])
                        except:
                            return default
                    return default
                
                return {
                    "code": stock_code,
                    "name": parts[1] if len(parts) > 1 else "",
                    "price": safe_float(parts, 3),
                    "prev_close": safe_float(parts, 4),
                    "open": safe_float(parts, 5),
                    "volume": safe_float(parts, 6),
                    "change": safe_float(parts, 31),  # 涨跌额
                    "change_pct": safe_float(parts, 32),  # 涨跌幅%
                    "high": safe_float(parts, 33),
                    "low": safe_float(parts, 34),
                    "market_cap_total": safe_float(parts, 45),  # 总市值
                    "market_cap_float": safe_float(parts, 44),   # 流通市值
                    "source": "腾讯财经",
                    "update_time": datetime.now().isoformat()
                }
        
        return {"error": "无法解析数据", "raw": data[:100]}
        
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print("🔍 腾讯财经 - 港股实时行情")
    print("=" * 60)
    
    # 格式化市值显示
    def format_market_cap(cap):
        if cap >= 10000:
            return f"{cap/10000:.2f}万亿"
        else:
            return f"{cap:.2f}亿"
    
    # 测试英诺赛科
    result = get_hk_stock_quote_tencent("02577")
    if "error" not in result:
        print(f"\n📊 英诺赛科 (02577)")
        print(f"   名称: {result['name']}")
        print(f"   价格: ${result['price']:.3f}")
        print(f"   涨跌: {result['change']:+.3f} ({result['change_pct']:+.2f}%)")
        print(f"   成交量: {result['volume']:,.0f}")
        print(f"   总市值: {format_market_cap(result['market_cap_total'])} HKD")
        print(f"   流通市值: {format_market_cap(result['market_cap_float'])} HKD")
    else:
        print(f"❌ 错误: {result.get('error')}")
    
    # 测试腾讯
    result = get_hk_stock_quote_tencent("00700")
    if "error" not in result:
        print(f"\n📊 腾讯控股 (00700)")
        print(f"   名称: {result['name']}")
        print(f"   价格: ${result['price']:.2f}")
        print(f"   涨跌: {result['change']:+.2f} ({result['change_pct']:+.2f}%)")
        print(f"   总市值: {format_market_cap(result['market_cap_total'])} HKD")
        print(f"   流通市值: {format_market_cap(result['market_cap_float'])} HKD")
    
    # 测试阿里
    result = get_hk_stock_quote_tencent("09988")
    if "error" not in result:
        print(f"\n📊 阿里巴巴 (09988)")
        print(f"   名称: {result['name']}")
        print(f"   价格: ${result['price']:.2f}")
        print(f"   涨跌: {result['change']:+.2f} ({result['change_pct']:+.2f}%)")
        print(f"   总市值: {format_market_cap(result['market_cap_total'])} HKD")
        print(f"   流通市值: {format_market_cap(result['market_cap_float'])} HKD")
