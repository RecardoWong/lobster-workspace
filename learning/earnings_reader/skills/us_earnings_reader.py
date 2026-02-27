#!/usr/bin/env python3
"""
美股财报速读器
快速提取美股财报关键指标
"""

import json
import urllib.request
from datetime import datetime
from typing import Dict, List, Optional

class USEarningsReader:
    """美股财报速读器"""
    
    # 评分权重
    WEIGHTS = {
        "growth": 0.30,
        "profitability": 0.25,
        "efficiency": 0.20,
        "safety": 0.15,
        "valuation": 0.10
    }
    
    def __init__(self):
        pass
    
    def get_stock_quote_yahoo(self, symbol: str) -> Dict:
        """
        从Yahoo Finance获取美股行情
        """
        try:
            # Yahoo Finance API
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            if data.get('chart') and data['chart'].get('result'):
                result = data['chart']['result'][0]
                meta = result.get('meta', {})
                
                # 获取最新价格
                timestamps = result.get('timestamp', [])
                prices = result.get('indicators', {}).get('quote', [{}])[0]
                
                if timestamps and prices.get('close'):
                    latest_idx = -1
                    for i in range(len(timestamps) - 1, -1, -1):
                        if prices['close'][i] is not None:
                            latest_idx = i
                            break
                    
                    if latest_idx >= 0:
                        price = prices['close'][latest_idx]
                        prev_close = meta.get('previousClose', price)
                        change = price - prev_close
                        change_pct = (change / prev_close * 100) if prev_close else 0
                        
                        return {
                            "symbol": symbol,
                            "price": price,
                            "prev_close": prev_close,
                            "change": change,
                            "change_pct": change_pct,
                            "currency": meta.get('currency', 'USD'),
                            "source": "Yahoo Finance",
                            "update_time": datetime.now().isoformat()
                        }
            
            return {"error": "无数据", "symbol": symbol}
            
        except Exception as e:
            return {"error": str(e), "symbol": symbol}
    
    def analyze_earnings(self, data: Dict) -> Dict:
        """
        分析美股财报数据
        """
        result = {
            "company": data.get("company", "Unknown"),
            "symbol": data.get("symbol", ""),
            "report_period": data.get("period", ""),
            "analysis_time": datetime.now().isoformat(),
            "scores": {},
            "key_metrics": {},
            "alerts": [],
            "summary": ""
        }
        
        # 计算各维度得分
        result["scores"] = self._calculate_scores(data)
        
        # 提取关键指标
        result["key_metrics"] = self._extract_key_metrics(data)
        
        # 异常检测
        result["alerts"] = self._detect_alerts(data)
        
        # 综合评级
        result["overall_grade"] = self._calculate_overall_grade(result["scores"])
        
        # 生成一句话总结
        result["summary"] = self._generate_summary(result)
        
        return result
    
    def _calculate_scores(self, data: Dict) -> Dict:
        """计算各维度得分"""
        scores = {}
        
        # 成长性 (30%)
        revenue_growth = data.get("revenue_growth_yoy", 0)
        profit_growth = data.get("profit_growth_yoy", 0)
        
        if revenue_growth > 50:
            revenue_score = 100
        elif revenue_growth > 30:
            revenue_score = 80
        elif revenue_growth > 10:
            revenue_score = 60
        elif revenue_growth > 0:
            revenue_score = 40
        else:
            revenue_score = 20
            
        if profit_growth > 100:
            profit_score = 100
        elif profit_growth > 50:
            profit_score = 80
        elif profit_growth > 20:
            profit_score = 60
        elif profit_growth > 0:
            profit_score = 50
        else:
            profit_score = max(20, 50 + profit_growth)
            
        scores["growth"] = round((revenue_score + profit_score) / 2)
        
        # 盈利能力 (25%)
        gross_margin = data.get("gross_margin", 0)
        net_margin = data.get("net_margin", 0)
        roe = data.get("roe", 0)
        
        if gross_margin > 60:
            gm_score = 100
        elif gross_margin > 40:
            gm_score = 80
        elif gross_margin > 20:
            gm_score = 60
        else:
            gm_score = 40
            
        if net_margin > 25:
            nm_score = 100
        elif net_margin > 15:
            nm_score = 80
        elif net_margin > 8:
            nm_score = 60
        elif net_margin > 0:
            nm_score = 40
        else:
            nm_score = 20
            
        if roe > 25:
            roe_score = 100
        elif roe > 20:
            roe_score = 80
        elif roe > 15:
            roe_score = 60
        elif roe > 8:
            roe_score = 40
        else:
            roe_score = 20
            
        scores["profitability"] = round((gm_score + nm_score + roe_score) / 3)
        
        # 运营效率 (20%)
        scores["efficiency"] = 70  # 美股默认给中等分
        
        # 财务安全 (15%)
        debt_ratio = data.get("debt_ratio", 0.4)
        if debt_ratio < 0.4:
            scores["safety"] = 90
        elif debt_ratio < 0.5:
            scores["safety"] = 70
        else:
            scores["safety"] = 50
        
        # 估值水平 (10%)
        pe_ratio = data.get("pe_ratio", 25)
        if pe_ratio < 15:
            scores["valuation"] = 100
        elif pe_ratio < 25:
            scores["valuation"] = 80
        elif pe_ratio < 40:
            scores["valuation"] = 60
        else:
            scores["valuation"] = 40
        
        return scores
    
    def _extract_key_metrics(self, data: Dict) -> Dict:
        """提取关键指标"""
        return {
            "revenue": {
                "value": data.get("revenue", 0),
                "unit": "亿美元",
                "yoy": data.get("revenue_growth_yoy", 0)
            },
            "profit": {
                "value": data.get("net_profit", 0),
                "unit": "亿美元",
                "yoy": data.get("profit_growth_yoy", 0)
            },
            "margins": {
                "gross": data.get("gross_margin", 0),
                "net": data.get("net_margin", 0),
                "gross_change": data.get("gross_margin_change", 0)
            },
            "per_share": {
                "eps": data.get("eps", 0),
                "eps_beat": data.get("eps_beat_percent", 0),  # 超预期幅度
                "revenue_beat": data.get("revenue_beat_percent", 0)
            }
        }
    
    def _detect_alerts(self, data: Dict) -> List[Dict]:
        """检测异常信号"""
        alerts = []
        
        # 1. 营收增长但利润下降
        if data.get("revenue_growth_yoy", 0) > 0 and data.get("profit_growth_yoy", 0) < -10:
            alerts.append({
                "level": "⚠️",
                "type": "增收不增利",
                "description": "营收增长但利润大幅下滑，成本压力增大"
            })
        
        # 2. EPS miss
        if data.get("eps_beat_percent", 0) < 0:
            alerts.append({
                "level": "⚠️",
                "type": "业绩miss",
                "description": f"EPS低于预期{abs(data.get('eps_beat_percent', 0)):.1f}%"
            })
        
        # 3. 毛利率下滑
        if data.get("gross_margin_change", 0) < -5:
            alerts.append({
                "level": "⚠️",
                "type": "毛利率下滑",
                "description": f"毛利率下滑{abs(data.get('gross_margin_change', 0)):.1f}个百分点"
            })
        
        if not alerts:
            alerts.append({
                "level": "✅",
                "type": "业绩健康",
                "description": "未发现明显异常信号"
            })
        
        return alerts
    
    def _calculate_overall_grade(self, scores: Dict) -> str:
        """计算综合评级"""
        weighted_score = (
            scores["growth"] * self.WEIGHTS["growth"] +
            scores["profitability"] * self.WEIGHTS["profitability"] +
            scores["efficiency"] * self.WEIGHTS["efficiency"] +
            scores["safety"] * self.WEIGHTS["safety"] +
            scores["valuation"] * self.WEIGHTS["valuation"]
        )
        
        if weighted_score >= 85:
            return "A+"
        elif weighted_score >= 75:
            return "A"
        elif weighted_score >= 65:
            return "B+"
        elif weighted_score >= 55:
            return "B"
        elif weighted_score >= 45:
            return "C"
        else:
            return "D"
    
    def _generate_summary(self, result: Dict) -> str:
        """生成一句话总结"""
        grade = result["overall_grade"]
        metrics = result["key_metrics"]
        
        revenue_growth = metrics["revenue"]["yoy"]
        profit_growth = metrics["profit"]["yoy"]
        
        parts = []
        
        if revenue_growth > 30:
            parts.append("高增长")
        elif revenue_growth > 10:
            parts.append("稳健增长")
        elif revenue_growth < 0:
            parts.append("收入下滑")
        
        if profit_growth > 50:
            parts.append("利润爆发")
        elif profit_growth < -10:
            parts.append("利润承压")
        
        if not parts:
            parts.append("业绩平稳")
        
        return "，".join(parts)
    
    def format_report(self, analysis: Dict) -> str:
        """格式化输出一页纸报告"""
        lines = [
            f"📊 {analysis['company']} ({analysis['symbol']}) 美股财报速读",
            f"📅 报告期: {analysis['report_period']}",
            "=" * 60,
            ""
        ]
        
        # 评级
        lines.extend([
            f"🎯 综合评级: {analysis['overall_grade']}",
            ""
        ])
        
        # 分项得分
        lines.append("📈 分项得分")
        scores = analysis["scores"]
        lines.append(f"• 成长性: {scores['growth']}/100 (权重30%)")
        lines.append(f"• 盈利能力: {scores['profitability']}/100 (权重25%)")
        lines.append(f"• 运营效率: {scores['efficiency']}/100 (权重20%)")
        lines.append(f"• 财务安全: {scores['safety']}/100 (权重15%)")
        lines.append(f"• 估值水平: {scores['valuation']}/100 (权重10%)")
        lines.append("")
        
        # 核心指标
        metrics = analysis["key_metrics"]
        lines.append("💰 核心指标")
        lines.append(f"• 营收: {metrics['revenue']['value']}{metrics['revenue']['unit']} " +
                    f"({'+' if metrics['revenue']['yoy'] > 0 else ''}{metrics['revenue']['yoy']:.1f}% YoY)")
        lines.append(f"• 净利润: {metrics['profit']['value']}{metrics['profit']['unit']} " +
                    f"({'+' if metrics['profit']['yoy'] > 0 else ''}{metrics['profit']['yoy']:.1f}% YoY)")
        lines.append(f"• 毛利率: {metrics['margins']['gross']:.1f}%")
        lines.append(f"• 净利率: {metrics['margins']['net']:.1f}%")
        lines.append(f"• EPS: ${metrics['per_share']['eps']:.2f}")
        if metrics['per_share']['eps_beat'] != 0:
            beat_emoji = "🟢" if metrics['per_share']['eps_beat'] > 0 else "🔴"
            lines.append(f"• EPS超预期: {beat_emoji} {metrics['per_share']['eps_beat']:+.1f}%")
        lines.append("")
        
        # 异常预警
        lines.append("🔍 异常预警")
        for alert in analysis["alerts"]:
            lines.append(f"{alert['level']} {alert['type']}")
            lines.append(f"   {alert['description']}")
        
        lines.extend([
            "",
            "=" * 60,
            f"💡 总结: {analysis['summary']}"
        ])
        
        return "\n".join(lines)


def demo():
    """演示：分析英伟达模拟数据"""
    reader = USEarningsReader()
    
    # 模拟数据（实际使用时从Yahoo Finance/SEC获取）
    sample_data = {
        "company": "NVIDIA",
        "symbol": "NVDA",
        "period": "FY2024 Q4",
        
        # 利润表
        "revenue": 221,  # 亿美元
        "revenue_growth_yoy": 265,
        "net_profit": 123,
        "profit_growth_yoy": 769,
        "gross_margin": 76.0,
        "net_margin": 55.6,
        "eps": 4.93,
        "eps_beat_percent": 12.0,  # 超预期12%
        "revenue_beat_percent": 8.5,
        
        # 其他
        "roe": 69.2,
        "pe_ratio": 65,
        "debt_ratio": 0.35
    }
    
    analysis = reader.analyze_earnings(sample_data)
    report = reader.format_report(analysis)
    
    # 获取实时行情
    print("📊 获取实时行情...")
    quote = reader.get_stock_quote_yahoo("NVDA")
    if "error" not in quote:
        print(f"🟢 NVDA: ${quote['price']:.2f} ({quote['change_pct']:+.2f}%)")
    
    print("\n" + "=" * 60)
    print(report)
    
    # 保存结果
    import os
    output_dir = "/root/.openclaw/workspace/learning/earnings_reader/data"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = f"{output_dir}/nvidia_earnings_us_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 报告已保存: {output_path}")


if __name__ == "__main__":
    demo()
