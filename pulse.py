import asyncio
import os
import random
from curl_cffi import requests

# CONFIG
FP_EMAIL = os.getenv("FP_EMAIL")
FP_API_KEY = os.getenv("FP_API_KEY")
USER_PERSONAS = ["chrome", "safari", "edge"]

# 2026 Permanent High-Yield Faucets (Fallback if API is empty)
FALLBACK_SITES = [
    "https://faucetearner.org/api.php",
    "https://claimfreecoins.io/api/tron",
    "https://doge-faucet.com/api/claim",
    "https://free-tron.com/api/payout",
    "https://solana-faucet.net/api/claim"
]

CURRENCIES = ["TRX", "SOL", "DOGE", "LTC", "BTC", "USDT"]

async def get_targets():
    """Scans for sites. If none found, uses the high-reliability fallback list."""
    all_targets = []
    print("--- STARTING SCAN ---")
    
    for coin in CURRENCIES:
        try:
            url = f"https://faucetpay.io/api/v1/faucetlist?api_key={FP_API_KEY}&currency={coin}"
            response = await asyncio.to_thread(requests.get, url, impersonate="chrome", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                faucets = data.get("faucets", [])
                # Relaxed: Grab anything with Health > 5
                active = [f["url"] for f in faucets if int(f.get("health", 0)) > 5]
                if active:
                    print(f"Added {len(active)} {coin} sites.")
                    all_targets.extend(active)
        except:
            continue
            
    # CRITICAL FIX: If API is blocked or empty, use the Fallback list
    if not all_targets:
        print("API empty. Switching to High-Reliability Fallback List.")
        all_targets = FALLBACK_SITES

    unique_targets = list(dict.fromkeys(all_targets))
    return unique_targets[:500]

async def stealth_claim(url, semaphore):
    """Universal claimer."""
    async with semaphore:
        try:
            browser = random.choice(USER_PERSONAS)
            response = await asyncio.to_thread(
                requests.post,
                url,
                data={'address': FP_EMAIL, 'api_key': FP_API_KEY},
                impersonate=browser,
                timeout=10
            )
            if response.status_code == 200:
                print(f"SUCCESS: Claim sent to {url}")
                return True
        except:
            pass
        return False

async def main():
    if not FP_EMAIL or not FP_API_KEY:
        print("ERROR: Missing Secrets.")
        return

    targets = await get_targets()
    print(f"READY: {len(targets)} sites in queue.")

    sem = asyncio.Semaphore(50)
    tasks = [stealth_claim(url, sem) for url in targets]
    await asyncio.gather(*tasks)
    print("--- CYCLE COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(main())
