# 语义搜索系统 - 两层记忆架构

## 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                      热记忆 (Hot)                        │
│  ┌─────────────────┐  ┌──────────────────────────────┐ │
│  │ MEMORY.md       │  │ memory/2026-02-20.md         │ │
│  │ ~200行          │  │ 当前活跃记忆                  │ │
│  │ 每次加载        │  │ 优先级分类 P0/P1/P2          │ │
│  └─────────────────┘  └──────────────────────────────┘ │
│                                                         │
│  Token 可控，快速访问                                    │
└─────────────────────────────────────────────────────────┘
                          ↕  淘汰/压缩
┌─────────────────────────────────────────────────────────┐
│                      冷记忆 (Cold)                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │ memory/archive/                                   │  │
│  │ - 2026-02-past.md                                │  │
│  │ - week_2026-02-13_2026-02-19.log.2026-02-20.bak │  │
│  │ - ...                                            │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  无限容量，语义索引，按需召回                             │
└─────────────────────────────────────────────────────────┘
```

## 工作原理

1. **热记忆**：当前活跃的 P0/P1/P2 记忆，约200行，每次对话加载
2. **冷记忆**：归档的历史记忆，通过语义搜索按需召回
3. **联想**：语义搜索就是 AI 的"联想能力"，根据当前话题召回相关记忆

## 使用方法

### 1. 建立索引

```bash
cd /root/.openclaw/workspace/memory
node semantic-search.js index
```

扫描 `archive/` 目录，为所有归档记忆建立语义索引。

### 2. 召回记忆

```bash
# 手动搜索
node semantic-search.js search "Twitter更新失败"
node semantic-search.js search "浏览器缓存问题"
node semantic-search.js search "Dashboard布局"

# JSON输出（供程序调用）
node semantic-search.js api "Twitter更新失败"
```

### 3. 在对话中自动召回

修改 `SOUL.md` 或 `AGENTS.md`，在每次对话开始时：

```javascript
// 分析当前话题
const topic = analyzeTopic(userMessage);

// 从冷记忆召回相关内容
const recalled = await semanticSearch(topic);

// 将召回的内容加入上下文
if (recalled.length > 0) {
  context += "\n\n【相关历史记忆】\n" + recalled.map(r => r.text).join('\n');
}
```

## 嵌入模型选择

当前使用**本地简单嵌入**（无需API，但效果一般）。

### 升级到 Voyage AI（推荐，中文效果好）

```bash
# 1. 获取 API Key: https://www.voyageai.com/
export VOYAGE_API_KEY="your-api-key"
export EMBED_PROVIDER="voyage"

# 2. 修改 semantic-search.js
# 在 getEmbedding() 函数中添加 Voyage API 调用
```

### 升级到 OpenAI

```bash
export OPENAI_API_KEY="your-api-key"
export EMBED_PROVIDER="openai"
```

## 定时任务

建议每天重建索引（归档可能有新增）：

```bash
# crontab -e
30 5 * * * cd /root/.openclaw/workspace/memory && node semantic-search.js index >> logs/search-index.log 2>&1
```

## 效果对比

| 方式 | 优点 | 缺点 |
|------|------|------|
| 本地嵌入 | 免费、无需网络、隐私 | 准确度一般（~50-60%） |
| Voyage AI | 中文好、准确率高（~80-90%） | 需要API Key、收费 |
| OpenAI | 英文好、速度快 | 中文一般、需要API Key |

## 使用示例

**场景**：用户问 "Twitter 为什么显示旧内容？"

```bash
$ node semantic-search.js search "Twitter旧内容"

🔍 语义搜索: "Twitter旧内容"
============================================================
✨ 召回 5 条相关记忆 (2ms)

1. [59%] Twitter更新待彻底解决：脚本更新JSON但未正确写入HTML
2. [57%] Twitter从动态加载改为静态HTML嵌入（浏览器缓存）
3. [56%] Twitter：Playwright抓取 + MyMemory翻译
4. [51%] Twitter API速率限制超限，脚本失败
5. [51%] Twitter显示旧内容，解决方案：脚本同时更新JSON和HTML
```

AI 根据召回的记忆，立即知道：
- 这是已知问题（P2 待解决）
- 原因是脚本只更新JSON，没更新HTML静态内容
- 之前的解决方案是改为静态HTML嵌入

无需翻阅海量日志，联想能力瞬间激活！
