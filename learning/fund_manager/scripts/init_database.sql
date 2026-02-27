-- 机构级基金经理数据库初始化脚本
-- 支持 20,000+新闻、50+财报、30+宏观指标

-- 创建数据库
CREATE DATABASE fund_manager;
\c fund_manager;

-- ==================== 新闻表 ====================
CREATE TABLE news_articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT,
    summary TEXT,
    source VARCHAR(100),
    author VARCHAR(100),
    url VARCHAR(500),
    published_at TIMESTAMP NOT NULL,
    category VARCHAR(50),
    sentiment_score FLOAT DEFAULT 0,  -- -1 to 1
    sentiment_label VARCHAR(20),       -- positive/negative/neutral
    relevance_score FLOAT DEFAULT 0,   -- 0 to 1
    importance_score FLOAT DEFAULT 0,  -- 0 to 1
    affected_tickers TEXT[],           -- ['AAPL', 'MSFT']
    affected_sectors TEXT[],           -- ['Technology', 'Finance']
    keywords TEXT[],
    is_important BOOLEAN DEFAULT FALSE,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_news_time ON news_articles(published_at DESC);
CREATE INDEX idx_news_sentiment ON news_articles(sentiment_score);
CREATE INDEX idx_news_relevance ON news_articles(relevance_score DESC);
CREATE INDEX idx_news_important ON news_articles(is_important) WHERE is_important = TRUE;
CREATE INDEX idx_news_tickers ON news_articles USING GIN(affected_tickers);
CREATE INDEX idx_news_source ON news_articles(source);

-- ==================== 财报表 ====================
CREATE TABLE earnings_reports (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    company_name VARCHAR(100),
    quarter VARCHAR(10) NOT NULL,       -- Q1 2024
    report_date DATE NOT NULL,
    fiscal_year INTEGER,
    
    -- 收入
    revenue BIGINT,                     -- 实际营收
    revenue_estimate BIGINT,            -- 预期营收
    revenue_surprise_pct FLOAT,         -- 超预期%
    
    -- 利润
    eps FLOAT,                          -- 每股收益
    eps_estimate FLOAT,                 -- 预期EPS
    eps_surprise_pct FLOAT,             -- 超预期%
    net_income BIGINT,
    
    -- 利润率
    gross_margin FLOAT,
    operating_margin FLOAT,
    net_margin FLOAT,
    
    -- 现金流
    operating_cash_flow BIGINT,
    free_cash_flow BIGINT,
    capex BIGINT,
    
    -- 指引
    guidance_revenue BIGINT,
    guidance_revenue_low BIGINT,
    guidance_revenue_high BIGINT,
    guidance_eps FLOAT,
    guidance_eps_low FLOAT,
    guidance_eps_high FLOAT,
    
    -- 关键指标
    total_debt BIGINT,
    cash_and_equivalents BIGINT,
    shares_outstanding BIGINT,
    
    -- 电话会议
    transcript TEXT,
    key_highlights JSONB,
    management_tone VARCHAR(20),        -- positive/cautious/negative
    
    -- 分析
    analyst_ratings JSONB,              -- [{'firm': 'Goldman', 'rating': 'Buy', 'target': 200}]
    sentiment VARCHAR(20),
    
    -- 市场反应
    price_before FLOAT,
    price_after FLOAT,
    price_change_pct FLOAT,
    volume_surge FLOAT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(ticker, quarter)
);

CREATE INDEX idx_earnings_ticker ON earnings_reports(ticker);
CREATE INDEX idx_earnings_date ON earnings_reports(report_date DESC);
CREATE INDEX idx_earnings_surprise ON earnings_reports(eps_surprise_pct);
CREATE INDEX idx_earnings_quarter ON earnings_reports(quarter);

-- ==================== 宏观指标表 ====================
CREATE TABLE macro_indicators (
    id SERIAL PRIMARY KEY,
    indicator_name VARCHAR(50) NOT NULL,
    indicator_code VARCHAR(20) NOT NULL,    -- CPI, NFP, GDP, etc
    country VARCHAR(10) DEFAULT 'US',
    value FLOAT NOT NULL,
    unit VARCHAR(20),                       -- %, millions, billions
    period DATE NOT NULL,                   -- 数据对应的月份/季度
    
    -- 预期 vs 实际
    estimate FLOAT,
    previous FLOAT,
    change_from_previous FLOAT,
    surprise FLOAT,                         -- 实际 - 预期
    surprise_pct FLOAT,
    
    -- 影响
    impact_level VARCHAR(10),               -- high/medium/low
    market_reaction JSONB,                  -- {'sp500': -0.5, 'nasdaq': -0.8}
    
    -- 历史对比
    historical_avg FLOAT,
    historical_max FLOAT,
    historical_min FLOAT,
    
    source VARCHAR(50),
    release_time TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(indicator_code, country, period)
);

CREATE INDEX idx_macro_indicator ON macro_indicators(indicator_code);
CREATE INDEX idx_macro_period ON macro_indicators(period DESC);
CREATE INDEX idx_macro_country ON macro_indicators(country);

-- ==================== 行业报告表 ====================
CREATE TABLE sector_reports (
    id SERIAL PRIMARY KEY,
    sector_name VARCHAR(50) NOT NULL,       -- Technology, Healthcare
    sub_sector VARCHAR(50),
    report_title VARCHAR(200),
    report_date DATE,
    author VARCHAR(100),
    firm VARCHAR(100),                      -- Goldman Sachs, Morgan Stanley
    
    -- 内容
    summary TEXT,
    key_points TEXT[],
    full_text TEXT,
    
    -- 评级
    sector_rating VARCHAR(20),              -- Overweight/Neutral/Underweight
    top_picks TEXT[],                       -- ['AAPL', 'MSFT']
    
    -- 估值
    pe_ratio FLOAT,
    pb_ratio FLOAT,
    ev_ebitda FLOAT,
    vs_sp500_premium FLOAT,                 -- 相对标普500溢价
    
    -- 趋势
    earnings_growth_forecast FLOAT,
    revenue_growth_forecast FLOAT,
    margin_trend VARCHAR(20),               -- expanding/stable/contracting
    
    file_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sector_name ON sector_reports(sector_name);
CREATE INDEX idx_sector_date ON sector_reports(report_date DESC);

-- ==================== 市场数据表 ====================
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    
    -- 价格
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    adj_close FLOAT,
    
    -- 成交量
    volume BIGINT,
    avg_volume_20d BIGINT,
    
    -- 技术指标
    sma_20 FLOAT,
    sma_50 FLOAT,
    sma_200 FLOAT,
    rsi_14 FLOAT,
    macd FLOAT,
    bollinger_upper FLOAT,
    bollinger_lower FLOAT,
    
    -- 波动率
    volatility_20d FLOAT,
    atr_14 FLOAT,
    
    -- 资金流向
    money_flow BIGINT,
    institutional_flow BIGINT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ticker, date)
);

CREATE INDEX idx_market_ticker ON market_data(ticker);
CREATE INDEX idx_market_date ON market_data(date DESC);

-- ==================== 投资组合表 ====================
CREATE TABLE portfolio_holdings (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    position_type VARCHAR(10) DEFAULT 'long',  -- long/short
    shares FLOAT,
    avg_cost FLOAT,
    current_price FLOAT,
    market_value FLOAT,
    unrealized_pnl FLOAT,
    unrealized_pnl_pct FLOAT,
    weight_pct FLOAT,                           -- 组合权重
    
    -- 评级
    rating VARCHAR(20),                         -- buy/hold/sell
    target_price FLOAT,
    stop_loss FLOAT,
    
    -- 更新
    last_updated TIMESTAMP DEFAULT NOW(),
    notes TEXT
);

CREATE INDEX idx_portfolio_ticker ON portfolio_holdings(ticker);

-- ==================== 分析日志表 ====================
CREATE TABLE analysis_logs (
    id SERIAL PRIMARY KEY,
    analysis_type VARCHAR(50),                  -- news/earnings/macro
    ticker VARCHAR(10),
    analysis_date DATE,
    
    -- 分析内容
    summary TEXT,
    key_findings JSONB,
    recommendation VARCHAR(20),
    confidence_score FLOAT,
    
    -- 结果跟踪
    actual_outcome VARCHAR(20),
    accuracy_score FLOAT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_analysis_type ON analysis_logs(analysis_type);
CREATE INDEX idx_analysis_date ON analysis_logs(analysis_date DESC);

-- ==================== 触发器 ====================
-- 自动更新 updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_news_updated_at BEFORE UPDATE ON news_articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_earnings_updated_at BEFORE UPDATE ON earnings_reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==================== 视图 ====================
-- 重要新闻视图
CREATE VIEW important_news AS
SELECT * FROM news_articles
WHERE is_important = TRUE OR relevance_score > 0.8
ORDER BY published_at DESC;

-- 最新财报视图
CREATE VIEW latest_earnings AS
SELECT DISTINCT ON (ticker) *
FROM earnings_reports
ORDER BY ticker, report_date DESC;

-- 组合概览视图
CREATE VIEW portfolio_summary AS
SELECT 
    SUM(market_value) as total_value,
    SUM(unrealized_pnl) as total_pnl,
    AVG(unrealized_pnl_pct) as avg_return,
    COUNT(*) as num_positions
FROM portfolio_holdings;

-- ==================== 初始化数据 ====================
-- 插入一些示例宏观指标
INSERT INTO macro_indicators (indicator_name, indicator_code, value, unit, period, estimate, previous, impact_level)
VALUES 
    ('Consumer Price Index', 'CPI', 3.1, '%', '2024-01-01', 2.9, 3.4, 'high'),
    ('Nonfarm Payrolls', 'NFP', 353000, 'jobs', '2024-01-01', 180000, 333000, 'high'),
    ('Fed Funds Rate', 'FEDRATE', 5.5, '%', '2024-01-01', 5.5, 5.5, 'high'),
    ('GDP Growth', 'GDP', 3.3, '%', '2023-12-01', 2.0, 4.9, 'high'),
    ('Unemployment Rate', 'UNEMP', 3.7, '%', '2024-01-01', 3.8, 3.7, 'medium');

-- 插入示例持仓
INSERT INTO portfolio_holdings (ticker, shares, avg_cost, current_price, market_value, unrealized_pnl, rating, target_price)
VALUES
    ('AAPL', 1000, 150.0, 185.0, 185000, 35000, 'buy', 220.0),
    ('MSFT', 800, 300.0, 420.0, 336000, 96000, 'buy', 500.0),
    ('NVDA', 500, 400.0, 700.0, 350000, 150000, 'hold', 750.0);

-- 完成
SELECT 'Database initialized successfully!' as status;
