#!/usr/bin/env python3
"""
🧠 Monty Analyzer - 通用 AI 分析工具
安全执行 AI 生成的 Python 代码，用于数据分析、情绪判断、风险评估等
"""

import pydantic_monty
import json
from typing import Any, Dict, List, Callable, Optional
from datetime import datetime

class MontyAnalyzer:
    """
    通用 Monty 分析工具
    所有监控任务都可以调用这个类进行 AI 分析
    """
    
    def __init__(self):
        self.execution_log = []
    
    def analyze(self, code: str, inputs: Dict[str, Any], 
                external_functions: Optional[Dict[str, Callable]] = None,
                description: str = "") -> Dict[str, Any]:
        """
        通用分析方法
        
        Args:
            code: Python 代码字符串
            inputs: 输入数据字典
            external_functions: 外部函数字典 {name: function}
            description: 分析描述（用于日志）
        
        Returns:
            {
                'success': bool,
                'result': Any,  # 分析结果
                'execution_time_ms': float,
                'error': str,  # 如果失败
                'description': str
            }
        """
        start_time = datetime.now()
        
        try:
            # 创建 Monty 实例
            input_keys = list(inputs.keys())
            ext_func_names = list(external_functions.keys()) if external_functions else []
            
            m = pydantic_monty.Monty(
                code,
                inputs=input_keys,
                external_functions=ext_func_names
            )
            
            # 执行
            if external_functions:
                result = m.run(inputs=inputs, external_functions=external_functions)
            else:
                result = m.run(inputs=inputs)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # 记录日志
            log_entry = {
                'time': datetime.now().isoformat(),
                'description': description,
                'execution_time_ms': execution_time,
                'success': True,
                'result_preview': str(result)[:100] if result else None
            }
            self.execution_log.append(log_entry)
            
            return {
                'success': True,
                'result': result,
                'execution_time_ms': execution_time,
                'error': None,
                'description': description
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            log_entry = {
                'time': datetime.now().isoformat(),
                'description': description,
                'execution_time_ms': execution_time,
                'success': False,
                'error': str(e)
            }
            self.execution_log.append(log_entry)
            
            return {
                'success': False,
                'result': None,
                'execution_time_ms': execution_time,
                'error': str(e),
                'description': description
            }
    
    # ==================== 预置分析方法 ====================
    
    def analyze_tokens(self, tokens: List[Dict]) -> Dict[str, Any]:
        """
        分析 Meme 币数据
        用于: XXYY.io 监控
        """
        code = '''
# Meme 币数据分析
total_holders = 0
total_mc = 0
max_holders = 0
max_symbol = ''
hot_tokens = []
narrative_counts = {}

for token in tokens:
    h = token['holders']
    mc = token['mc']
    sym = token['symbol']
    nar = token.get('narrative', '其他')
    
    total_holders = total_holders + h
    total_mc = total_mc + mc
    
    if h > max_holders:
        max_holders = h
        max_symbol = sym
    
    if h >= 200:
        hot_tokens.append(sym)
    
    if nar in narrative_counts:
        narrative_counts[nar] = narrative_counts[nar] + 1
    else:
        narrative_counts[nar] = 1

avg_holders = total_holders / len(tokens) if tokens else 0
avg_mc = total_mc / len(tokens) if tokens else 0

{
    'total_tokens': len(tokens),
    'avg_holders': avg_holders,
    'avg_mc': avg_mc,
    'hottest_token': max_symbol,
    'hottest_holders': max_holders,
    'hot_tokens': hot_tokens,
    'narrative_distribution': narrative_counts,
    'risk_score': len(hot_tokens) / len(tokens) if tokens else 0
}
'''
        return self.analyze(code, {'tokens': tokens}, description="Meme币数据分析")
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        情绪分析
        用于: Twitter 推文分析
        """
        code = '''
# 情绪分析
positive_words = ['good', 'great', 'amazing', 'excellent', 'love', 'best', 'bullish', 'moon', 'pump']
negative_words = ['bad', 'terrible', 'worst', 'hate', 'bearish', 'dump', 'crash', 'scam', 'rug']

text_lower = text.lower()
positive_count = 0
negative_count = 0

for word in positive_words:
    if word in text_lower:
        positive_count = positive_count + 1

for word in negative_words:
    if word in text_lower:
        negative_count = negative_count + 1

score = positive_count - negative_count

if score > 0:
    sentiment = '看涨/积极'
elif score < 0:
    sentiment = '看跌/消极'
else:
    sentiment = '中性'

{
    'sentiment': sentiment,
    'score': score,
    'positive_count': positive_count,
    'negative_count': negative_count,
    'text_length': len(text)
}
'''
        return self.analyze(code, {'text': text}, description=f"推文情绪分析: {text[:50]}...")
    
    def analyze_portfolio(self, holdings: List[Dict]) -> Dict[str, Any]:
        """
        投资组合风险评估
        用于: 股票监控
        """
        code = '''
# 投资组合分析
total_value = 0
weighted_volatility = 0
sector_counts = {}
risk_levels = {'高风险': 0, '中风险': 0, '低风险': 0}

for stock in holdings:
    value = stock['shares'] * stock['price']
    volatility = stock.get('volatility', 0.5)
    sector = stock.get('sector', '其他')
    
    total_value = total_value + value
    weighted_volatility = weighted_volatility + value * volatility
    
    # 统计行业
    if sector in sector_counts:
        sector_counts[sector] = sector_counts[sector] + 1
    else:
        sector_counts[sector] = 1
    
    # 风险分级
    if volatility > 0.7:
        risk_levels['高风险'] = risk_levels['高风险'] + value
    elif volatility > 0.4:
        risk_levels['中风险'] = risk_levels['中风险'] + value
    else:
        risk_levels['低风险'] = risk_levels['低风险'] + value

avg_volatility = weighted_volatility / total_value if total_value > 0 else 0

if avg_volatility > 0.6:
    overall_risk = '高风险'
elif avg_volatility > 0.3:
    overall_risk = '中风险'
else:
    overall_risk = '低风险'

{
    'total_value': total_value,
    'avg_volatility': avg_volatility,
    'overall_risk': overall_risk,
    'risk_distribution': risk_levels,
    'sector_distribution': sector_counts,
    'stock_count': len(holdings)
}
'''
        return self.analyze(code, {'holdings': holdings}, description="投资组合风险评估")
    
    def detect_anomalies(self, data: List[Dict], threshold: float = 0.05) -> Dict[str, Any]:
        """
        异常检测
        用于: 供应商监控、价格监控
        """
        code = '''
# 异常检测
anomalies = []
changes = []

for item in data:
    change = item['change_pct']
    changes.append(change)
    
    if abs(change) > threshold:
        direction = '大涨' if change > 0 else '大跌'
        anomalies.append({
            'name': item['name'],
            'change_pct': change,
            'direction': direction
        })

# 计算统计数据
if changes:
    total_change = 0
    max_change = changes[0]
    min_change = changes[0]
    
    for c in changes:
        total_change = total_change + c
        if c > max_change:
            max_change = c
        if c < min_change:
            min_change = c
    
    avg_change = total_change / len(changes)
else:
    avg_change = 0
    max_change = 0
    min_change = 0

{
    'anomalies': anomalies,
    'anomaly_count': len(anomalies),
    'avg_change': avg_change,
    'max_change': max_change,
    'min_change': min_change,
    'threshold': threshold
}
'''
        return self.analyze(code, {'data': data, 'threshold': threshold}, 
                          description=f"异常检测 (阈值: {threshold})")
    
    def summarize_texts(self, texts: List[str], max_length: int = 100) -> Dict[str, Any]:
        """
        文本摘要（简单版本）
        用于: 推文汇总、新闻摘要
        """
        code = '''
# 文本摘要
all_text = ' '.join(texts)
words = all_text.split()

# 统计词频
word_counts = {}
for word in words:
    word = word.lower()
    # 简单过滤
    if len(word) > 3 and word not in ['the', 'and', 'for', 'with', 'this', 'that']:
        if word in word_counts:
            word_counts[word] = word_counts[word] + 1
        else:
            word_counts[word] = 1

# 找出高频词
top_words = []
for word, count in word_counts.items():
    if count > 1:
        top_words.append((word, count))

# 简单排序（冒泡）
for i in range(len(top_words)):
    for j in range(i + 1, len(top_words)):
        if top_words[j][1] > top_words[i][1]:
            temp = top_words[i]
            top_words[i] = top_words[j]
            top_words[j] = temp

# 取前5
keywords = []
for i in range(min(5, len(top_words))):
    keywords.append(top_words[i][0])

{
    'total_texts': len(texts),
    'total_words': len(words),
    'unique_words': len(word_counts),
    'keywords': keywords,
    'avg_length': len(all_text) / len(texts) if texts else 0
}
'''
        return self.analyze(code, {'texts': texts}, description="文本摘要分析")
    
    def get_log(self, n: int = 10) -> List[Dict]:
        """获取最近的执行日志"""
        return self.execution_log[-n:]
    
    def clear_log(self):
        """清空日志"""
        self.execution_log = []


# ==================== 便捷函数 ====================

_analyzer = MontyAnalyzer()

def analyze_tokens(tokens: List[Dict]) -> Dict:
    """分析 Meme 币"""
    return _analyzer.analyze_tokens(tokens)

def analyze_sentiment(text: str) -> Dict:
    """情绪分析"""
    return _analyzer.analyze_sentiment(text)

def analyze_portfolio(holdings: List[Dict]) -> Dict:
    """投资组合分析"""
    return _analyzer.analyze_portfolio(holdings)

def detect_anomalies(data: List[Dict], threshold: float = 0.05) -> Dict:
    """异常检测"""
    return _analyzer.detect_anomalies(data, threshold)

def summarize_texts(texts: List[str]) -> Dict:
    """文本摘要"""
    return _analyzer.summarize_texts(texts)


# ==================== 测试 ====================

if __name__ == "__main__":
    print("🧠 Monty Analyzer 测试\n")
    
    analyzer = MontyAnalyzer()
    
    # 测试1: Meme 币分析
    print("=" * 50)
    print("测试1: Meme 币分析")
    print("=" * 50)
    tokens = [
        {'symbol': 'CMP', 'holders': 245, 'mc': 20000, 'narrative': '敏感/争议'},
        {'symbol': 'INU', 'holders': 206, 'mc': 21000, 'narrative': '动物+金融'},
        {'symbol': 'DIGLETT', 'holders': 181, 'mc': 22000, 'narrative': '游戏/动漫'},
    ]
    result = analyzer.analyze_tokens(tokens)
    print(f"✅ 执行时间: {result['execution_time_ms']:.3f} ms")
    print(f"结果: {json.dumps(result['result'], indent=2, ensure_ascii=False)}")
    print()
    
    # 测试2: 情绪分析
    print("=" * 50)
    print("测试2: 情绪分析")
    print("=" * 50)
    tweet = "This is an amazing project! Love the bullish trend to the moon!"
    result = analyzer.analyze_sentiment(tweet)
    print(f"推文: {tweet}")
    print(f"✅ 执行时间: {result['execution_time_ms']:.3f} ms")
    print(f"结果: {result['result']}")
    print()
    
    # 测试3: 异常检测
    print("=" * 50)
    print("测试3: 异常检测")
    print("=" * 50)
    data = [
        {'name': '中国铝业', 'change_pct': 0.02},
        {'name': '蓝晓科技', 'change_pct': 0.08},
        {'name': '北方华创', 'change_pct': -0.06},
        {'name': '中微公司', 'change_pct': 0.01},
    ]
    result = analyzer.detect_anomalies(data, threshold=0.05)
    print(f"✅ 执行时间: {result['execution_time_ms']:.3f} ms")
    print(f"异常数: {result['result']['anomaly_count']}")
    print(f"异常项: {result['result']['anomalies']}")
    print()
    
    print("=" * 50)
    print("✅ 所有测试通过！")
    print("=" * 50)
    print(f"\n执行日志: {len(analyzer.execution_log)} 条记录")
