# AkShare 功能增强清单

## 📊 已集成到系统的 akshare 功能

### 1. 财报数据 ✅
| 功能 | 函数 | 用途 | 文件 |
|------|------|------|------|
| 分红历史 | `stock_dividend_cninfo()` | 查看公司分红记录 | `cninfo_akshare_reader.py` |
| 配股历史 | `stock_allotment_cninfo()` | 查看配股方案 | `cninfo_akshare_reader.py` |
| 财务指标 | `stock_financial_analysis_indicator()` | ROE/毛利率等 | `a_share_earnings_reader.py` |
| 资产负债表 | `stock_balance_sheet_by_report_em()` | 资产负债结构 | `a_share_earnings_reader.py` |

### 2. 市场监控 (新增) ✅
| 功能 | 函数 | 用途 | 文件 |
|------|------|------|------|
| 融资融券 | `stock_margin_szse()/sse()` | 市场情绪指标 | `a_share_market_monitor.py` |
| 行业资金流向 | `stock_sector_fund_flow_rank()` | 板块热度 | `a_share_market_monitor.py` |
| 个股资金流向 | `stock_individual_fund_flow()` | 主力进出 | `a_share_market_monitor.py` |
| 北向资金 | `stock_hsgt_fund_flow_summary_em()` | 外资动向 | `a_share_market_monitor.py` |
| 龙虎榜 | `stock_lhb_detail_daily_sina()` | 游资/机构动向 | `a_share_market_monitor.py` |
| 大宗交易 | `stock_dzjy_mrmx()` | 机构大额交易 | `a_share_market_monitor.py` |

### 3. 实时行情 ✅
| 功能 | 函数 | 用途 | 文件 |
|------|------|------|------|
| A股实时行情 | `stock_zh_a_spot_em()` | 价格/涨跌/市值 | `a_share_earnings_reader.py` |

---

## 🚀 可以进一步添加的功能

### 情绪/热点类
- `stock_zt_pool_em()` - 涨停股池，看市场热度
- `stock_zt_pool_strong_em()` - 强势股池
- `stock_zt_pool_sub_new_em()` - 次新股涨停

### 机构/股东类
- `stock_gdfx_free_holding_detail_em()` - 股东持股详情
- `stock_gdfx_free_holding_change_em()` - 股东增减持
- `stock_gdfx_free_top_10_em()` - 十大流通股东

### 行业/概念类
- `stock_board_concept_name_em()` - 概念板块列表
- `stock_board_concept_cons_em()` - 概念板块成分股
- `stock_board_industry_name_em()` - 行业板块列表

### 新股/打新类
- `stock_xgsr_ths()` - 新股申购
- `stock_xgjl_ths()` - 新股缴款
- `stock_xgsg_ths()` - 新股上市

### 宏观经济类
- `macro_china_cpi()` - CPI数据
- `macro_china_pmi()` - PMI数据
- `macro_china_gdp()` - GDP数据

---

## 💡 建议优先级

### 高优先级 (立即有用)
1. **龙虎榜** - 看游资动向
2. **融资融券** - 市场情绪
3. **资金流向** - 主力进出
4. **北向资金** - 外资动向 ✅ 已添加

### 中优先级 (增强分析)
1. **股东增减持** - 内部人动向
2. **涨停股池** - 热点追踪
3. **概念板块** - 题材挖掘

### 低优先级 (锦上添花)
1. 宏观经济数据
2. 新股数据
3. 期货/期权数据

---

## 📝 总结

当前已用 akshare 功能：
- ✅ 财务数据 (分红/配股/财报)
- ✅ 市场监控 (两融/资金流向/北向资金)
- ✅ 实时行情
- ✅ 龙虎榜 (待修复参数)

**需要添加哪些功能？**
