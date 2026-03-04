import asyncio
import os
import random
from curl_cffi import requests # The secret weapon for 2026

# CONFIG
FP_EMAIL = os.getenv("FP_EMAIL")
FP_API_KEY = os.getenv("FP_API_KEY")

# A pool of personas to rotate
USER_PERSONAS = [
    {"browser": "chrome", "platform": "windows"},
    {"browser": "safari", "platform": "ios"},
    {"browser": "chrome", "platform": "android"}
]

async def stealth_claim(url, semaphore):
    async with semaphore:
        try:
            # Pick a random persona for THIS specific site
            persona = random.choice(USER_PERSONAS)
            
            # This 'impersonate' flag is the magic: 
            # It mimics the TLS/JA3 fingerprint of a real browser.
            response = await asyncio.to_thread(
                requests.post, 
                url, 
                data={'address': FP_EMAIL, 'api_key': FP_API_KEY},
                impersonate=persona["browser"], # Mimics Chrome/Safari TLS
                timeout=15
            )

            if response.status_code == 200:
                print(f"✅ Success: Site saw us as a unique {persona['browser']} user.")
                return True
        except Exception:
            pass
        return False

async def main():
    # Fetch list first (same as before)
    # ... (code to get 'targets' from FaucetPay API) ...
    
    # Process 500 sites with 50 parallel 'Unique' threads
    sem = asyncio.Semaphore(50)
    tasks = [stealth_claim(url, sem) for url in targets[:500]]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
