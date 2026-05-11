import json
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# List of stocks the Alpha Growth Fund trades
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", 
           "JPM", "BAC", "GS", "MS", "WFC",
           "JNJ", "PFE", "UNH", "CVS", "ABT"]

BROKERS = ["Goldman Sachs", "Morgan Stanley", 
           "JP Morgan", "Merrill Lynch", "Citigroup"]

FUND_ID = "AGF-001"
FUND_NAME = "Alpha Growth Fund"

def generate_trade(trade_date=None):
    """
    Generates one realistic stock trade record.
    Returns a dictionary representing one trade.
    """
    if trade_date is None:
        trade_date = datetime.now()

    # Market hours — 9:30 AM to 4:00 PM
    market_open  = trade_date.replace(hour=9,  minute=30, second=0)
    market_close = trade_date.replace(hour=16, minute=0,  second=0)

    # Random execution time within market hours
    seconds_in_day = int((market_close - market_open).total_seconds())
    execution_time = market_open + timedelta(seconds=random.randint(0, seconds_in_day))

    # Trade details
    ticker         = random.choice(TICKERS)
    action         = random.choice(["BUY", "SELL"])
    shares         = random.randint(100, 50000)
    price          = round(random.uniform(10.00, 2000.00), 2)
    total_value    = round(shares * price, 2)

    # Fraud logic — trades over $1M get a higher fraud score
    fraud_flag     = total_value > 1_000_000
    fraud_score    = random.randint(75, 99) if fraud_flag else random.randint(0, 40)

    return {
        "trade_id"        : str(uuid.uuid4())[:12].upper(),
        "fund_id"         : FUND_ID,
        "fund_name"       : FUND_NAME,
        "ticker"          : ticker,
        "action"          : action,
        "shares"          : shares,
        "price_per_share" : price,
        "total_value"     : total_value,
        "trader_id"       : f"TRD-{random.randint(1000, 9999)}",
        "broker"          : random.choice(BROKERS),
        "execution_time"  : execution_time.isoformat(),
        "settlement_date" : (execution_time + timedelta(days=2)).strftime("%Y-%m-%d"),
        "fraud_flag"      : fraud_flag,
        "fraud_score"     : fraud_score,
        "currency"        : "USD"
    }

def generate_trades(num_trades=100, trade_date=None):
    """
    Generates multiple trade records.
    Returns a list of trade dictionaries.
    """
    trades = []
    for _ in range(num_trades):
        trades.append(generate_trade(trade_date))
    return trades