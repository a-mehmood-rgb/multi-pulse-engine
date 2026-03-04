import asyncio
import os
import random
from curl_cffi import requests

# CONFIG
FP_EMAIL = os.getenv("FP_EMAIL")
FP_API_KEY = os.getenv("FP_API_KEY")
USER_PERSONAS = ["chrome", "safari", "edge"]

# 2026 Priority List
CURRENCIES = ["TRX", "SOL", "DOGE", "LTC", "BTC", "USDT", "DGB", "DASH", "ZEC"]

async def get_targets():
    """Aggressively scans all currencies. Standard text only to avoid Windows errors."""
    all_targets = []
    print("--- STARTING GLOBAL NETWORK SCAN ---")
    
    for coin in CURRENCIES:
        if len(all_targets) >= 500:
            break
            
        try:
            print(f"Checking {coin} list...")
            url = f"https://faucetpay.io/api/v1/faucetlist?api_key={FP_API_KEY}&currency={coin}"
            response = await asyncio.to_thread(requests.get, url, impersonate="chrome", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == 200:
                    faucets = data.get("faucets", [])
                    # Health check: Only skip dead sites (Health < 20)
                    active = [f["url"] for f in faucets if int(f.get("health", 0)) > 20]
                    print(f"Added {len(active)} sites from {coin}.")
                    all_targets.extend(active)
        except Exception as e:
            print(f"Skipping {coin} due to connection issue.")
            
    unique_targets = list(dict.fromkeys(all_targets))
    return unique_targets[:500]

async def stealth_claim(url, semaphore):
    """Executes the claim using stealth protocols."""
    async with semaphore:
        try:
            browser = random.choice(USER_PERSONAS)
            response = await asyncio.to_thread(
                requests.post,
                url,
                data={'address': FP_EMAIL, 'api_key': FP_API_KEY},
                impersonate=browser,
                timeout=12
            )
            if response.status_code == 200:
                print(f"SUCCESS: Payment request sent to {url}")
                return True
        except:
            pass
        return False

async def main():
    if not FP_EMAIL or not FP_API_KEY:
        print("ERROR: Missing Secrets (FP_EMAIL or FP_API_KEY)")
        return

    targets = await get_targets()
    
    if not targets:
        print("CRITICAL: No targets found. Retrying in 15 minutes.")
        return

    print(f"ENGINE ONLINE: Processing {len(targets)} active sites.")

    sem = asyncio.Semaphore(50)
    tasks = [stealth_claim(url, sem) for url in targets]
    await asyncio.gather(*tasks)
    print("--- CYCLE COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(main())
