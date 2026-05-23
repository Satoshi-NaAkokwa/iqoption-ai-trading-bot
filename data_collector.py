"""
Data Collector for IQ Option API
Fetches real-time market data via WebSocket
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time

try:
    from iqoptionapi.stable_api import IQ_Option
except ImportError:
    IQ_Option = None

logger = logging.getLogger(__name__)

class DataCollector:
    """Collects real-time market data from IQ Option"""

    def __init__(self, email: str, password: str, demo_mode: bool = True):
        """
        Initialize data collector

        Args:
            email: IQ Option email
            password: IQ Option password
            demo_mode: Use demo account
        """
        if IQ_Option is None:
            raise ImportError("iqoptionapi library not installed. Run: pip install iqoptionapi")

        self.email = email
        self.password = password
        self.demo_mode = demo_mode
        self.api = None
        self.connected = False
        self.assets = {}

        logger.info(f"DataCollector initialized (demo_mode={demo_mode})")

    def connect(self) -> bool:
        """
        Connect to IQ Option API

        Returns:
            True if successful, False otherwise
        """
        try:
            self.api = IQ_Option(self.email, self.password)
            check, reason = self.api.connect()

            if check:
                self.connected = True
                logger.info("Connected to IQ Option API")

                # Set demo/practice mode
                self.api.change_balance(self.demo_mode + 1)  # 1 for demo, 2 for real

                # Get account info
                account_type = self.api.get_balance_mode()
                balance = self.api.get_balance()
                logger.info(f"Account type: {'Demo' if account_type == 'PRACTICE' else 'Real'}, Balance: {balance}")

                return True
            else:
                logger.error(f"Failed to connect: {reason}")
                return False

        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from IQ Option API"""
        if self.api and self.connected:
            self.api.api.close()
            self.connected = False
            logger.info("Disconnected from IQ Option API")

    def get_available_assets(self) -> List[str]:
        """
        Get list of available trading assets

        Returns:
            List of asset names
        """
        if not self.connected:
            logger.error("Not connected to API")
            return []

        try:
            all_assets = self.api.get_all_open_time()
            forex_assets = []

            for asset_name, asset_info in all_assets.get("forex", {}).items():
                if asset_info.get("open", False):
                    forex_assets.append(asset_name)

            logger.info(f"Available forex assets: {len(forex_assets)}")
            return forex_assets

        except Exception as e:
            logger.error(f"Error getting assets: {e}")
            return []

    def get_candles(self, asset: str, timeframe: str, count: int = 100) -> Optional[List[Dict]]:
        """
        Get historical candle data

        Args:
            asset: Asset name (e.g., "EUR/USD")
            timeframe: Timeframe (e.g., "1M", "5M", "15M")
            count: Number of candles to fetch

        Returns:
            List of candle data or None
        """
        if not self.connected:
            logger.error("Not connected to API")
            return None

        try:
            # Convert timeframe to seconds
            timeframe_map = {
                "1M": 60,
                "5M": 300,
                "15M": 900,
                "30M": 1800,
                "1H": 3600,
                "4H": 14400,
                "1D": 86400
            }

            timeframe_seconds = timeframe_map.get(timeframe, 60)

            # Get candles
            candles = self.api.get_candles(
                asset,
                timeframe_seconds,
                count,
                datetime.now().timestamp()
            )

            if candles:
                logger.debug(f"Fetched {len(candles)} candles for {asset} ({timeframe})")
                return candles
            else:
                logger.warning(f"No candles returned for {asset} ({timeframe})")
                return []

        except Exception as e:
            logger.error(f"Error getting candles for {asset}: {e}")
            return None

    def get_current_price(self, asset: str) -> Optional[float]:
        """
        Get current price for an asset

        Args:
            asset: Asset name

        Returns:
            Current price or None
        """
        if not self.connected:
            logger.error("Not connected to API")
            return None

        try:
            # Get latest candle
            candles = self.get_candles(asset, "1M", 1)
            if candles and len(candles) > 0:
                return candles[0].get("close")
            return None

        except Exception as e:
            logger.error(f"Error getting current price for {asset}: {e}")
            return None

    def get_account_balance(self) -> float:
        """
        Get account balance

        Returns:
            Current balance
        """
        if not self.connected:
            logger.error("Not connected to API")
            return 0.0

        try:
            return self.api.get_balance()
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return 0.0

    def get_active_positions(self) -> List[Dict]:
        """
        Get currently open positions

        Returns:
            List of open positions
        """
        if not self.connected:
            logger.error("Not connected to API")
            return []

        try:
            positions = self.api.get_positions()
            return positions
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []

    def subscribe_candles(self, asset: str, timeframe: str):
        """
        Subscribe to real-time candle data

        Args:
            asset: Asset name
            timeframe: Timeframe
        """
        if not self.connected:
            logger.error("Not connected to API")
            return

        try:
            timeframe_map = {
                "1M": 60,
                "5M": 300,
                "15M": 900,
                "30M": 1800,
                "1H": 3600
            }

            timeframe_seconds = timeframe_map.get(timeframe, 60)

            # Subscribe to candles
            self.api.start_candles(asset, timeframe_seconds, 1)

            logger.info(f"Subscribed to {asset} candles ({timeframe})")

        except Exception as e:
            logger.error(f"Error subscribing to candles: {e}")

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()