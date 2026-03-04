import asyncio
import os
import random
from curl_cffi import requests

# CONFIG - Pulled from GitHub Secrets
FP_EMAIL = os.getenv("FP_EMAIL")
FP_API_KEY = os.getenv("FP_API_KEY")
USER_PERSONAS = ["chrome", "safari", "edge"]

# FULL WALLET SYNC: Matches your Dashboard exactly
ALL_CURRENCIES = [
    "BTC", "ETH", "DOGE", "LTC", "BCH", "DASH", "DGB", "TRX", 
    "USDT", "FEY", "ZEC", "BNB", "SOL", "XRP", "POL", "ADA", 
    "TON", "XLM", "USDC", "XMR", "TARA", "TRUMP", "PEPE", "FLT"
]

async def fetch_all_targets():
    """Scans all 24 currencies to maximize target list."""
    combined_list = []
    print("--- STARTING FULL WALLET SYNC SCAN ---")
    
    for coin in ALL_CURRENCIES:
        try:
            # Short timeout to keep the scan moving quickly
            url = f"https://faucetpay.io/api/v1/faucetlist?api_key={FP_API_KEY}&currency={coin}"
            resp = await asyncio.to_thread(requests.get, url, impersonate="chrome", timeout=7)
            
            if resp.status_code == 200:
                data = resp.json()
                faucets = data.get("faucets", [])
                # Filter: Grab any site that has any funds left (health > 0)
                active = [f["url"] for f in faucets if int(f.get("health", 0)) > 0]
                if active:
                    print(f"FOUND: {len(active)} active sites for {coin}")
                    combined_list.extend(active)
        except:
            continue
            
    # Clean the list (remove duplicates)
    unique_targets = list(dict.fromkeys(combined_list))
    print(f"TOTAL UNIQUE SITES DISCOVERED: {len(unique_targets)}")
    return unique_targets

async def claim_engine(url, semaphore):
    """The stealth claiming logic."""
    async with semaphore:
        try:
            # Human jitter to avoid instant bot flags
            await asyncio.sleep(random.uniform(0.5, 2))
            
            browser = random.choice(USER_PERSONAS)
            response = await asyncio.to_thread(
                requests.post,
                url,
                data={'address': FP_EMAIL, 'api_key': FP_API_KEY},
                impersonate=browser,
                timeout=12
            )
            if response.status_code == 200:
                print(f"SUCCESS: Claimed from {url}")
                return True
        except:
            pass
        return False

async def main():
    if not FP_EMAIL or not FP_API_KEY:
        print("ERROR: Missing FP_EMAIL or FP_API_KEY in GitHub Secrets.")
        return

    targets = await fetch_all_targets()
    
    if not targets:
        print("NOTICE: No sites found. The API might be rate-limiting. Waiting...")
        return

    # Process 40 sites at a time to handle the massive 2026 list
    sem = asyncio.Semaphore(40)
    print(f"LAUNCHING ENGINE: Processing {len(targets)} sites...")
    
    tasks = [claim_engine(url, sem) for url in targets]
    await asyncio.gather(*tasks)
    print("--- FULL ENGINE CYCLE COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(main())
