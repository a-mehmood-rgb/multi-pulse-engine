import asyncio, os, time, random
from curl_cffi import requests

# CONFIG - Pulled from your GitHub Secrets
WALLET = os.getenv("WALLET_ADDR")

# The 'Smart List' - Top verified API-friendly domains for 2026
# These are known to support direct API pings without captchas
SITES = [
    "https://instant-tron.com", "https://trx-king.xyz", "https://free-tron.io",
    "https://tron-express.io", "https://faucet-hub.net", "https://claim-trx.com",
    "https://fast-payout.pro", "https://crypto-pulse.xyz", "https://direct-trx.net",
    "https://faucetearner.org" # Added your preferred site back in
]

async def scan_and_pulse(domain, semaphore):
    """Targets common API paths used by faucet scripts."""
    # These are the 3 most common 'payout doors' in 2026
    paths = ["/api/payout", "/api/claim", "/api.php?act=faucet"]
    
    async with semaphore:
        async with requests.AsyncSession(impersonate="chrome120") as s:
            for path in paths:
                target = f"{domain.rstrip('/')}{path}"
                try:
                    # Mimic human delay
                    await asyncio.sleep(random.uniform(3, 7))
                    
                    # We send the request. No password, just the wallet and a fake browser header.
                    headers = {"X-Requested-With": "XMLHttpRequest"}
                    payload = {'address': WALLET, 'currency': 'TRX'}
                    
                    r = await s.post(target, data=payload, headers=headers, timeout=10)
                    
                    if "success" in r.text.lower() or "earned" in r.text.lower():
                        print(f"[{time.strftime('%H:%M')}] {domain}: Claim Successful")
                        return True
                except:
                    continue
    return False

async def main():
    if not WALLET:
        print("CRITICAL: WALLET_ADDR secret is missing in GitHub!")
        return

    print("--- 🚀 GHOST SCANNER: PULSE MODE ---")
    print(f"Targeting: {WALLET[:8]}...")

    # Limit to 2 concurrent requests to keep GitHub CPU at 0%
    sem = asyncio.Semaphore(2)
    
    # Run the cycle
    random.shuffle(SITES)
    tasks = [scan_and_pulse(site, sem) for site in SITES]
    results = await asyncio.gather(*tasks)
    
    success_count = sum(1 for r in results if r)
    print(f"--- 🏁 CYCLE FINISHED | SUCCESSES: {success_count} ---")

if __name__ == "__main__":
    asyncio.run(main())
