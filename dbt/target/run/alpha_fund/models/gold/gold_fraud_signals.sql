
  
    
    

    create  table
      "alpha_fund"."main"."gold_fraud_signals__dbt_tmp"
  
    as (
      -- Gold table 2: Fraud signals feed
-- All high risk trades for the risk team
-- Refreshed hourly -- SLA: risk team investigates within 2 hours

SELECT
    trade_id,
    fund_id,
    ticker,
    action,
    shares,
    price_per_share,
    total_value,
    trader_id,
    broker,
    execution_time,
    fraud_score,
    fraud_flag,
    risk_category,
    CASE
        WHEN fraud_score >= 90 THEN 'CRITICAL'
        WHEN fraud_score >= 75 THEN 'HIGH'
        WHEN fraud_score >= 40 THEN 'MEDIUM'
        ELSE 'LOW'
    END                           AS alert_level,
    CURRENT_TIMESTAMP             AS flagged_at
FROM "alpha_fund"."silver"."trades"
WHERE fraud_score >= 40
ORDER BY fraud_score DESC
    );
  
  