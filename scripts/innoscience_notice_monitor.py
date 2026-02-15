#!/usr/bin/env python3
"""
📰 英诺赛科公告监控 - 东方财富
实时监控港交所公告，有新公告立即推送
"""

import requests
import json
import re
from datetime import datetime
import os

class InnoscienceNoticeMonitor:
    """英诺赛科公告监控"""
    
    def __init__(self):
        self.stock_code = "02577"  # 港股代码
        self.stock_name = "英诺赛科"
        self.state_file = "/root/.openclaw/workspace/memory/innoscience_notices.json"
        
    def get_latest_notices(self, limit=10):
        """获取最新公告"""
        try:
            # 东方财富公告API
            url = f"http://datacenter-web.eastmoney.com/api/data/v1/get?sortColumns=NOTICE_DATE&sortTypes=-1&pageSize={limit}&pageNumber=1&reportName=RPT_WEB_PUBLICNOTICE&columns=ALL&filter=(SECURITY_CODE%3D%22{self.stock_code}%22)"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            
            if data.get('result') and data['result'].get('data'):
                notices = []
                for item in data['result']['data']:
                    notice = {
                        'id': item.get('NOTICE_ID', ''),
                        'title': item.get('NOTICE_TITLE', ''),
                        'date': item.get('NOTICE_DATE', ''),
                        'type': item.get('NOTICE_TYPE', ''),
                        'url': item.get('URL', ''),
                    }
                    notices.append(notice)
                return notices
            
            return []
            
        except Exception as e:
            print(f"❌ 获取公告失败: {e}")
            return []
    
    def load_state(self):
        """加载上次状态"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {'last_notice_id': '', 'last_check': ''}
        except:
            return {'last_notice_id': '', 'last_check': ''}
    
    def save_state(self, last_id):
        """保存状态"""
        state = {
            'last_notice_id': last_id,
            'last_check': datetime.now().isoformat()
        }
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    
    def check_new_notices(self):
        """检查新公告"""
        state = self.load_state()
        last_id = state.get('last_notice_id', '')
        
        notices = self.get_latest_notices(limit=5)
        if not notices:
            return []
        
        # 找出新公告
        new_notices = []
        for notice in notices:
            if notice['id'] == last_id:
                break
            new_notices.append(notice)
        
        # 更新状态
        if notices:
            self.save_state(notices[0]['id'])
        
        return new_notices
    
    def format_notice(self, notice):
        """格式化单条公告"""
        lines = []
        lines.append(f"📢 {self.stock_name} 新公告")
        lines.append(f"📅 {notice['date']}")
        lines.append(f"📋 {notice['title']}")
        if notice['type']:
            lines.append(f"🏷️ 类型: {notice['type']}")
        if notice['url']:
            lines.append(f"🔗 {notice['url']}")
        lines.append("-" * 50)
        return '\n'.join(lines)
    
    def run(self):
        """运行检查"""
        new_notices = self.check_new_notices()
        
        if new_notices:
            messages = []
            messages.append(f"🚨 发现 {len(new_notices)} 条新公告:\n")
            
            for notice in new_notices:
                messages.append(self.format_notice(notice))
            
            return '\n'.join(messages)
        else:
            return None  # 没有新公告

if __name__ == '__main__':
    monitor = InnoscienceNoticeMonitor()
    result = monitor.run()
    
    if result:
        print(result)
    else:
        print("✅ 暂无新公告")
        # 输出最后检查时间
        state = monitor.load_state()
        if state.get('last_check'):
            print(f"⏰ 上次检查: {state['last_check'][:19]}")
