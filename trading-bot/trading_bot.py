"""
Main Grid Trading Bot - Orchestrates the entire trading process
"""

import time
import logging
import os
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv

from binance_client import BinanceClient
from grid_manager import GridManager
from risk_manager import RiskManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class GridTradingBot:
    """Main grid trading bot orchestrator"""

    def __init__(self, config_path: str = '.env'):
        # Load configuration
        load_dotenv(config_path)

        # Validate required configuration
        self._validate_config()

        # Initialize components
        self.api_client = BinanceClient(
            api_key=os.getenv('BINANCE_API_KEY'),
            secret_key=os.getenv('BINANCE_SECRET_KEY'),
            testnet=os.getenv('TESTNET', 'false').lower() == 'true'
        )

        self.grid_manager = GridManager(
            grid_size=float(os.getenv('GRID_SIZE', 0.0001)),
            total_investment=float(os.getenv('TOTAL_INVESTMENT', 100)),
            grid_levels=int(os.getenv('GRID_LEVELS', 20))
        )

        self.risk_manager = RiskManager(
            max_position_size=float(os.getenv('MAX_POSITION_SIZE', 0.7)),
            max_orders_per_side=int(os.getenv('MAX_ORDERS_PER_SIDE', 5)),
            stop_price_deviation=float(os.getenv('STOP_PRICE_DEVIATION', 0.002)),
            reference_price=1.0
        )

        # Bot configuration
        self.trading_pair = os.getenv('TRADING_PAIR', 'USDCUSDT')
        self.check_interval = int(os.getenv('CHECK_INTERVAL', 30))
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'

        # State tracking
        self.running = False
        self.price_history = []
        self.start_time = None

        logger.info("="*50)
        logger.info("Grid Trading Bot Initialized")
        logger.info(f"Trading Pair: {self.trading_pair}")
        logger.info(f"Dry Run: {self.dry_run}")
        logger.info(f"Grid Size: {self.grid_manager.grid_size}")
        logger.info(f"Investment: ${self.grid_manager.total_investment}")
        logger.info("="*50)

    def _validate_config(self):
        """Validate that required configuration is present"""
        required_vars = ['BINANCE_API_KEY', 'BINANCE_SECRET_KEY']
        missing = [var for var in required_vars if not os.getenv(var)]

        if missing:
            raise ValueError(f"Missing required configuration: {missing}")

    def start(self):
        """Start the trading bot"""
        self.running = True
        self.start_time = datetime.now()
        logger.info("Bot started, entering main loop...")

        try:
            # Cancel any existing orders
            if not self.dry_run:
                logger.info("Canceling existing orders...")
                self.api_client.cancel_all_orders(self.trading_pair)
            else:
                logger.info("DRY RUN: Would cancel existing orders")

            # Main trading loop
            while self.running:
                try:
                    self._trading_iteration()
                except Exception as e:
                    logger.error(f"Error in trading iteration: {e}")
                    time.sleep(self.check_interval * 2)  # Wait longer on error

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        finally:
            self.stop()

    def _trading_iteration(self):
        """Execute one iteration of the trading loop"""
        try:
            # Get current market data
            current_price = self.api_client.get_current_price(self.trading_pair)
            logger.debug(f"Current price: {current_price:.4f}")

            # Update price history for volatility calculation
            self.price_history.append(current_price)
            if len(self.price_history) > 100:  # Keep last 100 prices
                self.price_history.pop(0)

            # Optimize grid spacing based on volatility
            if len(self.price_history) >= 10:
                self.grid_manager.optimize_grid_spacing(self.price_history)

            # Check if we should stop trading due to market conditions
            should_stop, reason = self.risk_manager.should_stop_trading(current_price)
            if should_stop:
                logger.error(f"STOPPING TRADING: {reason}")
                self.running = False
                return

            # Get existing orders
            open_orders = self.api_client.get_open_orders(self.trading_pair) if not self.dry_run else []
            logger.info(f"Open orders: {len(open_orders)}")

            # Get grid status
            grid_status = self.grid_manager.get_grid_status(current_price, open_orders)
            logger.info(f"Grid status: {grid_status}")

            # Calculate new grid orders
            new_orders = self.grid_manager.calculate_grid_orders(current_price)

            # Validate orders
            balance = self.api_client.get_account_balance('USDT') if not self.dry_run else self.grid_manager.total_investment
            if not self.risk_manager.validate_orders(new_orders, current_price, balance):
                logger.warning("Orders failed risk validation")
                return

            # Place orders (if dry run, just log)
            if self.dry_run:
                logger.info(f"DRY RUN: Would place {len(new_orders)} orders")
                self._log_orders(new_orders)
            else:
                self._place_orders(new_orders, open_orders)

            # Log statistics periodically
            self._log_statistics(current_price)

        except Exception as e:
            logger.error(f"Error in trading iteration: {e}")
            raise

    def _place_orders(self, new_orders: List[Dict], existing_orders: List[Dict]):
        """Place new orders that don't conflict with existing ones"""
        placed = 0
        for order in new_orders:
            # Check if we should place this order
            if not self.grid_manager.should_place_order(
                float(existing_orders[0]['price']) if existing_orders else 1.0,
                order,
                existing_orders
            ):
                continue

            # Validate single order
            current_price = self.api_client.get_current_price(self.trading_pair)
            if not self.risk_manager.validate_single_order(
                order,
                self.api_client.get_account_balance('USDT'),
                current_price
            ):
                continue

            # Place the order
            result = self.api_client.place_limit_order(
                symbol=self.trading_pair,
                side=order['side'],
                quantity=order['quantity'],
                price=order['price']
            )

            if result:
                placed += 1
                self.risk_manager.record_trade(True)
            else:
                self.risk_manager.record_trade(False)

        logger.info(f"Placed {placed} new orders")

    def _log_orders(self, orders: List[Dict]):
        """Log orders (for dry run mode)"""
        for order in orders:
            logger.info(
                f"{'BUY' if order['side'] == 'BUY' else 'SELL'} "
                f"{order['quantity']:.4f} @ {order['price']:.4f} "
                f"(Level: {order['grid_level']})"
            )

    def _log_statistics(self, current_price: float):
        """Log bot statistics"""
        runtime = datetime.now() - self.start_time if self.start_time else "N/A"
        risk_stats = self.risk_manager.get_statistics()

        logger.info("-" * 50)
        logger.info(f"Runtime: {runtime}")
        logger.info(f"Current Price: {current_price:.4f}")
        logger.info(f"Total Trades: {risk_stats['total_trades']}")
        logger.info(f"Success Rate: {risk_stats['success_rate']:.2f}%")
        logger.info(f"Failed Trades: {risk_stats['failed_trades']}")
        logger.info("-" * 50)

    def stop(self):
        """Stop the trading bot"""
        logger.info("Stopping bot...")
        self.running = False

        # Cancel all orders
        if not self.dry_run:
            try:
                canceled = self.api_client.cancel_all_orders(self.trading_pair)
                logger.info(f"Canceled {canceled} orders on shutdown")
            except Exception as e:
                logger.error(f"Error canceling orders on shutdown: {e}")

        # Log final statistics
        logger.info("="*50)
        logger.info("Bot stopped")
        logger.info(f"Total runtime: {datetime.now() - self.start_time if self.start_time else 'N/A'}")
        logger.info(f"Risk stats: {self.risk_manager.get_statistics()}")
        logger.info("="*50)


def main():
    """Main entry point"""
    try:
        bot = GridTradingBot()
        bot.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()