"""
Main Trading Bot - Orchestrates all components
"""

import logging
import signal
import sys
import time
from typing import Dict, Optional
from datetime import datetime, timedelta

# Import configuration and components
from config import Config
from data_collector import DataCollector
from technical_analyzer import TechnicalAnalyzer
from llm_analyst import LLMAnalyst
from strategy_engine import StrategyEngine
from risk_manager import RiskManager
from trade_executor import TradeExecutor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class TradingBot:
    """Main trading bot class"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize trading bot

        Args:
            config_path: Path to config file (optional)
        """
        self.config = Config()

        if not self.config.validate():
            logger.error("Invalid configuration")
            sys.exit(1)

        # Initialize components
        self.data_collector = DataCollector(
            email=self.config.iqoption.email,
            password=self.config.iqoption.password,
            demo_mode=self.config.iqoption.demo_mode
        )

        self.technical_analyzer = TechnicalAnalyzer(self.config)
        self.llm_analyst = LLMAnalyst(self.config)
        self.strategy_engine = StrategyEngine(self.config)
        self.risk_manager = RiskManager(self.config)

        self.trade_executor = None  # Will be initialized after connection

        self.running = False
        self.last_analysis_time = None

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("Trading Bot initialized")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()

    def connect(self) -> bool:
        """
        Connect to IQ Option API

        Returns:
            True if successful
        """
        logger.info("Connecting to IQ Option...")

        if not self.data_collector.connect():
            logger.error("Failed to connect to IQ Option")
            return False

        # Initialize trade executor
        self.trade_executor = TradeExecutor(self.data_collector.api, self.config)

        # Get initial balance
        balance = self.data_collector.get_account_balance()
        self.risk_manager.update_balance(balance)

        logger.info(f"Connected successfully. Balance: ${balance:.2f}")
        return True

    def analyze_and_trade(self, asset: str, timeframe: str) -> Optional[Dict]:
        """
        Analyze market and potentially execute trade

        Args:
            asset: Asset name
            timeframe: Timeframe (e.g., "1M", "5M", "15M")

        Returns:
            Trade information or None
        """
        try:
            logger.info(f"Analyzing {asset} ({timeframe})...")

            # Get market data
            candles = self.data_collector.get_candles(asset, timeframe, count=100)

            if not candles or len(candles) < 50:
                logger.warning(f"Insufficient candle data for {asset}")
                return None

            # Calculate technical indicators
            indicators = self.technical_analyzer.calculate_all_indicators(candles)

            if not indicators:
                logger.warning(f"Failed to calculate indicators for {asset}")
                return None

            # Get current price data
            price_data = {
                'current_price': indicators.get('current_price', 0),
                'price_change': indicators.get('price_change', 0)
            }

            # LLM analysis (if enabled)
            llm_analysis = None
            if self.llm_analyst.enabled:
                try:
                    llm_analysis = self.llm_analyst.analyze_market(asset, indicators, price_data)
                except Exception as e:
                    logger.error(f"LLM analysis error: {e}")

            # Evaluate strategies
            combined_signal = self.strategy_engine.evaluate_strategies(indicators, llm_analysis)

            # Check if we should trade
            if not self.strategy_engine.should_trade(combined_signal, self.config):
                logger.info(f"No trade signal for {asset} ({timeframe})")
                return None

            # Risk management check
            can_trade, reason = self.risk_manager.can_trade(combined_signal)

            if not can_trade:
                logger.info(f"Cannot trade {asset}: {reason}")
                return None

            # Check if should stop trading for the day
            should_stop, stop_reason = self.risk_manager.should_stop_trading()
            if should_stop:
                logger.warning(f"Stopping trading: {stop_reason}")
                self.stop()
                return None

            # Calculate position size
            signal_strength = combined_signal.get('strength', 0)
            confidence = combined_signal.get('confidence', 0)
            position_size = self.risk_manager.calculate_position_size(signal_strength, confidence)

            # Determine duration based on timeframe
            duration_map = {
                "1M": 60,
                "5M": 300,
                "15M": 900,
                "30M": 1800
            }
            duration = duration_map.get(timeframe, 60)

            # Execute trade
            action = combined_signal.get('action', 'CALL')
            trade_info = self.trade_executor.execute_trade(
                asset=asset,
                action=action,
                amount=position_size,
                duration=duration
            )

            if trade_info:
                # Record trade in risk manager
                self.risk_manager.record_trade(trade_info)

                logger.info(f"Trade executed: {action} on {asset}, Amount: ${position_size:.2f}, Duration: {duration}s")
                return trade_info
            else:
                logger.error("Failed to execute trade")
                return None

        except Exception as e:
            logger.error(f"Error in analyze_and_trade: {e}")
            return None

    def run(self, timeframes: Optional[list] = None):
        """
        Run the trading bot

        Args:
            timeframes: List of timeframes to trade
        """
        if timeframes is None:
            timeframes = self.config.trading.timeframes

        logger.info(f"Starting trading bot with timeframes: {timeframes}")

        self.running = True

        try:
            while self.running:
                # Get active assets
                assets = self.config.active_assets

                # Analyze each asset
                for asset in assets:
                    if not self.running:
                        break

                    for timeframe in timeframes:
                        if not self.running:
                            break

                        try:
                            # Analyze and trade
                            self.analyze_and_trade(asset, timeframe)

                            # Check for completed trades
                            self._check_trade_results()

                        except Exception as e:
                            logger.error(f"Error processing {asset} ({timeframe}): {e}")

                # Update balance
                current_balance = self.data_collector.get_account_balance()
                self.risk_manager.update_balance(current_balance)

                # Log performance
                performance = self.risk_manager.get_daily_performance()
                risk_assessment = self.risk_manager.get_risk_assessment()

                logger.info(f"Performance: {performance['trades']} trades, ${performance['pnl']:+.2f} PnL, {performance['win_rate']:.1%} win rate")
                logger.info(f"Risk Level: {risk_assessment['risk_level']}, Drawdown: {risk_assessment['drawdown']:.2%}")

                # Wait before next iteration
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            self.stop()

    def _check_trade_results(self):
        """Check results of open trades"""
        open_trades = self.trade_executor.get_open_trades()

        for trade in open_trades:
            try:
                trade_result = self.trade_executor.check_trade_result(trade['id'])

                if trade_result and trade_result.get('status') != 'OPEN':
                    # Update risk manager
                    self.risk_manager.update_trade_result(
                        trade_id=trade['id'],
                        result=trade_result.get('result', 'UNKNOWN'),
                        pnl=trade_result.get('pnl', 0)
                    )

                    # Update balance
                    current_balance = self.data_collector.get_account_balance()
                    self.risk_manager.update_balance(current_balance)

            except Exception as e:
                logger.error(f"Error checking trade result: {e}")

    def stop(self):
        """Stop the trading bot"""
        logger.info("Stopping trading bot...")
        self.running = False

        # Disconnect from API
        if self.data_collector:
            self.data_collector.disconnect()

        logger.info("Trading bot stopped")

    def generate_report(self) -> str:
        """
        Generate performance report

        Returns:
            Report text
        """
        performance = self.risk_manager.get_daily_performance()
        trade_history = self.trade_executor.get_trade_history() if self.trade_executor else []

        report = f"""
╔═══════════════════════════════════════════════════════════════╗
║              IQ Option Trading Bot - Performance Report        ║
╚═══════════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

═════════════════════════════════════════════════════════════════
                           PERFORMANCE
═════════════════════════════════════════════════════════════════

Total Trades:        {performance['trades']}
Wins:                {performance['wins']}
Losses:              {performance['losses']}
Ties:                {performance['ties']}
Win Rate:            {performance['win_rate']:.2%}

Total PnL:           ${performance['pnl']:+.2f}
Start Balance:       ${performance['start_balance']:.2f}
Current Balance:     ${performance['current_balance']:.2f}
Drawdown:            {performance['drawdown']:.2%}

═════════════════════════════════════════════════════════════════
                           RECENT TRADES
═════════════════════════════════════════════════════════════════
"""

        for trade in trade_history[-10:]:
            report += f"""
{trade.get('timestamp', 'N/A')} | {trade.get('asset', 'N/A')} | {trade.get('action', 'N/A')} | ${trade.get('amount', 0):.2f} | {trade.get('result', 'OPEN')} | ${trade.get('pnl', 0):+.2f}
"""

        report += """
═════════════════════════════════════════════════════════════════

End of Report
"""

        return report


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='IQ Option AI Trading Bot')
    parser.add_argument('--timeframe', type=str, default='5M', help='Trading timeframe (1M, 5M, 15M)')
    parser.add_argument('--demo', action='store_true', default=True, help='Use demo mode')
    parser.add_argument('--real', action='store_true', help='Use real trading mode')
    parser.add_argument('--report', action='store_true', help='Generate report only')

    args = parser.parse_args()

    # Override demo mode if real mode specified
    if args.real:
        import os
        os.environ['IQOPTION_DEMO_MODE'] = 'false'

    # Create bot instance
    bot = TradingBot()

    # Connect to IQ Option
    if not bot.connect():
        logger.error("Failed to connect to IQ Option")
        sys.exit(1)

    # Generate report and exit if requested
    if args.report:
        report = bot.generate_report()
        print(report)
        sys.exit(0)

    # Run trading bot
    try:
        bot.run(timeframes=[args.timeframe])
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()