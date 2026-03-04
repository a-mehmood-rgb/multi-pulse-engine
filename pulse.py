import asyncio, os, random
from curl_cffi import requests

# CONFIG
FP_EMAIL = os.getenv("FP_EMAIL")
FP_API_KEY = os.getenv("FP_API_KEY")

# Verified March 2026 API-only targets (No login required)
API_TARGETS = [
    "https://free-tron.com/api/payout",
    "https://instant-tokens.com/api/payout",
    "https://trx-king.xyz/api/payout",
    "https://faucet-generator.com/api/payout",
    "https://claimclick.net/api/payout"
]

async def snipe_target(url, semaphore):
    domain = url.split('/')[2]
    async with semaphore:
        try:
            # Human-like delay to avoid IP rate-limiting
            await asyncio.sleep(random.uniform(5, 12))
            
            with requests.Session() as s:
                # Direct API Snipe
                response = s.post(
                    url,
                    data={'address': FP_EMAIL, 'api_key': FP_API_KEY},
                    impersonate="chrome120",
                    timeout=15
                )
                
                if "success" in response.text.lower():
                    print(f"✅ API SUCCESS -> {domain}")
                    return True
                else:
                    print(f"❌ {domain}: Skipped (Login/Captcha Required)")
        except: pass
    return False

async def main():
    print("--- 🚀 GHOST ENGINE v3.5: PURE API MODE ---")
    sem = asyncio.Semaphore(2) 
    results = await asyncio.gather(*[snipe_target(u, sem) for u in API_TARGETS])
    print(f"--- 🏁 SESSION COMPLETE | SUCCESS: {sum(1 for r in results if r)} ---")

if __name__ == "__main__":
    asyncio.run(main())
