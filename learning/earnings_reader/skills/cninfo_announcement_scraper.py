#!/usr/bin/env python3
"""
巨潮资讯网公告抓取器
抓取各类公告：定期报告、重大事项、股权变动、监管函等
"""

import urllib.request
import urllib.parse
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class CNInfoAnnoucementScraper:
    """巨潮资讯网公告抓取器"""
    
    def __init__(self):
        self.base_url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'http://www.cninfo.com.cn/new/disclosure/stock'
        }
    
    def get_announcements(self, 
                         stock_code: str,
                         page_num: int = 1,
                         page_size: int = 30,
                         start_date: str = None,
                         end_date: str = None,
                         category: str = None) -> pd.DataFrame:
        """
        获取公司公告
        
        Args:
            stock_code: 股票代码 (如 000001)
            page_num: 页码
            page_size: 每页数量
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            category: 公告类别 (可选)
            
        Returns:
            DataFrame
        """
        # 判断板块
        if stock_code.startswith(('000', '001', '002', '003', '300', '301')):
            column, plate = "szse", "sz"
        elif stock_code.startswith(('600', '601', '602', '603', '605', '688')):
            column, plate = "sse", "sh"
        elif stock_code.startswith(('8', '4')):
            column, plate = "bj", "bj"
        else:
            column, plate = "szse", "sz"
        
        secid = f"{plate}{stock_code}"
        
        params = {
            'pageNum': str(page_num),
            'pageSize': str(page_size),
            'tabName': 'fullAnnouncement',
            'column': column,
            'stock': stock_code,
            'searchkey': '',
            'secid': secid,
            'plate': plate,
            'category': category or 'category_all_szsh',
            'trade': '',
            'startTime': start_date or '',
            'endTime': end_date or '',
            'sortName': '',
            'sortType': ''
        }
        
        data = urllib.parse.urlencode(params).encode('utf-8')
        
        try:
            req = urllib.request.Request(self.base_url, data=data, headers=self.headers, method='POST')
            with urllib.request.urlopen(req, timeout=20) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            announcements = result.get('announcements', [])
            if not announcements:
                return pd.DataFrame()
            
            # 提取关键字段
            data_list = []
            for ann in announcements:
                data_list.append({
                    '公告标题': ann.get('announcementTitle', ''),
                    '公告时间': ann.get('announcementTime', ''),
                    '公告类型': self._get_category_name(ann.get('columnId', '')),
                    '下载链接': f"http://static.cninfo.com.cn/{ann.get('adjunctUrl', '')}",
                    '公告ID': ann.get('announcementId', '')
                })
            
            return pd.DataFrame(data_list)
            
        except Exception as e:
            print(f"错误: {e}")
            return pd.DataFrame()
    
    def _get_category_name(self, column_id: str) -> str:
        """根据columnId获取类别名称"""
        categories = {
            'szse': '深市公告',
            'sse': '沪市公告',
            'bj': '北交所公告',
            'szseMain': '深主板',
            'szseGem': '创业板',
            'sseMain': '沪主板',
            'sseKcp': '科创板'
        }
        return categories.get(column_id, '其他')
    
    def get_latest_announcements(self, stock_code: str, days: int = 7) -> pd.DataFrame:
        """获取最近N天的公告"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        return self.get_announcements(stock_code, start_date=start_date, end_date=end_date)
    
    def filter_by_keywords(self, df: pd.DataFrame, keywords: List[str]) -> pd.DataFrame:
        """按关键词过滤公告"""
        if df.empty:
            return df
        
        pattern = '|'.join(keywords)
        return df[df['公告标题'].str.contains(pattern, na=False, case=False)]


def main():
    """测试公告抓取"""
    print("=" * 70)
    print("📋 巨潮资讯网公告抓取器")
    print("=" * 70)
    
    scraper = CNInfoAnnoucementScraper()
    
    # 测试1: 获取平安银行最新公告
    print("\n📊 平安银行 (000001) 最近公告:")
    df = scraper.get_latest_announcements('000001', days=30)
    if not df.empty:
        print(f"   共 {len(df)} 条公告")
        for _, row in df.head(5).iterrows():
            print(f"   • [{row['公告时间'][:10]}] {row['公告标题'][:50]}")
    else:
        print("   暂无公告数据")
    
    # 测试2: 按关键词过滤
    print("\n🔍 筛选'业绩'相关公告:")
    if not df.empty:
        filtered = scraper.filter_by_keywords(df, ['业绩', '年报', '季报', '财报'])
        if not filtered.empty:
            for _, row in filtered.head(3).iterrows():
                print(f"   • {row['公告标题'][:50]}")
        else:
            print("   无业绩相关公告")
    
    # 测试3: 获取贵州茅台
    print("\n📊 贵州茅台 (600519) 最近公告:")
    df = scraper.get_latest_announcements('600519', days=30)
    if not df.empty:
        print(f"   共 {len(df)} 条公告")
        for _, row in df.head(5).iterrows():
            print(f"   • [{row['公告时间'][:10]}] {row['公告标题'][:50]}")
    else:
        print("   暂无公告数据")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
