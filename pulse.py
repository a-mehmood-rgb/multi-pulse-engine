import asyncio, os, random
from curl_cffi import requests

# CONFIG
FP_EMAIL = os.getenv("FP_EMAIL")
FP_API_KEY = os.getenv("FP_API_KEY")

# 2026 HIGH-TRUST PROFILES
OS_PROFILES = ["chrome120", "edge101", "safari17_0"]

async def process_payout(url, semaphore):
    async with semaphore:
        # Create a Session to handle cookies/handshakes (Bypasses many 403s)
        with requests.Session() as s:
            try:
                await asyncio.sleep(random.uniform(5, 10))
                persona = random.choice(OS_PROFILES)
                
                # Step 1: Visit the site first to get a session cookie (Stealth)
                s.get(url, impersonate=persona, timeout=10)
                await asyncio.sleep(2)

                # Step 2: The actual Payout Post
                response = s.post(
                    url,
                    data={'address': FP_EMAIL, 'api_key': FP_API_KEY},
                    headers={"Referer": url},
                    impersonate=persona, 
                    timeout=15
                )
                
                site = url.split('/')[2]
                if response.status_code == 200:
                    if "success" in response.text.lower():
                        print(f"✅ Success -> {site}")
                        return True
                    else:
                        print(f"⚠️ {site}: Wallet Empty/Cooldown")
                else:
                    print(f"🚫 {site}: Error {response.status_code}")
            except: pass
    return False

async def main():
    print("--- 🚀 RELOADING GHOST ENGINE (SESSION MODE) ---")
    
    # HARD-CODED 2026 TOP EARNERS (March Updated)
    # These sites are currently bypassing GitHub IP blocks
    targets = [
        "https://claimfreecoins.io/api/trx",
        "https://free-tron.com/api/payout",
        "https://faucetearner.org/api/payout",
        "https://trx-king.xyz/api/claim",
        "https://instant-tokens.com/api/payout",
        "https://faucet.ovh/api/payout",
        "https://claimbits.net/api/claim",
        "https://bitsfree.net/api/payout",
        "https://firefaucet.win/api/claim",
        "https://cointiply.com/api/payout"
    ]

    sem = asyncio.Semaphore(5) # Lowered to 5 for better stability
    await asyncio.gather(*[process_payout(u, sem) for u in targets])
    print("--- 🏁 SESSION SECURED ---")

if __name__ == "__main__":
    asyncio.run(main())
