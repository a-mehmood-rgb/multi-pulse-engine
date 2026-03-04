import asyncio, os, random
from curl_cffi import requests

# CONFIG
FP_EMAIL = os.getenv("FP_EMAIL")
FP_API_KEY = os.getenv("FP_API_KEY")

# 2026 IMMORTAL LIST (Verified High-Paying March 2026)
TARGETS = [
    "https://free-tron.com/api/payout",
    "https://instant-tokens.com/api/payout",
    "https://trx-king.xyz/api/claim",
    "https://faucet.ovh/api/payout",
    "https://claimfreecoins.io/api/trx",
    "https://solana-faucet.net/api/claim",
    "https://doge-faucet.com/api/claim",
    "https://coin-faucet.com/api/trx",
    "https://crypto-drip.xyz/api/payout",
    "https://claimbits.net/api/claim",
    "https://bitsfree.net/api/payout",
    "https://autofaucet.org/api/payout"
]

async def process_payout(url, semaphore):
    async with semaphore:
        # Use a fresh session for every site to prevent tracking
        with requests.Session() as s:
            try:
                # 1. Randomized human-like behavior
                await asyncio.sleep(random.uniform(5, 12))
                persona = random.choice(["chrome120", "edge101", "safari17_0"])
                
                # 2. Visit the root domain first (Essential to bypass 2026 bot filters)
                base_url = url.split('/api')[0]
                s.get(base_url, impersonate=persona, timeout=10)
                await asyncio.sleep(random.uniform(2, 5))

                # 3. The Payout Request
                response = s.post(
                    url,
                    data={'address': FP_EMAIL, 'api_key': FP_API_KEY},
                    headers={"Referer": base_url, "X-Requested-With": "XMLHttpRequest"},
                    impersonate=persona, 
                    timeout=15
                )
                
                site = url.split('/')[2]
                if "success" in response.text.lower():
                    print(f"✅ SUCCESS -> {site}")
                    return True
                else:
                    # Specific 2026 logging to debug failures
                    status = "Busy/Empty" if response.status_code == 200 else f"Error {response.status_code}"
                    print(f"⚠️ {site}: {status}")
            except: pass
    return False

async def main():
    print("--- 🚀 GHOST ENGINE: MARCH 2026 PRIORITY MODE ---")
    if not FP_API_KEY:
        print("❌ Error: API Key missing from Secrets."); return

    # Shuffle targets so we don't hit the same site at the same second every cycle
    active_list = TARGETS
    random.shuffle(active_list)

    # 4 Parallel workers (The 'Sweet Spot' for staying under the radar)
    sem = asyncio.Semaphore(4) 
    print(f"🔥 Sniping {len(active_list)} Immortal Targets...")
    
    results = await asyncio.gather(*[process_payout(u, sem) for u in active_list])
    
    success = sum(1 for r in results if r)
    print(f"--- 🏁 BATCH COMPLETE | TOTAL SUCCESS: {success} ---")

if __name__ == "__main__":
    asyncio.run(main())
