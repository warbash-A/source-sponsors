#!/usr/bin/env python3
"""Check Eventbrite API accessibility and app status"""

import requests

print("=" * 70)
print("EVENTBRITE API STATUS CHECK")
print("=" * 70)

# Test 1: Check if API is accessible at all (no auth)
print("\nTest 1: Checking if Eventbrite API is accessible...")
try:
    response = requests.get("https://www.eventbriteapi.com/v3/categories", timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")

    if response.status_code == 401:
        print("✓ API is accessible (401 = needs authentication, which is expected)")
    elif response.status_code == 403:
        print("✗ Getting 403 even without auth - API might be restricted")
    else:
        print(f"Unexpected status: {response.status_code}")
except Exception as e:
    print(f"✗ Cannot reach API: {str(e)}")

print("\n" + "=" * 70)
print("\nYour credentials summary:")
print("  Private token: 20 chars (expected: 40-64)")
print("  Public token: 20 chars (expected: 40-64)")
print("  API key: 18 chars (expected: 40-64)")
print("  Client secret: 50 chars ✓")

print("\nDiagnosis:")
print("  All tokens are shorter than expected for Eventbrite OAuth tokens.")
print("  This suggests one of the following:")
print("    1. Your app is newly created and needs 24-48 hours for activation")
print("    2. Your Eventbrite account needs email verification")
print("    3. Your app needs manual approval from Eventbrite")
print("    4. You're on a free/trial account with limited API access")

print("\nRecommended actions:")
print("  1. Check your email for Eventbrite verification/approval messages")
print("  2. Visit: https://www.eventbrite.com/account-settings/apps")
print("  3. Look for any 'Pending', 'Under Review', or warning messages")
print("  4. If nothing works, contact Eventbrite support: support@eventbrite.com")
print("     Tell them: 'New OAuth app returning 403 on all API endpoints'")

print("\n" + "=" * 70)
