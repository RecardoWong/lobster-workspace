#!/usr/bin/env python3
"""
Twitter 每日复盘
读取前一天记录的推文，生成复盘报告
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path

LOG_DIR = '/root/.openclaw/workspace/memory/twitter_logs'

def parse_daily_log(date_str):
    """解析某一天的Markdown日志"""
    log_file = f"{LOG_DIR}/{date_str}.md"
    
    if not os.path.exists(log_file):
        return None
    
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析推文
    tweets = []
    tweet_blocks = re.split(r'### ', content)[1:]  # 跳过第一个空块
    
    for block in tweet_blocks:
        lines = block.strip().split('\n')
        if not lines:
            continue
        
        # 第一行是作者名
        author_line = lines[0].strip()
        match = re.match(r'(.+?) \(@(.+?)\)', author_line)
        if match:
            name = match.group(1)
            author = match.group(2)
        else:
            name = author_line
            author = 'unknown'
        
        # 提取其他信息
        tweet = {'name': name, 'author': author}
        for line in lines[1:]:
            if line.startswith('- 时间:'):
                tweet['time_info'] = line.replace('- 时间:', '').strip()
            elif line.startswith('- 原文:'):
                tweet['text'] = line.replace('- 原文:', '').strip()
            elif line.startswith('- 翻译:'):
                tweet['translate'] = line.replace('- 翻译:', '').strip()
            elif line.startswith('- 链接:'):
                tweet['url'] = line.replace('- 链接:', '').strip()
        
        tweets.append(tweet)
    
    return tweets

def analyze_tweets(tweets):
    """分析推文内容，提取关键信息"""
    if not tweets:
        return None
    
    # 按作者分组
    by_author = {}
    for t in tweets:
        author = t.get('author', 'unknown')
        if author not in by_author:
            by_author[author] = []
        by_author[author].append(t)
    
    # 提取关键词/主题
    all_text = ' '.join([t.get('text', '') + ' ' + t.get('translate', '') for t in tweets])
    
    # 简单的主题识别
    themes = []
    keywords = {
        'AI/科技': ['AI', 'Grok', 'OpenAI', '人工智能', '科技'],
        '股票/投资': ['stock', 'earnings', '财报', '股票', '看涨', '期权'],
        '加密货币': ['crypto', 'bitcoin', 'BTC', '加密货币', '交易所'],
        '地缘政治': ['war', 'war', '打仗', '国防', '军事'],
        '宏观/经济': ['fed', 'rate', '利率', '经济', '通胀']
    }
    
    for theme, words in keywords.items():
        if any(word.lower() in all_text.lower() for word in words):
            themes.append(theme)
    
    return {
        'by_author': by_author,
        'themes': themes,
        'total': len(tweets)
    }

def generate_report(date_str, analysis):
    """生成复盘报告"""
    if not analysis:
        return f"📅 {date_str} 没有推文记录"
    
    by_author = analysis['by_author']
    themes = analysis['themes']
    total = analysis['total']
    
    lines = [
        f"📊 Twitter 每日复盘 ({date_str})",
        f"📈 总计: {total} 条推文",
        f"🏷️ 主题: {', '.join(themes) if themes else '无明确主题'}",
        "=" * 40,
        ""
    ]
    
    # 各作者总结
    for author, tweets in by_author.items():
        name = tweets[0].get('name', author)
        lines.extend([
            f"👤 {name} (@{author}) - {len(tweets)}条",
            ""
        ])
        
        # 提取关键推文（前3条）
        for i, t in enumerate(tweets[:3], 1):
            text = t.get('text', '')[:80]
            translate = t.get('translate', '')[:60]
            lines.append(f"  {i}. {text}...")
            if translate and translate != text:
                lines.append(f"     📝 {translate}...")
        
        lines.append("")
    
    # 市场信号总结
    lines.extend([
        "🔍 市场信号:",
        ""
    ])
    
    # 根据主题生成信号
    if '地缘政治' in themes:
        lines.append("  ⚠️ 地缘政治风险提及 - 关注国防股、能源股")
    if '股票/投资' in themes:
        lines.append("  📈 投资讨论活跃 - 关注提及个股")
    if 'AI/科技' in themes:
        lines.append("  🤖 AI话题热度高 - 关注科技股")
    if '加密货币' in themes:
        lines.append("  ₿ 加密市场讨论 - 关注相关资产")
    
    if not themes:
        lines.append("  ℹ️ 今日讨论较分散，无集中主题")
    
    # 操作建议
    lines.extend([
        "",
        "💡 操作建议:",
        ""
    ])
    
    if total > 20:
        lines.append("  • 推文旅密度高，可能有重要事件，建议关注市场开盘")
    elif total > 10:
        lines.append("  • 讨论热度中等，保持常规关注")
    else:
        lines.append("  • 讨论较少，市场可能相对平静")
    
    if '地缘政治' in themes:
        lines.append("  • 建议关注VIX波动率指数和黄金走势")
    if 'AI/科技' in themes:
        lines.append("  • 建议关注NVDA、AI相关板块")
    
    lines.extend([
        "",
        "=" * 40,
        f"📅 复盘时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    ])
    
    return "\n".join(lines)

def save_and_notify(report, date_str):
    """保存报告并发送通知"""
    # 保存到文件
    report_file = f'/root/.openclaw/workspace/memory/twitter_review_{date_str}.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# Twitter 每日复盘 - {date_str}\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC\n\n")
        f.write("---\n\n")
        f.write(report)
    
    print(f"[{datetime.now().strftime('%H:%M')}] 报告已保存: {report_file}")
    return report_file

def main():
    # 获取昨天日期
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"[{datetime.now().strftime('%H:%M')}] 生成 {yesterday} 的Twitter复盘...")
    
    # 解析日志
    tweets = parse_daily_log(yesterday)
    
    if tweets:
        # 分析
        analysis = analyze_tweets(tweets)
        # 生成报告
        report = generate_report(yesterday, analysis)
        print(report)
        
        # 保存报告
        save_and_notify(report, yesterday)
    else:
        print(f"⚠️ {yesterday} 没有找到推文记录")

if __name__ == '__main__':
    main()
