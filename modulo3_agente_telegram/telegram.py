import os
import requests


def send_telegram_message(message: str) -> dict:

    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message
    }

    response = requests.post(
        url,
        json=payload,
        timeout=30
    )

    response.raise_for_status()

    return response.json()