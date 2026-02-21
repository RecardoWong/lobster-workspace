#!/usr/bin/env python3
"""
Dashboard v4.2 HTML 更新脚本
读取 JSON 数据并嵌入到 index.html
"""
import json
import re
from datetime import datetime
from pathlib import Path

DASHBOARD_DIR = "/root/.openclaw/workspace/lobster-workspace/dashboard"

def load_json(filename):
    """加载 JSON 文件"""
    filepath = Path(DASHBOARD_DIR) / "data" / filename
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 {filename} 失败: {e}")
        return None

def generate_tweet_html(tweets_data, limit=5):
    """生成推文 HTML"""
    if not tweets_data or 'tweets' not in tweets_data:
        return "<p style='color: #6b7280; text-align: center;'>暂无数据</p>"
    
    all_tweets = []
    for author, tweets in tweets_data['tweets'].items():
        for tweet in tweets[:2]:  # 每个作者取前2条
            all_tweets.append({
                'author': tweet.get('name', author),
                'handle': tweet.get('author', author),
                'text': tweet.get('text', ''),
                'translate': tweet.get('translate', ''),
                'time': tweet.get('time_ago', '刚刚'),
                'url': tweet.get('url', '#')
            })
    
    # 按时间排序并限制数量
    all_tweets = all_tweets[:limit]
    
    html_parts = []
    for i, tweet in enumerate(all_tweets, 1):
        # 截断过长的文本
        text = tweet['text'][:150] + '...' if len(tweet['text']) > 150 else tweet['text']
        translate = tweet['translate'][:150] + '...' if len(tweet['translate']) > 150 else tweet['translate']
        
        # 处理时间显示
        time_color = '#ef4444' if tweet['time'] in ['刚刚', '1小时前', '2小时前'] else '#9ca3af'
        
        html_parts.append(f'''<div class="tweet-item">
                        <div class="tweet-author">
                            <span style="background: #3b82f6; color: white; font-size: 10px; padding: 2px 6px; border-radius: 4px;">#{i}</span>
                            <span style="font-weight: 600;">{tweet['author']}</span>
                            <span style="color: #6b7280;">@{tweet['handle']}</span>
                            <span style="margin-left: auto; color: {time_color}; font-size: 11px;">{tweet['time']}</span>
                        </div>
                        <div class="tweet-text">{text}</div>
                        <div class="tweet-translate">[中文翻译] {translate}</div>
                    </div>''')
    
    return '\n'.join(html_parts)

def generate_news_html(news_data, limit=5):
    """生成新闻 HTML"""
    if not news_data or 'news' not in news_data:
        return "<p style='color: #6b7280; text-align: center;'>暂无数据</p>"
    
    tag_colors = {
        '数据中心': ('#8b5cf6', '#8b5cf615'),
        '全球': ('#10b981', '#10b98115'),
        '财经': ('#ef4444', '#ef444415'),
        'AI数据中心': ('#8b5cf6', '#8b5cf610'),
        'GaN需求': ('#ec4899', '#ec489905'),
        'GaN龙头': ('#f59e0b', '#f59e0b05'),
        '政策利好': ('#10b981', '#10b98105'),
        '上游供应': ('#3b82f6', '#3b82f605'),
    }
    
    html_parts = []
    for news in news_data['news'][:limit]:
        tag = news.get('tag', '财经')
        title = news.get('title', '')
        time = news.get('time', '刚刚')
        source = news.get('source', '行业动态')
        
        text_color, bg_color = tag_colors.get(tag, ('#6b7280', '#f3f4f6'))
        
        html_parts.append(f'''<div class="news-item" style="background: linear-gradient(135deg, {bg_color}, {bg_color.replace('15', '05').replace('10', '05')})); border-color: {text_color};">
                        <div class="news-header">
                            <span class="news-tag" style="color: {text_color}; background: {bg_color};">{tag}</span>
                            <span style="font-size: 11px; color: #9ca3af;">{time}</span>
                        </div>
                        <div class="news-title">{title}</div>
                        <div class="news-source">来源: {source}</div>
                    </div>''')
    
    return '\n'.join(html_parts)

def update_html():
    """更新 HTML 文件"""
    index_path = Path(DASHBOARD_DIR) / "index.html"
    
    # 读取当前 HTML
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 加载数据
    tweets_data = load_json('twitter_translated.json')
    news_data = load_json('finance_news.json')
    
    # 生成新的卡片内容
    tweets_html = generate_tweet_html(tweets_data)
    news_html = generate_news_html(news_data)
    
    # 更新 Twitter 卡片
    twitter_pattern = r'(<!-- 第二栏：Twitter -->.*?<div class="card-body">)(.*?)(</div>\s*<a href="tweets.html")'
    twitter_replacement = r'\1\n' + tweets_html + r'\n\3'
    html = re.sub(twitter_pattern, twitter_replacement, html, flags=re.DOTALL)
    
    # 更新财经要报卡片
    news_pattern = r'(<!-- 第三栏：财经要报 -->.*?<div class="card-body">)(.*?)(</div>\s*</div>\s*</div>\s*</main>)'
    news_replacement = r'\1\n' + news_html + r'\n\3'
    html = re.sub(news_pattern, news_replacement, html, flags=re.DOTALL)
    
    # 更新时间戳
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    html = re.sub(r'更新于: \d{4}-\d{2}-\d{2} \d{2}:\d{2}', f'更新于: {now}', html)
    
    # 写回文件
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Dashboard 已更新: {now}")
    print(f"   - Twitter 推文: {len(tweets_data.get('tweets', {})) if tweets_data else 0} 位作者")
    print(f"   - 财经新闻: {len(news_data.get('news', [])) if news_data else 0} 条")

if __name__ == '__main__':
    update_html()
