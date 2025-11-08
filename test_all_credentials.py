#!/usr/bin/env python3
"""Comprehensive Eventbrite API credential testing"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("EVENTBRITE API CREDENTIAL DIAGNOSTIC TEST")
print("=" * 70)

# All credentials from .env
private_token = "BNU7XQLE3O3FGGQ7VATY"
app_key = "VCUBJ6XZCART2UYN3D"
client_secret = "QZ45E5B7PATD2NFQXTKHALHFD5C4KVVUJGSRKCRQNHWBWIYLOV"

print("\nCredentials to test:")
print(f"1. Private Token: {private_token} ({len(private_token)} chars)")
print(f"2. Application Key: {app_key} ({len(app_key)} chars)")
print(f"3. Client Secret: {client_secret} ({len(client_secret)} chars)")
print("=" * 70)

credentials = [
    ("Private Token", private_token),
    ("Application Key", app_key),
    ("Client Secret", client_secret)
]

test_endpoints = [
    ("User Info", "https://www.eventbriteapi.com/v3/users/me"),
    ("Categories", "https://www.eventbriteapi.com/v3/categories"),
    ("Event Search", "https://www.eventbriteapi.com/v3/events/search")
]

for cred_name, cred_value in credentials:
    print(f"\n{'=' * 70}")
    print(f"Testing with: {cred_name}")
    print(f"{'=' * 70}")

    for endpoint_name, endpoint_url in test_endpoints:
        print(f"\n  → {endpoint_name}: {endpoint_url}")

        # Test with Bearer token
        headers = {
            "Authorization": f"Bearer {cred_value}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(endpoint_url, headers=headers, timeout=10)

            if response.status_code == 200:
                print(f"    ✓ SUCCESS! Status: {response.status_code}")
                data = response.json()
                if endpoint_name == "Categories":
                    cats = data.get('categories', [])
                    print(f"    ✓ Found {len(cats)} categories")
                elif endpoint_name == "Event Search":
                    events = data.get('events', [])
                    print(f"    ✓ Found {len(events)} events")
                elif endpoint_name == "User Info":
                    user_name = data.get('name', 'Unknown')
                    print(f"    ✓ User: {user_name}")
                break  # Success! No need to test other endpoints
            else:
                print(f"    ✗ Failed: {response.status_code} - {response.text[:100]}")

        except Exception as e:
            print(f"    ✗ Exception: {str(e)}")

print("\n" + "=" * 70)
print("DIAGNOSTIC SUMMARY")
print("=" * 70)

print("\nIf all tests failed with 403:")
print("  1. Your Eventbrite app may need approval/activation")
print("  2. Wait 5-10 minutes for the API keys to activate")
print("  3. Check if your Eventbrite account email is verified")
print("  4. Verify your app has proper permissions enabled")
print("  5. Contact Eventbrite support: support@eventbrite.com")

print("\nTo check app status:")
print("  → Visit: https://www.eventbrite.com/account-settings/apps")
print("  → Look for any warnings or 'pending approval' messages")
print("  → Ensure 'API Access' is enabled for your app")

print("\nEventbrite API Documentation:")
print("  → https://www.eventbrite.com/platform/api")
print("  → https://www.eventbrite.com/platform/api#/introduction/authentication")

print("\n" + "=" * 70)
