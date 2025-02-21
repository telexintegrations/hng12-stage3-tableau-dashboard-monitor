#!/usr/bin/env python3

import sys
import os
from datetime import datetime, UTC
from dotenv import load_dotenv

def check_prerequisites():
    """Check if all required packages are installed"""
    try:
        import tableauserverclient as TSC
    except ImportError:
        print("❌ Required package 'tableauserverclient' is not installed")
        print("Please install it using:")
        print("pip install tableauserverclient")
        sys.exit(1)
    return TSC

def clean_server_url(url):
    """Clean the server URL to remove unnecessary parts"""
    if not url:
        return url
    # Remove /#/site/ and anything after it
    if '/#/site/' in url:
        url = url.split('/#/site/')[0]
    # Remove trailing slash if present
    return url.rstrip('/')

def test_tableau_connection():
    # Load environment variables
    load_dotenv()

    # Get and clean server URL
    server_url = clean_server_url(os.getenv("TABLEAU_SERVER_HOST", "https://dub01.online.tableau.com"))

    # Check for required environment variables
    required_vars = {
        "TABLEAU_SERVER_HOST": server_url,
        "TABLEAU_API_TOKEN": os.getenv("TABLEAU_API_TOKEN"),
        "TABLEAU_SITE_NAME": os.getenv("TABLEAU_SITE_NAME", "emminexy-f537b42aad")
    }

    missing_vars = [var for var, value in required_vars.items() if not value]

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease add these to your .env file or export them directly.")
        sys.exit(1)

    TSC = check_prerequisites()

    print(f"Testing connection to Tableau Server")
    print(f"Server: {required_vars['TABLEAU_SERVER_HOST']}")
    print(f"Site: {required_vars['TABLEAU_SITE_NAME']}")
    print(f"Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Create server instance with specific API version
        server = TSC.Server(
            required_vars['TABLEAU_SERVER_HOST'],
            use_server_version=False,
            http_options={'verify': True}
        )

        # Set the API version explicitly to 3.16 (or higher)
        server.version = '3.16'

        # Create authentication object
        tableau_auth = TSC.PersonalAccessTokenAuth(
            token_name=os.getenv('TABLEAU_TOKEN_NAME', 'TelescopeMonitoring'),
            personal_access_token=required_vars['TABLEAU_API_TOKEN'],
            site_id=required_vars['TABLEAU_SITE_NAME']
        )

        # Sign in using the with statement
        with server.auth.sign_in_with_personal_access_token(tableau_auth):
            # Get server info
            server_info = server.server_info.get()
            print("✅ Connection successful!")
            print(f"Server version: {server_info.product_version}")
            print(f"API version: {server.version}")

            # Test view access
            all_views = list(TSC.Pager(server.views))
            print(f"Found {len(all_views)} views")

    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Verify your Tableau Server host is correct")
        print("   Current: " + required_vars['TABLEAU_SERVER_HOST'])
        print("   Expected format: https://dub01.online.tableau.com")
        print("\n2. Check if your API token is valid")
        print("   Make sure you have created a Personal Access Token in Tableau")
        print("\n3. Ensure your site name is correct")
        print("   Current: " + required_vars['TABLEAU_SITE_NAME'])
        print("\n4. API Version Information:")
        print("   Using API version: 3.16")
        print("   Required minimum version: 3.6")
        print("\n5. Verify network connectivity to Tableau Server")
        print("\nDebug Information:")
        print(f"Timestamp: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"User: cod-emminex")
        sys.exit(1)

if __name__ == "__main__":
    test_tableau_connection()
