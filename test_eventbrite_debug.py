#!/usr/bin/env python3
"""Debug test for Eventbrite API with different auth methods"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv('EVENTBRITE_API_KEY')
private_token = os.getenv('EVENTBRITE_API_KEY')
public_token = os.getenv('EVENTBRITE_PUBLIC_TOKEN')

print(f"Testing Eventbrite API credentials...")
print("=" * 60)
print(f"Private token: {private_token}")
print(f"Public token: {public_token}")
print("=" * 60)

# Test 1: Bearer token authentication (standard OAuth)
print("\nTest 1: Bearer token authentication (OAuth standard)")
headers = {
    "Authorization": f"Bearer {private_token}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(
        "https://www.eventbriteapi.com/v3/users/me",
        headers=headers,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✓ Success! User info: {response.json()}")
    else:
        print(f"✗ Error: {response.text}")
except Exception as e:
    print(f"✗ Exception: {str(e)}")

# Test 2: Token as query parameter
print("\n" + "=" * 60)
print("\nTest 2: Token as query parameter")

try:
    response = requests.get(
        "https://www.eventbriteapi.com/v3/users/me",
        params={"token": private_token},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✓ Success! User info: {response.json()}")
    else:
        print(f"✗ Error: {response.text}")
except Exception as e:
    print(f"✗ Exception: {str(e)}")

# Test 3: Check if credentials are from Eventbrite's new API
print("\n" + "=" * 60)
print("\nTest 3: Testing public events endpoint (no auth)")

try:
    response = requests.get(
        "https://www.eventbriteapi.com/v3/events/search",
        params={"location.address": "San Francisco"},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"✗ Exception: {str(e)}")

print("\n" + "=" * 60)
print("\nDebugging Info:")
print(f"Private token length: {len(private_token)} chars")
print(f"Expected length: 40-64 chars for valid OAuth tokens")
print(f"Token format looks valid: {private_token.isalnum()}")
