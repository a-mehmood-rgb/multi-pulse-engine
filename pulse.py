import asyncio
import os
import random
from curl_cffi import requests

# CONFIG
FP_EMAIL = os.getenv("FP_EMAIL")
FP_API_KEY = os.getenv("FP_API_KEY")
USER_PERSONAS = ["chrome", "safari", "edge"]

# FULL 2026 COIN LIST
ALL_CURRENCIES = [
    "BTC", "ETH", "DOGE", "LTC", "BCH", "DASH", "DGB", "TRX", 
    "USDT", "FEY", "ZEC", "BNB", "SOL", "XRP", "POL", "ADA", 
    "TON", "XLM", "USDC", "XMR", "TARA", "TRUMP", "PEPE", "FLT"
]

async def fetch_all_targets():
    """Fetches sites in small batches to prevent API rate-limiting."""
    combined_list = []
    print("--- INITIATING STEALTH BATCH SCAN ---")
    
    # Shuffle so we don't always hit the same coins first
    random.shuffle(ALL_CURRENCIES)
    
    # Process in batches of 4 coins at a time
    for i in range(0, len(ALL_CURRENCIES), 4):
        batch = ALL_CURRENCIES[i:i+4]
        print(f"Scanning Batch: {', '.join(batch)}...")
        
        for coin in batch:
            try:
                url = f"https://faucetpay.io/api/v1/faucetlist?api_key={FP_API_KEY}&currency={coin}"
                resp = await asyncio.to_thread(requests.get, url, impersonate="chrome", timeout=10)
                
                if resp.status_code == 200:
                    data = resp.json()
                    # Only accept status 200 from the API body itself
                    if data.get("status") == 200:
                        faucets = data.get("faucets", [])
                        active = [f["url"] for f in faucets if int(f.get("health", 0)) > 5]
                        combined_list.extend(active)
                elif resp.status_code == 429:
                    print("Rate limit hit! Cooling down...")
                    await asyncio.sleep(10)
            except:
                continue
        
        # Mandatory 5-second rest between batches
        await asyncio.sleep(5)
            
    unique_targets = list(dict.fromkeys(combined_list))
    
    # Fallback if API is totally blocked
    if not unique_targets:
        print("API returned zero results. Using Emergency Fallback.")
        return ["https://free-tron.com/api/payout", "https://claimfreecoins.io/api/trx"]
        
    print(f"SCAN COMPLETE: Found {len(unique_targets)} sites.")
    return unique_targets[:400] # Cap at 400 for safety

async def claim_engine(url, semaphore):
    """Processes claims with randomized delays to avoid detection."""
    async with semaphore:
        try:
            # Random wait (1-4s) per site
            await asyncio.sleep(random.uniform(1, 4))
            
            browser = random.choice(USER_PERSONAS)
            response = await asyncio.to_thread(
                requests.post, url,
                data={'address': FP_EMAIL, 'api_key': FP_API_KEY},
                impersonate=browser, timeout=12
            )
            if response.status_code == 200:
                print(f"SUCCESS: {url}")
        except:
            pass

async def main():
    if not FP_EMAIL or not FP_API_KEY:
        print("ERROR: Secrets missing.")
        return

    targets = await fetch_all_targets()
    
    # Run the engine (Limit to 20 parallel tasks for maximum stealth)
    sem = asyncio.Semaphore(20)
    tasks = [claim_engine(url, sem) for url in targets]
    await asyncio.gather(*tasks)
    print("--- ENGINE CYCLE COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(main())
