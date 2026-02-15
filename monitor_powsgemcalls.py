#!/usr/bin/env python3
"""
监控 t.me/PowsGemCalls 频道
学习目标：Gem狩猎方法论
推送：新内容即时通知
"""

import os
import re
import json
from datetime import datetime
from typing import List, Dict, Tuple

class PowsGemCallsMonitor:
    """Pow's Gem Calls 频道监控器"""
    
    def __init__(self):
        self.channel_url = "https://t.me/s/PowsGemCalls"
        self.data_file = "/tmp/pows_gem_calls_last.json"
        self.db_file = "/tmp/pows_gem_calls_db.json"
    
    def fetch_latest_posts(self) -> List[Dict]:
        """获取频道最新帖子（通过网页抓取）"""
        import urllib.request
        
        # 尝试多个数据源
        urls_to_try = [
            # 1. 直接抓取 Telegram 公开频道
            ("https://t.me/s/PowsGemCalls", "html"),
            # 2. 备用：使用 r.jina.ai 提取
            ("https://r.jina.ai/http://t.me/s/PowsGemCalls", "text"),
        ]
        
        for url, content_type in urls_to_try:
            try:
                req = urllib.request.Request(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                with urllib.request.urlopen(req, timeout=30) as resp:
                    content = resp.read().decode('utf-8')
                    if content_type == "html":
                        return self._parse_html_posts(content)
                    else:
                        return self._parse_simple(content)
            except Exception as e:
                print(f"Failed to fetch from {url}: {e}")
                continue
        
        return []
    
    def _parse_html_posts(self, html: str) -> List[Dict]:
        """解析HTML提取帖子"""
        posts = []
        
        # Telegram 网页版的消息结构
        # 尝试提取消息内容
        import re
        
        # 查找消息文本
        # Telegram 网页版的消息通常在特定class中
        message_pattern = r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>'
        messages = re.findall(message_pattern, html, re.DOTALL)
        
        for msg_html in messages:
            # 清理HTML标签
            text = re.sub(r'<[^>]+>', '', msg_html)
            text = text.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            text = text.strip()
            
            if text and len(text) > 10:
                post = {
                    "text": text,
                    "contracts": [],
                    "links": []
                }
                
                # 提取合约地址
                contract_pattern = r'0x[a-fA-F0-9]{40}'
                post["contracts"] = re.findall(contract_pattern, text)
                
                # 提取链接
                link_pattern = r'https?://[^\s<>"]+'
                post["links"] = re.findall(link_pattern, text)
                
                posts.append(post)
        
        return posts
    
    def _parse_simple(self, text: str) -> List[Dict]:
        """简单文本解析"""
        posts = []
        lines = text.split('\n')
        current_post = {"text": "", "contracts": [], "links": []}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_post["text"]:
                    posts.append(current_post)
                    current_post = {"text": "", "contracts": [], "links": []}
                continue
            
            current_post["text"] += line + "\n"
            
            # 提取合约地址
            contract_pattern = r'0x[a-fA-F0-9]{40}'
            contracts = re.findall(contract_pattern, line)
            current_post["contracts"].extend(contracts)
            
            # 提取链接
            link_pattern = r'https?://[^\s]+'
            links = re.findall(link_pattern, line)
            current_post["links"].extend(links)
        
        if current_post["text"]:
            posts.append(current_post)
        
        return posts
    
    def extract_gem_call(self, post: Dict) -> Dict:
        """提取Gem Call的结构化信息"""
        text = post.get("text", "")
        
        # 分析内容类型
        call_type = self._classify_content(text)
        
        # 提取关键信息
        info = {
            "raw_text": text[:500],
            "type": call_type,
            "contracts": post.get("contracts", []),
            "links": post.get("links", []),
            "extracted_at": datetime.now().isoformat()
        }
        
        # 如果是Gem Call，提取更多细节
        if call_type == "gem_call":
            info["chain"] = self._detect_chain(text)
            info["sentiment"] = self._detect_sentiment(text)
            info["narrative"] = self._extract_narrative(text)
        
        return info
    
    def _classify_content(self, text: str) -> str:
        """分类内容类型"""
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ['gem', 'call', 'moon', '100x', 'alpha']):
            return "gem_call"
        elif any(kw in text_lower for kw in ['update', 'sold', 'tp', 'take profit']):
            return "position_update"
        elif any(kw in text_lower for kw in ['warning', 'rug', 'honeypot', 'scam']):
            return "warning"
        elif len(text) < 50:
            return "short_update"
        else:
            return "analysis"
    
    def _detect_chain(self, text: str) -> str:
        """检测链"""
        text_lower = text.lower()
        if 'base' in text_lower or 'clanker' in text_lower or 'bankr' in text_lower:
            return "Base"
        elif 'solana' in text_lower or 'sol' in text_lower:
            return "Solana"
        elif 'ethereum' in text_lower or 'eth' in text_lower:
            return "Ethereum"
        elif 'bsc' in text_lower or 'binance' in text_lower:
            return "BSC"
        return "Unknown"
    
    def _detect_sentiment(self, text: str) -> str:
        """检测情绪"""
        text_lower = text.lower()
        bullish = ['bullish', 'moon', '100x', 'gem', 'alpha', 'buy', 'long']
        bearish = ['bearish', 'dump', 'rug', 'sell', 'short', 'avoid']
        
        b_count = sum(1 for w in bullish if w in text_lower)
        be_count = sum(1 for w in bearish if w in text_lower)
        
        if b_count > be_count:
            return "🟢 Bullish"
        elif be_count > b_count:
            return "🔴 Bearish"
        else:
            return "⚪ Neutral"
    
    def _extract_narrative(self, text: str) -> str:
        """提取叙事主题"""
        text_lower = text.lower()
        narratives = {
            "AI": ["ai", "agent", "gpt", "claude", "llm"],
            "Meme": ["meme", "pepe", "doge", "shib", "wojak"],
            "DeFi": ["defi", "yield", "farm", "stake", "liquidity"],
            "Gaming": ["game", "gaming", "p2e", "play"],
            "Social": ["social", "friend", "share", "community"]
        }
        
        for nar, keywords in narratives.items():
            if any(kw in text_lower for kw in keywords):
                return nar
        return "Other"
    
    def check_new_content(self) -> Tuple[bool, List[Dict]]:
        """检查是否有新内容"""
        posts = self.fetch_latest_posts()
        
        # 读取上次记录
        last_check = []
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    last_check = json.load(f)
            except:
                pass
        
        # 对比找新内容
        new_posts = []
        last_texts = [p.get("text", "")[:100] for p in last_check]
        
        for post in posts[:5]:  # 只检查最近5条
            post_preview = post.get("text", "")[:100]
            if post_preview not in last_texts:
                new_posts.append(post)
        
        # 保存当前记录
        with open(self.data_file, 'w') as f:
            json.dump(posts[:10], f, indent=2)
        
        return len(new_posts) > 0, new_posts
    
    def generate_alert(self, posts: List[Dict]) -> str:
        """生成推送内容"""
        lines = [
            "🎯 Pow's Gem Calls 更新",
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 50,
            ""
        ]
        
        for i, post in enumerate(posts[:3], 1):
            info = self.extract_gem_call(post)
            
            lines.append(f"\n🔔 更新 #{i}")
            lines.append(f"类型: {info['type']}")
            
            if info['type'] == 'gem_call':
                lines.append(f"链: {info['chain']}")
                lines.append(f"情绪: {info['sentiment']}")
                lines.append(f"叙事: {info['narrative']}")
            
            lines.append(f"\n内容:\n{info['raw_text'][:300]}...")
            
            if info['contracts']:
                lines.append(f"\n📋 合约地址:")
                for addr in info['contracts'][:3]:
                    lines.append(f"  {addr}")
            
            if info['links']:
                lines.append(f"\n🔗 链接:")
                for link in info['links'][:2]:
                    lines.append(f"  {link}")
            
            lines.append("\n" + "-" * 50)
        
        return "\n".join(lines)
    
    def learn_patterns(self) -> Dict:
        """学习Pow的Gem狩猎模式"""
        posts = self.fetch_latest_posts()
        
        patterns = {
            "total_posts": len(posts),
            "gem_calls": 0,
            "avg_contracts_per_call": 0,
            "preferred_chains": {},
            "common_narratives": {},
            "key_phrases": []
        }
        
        all_contracts = 0
        
        for post in posts:
            info = self.extract_gem_call(post)
            
            if info['type'] == 'gem_call':
                patterns["gem_calls"] += 1
                all_contracts += len(info['contracts'])
                
                chain = info['chain']
                patterns["preferred_chains"][chain] = patterns["preferred_chains"].get(chain, 0) + 1
                
                nar = info['narrative']
                patterns["common_narratives"][nar] = patterns["common_narratives"].get(nar, 0) + 1
        
        if patterns["gem_calls"] > 0:
            patterns["avg_contracts_per_call"] = all_contracts / patterns["gem_calls"]
        
        return patterns
    
    def generate_learning_report(self) -> str:
        """生成学习报告"""
        patterns = self.learn_patterns()
        
        lines = [
            "📚 Pow's Gem Calls 学习报告",
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 50,
            "",
            f"📊 统计数据:",
            f"  总帖子: {patterns['total_posts']}",
            f"  Gem Calls: {patterns['gem_calls']}",
            f"  平均每Call合约数: {patterns['avg_contracts_per_call']:.1f}",
            "",
            f"⛓️ 偏好链:",
        ]
        
        for chain, count in sorted(patterns['preferred_chains'].items(), key=lambda x: -x[1]):
            lines.append(f"  {chain}: {count}")
        
        lines.extend([
            "",
            f"📖 常见叙事:",
        ])
        
        for nar, count in sorted(patterns['common_narratives'].items(), key=lambda x: -x[1]):
            lines.append(f"  {nar}: {count}")
        
        lines.extend([
            "",
            "💡 学习要点:",
            "  1. Pow关注什么链的gem？",
            "  2. 什么叙事最容易被提及？",
            "  3. 如何快速判断一个call的质量？",
            "  4. 什么时机入场/出场？",
        ])
        
        return "\n".join(lines)


def main():
    """主函数"""
    monitor = PowsGemCallsMonitor()
    
    # 检查新内容
    has_new, new_posts = monitor.check_new_content()
    
    if has_new:
        alert = monitor.generate_alert(new_posts)
        print(alert)
        
        # 保存到文件
        filename = f"/tmp/pows_alert_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(alert)
        print(f"\n💾 推送已保存: {filename}")
    else:
        print("📭 暂无新内容")
    
    # 生成学习报告
    report = monitor.generate_learning_report()
    report_file = f"/tmp/pows_learning_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"📚 学习报告已保存: {report_file}")


if __name__ == "__main__":
    main()
