import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = "https://your-app.onrender.com"  # apna Render app URL daalo

def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    webhook_url = f"{RENDER_URL}/{BOT_TOKEN}"
    response = requests.get(url, params={"url": webhook_url})
    print("Webhook set response:", response.json())

if __name__ == "__main__":
    set_webhook()
