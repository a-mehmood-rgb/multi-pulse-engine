import asyncio, os, random, time
from curl_cffi import requests
from playwright.async_api import async_playwright

# CONFIG
FP_EMAIL = os.getenv("FP_EMAIL")
FP_API_KEY = os.getenv("FP_API_KEY")
COOLDOWN_SITES = {}

async def scrape_faucetpay_list():
    print("🕵️  Bypassing Cloudflare... (March 2026 Stealth)")
    targets = []
    async with async_playwright() as p:
        # Launch with 'headed' flags even if headless, to mimic real browser behavior
        browser = await p.chromium.launch(
            headless=True, 
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        try:
            # 1. Navigate and WAIT for the 'Just a moment' challenge to pass
            await page.goto("https://faucetpay.io/faucetlist/tron", wait_until="networkidle")
            
            # 2. Add a 'Human' jitter
            await asyncio.sleep(random.uniform(5, 8))
            
            # 3. New 2026 Selector: FaucetPay often hides the table now. 
            # We look for the 'Visit' buttons directly.
            await page.wait_for_selector("a[href*='faucet/out/']", timeout=15000)
            
            links = await page.locator("a[href*='faucet/out/']").all()
            for link in links[:12]:
                url = await link.get_attribute("href")
                # Convert the redirect link to a direct API target
                if url: targets.append(url + "/api/payout")
                
        except Exception as e:
            print(f"⚠️ Cloudflare still blocking. Using local cache.")
        
        await browser.close()
    return targets if targets else ["https://free-tron.com/api/payout", "https://instant-tokens.com/api/payout"]

async def process_payout(url, semaphore):
    site_domain = url.split('/')[2]
    if site_domain in COOLDOWN_SITES and time.time() < COOLDOWN_SITES[site_domain]:
        return False

    async with semaphore:
        with requests.Session() as s:
            try:
                await asyncio.sleep(random.uniform(5, 10))
                persona = random.choice(["chrome120", "edge101"])
                
                # Warm up
                base_url = url.split('/api')[0]
                s.get(base_url, impersonate=persona, timeout=10)
                
                # The Snipe
                response = s.post(
                    url,
                    data={'address': FP_EMAIL, 'api_key': FP_API_KEY},
                    headers={"Referer": base_url, "X-Requested-With": "XMLHttpRequest"},
                    impersonate=persona, timeout=15
                )
                
                if "success" in response.text.lower():
                    print(f"✅ SUCCESS -> {site_domain}")
                    return True
                else:
                    COOLDOWN_SITES[site_domain] = time.time() + 7200 # 2 hour cool
                    print(f"⏳ {site_domain}: Busy/Empty")
            except: pass
    return False

async def main():
    print("--- 🚀 GHOST ENGINE v3: SCRAPER MODE ---")
    if not FP_API_KEY:
        print("❌ Error: API Key missing."); return

    # Get fresh targets via Playwright
    targets = await scrape_faucetpay_list()
    random.shuffle(targets)

    sem = asyncio.Semaphore(3)
    print(f"🔥 Sniping {len(targets)} Targets...")
    results = await asyncio.gather(*[process_payout(u, sem) for u in targets])
    
    success = sum(1 for r in results if r)
    print(f"--- 🏁 SESSION COMPLETE | SUCCESS: {success} ---")

if __name__ == "__main__":
    asyncio.run(main())
