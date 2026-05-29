"""
Trade Executor - Executes trades on IQ Option
"""

import logging
from typing import Dict, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class TradeExecutor:
    """Executes trades on IQ Option platform"""

    def __init__(self, api, config):
        """
        Initialize trade executor

        Args:
            api: IQ Option API instance
            config: Configuration object
        """
        self.api = api
        self.config = config
        self.demo_mode = config.iqoption.demo_mode

        self.trades_executed = []

        logger.info(f"Trade Executor initialized (demo_mode={self.demo_mode})")

    def execute_trade(self, asset: str, action: str, amount: float, duration: int) -> Optional[Dict]:
        """
        Execute a trade

        Args:
            asset: Asset name (e.g., "EUR/USD")
            action: Trade action ("CALL" or "PUT")
            amount: Trade amount
            duration: Trade duration in seconds

        Returns:
            Trade information or None
        """
        try:
            if not self.api:
                logger.error("API not connected")
                return None

            # Check if demo mode
            mode = "PRACTICE" if self.demo_mode else "REAL"

            # Convert action to IQ Option format
            direction = "call" if action.upper() == "CALL" else "put"

            logger.info(f"Executing {direction.upper()} on {asset}, Amount: ${amount:.2f}, Duration: {duration}s, Mode: {mode}")

            # Execute trade
            trade_result = self.api.buy(amount, asset, direction, duration)

            if trade_result:
                trade_id = str(uuid.uuid4())
                trade_info = {
                    "id": trade_id,
                    "asset": asset,
                    "action": action,
                    "amount": amount,
                    "duration": duration,
                    "mode": mode,
                    "timestamp": datetime.now().isoformat(),
                    "status": "OPEN",
                    "iq_option_id": trade_result.get('id')
                }

                self.trades_executed.append(trade_info)

                logger.info(f"Trade executed successfully: {trade_id}")
                return trade_info
            else:
                logger.error("Trade execution failed")
                return None

        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return None

    def check_trade_result(self, trade_id: str) -> Optional[Dict]:
        """
        Check the result of a trade

        Args:
            trade_id: Trade ID

        Returns:
            Trade result or None
        """
        try:
            # Find trade in executed trades
            trade = next((t for t in self.trades_executed if t.get('id') == trade_id), None)

            if not trade:
                logger.error(f"Trade {trade_id} not found")
                return None

            if trade['status'] != 'OPEN':
                return trade

            # Check with IQ Option API
            iq_option_id = trade.get('iq_option_id')
            if not iq_option_id:
                logger.error(f"No IQ Option ID for trade {trade_id}")
                return None

            # Get result from API
            positions = self.api.get_positions()

            # Look for our trade
            position = next((p for p in positions if str(p.get('id')) == str(iq_option_id)), None)

            if position:
                # Update trade status
                trade['status'] = position.get('status', 'OPEN')

                if trade['status'] in ['win', 'lose', 'draw']:
                    result_map = {
                        'win': 'WIN',
                        'lose': 'LOSS',
                        'draw': 'TIE'
                    }
                    trade['result'] = result_map.get(trade['status'], 'UNKNOWN')

                    if trade['result'] == 'WIN':
                        trade['pnl'] = trade['amount'] * 0.85  # 85% payout
                    elif trade['result'] == 'LOSS':
                        trade['pnl'] = -trade['amount']
                    else:
                        trade['pnl'] = 0

                    logger.info(f"Trade {trade_id}: {trade['result']}, PnL: ${trade['pnl']:.2f}")

            return trade

        except Exception as e:
            logger.error(f"Error checking trade result: {e}")
            return None

    def get_open_trades(self) -> list:
        """
        Get list of open trades

        Returns:
            List of open trades
        """
        return [t for t in self.trades_executed if t.get('status') == 'OPEN']

    def close_all_trades(self):
        """Close all open trades"""
        open_trades = self.get_open_trades()

        for trade in open_trades:
            logger.info(f"Closing trade {trade.get('id')}")
            # Note: IQ Option binary options cannot be manually closed
            # They will close automatically based on duration
            trade['status'] = 'CLOSING'

    def get_trade_history(self) -> list:
        """
        Get complete trade history

        Returns:
            List of all trades
        """
        return self.trades_executed

    def calculate_pnl(self) -> float:
        """
        Calculate total PnL

        Returns:
            Total profit/loss
        """
        return sum(t.get('pnl', 0) for t in self.trades_executed)

    def get_win_rate(self) -> float:
        """
        Calculate win rate

        Returns:
            Win rate (0-1)
        """
        completed_trades = [t for t in self.trades_executed if t.get('result') in ['WIN', 'LOSS', 'TIE']]

        if not completed_trades:
            return 0.0

        wins = len([t for t in completed_trades if t.get('result') == 'WIN'])
        return wins / len(completed_trades)