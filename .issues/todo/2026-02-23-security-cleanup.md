# Issue: 安全整改 - 清理硬编码凭证

## 状态: 部分完成，见新Issue #2026-02-26-security-api-keys

> **更新 2026-02-26**: 发现新的硬编码API密钥问题，已创建专门Issue跟踪
> - 新Issue: `2026-02-26-security-api-keys.md` (9个文件)

## 问题描述
多处代码中存在硬编码的API密钥、Token等敏感信息

## 受影响文件 (原始)

| 文件 | 问题 | 风险等级 | 状态 |
|-----|------|---------|------|
| `test_last_hour_tweets.py` | 硬编码Twitter Auth Token和CT0 | 🔴 高 | ✅ 已改为os.getenv |
| `lobster-workspace/twitter_monitor.py` | API key处理逻辑可优化 | 🟡 中 | ⏳ 待验证 |
| `content_analyzer/x_cookie_collector.py` | 可能包含敏感cookie | 🟡 中 | ⏳ 待检查 |

## 新发现问题 (详见 2026-02-26-security-api-keys.md)
- `twitterapi_monitor.py` 等5个文件纯硬编码API密钥
- `elon_pro_analyzer.py` 等4个文件有环境变量回退但仍有硬编码值

## 整改方案

### 1. 迁移到环境变量
```python
# 当前 (不安全)
AUTH_TOKEN = '5da5c73c...'

# 建议 (安全)
AUTH_TOKEN = os.getenv('TWITTER_AUTH_TOKEN')
if not AUTH_TOKEN:
    raise ValueError("TWITTER_AUTH_TOKEN not set")
```

### 2. 添加 .env 文件支持
```python
from dotenv import load_dotenv
load_dotenv()
```

### 3. 清理Git历史 (如已提交)
```bash
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch path/to/file' \
--prune-empty --tag-name-filter cat -- --all
```

## 检查清单

- [ ] 移除 test_last_hour_tweets.py 中的硬编码Token
- [ ] 更新所有脚本使用环境变量
- [ ] 创建 .env.example 模板文件
- [ ] 将真实 .env 加入 .gitignore
- [ ] 审查Git历史确保无敏感信息泄露

## 优先级
🔴 高

## 预计工作量
2-3小时
