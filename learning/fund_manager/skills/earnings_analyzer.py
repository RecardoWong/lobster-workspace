#!/usr/bin/env python3
"""
Skills层 - 财报超预期检测
自动分析财报数据，发现超预期/低于预期的机会
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class EarningsSurpriseType(Enum):
    BEAT_BOTH = "BEAT_BOTH"           # 营收利润双超预期
    BEAT_EPS_MISS_REV = "BEAT_EPS_MISS_REV"  # 利润超预期但营收低于
    MISS_EPS_BEAT_REV = "MISS_EPS_BEAT_REV"  # 营收超预期但利润低于
    MISS_BOTH = "MISS_BOTH"           # 双双低于预期
    IN_LINE = "IN_LINE"               # 符合预期

@dataclass
class EarningsAnalysis:
    ticker: str
    quarter: str
    surprise_type: EarningsSurpriseType
    eps_surprise_pct: float
    revenue_surprise_pct: float
    guidance_change: str  # raise/maintain/lower
    management_tone: str  # positive/cautious/negative
    market_reaction: str  # gap_up/flat/gap_down
    trading_signal: str   # buy/hold/sell
    confidence: str       # high/medium/low
    key_highlights: List[str]
    risks: List[str]

class EarningsAnalyzerSkill:
    """
    财报分析器
    自动分析财报超预期情况并生成交易信号
    """
    
    def analyze(self, ticker: str) -> EarningsAnalysis:
        """分析单家公司财报"""
        # 获取财报数据
        data = self._fetch_earnings_data(ticker)
        
        # 计算超预期情况
        surprise_type, eps_surprise, rev_surprise = self._calculate_surprise(data)
        
        # 分析管理层指引
        guidance = self._analyze_guidance(data)
        
        # 分析管理层语气
        tone = self._analyze_management_tone(data)
        
        # 预测市场反应
        reaction = self._predict_market_reaction(
            surprise_type, eps_surprise, rev_surprise, guidance, tone
        )
        
        # 生成交易信号
        signal, confidence = self._generate_trading_signal(
            surprise_type, eps_surprise, rev_surprise, guidance, tone
        )
        
        # 提取要点
        highlights = self._extract_highlights(data)
        risks = self._identify_risks(data)
        
        return EarningsAnalysis(
            ticker=ticker,
            quarter=data['quarter'],
            surprise_type=surprise_type,
            eps_surprise_pct=eps_surprise,
            revenue_surprise_pct=rev_surprise,
            guidance_change=guidance,
            management_tone=tone,
            market_reaction=reaction,
            trading_signal=signal,
            confidence=confidence,
            key_highlights=highlights,
            risks=risks
        )
    
    def _fetch_earnings_data(self, ticker: str) -> Dict:
        """获取财报数据"""
        # TODO: 从API获取真实数据
        # 模拟NVDA Q4 2024数据
        mock_data = {
            'NVDA': {
                'quarter': 'Q4 FY2024',
                'report_date': '2024-02-21',
                'revenue': 22100000000,  # $22.1B
                'revenue_estimate': 20400000000,  # $20.4B
                'revenue_growth': 2.65,  # 265%增长
                'eps': 5.16,
                'eps_estimate': 4.64,
                'eps_growth': 4.86,  # 486%增长
                'guidance_revenue': 24000000000,  # 下季指引$24B
                'guidance_revenue_consensus': 22200000000,
                'gross_margin': 0.767,
                'operating_margin': 0.654,
                'free_cash_flow': 11200000000,
                'transcript_snippets': [
                    'AI demand is surging beyond our expectations',
                    'Data center revenue grew 279% year-over-year',
                    'We see sustained growth ahead'
                ]
            },
            'TSLA': {
                'quarter': 'Q4 2023',
                'revenue': 25167000000,
                'revenue_estimate': 25870000000,  # 低于预期
                'eps': 0.71,
                'eps_estimate': 0.73,  # 略低于预期
                'guidance_revenue': None,  # 没有给出明确指引
                'transcript_snippets': [
                    'Volume growth may be lower in 2024',
                    'We are between two major growth waves'
                ]
            }
        }
        return mock_data.get(ticker, mock_data['NVDA'])
    
    def _calculate_surprise(self, data: Dict) -> tuple:
        """计算超预期情况"""
        # EPS超预期
        eps_actual = data.get('eps', 0)
        eps_estimate = data.get('eps_estimate', eps_actual)
        eps_surprise = (eps_actual - eps_estimate) / abs(eps_estimate) * 100
        
        # 营收超预期
        rev_actual = data.get('revenue', 0)
        rev_estimate = data.get('revenue_estimate', rev_actual)
        rev_surprise = (rev_actual - rev_estimate) / rev_estimate * 100
        
        # 判断类型
        eps_beat = eps_surprise > 5  # 超预期5%以上算beat
        rev_beat = rev_surprise > 2  # 营收超预期2%以上
        
        eps_miss = eps_surprise < -5
        rev_miss = rev_surprise < -2
        
        if eps_beat and rev_beat:
            surprise_type = EarningsSurpriseType.BEAT_BOTH
        elif eps_beat and rev_miss:
            surprise_type = EarningsSurpriseType.BEAT_EPS_MISS_REV
        elif eps_miss and rev_beat:
            surprise_type = EarningsSurpriseType.MISS_EPS_BEAT_REV
        elif eps_miss or rev_miss:
            surprise_type = EarningsSurpriseType.MISS_BOTH
        else:
            surprise_type = EarningsSurpriseType.IN_LINE
        
        return surprise_type, eps_surprise, rev_surprise
    
    def _analyze_guidance(self, data: Dict) -> str:
        """分析管理层指引"""
        guidance = data.get('guidance_revenue')
        consensus = data.get('guidance_revenue_consensus')
        
        if guidance and consensus:
            if guidance > consensus * 1.05:
                return 'raise'  # 上调指引
            elif guidance < consensus * 0.95:
                return 'lower'  # 下调指引
        
        return 'maintain'  # 维持或未给出明确指引
    
    def _analyze_management_tone(self, data: Dict) -> str:
        """分析管理层语气"""
        # TODO: 用NLP分析电话会议记录
        # 简化版：关键词匹配
        transcripts = data.get('transcript_snippets', [])
        text = ' '.join(transcripts).lower()
        
        positive_words = ['strong', 'growth', 'exceed', 'demand', 'confident', 'robust']
        negative_words = ['challenging', 'headwind', 'difficult', 'slowdown', 'pressure']
        
        positive_count = sum(1 for w in positive_words if w in text)
        negative_count = sum(1 for w in negative_words if w in text)
        
        if positive_count > negative_count + 2:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'cautious'
    
    def _predict_market_reaction(self, surprise_type, eps_surprise, rev_surprise, guidance, tone) -> str:
        """预测市场反应"""
        score = 0
        
        # 超预期情况
        if surprise_type == EarningsSurpriseType.BEAT_BOTH:
            score += 3
        elif surprise_type in [EarningsSurpriseType.BEAT_EPS_MISS_REV, EarningsSurpriseType.MISS_EPS_BEAT_REV]:
            score += 1
        elif surprise_type == EarningsSurpriseType.MISS_BOTH:
            score -= 2
        
        # 指引
        if guidance == 'raise':
            score += 2
        elif guidance == 'lower':
            score -= 2
        
        # 语气
        if tone == 'positive':
            score += 1
        elif tone == 'negative':
            score -= 1
        
        # 判断
        if score >= 3:
            return 'gap_up'  # 跳空高开
        elif score >= 0:
            return 'flat'    # 平开或小波动
        else:
            return 'gap_down'  # 跳空低开
    
    def _generate_trading_signal(self, surprise_type, eps_surprise, rev_surprise, guidance, tone) -> tuple:
        """生成交易信号"""
        # 强买入信号：双超预期 + 上调指引 + 积极语气
        if (surprise_type == EarningsSurpriseType.BEAT_BOTH and 
            guidance == 'raise' and 
            tone == 'positive'):
            return 'STRONG_BUY', 'HIGH'
        
        # 买入信号：超预期 + 积极语气
        elif (surprise_type in [EarningsSurpriseType.BEAT_BOTH, EarningsSurpriseType.BEAT_EPS_MISS_REV] and
              tone in ['positive', 'cautious']):
            return 'BUY', 'MEDIUM'
        
        # 卖出信号：低于预期 + 下调指引
        elif (surprise_type in [EarningsSurpriseType.MISS_BOTH, EarningsSurpriseType.MISS_EPS_BEAT_REV] and
              guidance == 'lower'):
            return 'SELL', 'HIGH'
        
        # 观察信号：混合结果
        elif surprise_type == EarningsSurpriseType.BEAT_EPS_MISS_REV:
            return 'HOLD_WATCH', 'MEDIUM'  # 利润好但营收差，需观察
        
        else:
            return 'HOLD', 'LOW'
    
    def _extract_highlights(self, data: Dict) -> List[str]:
        """提取财报亮点"""
        highlights = []
        
        # 增长亮点
        if data.get('revenue_growth', 0) > 0.50:
            highlights.append(f"营收同比增长{data['revenue_growth']*100:.0f}%，高速增长")
        
        if data.get('eps_growth', 0) > 0.50:
            highlights.append(f"EPS同比增长{data['eps_growth']*100:.0f}%，盈利能力爆发")
        
        # 盈利能力
        if data.get('gross_margin', 0) > 0.70:
            highlights.append(f"毛利率{data['gross_margin']*100:.1f}%，定价权强")
        
        # 现金流
        fcf = data.get('free_cash_flow', 0)
        if fcf > 5000000000:  # $5B+
            highlights.append(f"自由现金流${fcf/1e9:.1f}B，造血能力强劲")
        
        return highlights
    
    def _identify_risks(self, data: Dict) -> List[str]:
        """识别风险点"""
        risks = []
        
        # 增长放缓
        if data.get('revenue_growth', 100) < data.get('revenue_growth_prev', 100):
            risks.append("营收增速环比放缓")
        
        # 库存增加
        if data.get('inventory_growth', 0) > data.get('revenue_growth', 0):
            risks.append("库存增速超过营收，可能存在积压")
        
        # 指引保守
        if data.get('guidance_revenue') and data['guidance_revenue'] < data.get('revenue', 0):
            risks.append("下季指引低于本季，增长可持续性存疑")
        
        return risks
    
    def scan_earnings_season(self, tickers: List[str]) -> List[EarningsAnalysis]:
        """财报季扫描所有公司"""
        results = []
        for ticker in tickers:
            try:
                analysis = self.analyze(ticker)
                results.append(analysis)
            except Exception as e:
                print(f"Error analyzing {ticker}: {e}")
        
        # 按超预期程度排序
        results.sort(key=lambda x: x.eps_surprise_pct + x.revenue_surprise_pct, reverse=True)
        return results

# 测试
if __name__ == '__main__':
    skill = EarningsAnalyzerSkill()
    
    print("="*70)
    print("📊 财报超预期检测")
    print("="*70)
    
    # 分析NVDA
    nvda = skill.analyze('NVDA')
    print(f"\n🚀 {nvda.ticker} {nvda.quarter}")
    print(f"类型: {nvda.surprise_type.value}")
    print(f"EPS超预期: {nvda.eps_surprise_pct:+.1f}%")
    print(f"营收超预期: {nvda.revenue_surprise_pct:+.1f}%")
    print(f"指引: {nvda.guidance_change}")
    print(f"管理层语气: {nvda.management_tone}")
    print(f"预测市场反应: {nvda.market_reaction}")
    print(f"交易信号: {nvda.trading_signal} (置信度: {nvda.confidence})")
    print(f"\n亮点: {', '.join(nvda.key_highlights)}")
    
    # 分析TSLA
    print("\n" + "-"*70)
    tsla = skill.analyze('TSLA')
    print(f"\n⚡ {tsla.ticker} {tsla.quarter}")
    print(f"类型: {tsla.surprise_type.value}")
    print(f"EPS超预期: {tsla.eps_surprise_pct:+.1f}%")
    print(f"营收超预期: {tsla.revenue_surprise_pct:+.1f}%")
    print(f"交易信号: {tsla.trading_signal}")
    
    print("\n" + "="*70)
