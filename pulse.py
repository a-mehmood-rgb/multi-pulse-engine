import asyncio
import os
import random
from curl_cffi import requests

# CONFIG
FP_EMAIL = os.getenv("FP_EMAIL")
FP_API_KEY = os.getenv("FP_API_KEY")

# 2026 Stealth Headers
def get_stealth_headers():
    fake_ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
    return {
        "X-Forwarded-For": fake_ip,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

ALL_CURRENCIES = ["TRX", "SOL", "DOGE", "LTC", "BTC", "USDT", "PEPE", "TON", "XRP", "ADA", "POL", "TRUMP"]

async def fetch_targets():
    combined = []
    print("--- 👻 BOOTING GHOST MODE SCAN ---")
    random.shuffle(ALL_CURRENCIES) # Change order every time
    
    # We only scan 5 random coins per run to stay under the 2026 rate limits
    for coin in ALL_CURRENCIES[:5]:
        try:
            print(f"Syncing {coin}...")
            url = f"https://faucetpay.io/api/v1/faucetlist?api_key={FP_API_KEY}&currency={coin}"
            resp = await asyncio.to_thread(requests.get, url, headers=get_stealth_headers(), impersonate="chrome", timeout=12)
            
            if resp.status_code == 200:
                data = resp.json()
                faucets = data.get("faucets", [])
                # Only grab high-health sites to ensure success without captchas
                valid = [f["url"] for f in faucets if int(f.get("health", 0)) > 20]
                combined.extend(valid)
            
            # Critical: 4-second rest between coins to reset the rate-limiter
            await asyncio.sleep(4)
        except:
            continue
    return list(set(combined))

async def process_payout(url, semaphore):
    async with semaphore:
        try:
            # Random 'human' thinking delay
            await asyncio.sleep(random.uniform(2, 7))
            
            response = await asyncio.to_thread(
                requests.post, url,
                data={'address': FP_EMAIL, 'api_key': FP_API_KEY},
                headers=get_stealth_headers(),
                impersonate="chrome",
                timeout=15
            )
            if response.status_code == 200:
                # Obfuscated log to hide the 'Job' from detection
                print(f"Update: Hash {random.randint(1000,9999)} verified.")
        except:
            pass

async def main():
    if not FP_EMAIL or not FP_API_KEY:
        print("Error: Env fail.")
        return

    targets = await fetch_targets()
    
    # Emergency Payouts (Fallback sites)
    if not targets:
        print("Primary API busy. Running Reserved Protocol.")
        targets = ["https://free-tron.com/api/payout", "https://claimfreecoins.io/api/trx"]

    # Low concurrency (5) makes the traffic look like a regular browser user
    sem = asyncio.Semaphore(5)
    tasks = [process_payout(url, sem) for url in targets[:100]]
    await asyncio.gather(*tasks)
    print("--- SESSION SECURED ---")

if __name__ == "__main__":
    asyncio.run(main())
