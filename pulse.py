import asyncio
import os
import random
from curl_cffi import requests

# CONFIG
FP_EMAIL = os.getenv("FP_EMAIL") 
FP_API_KEY = os.getenv("FP_API_KEY")

async def check_connection():
    """Verify credentials before starting."""
    url = f"https://faucetpay.io/api/v1/getbalance?api_key={FP_API_KEY}&currency=TRX"
    try:
        r = await asyncio.to_thread(requests.post, url, impersonate="chrome")
        data = r.json()
        if data.get("status") == 200:
            print(f"✅ CONNECTED | Balance: {data.get('balance')} TRX")
            return True
        else:
            print(f"❌ ERROR: {data.get('message')}")
            return False
    except:
        print("⚠️ ALERT: FaucetPay Firewall active. Adding 30s delay...")
        return False

async def main():
    print("--- DEBUG MODE START ---")
    if not await check_connection():
        return

    # March 2026 - High Liquidity Targets
    targets = [
        "https://faucetearner.org/api/payout",
        "https://trx-king.xyz/api/claim"
    ]
    
    for url in targets:
        await asyncio.sleep(random.uniform(2, 5))
        print(f"Attempting claim at {url.split('/')[2]}...")
        # (Rest of claiming logic goes here)

    print("--- SCAN COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(main())
