#!/usr/bin/env python3

import requests
import json
from datetime import datetime, UTC

def test_monitor_endpoint():
    print(f"Testing Tableau Monitor API")
    print(f"Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"User: cod-emminex")
    print("-" * 50)

    # Replace with your Vercel deployment URL
    url = "https://hng12-stage3-tableau-dashboard-monitor.vercel.app/api/monitor"

    try:
        print(f"Making request to: {url}")
        response = requests.get(url)

        print(f"\nStatus Code: {response.status_code}")
        print("Response Headers:")
        for key, value in response.headers.items():
            print(f"{key}: {value}")

        print("\nResponse Body:")
        try:
            data = response.json()
            print(json.dumps(data, indent=2))

            if data.get('success'):
                print("\n✅ API is working correctly!")
            else:
                print("\n❌ API returned failure status")
                if 'error' in data:
                    print(f"Error: {data['error']}")

        except json.JSONDecodeError:
            print("❌ Could not parse JSON response")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {str(e)}")

    print("\nTest completed at:", datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == "__main__":
    test_monitor_endpoint()
