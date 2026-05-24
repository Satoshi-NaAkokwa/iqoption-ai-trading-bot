#!/usr/bin/env python3
"""
IQ Option Adaptive 24/7 Trading Bot v2
- Dynamically switches between regular and OTC assets based on market hours
- Improved signal generation with better confidence scoring
- Works with fewer candles when needed
- More aggressive trading with proper risk management
"""
import os
import sys
import time
import logging
import signal
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import pytz
import random

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
    
    MARKETS = {
        'sydney': {'tz': 'Australia/Sydney', 'open': 8, 'close': 17},
        'tokyo': {'tz': 'Asia/Tokyo', 'open': 9, 'close': 18},
        'london': {'tz': 'Europe/London', 'open': 8, 'close': 17},
        'new_york': {'tz': 'America/New_York', 'open': 8, 'close': 17},
    }
    
    OTC_ASSETS = ['EURUSD-OTC', 'GBPUSD-OTC', 'EURJPY-OTC', 'EURGBP-OTC', 'GBPJPY-OTC', 'USDCHF-OTC']
    FOREX_ASSETS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD']
    
    @classmethod
    def get_market_status(cls) -> dict:
        """Get current market open/close status"""
        status = {}
        utc_now = datetime.now(pytz.UTC)
        
        for market, config in cls.MARKETS.items():
            tz = pytz.timezone(config['tz'])
            local_time = utc_now.astimezone(tz)
            local_hour = local_time.hour
            is_weekday = local_time.weekday() < 5
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
        
        # Check OTC assets first (24/7)
        logger.info("🌙 Checking OTC assets (24/7)...")
        for asset in cls.OTC_ASSETS:
            try:
                result = api.buy(1, asset, 'CALL', 1)
                if result and result[0]:
                    available.append(asset)
                    logger.info(f"  ✅ {asset} available")
                time.sleep(0.2)
            except Exception as e:
                logger.debug(f"  ❌ {asset}: {e}")
        
        # Check regular forex if market is open
        if cls.is_forex_market_open():
            logger.info("📈 Checking regular forex assets...")
            for asset in cls.FOREX_ASSETS:
                try:
                    result = api.buy(1, asset, 'CALL', 1)
                    if result and result[0]:
                        available.append(asset)
                        logger.info(f"  ✅ {asset} available")
                    time.sleep(0.2)
                except Exception as e:
                    logger.debug(f"  ❌ {asset}: {e}")
        
        return available


class TechnicalAnalyzer:
    """Simplified but effective technical analysis"""
    
    @staticmethod
    def get_trend(prices: List[float], period: int = 10) -> str:
        """Determine trend direction"""
        if len(prices) < period:
            return "neutral"
        
        recent = prices[-period:]
        if all(recent[i] <= recent[i+1] for i in range(len(recent)-1)):
            return "strong_up"
        elif all(recent[i] >= recent[i+1] for i in range(len(recent)-1)):
            return "strong_down"
        
        # Check general direction
        start = sum(prices[-period:-period//2]) / (period//2)
        end = sum(prices[-period//2:]) / (period//2)
        
        diff = (end - start) / start * 100 if start != 0 else 0
        
        if diff > 0.05:
            return "up"
        elif diff < -0.05:
            return "down"
        return "neutral"
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Simplified RSI"""
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
        
        if not gains or not losses:
            return 50
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def price_action_signal(prices: List[float]) -> Tuple[str, float]:
        """Analyze recent price action for quick signals"""
        if len(prices) < 10:
            return "neutral", 0
        
        # Last 5 candles vs previous 5
        recent = prices[-5:]
        previous = prices[-10:-5]
        
        recent_avg = sum(recent) / len(recent)
        previous_avg = sum(previous) / len(previous)
        
        # Calculate momentum
        change = (recent_avg - previous_avg) / previous_avg * 100 if previous_avg != 0 else 0
        
        # Check for reversal patterns
        last_3_trend = "up" if prices[-1] > prices[-3] else "down"
        last_5_trend = "up" if prices[-1] > prices[-5] else "down"
        
        # Momentum + potential reversal
        if abs(change) > 0.02:  # Significant move
            if change > 0:
                # Uptrend - look for PUT (reversal)
                if last_3_trend == "up" and prices[-1] > prices[-2]:
                    return "PUT", min(0.65, 0.50 + abs(change) * 10)
            else:
                # Downtrend - look for CALL (reversal)
                if last_3_trend == "down" and prices[-1] < prices[-2]:
                    return "CALL", min(0.65, 0.50 + abs(change) * 10)
        
        return "neutral", 0


class AdaptiveStrategy:
    """Improved adaptive trading strategy"""
    
    def __init__(self):
        self.market_detector = MarketDetector()
        self.last_signal_time = {}
        self.min_signal_interval = 60  # seconds between signals on same asset
    
    def get_signal(self, asset: str, candles: List[dict]) -> Tuple[Optional[str], float, dict]:
        """
        Generate trading signal
        Returns: (direction, confidence, analysis_info)
        """
        if not candles or len(candles) < 10:
            return None, 0, {"reason": "insufficient_data"}
        
        # Check signal cooldown
        now = time.time()
        if asset in self.last_signal_time:
            if now - self.last_signal_time[asset] < self.min_signal_interval:
                return None, 0, {"reason": "cooldown"}
        
        prices = [c['close'] for c in candles]
        
        # Gather signals from multiple strategies
        signals = []
        
        # 1. Price Action Strategy
        pa_dir, pa_conf = TechnicalAnalyzer.price_action_signal(prices)
        if pa_conf > 0:
            signals.append((pa_dir, pa_conf, "price_action"))
        
        # 2. Trend + RSI Strategy
        rsi = TechnicalAnalyzer.calculate_rsi(prices)
        trend = TechnicalAnalyzer.get_trend(prices)
        
        if rsi < 35 and trend in ["down", "strong_down"]:
            # Oversold in downtrend - potential bounce
            signals.append(("CALL", 0.55 + (35 - rsi) * 0.01, "rsi_oversold"))
        elif rsi > 65 and trend in ["up", "strong_up"]:
            # Overbought in uptrend - potential drop
            signals.append(("PUT", 0.55 + (rsi - 65) * 0.01, "rsi_overbought"))
        
        # 3. Simple Momentum Strategy
        if len(prices) >= 5:
            momentum = (prices[-1] - prices[-5]) / prices[-5] * 100 if prices[-5] != 0 else 0
            
            if momentum > 0.1:  # Up momentum
                # Bet on reversal for binary options
                signals.append(("PUT", 0.55 + min(momentum * 2, 0.15), "momentum_reversal"))
            elif momentum < -0.1:  # Down momentum
                signals.append(("CALL", 0.55 + min(abs(momentum) * 2, 0.15), "momentum_reversal"))
        
        # 4. Bollinger-like bands
        if len(prices) >= 20:
            sma = sum(prices[-20:]) / 20
            current = prices[-1]
            
            # Calculate simple standard deviation
            variance = sum((p - sma) ** 2 for p in prices[-20:]) / 20
            std = variance ** 0.5
            
            upper = sma + 2 * std
            lower = sma - 2 * std
            
            if current > upper:
                signals.append(("PUT", 0.60, "upper_band"))
            elif current < lower:
                signals.append(("CALL", 0.60, "lower_band"))
        
        # Combine signals
        if not signals:
            return None, 0, {"reason": "no_signals", "rsi": rsi, "trend": trend}
        
        # Weight signals and find best
        call_weight = sum(s[1] for s in signals if s[0] == "CALL")
        put_weight = sum(s[1] for s in signals if s[0] == "PUT")
        
        call_count = sum(1 for s in signals if s[0] == "CALL")
        put_count = sum(1 for s in signals if s[0] == "PUT")
        
        # Need at least 2 signals agreeing
        if call_count >= 2 and call_weight > put_weight:
            confidence = min(0.75, call_weight / call_count)
            self.last_signal_time[asset] = now
            return "CALL", confidence, {"signals": [s[2] for s in signals if s[0] == "CALL"], "rsi": round(rsi, 1)}
        
        elif put_count >= 2 and put_weight > call_weight:
            confidence = min(0.75, put_weight / put_count)
            self.last_signal_time[asset] = now
            return "PUT", confidence, {"signals": [s[2] for s in signals if s[0] == "PUT"], "rsi": round(rsi, 1)}
        
        # Single strong signal is acceptable
        best_signal = max(signals, key=lambda x: x[1])
        if best_signal[1] >= 0.60:
            self.last_signal_time[asset] = now
            return best_signal[0], best_signal[1], {"signal": best_signal[2], "rsi": round(rsi, 1)}
        
        return None, 0, {"reason": "weak_signals", "rsi": round(rsi, 1), "trend": trend}


class AdaptiveIQOptionBot:
    """Main adaptive trading bot"""
    
    def __init__(self):
        self.email = os.environ.get("IQOPTION_EMAIL")
        self.password = os.environ.get("IQOPTION_PASSWORD")
        self.api = None
        self.running = False
        self.balance = 0
        self.start_balance = 0
        
        # Trading settings
        self.trade_amount = 1.0
        self.max_trades_per_hour = 20  # Increased for 24/7 trading
        self.trades_this_hour = 0
        self.hour_start = datetime.now()
        
        # Dynamic strategy settings
        self.session_multipliers = {
            'asian': {'assets': ['EURJPY-OTC', 'GBPJPY-OTC'], 'multiplier': 1.2},
            'london': {'assets': ['EURUSD-OTC', 'GBPUSD-OTC', 'EURGBP-OTC'], 'multiplier': 1.3},
            'new_york': {'assets': ['EURUSD-OTC', 'GBPUSD-OTC', 'USDCHF-OTC'], 'multiplier': 1.1},
            'off_hours': {'assets': None, 'multiplier': 0.9}
        }
        self.recent_trades = []  # Track last 10 trades for adaptive sizing
        
        # Statistics
        self.total_trades = 0
        self.wins = 0
        self.losses = 0
        self.ties = 0
        self.total_profit = 0
        
        # Components
        self.market_detector = MarketDetector()
        self.strategy = AdaptiveStrategy()
        self.available_assets = []
        self.current_asset_index = 0
        self.last_asset_check = None
        self.asset_check_interval = 300
        
        logger.info("🤖 Adaptive IQ Option Bot v2 initialized")
    
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
        """Update list of available assets"""
        now = datetime.now()
        
        if self.last_asset_check and (now - self.last_asset_check).total_seconds() < self.asset_check_interval:
            return
        
        logger.info("🔄 Updating available assets...")
        self.available_assets = self.market_detector.get_available_assets(self.api)
        self.last_asset_check = now
        
        if not self.available_assets:
            logger.warning("⚠️ No assets available!")
        else:
            logger.info(f"📊 {len(self.available_assets)} assets available")
    
    def get_candles(self, asset: str, count: int = 60) -> Optional[List[dict]]:
        """Get candle data"""
        try:
            candles = self.api.get_candles(asset, 60, count, time.time())
            if candles:
                logger.debug(f"📊 Got {len(candles)} candles for {asset}")
            return candles
        except Exception as e:
            logger.error(f"Error getting candles: {e}")
            return None
    
    def execute_trade(self, asset: str, direction: str, amount: float) -> Optional[int]:
        """Execute trade"""
        try:
            check, trade_id = self.api.buy(amount, asset, direction, 1)
            
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
            # Try different check methods
            for method_name in ['check_win_v3', 'check_win_v2', 'check_win']:
                if hasattr(self.api, method_name):
                    try:
                        result = getattr(self.api, method_name)(trade_id)
                        if result is not None:
                            return result
                    except:
                        continue
            return None
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
        
        if self.trades_this_hour >= self.max_trades_per_hour:
            logger.debug(f"Hourly limit reached: {self.trades_this_hour}/{self.max_trades_per_hour}")
            return
        
        # Update assets
        self.update_available_assets()
        
        if not self.available_assets:
            time.sleep(30)
            return
        
        # Cycle through assets
        asset = self.available_assets[self.current_asset_index]
        self.current_asset_index = (self.current_asset_index + 1) % len(self.available_assets)
        
        # Get candles
        candles = self.get_candles(asset)
        
        if candles:
            signal, confidence, info = self.strategy.get_signal(asset, candles)
            
            if signal and confidence >= 0.55:
                logger.info(f"📈 Signal: {signal} {asset} @ {confidence:.0%} | {info}")
                
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
                            logger.info(f"✅ WIN: +${profit:.2f} (#{self.total_trades})")
                        elif result < 0:
                            loss = self.trade_amount + result
                            self.losses += 1
                            self.total_profit -= loss
                            logger.info(f"❌ LOSS: -${loss:.2f} (#{self.total_trades})")
                        else:
                            self.ties += 1
                            logger.info(f"🤝 TIE (#{self.total_trades})")
                        
                        self.balance = self.api.get_balance()
            else:
                logger.debug(f"No signal for {asset}: {info}")
    
    def print_status(self):
        """Print status"""
        win_rate = (self.wins / self.total_trades * 100) if self.total_trades > 0 else 0
        
        market_status = self.market_detector.get_market_status()
        open_markets = [m for m, s in market_status.items() if s['open']]
        market_str = ", ".join(open_markets) if open_markets else "All closed (OTC mode)"
        
        logger.info(f"""
╔═══════════════════════════════════════════════════════════════╗
║              ADAPTIVE IQ OPTION BOT v2                        ║
╚═══════════════════════════════════════════════════════════════╝
🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌍 Markets: {market_str}
💰 Balance: ${self.balance:.2f} (Start: ${self.start_balance:.2f})
📊 Trades: {self.total_trades} | W:{self.wins} L:{self.losses} T:{self.ties}
🎯 Win Rate: {win_rate:.1f}%
💵 P&L: ${self.total_profit:+.2f}
⚡ Hourly: {self.trades_this_hour}/{self.max_trades_per_hour}
📈 Assets: {len(self.available_assets)} available
""")
    
    def run(self):
        """Main loop"""
        logger.info("🚀 Starting Adaptive 24/7 trading bot v2...")
        
        if not self.connect():
            logger.error("Failed to connect")
            return
        
        self.running = True
        
        def signal_handler(sig, frame):
            logger.info("Shutdown signal received")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        cycle = 0
        
        while self.running:
            try:
                cycle += 1
                
                self.run_trading_cycle()
                
                if cycle % 10 == 0:
                    self.print_status()
                
                time.sleep(30)
                
                # Reconnect if needed
                if not self.api or not self.api.check_connect():
                    logger.info("🔄 Reconnecting...")
                    self.connect()
            
            except Exception as e:
                logger.error(f"Error: {e}")
                time.sleep(60)
                
                if not self.api or not self.api.check_connect():
                    self.connect()
        
        logger.info("Bot stopped")


if __name__ == "__main__":
    bot = AdaptiveIQOptionBot()
    bot.run()
