import os, time, random, requests

# CONFIG
WALLET = os.getenv("WALLET_ADDR")
API_KEY = os.getenv("FP_API_KEY") # Get this from FaucetPay Dashboard

def get_faucet_list():
    """Fetches the current list of active faucets from FaucetPay"""
    url = "https://faucetpay.io/api/v1/faucetlist"
    try:
        # FaucetPay requires a POST with your API Key
        r = requests.post(url, data={'api_key': API_KEY}, timeout=10)
        data = r.json()
        if data.get("status") == 200:
            # We filter for TRX faucets with > 80% health
            return [f for f in data['faucets'] if f['currency'] == 'TRX' and int(f['health']) > 80]
    except:
        return []
    return []

def claim_from_site(site_url):
    """Attempts a claim using the common 2026 API pattern"""
    # Most smaller faucets use this standardized API endpoint
    target = f"{site_url.rstrip('/')}/api/claim"
    try:
        payload = {'address': WALLET, 'currency': 'TRX'}
        # We use a real-looking User-Agent to avoid immediate 'Bot' flags
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
        
        r = requests.post(target, data=payload, headers=headers, timeout=10)
        if "success" in r.text.lower():
            return True
    except:
        pass
    return False

def main():
    print(f"--- 🚀 TARGETING $3.00/DAY | WALLET: {WALLET[:8]} ---")
    
    faucets = get_faucet_list()
    if not faucets:
        print("❌ No faucets found. Check your FaucetPay API Key.")
        return

    print(f"Found {len(faucets)} active TRX targets.")
    
    success_count = 0
    # We only try the top 20 to stay within GitHub's 5-minute window
    for site in faucets[:20]:
        domain = site['url'].split('/')[2]
        if claim_from_site(site['url']):
            print(f"✅ Success: {domain}")
            success_count += 1
        else:
            print(f"❌ Failed: {domain}")
        
        # 10-second wait between sites to prevent IP bans
        time.sleep(10)

    print(f"--- CYCLE COMPLETE | PAYOUTS: {success_count} ---")

if __name__ == "__main__":
    main()
