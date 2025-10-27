"""Get correct Tradier account ID from profile"""
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")

API_KEY = os.getenv("TRADIER_API_KEY")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
}

# Get user profile
print("Fetching Tradier profile...")
response = requests.get("https://api.tradier.com/v1/user/profile", headers=headers)

if response.status_code == 200:
    profile = response.json()
    print(f"\n[OK] Profile retrieved successfully")
    print(f"\nFull response: {profile}")

    # Extract account ID
    if "profile" in profile:
        prof_data = profile["profile"]
        if "account" in prof_data:
            accounts = prof_data["account"]
            # Handle single account (dict) or multiple (list)
            if isinstance(accounts, dict):
                accounts = [accounts]

            print(f"\n=== AVAILABLE ACCOUNTS ===")
            for acc in accounts:
                acc_num = acc.get("account_number")
                acc_type = acc.get("type")
                classification = acc.get("classification")
                status = acc.get("status")
                print(f"  Account: {acc_num}")
                print(f"    Type: {acc_type}")
                print(f"    Classification: {classification}")
                print(f"    Status: {status}")
                print()

            # Recommend first active account
            active_accounts = [a for a in accounts if a.get("status") == "active"]
            if active_accounts:
                recommended = active_accounts[0].get("account_number")
                print(f"\n[RECOMMENDED] Use this account ID: {recommended}")
                print(f"\nUpdate your .env file:")
                print(f"TRADIER_ACCOUNT_ID={recommended}")
            else:
                print("\n[WARNING] No active accounts found!")
        else:
            print("[ERROR] No 'account' key in profile")
    else:
        print("[ERROR] No 'profile' key in response")
else:
    print(f"[ERROR] HTTP {response.status_code}: {response.text}")
