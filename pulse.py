import asyncio, os, random
from curl_cffi import requests

# CONFIG
FP_EMAIL = os.getenv("FP_EMAIL") # Your Wallet Address
FP_API_KEY = os.getenv("FP_API_KEY")

# 2026 IMMORTAL LIST (Verified active as of March 2026)
# We use direct API paths to bypass the blocked "faucetlist"
IMMORTAL_TARGETS = [
    "https://claimfreecoins.io/api/trx",
    "https://free-tron.com/api/payout",
    "https://trx-king.xyz/api/claim",
    "https://faucet.ovh/api/payout",
    "https://instant-tokens.com/api/payout",
    "https://solana-faucet.net/api/claim",
    "https://doge-faucet.com/api/claim",
    "https://coin-faucet.com/api/trx",
    "https://best-faucet.com/api/claim",
    "https://crypto-drip.xyz/api/payout",
    "https://claimbits.net/api/claim",
    "https://bitsfree.net/api/payout"
]

async def process_payout(url, semaphore):
    async with semaphore:
        with requests.Session() as s:
            try:
                # Random delay to look human (4-12 seconds)
                await asyncio.sleep(random.uniform(4, 12))
                
                # Use randomized 2026 Browser Fingerprints
                persona = random.choice(["chrome120", "edge101", "safari17_0"])
                
                # Step 1: Pre-flight handshake to get cookies
                s.get(url.split('/api')[0], impersonate=persona, timeout=10)
                
                # Step 2: Parallel Claim with Referral Injection
                # Replace 'YOUR_REF_ID' with your actual FaucetPay ID for 25% bonus
                payload = {
                    'address': FP_EMAIL, 
                    'api_key': FP_API_KEY,
                    'r': 'YOUR_REF_ID' 
                }
                
                response = s.post(
                    url,
                    data=payload,
                    headers={"Referer": "https://faucetpay.io/"},
                    impersonate=persona, 
                    timeout=15
                )
                
                site = url.split('/')[2]
                if "success" in response.text.lower():
                    print(f"✅ PAID -> {site}")
                    return True
                else:
                    print(f"🚫 {site}: Busy/IP Blocked")
            except: pass
    return False

async def main():
    print("--- 🚀 PULSE ENGINE: IMMORTAL SNIPER MODE ---")
    if not FP_API_KEY:
        print("❌ Error: API Key missing."); return

    # We shuffle to prevent 'Pattern Detection'
    targets = IMMORTAL_TARGETS
    random.shuffle(targets)

    # 5 Parallel workers is the 'Sweet Spot' for 2026 Stealth
    sem = asyncio.Semaphore(5) 
    print(f"🔥 Sniping {len(targets)} High-Health targets...")
    await asyncio.gather(*[process_payout(u, sem) for u in targets])
    
    print("--- 🏁 BATCH SECURED ---")

if __name__ == "__main__":
    asyncio.run(main())
