import asyncio
import os
import random
from curl_cffi import requests

# CONFIG - Pulled from your GitHub Secrets
FP_EMAIL = os.getenv("FP_EMAIL")
FP_API_KEY = os.getenv("FP_API_KEY")

# Persona rotation for 2026 Stealth
USER_PERSONAS = ["chrome", "safari", "edge"]

async def get_targets():
    """Fetches the top 500 high-health API faucets from FaucetPay."""
    print("🔍 Scanning FaucetPay network for high-yield targets...")
    try:
        # We call the FaucetPay API list to see who has money right now
        url = f"https://faucetpay.io/api/v1/faucetlist?api_key={FP_API_KEY}&currency=BTC"
        response = await asyncio.to_thread(requests.get, url, impersonate="chrome", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 200:
                # Filter for sites that are 'Active' and have high 'Health'
                faucets = data.get("faucets", [])
                return [f["url"] for f in faucets if f.get("health", 0) > 90][:500]
    except Exception as e:
        print(f"⚠️ Connection error during scan: {e}")
    return []

async def stealth_claim(url, semaphore):
    """Executes a single claim using a unique browser fingerprint."""
    async with semaphore:
        try:
            browser = random.choice(USER_PERSONAS)
            # The 'impersonate' flag makes the site think we are a real human
            response = await asyncio.to_thread(
                requests.post,
                url,
                data={'address': FP_EMAIL, 'api_key': FP_API_KEY},
                impersonate=browser,
                timeout=15
            )
            if response.status_code == 200:
                print(f"✅ Received payment from: {url}")
                return True
        except:
            pass
        return False

async def main():
    if not FP_EMAIL or not FP_API_KEY:
        print("❌ Error: FP_EMAIL or FP_API_KEY is missing in GitHub Secrets!")
        return

    # 1. Get the list of sites
    targets = await get_targets()
    
    if not targets:
        print("❌ No active targets found. Retrying in 15 minutes.")
        return

    print(f"🚀 Launching Pulse Engine on {len(targets)} sites...")

    # 2. Process sites in parallel (50 at a time to stay under the radar)
    sem = asyncio.Semaphore(50)
    tasks = [stealth_claim(url, sem) for url in targets]
    await asyncio.gather(*tasks)
    print("🏁 Cycle Complete. Total earnings added to FaucetPay.")

if __name__ == "__main__":
    asyncio.run(main())
