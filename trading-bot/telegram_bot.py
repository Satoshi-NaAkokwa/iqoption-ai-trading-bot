#!/usr/bin/env python3
"""
Telegram Bot for Trading Bot Monitoring
Send alerts and status updates via Telegram
"""

import logging
import requests
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot for sending trading bot notifications"""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(self, message: str) -> bool:
        """Send a message to the configured chat"""
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get('ok'):
                logger.info(f"Telegram message sent successfully")
                return True
            else:
                logger.error(f"Telegram API error: {result}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    def send_trade_alert(self, trade_type: str, price: float, quantity: float, pnl: float = 0.0):
        """Send a trade execution alert"""
        emoji = "🟢" if pnl >= 0 else "🔴"
        message = (
            f"{emoji} <b>TRADE EXECUTED</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<b>Type:</b> {trade_type}\n"
            f"<b>Price:</b> ${price:.4f}\n"
            f"<b>Quantity:</b> {quantity:.4f}\n"
            f"<b>P&L:</b> ${pnl:.4f}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return self.send_message(message)

    def send_daily_report(self, stats: dict):
        """Send daily performance report"""
        message = (
            f"📊 <b>DAILY TRADING REPORT</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<b>Total Trades:</b> {stats.get('total_trades', 0)}\n"
            f"<b>Success Rate:</b> {stats.get('success_rate', 0):.1f}%\n"
            f"<b>Net P&L:</b> ${stats.get('pnl', 0):.2f}\n"
            f"<b>Sharpe Ratio:</b> {stats.get('sharpe_ratio', 0):.2f}\n"
            f"<b>Max Drawdown:</b> {stats.get('max_drawdown', 0)*100:.2f}%\n"
            f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}"
        )
        return self.send_message(message)

    def send_error_alert(self, error: str):
        """Send an error alert"""
        message = (
            f"🚨 <b>TRADING BOT ERROR</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<b>Error:</b> {error}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}\n"
            f"<b>Action:</b> Please check the bot logs"
        )
        return self.send_message(message)

    def send_status_update(self, status: str, price: float, balance: dict):
        """Send periodic status update"""
        message = (
            f"🔄 <b>BOT STATUS UPDATE</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<b>Status:</b> {status}\n"
            f"<b>Current Price:</b> ${price:.4f}\n"
            f"<b>USDT Balance:</b> ${balance.get('USDT', 0):.2f}\n"
            f"<b>USDC Balance:</b> {balance.get('USDC', 0):.4f}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return self.send_message(message)

    def test_connection(self) -> bool:
        """Test if Telegram bot is working"""
        message = (
            f"✅ <b>TRADING BOT ONLINE</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<b>Status:</b> Connected\n"
            f"<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"<b>Message:</b> Trading bot is now monitoring USDT/USDC grid trading"
        )
        return self.send_message(message)


def setup_telegram_bot(bot_token: str = None, chat_id: str = None) -> Optional[TelegramBot]:
    """
    Setup Telegram bot for monitoring

    Args:
        bot_token: Telegram bot token from BotFather
        chat_id: Your Telegram chat ID

    Returns:
        TelegramBot instance if configured, None otherwise
    """
    if not bot_token or not chat_id:
        logger.warning("Telegram credentials not provided. Monitoring disabled.")
        return None

    bot = TelegramBot(bot_token, chat_id)
    if bot.test_connection():
        logger.info("Telegram bot successfully configured")
        return bot
    else:
        logger.error("Failed to connect to Telegram bot")
        return None


if __name__ == "__main__":
    # Test the Telegram bot
    print("Telegram Bot Testing")
    print("="*60)
    print()
    print("To use Telegram notifications:")
    print("1. Create a Telegram bot via @BotFather")
    print("2. Get your bot token")
    print("3. Get your chat ID (send a message to @userinfobot)")
    print("4. Add to .env:")
    print("   TELEGRAM_BOT_TOKEN=your_bot_token")
    print("   TELEGRAM_CHAT_ID=your_chat_id")
    print()
    print("Example:")
    print("   bot = setup_telegram_bot('123456:ABC-DEF...', '123456789')")
    print("   bot.send_status_update('RUNNING', 1.0001, {'USDT': 1000, 'USDC': 1000})")
    print("="*60)