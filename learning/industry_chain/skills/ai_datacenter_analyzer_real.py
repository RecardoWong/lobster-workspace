#!/usr/bin/env python3
"""
AI数据中心产业链分析器 - 真实数据版
分析产业链上下游，接入真实市场数据
"""

import json
import sys
sys.path.insert(0, '/root/.openclaw/workspace/learning/fund_manager/skills')

from real_data_connector import RealDataConnector
from datetime import datetime
from typing import Dict, List, Optional

class AIDataCenterChain:
    """AI数据中心产业链分析器"""
    
    def __init__(self):
        self.data_connector = RealDataConnector()
        
        # 产业链基础数据
        self.chain_data = {
            "name": "AI数据中心产业链",
            "upstream": {
                "description": "上游：芯片与核心器件",
                "segments": [
                    {
                        "name": "GPU/AI芯片",
                        "key_players": [
                            {"ticker": "NVDA", "name": "英伟达", "market": "us"},
                            {"ticker": "AMD", "name": "AMD", "market": "us"},
                            {"ticker": "INTC", "name": "英特尔", "market": "us"}
                        ],
                        "bottleneck": True,
                        "margin_range": "60-80%",
                        "growth_rate": "+120% YoY",
                        "note": "核心算力来源，供不应求"
                    },
                    {
                        "name": "HBM高带宽内存",
                        "key_players": [
                            {"name": "SK海力士"},
                            {"name": "三星电子"},
                            {"name": "美光"}
                        ],
                        "bottleneck": True,
                        "margin_range": "50-60%",
                        "growth_rate": "+85% YoY",
                        "note": "AI芯片关键配套，产能紧张"
                    },
                    {
                        "name": "先进封装",
                        "key_players": [
                            {"ticker": "TSM", "name": "台积电", "market": "us"},
                            {"ticker": "ASX", "name": "日月光", "market": "us"},
                            {"name": "Amkor"}
                        ],
                        "bottleneck": True,
                        "margin_range": "40-50%",
                        "growth_rate": "+100% YoY",
                        "note": "CoWoS产能是瓶颈，2026年翻倍"
                    }
                ]
            },
            "midstream": {
                "description": "中游：服务器与基础设施",
                "segments": [
                    {
                        "name": "服务器代工",
                        "key_players": [
                            {"name": "工业富联"},
                            {"name": "广达"},
                            {"name": "纬创"}
                        ],
                        "bottleneck": False,
                        "margin_range": "5-10%",
                        "growth_rate": "+60% YoY",
                        "note": "GB200等新品量产中"
                    },
                    {
                        "name": "光模块",
                        "key_players": [
                            {"name": "中际旭创"},
                            {"name": "Coherent"},
                            {"name": "光迅科技"}
                        ],
                        "bottleneck": False,
                        "margin_range": "25-35%",
                        "growth_rate": "+150% YoY",
                        "note": "800G/1.6T光模块放量"
                    },
                    {
                        "name": "散热方案",
                        "key_players": [
                            {"name": "奇鋐"},
                            {"name": "双鸿"},
                            {"name": "健策"}
                        ],
                        "bottleneck": False,
                        "margin_range": "15-25%",
                        "growth_rate": "+80% YoY",
                        "note": "液冷需求快速增长"
                    }
                ]
            },
            "downstream": {
                "description": "下游：云服务与企业客户",
                "segments": [
                    {
                        "name": "云服务厂商",
                        "key_players": [
                            {"ticker": "AMZN", "name": "AWS", "market": "us"},
                            {"ticker": "MSFT", "name": "Azure", "market": "us"},
                            {"ticker": "GOOGL", "name": "Google Cloud", "market": "us"}
                        ],
                        "bottleneck": False,
                        "margin_range": "25-35%",
                        "growth_rate": "+25% YoY",
                        "note": "CAPEX大幅投入AI基础设施"
                    },
                    {
                        "name": "企业大客户",
                        "key_players": [
                            {"name": "Meta"},
                            {"name": "Google"},
                            {"name": "微软"},
                            {"name": "字节跳动"}
                        ],
                        "bottleneck": False,
                        "margin_range": "N/A",
                        "growth_rate": "AI投入翻倍",
                        "note": "自建AI算力集群"
                    }
                ]
            }
        }
    
    def get_real_time_quotes(self) -> Dict:
        """获取实时行情数据"""
        quotes = {}
        
        # 获取关键股票行情
        key_stocks = [
            ("NVDA", "us", "英伟达"),
            ("AMD", "us", "AMD"),
            ("TSM", "us", "台积电"),
            ("AMZN", "us", "亚马逊"),
            ("MSFT", "us", "微软"),
            ("GOOGL", "us", "谷歌")
        ]
        
        print("📊 获取实时行情...")
        for symbol, market, name in key_stocks:
            quote = self.data_connector.get_stock_quote(symbol, market)
            quotes[f"{symbol}.{market.upper()}"] = quote
            if "error" not in quote:
                print(f"  ✅ {name}(${symbol}): ${quote.get('price', 'N/A')}")
            else:
                print(f"  ⚠️ {name}(${symbol}): {quote.get('error', 'Unknown')}")
        
        # 获取加密货币行情
        crypto_symbols = ["BTC", "ETH"]
        for symbol in crypto_symbols:
            quote = self.data_connector.get_crypto_quote(symbol)
            quotes[symbol] = quote
            if "error" not in quote:
                print(f"  ✅ {symbol}: ${quote.get('price', 'N/A'):,.2f} ({quote.get('change_pct', 0):.2f}%)")
        
        return quotes
    
    def analyze_chain(self, real_time_quotes: Dict = None) -> Dict:
        """分析产业链各环节"""
        result = {
            "analysis_time": datetime.now().isoformat(),
            "market_data": real_time_quotes or {},
            "bottlenecks": [],
            "opportunities": [],
            "risks": [],
            "chain_summary": {},
            "market_sentiment": ""
        }
        
        # 识别瓶颈环节
        for tier in ["upstream", "midstream", "downstream"]:
            tier_data = self.chain_data[tier]
            for segment in tier_data["segments"]:
                if segment.get("bottleneck"):
                    result["bottlenecks"].append({
                        "tier": tier,
                        "segment": segment["name"],
                        "players": [p.get("name", p.get("ticker", "")) for p in segment["key_players"]],
                        "growth": segment["growth_rate"],
                        "note": segment["note"]
                    })
        
        # 生成投资机会
        result["opportunities"] = self._generate_opportunities(real_time_quotes)
        
        # 风险提示
        result["risks"] = self._generate_risks(real_time_quotes)
        
        # 产业链摘要
        result["chain_summary"] = self._generate_summary()
        
        # 市场情绪
        result["market_sentiment"] = self._analyze_sentiment(real_time_quotes)
        
        return result
    
    def _generate_opportunities(self, quotes: Dict = None) -> List[Dict]:
        """生成投资机会列表"""
        opportunities = [
            {
                "type": "短期",
                "theme": "上游瓶颈环节",
                "description": "GPU/HBM/先进封装供不应求，产能是核心变量",
                "tickers": ["NVDA", "TSM"],
                "catalyst": "CoWoS产能释放进度"
            },
            {
                "type": "中期",
                "theme": "国产替代",
                "description": "光模块、散热等中游环节中国企业快速崛起",
                "tickers": ["中际旭创", "工业富联"],
                "catalyst": "800G光模块放量、液冷渗透率提升"
            },
            {
                "type": "长期",
                "theme": "云服务商AI货币化",
                "description": "云厂商AI服务收入能否覆盖CAPEX投入",
                "tickers": ["MSFT", "AMZN", "GOOGL"],
                "catalyst": "AI服务收入增速"
            }
        ]
        
        # 根据实时数据调整
        if quotes:
            # 检查NVDA走势
            nvda = quotes.get("NVDA.US", {})
            if "error" not in nvda:
                change_pct = nvda.get("change_pct", 0)
                if change_pct < -3:
                    opportunities.append({
                        "type": "机会",
                        "theme": "NVDA回调",
                        "description": f"NVDA今日下跌{abs(change_pct):.2f}%，短期回调可能提供买入机会",
                        "tickers": ["NVDA"],
                        "catalyst": "AI需求依然强劲"
                    })
        
        return opportunities
    
    def _generate_risks(self, quotes: Dict = None) -> List[Dict]:
        """生成风险提示"""
        risks = [
            {
                "risk": "产能过剩风险",
                "description": "2025下半年GPU产能释放，供需缺口收窄",
                "timeline": "2025H2-2026",
                "impact": "上游毛利率承压"
            },
            {
                "risk": "地缘政治",
                "description": "美国对华AI芯片出口管制升级",
                "timeline": "持续",
                "impact": "中国AI产业链受限"
            }
        ]
        
        # 根据实时数据添加风险
        if quotes:
            btc = quotes.get("BTC", {})
            if "error" not in btc:
                change_pct = btc.get("change_pct", 0)
                if change_pct < -5:
                    risks.append({
                        "risk": "加密市场波动",
                        "description": f"BTC今日下跌{abs(change_pct):.2f}%，风险偏好下降",
                        "timeline": "短期",
                        "impact": "科技股可能承压"
                    })
        
        return risks
    
    def _generate_summary(self) -> Dict:
        """生成产业链摘要"""
        return {
            "total_segments": 8,
            "bottleneck_count": 3,
            "avg_growth_rate": "+65% YoY",
            "hottest_segment": "先进封装",
            "key_catalyst": "CoWoS产能",
            "investment_theme": "抓上游瓶颈，看国产替代"
        }
    
    def _analyze_sentiment(self, quotes: Dict = None) -> str:
        """分析市场情绪"""
        if not quotes:
            return "数据不足"
        
        # 检查NVDA走势
        nvda = quotes.get("NVDA.US", {})
        if "error" not in nvda:
            change = nvda.get("change_pct", 0)
            if change > 2:
                return f"🟢 乐观 - NVDA上涨{change:.2f}%，AI芯片需求强劲"
            elif change < -2:
                return f"🔴 谨慎 - NVDA下跌{abs(change):.2f}%，关注回调风险"
            else:
                return f"🟡 中性 - NVDA平盘，市场等待新催化剂"
        
        return "⚪ 数据不足"
    
    def format_report(self, analysis: Dict) -> str:
        """格式化输出报告"""
        lines = [
            "🏭 AI数据中心产业链分析报告",
            f"📅 分析时间: {analysis['analysis_time'][:19]}",
            "=" * 60,
            ""
        ]
        
        # 市场情绪
        lines.extend([
            "📊 市场情绪",
            f"{analysis['market_sentiment']}",
            ""
        ])
        
        # 实时行情
        if analysis.get("market_data"):
            lines.append("💹 关键标的实时行情")
            quotes = analysis["market_data"]
            
            # 显示NVDA
            nvda = quotes.get("NVDA.US", {})
            if "error" not in nvda:
                change_pct = nvda.get("change_pct", 0)
                emoji = "🟢" if change_pct > 0 else "🔴"
                lines.append(f"{emoji} NVDA: ${nvda.get('price', 'N/A'):,.2f} ({change_pct:+.2f}%)")
            
            # 显示BTC
            btc = quotes.get("BTC", {})
            if "error" not in btc:
                change_pct = btc.get("change_pct", 0)
                emoji = "🟢" if change_pct > 0 else "🔴"
                lines.append(f"{emoji} BTC: ${btc.get('price', 'N/A'):,.2f} ({change_pct:+.2f}%)")
            
            lines.append("")
        
        # 摘要
        summary = analysis["chain_summary"]
        lines.extend([
            "📈 产业链摘要",
            f"• 总环节数: {summary['total_segments']}",
            f"• 瓶颈环节: {summary['bottleneck_count']}个",
            f"• 平均增速: {summary['avg_growth_rate']}",
            f"• 最热环节: {summary['hottest_segment']}",
            f"• 核心变量: {summary['key_catalyst']}",
            f"• 投资主题: {summary['investment_theme']}",
            ""
        ])
        
        # 瓶颈环节
        lines.append("🔒 瓶颈环节（供不应求）")
        for b in analysis["bottlenecks"]:
            lines.extend([
                f"• {b['segment']}",
                f"  标的: {', '.join(b['players'][:3])}",
                f"  增速: {b['growth']}",
                f"  备注: {b['note']}"
            ])
        lines.append("")
        
        # 投资机会
        lines.append("💰 投资机会")
        for op in analysis["opportunities"]:
            lines.extend([
                f"【{op['type']}】{op['theme']}",
                f"  {op['description']}",
                f"  关注: {', '.join(op['tickers'])}",
                f"  催化: {op['catalyst']}",
                ""
            ])
        
        # 风险提示
        lines.append("⚠️ 风险提示")
        for risk in analysis["risks"]:
            lines.extend([
                f"• {risk['risk']} ({risk['timeline']})",
                f"  {risk['description']}",
                f"  影响: {risk['impact']}"
            ])
        
        lines.extend([
            "",
            "=" * 60,
            "💡 数据来源: 实时行情 + 行业研报整理"
        ])
        
        return "\n".join(lines)


def main():
    """主函数 - 生成产业链分析报告（真实数据版）"""
    print("=" * 60)
    print("🏭 AI数据中心产业链分析器")
    print("   接入真实市场数据")
    print("=" * 60)
    
    analyzer = AIDataCenterChain()
    
    # 获取实时行情
    print("\n🔌 获取实时数据...")
    real_time_quotes = analyzer.get_real_time_quotes()
    
    # 分析
    print("\n📊 分析产业链...")
    analysis = analyzer.analyze_chain(real_time_quotes)
    
    # 生成报告
    report = analyzer.format_report(analysis)
    
    # 保存
    import os
    output_dir = "/root/.openclaw/workspace/learning/industry_chain/data"
    os.makedirs(output_dir, exist_ok=True)
    
    json_path = f"{output_dir}/ai_datacenter_chain_real_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    report_path = f"{output_dir}/ai_datacenter_report_real_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + "=" * 60)
    print(report)
    print("\n" + "=" * 60)
    print(f"\n✅ 报告已保存:")
    print(f"   JSON: {json_path}")
    print(f"   报告: {report_path}")


if __name__ == "__main__":
    main()
