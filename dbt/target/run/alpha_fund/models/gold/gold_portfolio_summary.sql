
  
    
    

    create  table
      "alpha_fund"."main"."gold_portfolio_summary__dbt_tmp"
  
    as (
      -- Gold table 1: Portfolio summary
-- Shows daily portfolio value, AUM, and concentration per stock
-- Finance team queries this every morning for NAV calculation

SELECT
    fund_id,
    fund_name,
    ticker,
    action,
    COUNT(*)                          AS total_trades,
    SUM(shares)                       AS total_shares,
    AVG(price_per_share)              AS avg_price,
    SUM(total_value)                  AS total_value,
    SUM(SUM(total_value)) OVER ()     AS total_aum,
    ROUND(
        SUM(total_value) * 100.0 /
        SUM(SUM(total_value)) OVER (), 2
    )                                 AS concentration_pct,
    CASE
        WHEN ROUND(
            SUM(total_value) * 100.0 /
            SUM(SUM(total_value)) OVER (), 2
        ) >= 8 THEN 'APPROACHING LIMIT'
        ELSE 'WITHIN LIMIT'
    END                               AS regulatory_status,
    CURRENT_TIMESTAMP                 AS calculated_at
FROM "alpha_fund"."silver"."trades"
GROUP BY fund_id, fund_name, ticker, action
ORDER BY total_value DESC
    );
  
  