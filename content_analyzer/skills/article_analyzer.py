#!/usr/bin/env python3
"""
Skill 2: 文章结构解析器
分析开头钩子、段落节奏、论证逻辑、结尾设计
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class HookType(Enum):
    STORY = "故事钩子"        # 个人经历开场
    DATA = "数据钩子"         # 惊人数字开场
    QUOTE = "金句钩子"        # 名言/金句开场
    PAIN = "痛点钩子"         # 直击痛点开场
    QUESTION = "提问钩子"     # 提问开场
    CONTRAST = "对比钩子"     # 反差对比开场

class BodyStructure(Enum):
    PROBLEM_SOLUTION = "问题-解决式"
    LISTICLE = "清单式"
    STORY_ARC = "故事弧线式"
    COMPARISON = "对比分析式"
    PROGRESSION = "递进论证式"

class EndingType(Enum):
    CTA = "CTA式"            # 行动号召
    QUESTION = "提问式"       # 开放式问题
    SUMMARY = "总结式"        # 升华总结
    EMOTION = "情绪式"        # 情绪共鸣
    CLIFFHANGER = "悬念式"    # 预告下期

@dataclass
class ArticleStructure:
    # 整体信息
    word_count: int
    paragraph_count: int
    
    # 开头分析
    hook_type: HookType
    hook_text: str
    hook_effectiveness: int  # 0-100
    
    # 正文分析
    body_structure: BodyStructure
    sections: List[Dict]  # 各段落分析
    rhythm_score: int  # 节奏感 0-100
    
    # 结尾分析
    ending_type: EndingType
    ending_text: str
    ending_effectiveness: int  # 0-100
    
    # 整体评分
    structure_score: int  # 结构完整度 0-100
    readability_score: int  # 可读性 0-100
    shareability_score: int  # 传播性 0-100
    
    # 亮点和槽点
    highlights: List[str]
    weaknesses: List[str]
    
    # 可复用框架
    reusable_framework: str

class ArticleAnalyzer:
    """文章结构解析器"""
    
    def __init__(self):
        # 钩子关键词
        self.hook_patterns = {
            HookType.STORY: ['我', '那年', '记得', '曾经', '有一次', '那时候'],
            HookType.DATA: ['%', '万', '亿', '数据统计', '研究表明', '报告显示'],
            HookType.QUOTE: ['"', '「', '有人说', '某位', '名言', '经典'],
            HookType.PAIN: ['痛苦', '焦虑', '迷茫', '困境', '难题', '困扰着'],
            HookType.QUESTION: ['？', '你有没有', '为什么', '是什么', '怎么办'],
            HookType.CONTRAST: ['但是', '然而', '却', '相反', '对比', '差距']
        }
        
        # 结尾关键词
        self.ending_patterns = {
            EndingType.CTA: ['关注', '转发', '评论', '点赞', '行动', '试试', '开始'],
            EndingType.QUESTION: ['？', '你怎么看', '欢迎讨论', '你的想法', '留言'],
            EndingType.SUMMARY: ['总结', '总之', '综上所述', '最后', '一句话'],
            EndingType.EMOTION: ['希望', '相信', '一起', '未来', '加油', '共勉'],
            EndingType.CLIFFHANGER: ['下期', '下次', '后续', '预告', '敬请期待']
        }
    
    def analyze(self, article: str) -> ArticleStructure:
        """分析文章结构"""
        paragraphs = [p.strip() for p in article.split('\n') if p.strip()]
        
        if len(paragraphs) < 3:
            return self._create_error_structure("文章太短，无法分析")
        
        # 1. 分析开头
        hook_type, hook_text, hook_score = self._analyze_hook(paragraphs)
        
        # 2. 分析正文
        body_structure, sections, rhythm = self._analyze_body(paragraphs)
        
        # 3. 分析结尾
        ending_type, ending_text, ending_score = self._analyze_ending(paragraphs)
        
        # 4. 整体评分
        structure_score = self._score_structure(hook_score, ending_score, len(sections))
        readability = self._score_readability(article, paragraphs)
        shareability = self._score_shareability(hook_score, ending_score, body_structure)
        
        # 5. 提取亮点和槽点
        highlights, weaknesses = self._extract_highlights_weaknesses(
            hook_type, hook_score, body_structure, ending_type, ending_score, rhythm
        )
        
        # 6. 生成可复用框架
        framework = self._generate_framework(hook_type, body_structure, ending_type)
        
        return ArticleStructure(
            word_count=len(article),
            paragraph_count=len(paragraphs),
            hook_type=hook_type,
            hook_text=hook_text[:100] + "..." if len(hook_text) > 100 else hook_text,
            hook_effectiveness=hook_score,
            body_structure=body_structure,
            sections=sections,
            rhythm_score=rhythm,
            ending_type=ending_type,
            ending_text=ending_text[:100] + "..." if len(ending_text) > 100 else ending_text,
            ending_effectiveness=ending_score,
            structure_score=structure_score,
            readability_score=readability,
            shareability_score=shareability,
            highlights=highlights,
            weaknesses=weaknesses,
            reusable_framework=framework
        )
    
    def _analyze_hook(self, paragraphs: List[str]) -> Tuple[HookType, str, int]:
        """分析开头钩子"""
        if not paragraphs:
            return HookType.STORY, "", 30
        
        first_para = paragraphs[0]
        scores = {}
        
        for hook_type, patterns in self.hook_patterns.items():
            score = sum(2 for p in patterns if p in first_para)
            if score > 0:
                scores[hook_type] = score
        
        if not scores:
            # 默认故事钩子
            return HookType.STORY, first_para, 50
        
        best_type = max(scores, key=scores.get)
        effectiveness = min(50 + scores[best_type] * 10, 95)
        
        return best_type, first_para, effectiveness
    
    def _analyze_body(self, paragraphs: List[str]) -> Tuple[BodyStructure, List[Dict], int]:
        """分析正文结构"""
        if len(paragraphs) <= 2:
            return BodyStructure.PROGRESSION, [], 50
        
        body_paras = paragraphs[1:-1]  # 去掉开头结尾
        
        # 检测结构类型
        structure = self._detect_structure(body_paras)
        
        # 分析各段落
        sections = []
        for i, para in enumerate(body_paras):
            section = {
                'index': i + 1,
                'word_count': len(para),
                'has_number': bool(re.search(r'\d+', para)),
                'has_quote': '"' in para or '「' in para,
                'is_short': len(para) < 100
            }
            sections.append(section)
        
        # 节奏评分
        rhythm = self._calculate_rhythm(sections)
        
        return structure, sections, rhythm
    
    def _detect_structure(self, paragraphs: List[str]) -> BodyStructure:
        """检测正文结构"""
        # 清单式检测
        list_markers = sum(1 for p in paragraphs if re.match(r'^\d+[、.．]', p) or p.startswith('第'))
        if list_markers >= len(paragraphs) * 0.5:
            return BodyStructure.LISTICLE
        
        # 对比式检测
        contrast_markers = sum(1 for p in paragraphs if any(w in p for w in ['对比', '差距', '区别', 'vs', 'PK']))
        if contrast_markers >= 2:
            return BodyStructure.COMPARISON
        
        # 故事式检测
        story_markers = sum(1 for p in paragraphs if any(w in p for w in ['后来', '结果', '最终', '结局', '总结']))
        if story_markers >= 2:
            return BodyStructure.STORY_ARC
        
        # 问题解决式
        problem_markers = sum(1 for p in paragraphs if any(w in p for w in ['问题', '困难', '怎么办', '解决', '方法']))
        if problem_markers >= 2:
            return BodyStructure.PROBLEM_SOLUTION
        
        return BodyStructure.PROGRESSION
    
    def _calculate_rhythm(self, sections: List[Dict]) -> int:
        """计算节奏感"""
        if not sections:
            return 50
        
        score = 50
        
        # 长短交替
        lengths = [s['word_count'] for s in sections]
        if len(lengths) >= 2:
            variations = sum(1 for i in range(len(lengths)-1) if abs(lengths[i] - lengths[i+1]) > 50)
            score += variations * 5
        
        # 有数据支撑
        data_sections = sum(1 for s in sections if s['has_number'])
        score += data_sections * 5
        
        # 有金句
        quote_sections = sum(1 for s in sections if s['has_quote'])
        score += quote_sections * 5
        
        return min(score, 95)
    
    def _analyze_ending(self, paragraphs: List[str]) -> Tuple[EndingType, str, int]:
        """分析结尾"""
        if len(paragraphs) < 2:
            return EndingType.SUMMARY, "", 50
        
        last_para = paragraphs[-1]
        scores = {}
        
        for ending_type, patterns in self.ending_patterns.items():
            score = sum(2 for p in patterns if p in last_para)
            if score > 0:
                scores[ending_type] = score
        
        if not scores:
            return EndingType.SUMMARY, last_para, 55
        
        best_type = max(scores, key=scores.get)
        effectiveness = min(55 + scores[best_type] * 10, 95)
        
        return best_type, last_para, effectiveness
    
    def _score_structure(self, hook_score: int, ending_score: int, section_count: int) -> int:
        """评分结构完整度"""
        base = (hook_score + ending_score) / 2
        section_bonus = min(section_count * 3, 15)
        return int(base + section_bonus)
    
    def _score_readability(self, article: str, paragraphs: List[str]) -> int:
        """评分可读性"""
        score = 60
        
        # 段落数合适
        if 5 <= len(paragraphs) <= 15:
            score += 10
        
        # 平均段落长度
        avg_len = len(article) / len(paragraphs) if paragraphs else 200
        if 100 <= avg_len <= 300:
            score += 10
        
        # 有标点分隔
        if '。' in article or '！' in article:
            score += 5
        
        return min(score, 95)
    
    def _score_shareability(self, hook_score: int, ending_score: int, structure: BodyStructure) -> int:
        """评分传播性"""
        base = (hook_score + ending_score) / 2
        
        # 清单式和故事式更易传播
        if structure in [BodyStructure.LISTICLE, BodyStructure.STORY_ARC]:
            base += 10
        
        return int(min(base, 95))
    
    def _extract_highlights_weaknesses(self, hook_type, hook_score, structure, 
                                       ending_type, ending_score, rhythm) -> Tuple[List[str], List[str]]:
        """提取亮点和槽点"""
        highlights = []
        weaknesses = []
        
        if hook_score >= 70:
            highlights.append(f"开头钩子强: {hook_type.value}")
        elif hook_score < 60:
            weaknesses.append("开头平淡，建议优化钩子")
        
        if structure == BodyStructure.LISTICLE:
            highlights.append("清单式结构清晰，易读易传播")
        
        if rhythm >= 70:
            highlights.append("文章节奏感好，长短段落搭配合理")
        
        if ending_score >= 70:
            highlights.append(f"结尾设计好: {ending_type.value}")
        elif ending_score < 60:
            weaknesses.append("结尾力度不足，建议优化CTA")
        
        return highlights, weaknesses
    
    def _generate_framework(self, hook: HookType, body: BodyStructure, ending: EndingType) -> str:
        """生成可复用框架"""
        frameworks = {
            (HookType.STORY, BodyStructure.PROGRESSION, EndingType.EMOTION): 
                "故事开场 → 递进论证 → 情绪共鸣结尾",
            (HookType.DATA, BodyStructure.LISTICLE, EndingType.CTA): 
                "数据钩子 → 清单式论证 → 行动号召结尾",
            (HookType.PAIN, BodyStructure.PROBLEM_SOLUTION, EndingType.CTA): 
                "痛点开场 → 问题-解决 → CTA结尾",
            (HookType.QUESTION, BodyStructure.COMPARISON, EndingType.QUESTION): 
                "提问开场 → 对比分析 → 开放式问题结尾"
        }
        
        return frameworks.get((hook, body, ending), "标准结构: 钩子 → 论证 → 结尾")

# 测试
if __name__ == '__main__':
    analyzer = ArticleAnalyzer()
    
    # 测试文章
    test_article = """我曾在凌晨3点盯着账户里亏损的100万，彻夜难眠。

那是2021年，我把全部积蓄投入了所谓的"稳赚不赔"的项目。结果不到半年，100万变成了20万。

今天我想分享这3年血亏换来的5条投资铁律，希望帮你避开我踩过的坑。

第一，永远不要把鸡蛋放在一个篮子里。我当时80%的资金都投了一个项目，这是最大的错误。

第二，不懂的东西千万不要碰。 crypto、期权、外汇...这些我不懂的东西，亏得最惨。

第三，情绪是投资最大的敌人。恐慌时割肉，贪婪时追高，这是人性，但必须克服。

第四，时间是你的朋友。频繁交易不仅亏手续费，更容易做出错误决策。

第五，永远留有现金。满仓操作看似能赚更多，但遇到机会时只能眼睁睁看着。

投资是一场马拉松，不是百米冲刺。希望这5条铁律能帮你在投资路上少走些弯路。

你有哪些投资教训？欢迎在评论区分享。"""
    
    print("="*70)
    print("📄 文章结构解析器")
    print("="*70)
    
    result = analyzer.analyze(test_article)
    
    print(f"\n📊 基础信息")
    print(f"   字数: {result.word_count}  段落: {result.paragraph_count}")
    
    print(f"\n🪝 开头分析")
    print(f"   类型: {result.hook_type.value}")
    print(f"   效果: {result.hook_effectiveness}/100")
    print(f"   原文: {result.hook_text}")
    
    print(f"\n📖 正文结构")
    print(f"   类型: {result.body_structure.value}")
    print(f"   段落数: {len(result.sections)}")
    print(f"   节奏感: {result.rhythm_score}/100")
    
    print(f"\n🔚 结尾分析")
    print(f"   类型: {result.ending_type.value}")
    print(f"   效果: {result.ending_effectiveness}/100")
    
    print(f"\n📈 整体评分")
    print(f"   结构完整度: {result.structure_score}/100")
    print(f"   可读性: {result.readability_score}/100")
    print(f"   传播性: {result.shareability_score}/100")
    
    print(f"\n✨ 可复用框架")
    print(f"   {result.reusable_framework}")
    
    if result.highlights:
        print(f"\n👍 亮点")
        for h in result.highlights:
            print(f"   • {h}")
    
    if result.weaknesses:
        print(f"\n👎 改进点")
        for w in result.weaknesses:
            print(f"   • {w}")
    
    print("\n" + "="*70)
