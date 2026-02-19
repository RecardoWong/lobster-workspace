# Dashboard 数据管理 Skill

## 何时触发

当涉及以下任务时触发：
- "这个数据从哪里获取"
- "帮我添加自动更新"
- "定时任务怎么设置"
- "数据不显示了"
- "API限制怎么办"

## 数据源分类

### 1. 实时数据（可用）

| 数据类型 | API | 更新频率 | 可靠性 |
|---------|-----|---------|--------|
| 比特币 | 币安 API | 每5分钟 | ⭐⭐⭐⭐⭐ |
| 英诺赛科 | 腾讯财经 | 每5分钟 | ⭐⭐⭐⭐ |
| 港股美股 | 腾讯财经 | 每5分钟 | ⭐⭐⭐⭐ |
| Twitter | Playwright抓取 | 每小时 | ⭐⭐⭐ |
| 财经新闻 | 多源聚合 | 每30分钟 | ⭐⭐⭐ |

### 2. 已测试不可用的API

❌ 新浪财经 - 403 限制
❌ Yahoo Finance - 需要认证
❌ Alpha Vantage免费版 - 频率限制太低

## 添加新数据源的流程

### 步骤1: 验证API可用性

```python
# 测试脚本模板
try:
    response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
    data = response.json()
    print(f"✅ API可用: {data.keys()}")
except Exception as e:
    print(f"❌ API失败: {e}")
```

### 步骤2: 创建抓取脚本

位置: `scripts/[source]_fetch.py`

```python
#!/usr/bin/env python3
"""
[数据源名称] 数据抓取
- 来源: [API URL]
- 频率: [X分钟/小时]
- 输出: dashboard/data/[name].json
"""

def fetch_data():
    # 实现抓取逻辑
    pass

def save_data(data):
    # 保存到JSON
    pass

if __name__ == '__main__':
    fetch_data()
```

### 步骤3: 创建更新脚本

位置: `scripts/update_[name].py`

```python
#!/usr/bin/env python3
"""
更新 Dashboard [板块名称]
"""

def update_html():
    # 读取JSON数据
    # 更新HTML中的静态内容
    # 部署到服务器
    pass

if __name__ == '__main__':
    update_html()
```

### 步骤4: 添加到定时任务

```bash
# 编辑crontab
crontab -e

# 添加任务
# [数据名称] - 每X分钟更新
*/X * * * * cd /root/.openclaw/workspace/lobster-workspace && python3 scripts/update_[name].py >> logs/[name].log 2>&1
```

### 步骤5: 验证

- [ ] 手动运行脚本成功
- [ ] 定时任务正常执行
- [ ] Dashboard显示最新数据
- [ ] 错误日志正常记录

## 数据抓取最佳实践

### 错误处理

```python
def safe_fetch(url, retries=3):
    for i in range(retries):
        try:
            response = requests.get(url, timeout=10)
            return response.json()
        except Exception as e:
            if i == retries - 1:
                # 发送告警（可选）
                print(f"Failed after {retries} retries: {e}")
                return None
            time.sleep(2 ** i)  # 指数退避
```

### 缓存策略

```python
# 避免重复抓取相同数据
cache_file = '/tmp/cache_[name].json'
cache_duration = 300  # 5分钟

def get_cached_data():
    if os.path.exists(cache_file):
        mtime = os.path.getmtime(cache_file)
        if time.time() - mtime < cache_duration:
            with open(cache_file) as f:
                return json.load(f)
    return None
```

## 常见问题

### 问题: API返回403
**解决**: 
- 添加User-Agent头
- 使用代理（如果需要）
- 寻找替代API

### 问题: 数据更新不及时
**解决**:
- 检查cron日志: `grep CRON /var/log/syslog`
- 检查脚本日志: `tail -f logs/[name].log`
- 验证定时任务: `crontab -l`

### 问题: 数据格式变化
**解决**:
- 添加数据验证
- 记录原始响应
- 发送告警通知

## 数据更新频率建议

| 数据类型 | 建议频率 | 理由 |
|---------|---------|------|
| 股价 | 5分钟 | 实时性要求高 |
| 加密货币 | 5分钟 | 波动大 |
| Twitter | 1小时 | 避免API限制 |
| 新闻 | 30分钟 | 内容更新较慢 |
| 指数 | 15分钟 | 相对稳定的指标 |

## 监控和告警

创建监控脚本 `scripts/monitor_data.py`:

```python
#!/usr/bin/env python3
"""监控数据更新状态"""

def check_data_freshness():
    # 检查每个数据源的最后更新时间
    # 如果超过阈值，发送告警
    pass

if __name__ == '__main__':
    check_data_freshness()
```

添加到定时任务:
```bash
# 每10分钟检查一次数据新鲜度
*/10 * * * * python3 scripts/monitor_data.py
```
