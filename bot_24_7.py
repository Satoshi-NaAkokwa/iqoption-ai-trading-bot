#!/usr/bin/env python3
"""
IQ Option 24/7 Trading Bot
Runs continuously with intelligent trading strategies
"""
import os
import sys
import time
import logging
import signal
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

from iqoptionapi.stable_api import IQ_Option

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class IQOptionBot:
    def __init__(self):
        self.email = os.getenv("IQOPTION_EMAIL")
        self.password = os.getenv("IQOPTION_PASSWORD")
        self.api = None
        self.running = False
        self.balance = 0
        self.start_balance = 0
        
        # Trading settings
        self.trade_amount = 1.0  # $1 per trade
        self.min_confidence = 0.55  # 55% confidence threshold
        self.max_trades_per_hour = 10
        self.trades_this_hour = 0
        self.hour_start = datetime.now()
        
        # Statistics
        self.total_trades = 0
        self.wins = 0
        self.losses = 0
        self.ties = 0
        self.total_profit = 0
        
        # Assets to trade
        self.assets = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]
        self.current_asset_index = 0
        
        logger.info("🤖 IQ Option Bot initialized")
    
    def connect(self):
        """Connect to IQ Option"""
        try:
            self.api = IQ_Option(self.email, self.password)
            check, reason = self.api.connect()
            
            if check:
                self.api.change_balance("PRACTICE")
                self.balance = self.api.get_balance()
                self.start_balance = self.balance
                logger.info(f"✅ Connected! Balance: ${self.balance:.2f}")
                return True
            else:
                logger.error(f"❌ Connection failed: {reason}")
                return False
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return False
    
    def get_technical_signal(self, asset):
        """Generate trading signal based on technical analysis"""
        try:
            # Get candles
            candles = self.api.get_candles(asset, 60, 100, time.time())
            
            if not candles or len(candles) < 50:
                return None, 0
            
            # Extract close prices
            closes = [c['close'] for c in candles]
            
            # Simple moving averages
            sma_5 = sum(closes[-5:]) / 5
            sma_20 = sum(closes[-20:]) / 20
            sma_50 = sum(closes[-50:]) / 50
            
            current_price = closes[-1]
            
            # RSI calculation
            gains = []
            losses = []
            for i in range(1, 15):
                change = closes[-i] - closes[-i-1]
                if change > 0:
                    gains.append(change)
                else:
                    losses.append(abs(change))
            
            avg_gain = sum(gains) / 14 if gains else 0
            avg_loss = sum(losses) / 14 if losses else 0
            
            rs = avg_gain / avg_loss if avg_loss > 0 else 100
            rsi = 100 - (100 / (1 + rs))
            
            # MACD-style signal
            ema_12 = sum(closes[-12:]) / 12
            ema_26 = sum(closes[-26:]) / 26
            macd = ema_12 - ema_26
            
            # Determine signal
            signal = None
            confidence = 0
            
            # Trend analysis
            trend_up = sma_5 > sma_20 > sma_50
            trend_down = sma_5 < sma_20 < sma_50
            
            # RSI conditions
            rsi_oversold = rsi < 30
            rsi_overbought = rsi > 70
            
            # Generate signal
            if trend_up and rsi_oversold:
                signal = "CALL"
                confidence = 0.70
            elif trend_down and rsi_overbought:
                signal = "PUT"
                confidence = 0.70
            elif sma_5 > sma_20 and macd > 0:
                signal = "CALL"
                confidence = 0.60
            elif sma_5 < sma_20 and macd < 0:
                signal = "PUT"
                confidence = 0.60
            elif rsi_oversold:
                signal = "CALL"
                confidence = 0.55
            elif rsi_overbought:
                signal = "PUT"
                confidence = 0.55
            
            return signal, confidence
            
        except Exception as e:
            logger.error(f"Error getting signal for {asset}: {e}")
            return None, 0
    
    def execute_trade(self, asset, direction, amount):
        """Execute a trade"""
        try:
            # 1 minute expiry
            expiry = 1
            
            check, trade_id = self.api.buy(amount, asset, direction, expiry)
            
            if check:
                logger.info(f"📊 Trade placed: {direction} {asset} ${amount:.2f} (ID: {trade_id})")
                return trade_id
            else:
                logger.warning(f"⚠️ Trade failed: {trade_id}")
                return None
        except Exception as e:
            logger.error(f"❌ Trade error: {e}")
            return None
    
    def check_trade_result(self, trade_id):
        """Check trade result"""
        try:
            result = self.api.check_win_v4(trade_id)
            return result
        except Exception as e:
            logger.error(f"Error checking trade: {e}")
            return None
    
    def run_trading_cycle(self):
        """Run one trading cycle"""
        # Reset hourly counter
        if (datetime.now() - self.hour_start).total_seconds() > 3600:
            self.trades_this_hour = 0
            self.hour_start = datetime.now()
        
        # Check trade limit
        if self.trades_this_hour >= self.max_trades_per_hour:
            logger.info("⏳ Hourly trade limit reached, waiting...")
            return
        
        # Select asset (rotate through list)
        asset = self.assets[self.current_asset_index]
        self.current_asset_index = (self.current_asset_index + 1) % len(self.assets)
        
        # Get signal
        signal, confidence = self.get_technical_signal(asset)
        
        if signal and confidence >= self.min_confidence:
            logger.info(f"📈 Signal: {signal} {asset} @ {confidence:.0%} confidence")
            
            # Execute trade
            trade_id = self.execute_trade(asset, signal, self.trade_amount)
            
            if trade_id:
                self.total_trades += 1
                self.trades_this_hour += 1
                
                # Wait for result
                time.sleep(65)
                
                result = self.check_trade_result(trade_id)
                
                if result:
                    if result > 0:
                        profit = result - self.trade_amount
                        self.wins += 1
                        self.total_profit += profit
                        logger.info(f"✅ WIN: +${profit:.2f} (Trade #{self.total_trades})")
                    elif result < 0:
                        loss = self.trade_amount + result
                        self.losses += 1
                        self.total_profit -= loss
                        logger.info(f"❌ LOSS: -${loss:.2f} (Trade #{self.total_trades})")
                    else:
                        self.ties += 1
                        logger.info(f"🤝 TIE (Trade #{self.total_trades})")
                
                # Update balance
                self.balance = self.api.get_balance()
        else:
            logger.info(f"⏭️ No signal for {asset} (confidence: {confidence:.0%})")
    
    def print_status(self):
        """Print current status"""
        win_rate = (self.wins / self.total_trades * 100) if self.total_trades > 0 else 0
        
        status = f"""
╔═══════════════════════════════════════════════════════════════╗
║                  IQ OPTION BOT STATUS                          ║
╚═══════════════════════════════════════════════════════════════╝
🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
💰 Balance: ${self.balance:.2f} (Started: ${self.start_balance:.2f})
📊 Total Trades: {self.total_trades} | Wins: {self.wins} | Losses: {self.losses} | Ties: {self.ties}
🎯 Win Rate: {win_rate:.1f}%
💵 Total P&L: ${self.total_profit:+.2f}
⚡ Trades this hour: {self.trades_this_hour}/{self.max_trades_per_hour}
"""
        logger.info(status)
    
    def run(self):
        """Main run loop"""
        logger.info("🚀 Starting 24/7 trading bot...")
        
        if not self.connect():
            logger.error("Failed to connect, exiting")
            return
        
        self.running = True
        
        # Signal handlers
        def signal_handler(sig, frame):
            logger.info("Shutdown signal received")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        cycle_count = 0
        
        while self.running:
            try:
                cycle_count += 1
                
                # Run trading cycle
                self.run_trading_cycle()
                
                # Print status every 10 cycles
                if cycle_count % 10 == 0:
                    self.print_status()
                
                # Small delay between cycles
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in trading cycle: {e}")
                time.sleep(60)
                
                # Try to reconnect
                if not self.api or not self.api.check_connect():
                    logger.info("Reconnecting...")
                    self.connect()
        
        logger.info("Bot stopped")

if __name__ == "__main__":
    bot = IQOptionBot()
    bot.run()
