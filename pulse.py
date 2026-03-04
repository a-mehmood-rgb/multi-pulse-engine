import asyncio, os, random
from curl_cffi import requests

# CONFIG
FP_EMAIL = os.getenv("FP_EMAIL")
FP_API_KEY = os.getenv("FP_API_KEY")

# 2026 ANTI-DETECT PROFILES
OS_PROFILES = ["chrome120", "edge101", "safari17_0"]

async def process_payout(url, semaphore):
    async with semaphore:
        with requests.Session() as s:
            try:
                # 1. Random 'Human' delay (essential for 2026 stealth)
                await asyncio.sleep(random.uniform(5, 12))
                persona = random.choice(OS_PROFILES)
                
                # 2. Visit homepage first to grab a session/security cookie
                # This mimics a human user landing on the page
                base_url = url.split('/api')[0]
                s.get(base_url, impersonate=persona, timeout=10)
                await asyncio.sleep(random.uniform(2, 4))

                # 3. The Payout Post
                payload = {
                    'address': FP_EMAIL, 
                    'api_key': FP_API_KEY
                }
                
                response = s.post(
                    url,
                    data=payload,
                    headers={
                        "Referer": base_url,
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    impersonate=persona, 
                    timeout=15
                )
                
                site = url.split('/')[2]
                if "success" in response.text.lower():
                    print(f"✅ PAID -> {site}")
                    return True
                elif response.status_code == 403:
                    print(f"🚫 {site}: IP Blocked (GitHub Server Burned)")
                else:
                    # Often means site is empty or rate-limited for your address
                    print(f"⚠️ {site}: Busy/Empty")
            except: pass
    return False

async def main():
    print("--- 🚀 SHADOW PULSE: MARCH 2026 EDITION ---")
    
    # 2026 Target List (High-health sites)
    targets = [
        "https://free-tron.com/api/payout", "https://instant-tokens.com/api/payout",
        "https://trx-king.xyz/api/claim", "https://faucet.ovh/api/payout",
        "https://claimfreecoins.io/api/trx", "https://solana-faucet.net/api/claim",
        "https://doge-faucet.com/api/claim", "https://coin-faucet.com/api/trx",
        "https://crypto-drip.xyz/api/payout", "https://claimbits.net/api/claim"
    ]
    
    random.shuffle(targets)
    sem = asyncio.Semaphore(4) # Lower concurrency = Better chance of bypass
    await asyncio.gather(*[process_payout(u, sem) for u in targets])
    print("--- 🏁 BATCH SECURED ---")

if __name__ == "__main__":
    asyncio.run(main())
