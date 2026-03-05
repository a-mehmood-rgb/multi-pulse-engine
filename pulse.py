import asyncio, os, time, random
from curl_cffi import requests

# CONFIG
API_KEY = os.getenv("FP_API_KEY") 
WALLET_ADDR = os.getenv("WALLET_ADDR")

async def get_active_faucets():
    """Fetches the dynamic faucet list with error handling."""
    # Updated endpoint for 2026
    url = "https://faucetpay.io/api/v1/faucetlist"
    
    try:
        async with requests.AsyncSession(impersonate="chrome120") as s:
            # FaucetPay requires the API key to see the full list
            r = await s.post(url, data={'api_key': API_KEY}, timeout=15)
            
            if r.status_code != 200:
                print(f"Server Error: {r.status_code}")
                return []

            data = r.json()
            # Safety check: ensure 'faucets' key exists and is a list
            faucets = data.get("faucets", [])
            if not faucets:
                print("Notice: API returned an empty list. Check your API Key.")
                return []
                
            # Filter for high health (guaranteed funds)
            return [f for f in faucets if int(f.get('health', 0)) >= 90]
            
    except Exception as e:
        print(f"Connection failed: {e}")
        return []

async def claim_payout(site, semaphore):
    """Attempts a direct API claim."""
    domain = site.get('url', '').split('/')[2] if 'url' in site else "unknown"
    target_api = f"{site['url'].rstrip('/')}/api/payout"
    
    async with semaphore:
        try:
            await asyncio.sleep(random.uniform(1, 4))
            async with requests.AsyncSession(impersonate="chrome120") as s:
                res = await s.post(
                    target_api,
                    data={'address': WALLET_ADDR, 'api_key': API_KEY, 'currency': 'TRX'},
                    timeout=10
                )
                if "success" in res.text.lower():
                    print(f"✅ Success: {domain}")
                    return True
        except:
            pass
    return False

async def main():
    if not API_KEY:
        print("CRITICAL: FP_API_KEY is missing in GitHub Secrets!")
        return

    print("--- 🚀 GHOST ENGINE: DYNAMIC MODE ---")
    
    faucet_list = await get_active_faucets()
    
    # This check prevents the 'NoneType' error
    if not faucet_list:
        print("No active targets found this cycle. Exiting safely.")
        return

    print(f"Discovered {len(faucet_list)} high-health API targets.")

    # Limit to 3 concurrent requests to keep GitHub CPU low
    sem = asyncio.Semaphore(3)
    tasks = [claim_payout(f, sem) for f in faucet_list[:30]] # Test first 30
    
    results = await asyncio.gather(*tasks)
    success_count = sum(1 for r in results if r)
    print(f"--- SESSION ENDED | Payouts: {success_count} ---")

if __name__ == "__main__":
    asyncio.run(main())
