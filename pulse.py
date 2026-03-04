import asyncio, os, random, time
from curl_cffi import requests
from playwright.async_api import async_playwright

# CONFIG
FP_EMAIL = os.getenv("FP_EMAIL")
FP_API_KEY = os.getenv("FP_API_KEY")
COOLDOWN_SITES = {}

async def scrape_faucetpay_list():
    """Bypasses API blocks by scraping the FaucetPay website directly."""
    print("🕵️  Scraping FaucetPay for fresh targets...")
    targets = []
    async with async_playwright() as p:
        # Launch stealth browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0")
        page = await context.new_page()
        
        try:
            # Navigate to the Tron Faucet List (Highest payout in March 2026)
            await page.goto("https://faucetpay.io/faucetlist/tron", timeout=60000)
            await page.wait_for_selector("table", timeout=10000)
            
            # Grab top 15 'Visit' buttons
            links = await page.locator("a.btn-visit").element_handles()
            for link in links[:15]:
                href = await link.get_attribute("href")
                if href:
                    # Clean the URL and add the common API path
                    clean_url = href.split('?')[0].rstrip('/') + "/api/payout"
                    targets.append(clean_url)
        except Exception as e:
            print(f"⚠️ Scraper failed: {e}")
        
        await browser.close()
    
    # Backup if scraping fails
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
