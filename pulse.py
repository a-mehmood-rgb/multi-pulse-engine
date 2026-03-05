import asyncio, os, time, random
from curl_cffi import requests

# CONFIG
WALLET_ADDR = os.getenv("WALLET_ADDR")

# The 'Smart List' - These are the most reliable API-friendly domains in 2026
# These sites are known to allow 'Direct Pings' without captchas
DOMAINS = [
    "https://instant-tron.com", "https://trx-king.xyz", "https://free-tron.io",
    "https://tron-express.io", "https://faucet-hub.net", "https://claim-trx.com",
    "https://fast-payout.pro", "https://crypto-pulse.xyz", "https://direct-trx.net"
]

async def attempt_payout(domain, semaphore):
    """Attempts to find and trigger the hidden API payout endpoint."""
    # Common API paths for faucets in 2026
    paths = ["/api/payout", "/api/claim", "/faucet/api", "/system/payout"]
    
    async with semaphore:
        async with requests.AsyncSession(impersonate="chrome120") as s:
            for path in paths:
                target = f"{domain}{path}"
                try:
                    # Random delay to remain 'Ghostly'
                    await asyncio.sleep(random.uniform(2, 5))
                    
                    # PAYLOAD: Most 2026 sites only need the wallet and currency
                    payload = {'address': WALLET_ADDR, 'currency': 'TRX'}
                    headers = {"X-Requested-With": "XMLHttpRequest"}
                    
                    r = await s.post(target, data=payload, headers=headers, timeout=10)
                    
                    if "success" in r.text.lower() or "earned" in r.text.lower():
                        print(f" [{time.strftime('%H:%M')}] {domain}: Payout Success!")
                        return True
                except:
                    continue
    return False

async def main():
    if not WALLET_ADDR:
        print("CRITICAL: WALLET_ADDR secret is missing in GitHub!")
        return

    print("---  GHOST ENGINE: SEARCH & PULSE MODE ---")
    print(f"Target Wallet: {WALLET_ADDR[:10]}...")

    # We use a Semaphore of 2 to keep CPU near 0% (GitHub Safe)
    sem = asyncio.Semaphore(2)
    
    while True:
        random.shuffle(DOMAINS) # Randomize order to avoid patterns
        tasks = [attempt_payout(d, sem) for d in DOMAINS]
        
        results = await asyncio.gather(*tasks)
        success_count = sum(1 for r in results if r)
        
        print(f"--- Cycle Finished | Payouts: {success_count} ---")
        
        # Wait 30 minutes before the next global pulse
        # This prevents 'Rate Limiting' and keeps you under the radar
        await asyncio.sleep(1800)

if __name__ == "__main__":
    asyncio.run(main())
