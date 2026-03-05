import asyncio, os, time, random
from curl_cffi import requests

# CONFIG: Set these in GitHub Secrets
WALLET = os.getenv("WALLET_ADDR")

# 2026 High-Trust Targets (Optimized for $3/day scale)
SITES = [
    {"url": "https://faucetearner.org", "api": "/api.php?act=faucet"},
    {"url": "https://instant-tron.com", "api": "/api/claim"},
    {"url": "https://trx-king.xyz", "api": "/api/payout"},
    {"url": "https://free-tron.io", "api": "/api/claim"},
    {"url": "https://tron-express.io", "api": "/api/payout"}
]

async def ghost_claim(site, semaphore):
    domain = site['url'].split('/')[2]
    async with semaphore:
        # Create a session to handle cookies automatically
        async with requests.AsyncSession(impersonate="chrome120") as s:
            try:
                # 1. 'Visit' the home page to get a Session ID (Bypasses basic bot blocks)
                await s.get(site['url'], timeout=15)
                await asyncio.sleep(random.uniform(3, 6))

                # 2. Prepare the payout request with real headers
                headers = {
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": site['url'],
                    "Origin": site['url']
                }
                payload = {'address': WALLET, 'currency': 'TRX'}
                
                # 3. Fire the actual claim
                r = await s.post(f"{site['url']}{site['api']}", data=payload, headers=headers, timeout=15)

                if "success" in r.text.lower() or "earned" in r.text.lower():
                    print(f"✅ [{time.strftime('%H:%M')}] {domain}: Success!")
                    return True
                else:
                    # If it fails, we show the first 40 characters of the error
                    print(f"❌ [{time.strftime('%H:%M')}] {domain}: {r.text[:40].strip()}")
            except Exception:
                print(f"⚠️ [{time.strftime('%H:%M')}] {domain}: Connection Refused")
    return False

async def main():
    if not WALLET:
        print("CRITICAL: WALLET_ADDR secret is missing!")
        return

    print(f"--- 🚀 GHOST ENGINE v12.1 | TARGET: {WALLET[:8]} ---")
    sem = asyncio.Semaphore(2) # Keep CPU at 0% for GitHub safety
    
    # Run one full cycle of all sites
    tasks = [ghost_claim(s, sem) for s in SITES]
    results = await asyncio.gather(*tasks)
    
    success_count = sum(1 for r in results if r)
    print(f"--- 🏁 CYCLE FINISHED | PAYOUTS: {success_count} ---")

if __name__ == "__main__":
    asyncio.run(main())
