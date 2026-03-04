import asyncio
import os
import random
from curl_cffi import requests

# CONFIG - Ensure these are set in GitHub Secrets
FP_EMAIL = os.getenv("FP_EMAIL")
FP_API_KEY = os.getenv("FP_API_KEY")

# 2026 ANTI-DETECT PROFILES (Windows, Ubuntu, Safari)
OS_PROFILES = ["chrome120", "edge101", "safari17_0", "chrome110_android"]
COINS = ["SOL", "TRX", "DOGE", "LTC", "BTC", "PEPE"]

async def get_dynamic_targets():
    """
    Scans FaucetPay for sites in the 20-55% Health range.
    These are the 'Honest' sites that are currently paying out.
    """
    print("🛰️ Sniping 'Sweet Spot' wallets (20-55% Health)...")
    discovered = []
    
    for coin in COINS:
        try:
            url = f"https://faucetpay.io/api/v1/faucetlist?api_key={FP_API_KEY}&currency={coin}"
            # Use a high-trust persona to fetch the list
            resp = await asyncio.to_thread(requests.get, url, impersonate="chrome120", timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == 200:
                    faucets = data.get("faucets", [])
                    # The Sweet Spot: 20% to 55%
                    valid = [f["url"] for f in faucets if 20 <= int(f.get("health", 0)) <= 55]
                    discovered.extend(valid)
            
            # Tiny delay to avoid API rate limits during discovery
            await asyncio.sleep(1.2)
        except Exception:
            continue
            
    return list(set(discovered))

async def process_payout(url, semaphore):
    """
    Handles the individual claim with Session Mimicry.
    """
    async with semaphore:
        # Sessions are required in 2026 to hold cookies and bypass 403s
        with requests.Session() as s:
            try:
                # 1. Random 'Human' Delay
                await asyncio.sleep(random.uniform(5, 15))
                persona = random.choice(OS_PROFILES)
                
                # 2. Pre-flight Handshake (Visit homepage first)
                base_url = url.split('/api')[0] if '/api' in url else url
                s.get(base_url, impersonate=persona, timeout=10)
                await asyncio.sleep(random.uniform(2, 4))

                # 3. The Payout Request
                payload = {
                    'address': FP_EMAIL, 
                    'api_key': FP_API_KEY
                }
                
                response = s.post(
                    url,
                    data=payload,
                    headers={
                        "Referer": base_url,
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    impersonate=persona, 
                    timeout=15
                )
                
                site = url.split('/')[2]
                if "success" in response.text.lower():
                    print(f"✅ PAID -> {site}")
                    return True
                elif response.status_code == 403:
                    # If this happens often, re-run the action for a new IP
                    print(f"🚫 {site}: IP Blocked")
                else:
                    return False
            except:
                return False

async def main():
    print("--- 🚀 SHADOW PULSE: HIGH-VOLUME SWEET-SPOT MODE ---")
    
    if not FP_EMAIL or not FP_API_KEY:
        print("❌ Error: Missing FP_EMAIL or FP_API_KEY in Secrets.")
        return

    # Step 1: Discover sites currently paying out
    targets = await get_dynamic_targets()
    
    # Step 2: Add 'Immortal' backup sites just in case
    backups = ["https://free-tron.com/api/payout", "https://instant-tokens.com/api/payout"]
    targets = list(set(targets + backups))
    
    random.shuffle(targets)
    
    # Step 3: Execute in Parallel
    # 6 parallel workers is the stealth limit for GitHub Runners
    sem = asyncio.Semaphore(6) 
    print(f"🔥 Engaging {len(targets[:70])} sites...")
    
    results = await asyncio.gather(*[process_payout(u, sem) for u in targets[:70]])
    
    # Summary
    success_count = sum(1 for r in results if r)
    print(f"--- 🏁 SESSION COMPLETE | TOTAL SUCCESS: {success_count} ---")

if __name__ == "__main__":
    asyncio.run(main())
