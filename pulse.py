import asyncio
import os
import random
from curl_cffi import requests

# CONFIG
FP_EMAIL = os.getenv("FP_EMAIL")
FP_API_KEY = os.getenv("FP_API_KEY")
USER_PERSONAS = ["chrome", "safari", "edge"]
# 2026 High-yield coins
CURRENCIES = ["BTC", "TRX", "SOL", "LTC", "DOGE"]

async def get_targets():
    """Scans multiple currencies to find the best targets."""
    all_targets = []
    print("--- Scanning FaucetPay Network ---")
    
    for coin in CURRENCIES:
        try:
            url = f"https://faucetpay.io/api/v1/faucetlist?api_key={FP_API_KEY}&currency={coin}"
            response = await asyncio.to_thread(requests.get, url, impersonate="chrome", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == 200:
                    faucets = data.get("faucets", [])
                    # Lowered health bar to 70% to catch more active sites
                    coin_targets = [f["url"] for f in faucets if int(f.get("health", 0)) > 70]
                    print(f"Found {len(coin_targets)} active {coin} targets.")
                    all_targets.extend(coin_targets)
        except Exception as e:
            print(f"Skip {coin}: {e}")
            
    return list(set(all_targets))[:500] # Remove duplicates and cap at 500

async def stealth_claim(url, semaphore):
    """Executes a single claim."""
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
                print(f"Success: Payment from {url}")
                return True
        except:
            pass
        return False

async def main():
    if not FP_EMAIL or not FP_API_KEY:
        print("Error: Missing Secrets!")
        return

    targets = await get_targets()
    
    if not targets:
        print("No targets found across all coins. FaucetPay API might be rate-limiting. Waiting...")
        return

    print(f"Launching Pulse Engine on {len(targets)} total sites...")
    sem = asyncio.Semaphore(50)
    tasks = [stealth_claim(url, sem) for url in targets]
    await asyncio.gather(*tasks)
    print("Cycle Complete.")

if __name__ == "__main__":
    asyncio.run(main())
