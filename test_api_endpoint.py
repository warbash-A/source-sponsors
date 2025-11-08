#!/usr/bin/env python3
"""Test Eventbrite API endpoint and parameters"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('EVENTBRITE_API_KEY')

print("Testing Eventbrite API v3 Endpoint")
print("=" * 60)
print(f"API Key: {api_key}")
print()

# Test different endpoint variations
endpoints = [
    "https://www.eventbriteapi.com/v3/events/search/",  # with trailing slash
    "https://www.eventbriteapi.com/v3/events/search",   # without trailing slash
]

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Test query with spaces
test_queries = [
    "event IT/AI",  # with space
    "event+IT/AI",  # manually encoded with +
    "technology conference",  # simple query
]

for endpoint in endpoints:
    print(f"\nTesting endpoint: {endpoint}")
    print("-" * 60)

    for query in test_queries:
        params = {
            'q': query,
            'page_size': 5
        }

        print(f"\nQuery: '{query}'")

        try:
            response = requests.get(
                endpoint,
                headers=headers,
                params=params,
                timeout=10
            )

            print(f"  Status: {response.status_code}")
            print(f"  URL: {response.url}")

            if response.status_code == 200:
                data = response.json()
                events = data.get('events', [])
                print(f"  ✓ Success! Found {len(events)} events")
                if events:
                    print(f"  First event: {events[0].get('name', {}).get('text', 'N/A')}")
            elif response.status_code == 404:
                print(f"  ✗ 404 Not Found")
            elif response.status_code == 403:
                print(f"  ✗ 403 Forbidden")
            else:
                print(f"  ✗ Error: {response.text[:100]}")

        except Exception as e:
            print(f"  ✗ Exception: {str(e)}")

print("\n" + "=" * 60)
print("Recommended Configuration:")
print("  Endpoint: https://www.eventbriteapi.com/v3/events/search")
print("  Method: GET")
print("  Auth: Bearer token in Authorization header")
print("  Query param: 'q' with plain text (spaces OK, requests will encode)")
