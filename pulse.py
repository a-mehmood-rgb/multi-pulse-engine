import os, time, random
from seleniumbase import Driver

# CONFIG
WALLET = os.getenv("WALLET_ADDR")
# Note: You can't just 'Ping' these anymore; you must 'Visit' them.
SITES = ["https://faucetearner.org", "https://instant-tron.com"]

def ghost_pulse():
    # Launch a stealth driver that Cloudflare cannot see
    driver = Driver(browser="chrome", uc=True, headless=True)
    
    try:
        for url in SITES:
            print(f"--- Visiting {url} ---")
            driver.get(url)
            time.sleep(random.uniform(5, 8)) # Wait for Cloudflare to 'Green Light' you

            # Logic for FaucetEarner (Requires login now)
            if "faucetearner" in url:
                # You must manually login ONCE on your PC and export cookies, 
                # OR use the login secrets here:
                # driver.type("#email", os.getenv("MAIL"))
                # driver.type("#password", os.getenv("PASSWORD"))
                # driver.click("#login_btn")
                pass

            # Logic for Direct Wallet Faucets
            try:
                # Find the input box and type the wallet
                driver.type("input[name='address']", WALLET)
                time.sleep(2)
                driver.click("button:contains('Claim')")
                print(f"✅ Claim Attempted on {url}")
            except:
                print(f"❌ Could not find claim button on {url}")

    finally:
        driver.quit()

if __name__ == "__main__":
    ghost_pulse()
