import os, time, requests

# CONFIG
WALLET = os.getenv("WALLET_ADDR")
API_KEY = os.getenv("FP_API_KEY") # Use your FaucetPay API Key

# 2026 High-Volume Aggregators
# These don't need a browser if you have the API Key
TARGETS = [
    {"name": "FireFaucet", "url": "https://firefaucet.win/api/v1/payout"},
    {"name": "DutchyCorp", "url": "https://autofaucet.dutchycorp.space/api/v1/claim"}
]

def claim_all():
    print(f"--- ⚡ POWER PULSE 2026 | WALLET: {WALLET[:8]} ---")
    for site in TARGETS:
        try:
            # Direct API request to the aggregator's payout engine
            res = requests.post(site['url'], data={
                'api_key': API_KEY,
                'address': WALLET,
                'coin': 'TRX'
            }, timeout=10)
            
            if res.status_code == 200:
                print(f"✅ {site['name']}: Payout Triggered.")
            else:
                print(f"❌ {site['name']}: {res.status_code} - Check API Key.")
        except:
            print(f"⚠️ {site['name']}: Site Offline or IP Blocked.")

if __name__ == "__main__":
    claim_all()
