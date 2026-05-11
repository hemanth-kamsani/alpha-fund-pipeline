import boto3
import json
import os
from datetime import datetime

# S3 configuration
BRONZE_BUCKET = "alpha-fund-bronze"
s3_client = boto3.client("s3", region_name="us-east-1")

def upload_to_bronze(local_file_path, trade_date=None):
    """
    Uploads a local JSON file to S3 Bronze bucket
    using date-partitioned folder structure.
    """
    if trade_date is None:
        trade_date = datetime.now()

    # Date partitioned S3 path — same pattern real companies use
    s3_key = (
        f"trades/"
        f"year={trade_date.strftime('%Y')}/"
        f"month={trade_date.strftime('%m')}/"
        f"day={trade_date.strftime('%d')}/"
        f"{os.path.basename(local_file_path)}"
    )

    print(f"⬆️  Uploading {local_file_path} to s3://{BRONZE_BUCKET}/{s3_key}")

    s3_client.upload_file(
        Filename=local_file_path,
        Bucket=BRONZE_BUCKET,
        Key=s3_key
    )

    print(f"✅ Upload complete")
    print(f"✅ S3 path: s3://{BRONZE_BUCKET}/{s3_key}")

    return s3_key

if __name__ == "__main__":
    # Find today's generated file
    today = datetime.now()
    filename = f"data/raw/trades_{today.strftime('%Y%m%d')}.json"

    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        print("Run src/generator/run_generator.py first")
    else:
        upload_to_bronze(filename, today)