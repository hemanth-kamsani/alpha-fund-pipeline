import json
import os
from datetime import datetime
from trade_generator import generate_trades

# Create output directory if it doesn't exist
output_dir = "data/raw"
os.makedirs(output_dir, exist_ok=True)

# Generate today's trades
today = datetime.now()
trades = generate_trades(num_trades=100, trade_date=today)

# Save to JSON file
filename = f"{output_dir}/trades_{today.strftime('%Y%m%d')}.json"
with open(filename, "w") as f:
    json.dump(trades, f, indent=2)

print(f"✅ Generated {len(trades)} trades")
print(f"✅ Saved to {filename}")
print(f"✅ Sample trade:")
print(json.dumps(trades[0], indent=2))