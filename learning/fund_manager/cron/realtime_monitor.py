#!/usr/bin/env python3
"""
实时监控 - 流动性指标异常预警
触发条件时推送到手机
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/learning/fund_manager')

from datetime import datetime
import time
from skills.macro_liquidity_v2 import MacroLiquiditySkill
from skills.market_sentiment_v2 import MarketSentimentSkill

class RealtimeMonitor:
    """实时监控器"""
    
    def __init__(self):
        self.macro = MacroLiquiditySkill()
        self.sentiment = MarketSentimentSkill()
        self.last_alert_time = None
        self.alert_cooldown = 3600  # 1小时内不重复报警
        
        # 预警阈值
        self.thresholds = {
            'liquidity_drop': 0.05,  # 5%
            'vix_spike': 30,         # VIX > 30
            'sentiment_extreme': 85,  # 贪婪指数
        }
    
    def check_once(self):
        """检查一次"""
        alerts = []
        
        # 检查流动性
        macro = self.macro.analyze()
        if macro.liquidity_trigger:
            alerts.append(f"🚨 流动性预警: 单周下降{macro.liquidity_change*100:.1f}%")
        if macro.sofr_trigger:
            alerts.append(f"🚨 SOFR过高: {macro.sofr_rate}%")
        if macro.move_trigger:
            alerts.append(f"🚨 MOVE指数: {macro.move_index}")
        
        # 检查情绪
        sentiment = self.sentiment.analyze()
        if sentiment.warning_count >= 3:
            alerts.append(f"⚠️ 情绪预警: {sentiment.warning_count}/5指标触发")
        
        return alerts
    
    def send_alert(self, alerts: list):
        """发送警报"""
        # 检查冷却时间
        if self.last_alert_time:
            elapsed = (datetime.now() - self.last_alert_time).total_seconds()
            if elapsed < self.alert_cooldown:
                return
        
        message = f"""
🚨 投资Agent实时预警 {datetime.now().strftime('%H:%M')}

{chr(10).join(alerts)}

请立即检查市场情况！
"""
        print(message)
        # TODO: Telegram推送
        
        self.last_alert_time = datetime.now()
        
        # 保存到文件
        with open('/root/.openclaw/workspace/learning/fund_manager/logs/alerts.log', 'a') as f:
            f.write(f"{datetime.now()}: {alerts}\n")
    
    def run(self):
        """持续运行"""
        print(f"🔍 实时监控启动... {datetime.now()}")
        print(f"   检查频率: 每5分钟")
        print(f"   预警冷却: 1小时")
        print(f"   监控指标: 流动性、VIX、情绪")
        
        while True:
            try:
                alerts = self.check_once()
                if alerts:
                    self.send_alert(alerts)
                else:
                    print(f"{datetime.now().strftime('%H:%M')} ✓ 无异常")
                
                time.sleep(300)  # 5分钟
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(300)

if __name__ == '__main__':
    monitor = RealtimeMonitor()
    
    # 测试模式: 只检查一次
    # monitor.run()  # 持续运行
    
    # 测试一次
    print("测试模式 - 检查一次:\n")
    alerts = monitor.check_once()
    if alerts:
        monitor.send_alert(alerts)
    else:
        print("✓ 当前无预警")
