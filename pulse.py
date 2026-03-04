import asyncio
import os
import random
from curl_cffi import requests

# CONFIG
FP_EMAIL = os.getenv("FP_EMAIL")
FP_API_KEY = os.getenv("FP_API_KEY")

# 2026 STEALTH PROFILES (Windows, Ubuntu, and Safari)
DEVICE_PROFILES = [
    "chrome110", "chrome120", "edge101", 
    "safari15_5", "safari17_0", "chrome110_android"
]

async def process_payout(url, semaphore):
    # The Semaphore limits parallel tasks so you don't crash the Runner
    async with semaphore:
        try:
            # Random 'Thinking' time between 2-6 seconds
            await asyncio.sleep(random.uniform(2, 6))
            
            # Select a random OS profile for this specific site
            persona = random.choice(DEVICE_PROFILES)
            
            # FAST PARALLEL REQUEST
            response = await asyncio.to_thread(
                requests.post, url,
                data={'address': FP_EMAIL, 'api_key': FP_API_KEY},
                impersonate=persona, # This mimics Windows/Ubuntu/Mac fingerprints
                timeout=15
            )
            
            site = url.split('/')[2]
            if response.status_code == 200 and "success" in response.text.lower():
                print(f"✅ [{persona}] Success at {site}")
            else:
                print(f"⚠️ [{persona}] Busy/Empty at {site}")
        except:
            pass

async def main():
    print("--- 🚀 STARTING PARALLEL GHOST ENGINE ---")
    
    # 1. Fetch targets (as we did before)
    targets = await fetch_targets() # Uses your existing target fetcher
    
    # 2. RUN IN PARALLEL (Semaphore 8 = 8 sites at once)
    # 8 is the 'Sweet Spot' for 2026. Fast but doesn't trigger DDOS filters.
    sem = asyncio.Semaphore(8)
    
    tasks = [process_payout(url, sem) for url in targets[:100]]
    
    # This line triggers all tasks at the same time
    await asyncio.gather(*tasks)
    
    print("--- 🏁 BATCH COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(main())
