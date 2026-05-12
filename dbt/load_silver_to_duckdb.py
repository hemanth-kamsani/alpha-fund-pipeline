import duckdb
import pandas as pd
from datetime import datetime

# Paths
SILVER_FILE = "data/silver/trades_silver_20260511.parquet"
DB_PATH = "data/alpha_fund.duckdb"

def load_silver():
    """Loads Silver Parquet into DuckDB for dbt to transform."""
    print(f"📖 Loading Silver data from {SILVER_FILE}")
    
    df = pd.read_parquet(SILVER_FILE)
    print(f"📊 Loaded {len(df)} records")
    
    con = duckdb.connect(DB_PATH)
    con.execute("CREATE SCHEMA IF NOT EXISTS silver")
    con.execute("DROP TABLE IF EXISTS silver.trades")
    con.execute("CREATE TABLE silver.trades AS SELECT * FROM df")
    
    count = con.execute("SELECT COUNT(*) FROM silver.trades").fetchone()[0]
    print(f"✅ Loaded {count} records into silver.trades")
    
    con.close()
    print("✅ DuckDB ready for dbt")

if __name__ == "__main__":
    load_silver()
