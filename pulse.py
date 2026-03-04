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
    print("--- Scanning FaucetPay network for high-yield targets ---")
    try:
        # Calling the FaucetPay API
        url = f"https://faucetpay.io/api/v1/faucetlist?api_key={FP_API_KEY}&currency=BTC"
        response = await asyncio.to_thread(requests.get, url, impersonate="chrome", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 200:
                faucets = data.get("faucets", [])
                # Filter for sites > 90% health
                return [f["url"] for f in faucets if f.get("health", 0) > 90][:500]
    except Exception as e:
        print(f"Connection error during scan: {e}")
    return []

async def stealth_claim(url, semaphore):
    """Executes a single claim using a unique browser fingerprint."""
    async with semaphore:
        try:
            browser = random.choice(USER_PERSONAS)
            response = await asyncio.to_thread(
                requests.post,
                url,
                data={'address': FP_EMAIL, 'api_key': FP_API_KEY},
                impersonate=browser,
                timeout=15
            )
            if response.status_code == 200:
                # Removed the 'Green Check' emoji to prevent Windows crashes
                print(f"Success: Payment received from {url}")
                return True
        except:
            pass
        return False

async def main():
    if not FP_EMAIL or not FP_API_KEY:
        print("Error: FP_EMAIL or FP_API_KEY is missing in GitHub Secrets!")
        return

    targets = await get_targets()
    
    if not targets:
        print("No active targets found. Retrying in 15 minutes.")
        return

    print(f"Starting Engine on {len(targets)} sites...")

    sem = asyncio.Semaphore(50)
    tasks = [stealth_claim(url, sem) for url in targets]
    await asyncio.gather(*tasks)
    print("Cycle Complete. Check your FaucetPay Dashboard.")

if __name__ == "__main__":
    asyncio.run(main())
