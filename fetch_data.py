import sqlite3
import requests
import pandas as pd
from datetime import datetime

# CoinGecko free API endpoint (No API key needed)
API_URL = "https://api.coingecko.com/api/v3/coins/markets"
PARAMS = {
    "vs_currency": "usd",
    "ids": "bitcoin,ethereum,cardano,solana,ripple",
    "order": "market_cap_desc",
    "per_page": 5,
    "page": 1,
    "sparkline": "false"
}

def fetch_market_data():
    """Fetch live crypto market metrics via REST API."""
    try:
        response = requests.get(API_URL, params=PARAMS, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print("[Warning] API Rate limit reached. Waiting for next cycle.")
            return None
        else:
            print(f"[Error] API returned status code {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"[Error] Network issue: {e}")
        return None

def save_to_database(data):
    """Parse JSON with Pandas and append records into SQLite DB."""
    if not data:
        return

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    records = []

    for item in data:
        records.append({
            "timestamp": current_time,
            "symbol": item["symbol"].upper(),
            "name": item["name"],
            "price_usd": item["current_price"],
            "market_cap": item["market_cap"],
            "volume_24h": item["total_volume"],
            "change_24h": item["price_change_percentage_24h"]
        })

    df = pd.DataFrame(records)

    # Save to SQLite database
    conn = sqlite3.connect("crypto.db")
    df.to_sql("crypto_history", conn, if_exists="append", index=False)
    conn.close()
    
    print(f"[{current_time}] Successfully stored {len(records)} asset snapshots in crypto.db")

if __name__ == "__main__":
    raw_data = fetch_market_data()
    save_to_database(raw_data)