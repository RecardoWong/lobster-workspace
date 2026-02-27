#!/usr/bin/env python3
"""
基金经理系统主入口
整合: FRED宏观数据 + 新闻情感分析 + 财报速读
完全免费，无需API Key
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skills.news_processor import NewsProcessor
from typing import Dict, Optional
from datetime import datetime


class FundManager:
    """基金经理系统"""
    
    def __init__(self, news_api_key: Optional[str] = None):
        """
        初始化基金经理系统
        
        Args:
            news_api_key: NewsAPI Key (可选，免费申请 https://newsapi.org/)
        """
        self.news_processor = NewsProcessor(news_api_key=news_api_key)
    
    def daily_market_scan(self) -> Dict:
        """
        每日市场扫描
        
        Returns:
            市场扫描报告
        """
        print("🔍 开始每日市场扫描...")
        
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'sections': {}
        }
        
        # 1. 新闻情感分析
        print("\n[1/3] 获取新闻情感...")
        try:
            news_result = self.news_processor.process_daily_news(
                days_back=1,
                max_articles=20
            )
            report['sections']['news_sentiment'] = news_result
        except Exception as e:
            print(f"[警告] 新闻获取失败: {e}")
            report['sections']['news_sentiment'] = {
                'status': 'error',
                'message': str(e)
            }
        
        # 2. 宏观数据 (FRED) ✅ 已接入
        print("\n[2/3] 获取宏观数据...")
        try:
            from fred_client import FREDClient
            fred = FREDClient()
            
            liquidity = fred.get_liquidity_summary()
            inflation = fred.get_inflation_signals()
            
            report['sections']['macro_data'] = {
                'status': 'success',
                'fed_funds_rate': liquidity.get('fed_funds_rate'),
                'treasury_10y': liquidity.get('treasury_10y'),
                'treasury_2y': liquidity.get('treasury_2y'),
                'yield_spread': liquidity.get('yield_spread'),
                'inverted': liquidity.get('inverted', False),
                'cpi': inflation.get('cpi'),
                'core_cpi': inflation.get('core_cpi')
            }
            print("  ✅ FRED数据获取成功")
        except Exception as e:
            print(f"  ⚠️ FRED数据获取失败: {e}")
            report['sections']['macro_data'] = {
                'status': 'error',
                'message': str(e)
            }
        
        # 3. 板块热点 (从新闻中提取)
        print("\n[3/3] 分析板块热点...")
        if news_result.get('status') == 'success':
            report['sections']['sector_hot'] = {
                'status': 'success',
                'hot_topics': news_result.get('hot_topics', [])
            }
        else:
            report['sections']['sector_hot'] = {
                'status': 'no_data',
                'hot_topics': []
            }
        
        print("\n✅ 市场扫描完成")
        return report
    
    def print_daily_report(self, report: Dict):
        """打印每日报告"""
        print("\n" + "="*70)
        print(f"📊 每日市场扫描报告 - {report['date']}")
        print("="*70)
        
        # 新闻情感
        news = report['sections'].get('news_sentiment', {})
        if news.get('status') == 'success':
            summary = news.get('sentiment_summary', {})
            print(f"\n🎭 市场情绪: {summary.get('mood', 'N/A')}")
            print(f"   平均分: {summary.get('average_score', 0):+.3f}")
            print(f"   正面: {summary.get('positive_ratio', 0)}% | "
                  f"负面: {summary.get('negative_ratio', 0)}%")
            
            # 热门主题
            topics = news.get('hot_topics', [])
            if topics:
                print(f"\n🔥 热门主题:")
                for t in topics[:5]:
                    print(f"   • {t['topic']}: {t['count']}篇")
        else:
            print(f"\n⚠️ 新闻数据: {news.get('message', '未获取')}")
        
        # 板块热点
        sector = report['sections'].get('sector_hot', {})
        
        # 宏观数据
        macro = report['sections'].get('macro_data', {})
        if macro.get('status') == 'success':
            print(f"\n🌍 宏观数据:")
            if macro.get('fed_funds_rate'):
                print(f"   联邦基金利率: {macro['fed_funds_rate']['value']}%")
            if macro.get('treasury_10y'):
                print(f"   10年期国债: {macro['treasury_10y']['value']}%")
            if macro.get('yield_spread') is not None:
                spread = macro['yield_spread']
                status = "⚠️ 倒挂" if macro.get('inverted') else "正常"
                print(f"   收益率利差: {spread}% ({status})")
            if macro.get('cpi'):
                print(f"   CPI: {macro['cpi']['value']} ({macro['cpi']['date']})")
        else:
            print(f"\n🌍 宏观数据: {macro.get('message', '未获取')}")
        
        print("\n" + "="*70)
    
    def get_earnings_report(self, ticker: str, market: str = "auto") -> Optional[Dict]:
        """
        获取财报速读
        
        Args:
            ticker: 股票代码
            market: 市场 (us/hk/cn/auto)
            
        Returns:
            财报报告
        """
        # 导入财报速读模块
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'earnings_reader'))
            from earnings_reader import EarningsReader
            
            reader = EarningsReader()
            return reader.analyze(ticker, market)
        except Exception as e:
            print(f"[错误] 财报读取失败: {e}")
            return None


# 命令行入口
if __name__ == "__main__":
    print("🚀 基金经理系统")
    print("="*70)
    
    # 初始化 (使用demo key，功能受限)
    manager = FundManager(news_api_key="demo")
    
    print("\n[提示] 使用真实NewsAPI Key可获取完整功能")
    print("申请: https://newsapi.org/register (免费100次/天)\n")
    
    # 每日扫描
    print("开始每日市场扫描...\n")
    report = manager.daily_market_scan()
    manager.print_daily_report(report)
    
    print("\n✅ 扫描完成")
