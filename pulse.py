import asyncio, os, time
from curl_cffi import requests

# CONFIG: Use your FaucetPay API Key from your dashboard
API_KEY = os.getenv("FP_API_KEY") 
WALLET_ADDR = os.getenv("WALLET_ADDR")

async def get_active_faucets():
    """Fetches the latest list of high-health faucets from FaucetPay."""
    url = f"https://faucetpay.io/api/v1/listfaucets?api_key={API_KEY}"
    try:
        async with requests.AsyncSession() as s:
            r = await s.get(url)
            data = r.json()
            if data.get("status") == 200:
                # Filter for sites with > 80% health and 'Normal' payout
                return [f['url'] for f in data['faucets'] if int(f['health']) > 80]
    except:
        return []

async def claim_payout(faucet_url):
    """Attempts a direct API claim without login/captcha."""
    try:
        async with requests.AsyncSession(impersonate="chrome120") as s:
            # We target the common 'api/claim' endpoint many sites use
            target = f"{faucet_url.rstrip('/')}/api/claim"
            payload = {'address': WALLET_ADDR, 'currency': 'TRX'}
            
            # Direct POST to bypass frontend links
            res = await s.post(target, data=payload, timeout=10)
            if "success" in res.text.lower():
                print(f"Success: {faucet_url}")
    except:
        pass

async def main():
    print("--- 🌫️ GHOST AUTO-SCOUT: DYNAMIC API MODE ---")
    while True:
        # 1. Dynamically get all sites (Not fixed!)
        faucet_list = await get_active_faucets()
        print(f"Discovered {len(faucet_list)} active API faucets.")

        # 2. Pulse through the list
        for url in faucet_list:
            await claim_payout(url)
            await asyncio.sleep(60) # Stagger to avoid IP bans

        # 3. Rest before next global scan
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
