#!/usr/bin/env python3
"""
港股财报速读器
快速提取财报关键指标，生成一页纸摘要
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

class HKStockEarningsReader:
    """港股财报速读器"""
    
    # 评分权重
    WEIGHTS = {
        "growth": 0.30,      # 成长性
        "profitability": 0.25,  # 盈利能力
        "efficiency": 0.20,   # 运营效率
        "safety": 0.15,      # 财务安全
        "valuation": 0.10    # 估值水平
    }
    
    def __init__(self):
        pass
    
    def analyze_earnings(self, data: Dict) -> Dict:
        """
        分析财报数据
        
        Args:
            data: 包含财报原始数据的字典
        
        Returns:
            分析结果字典
        """
        result = {
            "company": data.get("company", "Unknown"),
            "ticker": data.get("ticker", ""),
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
            profit_score = max(20, 50 + profit_growth)  # 亏损扣分
            
        scores["growth"] = round((revenue_score + profit_score) / 2)
        
        # 盈利能力 (25%)
        gross_margin = data.get("gross_margin", 0)
        net_margin = data.get("net_margin", 0)
        roe = data.get("roe", 0)
        
        # 毛利率评分
        if gross_margin > 50:
            gm_score = 100
        elif gross_margin > 30:
            gm_score = 80
        elif gross_margin > 15:
            gm_score = 60
        else:
            gm_score = 40
            
        # 净利率评分
        if net_margin > 20:
            nm_score = 100
        elif net_margin > 10:
            nm_score = 80
        elif net_margin > 5:
            nm_score = 60
        elif net_margin > 0:
            nm_score = 40
        else:
            nm_score = 20
            
        # ROE评分
        if roe > 20:
            roe_score = 100
        elif roe > 15:
            roe_score = 80
        elif roe > 10:
            roe_score = 60
        elif roe > 5:
            roe_score = 40
        else:
            roe_score = 20
            
        scores["profitability"] = round((gm_score + nm_score + roe_score) / 3)
        
        # 运营效率 (20%)
        inventory_days = data.get("inventory_days", 90)
        receivable_days = data.get("receivable_days", 60)
        
        # 存货周转天数（越少越好）
        if inventory_days < 30:
            inv_score = 100
        elif inventory_days < 60:
            inv_score = 80
        elif inventory_days < 90:
            inv_score = 60
        else:
            inv_score = 40
            
        # 应收周转天数
        if receivable_days < 30:
            rec_score = 100
        elif receivable_days < 60:
            rec_score = 80
        elif receivable_days < 90:
            rec_score = 60
        else:
            rec_score = 40
            
        scores["efficiency"] = round((inv_score + rec_score) / 2)
        
        # 财务安全 (15%)
        debt_ratio = data.get("debt_ratio", 0.5)
        current_ratio = data.get("current_ratio", 1.5)
        
        # 负债率（适中最好，30-60%）
        if 0.3 <= debt_ratio <= 0.5:
            debt_score = 100
        elif debt_ratio < 0.7:
            debt_score = 80
        elif debt_ratio < 0.8:
            debt_score = 60
        else:
            debt_score = 40
            
        # 流动比率
        if current_ratio > 2:
            curr_score = 100
        elif current_ratio > 1.5:
            curr_score = 80
        elif current_ratio > 1:
            curr_score = 60
        else:
            curr_score = 40
            
        scores["safety"] = round((debt_score + curr_score) / 2)
        
        # 估值水平 (10%) - 需要市场数据，这里简化
        pe_ratio = data.get("pe_ratio", 20)
        if pe_ratio is None:
            val_score = 60  # 亏损公司给中等分
        elif pe_ratio < 10:
            val_score = 100
        elif pe_ratio < 20:
            val_score = 80
        elif pe_ratio < 30:
            val_score = 60
        else:
            val_score = 40
            
        scores["valuation"] = val_score
        
        return scores
    
    def _extract_key_metrics(self, data: Dict) -> Dict:
        """提取关键指标"""
        return {
            "revenue": {
                "value": data.get("revenue", 0),
                "unit": data.get("revenue_unit", "亿元"),
                "yoy": data.get("revenue_growth_yoy", 0),
                "qoq": data.get("revenue_growth_qoq", 0)
            },
            "profit": {
                "value": data.get("net_profit", 0),
                "unit": data.get("profit_unit", "亿元"),
                "yoy": data.get("profit_growth_yoy", 0),
                "qoq": data.get("profit_growth_qoq", 0)
            },
            "margins": {
                "gross": data.get("gross_margin", 0),
                "net": data.get("net_margin", 0),
                "gross_change": data.get("gross_margin_change", 0),
                "net_change": data.get("net_margin_change", 0)
            },
            "cash": {
                "operating": data.get("operating_cash_flow", 0),
                "free": data.get("free_cash_flow", 0),
                "cash_equiv": data.get("cash_and_equiv", 0)
            }
        }
    
    def _detect_alerts(self, data: Dict) -> List[Dict]:
        """检测异常信号"""
        alerts = []
        
        # 1. 营收增长但经营现金流下降
        if data.get("revenue_growth_yoy", 0) > 0 and data.get("operating_cash_flow_change", 0) < -20:
            alerts.append({
                "level": "⚠️",
                "type": "现金流异常",
                "description": "营收增长但经营现金流大幅下降，可能存在收入质量问题"
            })
        
        # 2. 应收账款增速 > 营收增速
        if data.get("receivable_growth", 0) > data.get("revenue_growth_yoy", 0) + 10:
            alerts.append({
                "level": "⚠️",
                "type": "应收款风险",
                "description": "应收账款增速超过营收增速，回款压力增大"
            })
        
        # 3. 存货异常增加
        if data.get("inventory_growth", 0) > data.get("revenue_growth_yoy", 0) + 20:
            alerts.append({
                "level": "⚠️",
                "type": "存货积压",
                "description": "存货增速明显高于营收增速，可能存在滞销"
            })
        
        # 4. 毛利率下滑
        if data.get("gross_margin_change", 0) < -3:
            alerts.append({
                "level": "⚠️",
                "type": "毛利率下滑",
                "description": f"毛利率下滑{abs(data.get('gross_margin_change', 0)):.1f}个百分点，竞争加剧或成本上升"
            })
        
        # 5. 由盈转亏
        if data.get("net_profit", 0) < 0 and data.get("previous_profit", 0) > 0:
            alerts.append({
                "level": "🚨",
                "type": "业绩转亏",
                "description": "本期由盈转亏，需重点关注"
            })
        
        # 6. 经营现金流持续为负
        if data.get("operating_cash_flow", 0) < 0 and data.get("previous_ocf", 0) < 0:
            alerts.append({
                "level": "⚠️",
                "type": "现金流失血",
                "description": "经营现金流持续为负，需关注造血能力"
            })
        
        if not alerts:
            alerts.append({
                "level": "✅",
                "type": "财务健康",
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
        alerts = result["alerts"]
        
        revenue_growth = metrics["revenue"]["yoy"]
        profit_growth = metrics["profit"]["yoy"]
        gross_margin = metrics["margins"]["gross"]
        
        # 构建总结
        parts = []
        
        # 成长性描述
        if revenue_growth > 50:
            parts.append("高增长")
        elif revenue_growth > 20:
            parts.append("稳健增长")
        elif revenue_growth > 0:
            parts.append("增长放缓")
        else:
            parts.append("收入下滑")
        
        # 盈利描述
        if profit_growth > 100:
            parts.append("利润爆发")
        elif profit_growth > 20:
            parts.append("盈利改善")
        elif profit_growth < 0:
            parts.append("盈利承压")
        
        # 财务健康
        has_alert = any(a["level"] in ["⚠️", "🚨"] for a in alerts)
        if not has_alert:
            parts.append("财务健康")
        
        return "，".join(parts)
    
    def format_report(self, analysis: Dict) -> str:
        """格式化输出一页纸报告"""
        lines = [
            f"📊 {analysis['company']} ({analysis['ticker']}) 财报速读",
            f"📅 报告期: {analysis['report_period']}",
            "=" * 50,
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
        lines.append(f"• 毛利率: {metrics['margins']['gross']:.1f}% " +
                    f"({'+' if metrics['margins']['gross_change'] > 0 else ''}{metrics['margins']['gross_change']:.1f}pp)")
        lines.append(f"• 净利率: {metrics['margins']['net']:.1f}%")
        lines.append(f"• 经营现金流: {metrics['cash']['operating']:.1f}亿元")
        lines.append("")
        
        # 异常预警
        lines.append("🔍 异常预警")
        for alert in analysis["alerts"]:
            lines.append(f"{alert['level']} {alert['type']}")
            lines.append(f"   {alert['description']}")
        lines.append("")
        
        # 一句话总结
        lines.extend([
            "=" * 50,
            f"💡 总结: {analysis['summary']}"
        ])
        
        return "\n".join(lines)


def demo():
    """演示：分析英诺赛科模拟数据"""
    reader = HKStockEarningsReader()
    
    # 模拟数据（实际使用时从财报中提取）
    sample_data = {
        "company": "英诺赛科",
        "ticker": "02577.HK",
        "period": "2024年第三季度",
        
        # 利润表
        "revenue": 12.3,
        "revenue_unit": "亿元",
        "revenue_growth_yoy": 45.2,
        "revenue_growth_qoq": 8.5,
        "net_profit": -2.1,
        "profit_unit": "亿元",
        "profit_growth_yoy": 15.0,  # 亏损收窄
        "gross_margin": 28.5,
        "gross_margin_change": 3.2,
        "net_margin": -17.1,
        
        # 资产负债表
        "inventory_days": 85,
        "receivable_days": 45,
        "debt_ratio": 0.55,
        "current_ratio": 1.8,
        
        # 现金流量表
        "operating_cash_flow": -2.1,
        "operating_cash_flow_change": -10.0,
        "previous_ocf": -3.5,
        "free_cash_flow": -3.8,
        "cash_and_equiv": 15.2,
        
        # 其他
        "roe": -5.2,
        "pe_ratio": None,  # 亏损无PE
        "inventory_growth": 25.0,
        "receivable_growth": 30.0,
        "previous_profit": -2.5
    }
    
    analysis = reader.analyze_earnings(sample_data)
    report = reader.format_report(analysis)
    
    # 保存结果
    import os
    output_dir = "/root/.openclaw/workspace/learning/earnings_reader/data"
    os.makedirs(output_dir, exist_ok=True)
    
    json_path = f"{output_dir}/earnings_analysis_{datetime.now().strftime('%Y%m%d')}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    report_path = f"{output_dir}/earnings_report_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(report)
    print(f"\n✅ 报告已保存: {report_path}")


if __name__ == "__main__":
    demo()
