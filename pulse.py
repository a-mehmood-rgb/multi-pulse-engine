import asyncio, os, random, time
from curl_cffi import requests
from playwright.async_api import async_playwright

# CONFIG
FP_EMAIL = os.getenv("FP_EMAIL")
FP_API_KEY = os.getenv("FP_API_KEY")
COOLDOWN_SITES = {}

async def scrape_faucetpay_list():
    print("🕵️  Initiating Hardware Simulation (Bypassing Turnstile 2026)")
    targets = []
    async with async_playwright() as p:
        # Use Chromium with specific flags to hide automation
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0",
            viewport={'width': 1366, 'height': 768}
        )
        
        # KEY: This script deletes the "webdriver" property so Cloudflare can't see it
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = await context.new_page()
        try:
            # 1. Random delay before navigating
            await asyncio.sleep(random.uniform(2, 4))
            await page.goto("https://faucetpay.io/faucetlist/tron", wait_until="domcontentloaded")
            
            # 2. WAIT for the human check. 
            # In 2026, you shouldn't just wait for the table; 
            # you must wait for the "cf_clearance" cookie to appear.
            print("⏳ Solving Turnstile...")
            await asyncio.sleep(random.uniform(10, 15)) 
            
            # 3. Use a different selector. Cloudflare often blocks 'a.btn-visit'
            # We scrape the data directly from the row text if buttons are hidden.
            rows = await page.locator("tr").all()
            for row in rows[1:15]: # Skip header, grab top 14
                text = await row.inner_text()
                if "Visit" in text:
                    # Logic to find the link within that specific row
                    link_el = row.locator("a[href*='/out/']")
                    if await link_el.count() > 0:
                        href = await link_el.get_attribute("href")
                        targets.append(href + "/api/payout")
            
            print(f"📡 Found {len(targets)} Fresh Targets via Stealth Scraper")
            
        except Exception as e:
            print(f"⚠️ Stealth Scraper failed. Error: {str(e)[:50]}")
        
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
