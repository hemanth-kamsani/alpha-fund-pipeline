# Alpha Growth Fund — Data Pipeline

End-to-end financial data pipeline implementing the 
Medallion Architecture (Bronze → Silver → Gold) on AWS.

## Stack
Python · AWS S3 · AWS Glue · Great Expectations · 
dbt · Snowflake · Apache Airflow

## Domain
BFSI — mutual fund trade processing, NAV calculation,
fraud detection, regulatory compliance

## Architecture

## Progress
- [x] Phase 0 — Environment setup
- [x] Phase 1 — Trade data generator
- [x] Phase 2 — S3 Bronze landing
- [ ] Phase 3 — AWS Glue Silver cleaning
- [ ] Phase 4 — Great Expectations quality gates
- [ ] Phase 5 — dbt Gold models
- [ ] Phase 6 — Snowflake warehouse
- [ ] Phase 7 — Airflow orchestration

## Author
Hemanth Kamsani