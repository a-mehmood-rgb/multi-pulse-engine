import asyncio, os, random, time
from curl_cffi import requests

# CONFIG
FP_EMAIL = os.getenv("FP_EMAIL")
FP_API_KEY = os.getenv("FP_API_KEY")

# Dictionary to prevent spamming dry sites
COOLDOWN_SITES = {}

async def fetch_dynamic_targets():
    """Fetches the top 50 faucets currently active on FaucetPay."""
    print("📡 Fetching fresh targets from FaucetPay...")
    try:
        # FaucetPay's public faucet list endpoint
        url = "https://faucetpay.io/api/v1/faucetlist"
        # In a real scenario, you'd use your API key here to get premium lists
        r = requests.get(url, params={'api_key': FP_API_KEY}, impersonate="chrome120")
        data = r.json()
        
        # Extract the URLs from the top 50 faucets
        new_targets = [f['url'] + "/api/payout" for f in data.get('faucets', [])[:50]]
        return new_targets
    except Exception as e:
        print(f"⚠️ Could not fetch dynamic list. Using backup targets.")
        return [
            "https://free-tron.com/api/payout",
            "https://instant-tokens.com/api/payout",
            "https://autofaucet.org/api/payout"
        ]

async def process_payout(url, semaphore):
    site_domain = url.split('/')[2]
    
    # 1. Check Cooldown (Skip if we hit 'Busy' in the last 4 hours)
    if site_domain in COOLDOWN_SITES and time.time() < COOLDOWN_SITES[site_domain]:
        return False

    async with semaphore:
        with requests.Session() as s:
            try:
                # 2. Random Human Jitter
                await asyncio.sleep(random.uniform(10, 25))
                persona = random.choice(["chrome120", "edge101", "safari17_0"])
                
                # 3. Simulate a 'Warm-up' visit to the homepage
                base_url = url.split('/api')[0]
                s.get(base_url, impersonate=persona, timeout=10)
                await asyncio.sleep(random.uniform(3, 7))

                # 4. The Snipe
                response = s.post(
                    url,
                    data={'address': FP_EMAIL, 'api_key': FP_API_KEY},
                    headers={"Referer": base_url, "X-Requested-With": "XMLHttpRequest"},
                    impersonate=persona, 
                    timeout=15
                )
                
                if "success" in response.text.lower():
                    print(f"✅ SUCCESS -> {site_domain}")
                    return True
                else:
                    # If site is dry, put it on a 4-hour cooldown
                    COOLDOWN_SITES[site_domain] = time.time() + 14400 
                    status = "Busy/Empty" if response.status_code == 200 else f"Error {response.status_code}"
                    print(f"⏳ {site_domain}: {status} (Cooldown active)")
            except: pass
    return False

async def main():
    print("--- 🚀 GHOST ENGINE v2: DYNAMIC DISCOVERY MODE ---")
    
    # Fetch 50 fresh targets
    targets = await fetch_dynamic_targets()
    random.shuffle(targets)

    sem = asyncio.Semaphore(2) # Lower parallelism = Harder to detect
    print(f"🔥 Sniping {len(targets)} Fresh Targets...")
    
    results = await asyncio.gather(*[process_payout(u, sem) for u in targets])
    
    success = sum(1 for r in results if r)
    print(f"--- 🏁 SESSION COMPLETE | TOTAL SUCCESS: {success} ---")

if __name__ == "__main__":
    asyncio.run(main())
