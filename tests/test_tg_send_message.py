import unittest
from typing import Any
from unittest.mock import MagicMock, patch

from monitor.notifier.tg_send_message import send_telegram_message


class TestSendTelegramMessage(unittest.TestCase):
    @patch("monitor.notifier.tg_send_message.requests.get")
    def test_send_message_success(self: Any, mock_get: Any) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": True}
        mock_get.return_value = mock_response

        result = send_telegram_message("dummy_token", "dummy_chat", "Hello!")
        self.assertTrue(result)
        mock_get.assert_called_once()

    @patch("monitor.notifier.tg_send_message.requests.get")
    def test_send_message_failure(self: Any, mock_get: Any) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": False}
        mock_get.return_value = mock_response

        result = send_telegram_message("dummy_token", "dummy_chat", "Hello!")
        self.assertFalse(result)
        mock_get.assert_called_once()

    @patch("monitor.notifier.tg_send_message.requests.get")
    def test_send_message_no_ok_key(self: Any, mock_get: Any) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        result = send_telegram_message("dummy_token", "dummy_chat", "Hello!")
        self.assertFalse(result)
        mock_get.assert_called_once()
