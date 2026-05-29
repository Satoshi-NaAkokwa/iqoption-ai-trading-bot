"""
Risk Manager - Controls risk and validates trading decisions
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class RiskManager:
    """Manages trading risk and validates orders"""

    def __init__(
        self,
        max_position_size: float = 0.7,
        max_orders_per_side: int = 5,
        stop_price_deviation: float = 0.002,
        reference_price: float = 1.0
    ):
        self.max_position_size = max_position_size  # Never risk more than 70%
        self.max_orders_per_side = max_orders_per_side  # Limit concurrent orders
        self.stop_price_deviation = stop_price_deviation  # Stop if price moves 0.2%
        self.reference_price = reference_price  # Normal stablecoin price

        # Tracking
        self.total_trades = 0
        self.successful_trades = 0
        self.failed_trades = 0

    def validate_orders(self, orders: List[Dict], current_price: float, balance: float) -> bool:
        """
        Validate that orders are within risk limits

        Args:
            orders: List of orders to validate
            current_price: Current market price
            balance: Available balance

        Returns:
            True if orders are safe, False otherwise
        """
        # Check total investment doesn't exceed max position size
        total_investment = sum(
            order['quantity'] * order['price']
            for order in orders
            if order['side'] == 'BUY'
        )

        max_investment = balance * self.max_position_size
        if total_investment > max_investment:
            logger.error(f"Total investment ${total_investment:.2f} exceeds max ${max_investment:.2f}")
            return False

        # Check number of orders per side
        buy_orders = [o for o in orders if o['side'] == 'BUY']
        sell_orders = [o for o in orders if o['side'] == 'SELL']

        if len(buy_orders) > self.max_orders_per_side:
            logger.error(f"Too many buy orders: {len(buy_orders)} > {self.max_orders_per_side}")
            return False

        if len(sell_orders) > self.max_orders_per_side:
            logger.error(f"Too many sell orders: {len(sell_orders)} > {self.max_orders_per_side}")
            return False

        # Check price deviation (for stablecoins)
        if not self._is_price_stable(current_price):
            logger.error(f"Price {current_price:.4f} has deviated too far from {self.reference_price:.4f}")
            return False

        logger.info(f"Orders validated: {len(orders)} orders, ${total_investment:.2f} investment")
        return True

    def _is_price_stable(self, current_price: float) -> bool:
        """Check if price is within acceptable deviation from reference"""
        deviation = abs(current_price - self.reference_price)
        return deviation <= self.stop_price_deviation

    def should_stop_trading(self, current_price: float) -> Tuple[bool, str]:
        """
        Check if trading should be stopped due to market conditions

        Args:
            current_price: Current market price

        Returns:
            Tuple of (should_stop, reason)
        """
        if not self._is_price_stable(current_price):
            deviation = abs(current_price - self.reference_price)
            reason = f"Price deviation {deviation:.6f} exceeds limit {self.stop_price_deviation}"
            return True, reason

        return False, ""

    def validate_single_order(self, order: Dict, balance: float, current_price: float) -> bool:
        """
        Validate a single order before placing it

        Args:
            order: Order to validate
            balance: Available balance
            current_price: Current market price

        Returns:
            True if order is safe, False otherwise
        """
        # Check if we have enough balance for buy orders
        if order['side'] == 'BUY':
            required = order['quantity'] * order['price']
            max_required = balance * self.max_position_size

            if required > max_required:
                logger.warning(f"Order requires ${required:.2f}, max allowed ${max_required:.2f}")
                return False

        # Check price is reasonable (for stablecoins)
        if not self._is_price_stable(order['price']):
            logger.warning(f"Order price {order['price']:.4f} outside stable range")
            return False

        return True

    def record_trade(self, success: bool):
        """Record trade outcome for tracking"""
        self.total_trades += 1
        if success:
            self.successful_trades += 1
        else:
            self.failed_trades += 1

    def get_statistics(self) -> Dict:
        """Get risk management statistics"""
        success_rate = 0
        if self.total_trades > 0:
            success_rate = (self.successful_trades / self.total_trades) * 100

        return {
            'total_trades': self.total_trades,
            'successful_trades': self.successful_trades,
            'failed_trades': self.failed_trades,
            'success_rate': success_rate,
            'max_position_size': self.max_position_size,
            'max_orders_per_side': self.max_orders_per_side
        }

    def reset_statistics(self):
        """Reset trade statistics"""
        self.total_trades = 0
        self.successful_trades = 0
        self.failed_trades = 0
        logger.info("Risk manager statistics reset")