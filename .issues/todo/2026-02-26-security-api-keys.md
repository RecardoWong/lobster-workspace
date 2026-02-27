# Issue: 安全整改 - 硬编码API密钥清理

## 问题描述
代码库中多处存在硬编码的TwitterAPI.io API密钥，需立即清理

## 受影响文件 (9个)

| 文件 | 问题行 | 当前代码 | 风险等级 |
|------|--------|----------|----------|
| `elon_pro_analyzer.py` | 18 | `os.environ.get('TWITTERAPI_IO_KEY') or "new1_47751911508746daafaf9194b664aaed"` | 🟡 中 |
| `monitor_elon_musk.py` | 20 | `os.environ.get('TWITTERAPI_IO_KEY') or "new1_47751911508746daafaf9194b664aaed"` | 🟡 中 |
| `monitor_jdhasoptions.py` | 15 | `os.environ.get('TWITTERAPI_IO_KEY') or "new1_47751911508746daafaf9194b664aaed"` | 🟡 中 |
| `twitterapi_monitor.py` | 18 | `self.api_key = "new1_47751911508746daafaf9194b664aaed"` | 🔴 高 |
| `twitter_full_monitor.py` | 18 | `self.api_key = "new1_47751911508746daafaf9194b664aaed"` | 🔴 高 |
| `twitter_link_monitor.py` | 18 | `self.api_key = "new1_47751911508746daafaf9194b664aaed"` | 🔴 高 |
| `twitter_personal_assistant.py` | 21 | `os.environ.get('TWITTERAPI_IO_KEY') or "new1_47751911508746daafaf9194b664aaed"` | 🟡 中 |
| `twitter_separate_monitor.py` | 17 | `self.api_key = "new1_47751911508746daafaf9194b664aaed"` | 🔴 高 |
| `twitter_trans_monitor.py` | 17 | `self.api_key = "new1_47751911508746daafaf9194b664aaed"` | 🔴 高 |

## 整改方案

### 1. 统一改为纯环境变量读取
```python
# 当前 (不安全，有回退硬编码)
self.api_key = os.environ.get('TWITTERAPI_IO_KEY') or "hardcoded_key"

# 建议 (安全)
self.api_key = os.environ.get('TWITTERAPI_IO_KEY')
if not self.api_key:
    raise ValueError("TWITTERAPI_IO_KEY environment variable not set")
```

### 2. 创建 .env.example 模板
```bash
# Twitter API配置
TWITTERAPI_IO_KEY=your_api_key_here
TWITTER_CONSUMER_KEY=your_consumer_key
TWITTER_CONSUMER_SECRET=your_consumer_secret
```

### 3. 确保 .gitignore 包含
```
.env
*.env
```

## 检查清单

- [ ] 清理 `twitterapi_monitor.py` 硬编码密钥
- [ ] 清理 `twitter_full_monitor.py` 硬编码密钥
- [ ] 清理 `twitter_link_monitor.py` 硬编码密钥
- [ ] 清理 `twitter_separate_monitor.py` 硬编码密钥
- [ ] 清理 `twitter_trans_monitor.py` 硬编码密钥
- [ ] 更新 `elon_pro_analyzer.py` 移除回退值
- [ ] 更新 `monitor_elon_musk.py` 移除回退值
- [ ] 更新 `monitor_jdhasoptions.py` 移除回退值
- [ ] 更新 `twitter_personal_assistant.py` 移除回退值
- [ ] 创建 `.env.example` 模板
- [ ] 更新 `.gitignore`

## 优先级
🔴 高

## 预计工作量
1-2小时

## 备注
此API密钥为TwitterAPI.io的API Key，已确认泄露需立即撤销并重新生成。
