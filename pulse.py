import asyncio
import os
import random
from curl_cffi import requests

# CONFIG
FP_EMAIL = os.getenv("FP_EMAIL")
FP_API_KEY = os.getenv("FP_API_KEY")

# 2026 STEALTH PROFILES (Mimicking Windows and Ubuntu)
OS_PROFILES = ["chrome110", "edge101", "safari15_5", "chrome120", "safari17_0"]
ALL_CURRENCIES = ["TRX", "SOL", "DOGE", "LTC", "BTC", "USDT", "PEPE", "TON", "XRP", "ADA", "POL"]

async def fetch_targets():
    """Restored function to sync the best-paying sites from FaucetPay."""
    combined = []
    print("--- 👻 SYNCING HIGH-VALUE BATCH ---")
    
    # We rotate through 4 random coins per 16-minute cycle to stay under limits
    random.shuffle(ALL_CURRENCIES)
    for coin in ALL_CURRENCIES[:4]:
        try:
            url = f"https://faucetpay.io/api/v1/faucetlist?api_key={FP_API_KEY}&currency={coin}"
            # Use a fast Ubuntu/Chrome signature to grab the list
            resp = await asyncio.to_thread(requests.get, url, impersonate="chrome110", timeout=12)
            
            if resp.status_code == 200:
                data = resp.json()
                faucets = data.get("faucets", [])
                # Filter for Health > 30 to ensure they actually have money to pay you
                valid = [f["url"] for f in faucets if int(f.get("health", 0)) > 30]
                combined.extend(valid)
            await asyncio.sleep(1.5) # Anti-spam delay
        except:
            continue
    return list(set(combined))

async def process_payout(url, semaphore):
    """Claims crypto using parallel threads and OS spoofing."""
    async with semaphore:
        try:
            # Human-like 'thinking' delay (2-6 seconds)
            await asyncio.sleep(random.uniform(2, 6))
            persona = random.choice(OS_PROFILES)
            
            response = await asyncio.to_thread(
                requests.post, url,
                data={'address': FP_EMAIL, 'api_key': FP_API_KEY},
                impersonate=persona, 
                timeout=12
            )
            
            site = url.split('/')[2]
            if response.status_code == 200 and "success" in response.text.lower():
                print(f"✅ Success [{persona}] -> {site}")
                return True
            return False
        except:
            return False

async def main():
    print("--- 🚀 STARTING PARALLEL GHOST ENGINE ---")
    
    if not FP_EMAIL or not FP_API_KEY:
        print("❌ Error: Missing FP_EMAIL or FP_API_KEY in GitHub Secrets.")
        return

    # Fetch the list (This was the missing piece causing your error!)
    targets = await fetch_targets() 
    
    if not targets:
        print("⚠️ List API busy. Using 2026 Emergency Reserve nodes...")
        targets = ["https://claimfreecoins.io/api/trx", "https://faucet.ovh/api/payout"]

    # 1. ATTEMPT PRIMARY TOP 40 (Batch A)
    sem = asyncio.Semaphore(8) # 8 parallel threads for speed
    print(f"🛰️ Scanning Batch A ({len(targets[:40])} sites)...")
    results = await asyncio.gather(*[process_payout(u, sem) for u in targets[:40]])
    
    # 2. FAILOVER: If success rate is low, do 'Next 40' (Batch B)
    success_count = sum(1 for r in results if r)
    if success_count < 3 and len(targets) > 40:
        print(f"🔄 Low hits ({success_count}). Engaging Batch B (Next 40)...")
        await asyncio.gather(*[process_payout(u, sem) for u in targets[40:80]])
    else:
        print(f"🔥 Batch A completed with {success_count} payouts.")

    print("--- 🏁 SESSION SECURED ---")

if __name__ == "__main__":
    asyncio.run(main())
