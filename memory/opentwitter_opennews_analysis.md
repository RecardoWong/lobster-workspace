# opentwitter-mcp & opennews-mcp 架构分析

## 概述

两个 skill 都使用 **6551 API** 架构，属于 **MCP (Model Context Protocol)** 类型 skill。

---

## 1. opentwitter-mcp 架构设计

### 核心功能模块

```
opentwitter-mcp/
├── src/
│   ├── api/           # 6551 API 接口层
│   │   ├── client.py      # API 客户端
│   │   ├── auth.py        # 认证管理
│   │   └── rate_limit.py  # 限流处理
│   ├── modules/       # 功能模块
│   │   ├── user_profile.py      # 用户资料查询
│   │   ├── tweet_search.py      # 推文搜索
│   │   ├── user_tweets.py       # 用户推文获取
│   │   ├── follower_events.py   # 粉丝事件监控
│   │   ├── deleted_tweets.py    # 删除推文追踪
│   │   └── kol_followers.py     # KOL 粉丝分析
│   ├── models/        # 数据模型
│   │   ├── tweet.py
│   │   ├── user.py
│   │   └── event.py
│   └── utils/         # 工具函数
│       ├── parser.py      # 数据解析
│       └── formatter.py   # 格式转换
├── config/
│   └── settings.yaml  # 配置文件
└── tests/
```

### 6551 API 特点

1. **统一接口规范**
   - 所有请求通过 6551 协议标准化
   - 支持 RESTful + WebSocket 双模式

2. **数据字段标准化**
   ```json
   {
     "tweet_id": "string",
     "author": {
       "id": "string",
       "username": "string",
       "display_name": "string"
     },
     "content": {
       "text": "string",
       "entities": [...]
     },
     "metrics": {
       "likes": 0,
       "retweets": 0,
       "replies": 0
     },
     "created_at": "ISO8601",
     "source": "string"
   }
   ```

3. **实时事件流**
   - WebSocket 连接保持实时推送
   - 支持 follower events、deleted tweets 等事件

---

## 2. opennews-mcp 架构设计

### 核心功能模块

```
opennews-mcp/
├── src/
│   ├── api/
│   │   ├── opennews_client.py   # OpenNews API 客户端
│   │   └── websocket.py         # 实时推送连接
│   ├── modules/
│   │   ├── news_search.py       # 新闻搜索
│   │   ├── ai_rating.py         # AI 评级系统
│   │   ├── trading_signals.py   # 交易信号
│   │   ├── realtime_updates.py  # 实时更新
│   │   ├── coin_filter.py       # 币种过滤
│   │   └── source_filter.py     # 来源过滤
│   ├── ai/
│   │   ├── sentiment.py         # 情感分析
│   │   ├── importance.py        # 重要性评分
│   │   └── classification.py    # 新闻分类
│   └── models/
│       ├── news_article.py
│       ├── rating.py
│       └── signal.py
└── config/
    └── sources.yaml       # 新闻源配置
```

### AI 评级系统设计

1. **多维度评分**
   ```python
   {
     "relevance": 0-100,      # 相关性
     "credibility": 0-100,    # 可信度
     "timeliness": 0-100,     # 时效性
     "impact": 0-100,         # 市场影响
     "overall": 0-100         # 综合评分
   }
   ```

2. **交易信号生成**
   ```python
   {
     "signal_type": "buy|sell|hold|watch",
     "confidence": 0-100,
     "timeframe": "short|medium|long",
     "related_coins": ["BTC", "ETH", ...],
     "reasoning": "string"
   }
   ```

---

## 3. 6551 API 协议分析

### 协议特点

1. **标准化请求格式**
   ```http
   GET /api/v1/6551/{resource}
   Headers:
     X-6551-API-Key: {key}
     X-6551-Version: 1.0
   ```

2. **流式响应支持**
   ```json
   {
     "type": "stream|batch|event",
     "data": {...},
     "metadata": {
       "timestamp": "",
       "source": "",
       "confidence": 0-100
     }
   }
   ```

3. **增量更新机制**
   - 支持 cursor-based 分页
   - WebSocket 推送变更

---

## 4. 对我们系统的改进建议

### 可以借鉴的模块

| 功能 | opentwitter | opennews | 我们的现状 | 改进建议 |
|------|-------------|----------|-----------|----------|
| 数据标准化 | ✅ 6551协议 | ✅ 标准化 | ⚠️ 自定义格式 | 统一数据模型 |
| 实时流 | ✅ WebSocket | ✅ WebSocket | ❌ 轮询 | 增加流式推送 |
| AI评级 | ❌ | ✅ | ❌ | 增加新闻AI评分 |
| 交易信号 | ❌ | ✅ | ❌ | 增加信号系统 |
| 删除追踪 | ✅ | ❌ | ❌ | 可增加推文变更追踪 |
| 事件驱动 | ✅ 粉丝事件 | ✅ 实时新闻 | ❌ 定时抓取 | 改为事件驱动 |

### 具体改进点

1. **数据模型标准化**
   ```python
   # 统一推文模型
   class StandardTweet:
       id: str
       author: Author
       content: Content
       metrics: Metrics
       metadata: Metadata
       events: List[Event]  # 新增：事件历史
   ```

2. **AI 分析层**
   ```python
   # 增加AI评级
   class AIAnalyzer:
       def rate_importance(tweet) -> Rating
       def generate_signal(news) -> Signal
       def sentiment_analysis(text) -> Sentiment
   ```

3. **事件驱动架构**
   ```python
   # 从轮询改为事件驱动
   class EventDrivenMonitor:
       def on_new_tweet(tweet)
       def on_tweet_deleted(tweet_id)
       def on_follower_change(user, delta)
   ```

4. **实时推送优化**
   - 使用 WebSocket 替代轮询
   - 减少延迟，提高实时性

---

## 5. 实现参考

### 6551 API Client 伪代码

```python
class MCP6551Client:
    def __init__(self, api_key, endpoint):
        self.api_key = api_key
        self.endpoint = endpoint
        self.ws = None
    
    # REST API 调用
    def query(self, resource, params):
        headers = {'X-6551-API-Key': self.api_key}
        return requests.get(f"{self.endpoint}/{resource}", 
                          headers=headers, params=params)
    
    # WebSocket 实时连接
    def connect_stream(self, callback):
        self.ws = websocket.create_connection(
            f"{self.endpoint}/stream",
            header=[f"X-6551-API-Key: {self.api_key}"]
        )
        while True:
            data = self.ws.recv()
            callback(json.loads(data))
```

### AI 评级系统伪代码

```python
class AIRatingEngine:
    def rate_content(self, content):
        scores = {
            'relevance': self.calc_relevance(content),
            'credibility': self.calc_credibility(content.source),
            'timeliness': self.calc_timeliness(content.time),
            'impact': self.calc_market_impact(content)
        }
        scores['overall'] = weighted_average(scores)
        return scores
    
    def generate_trading_signal(self, news, ratings):
        if ratings['impact'] > 80 and news.sentiment == 'positive':
            return Signal(type='buy', confidence=ratings['overall'])
        # ...
```

---

## 总结

**核心价值**:
1. 标准化数据模型 (6551 API)
2. 事件驱动实时推送 (WebSocket)
3. AI 智能分析 (评级+信号)
4. 模块化架构 (可扩展)

**我们可以学习的**:
1. 统一数据格式，便于后续分析
2. 增加 AI 评级层，自动判断重要性
3. 优化为事件驱动，减少无效轮询
4. 增加交易信号生成能力
