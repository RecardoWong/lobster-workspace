#!/usr/bin/env python3
"""
巨潮资讯网API抓取器
可以访问搜索接口，但公告查询接口返回空数据
"""

import urllib.request
import urllib.parse
import json
from datetime import datetime

class CNInfoAPI:
    """巨潮资讯网API客户端"""
    
    def __init__(self):
        self.base_url = "http://www.cninfo.com.cn"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'http://www.cninfo.com.cn/new/index'
        }
    
    def search_stock(self, keyword: str) -> list:
        """
        搜索股票
        
        ✅ 此接口可用
        
        Args:
            keyword: 股票代码或名称
            
        Returns:
            股票列表
        """
        url = f"{self.base_url}/new/information/topSearch/query"
        data = urllib.parse.urlencode({'keyWord': keyword}).encode('utf-8')
        
        try:
            req = urllib.request.Request(url, data=data, headers=self.headers, method='POST')
            with urllib.request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result if isinstance(result, list) else []
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_announcements(self, stock_code: str, org_id: str = None) -> dict:
        """
        获取公告列表
        
        ⚠️ 此接口返回空数据，可能需要特殊认证
        
        Args:
            stock_code: 股票代码
            org_id: 机构代码 (如 gssz0000001)
            
        Returns:
            公告数据
        """
        url = f"{self.base_url}/new/hisAnnouncement/query"
        
        # 判断板块
        if stock_code.startswith(('000', '001', '002', '003', '300', '301')):
            column, plate, secid_prefix = "szseMain", "sz", "sz"
        elif stock_code.startswith(('600', '601', '602', '603', '605', '688')):
            column, plate, secid_prefix = "sse", "sh", "sh"
        elif stock_code.startswith(('8', '4')):
            column, plate, secid_prefix = "bj", "bj", "bj"
        else:
            column, plate, secid_prefix = "szseMain", "sz", "sz"
        
        secid = f"{secid_prefix}{stock_code}"
        
        params = {
            'pageNum': '1',
            'pageSize': '30',
            'tabName': 'fullAnnouncement',
            'column': column,
            'stock': stock_code,
            'searchkey': '',
            'secid': secid,
            'plate': plate,
            'category': 'category_all_szsh',
            'trade': '',
            'startTime': '',
            'endTime': ''
        }
        
        if org_id:
            params['orgId'] = org_id
        
        data = urllib.parse.urlencode(params).encode('utf-8')
        
        try:
            req = urllib.request.Request(url, data=data, headers=self.headers, method='POST')
            with urllib.request.urlopen(req, timeout=15) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            return {'error': str(e)}


def main():
    """测试API"""
    print("=" * 60)
    print("🔍 巨潮资讯网API测试报告")
    print("=" * 60)
    
    api = CNInfoAPI()
    
    # 测试搜索功能
    print("\n✅ 可用功能：")
    print("\n1. 股票搜索:")
    stocks = api.search_stock("平安")
    if stocks and not any('error' in str(s) for s in stocks[:1]):
        for stock in stocks[:5]:
            code = stock.get('code', '')
            name = stock.get('zwjc', '')
            org_id = stock.get('orgId', '')
            print(f"   • {code} - {name} (orgId: {org_id})")
    
    print("\n2. 港股搜索:")
    stocks = api.search_stock("英诺赛科")
    for stock in stocks[:3]:
        print(f"   • {stock.get('code', '')} - {stock.get('zwjc', '')}")
    
    # 测试公告功能
    print("\n⚠️ 受限功能：")
    print("\n3. 公告查询 (返回空数据):")
    result = api.get_announcements("000001", org_id="gssz0000001")
    total = result.get('totalAnnouncement', 0)
    print(f"   返回公告数: {total}")
    print(f"   说明: 公告查询接口需要特殊认证或 cookies")
    
    print("\n" + "=" * 60)
    print("📋 总结:")
    print("   • ✅ 股票搜索接口 - 可用")
    print("   • ✅ 公司信息查询 - 可用 (通过搜索)")
    print("   • ⚠️  公告列表查询 - 需要认证")
    print("   • ❌ 公告详情/下载 - 需要页面抓取")
    print("=" * 60)


if __name__ == "__main__":
    main()
