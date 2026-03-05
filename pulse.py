import asyncio, os, time, random
from curl_cffi import requests
from termcolor import colored

# CONFIG
MAIL = os.getenv("MAIL")
PASSWORD = os.getenv("PASSWORD")
BASE_URL = "https://faucetearner.org"

def log(message, color="white", on_color=None):
    t = time.strftime("%H:%M:%S")
    print(f"[{t}] {colored(message, color, on_color)}")

async def ghost_pulse():
    log("---  GHOST ENGINE v7.0: PULSE-SYNC ---", "magenta")
    
    # Use AsyncSession to maintain cookies (login state)
    async with requests.AsyncSession(impersonate="chrome120") as s:
        # 1. AUTHENTICATION
        log("Logging in...", "yellow")
        login_data = {'email': MAIL, 'password': PASSWORD}
        # Emulating the AJAX login used by faucetearner
        r = await s.post(f"{BASE_URL}/api.php?act=login", data=login_data)
        
        if "success" not in r.text.lower() and r.status_code != 200:
            log("Login failed! check credentials.", "red")
            return

        log("Logged in successfully!", "green")

        # 2. MAIN PULSE LOOP
        while True:
            try:
                # Sync with the server's 'second' counter
                # We fetch the faucet page to get the current timer state
                faucet_page = await s.get(f"{BASE_URL}/faucet.php")
                
                # Optimized: Direct API Request during the 55s-60s window
                # The Selenium script waits for '55'. We'll fire right at the sweet spot.
                log("Waiting for pulse window (55s mark)...", "cyan")
                
                while True:
                    current_sec = time.localtime().tm_sec
                    if current_sec >= 55:
                        break
                    await asyncio.sleep(0.5) # High-precision polling

                # 3. TRIGGER PAYOUT (The 'apireq' equivalent)
                log("Target in sight. Firing API request...", "white", "on_blue")
                
                # Faucetearner uses a specific API endpoint for the 'apireq()' function
                payout_req = await s.post(
                    f"{BASE_URL}/api.php?act=faucet", 
                    headers={"X-Requested-With": "XMLHttpRequest"}
                )
                
                if payout_req.status_code == 200:
                    res_data = payout_req.json()
                    reward = res_data.get("message", "Unknown Amount")
                    log(f" CLAIM SUCCESS: {reward}", "white", "on_green")
                else:
                    log(f"Pulse missed or rate-limited. Retrying next cycle.", "red")

                # Wait for the next minute cycle
                await asyncio.sleep(60 - time.localtime().tm_sec + 1)
                
            except Exception as e:
                log(f" Error in pulse: {e}", "red")
                await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(ghost_pulse())
    except KeyboardInterrupt:
        log("Ghost Engine stopped by user.", "yellow")
