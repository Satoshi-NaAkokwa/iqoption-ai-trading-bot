"""
Grid Manager - Core grid trading strategy logic
"""

import logging
from typing import List, Dict, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class GridManager:
    """Manages grid trading strategy calculations and order generation"""

    def __init__(self, grid_size: float, total_investment: float, grid_levels: int = 20):
        self.grid_size = grid_size
        self.total_investment = total_investment
        self.grid_levels = grid_levels  # Total grid levels (half buy, half sell)
        self.buy_levels = grid_levels // 2
        self.sell_levels = grid_levels // 2

    def calculate_grid_orders(self, current_price: float) -> List[Dict]:
        """
        Calculate grid orders around current price

        Args:
            current_price: Current market price

        Returns:
            List of order dictionaries with side, price, quantity
        """
        orders = []
        order_amount = self.total_investment / self.buy_levels

        # Calculate buy orders below current price
        for i in range(1, self.buy_levels + 1):
            buy_price = current_price - (self.grid_size * i)
            quantity = order_amount / buy_price

            orders.append({
                'side': 'BUY',
                'price': buy_price,
                'quantity': quantity,
                'grid_level': -i
            })

        # Calculate sell orders above current price
        for i in range(1, self.sell_levels + 1):
            sell_price = current_price + (self.grid_size * i)
            quantity = order_amount / current_price  # Sell base currency amount

            orders.append({
                'side': 'SELL',
                'price': sell_price,
                'quantity': quantity,
                'grid_level': i
            })

        logger.info(f"Generated {len(orders)} grid orders around price {current_price:.4f}")
        return orders

    def optimize_grid_spacing(self, price_history: List[float]) -> float:
        """
        Dynamically adjust grid spacing based on market volatility

        Args:
            price_history: List of recent prices

        Returns:
            Optimized grid size
        """
        if len(price_history) < 10:
            logger.warning("Insufficient price history for optimization, using default")
            return self.grid_size

        volatility = self._calculate_volatility(price_history)

        # Adjust grid size based on volatility
        if volatility > 0.0002:  # High volatility
            new_grid_size = 0.00015  # Wider spacing
            logger.info(f"High volatility detected ({volatility:.6f}), using wider grid: {new_grid_size:.6f}")
        elif volatility < 0.00005:  # Low volatility
            new_grid_size = 0.00008  # Tighter spacing
            logger.info(f"Low volatility detected ({volatility:.6f}), using tighter grid: {new_grid_size:.6f}")
        else:
            new_grid_size = 0.0001  # Standard spacing
            logger.info(f"Normal volatility ({volatility:.6f}), using standard grid: {new_grid_size:.6f}")

        self.grid_size = new_grid_size
        return new_grid_size

    def _calculate_volatility(self, price_history: List[float]) -> float:
        """Calculate price volatility using standard deviation"""
        if len(price_history) < 2:
            return 0.0

        returns = np.diff(price_history) / price_history[:-1]
        volatility = np.std(returns)
        return volatility

    def get_grid_status(self, current_price: float, open_orders: List[Dict]) -> Dict:
        """
        Get current status of grid

        Args:
            current_price: Current market price
            open_orders: List of open orders from exchange

        Returns:
            Dictionary with grid status information
        """
        if not open_orders:
            return {
                'active_buy_orders': 0,
                'active_sell_orders': 0,
                'grid_coverage': 0.0,
                'status': 'empty'
            }

        active_buy = sum(1 for order in open_orders if order['side'] == 'BUY')
        active_sell = sum(1 for order in open_orders if order['side'] == 'SELL')

        # Calculate how much of the grid is covered
        grid_coverage = (active_buy + active_sell) / self.grid_levels * 100

        status = 'normal'
        if grid_coverage < 50:
            status = 'sparse'
        elif grid_coverage > 90:
            status = 'dense'

        return {
            'active_buy_orders': active_buy,
            'active_sell_orders': active_sell,
            'grid_coverage': grid_coverage,
            'status': status
        }

    def should_place_order(self, current_price: float, order: Dict, existing_orders: List[Dict]) -> bool:
        """
        Check if an order should be placed based on existing orders

        Args:
            current_price: Current market price
            order: Order to check
            existing_orders: List of existing orders

        Returns:
            True if order should be placed, False otherwise
        """
        # Check if there's already an order too close
        for existing in existing_orders:
            existing_price = float(existing['price'])
            if abs(existing_price - order['price']) < (self.grid_size / 2):
                logger.debug(f"Order too close to existing order: {existing_price:.4f}")
                return False

        # Check if order is too far from current price
        price_distance = abs(order['price'] - current_price)
        max_distance = self.grid_size * (self.grid_levels / 2 + 2)

        if price_distance > max_distance:
            logger.debug(f"Order too far from current price: {price_distance:.6f}")
            return False

        return True