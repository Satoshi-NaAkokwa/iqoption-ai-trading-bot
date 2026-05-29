"""
Binance API Client - Handles all Binance API interactions
"""

import time
import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class BinanceClient:
    """Robust Binance API client with rate limiting and error handling"""

    def __init__(self, api_key: str, secret_key: str, testnet: bool = False):
        self.client = Client(api_key, secret_key, testnet=testnet)
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests to avoid rate limiting

    def _rate_limit(self):
        """Prevent API rate limiting"""
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()

    def get_current_price(self, symbol: str = 'USDCUSDT') -> float:
        """Get current price for a trading pair"""
        self._rate_limit()
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            logger.debug(f"Current price for {symbol}: {price}")
            return price
        except BinanceAPIException as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            if e.code == -1121:  # Invalid symbol
                raise ValueError(f"Invalid trading pair: {symbol}")
            raise

    def get_account_balance(self, asset: str = 'USDT') -> float:
        """Get available balance for an asset"""
        self._rate_limit()
        try:
            account = self.client.get_account()
            for balance in account['balances']:
                if balance['asset'] == asset:
                    available = float(balance['free'])
                    logger.debug(f"Available {asset}: {available}")
                    return available
            return 0.0
        except BinanceAPIException as e:
            logger.error(f"Error getting account balance: {e}")
            raise

    def get_open_orders(self, symbol: str = 'USDCUSDT') -> List[Dict]:
        """Get all open orders for a symbol"""
        self._rate_limit()
        try:
            orders = self.client.get_open_orders(symbol=symbol)
            logger.debug(f"Open orders for {symbol}: {len(orders)}")
            return orders
        except BinanceAPIException as e:
            logger.error(f"Error getting open orders: {e}")
            raise

    def cancel_all_orders(self, symbol: str = 'USDCUSDT') -> int:
        """Cancel all open orders for a symbol"""
        self._rate_limit()
        try:
            orders = self.client.get_open_orders(symbol=symbol)
            canceled = 0
            for order in orders:
                try:
                    self.client.cancel_order(symbol=symbol, orderId=order['orderId'])
                    canceled += 1
                    logger.info(f"Canceled order {order['orderId']}")
                except BinanceAPIException as e:
                    logger.warning(f"Failed to cancel order {order['orderId']}: {e}")
            logger.info(f"Canceled {canceled} orders for {symbol}")
            return canceled
        except BinanceAPIException as e:
            logger.error(f"Error canceling orders: {e}")
            raise

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> Optional[Dict]:
        """
        Place a limit order

        Args:
            symbol: Trading pair (e.g., USDCUSDT)
            side: 'BUY' or 'SELL'
            quantity: Amount to buy/sell
            price: Limit price

        Returns:
            Order details if successful, None otherwise
        """
        self._rate_limit()
        try:
            order = self.client.order_limit(
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=f"{price:.4f}",  # Stablecoins need 4 decimal places
                timeInForce='GTC'  # Good Till Cancelled
            )
            logger.info(f"Placed {side} order: {quantity} {symbol.split('USDT')[0]} @ {price:.4f}")
            return order
        except BinanceAPIException as e:
            if e.code == -2010:  # Insufficient balance
                logger.warning(f"Insufficient balance for {side} order")
                return None
            elif e.code == -1013:  # Filter failure (price/quantity precision)
                logger.warning(f"Filter failure for {side} order: {e}")
                return None
            logger.error(f"Error placing {side} order: {e}")
            raise
        except BinanceOrderException as e:
            logger.error(f"Order exception for {side} order: {e}")
            raise

    def get_order_status(self, symbol: str, order_id: int) -> Dict:
        """Get status of a specific order"""
        self._rate_limit()
        try:
            order = self.client.get_order(symbol=symbol, orderId=order_id)
            return order
        except BinanceAPIException as e:
            logger.error(f"Error getting order status: {e}")
            raise

    def get_trade_history(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Get recent trade history"""
        self._rate_limit()
        try:
            trades = self.client.get_my_trades(symbol=symbol, limit=limit)
            return trades
        except BinanceAPIException as e:
            logger.error(f"Error getting trade history: {e}")
            raise