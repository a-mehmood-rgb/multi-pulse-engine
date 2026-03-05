import asyncio, os, time, random
from curl_cffi import requests

WALLET = os.getenv("WALLET_ADDR")

# Updated 2026 High-Yield Targets
SITES = [
    {"url": "https://faucetearner.org", "api": "/api.php?act=faucet"},
    {"url": "https://instant-tron.com", "api": "/api/claim"},
    {"url": "https://trx-king.xyz", "api": "/api/payout"},
    {"url": "https://free-tron.io", "api": "/api/claim"}
]

async def ghost_claim(site, semaphore):
    domain = site['url'].split('/')[2]
    async with semaphore:
        # 1. Start a Session to handle Cookies automatically
        async with requests.AsyncSession(impersonate="chrome120") as s:
            try:
                # 2. Visit Home Page first (Crucial to get the Session Cookie)
                await s.get(site['url'], timeout=15)
                await asyncio.sleep(random.uniform(2, 4))

                # 3. Fire the Actual Payout
                headers = {
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": site['url']
                }
                payload = {'address': WALLET, 'currency': 'TRX'}
                
                response = await s.post(
                    f"{site['url']}{site['api']}", 
                    data=payload, 
                    headers=headers, 
                    timeout=15
                )

                if "success" in response.text.lower() or "earned" in response.text.lower():
                    print(f"✅ [{time.strftime('%H:%M')}] {domain}: Success!")
                    return True
                else:
                    # Log the reason for failure (e.g., "Wait 5 minutes")
                    reason = response.text[:30].replace('\n', '')
                    print(f"❌ [{time.strftime('%H:%M')}] {domain}: {reason}")
            except Exception as e:
                print(f"⚠️ [{time.strftime('%H:%M')}] {domain}: Connection Error")
    return False

async def main():
    if not WALLET:
        print("MISSING WALLET_ADDR IN SECRETS")
        return

    print(f"--- 🚀 GHOST ENGINE v12.0 | TARGET: {WALLET[:8]} ---")
    sem = asyncio.Semaphore(2)
    
    while True:
        tasks = [ghost_claim(s, sem) for s in SITES]
        await asyncio.gather(*tasks)
        
        # 15-minute rest to avoid 'Bot' detection
        print("Cycle finished. Resting 15m...")
        await asyncio.sleep(900)

if __name__ == "__main__":
    asyncio.run(main())
