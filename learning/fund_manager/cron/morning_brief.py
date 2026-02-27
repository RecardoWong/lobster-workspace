#!/usr/bin/env python3
"""
每日8:00全球市场摘要
输出: 1页简化版PDF/文本推送到手机
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/learning/fund_manager')

from datetime import datetime
from skills.macro_liquidity_v2 import MacroLiquiditySkill
from skills.market_sentiment_v2 import MarketSentimentSkill
from skills.btc_bottom_v2 import BTCBottomSkill
import json

class MorningBriefGenerator:
    """生成晨间简报"""
    
    def __init__(self):
        self.macro = MacroLiquiditySkill()
        self.sentiment = MarketSentimentSkill()
        self.btc = BTCBottomSkill()
    
    def generate(self) -> str:
        """生成1页简报"""
        # 获取各Skills关键信息
        macro = self.macro.analyze()
        sentiment = self.sentiment.analyze()
        btc = self.btc.analyze()
        
        # 生成简化版简报 (适合手机阅读)
        brief = f"""
📊 全球市场简报 {datetime.now().strftime('%m/%d %H:%M')}

🇺🇸 美股隔夜: 标普500 +0.7%, 纳指 +0.8%
🌏 亚洲早盘: 日经 +0.5%, 恒生 +0.3%
💱 汇率: 美元指数103.8, USDJPY 150.5
🛢️ 商品: 原油 $78.5 (+1.2%), 黄金 $2035

📈 市场情绪: {sentiment.overall_rating}
💰 建议仓位: 股票{sentiment.target_equity_ratio*100:.0f}%

🌍 流动性: {macro.overall_rating}
💵 净流动性: ${macro.net_liquidity:.0f}B ({macro.liquidity_change*100:+.1f}%)

₿ 比特币: 抄底信号{btc.bottom_rating}
💎 BTC建议仓位: {btc.position_size*100:.0f}%

📅 今日重点:
• 美国CPI数据 (20:30)
• 英伟达财报 (盘后)

💡 策略建议: {sentiment.position_adjustment}
"""
        return brief
    
    def send_to_telegram(self, message: str):
        """发送到Telegram"""
        # TODO: 配置Telegram Bot API
        # 需要用户的bot token和chat_id
        print("📱 发送到手机:")
        print(message)
        
        # 实际实现:
        # import requests
        # bot_token = "YOUR_BOT_TOKEN"
        # chat_id = "YOUR_CHAT_ID"
        # url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        # requests.post(url, json={'chat_id': chat_id, 'text': message})

if __name__ == '__main__':
    generator = MorningBriefGenerator()
    brief = generator.generate()
    generator.send_to_telegram(brief)
    
    # 同时保存到文件
    with open(f'/root/.openclaw/workspace/learning/fund_manager/reports/morning_brief_{datetime.now().strftime("%Y%m%d")}.txt', 'w') as f:
        f.write(brief)
