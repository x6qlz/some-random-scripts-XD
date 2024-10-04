import requests
import json
import time

def send_to_discord(webhook_url, message):
    
    payload = {
        "content": message
    }

    try:
        
        response = requests.post(webhook_url, json=payload)

        
        if response.status_code == 204:
            print("message sent")
        else:
            print(f"Failed to send message: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")


webhook_url = "ur webhook"


message = "ur message"

try:
    while True:
        send_to_discord(webhook_url, message)
        
        time.sleep(HOW LONG UNTIL IT RESENDS)  

except KeyboardInterrupt:
    print("stopped")
