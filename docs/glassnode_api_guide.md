# Glassnode API 申请指南

## 申请步骤

### 1. 注册账号
访问: https://glassnode.com/
点击右上角 "Sign Up" 注册

### 2. 申请API Key
1. 登录后进入 Dashboard
2. 点击左侧菜单 "API"
3. 点击 "Create API Key"
4. 填写用途描述 (示例):
   ```
   Personal cryptocurrency research and portfolio analysis.
   Will be used for tracking BTC on-chain metrics like MVRV ratio
   and long-term holder behavior.
   ```

### 3. 免费层限制
- **请求限额**: 30次/分钟, 每天300次
- **可用指标**: 
  - ✅ 基础链上数据 (MVRV, SOPR, NUPL)
  - ✅ 地址余额分布
  - ✅ 交易所流入流出
  - ❌ 高级指标 (需要付费层)

### 4. 保存API Key
获得Key后保存到环境变量:
```bash
export GLASSNODE_API_KEY="你的API Key"
```

## 接入代码示例

```python
import requests
import os

class GlassnodeClient:
    def __init__(self):
        self.api_key = os.environ.get('GLASSNODE_API_KEY')
        self.base_url = 'https://api.glassnode.com/v1/metrics'
    
    def get_mvrv(self, asset='BTC'):
        """获取MVRV比率"""
        url = f"{self.base_url}/market/mvrv"
        params = {
            'a': asset,
            'api_key': self.api_key
        }
        res = requests.get(url, params=params)
        return res.json()
    
    def get_lth_supply(self, asset='BTC'):
        """获取长期持有者供应量"""
        url = f"{self.base_url}/supply/active_more_1y_percent"
        params = {
            'a': asset,
            'api_key': self.api_key
        }
        res = requests.get(url, params=params)
        return res.json()

# 使用示例
client = GlassnodeClient()
mvrv_data = client.get_mvrv()
lth_data = client.get_lth_supply()
```

## 注意事项

1. **免费层够用吗?**
   - 每天300次请求，BTC抄底模型每天调用1-2次完全够用
   - 如果做多币种监控可能需要付费层 ($29/月)

2. **数据更新频率**
   - 大多数指标24小时更新一次
   - 不需要高频调用

3. **申请审核时间**
   - 通常即时通过
   - 偶尔需要人工审核 (24小时内)

---
申请完成后把API Key发给我，我来接入代码。
