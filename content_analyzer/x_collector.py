#!/usr/bin/env python3
"""
X平台数据采集器
爬取财经/科技领域爆款文章，提取爆款公式
"""

import json
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urlencode

@dataclass
class XPost:
    """X平台帖子数据结构"""
    post_id: str
    author: str
    author_handle: str
    content: str
    created_at: datetime
    
    # 互动数据
    views: int
    likes: int
    retweets: int
    replies: int
    bookmarks: int
    
    # 分类标签
    category: str  # finance/tech/investment
    hashtags: List[str]
    
    # 质量评估
    engagement_rate: float
    is_viral: bool  # 是否爆款

class XDataCollector:
    """X平台数据采集器"""
    
    def __init__(self):
        # 目标账号列表 (财经/科技领域大V)
        self.target_accounts = {
            'finance': [
                'tracyalloway',     # Tracy Alloway
                'biancoresearch',   # Bianco Research
                'LizAnnSonders',    # Liz Ann Sonders
                'DougKass',         # Doug Kass
                'michaeljburry',    # Michael Burry
                'chamath',          # Chamath
                'howardmarksbook',  # Howard Marks
                'BillAckman',       # Bill Ackman
            ],
            'tech': [
                'elonmusk',         # Elon Musk
                'sama',             # Sam Altman
                'naval',            # Naval
                'balajis',          # Balaji
                'paulg',            # Paul Graham
                'sbf_ftx',          # SBF (经验教训)
            ],
            'crypto': [
                'woonomic',         # Willy Woo
                'glassnode',        # Glassnode
                'CryptoCred',       # CryptoCred
            ]
        }
        
        # 爆款标准
        self.viral_threshold = {
            'views': 100000,      # 10万浏览
            'likes': 5000,        # 5000赞
            'engagement_rate': 0.05  # 5%互动率
        }
        
        # 关键词过滤
        self.keywords = {
            'finance': ['投资', '股票', '基金', '理财', '财报', '美联储', '加息', '降息', '通胀', 'CPI'],
            'tech': ['AI', '人工智能', '大模型', 'ChatGPT', '科技', '创业', '硅谷', '产品'],
            'crypto': ['比特币', 'BTC', '以太坊', 'ETH', '加密货币', '区块链', '挖矿']
        }
    
    def collect_posts(self, days_back: int = 7, max_posts: int = 200) -> List[XPost]:
        """
        采集帖子
        
        方案1: Twitter API v2 (付费 $100/月)
        方案2: Nitter 实例 (免费，不稳定)
        方案3: RSSHub (免费，需要部署)
        方案4: 浏览器自动化 (Playwright/Selenium)
        
        这里实现方案4的模拟数据，实际使用需接入真实数据源
        """
        # TODO: 接入真实采集方式
        # 当前返回模拟数据用于测试系统
        
        mock_posts = self._generate_mock_data(days_back)
        
        # 筛选爆款
        viral_posts = [p for p in mock_posts if p.is_viral]
        
        return viral_posts[:max_posts]
    
    def _generate_mock_data(self, days_back: int) -> List[XPost]:
        """生成模拟数据 (实际使用时删除)"""
        posts = []
        
        # 基于真实爆款改写的模拟数据
        mock_data = [
            {
                'author': 'Michael Burry',
                'handle': '@michaeljburry',
                'content': '''The S&P 500 is at a critical juncture. Here's what the data is telling us:

1. Market breadth is deteriorating
2. Insider selling at 20-year highs
3. Consumer credit delinquencies rising

History doesn't repeat, but it rhymes. 2007 vibes.''',
                'views': 2500000,
                'likes': 45000,
                'retweets': 18000,
                'category': 'finance'
            },
            {
                'author': 'Naval',
                'handle': '@naval',
                'content': '''How to get rich (without getting lucky):

1. Seek wealth, not money or status
2. Play iterated games
3. Pick business partners with high intelligence, energy, and integrity
4. Learn to sell. Learn to build.
5. Arm yourself with specific knowledge

A thread...''',
                'views': 5000000,
                'likes': 120000,
                'retweets': 45000,
                'category': 'tech'
            },
            {
                'author': 'Chamath',
                'handle': '@chamath',
                'content': '''3 things I learned from losing $100M:

1. Conviction without flexibility is arrogance
2. Never confuse a bull market for brains
3. The best investment is in yourself

Full post: [link]''',
                'views': 1800000,
                'likes': 67000,
                'retweets': 22000,
                'category': 'finance'
            },
            {
                'author': 'Willy Woo',
                'handle': '@woonomic',
                'content': '''Bitcoin on-chain analysis thread 🧵

5 indicators showing we're at a major bottom:

1. MVRV Z-Score at -0.8
2. NUPL negative for 45 days
3. Long-term holders accumulating
4. Miner capitulation complete
5. Exchange outflows at ATH

Each indicator explained below 👇''',
                'views': 890000,
                'likes': 28000,
                'retweets': 12000,
                'category': 'crypto'
            },
            {
                'author': 'Balaji',
                'handle': '@balajis',
                'content': '''The Network State is the sequel to The Sovereign Individual.

While the book predicted the shift from centralized to decentralized,
it didn't predict that countries themselves would become decentralized.

Here's what that means for the next decade...''',
                'views': 1200000,
                'likes': 34000,
                'retweets': 8900,
                'category': 'tech'
            },
            {
                'author': 'Elon Musk',
                'handle': '@elonmusk',
                'content': '''Starlink eliminates dead zones and keeps you connected on the go.

It's not just about speed. It's about reliability anywhere on Earth.

This changes everything for remote work, emergency response, and global connectivity.''',
                'views': 8500000,
                'likes': 280000,
                'retweets': 45000,
                'category': 'tech'
            },
            {
                'author': 'Howard Marks',
                'handle': '@howardmarksbook',
                'content': '''The most important thing is understanding market cycles.

Right now:
- Valuations are extended
- Risk appetite is high
- FOMO is pervasive

This doesn't mean sell everything. It means be cautious.

History shows the best returns come from buying when others are fearful.''',
                'views': 450000,
                'likes': 18000,
                'retweets': 5200,
                'category': 'finance'
            }
        ]
        
        for data in mock_data:
            engagement_rate = (data['likes'] + data['retweets']) / data['views']
            
            post = XPost(
                post_id=f"mock_{hash(data['content']) % 10000}",
                author=data['author'],
                author_handle=data['handle'],
                content=data['content'],
                created_at=datetime.now() - timedelta(days=hash(data['author']) % days_back),
                views=data['views'],
                likes=data['likes'],
                retweets=data['retweets'],
                replies=int(data['likes'] * 0.1),
                bookmarks=int(data['likes'] * 0.15),
                category=data['category'],
                hashtags=self._extract_hashtags(data['content']),
                engagement_rate=engagement_rate,
                is_viral=self._is_viral(data, engagement_rate)
            )
            posts.append(post)
        
        return posts
    
    def _extract_hashtags(self, content: str) -> List[str]:
        """提取话题标签"""
        # 匹配中英文话题标签
        hashtags = re.findall(r'#\w+', content)
        return [h.lower() for h in hashtags]
    
    def _is_viral(self, data: Dict, engagement_rate: float) -> bool:
        """判断是否爆款"""
        return (
            data['views'] >= self.viral_threshold['views'] or
            data['likes'] >= self.viral_threshold['likes'] or
            engagement_rate >= self.viral_threshold['engagement_rate']
        )
    
    def analyze_viral_patterns(self, posts: List[XPost]) -> Dict:
        """分析爆款帖子共性"""
        
        # 按类别分组分析
        categories = {}
        for post in posts:
            cat = post.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(post)
        
        patterns = {}
        for cat, cat_posts in categories.items():
            patterns[cat] = {
                'count': len(cat_posts),
                'avg_views': sum(p.views for p in cat_posts) // len(cat_posts),
                'avg_engagement': sum(p.engagement_rate for p in cat_posts) / len(cat_posts),
                'common_patterns': self._extract_common_patterns(cat_posts)
            }
        
        return patterns
    
    def _extract_common_patterns(self, posts: List[XPost]) -> Dict:
        """提取共同模式"""
        
        # 标题/开头分析
        hooks = []
        structures = []
        lengths = []
        
        for post in posts:
            content = post.content
            
            # 分析开头
            first_line = content.split('\n')[0]
            hooks.append(first_line)
            
            # 检测结构
            if '🧵' in content or 'thread' in content.lower():
                structures.append('thread')
            elif re.search(r'\d+\.', content):
                structures.append('listicle')
            elif '?' in first_line:
                structures.append('question')
            else:
                structures.append('statement')
            
            # 长度
            lengths.append(len(content))
        
        return {
            'common_hooks': self._find_common_patterns(hooks),
            'structure_distribution': self._count_distribution(structures),
            'avg_length': sum(lengths) // len(lengths),
            'length_range': f"{min(lengths)}-{max(lengths)}"
        }
    
    def _find_common_patterns(self, items: List[str]) -> List[str]:
        """找出共同模式"""
        # 简化的模式识别
        patterns = []
        
        # 检查数字开头
        number_starts = sum(1 for item in items if re.match(r'^\d', item))
        if number_starts >= len(items) * 0.3:
            patterns.append(f"{number_starts}/{len(items)} 以数字开头")
        
        # 检查提问
        questions = sum(1 for item in items if '?' in item or '？' in item)
        if questions >= len(items) * 0.3:
            patterns.append(f"{questions}/{len(items)} 使用提问")
        
        return patterns
    
    def _count_distribution(self, items: List[str]) -> Dict:
        """统计分布"""
        from collections import Counter
        return dict(Counter(items))
    
    def save_to_database(self, posts: List[XPost]):
        """保存到数据库"""
        # 转换为JSON格式
        data = []
        for post in posts:
            data.append({
                'post_id': post.post_id,
                'author': post.author,
                'handle': post.author_handle,
                'content': post.content,
                'created_at': post.created_at.isoformat(),
                'metrics': {
                    'views': post.views,
                    'likes': post.likes,
                    'retweets': post.retweets,
                    'replies': post.replies,
                    'bookmarks': post.bookmarks,
                    'engagement_rate': post.engagement_rate
                },
                'category': post.category,
                'hashtags': post.hashtags,
                'is_viral': post.is_viral
            })
        
        # 保存到文件
        output_file = f"/root/.openclaw/workspace/content_analyzer/data/x_posts_{datetime.now().strftime('%Y%m%d')}.json"
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已保存 {len(posts)} 条帖子到 {output_file}")

# 测试
if __name__ == '__main__':
    collector = XDataCollector()
    
    print("="*70)
    print("🕷️ X平台数据采集器")
    print("="*70)
    
    # 采集爆款帖子
    posts = collector.collect_posts(days_back=7, max_posts=200)
    
    print(f"\n📊 采集结果:")
    print(f"   共采集 {len(posts)} 条爆款帖子")
    
    # 分类统计
    by_category = {}
    for post in posts:
        cat = post.category
        by_category[cat] = by_category.get(cat, 0) + 1
    
    print(f"\n📁 分类分布:")
    for cat, count in by_category.items():
        print(f"   {cat}: {count}条")
    
    # 分析共性
    patterns = collector.analyze_viral_patterns(posts)
    
    print(f"\n🔍 爆款共性分析:")
    for cat, data in patterns.items():
        print(f"\n   【{cat.upper()}】")
        print(f"   样本数: {data['count']}")
        print(f"   平均浏览: {data['avg_views']:,}")
        print(f"   平均互动率: {data['avg_engagement']:.2%}")
        print(f"   共同模式: {', '.join(data['common_patterns']['common_hooks'])}")
        print(f"   结构分布: {data['common_patterns']['structure_distribution']}")
    
    # 保存
    collector.save_to_database(posts)
    
    # 显示示例
    print(f"\n📌 爆款示例:")
    for i, post in enumerate(posts[:3], 1):
        print(f"\n{i}. @{post.author_handle}")
        print(f"   浏览: {post.views:,} | 赞: {post.likes:,} | 互动率: {post.engagement_rate:.2%}")
        print(f"   内容: {post.content[:100]}...")
    
    print("\n" + "="*70)
