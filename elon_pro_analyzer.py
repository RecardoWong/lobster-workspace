#!/usr/bin/env python3
"""
Elon Musk 推特监控 - 专业分析版
基于Moltbook/专业Agent推文分析方法
"""

import os
import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import Counter

class ElonMuskProAnalyzer:
    """马斯克推文专业分析器"""
    
    def __init__(self):
        self.api_key = os.environ.get('TWITTERAPI_IO_KEY') or "new1_47751911508746daafaf9194b664aaed"
        self.base_url = "https://api.twitterapi.io/twitter"
        self.target_user = "elonmusk"
        self.history_file = "/tmp/elon_tweet_history.json"
        
        # 改进的关键词库
        self.keywords = {
            'crypto': {
                'terms': ['doge', 'dogecoin', 'bitcoin', 'btc', 'crypto', 'cryptocurrency', 
                         'blockchain', 'token', '$doge', '$btc', 'memecoin'],
                'impact_level': 'high',
                'typical_movement': '±10-30%'
            },
            'tesla': {
                'terms': ['tesla', 'tsla', 'cybertruck', 'fsd', 'model s', 'model 3', 
                         'model x', 'model y', 'ev', 'electric vehicle'],
                'impact_level': 'medium',
                'typical_movement': '±3-8%'
            },
            'spacex': {
                'terms': ['spacex', 'mars', 'rocket', 'starship', 'falcon', 'launch', 
                         'landing', 'space', 'starlink', 'satellite'],
                'impact_level': 'low',
                'typical_movement': '概念相关'
            },
            'ai_tech': {
                'terms': ['ai', 'artificial intelligence', 'neural', 'gpt', 'neuralink', 
                         'tech', 'technology', 'robot', 'optimus'],
                'impact_level': 'medium',
                'typical_movement': 'AI概念股'
            }
        }
        
        # 讽刺/玩笑检测
        self.sarcasm_markers = ['lol', 'haha', '😂', 'joke', 'jk', 'just kidding', 
                               'obviously', 'definitely', 'sure', 'totally', 'probably']
        
        # 强度词
        self.intensity_words = {
            'strong': ['massive', 'huge', 'incredible', 'amazing', 'revolutionary', 
                      'game changer', 'breakthrough', 'moon', 'mars'],
            'moderate': ['good', 'great', 'nice', 'cool', 'interesting'],
            'mild': ['ok', 'fine', 'maybe', 'perhaps']
        }
    
    def fetch_recent_tweets(self, hours: int = 25) -> List[Dict]:
        """获取最近N小时的推文"""
        # API调用逻辑...
        pass
    
    def analyze_tweet_pro(self, tweet: Dict) -> Dict:
        """专业级推文分析（5层分析法）"""
        
        text = tweet.get('text', '')
        text_lower = text.lower()
        created = tweet.get('createdAt', '')
        likes = tweet.get('likeCount', 0)
        retweets = tweet.get('retweetCount', 0)
        
        analysis = {
            'basic': {},
            'entities': {},
            'semantic': {},
            'impact': {},
            'recommendation': {}
        }
        
        # === 第1层：基础信息 ===
        analysis['basic'] = {
            'id': tweet.get('id'),
            'created_at': created,
            'text': text,
            'likes': likes,
            'retweets': retweets,
            'replies': tweet.get('replyCount', 0),
            'engagement_rate': self._calc_engagement(likes, retweets, tweet.get('replyCount', 0)),
            'has_media': bool(tweet.get('media')),
            'is_reply': bool(tweet.get('inReplyToStatusId')),
            'is_retweet': bool(tweet.get('retweetedStatus'))
        }
        
        # === 第2层：实体识别 ===
        mentions = re.findall(r'@(\w+)', text)
        cashtags = re.findall(r'\$([A-Za-z]+)', text)
        hashtags = re.findall(r'#(\w+)', text)
        urls = re.findall(r'https?://[^\s]+', text)
        
        # 检测相关领域
        detected_categories = []
        for category, data in self.keywords.items():
            if any(term in text_lower for term in data['terms']):
                detected_categories.append({
                    'category': category,
                    'impact': data['impact_level'],
                    'typical_move': data['typical_movement']
                })
        
        analysis['entities'] = {
            'mentions': mentions,
            'cashtags': cashtags,
            'hashtags': hashtags,
            'urls': urls,
            'categories': detected_categories
        }
        
        # === 第3层：语义分析 ===
        # 讽刺检测
        sarcasm_score = sum(1 for marker in self.sarcasm_markers if marker in text_lower)
        is_likely_sarcasm = sarcasm_score >= 1 and likes > 100000  # 高互动+讽刺标记
        
        # 情感强度
        intensity = 'neutral'
        for level, words in self.intensity_words.items():
            if any(w in text_lower for w in words):
                intensity = level
                break
        
        # 情绪极性
        sentiment = self._analyze_sentiment(text_lower)
        
        analysis['semantic'] = {
            'sentiment': sentiment,
            'intensity': intensity,
            'sarcasm_score': sarcasm_score,
            'is_likely_sarcasm': is_likely_sarcasm,
            'tone': 'playful' if is_likely_sarcasm else sentiment['type'],
            'key_phrases': self._extract_key_phrases(text)
        }
        
        # === 第4层：影响评估 ===
        # 历史模式匹配
        historical_pattern = self._match_historical_pattern(text_lower, detected_categories)
        
        # 时间敏感性
        time_context = self._analyze_time_context(created)
        
        # 综合影响评分
        impact_score = self._calc_impact_score(
            likes, detected_categories, is_likely_sarcasm, 
            sentiment['score'], time_context
        )
        
        analysis['impact'] = {
            'score': impact_score,
            'level': 'high' if impact_score >= 8 else 'medium' if impact_score >= 5 else 'low',
            'historical_pattern': historical_pattern,
            'time_context': time_context,
            'predicted_assets': self._predict_affected_assets(detected_categories),
            'estimated_volatility': self._estimate_volatility(detected_categories, is_likely_sarcasm)
        }
        
        # === 第5层：行动建议 ===
        analysis['recommendation'] = self._generate_recommendation(
            impact_score, detected_categories, is_likely_sarcasm, time_context
        )
        
        return analysis
    
    def _calc_engagement(self, likes: int, retweets: int, replies: int) -> float:
        """计算互动率分数"""
        total = likes + retweets * 2 + replies * 3  # 不同权重
        if total > 500000:
            return 10.0
        elif total > 100000:
            return 7.0 + (total - 100000) / 400000 * 3
        elif total > 50000:
            return 5.0 + (total - 50000) / 50000 * 2
        else:
            return total / 50000 * 5
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """分析情感"""
        positive_words = ['love', 'great', 'amazing', 'awesome', 'bullish', 'moon', 'rocket']
        negative_words = ['hate', 'bad', 'terrible', 'bearish', 'crash', 'dump', 'scam']
        
        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        
        if pos_count > neg_count:
            return {'type': 'positive', 'score': min(pos_count * 2, 10)}
        elif neg_count > pos_count:
            return {'type': 'negative', 'score': min(neg_count * 2, 10)}
        else:
            return {'type': 'neutral', 'score': 5}
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """提取关键短语"""
        # 简化版：提取引号内容和重要声明
        phrases = []
        
        # 引号内容
        quotes = re.findall(r'"([^"]+)"', text)
        phrases.extend(quotes)
        
        # 大写强调
        caps = re.findall(r'\b[A-Z]{2,}\b', text)
        phrases.extend(caps[:3])  # 最多3个
        
        return phrases[:5]
    
    def _match_historical_pattern(self, text: str, categories: List[Dict]) -> str:
        """匹配历史模式"""
        if not categories:
            return 'general_comment'
        
        category = categories[0]['category']
        
        patterns = {
            'crypto': {
                'doge_direct': ['doge' in text, '直接提及DOGE，通常引发5-20%波动'],
                'crypto_general': ['crypto' in text or 'bitcoin' in text, '泛泛提及币圈，影响较小'],
                'meme_coin': ['meme' in text, '提及Meme概念，可能带动相关币种']
            },
            'tesla': {
                'product_announce': ['cybertruck' in text or 'fsd' in text, '产品相关，关注TSLA'],
                'production_update': ['production' in text or 'delivery' in text, '生产数据，影响股价']
            }
        }
        
        cat_patterns = patterns.get(category, {})
        for pattern_name, (condition, description) in cat_patterns.items():
            if condition:
                return f"{pattern_name}: {description}"
        
        return 'no_specific_pattern'
    
    def _analyze_time_context(self, created: str) -> Dict:
        """分析时间上下文"""
        try:
            # 解析时间
            dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
            hour = dt.hour
            weekday = dt.weekday()
            
            # 判断市场时段
            context = {
                'hour': hour,
                'weekday': weekday,
                'is_trading_hours': 9 <= hour <= 16 and weekday < 5,  # 美股交易时间
                'is_pre_market': 4 <= hour < 9 and weekday < 5,
                'is_after_hours': 16 <= hour <= 20 and weekday < 5,
                'is_weekend': weekday >= 5,
                'sensitivity': 'high' if (9 <= hour <= 16 and weekday < 5) else 'medium'
            }
            return context
        except:
            return {'sensitivity': 'unknown'}
    
    def _calc_impact_score(self, likes: int, categories: List[Dict], 
                          is_sarcasm: bool, sentiment_score: int, 
                          time_context: Dict) -> float:
        """计算综合影响分数"""
        score = 0
        
        # 互动分数 (0-3)
        if likes > 200000:
            score += 3
        elif likes > 100000:
            score += 2.5
        elif likes > 50000:
            score += 2
        elif likes > 10000:
            score += 1
        
        # 类别分数 (0-3)
        if categories:
            top_cat = categories[0]
            if top_cat['impact'] == 'high':
                score += 3
            elif top_cat['impact'] == 'medium':
                score += 2
            else:
                score += 1
        
        # 时间敏感性 (0-2)
        if time_context.get('sensitivity') == 'high':
            score += 2
        else:
            score += 1
        
        # 讽刺惩罚 (如果是讽刺，降低影响)
        if is_sarcasm:
            score *= 0.7
        
        # 情感强度加成
        if sentiment_score >= 8:
            score += 1
        
        return min(score, 10)
    
    def _predict_affected_assets(self, categories: List[Dict]) -> List[str]:
        """预测受影响的资产"""
        assets = []
        
        for cat in categories:
            cat_name = cat['category']
            if cat_name == 'crypto':
                assets.extend(['DOGE/USDT', 'DOGE/USD', 'BTC/USDT'])
            elif cat_name == 'tesla':
                assets.extend(['TSLA (美股)', '特斯拉概念股'])
            elif cat_name == 'spacex':
                assets.extend(['航天ETF (ITA)', 'SpaceX未上市'])
            elif cat_name == 'ai_tech':
                assets.extend(['AI概念股', 'NVDA', 'MSFT'])
        
        return list(set(assets))  # 去重
    
    def _estimate_volatility(self, categories: List[Dict], is_sarcasm: bool) -> str:
        """估计波动率"""
        if not categories:
            return "预计无显著波动"
        
        base_vol = categories[0].get('typical_move', '±5%')
        
        if is_sarcasm:
            return f"{base_vol} (但可能是讽刺，波动可能短暂)"
        
        return base_vol
    
    def _generate_recommendation(self, impact_score: float, categories: List[Dict],
                                is_sarcasm: bool, time_context: Dict) -> Dict:
        """生成行动建议"""
        
        rec = {
            'urgency': 'low',
            'action': 'observe',
            'timeline': '下次检查',
            'details': [],
            'risks': []
        }
        
        if impact_score >= 8:
            rec['urgency'] = 'high'
            rec['action'] = 'immediate_attention'
            rec['timeline'] = '立即查看相关资产'
            rec['details'].append('高影响力推文，可能引发市场剧烈波动')
            
        elif impact_score >= 5:
            rec['urgency'] = 'medium'
            rec['action'] = 'monitor_closely'
            rec['timeline'] = '30分钟内关注'
            rec['details'].append('中度影响，建议关注相关资产价格')
        
        else:
            rec['details'].append('影响有限，常规观察即可')
        
        if is_sarcasm:
            rec['details'].append('⚠️ 推文可能为讽刺/玩笑，市场可能过度反应')
            rec['risks'].append('追涨杀跌风险')
        
        if time_context.get('is_trading_hours'):
            rec['details'].append('美股交易时间内，股票相关影响更直接')
        elif time_context.get('is_weekend'):
            rec['details'].append('周末时段，币圈反应可能更快')
        
        return rec
    
    def generate_pro_report(self, analysis: Dict) -> str:
        """生成专业分析报告"""
        lines = [
            "🎯 Elon Musk 推文专业分析",
            f"⏰ 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 70,
            ""
        ]
        
        # 基础信息
        basic = analysis['basic']
        lines.append("📋 基础信息:")
        lines.append(f"  发布时间: {basic['created_at']}")
        lines.append(f"  互动数据: ❤️{basic['likes']:,} | 🔄{basic['retweets']:,} | 💬{basic['replies']:,}")
        lines.append(f"  互动评分: {basic['engagement_rate']:.1f}/10")
        lines.append("")
        
        # 原文+翻译
        lines.append("📝 推文内容:")
        lines.append(f"  {basic['text']}")
        
        translation = self._full_translate_v2(basic['text'])
        if translation:
            lines.append(f"\n🌐 翻译:")
            lines.append(f"  {translation}")
        lines.append("")
        
        # 语义分析
        semantic = analysis['semantic']
        lines.append("🔍 语义分析:")
        lines.append(f"  情绪: {semantic['sentiment']['type']} (强度: {semantic['sentiment']['score']}/10)")
        lines.append(f"  语气: {semantic['tone']}")
        lines.append(f"  讽刺可能: {'是 ⚠️' if semantic['is_likely_sarcasm'] else '否'}")
        if semantic['key_phrases']:
            lines.append(f"  关键短语: {', '.join(semantic['key_phrases'])}")
        lines.append("")
        
        # 影响评估
        impact = analysis['impact']
        lines.append("💹 影响评估:")
        lines.append(f"  影响分数: {impact['score']:.1f}/10 ({impact['level'].upper()})")
        lines.append(f"  预计波动: {impact['estimated_volatility']}")
        
        if impact['predicted_assets']:
            lines.append(f"  相关资产:")
            for asset in impact['predicted_assets'][:5]:
                lines.append(f"    • {asset}")
        
        if impact['historical_pattern'] != 'no_specific_pattern':
            lines.append(f"  历史模式: {impact['historical_pattern']}")
        lines.append("")
        
        # 行动建议
        rec = analysis['recommendation']
        emoji = "🔴" if rec['urgency'] == 'high' else "🟡" if rec['urgency'] == 'medium' else "⚪"
        lines.append(f"{emoji} 行动建议:")
        lines.append(f"  紧急度: {rec['urgency'].upper()}")
        lines.append(f"  建议操作: {rec['action']}")
        lines.append(f"  时间线: {rec['timeline']}")
        
        if rec['details']:
            lines.append(f"  详情:")
            for detail in rec['details']:
                lines.append(f"    • {detail}")
        
        if rec['risks']:
            lines.append(f"  ⚠️ 风险提示:")
            for risk in rec['risks']:
                lines.append(f"    • {risk}")
        
        lines.append("")
        lines.append("=" * 70)
        lines.append("💡 基于Moltbook专业Agent分析方法生成")
        
        return "\n".join(lines)
    
    def _full_translate_v2(self, text: str) -> str:
        """改进的翻译"""
        translations = {
            'dogecoin': '狗狗币', 'doge': 'DOGE',
            'bitcoin': '比特币', 'btc': 'BTC',
            'to the moon': '去月球（暴涨）',
            'rocket': '🚀火箭',
            'tesla': '特斯拉', 'tsla': 'TSLA股票',
            'cybertruck': '赛博皮卡',
            'mars': '火星',
        }
        
        result = text
        for eng, chn in translations.items():
            result = re.sub(r'\b' + re.escape(eng) + r'\b', chn, result, flags=re.IGNORECASE)
        
        return result if result != text else ""


def main():
    """测试专业分析"""
    analyzer = ElonMuskProAnalyzer()
    
    # 模拟推文测试
    test_tweets = [
        {
            'id': 'test1',
            'text': 'Dogecoin to the moon 🚀',
            'createdAt': '2026-02-11T10:00:00Z',
            'likeCount': 150000,
            'retweetCount': 45000,
            'replyCount': 8000
        },
        {
            'id': 'test2',
            'text': 'Tesla FSD is getting better every day lol',
            'createdAt': '2026-02-11T09:00:00Z',
            'likeCount': 80000,
            'retweetCount': 12000,
            'replyCount': 3000
        }
    ]
    
    for tweet in test_tweets:
        analysis = analyzer.analyze_tweet_pro(tweet)
        report = analyzer.generate_pro_report(analysis)
        print(report)
        print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
