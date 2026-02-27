#!/usr/bin/env python3
"""
财报速读主入口
整合美股/港股/A股财报获取 + 健康度评分
完全免费，无需API Key
"""

import sys
import os
import subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skills.us_earnings import USEarningsFetcher
from skills.hk_earnings import HKEarningsFetcher
from skills.cn_earnings import CNEarningsFetcher
from skills.health_scorer import HealthScorer
from typing import Optional, Dict


class EarningsReader:
    """财报速读主类"""
    
    # Telegram推送配置
    TELEGRAM_TARGET = '5440939697'
    
    def __init__(self):
        self.us_fetcher = USEarningsFetcher(rate_limit_delay=3.0)
        self.hk_fetcher = HKEarningsFetcher(rate_limit_delay=2.0)
        self.cn_fetcher = CNEarningsFetcher(rate_limit_delay=2.0)
        self.scorer = HealthScorer()
    
    def send_to_telegram(self, message: str) -> bool:
        """推送消息到Telegram"""
        try:
            env = os.environ.copy()
            env['PATH'] = '/root/.nvm/versions/node/v22.22.0/bin:' + env.get('PATH', '')
            
            cmd = [
                '/root/.nvm/versions/node/v22.22.0/bin/openclaw',
                'message', 'send',
                '--channel', 'telegram',
                '--target', self.TELEGRAM_TARGET,
                '--message', message
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=30, env=env)
            if result.returncode == 0:
                print("✅ Telegram 推送成功")
                return True
            else:
                err = result.stderr.decode()[:100] if result.stderr else '未知错误'
                print(f"⚠️ Telegram 推送失败: {err}")
                return False
        except Exception as e:
            print(f"❌ Telegram 推送异常: {e}")
            return False
    
    def analyze(self, code: str, market: str = "auto", push_to_telegram: bool = False) -> Optional[Dict]:
        """
        分析财报
        
        Args:
            code: 股票代码
                - 美股: "AAPL", "NVDA"
                - 港股: "00700", "09988"
                - A股: "600519", "000001"
            market: 市场类型 ("us"/"hk"/"cn"/"auto")
        
        Returns:
            分析报告字典
        """
        # 自动识别市场
        if market == "auto":
            market = self._detect_market(code)
        
        # 获取财报数据
        if market == "us":
            data = self.us_fetcher.fetch(code)
            if data:
                raw_data = data.to_dict()
                stock_name = data.company_name
            else:
                return None
                
        elif market == "hk":
            data = self.hk_fetcher.fetch(code)
            if data:
                raw_data = data.to_dict()
                stock_name = f"{data.name}({data.code})"
            else:
                return None
                
        elif market == "cn":
            data = self.cn_fetcher.fetch(code)
            if data:
                raw_data = data.to_dict()
                stock_name = f"{data.name}({data.code})"
            else:
                return None
        else:
            print(f"[错误] 不支持的市场类型: {market}")
            return None
        
        # 健康度评分
        score = self.scorer.score(raw_data)
        
        # 格式化输出
        report = self._format_report(stock_name, raw_data, score, market)
        
        # 推送到Telegram
        if push_to_telegram and report:
            self._push_earnings_report(report)
        
        return report
    
    def _push_earnings_report(self, report: Dict):
        """推送财报报告到Telegram"""
        lines = []
        lines.append(f"📊 {report['stock_name']} 财报速读")
        lines.append("=" * 40)
        lines.append(f"🎯 综合评级: {report['rating']} ({report['total_score']}分)")
        
        lines.append("\n📈 5维评分:")
        for dim, score in report['dimension_scores'].items():
            lines.append(f"• {dim}: {score}")
        
        lines.append("\n💰 核心指标:")
        for metric, value in report['key_metrics'].items():
            lines.append(f"• {metric}: {value}")
        
        if report['positives']:
            lines.append("\n✅ 积极信号:")
            for p in report['positives'][:3]:
                lines.append(f"• {p}")
        
        if report['warnings']:
            lines.append("\n⚠️ 风险信号:")
            for w in report['warnings'][:3]:
                lines.append(f"• {w}")
        
        lines.append(f"\n💡 总结: {report['summary']}")
        
        message = "\n".join(lines)
        self.send_to_telegram(message)
    
    def _detect_market(self, code: str) -> str:
        """自动识别市场"""
        code = code.upper()
        
        # 美股 (字母为主)
        if code.isalpha() or (len(code) <= 5 and any(c.isalpha() for c in code)):
            return "us"
        
        # A股 (6位数字)
        if code.isdigit() and len(code) == 6:
            if code.startswith('6') or code.startswith('0') or code.startswith('3'):
                return "cn"
        
        # 港股 (5位数字)
        if code.isdigit() and len(code) == 5:
            return "hk"
        
        # 默认美股
        return "us"
    
    def _format_report(self, stock_name: str, data: Dict, score, market: str) -> Dict:
        """格式化报告"""
        
        # 货币单位
        currency_unit = "亿美元" if market == "us" else "亿港元" if market == "hk" else "亿元"
        
        report = {
            'stock_name': stock_name,
            'market': market.upper(),
            'rating': score.rating,
            'total_score': score.total_score,
            'dimension_scores': {
                '成长性': f"{score.growth_score}/100 (30%)",
                '盈利能力': f"{score.profitability_score}/100 (25%)",
                '运营效率': f"{score.efficiency_score}/100 (20%)",
                '财务安全': f"{score.safety_score}/100 (15%)",
                '估值水平': f"{score.valuation_score}/100 (10%)"
            },
            'key_metrics': {
                '营收': self._format_value(data.get('revenue'), currency_unit, data.get('revenue_growth')),
                '净利润': self._format_value(data.get('net_profit'), currency_unit, data.get('net_profit_growth')),
                'EPS': f"${data.get('eps'):.2f}" if data.get('eps') else "N/A",
                'PE': f"{data.get('pe'):.1f}" if data.get('pe') else "N/A",
                'ROE': f"{data.get('roe'):.1f}%" if data.get('roe') else "N/A"
            },
            'positives': score.positives,
            'warnings': score.warnings,
            'summary': score.summary
        }
        
        return report
    
    def _format_value(self, value, unit: str, growth: Optional[float] = None) -> str:
        """格式化数值"""
        if value is None:
            return "N/A"
        
        if value >= 1e4:
            formatted = f"{value/1e4:.1f}万{unit}"
        else:
            formatted = f"{value:.1f}{unit}"
        
        if growth is not None:
            growth_str = f"+{growth:.1f}%" if growth >= 0 else f"{growth:.1f}%"
            formatted += f" ({growth_str})"
        
        return formatted
    
    def print_report(self, report: Dict):
        """打印格式化报告"""
        if not report:
            print("❌ 无法生成报告")
            return
        
        print("\n" + "="*60)
        print(f"📊 {report['stock_name']} 财报速读")
        print("="*60)
        print(f"🎯 综合评级: {report['rating']} ({report['total_score']}分)")
        print()
        
        print("📈 5维评分:")
        for dim, score in report['dimension_scores'].items():
            print(f"  • {dim}: {score}")
        print()
        
        print("💰 核心指标:")
        for metric, value in report['key_metrics'].items():
            print(f"  • {metric}: {value}")
        print()
        
        if report['positives']:
            print("✅ 积极信号:")
            for p in report['positives'][:5]:  # 最多显示5条
                print(f"  • {p}")
            print()
        
        if report['warnings']:
            print("⚠️ 风险信号:")
            for w in report['warnings'][:5]:  # 最多显示5条
                print(f"  • {w}")
            print()
        
        print(f"💡 总结: {report['summary']}")
        print("="*60)


# 命令行入口
if __name__ == "__main__":
    reader = EarningsReader()
    
    # 测试用例
    test_cases = [
        ("AAPL", "us"),      # 美股 - 苹果
        ("00700", "hk"),     # 港股 - 腾讯
        ("600519", "cn"),    # A股 - 茅台
    ]
    
    print("🚀 财报速读系统测试\n")
    
    for code, market in test_cases:
        try:
            print(f"\n{'='*60}")
            print(f"🔍 分析: {code} ({market.upper()})")
            print(f"{'='*60}")
            
            report = reader.analyze(code, market)
            reader.print_report(report)
            
        except Exception as e:
            print(f"❌ 分析 {code} 失败: {e}")
    
    print("\n✅ 测试完成")
