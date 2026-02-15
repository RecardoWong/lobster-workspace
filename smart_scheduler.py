#!/usr/bin/env python3
"""
智能推送调节器
根据市场活跃度自动调整推送频率
"""

import os
import json
from datetime import datetime, timedelta

class SmartScheduler:
    """智能调度器"""
    
    def __init__(self, state_file="/tmp/smart_scheduler.json"):
        self.state_file = state_file
        self.state = self.load_state()
    
    def load_state(self):
        """加载状态"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            'last_push_time': None,
            'last_active_count': 0,
            'consecutive_silent': 0,  # 连续静默次数
            'market_status': 'normal',  # normal, hot, sleep, deep_sleep
        }
    
    def save_state(self):
        """保存状态"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f)
    
    def should_push(self, active_token_count: int) -> bool:
        """
        判断是否该推送
        
        规则（用户定制版 - 激进静默）：
        1. 有活跃代币(>0) → 立即推送
        2. 连续1次无活跃 → 延长到4小时
        3. 连续2次+无活跃 → 延长到8小时
        4. 新币首次出现 → 立即推送（不管时间）
        """
        now = datetime.now()
        
        # 更新活跃计数
        if active_token_count > 0:
            self.state['consecutive_silent'] = 0
            self.state['market_status'] = 'hot'
            self.save_state()
            return True  # 有活跃币，立即推送
        
        # 无活跃币
        self.state['consecutive_silent'] += 1
        silent_count = self.state['consecutive_silent']
        
        # 检查距离上次推送的时间
        if self.state['last_push_time']:
            last_push = datetime.fromisoformat(self.state['last_push_time'])
            hours_since_last = (now - last_push).total_seconds() / 3600
        else:
            hours_since_last = 999  # 第一次
        
        # 根据静默次数决定推送间隔（用户定制版）
        if silent_count >= 2:
            # 连续2次+无活跃，进入"深度休眠"模式
            self.state['market_status'] = 'deep_sleep'
            if hours_since_last >= 8:
                self.save_state()
                return True  # 8小时推一次
            else:
                self.save_state()
                return False
        
        elif silent_count >= 1:
            # 连续1次无活跃，进入"休眠"模式
            self.state['market_status'] = 'sleep'
            if hours_since_last >= 4:
                self.save_state()
                return True  # 4小时推一次
            else:
                self.save_state()
                return False
        
        else:
            # 正常情况
            self.state['market_status'] = 'normal'
            if hours_since_last >= 1:
                self.save_state()
                return True
            else:
                self.save_state()
                return False
    
    def mark_pushed(self):
        """标记已推送"""
        self.state['last_push_time'] = datetime.now().isoformat()
        self.save_state()
    
    def get_status(self) -> str:
        """获取当前状态说明"""
        silent = self.state['consecutive_silent']
        status = self.state['market_status']
        
        if status == 'hot':
            return "🔥 市场活跃 - 正常推送"
        elif status == 'deep_sleep':
            return f"💤 深度休眠 - 连续{silent}次无活跃，8小时推一次"
        elif status == 'sleep':
            return f"🌙 休眠模式 - 连续{silent}次无活跃，4小时推一次"
        else:
            return f"📊 正常模式 - 连续{silent}次无活跃，1小时推一次"


if __name__ == "__main__":
    scheduler = SmartScheduler()
    
    # 测试：假设当前有0个活跃币
    should = scheduler.should_push(0)
    print(f"是否推送: {should}")
    print(f"状态: {scheduler.get_status()}")
