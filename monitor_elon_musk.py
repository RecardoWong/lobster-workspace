#!/usr/bin/env python3
"""
Elon Musk 推特监控 - 专业5层分析版
基于Moltbook/专业Agent推文分析方法
"""

import os
import re
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import Counter

class ElonMuskMonitor:
    """马斯克推特专业监控器"""
    
    def __init__(self):
        self.api_key = os.environ.get('TWITTERAPI_IO_KEY') or "new1_47751911508746daafaf9194b664aaed"
        self.base_url = "https://api.twitterapi.io/twitter"
        self.target_user = "elonmusk"
        self.history_file = "/tmp/elon_tweet_history.json"
        
        # 专业关键词库
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
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """发送API请求"""
        url = f"{self.base_url}{endpoint}"
        if params:
            query = '&'.join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])
            url = f"{url}?{query}"
        
        headers = {
            'X-API-Key': self.api_key,
            'User-Agent': 'ElonMonitor/1.0'
        }
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            return {'error': str(e)}
    
    def get_latest_tweets(self, max_results: int = 10) -> List[Dict]:
        """获取最新推文"""
        endpoint = "/tweet/advanced_search"
        params = {
            'query': f'from:{self.target_user}',
            'queryType': 'Latest',
            'count': max_results
        }
        
        result = self._make_request(endpoint, params)
        return result.get('tweets', [])
    
    def check_new_tweets(self) -> Tuple[bool, List[Dict]]:
        """检查新推文"""
        tweets = self.get_latest_tweets(max_results=10)
        
        # 读取历史
        history = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
            except:
                pass
        
        # 找新推文
        history_ids = {h.get('id') for h in history}
        new_tweets = [t for t in tweets if t.get('id') not in history_ids]
        
        # 保存当前记录
        if tweets:
            with open(self.history_file, 'w') as f:
                json.dump(tweets[:20], f)
        
        return len(new_tweets) > 0, new_tweets
    
    def analyze_tweet_pro(self, tweet: Dict) -> Dict:
        """专业5层分析"""
        
        # 优先获取完整文本（Twitter API可能有full_text字段）
        text = tweet.get('full_text', '') or tweet.get('text', '')
        text_lower = text.lower()
        created = tweet.get('createdAt', '')
        likes = tweet.get('likeCount', 0)
        retweets = tweet.get('retweetCount', 0)
        replies = tweet.get('replyCount', 0)
        
        analysis = {}
        
        # === Layer 1: 基础信息 ===
        analysis['basic'] = {
            'id': tweet.get('id'),
            'created_at': created,
            'text': text,  # 优先使用可能存在的完整文本
            'full_text': tweet.get('full_text', text),  # 保存完整文本备用
            'likes': likes,
            'retweets': retweets,
            'replies': replies,
            'engagement_score': min((likes + retweets * 2 + replies * 3) / 50000, 10)
        }
        
        # === Layer 2: 实体识别 ===
        mentions = re.findall(r'@(\w+)', text)
        cashtags = re.findall(r'\$([A-Za-z]+)', text)
        hashtags = re.findall(r'#(\w+)', text)
        
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
            'categories': detected_categories
        }
        
        # === Layer 3: 语义分析 ===
        sarcasm_score = sum(1 for marker in self.sarcasm_markers if marker in text_lower)
        is_sarcasm = sarcasm_score >= 1 and likes > 100000
        
        intensity = 'neutral'
        for level, words in self.intensity_words.items():
            if any(w in text_lower for w in words):
                intensity = level
                break
        
        # 情绪分析
        positive = ['love', 'great', 'amazing', 'awesome', 'bullish', 'moon', 'rocket']
        negative = ['hate', 'bad', 'terrible', 'bearish', 'crash', 'dump']
        pos_count = sum(1 for w in positive if w in text_lower)
        neg_count = sum(1 for w in negative if w in text_lower)
        sentiment = 'positive' if pos_count > neg_count else 'negative' if neg_count > pos_count else 'neutral'
        
        analysis['semantic'] = {
            'sentiment': sentiment,
            'intensity': intensity,
            'is_sarcasm': is_sarcasm,
            'sarcasm_warning': '⚠️ 可能为讽刺/玩笑' if is_sarcasm else '否'
        }
        
        # === Layer 4: 影响评估 ===
        # 计算影响分数
        score = 0
        if likes > 200000: score += 3
        elif likes > 100000: score += 2.5
        elif likes > 50000: score += 2
        elif likes > 10000: score += 1
        
        if detected_categories:
            if detected_categories[0]['impact'] == 'high': score += 3
            elif detected_categories[0]['impact'] == 'medium': score += 2
            else: score += 1
        
        if is_sarcasm: score *= 0.7
        
        impact_level = 'high' if score >= 8 else 'medium' if score >= 5 else 'low'
        
        # 预测受影响资产
        assets = []
        for cat in detected_categories:
            if cat['category'] == 'crypto':
                assets.extend(['DOGE/USDT', 'BTC/USDT', 'DOGE/USD'])
            elif cat['category'] == 'tesla':
                assets.extend(['TSLA (美股)', '特斯拉概念股'])
            elif cat['category'] == 'spacex':
                assets.extend(['航天ETF', 'SpaceX相关'])
        
        analysis['impact'] = {
            'score': round(score, 1),
            'level': impact_level,
            'level_emoji': '🔴' if impact_level == 'high' else '🟡' if impact_level == 'medium' else '⚪',
            'predicted_assets': list(set(assets))[:5],
            'volatility_estimate': detected_categories[0]['typical_move'] if detected_categories else '±5%'
        }
        
        # === Layer 5: 行动建议 ===
        if impact_level == 'high':
            action = {'urgency': 'HIGH', 'action': '立即关注', 'timeline': '马上查看'}
        elif impact_level == 'medium':
            action = {'urgency': 'MEDIUM', 'action': '密切监控', 'timeline': '30分钟内'}
        else:
            action = {'urgency': 'LOW', 'action': '常规观察', 'timeline': '下次检查'}
        
        if is_sarcasm:
            action['warning'] = '推文可能为讽刺，市场可能过度反应，谨慎追涨'
        
        analysis['recommendation'] = action
        
        return analysis
    
    def generate_pro_alert(self, analyses: List[Dict]) -> str:
        """生成专业推送"""
        lines = [
            "🚨 ELON MUSK 新推文检测",
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 70,
            ""
        ]
        
        for i, analysis in enumerate(analyses, 1):
            basic = analysis['basic']
            entities = analysis['entities']
            semantic = analysis['semantic']
            impact = analysis['impact']
            rec = analysis['recommendation']
            
            # 标题
            lines.append(f"\n{impact['level_emoji']} 推文 #{i} | 影响级别: {impact['level']}")
            lines.append(f"⏰ 发布时间: {basic['created_at'][:16]}")
            lines.append("-" * 70)
            
            # Layer 1: 基础
            lines.append("\n📋 基础信息:")
            lines.append(f"  互动: ❤️{basic['likes']:,} | 🔄{basic['retweets']:,} | 💬{basic['replies']:,}")
            lines.append(f"  互动评分: {basic['engagement_score']:.1f}/10")
            
            # 原文+翻译 - 同时显示英文和中文
            full_text = basic.get('full_text', basic['text'])
            tweet_id = basic.get('id', '')
            
            lines.append(f"\n📝 英文原文:")
            lines.append(f"  {full_text}")
            
            # 自动生成中文翻译
            lines.append(f"\n🌐 中文翻译:")
            chinese_translation = self._translate_to_chinese(full_text)
            lines.append(f"  {chinese_translation}")
            
            # 如果被截断，提供链接
            if '…' in full_text or full_text.endswith('...') or len(full_text) > 280:
                if tweet_id:
                    lines.append(f"\n  🔗 查看完整推文: https://x.com/elonmusk/status/{tweet_id}")
            
            # Layer 2: 实体
            if entities['categories']:
                lines.append(f"\n🏷️ 相关领域:")
                for cat in entities['categories']:
                    lines.append(f"  • {cat['category']} ({cat['impact']})")
            
            if entities['mentions']:
                lines.append(f"  提及: {', '.join(entities['mentions'][:3])}")
            
            # Layer 3: 语义
            lines.append(f"\n🔍 语义分析:")
            lines.append(f"  情绪: {semantic['sentiment']} | 强度: {semantic['intensity']}")
            if semantic['is_sarcasm']:
                lines.append(f"  ⚠️ 讽刺警告: {semantic['sarcasm_warning']}")
            
            # Layer 4: 影响
            lines.append(f"\n💹 影响评估:")
            lines.append(f"  影响分数: {impact['score']}/10")
            lines.append(f"  预计波动: {impact['volatility_estimate']}")
            if impact['predicted_assets']:
                lines.append(f"  相关资产:")
                for asset in impact['predicted_assets']:
                    lines.append(f"    • {asset}")
            
            # Layer 5: 建议
            lines.append(f"\n{impact['level_emoji']} 行动建议:")
            lines.append(f"  紧急度: {rec['urgency']}")
            lines.append(f"  操作建议: {rec['action']}")
            lines.append(f"  时间线: {rec['timeline']}")
            if 'warning' in rec:
                lines.append(f"  ⚠️ 提醒: {rec['warning']}")
            
            lines.append("\n" + "=" * 70)
        
        lines.append("\n💡 基于Moltbook专业Agent 5层分析法")
        return "\n".join(lines)
    
    def _translate(self, text: str) -> str:
        """翻译关键术语"""
        translations = {
            'dogecoin': '狗狗币', 'doge': 'DOGE',
            'bitcoin': '比特币', 'btc': 'BTC',
            'to the moon': '去月球（暴涨）',
            'rocket': '🚀火箭',
            'tesla': '特斯拉', 'tsla': 'TSLA',
            'cybertruck': '赛博皮卡',
            'mars': '火星',
            'launch': '发射',
            'ai': 'AI',
            'artificial intelligence': '人工智能'
        }
        
        result = text
        for eng, chn in translations.items():
            result = re.sub(r'\b' + re.escape(eng) + r'\b', chn, result, flags=re.IGNORECASE)
        
        return result if result != text else ""
    
    def _translate_to_chinese(self, text: str) -> str:
        """整句翻译为中文"""
        import re
        
        # 如果是纯中文，直接返回
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            return text
        
        # 常用短语整句翻译
        translations = {
            # 问候/日常
            r'\bgm\b': '早上好',
            r'\bgn\b': '晚安', 
            r'\bhello\b': '你好',
            r'\bhi\b': '嗨',
            r'\bthanks?\b': '谢谢',
            r'\bthank you\b': '谢谢你',
            
            # 情绪表达
            r'\blol\b': '哈哈',
            r'\bhaha\b': '哈哈',
            r'\bwow\b': '哇',
            r'\bamazing\b': '太棒了',
            r'\bawesome\b': '厉害',
            r'\bterrible\b': '糟糕',
            r'\bgreat\b': '很棒',
            r'\bgood\b': '好的',
            r'\bbravo\b': '太棒了',
            r'\babsolutely\b': '完全同意',
            r'\btrue\b': '确实',
            r'\bugh\b': '呃/唉',
            r'\bdisturbing\b': '令人不安',
            
            # 币圈/股票
            r'\bdogecoin\b': '狗狗币',
            r'\bdoge\b': '狗狗币',
            r'\bbitcoin\b': '比特币',
            r'\bbtc\b': '比特币',
            r'\bto the moon\b': '暴涨/去月球',
            r'\bro\b': '火箭',
            r'\bcrypto\b': '加密货币',
            r'\btesla\b': '特斯拉',
            r'\btsla\b': '特斯拉股票',
            r'\bstock\b': '股票',
            r'\bmarket\b': '市场',
            
            # SpaceX
            r'\bspacex\b': 'SpaceX',
            r'\bmars\b': '火星',
            r'\brocket\b': '火箭',
            r'\blaunch\b': '发射',
            
            # 常用句型
            r'\bi think\b': '我认为',
            r'\bi believe\b': '我相信',
        }
        
        translated = text
        for pattern, chinese in translations.items():
            translated = re.sub(pattern, chinese, translated, flags=re.IGNORECASE)
        
        # 如果翻译后有明显变化，返回翻译
        if translated != text:
            return translated
        
        # 如果没有匹配到复杂句型，返回原文+提示
        return text + "\n  [英文推文，可点击链接查看原文]"


def main():
    """主函数"""
    monitor = ElonMuskMonitor()
    
    # 检查新推文
    has_new, new_tweets = monitor.check_new_tweets()
    
    if has_new:
        print(f"🔔 发现 {len(new_tweets)} 条新推文！\n")
        
        # 专业5层分析每条推文
        analyses = [monitor.analyze_tweet_pro(t) for t in new_tweets]
        
        # 生成专业推送
        alert = monitor.generate_pro_alert(analyses)
        print(alert)
        
        # 保存
        filename = f"/tmp/elon_pro_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(alert)
        print(f"\n💾 专业分析报告已保存: {filename}")
        
    else:
        print("📭 马斯克暂无新推文")


if __name__ == "__main__":
    main()
