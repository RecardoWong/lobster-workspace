#!/usr/bin/env python3
"""
爆款内容生成器
应用爆款公式，自动生成文章
"""

import random
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ContentBrief:
    """内容需求简报"""
    topic: str           # 主题
    target_audience: str # 目标受众
    key_message: str     # 核心观点
    tone: str           # 语气风格
    content_type: str   # 类型：观点/教程/故事

class ContentGenerator:
    """内容生成器"""
    
    def __init__(self):
        self.title_templates = {
            '数字冲击': [
                "{loss}后，我悟到了{number}个{topic}真相",
                "{time}亏掉{amount}后，我总结出的{number}条{topic}铁律",
                "连续{duration}，我发现了{number}个{topic}秘密"
            ],
            '反常识': [
                "{common_belief}已死，{new_trend}永生",
                "别再{common_action}了，这才是{topic}的真相",
                "{percentage}的{advice}都是错的，包括这条"
            ],
            '价值承诺': [
                "帮你节省{benefit}，不用{traditional_way}",
                "让你{outcome}，不用{difficulty}",
                "帮你找到{target}，不用{complexity}"
            ],
            '身份反差': [
                "{expert}私下告诉我：{audience}永远别碰这{number}类{topic}",
                "{unexpected_identity}，教我的{number}个{topic}真相",
                "{prestigious_background}，为什么劝你别{common_action}"
            ]
        }
        
        self.hook_templates = {
            '具体事件': [
                "{time}，我{action}。",
                "{date}，我的{subject}里{change}。",
                "{time_of_day}，我终于{action}。"
            ],
            '极端对比': [
                "如果你继续{current_action}，{time}后你大概还是{current_state}。但如果从今天开始{new_action}，{short_time}后你可能会{future_state}。",
                "大部分人都在{common_choice}，但{percentage}的人发现{alternative}才是真正的答案。"
            ],
            '先破后立': [
                "关于{topic}，市场上主要有{number}种说法：{view1}，{view2}，还有人觉得是{view3}。但在我看来，以上都不对。真相其实是...",
                "你可能听过{common_explanation}，但它们都忽略了一个关键点..."
            ]
        }
        
        self.body_templates = {
            '清单式': """今天分享这{number}条{topic}：

1. {point1}
(故事：{story1})

2. {point2}
(数据：{data2})

3. {point3}
(案例：{case3})

4. {point4}
(反面：{negative4})

5. {point5}
(金句：{quote5})""",
            
            '金字塔': """{point}

数据显示，{data}。

{time}，{story}。

如果当时{alternative}，结果可能完全不同。

{quote}"""
        }
        
        self.ending_templates = {
            'CTA': [
                "总之，{summary}。{time}就可以做的一件事：{action}。",
                "改变不需要惊天动地，从{time}开始，{small_action}，坚持{duration}，你会发现{outcome}。"
            ],
            '开放提问': [
                "你有哪些{topic}教训？欢迎在评论区分享，{reward}。下期聊聊：{next_topic}。",
                "如果是你，会怎么选？{option_a} 还是 {option_b}？评论区见。"
            ],
            '情绪共鸣': [
                "我知道这条路很难，因为我也是这样走过来的。但请相信，{encouragement}。我们一起加油。",
                "{topic}这条路，注定是孤独的。但请记住，你不是一个人在战斗。"
            ]
        }
    
    def generate(self, brief: ContentBrief, title_type: str = '数字冲击', 
                 hook_type: str = '具体事件', body_type: str = '清单式',
                 ending_type: str = 'CTA') -> Dict:
        """生成完整文章"""
        
        # 1. 生成标题
        title = self._generate_title(brief, title_type)
        
        # 2. 生成开头
        hook = self._generate_hook(brief, hook_type)
        
        # 3. 生成正文
        body = self._generate_body(brief, body_type)
        
        # 4. 生成结尾
        ending = self._generate_ending(brief, ending_type)
        
        # 5. 组装
        full_article = f"{title}\n\n{hook}\n\n{body}\n\n{ending}"
        
        return {
            'title': title,
            'hook': hook,
            'body': body,
            'ending': ending,
            'full_article': full_article,
            'structure': {
                'title_type': title_type,
                'hook_type': hook_type,
                'body_type': body_type,
                'ending_type': ending_type
            }
        }
    
    def _generate_title(self, brief: ContentBrief, title_type: str) -> str:
        """生成标题"""
        templates = self.title_templates.get(title_type, self.title_templates['数字冲击'])
        template = random.choice(templates)
        
        # 填充变量
        variables = {
            'loss': '资产缩水 70%',
            'number': '5',
            'topic': brief.topic,
            'time': '3年',
            'amount': '100万',
            'duration': '30天凌晨4点起床',
            'common_belief': '互联网',
            'new_trend': 'Agent',
            'common_action': '努力工作',
            'percentage': '90%',
            'advice': '理财建议',
            'benefit': '2万',
            'traditional_way': '上闲鱼买',
            'outcome': '每天多出2小时',
            'difficulty': '早起',
            'target': '10倍股',
            'complexity': '看财报',
            'expert': '基金经理',
            'audience': '散户',
            'unexpected_identity': '月入3万的保洁阿姨',
            'prestigious_background': '985毕业的投行VP'
        }
        
        try:
            return template.format(**variables)
        except:
            return f"关于{brief.topic}的5个真相"
    
    def _generate_hook(self, brief: ContentBrief, hook_type: str) -> str:
        """生成开头钩子"""
        templates = self.hook_templates.get(hook_type, self.hook_templates['具体事件'])
        template = random.choice(templates)
        
        variables = {
            'time': '2025年1月',
            'action': '做了一个决定：裸辞',
            'date': '去年3月15日',
            'subject': '账户',
            'change': '少了50万',
            'time_of_day': '凌晨3点47分',
            'current_action': '按现在的节奏工作',
            'current_state': '那个样子',
            'new_action': '改变1个习惯',
            'short_time': '6个月',
            'future_state': '感谢现在的自己',
            'common_choice': '做A',
            'percentage': '1%',
            'alternative': '发现B',
            'topic': brief.topic,
            'number': '3',
            'view1': 'A说是XXX',
            'view2': 'B认为是YYY',
            'view3': 'ZZZ',
            'common_explanation': '很多说法'
        }
        
        try:
            return template.format(**variables)
        except:
            return f"关于{brief.topic}，我想分享一个故事。"
    
    def _generate_body(self, brief: ContentBrief, body_type: str) -> str:
        """生成正文"""
        if body_type == '清单式':
            return self.body_templates['清单式'].format(
                number='5',
                topic=brief.topic,
                point1='永远不要把鸡蛋放在一个篮子里',
                story1='我当时80%的资金都投了一个项目，结果...',
                point2='不懂的东西千万不要碰',
                data2='数据显示，90%的散户在不懂的领域亏损',
                point3='情绪是投资最大的敌人',
                case3='2022年3月，恐慌中的我差点割肉在最低点',
                point4='时间是你的朋友',
                negative4='如果当时没稳住，现在会少赚50%',
                point5='永远留有现金',
                quote5='满仓是贪婪，空仓是恐惧，半仓才是智慧'
            )
        else:
            return self.body_templates['金字塔'].format(
                point=f"{brief.key_message}",
                data='数据显示，这个观点有90%的正确率',
                time='去年',
                story='我亲身经历了一次验证',
                alternative='没有坚持',
                quote='坚持到最后的人，才能看到希望'
            )
    
    def _generate_ending(self, brief: ContentBrief, ending_type: str) -> str:
        """生成结尾"""
        templates = self.ending_templates.get(ending_type, self.ending_templates['CTA'])
        template = random.choice(templates)
        
        variables = {
            'summary': brief.key_message,
            'time': '今晚',
            'action': '写下你的3个目标',
            'small_action': '早起30分钟',
            'duration': '21天',
            'outcome': '不一样',
            'topic': brief.topic,
            'reward': '点赞最高的3位送我的投资笔记',
            'next_topic': '如何避免黑天鹅事件',
            'option_a': 'A方案',
            'option_b': 'B方案',
            'encouragement': '坚持到最后的人，会看到不一样的风景'
        }
        
        try:
            return template.format(**variables)
        except:
            return f"总之，{brief.key_message}。希望对你有帮助。"

# 测试
if __name__ == '__main__':
    generator = ContentGenerator()
    
    # 创建内容需求
    brief = ContentBrief(
        topic="投资",
        target_audience="散户投资者",
        key_message="投资的核心是控制情绪",
        tone="真诚、有共鸣",
        content_type="观点"
    )
    
    print("="*70)
    print("📝 爆款内容生成器")
    print("="*70)
    
    # 生成不同风格的文章
    combinations = [
        ('数字冲击', '具体事件', '清单式', 'CTA'),
        ('反常识', '先破后立', '金字塔', '开放提问'),
        ('身份反差', '极端对比', '清单式', '情绪共鸣')
    ]
    
    for i, (title_t, hook_t, body_t, ending_t) in enumerate(combinations, 1):
        result = generator.generate(brief, title_t, hook_t, body_t, ending_t)
        
        print(f"\n{'='*70}")
        print(f"📄 文章版本 {i}: {title_t}+{hook_t}+{body_t}+{ending_t}")
        print(f"{'='*70}")
        print(result['full_article'])
    
    print("\n" + "="*70)
