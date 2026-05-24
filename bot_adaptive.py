#!/usr/bin/env python3
"""
IQ Option Adaptive 24/7 Trading Bot
- Dynamically switches between regular and OTC assets based on market hours
- Adapts trading strategies based on market conditions
- Truly operates 24/7 across all timezones
"""
import os
import sys
import time
import logging
import signal
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import pytz

# Load environment variables
with open('.env') as f:
    for line in f:
        if '=' in line:
            key, val = line.strip().split('=', 1)
            os.environ[key] = val

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


class MarketDetector:
    """Detects market hours and availability"""
    
    # Market timezone definitions
    MARKETS = {
        'sydney': {'tz': 'Australia/Sydney', 'open': 8, 'close': 17},
        'tokyo': {'tz': 'Asia/Tokyo', 'open': 9, 'close': 18},
        'london': {'tz': 'Europe/London', 'open': 8, 'close': 17},
        'new_york': {'tz': 'America/New_York', 'open': 8, 'close': 17},
    }
    
    # Asset availability by market
    FOREX_ASSETS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'EURJPY', 'GBPJPY', 'USDCHF']
    OTC_ASSETS = ['EURUSD-OTC', 'GBPUSD-OTC', 'EURJPY-OTC', 'EURGBP-OTC', 'GBPJPY-OTC', 'USDCHF-OTC']
    
    @classmethod
    def get_market_status(cls) -> dict:
        """Get current market open/close status"""
        status = {}
        utc_now = datetime.now(pytz.UTC)
        
        for market, config in cls.MARKETS.items():
            tz = pytz.timezone(config['tz'])
            local_time = utc_now.astimezone(tz)
            local_hour = local_time.hour
            
            # Check if it's a weekday and within trading hours
            is_weekday = local_time.weekday() < 5  # Mon-Fri
            is_open = config['open'] <= local_hour < config['close']
            
            status[market] = {
                'open': is_weekday and is_open,
                'local_time': local_time.strftime('%H:%M'),
                'timezone': config['tz']
            }
        
        return status
    
    @classmethod
    def is_forex_market_open(cls) -> bool:
        """Check if any forex market is open"""
        status = cls.get_market_status()
        return any(s['open'] for s in status.values())
    
    @classmethod
    def get_available_assets(cls, api: IQ_Option) -> List[str]:
        """Dynamically determine which assets are available"""
        available = []
        
        # Check if forex market is open
        if cls.is_forex_market_open():
            logger.info("📈 Forex market is OPEN - checking regular assets...")
            for asset in cls.FOREX_ASSETS:
                try:
                    result = api.buy(1, asset, 'CALL', 1)
                    if result[0]:
                        available.append(asset)
                        logger.info(f"  ✅ {asset} available")
                    time.sleep(0.3)
                except:
                    pass
        
        # Always check OTC assets (24/7)
        logger.info("🌙 Checking OTC assets (24/7)...")
        for asset in cls.OTC_ASSETS:
            try:
                result = api.buy(1, asset, 'CALL', 1)
                if result[0]:
                    available.append(asset)
                    logger.info(f"  ✅ {asset} available")
                time.sleep(0.3)
            except:
                pass
        
        return available


class TechnicalAnalyzer:
    """Advanced technical analysis for trading signals"""
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> float:
        """Simple Moving Average"""
        if len(prices) < period:
            return 0
        return sum(prices[-period:]) / period
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> float:
        """Exponential Moving Average"""
        if len(prices) < period:
            return 0
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Relative Strength Index"""
        if len(prices) < period + 1:
            return 50
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def calculate_macd(prices: List[float]) -> Tuple[float, float, float]:
        """MACD indicator"""
        if len(prices) < 26:
            return 0, 0, 0
        
        ema_12 = TechnicalAnalyzer.calculate_ema(prices, 12)
        ema_26 = TechnicalAnalyzer.calculate_ema(prices, 26)
        macd = ema_12 - ema_26
        
        # Signal line (9-period EMA of MACD)
        signal = 0  # Simplified
        
        return macd, signal, macd - signal
    
    @staticmethod
    def calculate_bollinger(prices: List[float], period: int = 20) -> Tuple[float, float, float]:
        """Bollinger Bands"""
        if len(prices) < period:
            return 0, 0, 0
        
        sma = sum(prices[-period:]) / period
        variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
        std = variance ** 0.5
        
        return sma - 2*std, sma, sma + 2*std


class TradingStrategy:
    """Adaptive trading strategy based on market conditions"""
    
    def __init__(self):
        self.market_detector = MarketDetector()
    
    def get_signal(self, api: IQ_Option, asset: str, candles: List[dict]) -> Tuple[Optional[str], float]:
        """
        Generate trading signal with confidence level
        Returns: (direction, confidence) or (None, 0)
        """
        if not candles or len(candles) < 50:
            return None, 0
        
        prices = [c['close'] for c in candles]
        
        # Technical indicators
        sma_5 = TechnicalAnalyzer.calculate_sma(prices, 5)
        sma_20 = TechnicalAnalyzer.calculate_sma(prices, 20)
        sma_50 = TechnicalAnalyzer.calculate_sma(prices, 50)
        
        rsi = TechnicalAnalyzer.calculate_rsi(prices, 14)
        macd, signal, hist = TechnicalAnalyzer.calculate_macd(prices)
        
        bb_lower, bb_mid, bb_upper = TechnicalAnalyzer.calculate_bollinger(prices, 20)
        
        current_price = prices[-1]
        
        # Market volatility estimation
        recent_range = max(prices[-20:]) - min(prices[-20:])
        avg_range = (max(prices) - min(prices)) / (len(prices) / 20)
        volatility = recent_range / avg_range if avg_range > 0 else 1
        
        # Signal scoring
        call_score = 0
        put_score = 0
        
        # Trend analysis
        if sma_5 > sma_20 > sma_50:
            call_score += 3
        elif sma_5 < sma_20 < sma_50:
            put_score += 3
        
        # RSI conditions
        if rsi < 30:
            call_score += 2  # Oversold - buy
        elif rsi > 70:
            put_score += 2  # Overbought - sell
        elif rsi < 40:
            call_score += 1
        elif rsi > 60:
            put_score += 1
        
        # MACD
        if macd > 0 and hist > 0:
            call_score += 2
        elif macd < 0 and hist < 0:
            put_score += 2
        
        # Bollinger Bands
        if current_price < bb_lower:
            call_score += 2  # Below lower band - buy
        elif current_price > bb_upper:
            put_score += 2  # Above upper band - sell
        
        # Price action
        price_change = (prices[-1] - prices[-5]) / prices[-5] * 100 if prices[-5] != 0 else 0
        if price_change > 0.1:
            put_score += 1  # Recent uptick - potential reversal
        elif price_change < -0.1:
            call_score += 1  # Recent drop - potential bounce
        
        # Determine signal
        total_score = call_score + put_score
        if total_score == 0:
            return None, 0
        
        confidence = max(call_score, put_score) / 10.0  # Normalize to 0-1
        
        # Minimum confidence threshold
        if confidence < 0.55:
            return None, 0
        
        if call_score > put_score:
            return "CALL", confidence
        elif put_score > call_score:
            return "PUT", confidence
        
        return None, 0


class AdaptiveIQOptionBot:
    """Main trading bot with adaptive strategies"""
    
    def __init__(self):
        self.email = os.environ.get("IQOPTION_EMAIL")
        self.password = os.environ.get("IQOPTION_PASSWORD")
        self.api = None
        self.running = False
        self.balance = 0
        self.start_balance = 0
        
        # Trading settings
        self.trade_amount = 1.0
        self.min_confidence = 0.55
        self.max_trades_per_hour = 10
        self.trades_this_hour = 0
        self.hour_start = datetime.now()
        
        # Statistics
        self.total_trades = 0
        self.wins = 0
        self.losses = 0
        self.ties = 0
        self.total_profit = 0
        
        # Adaptive components
        self.market_detector = MarketDetector()
        self.strategy = TradingStrategy()
        self.available_assets = []
        self.current_asset_index = 0
        
        # Market session tracking
        self.last_asset_check = None
        self.asset_check_interval = 300  # 5 minutes
        
        logger.info("🤖 Adaptive IQ Option Bot initialized")
    
    def connect(self) -> bool:
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
    
    def update_available_assets(self):
        """Update list of available assets based on market conditions"""
        now = datetime.now()
        
        # Check if we need to update
        if self.last_asset_check and (now - self.last_asset_check).total_seconds() < self.asset_check_interval:
            return
        
        logger.info("🔄 Updating available assets...")
        self.available_assets = self.market_detector.get_available_assets(self.api)
        self.last_asset_check = now
        
        if not self.available_assets:
            logger.warning("⚠️ No assets available! Waiting...")
        else:
            logger.info(f"📊 {len(self.available_assets)} assets available: {self.available_assets}")
    
    def get_candles(self, asset: str, count: int = 100) -> Optional[List[dict]]:
        """Get candle data for asset"""
        try:
            candles = self.api.get_candles(asset, 60, count, time.time())
            return candles
        except Exception as e:
            logger.error(f"Error getting candles for {asset}: {e}")
            return None
    
    def execute_trade(self, asset: str, direction: str, amount: float) -> Optional[int]:
        """Execute a trade"""
        try:
            check, trade_id = self.api.buy(amount, asset, direction, 1)  # 1 minute expiry
            
            if check:
                logger.info(f"📊 Trade placed: {direction} {asset} ${amount:.2f}")
                return trade_id
            else:
                logger.warning(f"⚠️ Trade failed: {trade_id}")
                return None
        except Exception as e:
            logger.error(f"❌ Trade error: {e}")
            return None
    
    def check_trade_result(self, trade_id: int) -> Optional[float]:
        """Check trade result"""
        try:
            # Use check_win_v3 (correct method for this API version)
            result = self.api.check_win_v3(trade_id)
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
            logger.info("⏰ Hourly counter reset")
        
        # Check trade limit
        if self.trades_this_hour >= self.max_trades_per_hour:
            return
        
        # Update available assets
        self.update_available_assets()
        
        if not self.available_assets:
            logger.info("⏳ No assets available, waiting...")
            time.sleep(60)
            return
        
        # Select asset (rotate through available)
        asset = self.available_assets[self.current_asset_index]
        self.current_asset_index = (self.current_asset_index + 1) % len(self.available_assets)
        
        # Get candles and signal
        candles = self.get_candles(asset)
        
        if candles:
            signal, confidence = self.strategy.get_signal(self.api, asset, candles)
            
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
        
        # Get market status
        market_status = self.market_detector.get_market_status()
        open_markets = [m for m, s in market_status.items() if s['open']]
        market_str = ", ".join(open_markets) if open_markets else "All closed (OTC mode)"
        
        status = f"""
╔═══════════════════════════════════════════════════════════════╗
║              ADAPTIVE IQ OPTION BOT STATUS                     ║
╚═══════════════════════════════════════════════════════════════╝
🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌍 Markets: {market_str}
💰 Balance: ${self.balance:.2f} (Started: ${self.start_balance:.2f})
📊 Trades: {self.total_trades} | Wins: {self.wins} | Losses: {self.losses} | Ties: {self.ties}
🎯 Win Rate: {win_rate:.1f}%
💵 P&L: ${self.total_profit:+.2f}
⚡ Hourly: {self.trades_this_hour}/{self.max_trades_per_hour}
📈 Assets: {len(self.available_assets)} available
"""
        logger.info(status)
    
    def run(self):
        """Main run loop"""
        logger.info("🚀 Starting Adaptive 24/7 trading bot...")
        
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
                
                # Print status every 5 cycles
                if cycle_count % 5 == 0:
                    self.print_status()
                
                # Small delay between cycles
                time.sleep(30)
                
                # Reconnect if needed
                if not self.api or not self.api.check_connect():
                    logger.info("🔄 Reconnecting...")
                    self.connect()
                
            except Exception as e:
                logger.error(f"Error in trading cycle: {e}")
                time.sleep(60)
                
                if not self.api or not self.api.check_connect():
                    logger.info("🔄 Reconnecting after error...")
                    self.connect()
        
        logger.info("Bot stopped")


if __name__ == "__main__":
    bot = AdaptiveIQOptionBot()
    bot.run()
