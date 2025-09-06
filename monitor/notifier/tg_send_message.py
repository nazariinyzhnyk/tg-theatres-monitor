import requests


def send_telegram_message(bot_token: str, chat_id: str, message: str) -> bool:
    """
    Send a message to a Telegram group using a bot.
    Args:
        bot_token (str): The token of the Telegram bot.
        chat_id (str): The ID of the Telegram group.
        message (str): The message to send.
    Returns:
        bool: True if the message was sent successfully, False otherwise.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    response = requests.get(url, params=params)
    return response.json().get("ok", False)
