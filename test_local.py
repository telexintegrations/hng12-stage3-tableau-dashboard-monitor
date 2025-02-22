#!/usr/bin/env python3

import os
import json
import requests
from datetime import datetime, UTC
from dotenv import load_dotenv

def test_environment():
    """Test environment variables"""
    # Load environment variables from .env file
    load_dotenv()

    required_vars = {
        'TABLEAU_API_TOKEN': os.getenv('TABLEAU_API_TOKEN'),
        'TABLEAU_SERVER_HOST': os.getenv('TABLEAU_SERVER_HOST'),
        'TABLEAU_SITE_NAME': os.getenv('TABLEAU_SITE_NAME'),
        'TABLEAU_TOKEN_NAME': os.getenv('TABLEAU_TOKEN_NAME')
    }

    print("Current Environment Variables:")
    print("-" * 50)
    for var, value in required_vars.items():
        masked_value = "***" if var == 'TABLEAU_API_TOKEN' and value else 'Not Set'
        print(f"{var}: {masked_value if var == 'TABLEAU_API_TOKEN' else value or 'Not Set'}")
    print("-" * 50)

    missing = [var for var, value in required_vars.items() if not value]

    if missing:
        print("\n❌ Missing environment variables:")
        for var in missing:
            print(f"  - {var}")
        return False

    print("\n✅ All required environment variables are set")
    return True

def test_api():
    """Test the API endpoint"""
    url = "https://hng12-stage3-tableau-dashboard-monitor.vercel.app/api/monitor"
    current_time = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')

    print(f"\nTesting API at: {url}")
    print(f"Time: {current_time}")
    print(f"User: cod-emminex")
    print("-" * 50)

    try:
        response = requests.get(url)
        print(f"\nStatus Code: {response.status_code}")

        print("\nResponse Headers:")
        for key, value in response.headers.items():
            print(f"{key}: {value}")

        print("\nResponse Body:")
        data = response.json()
        print(json.dumps(data, indent=2))

        if data.get('success'):
            print("\n✅ API check successful!")
            print(f"Total Views: {data.get('total_views', 'N/A')}")
            print(f"Server: {data.get('server_url', 'N/A')}")
            print(f"Site: {data.get('site_name', 'N/A')}")
        else:
            print("\n❌ API returned error:")
            print(f"Error: {data.get('error')}")
            print(f"Debug Info: {data.get('debug_info', {})}")

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")

def verify_env_file():
    """Verify .env file contents"""
    try:
        with open('.env', 'r') as f:
            env_contents = f.read().strip()

        print("Verifying .env file:")
        print("-" * 50)

        expected_vars = [
            'TABLEAU_SERVER_HOST',
            'TABLEAU_API_TOKEN',
            'TABLEAU_SITE_NAME',
            'TABLEAU_TOKEN_NAME',
            'LOAD_TIME_THRESHOLD'
        ]

        found_vars = []
        for line in env_contents.split('\n'):
            if '=' in line:
                var_name = line.split('=')[0]
                found_vars.append(var_name)

        missing_vars = set(expected_vars) - set(found_vars)

        if missing_vars:
            print("❌ Missing variables in .env file:")
            for var in missing_vars:
                print(f"  - {var}")
        else:
            print("✅ All expected variables found in .env file")

    except FileNotFoundError:
        print("❌ .env file not found")
    except Exception as e:
        print(f"❌ Error reading .env file: {str(e)}")

if __name__ == "__main__":
    print(f"Current Date and Time (UTC): {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Current User's Login: cod-emminex")
    print("-" * 50)

    verify_env_file()
    print("\n")

    if test_environment():
        test_api()
