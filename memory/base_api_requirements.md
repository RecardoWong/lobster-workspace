# Base链API需求

## 需要的功能
1. 查询地址持仓（Token列表+数量）
2. 查询地址交易历史
3. 实时/近实时更新

## 可选API来源

### 1. BaseScan API ⭐⭐⭐
- 官网: https://basescan.org/apis
- 免费额度: 5 calls/second
- 功能: 地址持仓、交易历史、合约信息
- 需要: API Key (免费申请)

### 2. DeBank API ⭐⭐⭐
- 官网: https://cloud.debank.com/
- 免费额度: 有免费 tier
- 功能: 多链持仓、DeFi仓位、NFT
- 需要: API Key

### 3. Alchemy / Infura ⭐⭐
- 功能: Base节点访问
- 需要: 自己写合约调用
- 复杂度高

### 4. Covalent API ⭐⭐
- 官网: https://www.covalenthq.com/
- 功能: 链上数据索引
- 免费额度有限

## 推荐
**BaseScan API** 最简单直接，只需要读地址持仓和交易。

申请地址: https://basescan.org/apis
