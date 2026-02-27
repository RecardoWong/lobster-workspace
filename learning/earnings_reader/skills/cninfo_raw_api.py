#!/usr/bin/env python3
"""
巨潮资讯网公告API (直接使用，不依赖akshare包装)
"""

import urllib.request
import urllib.parse
import json
import pandas as pd
from datetime import datetime, timedelta

class CNInfoRawAPI:
    """巨潮资讯网原始API"""
    
    def __init__(self):
        self.base_url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest'
        }
    
    def get_announcements(self, stock_code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取公告"""
        
        # 判断板块
        if stock_code.startswith(('000', '001', '002', '003', '300', '301')):
            column, plate = "szse", "sz"
        elif stock_code.startswith(('600', '601', '602', '603', '605', '688')):
            column, plate = "sse", "sh"
        elif stock_code.startswith(('8', '4')):
            column, plate = "bj", "bj"
        else:
            column, plate = "szse", "sz"
        
        params = {
            'pageNum': '1',
            'pageSize': '30',
            'tabName': 'fullAnnouncement',
            'column': column,
            'stock': stock_code,
            'searchkey': '',
            'secid': f'{plate}{stock_code}',
            'plate': plate,
            'category': 'category_all_szsh',
            'startTime': start_date or '',
            'endTime': end_date or ''
        }
        
        data = urllib.parse.urlencode(params).encode('utf-8')
        
        try:
            req = urllib.request.Request(self.base_url, data=data, headers=self.headers, method='POST')
            with urllib.request.urlopen(req, timeout=20) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            announcements = result.get('announcements', [])
            if not announcements:
                return pd.DataFrame()
            
            data_list = []
            for ann in announcements:
                data_list.append({
                    '代码': ann.get('secCode', ''),
                    '简称': ann.get('secName', ''),
                    '公告标题': ann.get('announcementTitle', ''),
                    '公告时间': ann.get('announcementTime', '')
                })
            
            return pd.DataFrame(data_list)
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            return pd.DataFrame()
    
    def format_output(self, stock_code: str, days: int = 30) -> str:
        """格式化输出"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        df = self.get_announcements(stock_code, start_date, end_date)
        
        if df.empty:
            return f"📋 {stock_code} 暂无公告数据\n   (巨潮API返回空，可能需要登录态)"
        
        lines = [
            f"📋 {stock_code} 公告 ({len(df)}条)",
            "=" * 50
        ]
        
        for _, row in df.head(10).iterrows():
            date = str(row.get('公告时间', 'N/A'))[:10]
            title = row.get('公告标题', '')[:45]
            lines.append(f"   • [{date}] {title}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    print("=" * 60)
    print("📋 巨潮资讯网公告API测试")
    print("=" * 60)
    
    api = CNInfoRawAPI()
    
    print("\n1. 平安银行 (000001):")
    print(api.format_output('000001'))
    
    print("\n2. 贵州茅台 (600519):")
    print(api.format_output('600519'))
    
    print("\n" + "=" * 60)
    print("💡 说明: 巨潮API返回空数据可能是反爬机制，")
    print("   建议使用akshare的替代数据源")
    print("=" * 60)
