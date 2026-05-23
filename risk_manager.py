"""
Risk Manager - Manages trading risk and position sizing
"""

import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RiskManager:
    """Manages trading risk and position sizing"""

    def __init__(self, config):
        """
        Initialize risk manager

        Args:
            config: Configuration object
        """
        self.config = config
        self.risk_config = config.risk_management

        # Track daily performance
        self.daily_trades = []
        self.daily_pnl = 0.0
        self.current_balance = 0.0
        self.start_balance = 0.0

        # Max concurrent trades
        self.current_trades = []

        logger.info("Risk Manager initialized")

    def update_balance(self, balance: float):
        """
        Update current balance

        Args:
            balance: Current balance
        """
        self.current_balance = balance
        if self.start_balance == 0:
            self.start_balance = balance
            logger.info(f"Starting balance: ${balance:.2f}")

    def calculate_position_size(self, signal_strength: float, confidence: float) -> float:
        """
        Calculate position size based on risk parameters

        Args:
            signal_strength: Strength of trading signal (0-1)
            confidence: Confidence level (0-100)

        Returns:
            Position size
        """
        try:
            # Base position size
            base_size = self.config.trading.default_amount

            # Adjust based on signal strength
            size_adjustment = 0.5 + (signal_strength * 0.5)  # 0.5 to 1.0

            # Adjust based on confidence
            confidence_adjustment = confidence / 100.0

            # Calculate adjusted size
            adjusted_size = base_size * size_adjustment * confidence_adjustment

            # Maximum risk per trade
            max_risk = self.current_balance * self.risk_config.max_risk_per_trade

            # Cap position size
            final_size = min(adjusted_size, max_risk)

            logger.debug(f"Position size: ${final_size:.2f} (base: ${base_size:.2f}, signal: {signal_strength:.2f}, confidence: {confidence:.0f})")

            return final_size

        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return self.config.trading.default_amount

    def can_trade(self, signal: Dict) -> tuple[bool, str]:
        """
        Check if we can place a trade based on risk parameters

        Args:
            signal: Trading signal

        Returns:
            Tuple of (can_trade, reason)
        """
        # Check daily trade limit
        if len(self.daily_trades) >= self.risk_config.max_daily_trades:
            return False, f"Daily trade limit reached ({self.risk_config.max_daily_trades})"

        # Check concurrent trades
        if len(self.current_trades) >= self.config.trading.max_concurrent_trades:
            return False, f"Max concurrent trades reached ({self.config.trading.max_concurrent_trades})"

        # Check daily loss limit
        if self.daily_pnl <= -self.risk_config.max_loss_per_day:
            return False, f"Daily loss limit reached (${self.risk_config.max_loss_per_day})"

        # Check max drawdown
        drawdown = (self.start_balance - self.current_balance) / self.start_balance if self.start_balance > 0 else 0
        if drawdown >= self.risk_config.max_drawdown:
            return False, f"Max drawdown reached ({drawdown:.2%})"

        # Check account balance
        if self.current_balance <= 0:
            return False, "Insufficient balance"

        # Check signal strength
        if signal.get('strength', 0) < 0.3:
            return False, "Signal strength too low"

        # Check confidence
        if signal.get('confidence', 0) < 55:
            return False, "Confidence too low"

        # Check minimum win rate (would need historical data)
        # For now, we'll skip this check

        return True, "OK"

    def record_trade(self, trade: Dict):
        """
        Record a trade

        Args:
            trade: Trade information
        """
        trade['timestamp'] = datetime.now().isoformat()
        self.daily_trades.append(trade)
        self.current_trades.append(trade)

        logger.info(f"Recorded trade: {trade.get('action')} on {trade.get('asset')} for ${trade.get('amount', 0):.2f}")

    def update_trade_result(self, trade_id: str, result: str, pnl: float):
        """
        Update trade result

        Args:
            trade_id: Trade ID
            result: Trade result (WIN/LOSS/TIE)
            pnl: Profit/Loss amount
        """
        self.daily_pnl += pnl

        # Update in current trades
        for trade in self.current_trades:
            if trade.get('id') == trade_id:
                trade['result'] = result
                trade['pnl'] = pnl

        # Remove from current trades
        self.current_trades = [t for t in self.current_trades if t.get('id') != trade_id]

        logger.info(f"Trade {trade_id}: {result}, PnL: ${pnl:.2f}, Daily PnL: ${self.daily_pnl:.2f}")

    def get_daily_performance(self) -> Dict:
        """
        Get daily performance summary

        Returns:
            Performance summary
        """
        if not self.daily_trades:
            return {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "ties": 0,
                "win_rate": 0,
                "pnl": 0,
                "start_balance": self.start_balance,
                "current_balance": self.current_balance,
                "drawdown": 0
            }

        wins = len([t for t in self.daily_trades if t.get('result') == 'WIN'])
        losses = len([t for t in self.daily_trades if t.get('result') == 'LOSS'])
        ties = len([t for t in self.daily_trades if t.get('result') == 'TIE'])

        win_rate = wins / len(self.daily_trades) if self.daily_trades else 0

        drawdown = (self.start_balance - self.current_balance) / self.start_balance if self.start_balance > 0 else 0

        return {
            "trades": len(self.daily_trades),
            "wins": wins,
            "losses": losses,
            "ties": ties,
            "win_rate": win_rate,
            "pnl": self.daily_pnl,
            "start_balance": self.start_balance,
            "current_balance": self.current_balance,
            "drawdown": drawdown
        }

    def reset_daily_stats(self):
        """Reset daily statistics (call at start of each trading day)"""
        self.daily_trades = []
        self.daily_pnl = 0.0
        self.start_balance = self.current_balance

        logger.info("Daily statistics reset")

    def should_stop_trading(self) -> tuple[bool, str]:
        """
        Check if we should stop trading for the day

        Returns:
            Tuple of (should_stop, reason)
        """
        performance = self.get_daily_performance()

        # Stop if daily loss limit reached
        if performance['pnl'] <= -self.risk_config.max_loss_per_day:
            return True, f"Daily loss limit reached (${performance['pnl']:.2f})"

        # Stop if max drawdown reached
        if performance['drawdown'] >= self.risk_config.max_drawdown:
            return True, f"Max drawdown reached ({performance['drawdown']:.2%})"

        # Stop if win rate is too low and losses are accumulating
        if performance['trades'] >= 10 and performance['win_rate'] < 0.3:
            return True, f"Win rate too low ({performance['win_rate']:.1%})"

        return False, "OK"

    def get_risk_assessment(self) -> Dict:
        """
        Get current risk assessment

        Returns:
            Risk assessment
        """
        performance = self.get_daily_performance()

        risk_level = "LOW"
        if performance['drawdown'] > 0.05:
            risk_level = "MEDIUM"
        if performance['drawdown'] > 0.08:
            risk_level = "HIGH"

        return {
            "risk_level": risk_level,
            "current_trades": len(self.current_trades),
            "max_concurrent": self.config.trading.max_concurrent_trades,
            "daily_trades": performance['trades'],
            "max_daily": self.risk_config.max_daily_trades,
            "daily_pnl": performance['pnl'],
            "max_loss": self.risk_config.max_loss_per_day,
            "drawdown": performance['drawdown'],
            "max_drawdown": self.risk_config.max_drawdown
        }