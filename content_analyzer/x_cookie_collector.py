#!/usr/bin/env python3
"""
X平台数据采集器 - Cookie版本
使用用户提供的Twitter Cookie访问
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class XPost:
    """X平台帖子数据结构"""
    post_id: str
    author: str
    author_handle: str
    content: str
    created_at: datetime
    views: int
    likes: int
    retweets: int
    replies: int
    category: str
    is_viral: bool

class XCookieCollector:
    """使用Cookie采集X平台数据"""
    
    def __init__(self, cookie_str: Optional[str] = None):
        self.cookie_str = cookie_str
        self.session = None
        
    def load_cookies_from_file(self, filepath: str = ".twitter_cookies.json"):
        """从文件加载cookies"""
        try:
            with open(filepath, 'r') as f:
                cookies = json.load(f)
                # 转换为requests可用的格式
                self.cookie_str = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
                print(f"✅ 已加载 {len(cookies)} 个cookies")
                return True
        except Exception as e:
            print(f"❌ 加载cookies失败: {e}")
            return False
    
    def collect_timeline(self, max_posts: int = 100) -> List[XPost]:
        """
        采集用户时间线
        
        方案: 使用Playwright + Cookie访问
        1. 启动浏览器
        2. 注入cookie
        3. 访问twitter.com/home
        4. 滚动加载帖子
        5. 解析并保存
        """
        # TODO: 实现Playwright版本
        # 需要用户的cookie才能实际运行
        
        print("📝 使用Cookie访问X平台时间线")
        print(f"   Cookie长度: {len(self.cookie_str) if self.cookie_str else 0} 字符")
        print("   正在采集...")
        
        # 这里应该使用Playwright实现
        # 暂时返回模拟数据
        return self._mock_collect()
    
    def collect_by_hashtag(self, hashtag: str, max_posts: int = 50) -> List[XPost]:
        """按话题标签采集"""
        # 访问 https://twitter.com/search?q=%23{hashtag}
        pass
    
    def collect_user_posts(self, username: str, max_posts: int = 50) -> List[XPost]:
        """采集特定用户的帖子"""
        # 访问 https://twitter.com/{username}
        pass
    
    def _mock_collect(self) -> List[XPost]:
        """模拟采集 (实际实现时删除)"""
        # 等待用户提供了真实cookie后实现
        print("⏳ 等待真实cookie...")
        print("   请提供cookies文件路径或cookie字符串")
        return []
    
    def analyze_viral_posts(self, posts: List[XPost]) -> Dict:
        """分析爆款帖子"""
        if not posts:
            return {}
        
        # 筛选爆款 (互动率>5% 或 点赞>1000)
        viral = [p for p in posts if (p.likes / p.views > 0.05 if p.views > 0 else False) or p.likes > 1000]
        
        return {
            'total': len(posts),
            'viral_count': len(viral),
            'viral_rate': len(viral) / len(posts) * 100 if posts else 0,
            'avg_likes': sum(p.likes for p in posts) // len(posts) if posts else 0,
            'top_post': max(posts, key=lambda x: x.likes) if posts else None
        }

# Cookie导出教程
def print_cookie_guide():
    """打印Cookie导出教程"""
    guide = """
🔐 如何导出Twitter/X Cookie

方法1: 浏览器插件 (推荐)
1. 安装 "EditThisCookie" 或 "Cookie-Editor" 浏览器插件
2. 登录 twitter.com
3. 点击插件图标
4. 选择 "导出" → "JSON格式"
5. 保存为 twitter_cookies.json
6. 把文件发给我

方法2: 开发者工具
1. 登录 twitter.com
2. 按 F12 打开开发者工具
3. 切换到 Application/应用 标签
4. 左侧选择 Cookies → https://twitter.com
5. 右键 → Copy all → 粘贴给我

⚠️ 安全提醒:
- Cookie包含登录凭证，请通过安全渠道发送
- 不要截图发在公开场合
- 我可以随时帮你撤销这些Cookie

导出后放在: /root/.openclaw/workspace/content_analyzer/.twitter_cookies.json
"""
    print(guide)

if __name__ == '__main__':
    print("="*70)
    print("🕷️ X平台数据采集器 - Cookie版本")
    print("="*70)
    print()
    
    # 检查是否有cookie文件
    import os
    cookie_file = "/root/.openclaw/workspace/content_analyzer/.twitter_cookies.json"
    
    if os.path.exists(cookie_file):
        print(f"✅ 发现Cookie文件: {cookie_file}")
        collector = XCookieCollector()
        if collector.load_cookies_from_file(cookie_file):
            posts = collector.collect_timeline()
            print(f"\n📊 采集到 {len(posts)} 条帖子")
    else:
        print("❌ 未发现Cookie文件")
        print()
        print_cookie_guide()
    
    print("="*70)
