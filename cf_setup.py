#!/usr/bin/env python3
"""Set up Cloudflare Pages for Passe La Fete"""
import requests
import json

TOKEN = "***"
BASE = "https://api.cloudflare.com/client/v4"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

# Step 1: Get account ID
r = requests.get(f"{BASE}/accounts", headers=HEADERS)
print("1. Accounts:", json.dumps(r.json(), indent=2)[:500])

if r.json()["success"]:
    accounts = r.json()["result"]
    if accounts:
        account_id = accounts[0]["id"]
        print(f"\nAccount ID: {account_id}")

        # Step 2: Create Pages project
        project_data = {
            "name": "passelafete",
            "production_branch": "main",
        }
        r2 = requests.post(
            f"{BASE}/accounts/{account_id}/pages/projects",
            headers=HEADERS,
            json=project_data
        )
        print(f"\n2. Create project: {r2.status_code}")
        print(json.dumps(r2.json(), indent=2)[:1000])
else:
    print("Failed to get accounts - check token")
