#!/usr/bin/env python3
"""Quick test of Eventbrite API credentials"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv('EVENTBRITE_API_KEY')

print(f"Testing Eventbrite API with key: {api_key[:10]}...")
print("=" * 60)

# Test 1: Get categories
print("\nTest 1: Fetching categories...")
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(
        "https://www.eventbriteapi.com/v3/categories/",
        headers=headers,
        timeout=10
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")

    if response.status_code == 200:
        data = response.json()
        categories = data.get('categories', [])
        print(f"✓ Success! Found {len(categories)} categories")
        if categories:
            print(f"\nFirst 3 categories:")
            for cat in categories[:3]:
                print(f"  - [{cat.get('id')}] {cat.get('name')}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"✗ Exception: {str(e)}")

# Test 2: Search events
print("\n" + "=" * 60)
print("\nTest 2: Searching for tech events...")

try:
    response = requests.get(
        "https://www.eventbriteapi.com/v3/events/search/",
        headers=headers,
        params={"q": "technology", "page_size": 3},
        timeout=10
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        events = data.get('events', [])
        print(f"✓ Success! Found {data.get('pagination', {}).get('object_count', 0)} total events")
        print(f"\nShowing first {len(events)} events:")
        for event in events:
            name = event.get('name', {}).get('text', 'Unknown')
            print(f"  - {name}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"✗ Exception: {str(e)}")

print("\n" + "=" * 60)
