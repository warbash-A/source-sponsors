#!/usr/bin/env python3
"""Test all Eventbrite credentials systematically"""

import requests

credentials = {
    "Private token": "BNU7XQLE3O3FGGQ7VATY",
    "Public token": "ZUKT3OVADHMDTGUKBTOH",
    "API key": "VCUBJ6XZCART2UYN3D",
    "Client secret": "QZ45E5B7PATD2NFQXTKHALHFD5C4KVVUJGSRKCRQNHWBWIYLOV"
}

print("=" * 70)
print("TESTING ALL EVENTBRITE CREDENTIALS")
print("=" * 70)

for name, token in credentials.items():
    print(f"\n{name}: {token[:10]}... ({len(token)} chars)")
    print("-" * 70)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            "https://www.eventbriteapi.com/v3/users/me",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✓ SUCCESS! User: {data.get('name', 'Unknown')}")
            print(f"✓ Email: {data.get('emails', [{}])[0].get('email', 'N/A')}")
            print(f"\n*** THIS TOKEN WORKS! Use: {name} = {token}")
            break
        else:
            print(f"✗ Failed: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"✗ Exception: {str(e)}")

print("\n" + "=" * 70)
