#!/usr/bin/env python3
"""
选题策划Agent - 人机协作内容生产线
每周一自动推送3-5个选题建议
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class TopicSource(Enum):
    MARKET_HOT = "市场热点"
    RESEARCH_NOTE = "投研笔记"
    SOCIAL_TREND = "社媒话题"
    READER_QUESTION = "读者问题"
    EVERGREEN = "常青话题"

class TopicPriority(Enum):
    HIGH = "高"      # 时效性强，必须本周发
    MEDIUM = "中"    # 有热度，建议本周发
    LOW = "低"       # 常青话题，可灵活安排

@dataclass
class TopicCandidate:
    title: str
    source: TopicSource
    priority: TopicPriority
    
    # 选题依据
    why_now: str           # 为什么现在写
    target_audience: str   # 目标读者
    key_angle: str         # 切入角度
    
    # 数据支撑
    heat_score: int        # 热度分数 0-100
    relevance_score: int   # 相关度分数 0-100
    uniqueness_score: int  # 差异化分数 0-100
    
    # 执行建议
    content_type: str      # 文章类型
    estimated_time: str    # 预计写作时间
    recommended_formula: str  # 建议使用的爆款公式
    
    # 参考素材
    reference_links: List[str]
    key_data_points: List[str]

class TopicGenerator:
    """选题生成器"""
    
    def __init__(self):
        self.hot_topics = []
        self.research_notes = []
        self.social_trends = []
        self.reader_questions = []
    
    def generate_weekly_topics(self) -> List[TopicCandidate]:
        """生成本周选题建议"""
        candidates = []
        
        # 1. 从市场热点生成选题 (1-2个)
        market_topics = self._generate_from_market()
        candidates.extend(market_topics)
        
        # 2. 从投研笔记生成选题 (1个)
        research_topics = self._generate_from_research()
        candidates.extend(research_topics)
        
        # 3. 从社媒话题生成选题 (1个)
        social_topics = self._generate_from_social()
        candidates.extend(social_topics)
        
        # 4. 从读者问题生成选题 (0-1个)
        reader_topics = self._generate_from_readers()
        candidates.extend(reader_topics)
        
        # 5. 补充常青话题 (如果需要)
        if len(candidates) < 3:
            evergreen_topics = self._generate_evergreen()
            candidates.extend(evergreen_topics)
        
        # 排序和筛选
        candidates = self._rank_candidates(candidates)
        
        return candidates[:5]  # 最多返回5个
    
    def _generate_from_market(self) -> List[TopicCandidate]:
        """从市场热点生成选题"""
        # TODO: 实际抓取市场数据
        # 这里模拟本周热点
        
        hot_events = [
            {
                'event': '英伟达财报超预期，AI概念继续狂飙',
                'heat': 95,
                'angle': '从英伟达看AI投资的泡沫与机会',
                'data': ['Q4营收$22.1B，同比+265%', '数据中心收入+279%', '盘后涨8.5%']
            },
            {
                'event': '美联储暗示提前降息，市场狂欢',
                'heat': 88,
                'angle': '降息周期开启，资产配置策略调整',
                'data': ['CPI 3.1%低于预期', '官员暗示可能提前降息', '美债收益率回落']
            },
            {
                'event': '比特币突破5万，加密市场回暖',
                'heat': 75,
                'angle': '比特币ETF后的市场逻辑变化',
                'data': ['BTC突破$51,000', 'ETF持续净流入', '矿工收益回升']
            }
        ]
        
        topics = []
        for event in hot_events[:2]:  # 取前2个
            topic = TopicCandidate(
                title=f"{event['angle']}",
                source=TopicSource.MARKET_HOT,
                priority=TopicPriority.HIGH if event['heat'] > 90 else TopicPriority.MEDIUM,
                why_now=f"{event['event']}，时效性强，读者关注度高",
                target_audience="关注市场的投资者",
                key_angle=event['angle'],
                heat_score=event['heat'],
                relevance_score=90,
                uniqueness_score=75,
                content_type="观点分析",
                estimated_time="3-4小时",
                recommended_formula="数字冲击型标题 + 先破后立开头 + 金字塔论证",
                reference_links=["相关新闻链接1", "数据图表链接"],
                key_data_points=event['data']
            )
            topics.append(topic)
        
        return topics
    
    def _generate_from_research(self) -> List[TopicCandidate]:
        """从投研笔记生成选题"""
        # TODO: 读取投研笔记数据库
        
        research_thoughts = [
            {
                'title': "价值投资框架2.0：如何用算法替代人工判断",
                'insight': "把投资决策系统化、公式化",
                'uniqueness': 95
            },
            {
                'title': "宏观流动性监控实战：FRED数据的妙用",
                'insight': "用免费数据判断市场拐点",
                'uniqueness': 85
            }
        ]
        
        thought = research_thoughts[0]  # 取最新的
        
        return [TopicCandidate(
            title=thought['title'],
            source=TopicSource.RESEARCH_NOTE,
            priority=TopicPriority.MEDIUM,
            why_now="近期完成了投资系统的升级，有实战案例可以分享",
            target_audience="想提升投资效率的进阶投资者",
            key_angle=thought['insight'],
            heat_score=70,
            relevance_score=95,
            uniqueness_score=thought['uniqueness'],
            content_type="方法论/教程",
            estimated_time="4-5小时",
            recommended_formula="身份反差型标题 + 教程式结构 + CTA结尾",
            reference_links=["投资系统代码链接", "回测数据链接"],
            key_data_points=["系统运行3个月的效果", "成本节省99%", "信号准确率统计"]
        )]
    
    def _generate_from_social(self) -> List[TopicCandidate]:
        """从社媒话题生成选题"""
        # TODO: 监控Twitter/小红书/即刻等平台
        
        social_trends = [
            {
                'topic': "年轻人该不该all in crypto",
                'volume': '高',
                'sentiment': '两极分化'
            },
            {
                'topic': "30岁该有多少存款",
                'volume': '极高',
                'sentiment': '焦虑'
            }
        ]
        
        trend = social_trends[1]  # 选争议性话题
        
        return [TopicCandidate(
            title=f"30岁该有多少存款？我算了一笔账，真相可能和你想的不一样",
            source=TopicSource.SOCIAL_TREND,
            priority=TopicPriority.MEDIUM,
            why_now=f"社交媒体上{trend['topic']}讨论热度{trend['volume']}，情绪{trend['sentiment']}",
            target_audience="25-35岁职场人群",
            key_angle="用数据拆解焦虑，给出务实建议",
            heat_score=85,
            relevance_score=80,
            uniqueness_score=70,
            content_type="观点分析",
            estimated_time="2-3小时",
            recommended_formula="提问型标题 + 数据钩子 + 对比论证 + 情绪共鸣结尾",
            reference_links=["相关讨论截图", "数据统计来源"],
            key_data_points=["一线城市vs二三线城市", "不同行业收入分布", "存钱vs投资的平衡"]
        )]
    
    def _generate_from_readers(self) -> List[TopicCandidate]:
        """从读者问题生成选题"""
        # TODO: 读取评论区高频问题
        
        reader_qs = [
            {
                'question': "如何开始定投？选什么标的？",
                'frequency': '高频',
                'complexity': '入门'
            },
            {
                'question': "现在还能买NVDA吗？会不会太高了？",
                'frequency': '中频',
                'complexity': '进阶'
            }
        ]
        
        q = reader_qs[1]  # 选时效性强的
        
        return [TopicCandidate(
            title="现在还能买NVDA吗？我的判断逻辑是这样的",
            source=TopicSource.READER_QUESTION,
            priority=TopicPriority.HIGH,
            why_now=f"读者多次提问'{q['question']}'，结合最新财报给出答案",
            target_audience="持有或想买入NVDA的投资者",
            key_angle="不直接给答案，教判断逻辑",
            heat_score=90,
            relevance_score=95,
            uniqueness_score=80,
            content_type="问答/分析",
            estimated_time="2-3小时",
            recommended_formula="提问型标题 + 先破后立开头 + 清单式论证",
            reference_links=["读者提问截图", "NVDA财报数据"],
            key_data_points=["当前估值水平", "增长预期vs历史", "风险因素清单"]
        )]
    
    def _generate_evergreen(self) -> List[TopicCandidate]:
        """生成常青话题"""
        evergreen_topics = [
            {
                'title': "我读了100本投资书籍，真正有用的只有这5本",
                'value': '长期有效'
            },
            {
                'title': "从零开始学投资：我的3年成长路径",
                'value': '入门必读'
            }
        ]
        
        topic = evergreen_topics[0]
        
        return [TopicCandidate(
            title=topic['title'],
            source=TopicSource.EVERGREEN,
            priority=TopicPriority.LOW,
            why_now="暂无强时效性选题，用常青内容补充",
            target_audience="投资新手",
            key_angle="书单推荐+阅读顺序",
            heat_score=60,
            relevance_score=85,
            uniqueness_score=70,
            content_type="书单/资源",
            estimated_time="3-4小时",
            recommended_formula="数字型标题 + 清单式结构 + 价值承诺",
            reference_links=["书籍购买链接", "读书笔记链接"],
            key_data_points=["5本书的核心观点", "适合人群", "阅读顺序建议"]
        )]
    
    def _rank_candidates(self, candidates: List[TopicCandidate]) -> List[TopicCandidate]:
        """排序选题"""
        # 综合评分 = 热度*0.3 + 相关度*0.3 + 差异化*0.2 + 时效性*0.2
        def score(c: TopicCandidate):
            priority_weight = {'高': 1.3, '中': 1.0, '低': 0.8}
            p_weight = priority_weight.get(c.priority.value, 1.0)
            
            base_score = (
                c.heat_score * 0.3 +
                c.relevance_score * 0.3 +
                c.uniqueness_score * 0.2 +
                80 * 0.2  # 时效性默认80
            )
            
            return base_score * p_weight
        
        return sorted(candidates, key=score, reverse=True)
    
    def format_report(self, topics: List[TopicCandidate]) -> str:
        """格式化选题报告"""
        lines = [
            f"📋 本周选题建议 ({datetime.now().strftime('%Y-%m-%d')})",
            "="*70,
            f"\n共筛选出 {len(topics)} 个候选选题，建议重点考虑前3个：\n"
        ]
        
        for i, topic in enumerate(topics, 1):
            priority_emoji = {"高": "🔴", "中": "🟡", "低": "🟢"}
            
            lines.extend([
                f"\n{'='*70}",
                f"{priority_emoji.get(topic.priority.value, '⚪')} 选题 {i}: {topic.title}",
                f"{'='*70}",
                f"📊 优先级: {topic.priority.value} | 来源: {topic.source.value}",
                f"\n💡 为什么现在写:",
                f"   {topic.why_now}",
                f"\n🎯 目标读者: {topic.target_audience}",
                f"   切入角度: {topic.key_angle}",
                f"\n📈 数据评估:",
                f"   热度: {topic.heat_score}/100 | 相关度: {topic.relevance_score}/100 | 差异化: {topic.uniqueness_score}/100",
                f"\n✍️ 写作建议:",
                f"   类型: {topic.content_type}",
                f"   预计用时: {topic.estimated_time}",
                f"   推荐公式: {topic.recommended_formula}",
                f"\n📎 参考素材:",
            ])
            
            for data in topic.key_data_points:
                lines.append(f"   • {data}")
            
            lines.append(f"\n⏰ 建议发布时间: 根据时效性安排")
        
        lines.extend([
            "\n" + "="*70,
            "💬 决策说明:",
            "  请从以上选题中选择3-5个，考虑因素:",
            "  1. 时效性：🔴高优先级建议本周发",
            "  2. 你的兴趣：选你有表达欲的话题",
            "  3. 读者需求：选评论区问得多的问题",
            "",
            "回复数字(如: 1,3,5)告诉我你的选择!",
            "="*70
        ])
        
        return '\n'.join(lines)

# 测试
if __name__ == '__main__':
    generator = TopicGenerator()
    
    print("="*70)
    print("📋 选题策划Agent - 测试运行")
    print("="*70)
    
    topics = generator.generate_weekly_topics()
    report = generator.format_report(topics)
    
    print(report)
    
    # 保存到文件
    with open(f'/root/.openclaw/workspace/content_analyzer/reports/topic_suggestions_{datetime.now().strftime("%Y%m%d")}.txt', 'w') as f:
        f.write(report)
    
    print(f"\n✅ 报告已保存到 reports/topic_suggestions_{datetime.now().strftime('%Y%m%d')}.txt")
