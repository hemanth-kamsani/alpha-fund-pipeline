import snowflake.connector
import pandas as pd
import duckdb

# ── Your Snowflake credentials ──────────────────────────────
# Replace these with your actual values
SNOWFLAKE_CONFIG = {
    "account"  : "szc08874.us-east-1" ,  
    "user"     : "HEMANTHREDDY" ,
    "password" : "9440927454Abc@" ,
    "warehouse": "COMPUTE_WH",
    "database" : "ALPHA_FUND_DB",
    "schema"   : "GOLD"
}

DUCKDB_PATH = "data/alpha_fund.duckdb"

def get_snowflake_connection():
    """Creates and returns a Snowflake connection."""
    return snowflake.connector.connect(**SNOWFLAKE_CONFIG)

def setup_snowflake():
    """Creates database, schema, and warehouse in Snowflake."""
    print("🔧 Setting up Snowflake...")

    # Connect without database first
    config = SNOWFLAKE_CONFIG.copy()
    config.pop("database")
    config.pop("schema")
    conn = snowflake.connector.connect(**config)
    cursor = conn.cursor()

    # Create database
    cursor.execute("CREATE DATABASE IF NOT EXISTS ALPHA_FUND_DB")
    print("✅ Database ALPHA_FUND_DB created")

    # Create schema
    cursor.execute("USE DATABASE ALPHA_FUND_DB")
    cursor.execute("CREATE SCHEMA IF NOT EXISTS GOLD")
    print("✅ Schema GOLD created")

    # Create warehouse
    cursor.execute("""
        CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH
        WITH WAREHOUSE_SIZE = 'X-SMALL'
        AUTO_SUSPEND = 60
        AUTO_RESUME = TRUE
    """)
    print("✅ Warehouse COMPUTE_WH created")

    cursor.close()
    conn.close()
    print("✅ Snowflake setup complete")

def load_gold_to_snowflake():
    """Reads Gold tables from DuckDB and loads into Snowflake."""
    print("\n📤 Loading Gold tables to Snowflake...")

    # Read Gold tables from DuckDB
    duck = duckdb.connect(DUCKDB_PATH)

    tables = [
        "gold_portfolio_summary",
        "gold_fraud_signals",
        "gold_trade_volume"
    ]

    conn = get_snowflake_connection()
    cursor = conn.cursor()

    for table in tables:
        print(f"\n⬆️  Loading {table}...")

        # Read from DuckDB
        df = duck.execute(f"SELECT * FROM main.{table}").df()
        print(f"   📊 {len(df)} records to load")

        # Convert datetime columns to string for Snowflake
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype(str)

        # Convert category columns to string
        for col in df.select_dtypes(include=["category"]).columns:
            df[col] = df[col].astype(str)

        # Create table in Snowflake
        columns = []
        for col, dtype in df.dtypes.items():
            if "int" in str(dtype):
                sf_type = "NUMBER"
            elif "float" in str(dtype):
                sf_type = "FLOAT"
            elif "bool" in str(dtype):
                sf_type = "BOOLEAN"
            else:
                sf_type = "VARCHAR"
            columns.append(f"{col} {sf_type}")

        create_sql = f"""
            CREATE OR REPLACE TABLE ALPHA_FUND_DB.GOLD.{table.upper()} (
                {', '.join(columns)}
            )
        """
        cursor.execute(create_sql)

        # Insert data in batches
        cols = ", ".join(df.columns)
        placeholders = ", ".join(["%s"] * len(df.columns))
        insert_sql = f"INSERT INTO ALPHA_FUND_DB.GOLD.{table.upper()} ({cols}) VALUES ({placeholders})"

        batch_size = 1000
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            cursor.executemany(insert_sql, batch.values.tolist())

        print(f"   ✅ {table} loaded successfully")

    cursor.close()
    conn.close()
    duck.close()
    print("\n✅ All Gold tables loaded to Snowflake")

if __name__ == "__main__":
    setup_snowflake()
    load_gold_to_snowflake()