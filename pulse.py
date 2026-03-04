import asyncio
import os
import random
from curl_cffi import requests

# CONFIG
FP_EMAIL = os.getenv("FP_EMAIL")
FP_API_KEY = os.getenv("FP_API_KEY")
USER_PERSONAS = ["chrome", "safari", "edge"]

# 2026 Priority List: TRX and SOL are currently the most active for bots
CURRENCIES = ["TRX", "SOL", "DOGE", "LTC", "BTC", "USDT", "DGB", "DASH", "ZEC"]

async def get_targets():
    """Aggressively scans all currencies until 500 active sites are found."""
    all_targets = []
    print("--- 🚀 Starting Global Network Scan ---")
    
    for coin in CURRENCIES:
        if len(all_targets) >= 500:
            break
            
        try:
            print(f"Checking {coin} list...")
            url = f"https://faucetpay.io/api/v1/faucetlist?api_key={FP_API_KEY}&currency={coin}"
            # Impersonating a browser prevents the API from rate-limiting the bot
            response = await asyncio.to_thread(requests.get, url, impersonate="chrome", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == 200:
                    faucets = data.get("faucets", [])
                    # Health check: Only skip the 'dead' sites (Health < 20)
                    active = [f["url"] for f in faucets if int(f.get("health", 0)) > 20]
                    print(f"Added {len(active)} sites from {coin}.")
                    all_targets.extend(active)
        except Exception as e:
            print(f"Skipping {coin} due to connection lag.")
            
    # Remove any duplicates and return the top 500
    unique_targets = list(dict.fromkeys(all_targets))
    return unique_targets[:500]

async def stealth_claim(url, semaphore):
    """Executes the claim using 2026 stealth protocols."""
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
                print(f"Success: Sent payment request to {url}")
                return True
        except:
            pass
        return False

async def main():
    if not FP_EMAIL or not FP_API_KEY:
        print("Error: Missing Secrets (FP_EMAIL or FP_API_KEY)")
        return

    targets = await get_targets()
    
    if not targets:
        print("Critical: The entire network is quiet. Will retry in 15 minutes.")
        return

    print(f"Engine Online: Processing {len(targets)} active sites.")

    # Process 50 sites at a time to maximize speed without being banned
    sem = asyncio.Semaphore(50)
    tasks = [stealth_claim(url, sem) for url in targets]
    await asyncio.gather(*tasks)
    print("--- Cycle Complete: Check your FaucetPay Wallet ---")

if __name__ == "__main__":
    asyncio.run(main())
