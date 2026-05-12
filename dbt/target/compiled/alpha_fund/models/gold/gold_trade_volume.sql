-- Gold table 3: Daily trade volume by ticker
-- Used by fund manager and BA for portfolio analysis

SELECT
    ticker,
    action,
    COUNT(*)                AS trade_count,
    SUM(shares)             AS total_shares,
    SUM(total_value)        AS total_value,
    AVG(price_per_share)    AS avg_price,
    MIN(price_per_share)    AS min_price,
    MAX(price_per_share)    AS max_price,
    SUM(CASE WHEN action = 'BUY'
        THEN total_value ELSE 0 END)  AS buy_value,
    SUM(CASE WHEN action = 'SELL'
        THEN total_value ELSE 0 END)  AS sell_value,
    CURRENT_TIMESTAMP       AS calculated_at
FROM "alpha_fund"."silver"."trades"
GROUP BY ticker, action
ORDER BY total_value DESC