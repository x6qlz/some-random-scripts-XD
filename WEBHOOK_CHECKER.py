import requests

def check_webhook_status(webhook_url):
    """Check the status of a Discord webhook."""
    payload = {
        "content": "Test"
    }

    try:
        
        response = requests.post(webhook_url, json=payload)

        
        if response.status_code == 204:
            print(f"Webhook is active: {webhook_url}")
        else:
            print(f"Failed to send message to {webhook_url}: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error checking {webhook_url}: {e}")

def main():
    
    webhooks = [
        "ur webhook",
        "webhook",  
        "hook",  
    ]

    for webhook in webhooks:
        
        if webhook and webhook.startswith("http"):
            check_webhook_status(webhook)
        else:
            print(f"Invalid or empty webhook URL skipped: {webhook}")

if __name__ == "__main__":
    main()
