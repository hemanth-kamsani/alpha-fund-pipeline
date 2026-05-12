import pandas as pd
import boto3
import json
from datetime import datetime

# ── Configuration ──────────────────────────────────────────
BRONZE_BUCKET = "alpha-fund-bronze"
TODAY = datetime.now()
BRONZE_KEY = (
    f"trades/year={TODAY.strftime('%Y')}/"
    f"month={TODAY.strftime('%m')}/"
    f"day={TODAY.strftime('%d')}/"
    f"trades_{TODAY.strftime('%Y%m%d')}.json"
)

VALID_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
    "JPM", "BAC", "GS", "MS", "WFC",
    "JNJ", "PFE", "UNH", "CVS", "ABT"
]

REQUIRED_COLUMNS = [
    "trade_id", "fund_id", "ticker", "action",
    "shares", "price_per_share", "total_value",
    "trader_id", "execution_time", "settlement_date",
    "fraud_flag", "fraud_score", "currency"
]

def load_bronze_from_s3():
    """Downloads Bronze file from S3 into pandas DataFrame."""
    print(f"📖 Loading Bronze from s3://{BRONZE_BUCKET}/{BRONZE_KEY}")
    s3 = boto3.client("s3", region_name="us-east-1")
    response = s3.get_object(Bucket=BRONZE_BUCKET, Key=BRONZE_KEY)
    trades = json.loads(response["Body"].read())
    df = pd.DataFrame(trades)
    print(f"📊 Loaded {len(df)} records")
    return df

def run_quality_checks(df):
    """Runs all quality checks. Returns True if all pass."""
    print("\n🔍 Running quality checks...")
    print("=" * 50)

    checks = []

    def check(name, passed, details=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} — {name} {details}")
        checks.append(passed)

    # 1. Required columns exist
    for col in REQUIRED_COLUMNS:
        check(f"Column exists [{col}]", col in df.columns)

    # 2. trade_id not null
    check("trade_id not null",
          df["trade_id"].notna().all())

    # 3. trade_id unique
    check("trade_id unique",
          df["trade_id"].nunique() == len(df),
          f"({df['trade_id'].nunique()} unique / {len(df)} total)")

    # 4. ticker in approved list
    invalid_tickers = df[~df["ticker"].isin(VALID_TICKERS)]["ticker"].unique()
    check("ticker in approved list",
          len(invalid_tickers) == 0,
          f"(invalid: {invalid_tickers})" if len(invalid_tickers) > 0 else "")

    # 5. action is BUY or SELL only
    invalid_actions = df[~df["action"].isin(["BUY", "SELL"])]["action"].unique()
    check("action is BUY or SELL",
          len(invalid_actions) == 0)

    # 6. price_per_share positive
    check("price_per_share > 0",
          (df["price_per_share"] > 0).all())

    # 7. shares positive integer
    check("shares >= 1",
          (df["shares"] >= 1).all())

    # 8. fraud_score between 0 and 100
    check("fraud_score between 0-100",
          df["fraud_score"].between(0, 100).all())

    # 9. total_value not null
    check("total_value not null",
          df["total_value"].notna().all())

    # 10. execution_time not null
    check("execution_time not null",
          df["execution_time"].notna().all())

    print("=" * 50)
    all_passed = all(checks)

    if all_passed:
        print(f"✅ ALL {len(checks)} QUALITY CHECKS PASSED — Pipeline continues")
    else:
        failed = checks.count(False)
        print(f"❌ {failed} QUALITY CHECKS FAILED — Pipeline stopped")
        print("❌ Fix data issues before running Silver job")

    return all_passed

if __name__ == "__main__":
    df = load_bronze_from_s3()
    passed = run_quality_checks(df)
    if not passed:
        exit(1)