import pandas as pd
import boto3
import json
import os
from datetime import datetime

# ── Configuration ──────────────────────────────────────────
BRONZE_BUCKET = "alpha-fund-bronze"
SILVER_BUCKET = "alpha-fund-silver"
TODAY = datetime.now()
BRONZE_KEY = f"trades/year={TODAY.strftime('%Y')}/month={TODAY.strftime('%m')}/day={TODAY.strftime('%d')}/trades_{TODAY.strftime('%Y%m%d')}.json"
SILVER_PATH = "data/silver/"

s3 = boto3.client("s3", region_name="us-east-1")

def read_bronze():
    """Downloads raw JSON from S3 Bronze and loads into pandas."""
    print(f"📖 Reading Bronze from s3://{BRONZE_BUCKET}/{BRONZE_KEY}")
    response = s3.get_object(Bucket=BRONZE_BUCKET, Key=BRONZE_KEY)
    trades = json.loads(response["Body"].read())
    df = pd.DataFrame(trades)
    print(f"📊 Raw record count: {len(df)}")
    return df

def deduplicate(df):
    """Removes duplicate trades based on trade_id."""
    before = len(df)
    df = df.drop_duplicates(subset=["trade_id"])
    after = len(df)
    print(f"🔄 Deduplication: {before} → {after} records ({before - after} duplicates removed)")
    return df

def handle_nulls(df):
    """Fills missing values with business defaults."""
    df["fraud_score"]  = df["fraud_score"].fillna(0)
    df["broker"]       = df["broker"].fillna("UNKNOWN")
    df["currency"]     = df["currency"].fillna("USD")
    df["fraud_flag"]   = df["fraud_flag"].fillna(False)
    print("✅ Null handling complete")
    return df

def cast_and_standardize(df):
    """Standardizes data types and formats."""
    df["execution_time"]  = pd.to_datetime(df["execution_time"])
    df["settlement_date"] = pd.to_datetime(df["settlement_date"])
    df["shares"]          = df["shares"].astype(int)
    df["processed_at"]    = datetime.now()
    df["pipeline_version"] = "1.0"
    print("✅ Type casting complete")
    return df

def add_risk_category(df):
    """Adds human readable risk category."""
    df["risk_category"] = pd.cut(
        df["fraud_score"],
        bins=[-1, 39, 74, 100],
        labels=["LOW", "MEDIUM", "HIGH"]
    )
    print("✅ Risk category enrichment complete")
    return df

def write_silver(df):
    """Saves cleaned data locally and uploads to S3 Silver."""
    os.makedirs(SILVER_PATH, exist_ok=True)
    filename = f"trades_silver_{TODAY.strftime('%Y%m%d')}.parquet"
    local_path = f"{SILVER_PATH}{filename}"

    # Save as Parquet
    df.to_parquet(local_path, index=False)
    print(f"💾 Saved locally: {local_path}")

    # Upload to S3 Silver
    s3_key = f"trades/cleaned/{filename}"
    s3.upload_file(local_path, SILVER_BUCKET, s3_key)
    print(f"✅ Uploaded to s3://{SILVER_BUCKET}/{s3_key}")
    print(f"✅ Final record count: {len(df)}")

def run_pipeline():
    """Runs all Silver cleaning steps in order."""
    print("🚀 Starting Silver cleaning job")
    print("=" * 50)

    df = read_bronze()
    df = deduplicate(df)
    df = handle_nulls(df)
    df = cast_and_standardize(df)
    df = add_risk_category(df)
    write_silver(df)

    print("=" * 50)
    print("✅ Silver cleaning job complete")

if __name__ == "__main__":
    run_pipeline()