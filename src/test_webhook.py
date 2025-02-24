from datetime import datetime, UTC
import requests
import json

def test_webhook():
    webhook_url = "https://ping.telex.im/v1/webhooks/01952fe5-d4fd-7bde-bcd2-7a2fd2c55c87"
    current_time = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')

    # Updated payload structure according to Telex requirements
    payload = {
        "event_name": "tableau_monitor",  # Required
        "username": "cod-emminex",        # Required
        "status": "active",               # Required
        "message": "Tableau integration webhook test"  # Required
    }

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        print(f"Webhook test status code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 202:
            try:
                response_data = response.json()
                if "status" in response_data and response_data["status"] == "error":
                    print("\nError Details:")
                    print("Required fields:")
                    print("- event_name: Name of the event")
                    print("- username: Your username (cod-emminex)")
                    print("- status: Current status")
                    print("- message: Descriptive message")
                    return False
            except json.JSONDecodeError:
                pass

        return response.status_code == 202 and "error" not in response.text.lower()

    except Exception as e:
        print(f"Error testing webhook: {str(e)}")
        return False

if __name__ == "__main__":
    test_webhook()
