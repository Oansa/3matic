import httpx
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

async def setup_telegram_webhook(bot_token: str, community_id: str) -> bool:
    """Setup Telegram webhook"""
    webhook_url = f"{BASE_URL}/api/webhooks/telegram/{community_id}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"https://api.telegram.org/bot{bot_token}/setWebhook",
                params={"url": webhook_url}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error setting up Telegram webhook: {e}")
            return False

async def send_telegram_message(bot_token: str, chat_id: str, message: str) -> bool:
    """Send message via Telegram"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": message}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False

