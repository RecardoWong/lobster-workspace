#!/usr/bin/env python3
"""
巨潮资讯网公告抓取器 (带Cookie版)
使用用户提供的Cookie抓取公告
"""

import os
import urllib.request
import urllib.parse
import json
import pandas as pd
from datetime import datetime, timedelta

class CNInfoScraperWithCookie:
    """巨潮资讯网公告抓取器 (Cookie版)"""
    
    def __init__(self):
        self.base_url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
        self.cookie = os.environ.get('CNINFO_COOKIE', '')
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'http://www.cninfo.com.cn/new/disclosure/stock',
            'Cookie': self.cookie
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
            category: 公告类别 (category_zj_szsh=重大事项, category_zqszq=增发, 等)
            
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
                    '代码': ann.get('secCode', ''),
                    '简称': ann.get('secName', ''),
                    '公告标题': ann.get('announcementTitle', ''),
                    '公告时间': ann.get('announcementTime', ''),
                    '公告类型': self._get_category_name(ann.get('columnId', '')),
                    '公告ID': ann.get('announcementId', ''),
                    '链接': f"http://static.cninfo.com.cn/{ann.get('adjunctUrl', '')}"
                })
            
            return pd.DataFrame(data_list)
            
        except Exception as e:
            print(f"❌ 错误: {e}")
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
    
    def get_important_events(self, stock_code: str, days: int = 30) -> pd.DataFrame:
        """获取重大事项公告"""
        return self.get_announcements(
            stock_code, 
            category='category_zj_szsh',
            start_date=(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            end_date=datetime.now().strftime('%Y-%m-%d')
        )
    
    def get_equity_pledge(self, stock_code: str, days: int = 30) -> pd.DataFrame:
        """获取股权质押公告"""
        return self.get_announcements(
            stock_code,
            category='category_gqzy_szsh',
            start_date=(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            end_date=datetime.now().strftime('%Y-%m-%d')
        )
    
    def get_hold_change(self, stock_code: str, days: int = 30) -> pd.DataFrame:
        """获取增减持公告"""
        return self.get_announcements(
            stock_code,
            category='category_zjc_szsh',
            start_date=(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            end_date=datetime.now().strftime('%Y-%m-%d')
        )
    
    def format_report(self, stock_code: str, days: int = 7) -> str:
        """格式化输出报告"""
        df = self.get_latest_announcements(stock_code, days)
        
        if df.empty:
            return f"📋 {stock_code} 最近{days}天无公告\n   (Cookie可能已过期或该股票无公告)"
        
        lines = [
            f"📋 {df.iloc[0].get('简称', stock_code)} ({stock_code}) 公告",
            f"📅 {datetime.now().strftime('%Y-%m-%d')} | 共{len(df)}条",
            "=" * 60,
            ""
        ]
        
        for _, row in df.head(10).iterrows():
            date = str(row.get('公告时间', 'N/A'))[:10]
            title = row.get('公告标题', '')[:50]
            lines.append(f"   • [{date}] {title}")
        
        if len(df) > 10:
            lines.append(f"   ... 还有 {len(df) - 10} 条")
        
        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)


def main():
    """测试抓取"""
    print("=" * 70)
    print("📋 巨潮资讯网公告抓取器 (Cookie版)")
    print("=" * 70)
    
    scraper = CNInfoScraperWithCookie()
    
    if not scraper.cookie:
        print("\n❌ 未找到 Cookie!")
        print("   请设置环境变量 CNINFO_COOKIE")
        return
    
    print(f"\n✅ Cookie 已加载 (长度: {len(scraper.cookie)})")
    
    # 测试1: 平安银行
    print("\n📊 平安银行 (000001) 最新公告:")
    print("-" * 70)
    print(scraper.format_report('000001', days=30))
    
    # 测试2: 重大事项
    print("\n📊 平安银行 重大事项:")
    print("-" * 70)
    df = scraper.get_important_events('000001')
    if not df.empty:
        print(f"找到 {len(df)} 条重大事项")
        for _, row in df.head(5).iterrows():
            print(f"   • {row.get('公告标题', '')[:50]}")
    else:
        print("暂无重大事项")
    
    # 测试3: 股权质押
    print("\n📊 平安银行 股权质押:")
    print("-" * 70)
    df = scraper.get_equity_pledge('000001')
    if not df.empty:
        print(f"找到 {len(df)} 条股权质押公告")
    else:
        print("暂无股权质押公告")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
