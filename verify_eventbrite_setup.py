#!/usr/bin/env python3
"""Verify Eventbrite API setup and credentials"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("EVENTBRITE API SETUP VERIFICATION")
print("=" * 70)

api_key = os.getenv('EVENTBRITE_API_KEY')

print(f"\n1. API Key Status:")
print(f"   Key: {api_key[:10]}...{api_key[-10:]} ({len(api_key)} characters)")

if len(api_key) < 40:
    print(f"   ⚠️  WARNING: Token is only {len(api_key)} characters")
    print(f"   ⚠️  Personal OAuth Tokens are typically 40-64 characters")
    print(f"   ⚠️  You might be using an Application Key or Client Secret")
elif len(api_key) >= 40:
    print(f"   ✓ Token length looks correct for Personal OAuth Token")

print(f"\n2. Testing Eventbrite API Endpoint:")
print(f"   Endpoint: https://www.eventbriteapi.com/v3/events/search")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Test 1: Simple search
print(f"\n3. Test Search:")
print(f"   Query: 'technology'")

try:
    response = requests.get(
        "https://www.eventbriteapi.com/v3/events/search",
        headers=headers,
        params={'q': 'technology', 'page_size': 3},
        timeout=10
    )

    print(f"   Status: {response.status_code}")
    print(f"   Full URL: {response.url}")

    if response.status_code == 200:
        data = response.json()
        events = data.get('events', [])
        pagination = data.get('pagination', {})

        print(f"\n   ✅ SUCCESS!")
        print(f"   Found {len(events)} events (out of {pagination.get('object_count', 0)} total)")

        if events:
            print(f"\n   Sample events:")
            for i, event in enumerate(events[:3], 1):
                name = event.get('name', {}).get('text', 'N/A')
                url = event.get('url', 'N/A')
                print(f"     {i}. {name}")
                print(f"        {url}")

        print(f"\n   ✅ Your Eventbrite API integration is working correctly!")

    elif response.status_code == 401:
        print(f"\n   ❌ ERROR: 401 Unauthorized")
        print(f"   Your API key is invalid or expired")
        print(f"   Solution: Generate a new Personal OAuth Token")

    elif response.status_code == 403:
        print(f"\n   ❌ ERROR: 403 Forbidden")
        print(f"   Your credentials don't have permission for this endpoint")
        print(f"\n   Common causes:")
        print(f"     1. Using Client Secret instead of Personal OAuth Token")
        print(f"     2. Using Application Key instead of Personal OAuth Token")
        print(f"     3. Token doesn't have proper scopes")
        print(f"\n   Solution: Get a Personal OAuth Token from:")
        print(f"     https://www.eventbrite.com/account-settings/apps")
        print(f"     Look for 'Personal OAuth Token' or 'Generate Personal Token'")

    elif response.status_code == 404:
        print(f"\n   ❌ ERROR: 404 Not Found")
        print(f"   The endpoint doesn't exist")
        print(f"   This should not happen with the correct URL")

    else:
        print(f"\n   ❌ ERROR: {response.status_code}")
        print(f"   Response: {response.text[:200]}")

except requests.exceptions.ConnectionError:
    print(f"\n   ❌ CONNECTION ERROR")
    print(f"   Could not connect to Eventbrite API")
    print(f"   Check your internet connection")

except Exception as e:
    print(f"\n   ❌ EXCEPTION: {str(e)}")

print(f"\n" + "=" * 70)
print(f"SUMMARY")
print(f"=" * 70)

print(f"\nCredentials in .env:")
print(f"  EVENTBRITE_API_KEY: {'✓ Set' if api_key else '✗ Missing'} ({len(api_key)} chars)")

print(f"\nRequired for Eventbrite API:")
print(f"  ✓ Endpoint: https://www.eventbriteapi.com/v3/events/search (no trailing slash)")
print(f"  ✓ Method: GET")
print(f"  ✓ Auth: Bearer token in Authorization header")
print(f"  ✓ Query: Use 'q' parameter with plain text")

print(f"\nNext steps if 403 Forbidden:")
print(f"  1. Go to https://www.eventbrite.com/account-settings/apps")
print(f"  2. Find 'Personal OAuth Token' or 'Generate Personal Token'")
print(f"  3. Copy the token (should be 40-64 characters)")
print(f"  4. Update .env: EVENTBRITE_API_KEY=<your_personal_token>")
print(f"  5. Run this script again: python verify_eventbrite_setup.py")

print(f"\n" + "=" * 70)
