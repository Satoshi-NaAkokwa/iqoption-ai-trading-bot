#!/usr/bin/env python3
"""
IQ Option AGGRESSIVE 24/7 Trading Bot v3
- $100 trade amount, 30 trades/hour
- Dynamic loss recovery (Martingale system)
- Session-aware strategies (Asian/London/NY)
- Aggressive account growth targeting
- Multiple specialized strategies
- Real-time win rate tracking and adaptation
"""
import os
import sys
import time
import logging
import signal
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict
import pytz
from collections import deque

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


class TradingSession:
    """Trading session configuration"""
    ASIAN = {
        'name': 'Asian',
        'tz': 'Asia/Tokyo',
        'hours': (0, 8),
        'preferred_assets': ['EURJPY-OTC', 'GBPJPY-OTC', 'USDJPY-OTC'],
        'volatility': 'medium',
        'strategy': 'range_breakout'
    }
    LONDON = {
        'name': 'London',
        'tz': 'Europe/London',
        'hours': (8, 16),
        'preferred_assets': ['EURUSD-OTC', 'GBPUSD-OTC', 'EURGBP-OTC'],
        'volatility': 'high',
        'strategy': 'momentum'
    }
    NEW_YORK = {
        'name': 'New York',
        'tz': 'America/New_York',
        'hours': (13, 21),
        'preferred_assets': ['EURUSD-OTC', 'GBPUSD-OTC', 'USDCHF-OTC'],
        'volatility': 'high',
        'strategy': 'reversal'
    }
    OFF_HOURS = {
        'name': 'Off-Hours',
        'tz': 'UTC',
        'hours': None,
        'preferred_assets': None,  # Use all OTC
        'volatility': 'low',
        'strategy': 'scalping'
    }


class AdvancedTechnicalAnalysis:
    """Advanced technical analysis for aggressive trading"""
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate RSI"""
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
    def calculate_stochastic(prices: List[float], k_period: int = 14, d_period: int = 3) -> Tuple[float, float]:
        """Calculate Stochastic Oscillator"""
        if len(prices) < k_period:
            return 50, 50
        
        high = max(prices[-k_period:])
        low = min(prices[-k_period:])
        close = prices[-1]
        
        if high == low:
            return 50, 50
        
        k = ((close - low) / (high - low)) * 100
        
        # Calculate %D (SMA of %K)
        k_values = []
        for i in range(d_period):
            if len(prices) >= k_period + i:
                h = max(prices[-(k_period + i):-i if i > 0 else None])
                l = min(prices[-(k_period + i):-i if i > 0 else None])
                c = prices[-(i + 1)]
                if h != l:
                    k_values.append(((c - l) / (h - l)) * 100)
        
        d = sum(k_values) / len(k_values) if k_values else 50
        
        return k, d
    
    @staticmethod
    def calculate_macd(prices: List[float]) -> Tuple[float, float, float]:
        """Calculate MACD"""
        if len(prices) < 26:
            return 0, 0, 0
        
        # EMAs
        ema_12 = sum(prices[-12:]) / 12
        ema_26 = sum(prices[-26:]) / 26
        
        macd_line = ema_12 - ema_26
        signal_line = macd_line * 0.9  # Simplified
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20) -> Tuple[float, float, float, float]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return 0, 0, 0, 0.5
        
        sma = sum(prices[-period:]) / period
        variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
        std = variance ** 0.5
        
        upper = sma + (2 * std)
        lower = sma - (2 * std)
        current = prices[-1]
        
        # Position within bands (0-1)
        if upper != lower:
            position = (current - lower) / (upper - lower)
        else:
            position = 0.5
        
        return upper, lower, current, position
    
    @staticmethod
    def detect_candlestick_patterns(candles: List[dict]) -> Dict[str, str]:
        """Detect candlestick patterns"""
        patterns = {}
        
        if len(candles) < 3:
            return patterns
        
        # Last 3 candles
        c1 = candles[-3]
        c2 = candles[-2]
        c3 = candles[-1]
        
        # Doji
        if abs(c3['close'] - c3['open']) < (c3['max'] - c3['min']) * 0.1:
            patterns['doji'] = 'reversal'
        
        # Hammer / Hanging Man
        body = abs(c3['close'] - c3['open'])
        lower_wick = min(c3['open'], c3['close']) - c3['min']
        upper_wick = c3['max'] - max(c3['open'], c3['close'])
        
        if lower_wick > body * 2 and upper_wick < body * 0.5:
            patterns['hammer'] = 'bullish'
        elif upper_wick > body * 2 and lower_wick < body * 0.5:
            patterns['hanging_man'] = 'bearish'
        
        # Engulfing
        if (c2['close'] < c2['open'] and c3['close'] > c3['open'] and
            c3['close'] > c2['open'] and c3['open'] < c2['close']):
            patterns['bullish_engulfing'] = 'bullish'
        elif (c2['close'] > c2['open'] and c3['close'] < c3['open'] and
              c3['open'] > c2['close'] and c3['close'] < c2['open']):
            patterns['bearish_engulfing'] = 'bearish'
        
        return patterns
    
    @staticmethod
    def calculate_support_resistance(prices: List[float], period: int = 20) -> Tuple[float, float]:
        """Calculate support and resistance levels"""
        if len(prices) < period:
            return prices[-1] * 0.99, prices[-1] * 1.01
        
        recent = prices[-period:]
        support = min(recent)
        resistance = max(recent)
        
        return support, resistance
    
    @staticmethod
    def calculate_momentum(prices: List[float], period: int = 10) -> float:
        """Calculate momentum indicator"""
        if len(prices) < period:
            return 0
        
        return (prices[-1] - prices[-period]) / prices[-period] * 100


class AggressiveStrategy:
    """Aggressive multi-strategy system"""
    
    def __init__(self):
        self.last_signal_time = {}
        self.min_signal_interval = 45  # Faster signal generation
        self.ta = AdvancedTechnicalAnalysis()
        
        # Strategy weights (can be adjusted based on performance)
        self.strategy_weights = {
            'rsi_reversal': 1.0,
            'bollinger_breakout': 1.2,
            'stochastic': 0.9,
            'momentum': 1.1,
            'candlestick': 1.3,
            'support_resistance': 1.0,
            'macd_cross': 0.8
        }
    
    def get_signal(self, asset: str, candles: List[dict], session: dict) -> Tuple[Optional[str], float, dict]:
        """
        Generate aggressive trading signal
        Returns: (direction, confidence, analysis_info)
        """
        if not candles or len(candles) < 20:
            return None, 0, {"reason": "insufficient_data"}
        
        # Check cooldown
        now = time.time()
        if asset in self.last_signal_time:
            if now - self.last_signal_time[asset] < self.min_signal_interval:
                return None, 0, {"reason": "cooldown"}
        
        prices = [c['close'] for c in candles]
        signals = []
        
        # 1. RSI Reversal Strategy
        rsi = self.ta.calculate_rsi(prices)
        
        if rsi < 25:  # Extremely oversold
            signals.append(("CALL", 0.70, "rsi_extreme_oversold", self.strategy_weights['rsi_reversal']))
        elif rsi < 30:
            signals.append(("CALL", 0.62, "rsi_oversold", self.strategy_weights['rsi_reversal']))
        elif rsi > 75:  # Extremely overbought
            signals.append(("PUT", 0.70, "rsi_extreme_overbought", self.strategy_weights['rsi_reversal']))
        elif rsi > 70:
            signals.append(("PUT", 0.62, "rsi_overbought", self.strategy_weights['rsi_reversal']))
        
        # 2. Stochastic Strategy
        stoch_k, stoch_d = self.ta.calculate_stochastic(prices)
        
        if stoch_k < 20 and stoch_d < 20:
            signals.append(("CALL", 0.65, "stoch_oversold", self.strategy_weights['stochastic']))
        elif stoch_k > 80 and stoch_d > 80:
            signals.append(("PUT", 0.65, "stoch_overbought", self.strategy_weights['stochastic']))
        elif stoch_k > stoch_d and stoch_k < 30:  # Bullish crossover in oversold
            signals.append(("CALL", 0.60, "stoch_bullish_cross", self.strategy_weights['stochastic']))
        elif stoch_k < stoch_d and stoch_k > 70:  # Bearish crossover in overbought
            signals.append(("PUT", 0.60, "stoch_bearish_cross", self.strategy_weights['stochastic']))
        
        # 3. Bollinger Bands Breakout
        bb_upper, bb_lower, current, bb_position = self.ta.calculate_bollinger_bands(prices)
        
        if bb_position < 0.1:  # Near lower band
            signals.append(("CALL", 0.65, "bb_lower_band", self.strategy_weights['bollinger_breakout']))
        elif bb_position > 0.9:  # Near upper band
            signals.append(("PUT", 0.65, "bb_upper_band", self.strategy_weights['bollinger_breakout']))
        elif bb_position < 0.05:  # Extreme lower
            signals.append(("CALL", 0.72, "bb_extreme_low", self.strategy_weights['bollinger_breakout'] * 1.2))
        elif bb_position > 0.95:  # Extreme upper
            signals.append(("PUT", 0.72, "bb_extreme_high", self.strategy_weights['bollinger_breakout'] * 1.2))
        
        # 4. Momentum Strategy
        momentum = self.ta.calculate_momentum(prices)
        
        if momentum > 0.5:  # Strong up momentum - bet reversal for binary
            signals.append(("PUT", 0.58, "momentum_reversal_up", self.strategy_weights['momentum']))
        elif momentum < -0.5:  # Strong down momentum
            signals.append(("CALL", 0.58, "momentum_reversal_down", self.strategy_weights['momentum']))
        
        # 5. Candlestick Patterns
        patterns = self.ta.detect_candlestick_patterns(candles)
        
        if 'bullish_engulfing' in patterns or 'hammer' in patterns:
            signals.append(("CALL", 0.68, "bullish_pattern", self.strategy_weights['candlestick']))
        elif 'bearish_engulfing' in patterns or 'hanging_man' in patterns:
            signals.append(("PUT", 0.68, "bearish_pattern", self.strategy_weights['candlestick']))
        elif 'doji' in patterns:
            # Doji indicates indecision - use with other signals
            if rsi > 60:
                signals.append(("PUT", 0.55, "doji_reversal", self.strategy_weights['candlestick'] * 0.8))
            elif rsi < 40:
                signals.append(("CALL", 0.55, "doji_reversal", self.strategy_weights['candlestick'] * 0.8))
        
        # 6. Support/Resistance Bounce
        support, resistance = self.ta.calculate_support_resistance(prices)
        
        price_range = resistance - support
        if price_range > 0:
            support_distance = (current - support) / price_range
            resistance_distance = (resistance - current) / price_range
            
            if support_distance < 0.05:  # Near support
                signals.append(("CALL", 0.63, "support_bounce", self.strategy_weights['support_resistance']))
            elif resistance_distance < 0.05:  # Near resistance
                signals.append(("PUT", 0.63, "resistance_bounce", self.strategy_weights['support_resistance']))
        
        # 7. MACD Crossover
        macd, signal_line, histogram = self.ta.calculate_macd(prices)
        
        if histogram > 0 and len(prices) > 2:
            # Check for crossover
            signals.append(("CALL", 0.57, "macd_bullish", self.strategy_weights['macd_cross']))
        elif histogram < 0:
            signals.append(("PUT", 0.57, "macd_bearish", self.strategy_weights['macd_cross']))
        
        # Combine signals with weights
        if not signals:
            return None, 0, {"reason": "no_signals", "rsi": round(rsi, 1)}
        
        call_weight = sum(s[1] * s[3] for s in signals if s[0] == "CALL")
        put_weight = sum(s[1] * s[3] for s in signals if s[0] == "PUT")
        
        call_count = sum(1 for s in signals if s[0] == "CALL")
        put_count = sum(1 for s in signals if s[0] == "PUT")
        
        # Determine direction
        if call_weight > put_weight and call_count >= 2:
            confidence = min(0.80, call_weight / (call_count if call_count > 0 else 1))
            self.last_signal_time[asset] = now
            return "CALL", confidence, {
                "signals": [s[2] for s in signals if s[0] == "CALL"],
                "rsi": round(rsi, 1),
                "stoch": round(stoch_k, 1),
                "bb_pos": round(bb_position, 2)
            }
        elif put_weight > call_weight and put_count >= 2:
            confidence = min(0.80, put_weight / (put_count if put_count > 0 else 1))
            self.last_signal_time[asset] = now
            return "PUT", confidence, {
                "signals": [s[2] for s in signals if s[0] == "PUT"],
                "rsi": round(rsi, 1),
                "stoch": round(stoch_k, 1),
                "bb_pos": round(bb_position, 2)
            }
        
        # Single strong signal
        best_signal = max(signals, key=lambda x: x[1] * x[3])
        if best_signal[1] >= 0.62:
            self.last_signal_time[asset] = now
            return best_signal[0], best_signal[1], {
                "signal": best_signal[2],
                "rsi": round(rsi, 1)
            }
        
        return None, 0, {"reason": "weak_signals", "rsi": round(rsi, 1)}


class DynamicLossRecovery:
    """Martingale-based loss recovery system"""
    
    def __init__(self, base_amount: float = 100.0, max_levels: int = 5, multiplier: float = 2.0):
        self.base_amount = base_amount
        self.max_levels = max_levels
        self.multiplier = multiplier
        self.current_level = 0
        self.consecutive_losses = 0
        self.recovery_history = []
    
    def get_trade_amount(self) -> float:
        """Calculate trade amount based on loss recovery"""
        if self.consecutive_losses == 0:
            return self.base_amount
        
        # Martingale calculation
        amount = self.base_amount
        for i in range(min(self.consecutive_losses, self.max_levels)):
            amount *= self.multiplier
        
        return amount
    
    def record_trade(self, won: bool, profit: float):
        """Record trade result"""
        if won:
            self.consecutive_losses = 0
            self.current_level = 0
        else:
            self.consecutive_losses += 1
            self.current_level = min(self.current_level + 1, self.max_levels)
        
        self.recovery_history.append({
            'time': datetime.now().isoformat(),
            'won': won,
            'profit': profit,
            'level': self.current_level,
            'consecutive_losses': self.consecutive_losses
        })
    
    def get_status(self) -> dict:
        """Get recovery status"""
        return {
            'current_level': self.current_level,
            'consecutive_losses': self.consecutive_losses,
            'next_amount': self.get_trade_amount(),
            'max_level_reached': self.current_level >= self.max_levels
        }
    
    def should_pause(self) -> bool:
        """Check if we should pause due to too many losses"""
        return self.consecutive_losses >= self.max_levels


class AggressiveIQOptionBot:
    """Main aggressive trading bot"""
    
    OTC_ASSETS = ['EURUSD-OTC', 'GBPUSD-OTC', 'EURJPY-OTC', 'EURGBP-OTC', 'GBPJPY-OTC', 'USDCHF-OTC']
    
    def __init__(self):
        self.email = os.environ.get("IQOPTION_EMAIL")
        self.password = os.environ.get("IQOPTION_PASSWORD")
        self.api = None
        self.running = False
        self.balance = 0
        self.start_balance = 0
        
        # Aggressive trading settings
        self.base_trade_amount = 100.0  # $100 per trade
        self.max_trades_per_hour = 30
        self.trades_this_hour = 0
        self.hour_start = datetime.now()
        
        # Loss recovery system
        self.recovery = DynamicLossRecovery(
            base_amount=100.0,
            max_levels=5,
            multiplier=2.0
        )
        
        # Session awareness
        self.current_session = None
        
        # Statistics
        self.total_trades = 0
        self.wins = 0
        self.losses = 0
        self.ties = 0
        self.total_profit = 0
        self.recent_trades = deque(maxlen=50)  # Track last 50 trades
        self.hourly_pnl = deque(maxlen=24)  # Track 24 hours of P&L
        
        # Strategy
        self.strategy = AggressiveStrategy()
        self.available_assets = []
        self.current_asset_index = 0
        self.last_asset_check = None
        self.asset_check_interval = 300
        
        # Risk management
        self.daily_loss_limit = 500.0  # Stop if lost $500 in a day
        self.daily_profit_target = 1000.0  # Target $1000 profit per day
        self.daily_pnl = 0
        self.day_start = datetime.now().date()
        
        logger.info("🔥 AGGRESSIVE IQ Option Bot v3 initialized")
        logger.info(f"💰 Base Trade Amount: ${self.base_trade_amount}")
        logger.info(f"⚡ Max Trades/Hour: {self.max_trades_per_hour}")
        logger.info(f"🎯 Daily Target: ${self.daily_profit_target}")
    
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
    
    def get_current_session(self) -> dict:
        """Determine current trading session"""
        utc_now = datetime.now(pytz.UTC)
        hour = utc_now.hour
        
        if 0 <= hour < 8:
            return TradingSession.ASIAN
        elif 8 <= hour < 16:
            return TradingSession.LONDON
        elif 13 <= hour < 21:
            return TradingSession.NEW_YORK
        else:
            return TradingSession.OFF_HOURS
    
    def get_session_assets(self, session: dict) -> List[str]:
        """Get preferred assets for current session"""
        if session['preferred_assets']:
            # Prioritize session assets but include all OTC
            preferred = [a for a in session['preferred_assets'] if a in self.available_assets]
            other = [a for a in self.available_assets if a not in preferred]
            return preferred + other
        return self.available_assets
    
    def update_available_assets(self):
        """Update list of available assets"""
        now = datetime.now()
        
        if self.last_asset_check and (now - self.last_asset_check).total_seconds() < self.asset_check_interval:
            return
        
        logger.info("🔄 Updating available assets...")
        self.available_assets = []
        
        for asset in self.OTC_ASSETS:
            try:
                result = self.api.buy(1, asset, 'CALL', 1)
                if result and result[0]:
                    self.available_assets.append(asset)
                    logger.info(f"  ✅ {asset} available")
                time.sleep(0.3)
            except Exception as e:
                logger.debug(f"  ❌ {asset}: {e}")
        
        self.last_asset_check = now
        
        if not self.available_assets:
            logger.warning("⚠️ No assets available!")
        else:
            logger.info(f"📊 {len(self.available_assets)} assets available")
    
    def get_candles(self, asset: str, count: int = 60) -> Optional[List[dict]]:
        """Get candle data"""
        try:
            candles = self.api.get_candles(asset, 60, count, time.time())
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
    
    def check_risk_limits(self) -> Tuple[bool, str]:
        """Check if we should stop trading"""
        # Reset daily counters
        today = datetime.now().date()
        if today != self.day_start:
            self.day_start = today
            self.daily_pnl = 0
            logger.info("📅 New day - counters reset")
        
        # Check daily loss limit
        if self.daily_pnl <= -self.daily_loss_limit:
            return False, f"Daily loss limit reached: ${self.daily_pnl:.2f}"
        
        # Check daily profit target
        if self.daily_pnl >= self.daily_profit_target:
            return False, f"Daily profit target reached: ${self.daily_pnl:.2f}"
        
        # Check recovery system
        if self.recovery.should_pause():
            return False, f"Recovery pause: {self.recovery.consecutive_losses} consecutive losses"
        
        return True, "OK"
    
    def run_trading_cycle(self):
        """Run one trading cycle"""
        # Reset hourly counter
        if (datetime.now() - self.hour_start).total_seconds() > 3600:
            self.hourly_pnl.append({
                'hour': self.hour_start.hour,
                'trades': self.trades_this_hour,
                'pnl': self.total_profit
            })
            self.trades_this_hour = 0
            self.hour_start = datetime.now()
            logger.info("⏰ Hourly counter reset")
        
        if self.trades_this_hour >= self.max_trades_per_hour:
            logger.debug(f"Hourly limit reached: {self.trades_this_hour}/{self.max_trades_per_hour}")
            return
        
        # Check risk limits
        can_trade, reason = self.check_risk_limits()
        if not can_trade:
            logger.warning(f"⚠️ {reason}")
            return
        
        # Update assets
        self.update_available_assets()
        
        if not self.available_assets:
            time.sleep(30)
            return
        
        # Get current session and prioritize assets
        self.current_session = self.get_current_session()
        session_assets = self.get_session_assets(self.current_session)
        
        # Select asset
        asset = session_assets[self.current_asset_index % len(session_assets)]
        self.current_asset_index += 1
        
        # Get candles
        candles = self.get_candles(asset)
        
        if candles:
            signal, confidence, info = self.strategy.get_signal(asset, candles, self.current_session)
            
            if signal and confidence >= 0.55:
                # Get dynamic trade amount
                trade_amount = self.recovery.get_trade_amount()
                
                logger.info(f"📈 Signal: {signal} {asset} @ {confidence:.0%} | {info}")
                logger.info(f"💰 Trade Amount: ${trade_amount:.2f} (Level: {self.recovery.current_level})")
                
                # Execute trade
                trade_id = self.execute_trade(asset, signal, trade_amount)
                
                if trade_id:
                    self.total_trades += 1
                    self.trades_this_hour += 1
                    
                    # Wait for result
                    time.sleep(65)
                    
                    result = self.check_trade_result(trade_id)
                    
                    if result:
                        if result > 0:
                            profit = result - trade_amount
                            self.wins += 1
                            self.total_profit += profit
                            self.daily_pnl += profit
                            self.recovery.record_trade(True, profit)
                            self.recent_trades.append({'won': True, 'profit': profit, 'asset': asset})
                            logger.info(f"✅ WIN: +${profit:.2f} (#{self.total_trades})")
                        elif result < 0:
                            loss = trade_amount + result
                            self.losses += 1
                            self.total_profit -= loss
                            self.daily_pnl -= loss
                            self.recovery.record_trade(False, -loss)
                            self.recent_trades.append({'won': False, 'loss': loss, 'asset': asset})
                            logger.info(f"❌ LOSS: -${loss:.2f} (#{self.total_trades})")
                        else:
                            self.ties += 1
                            self.recovery.record_trade(True, 0)
                            logger.info(f"🤝 TIE (#{self.total_trades})")
                        
                        self.balance = self.api.get_balance()
            else:
                logger.debug(f"No signal for {asset}: {info}")
    
    def print_status(self):
        """Print detailed status"""
        win_rate = (self.wins / self.total_trades * 100) if self.total_trades > 0 else 0
        recovery_status = self.recovery.get_status()
        
        logger.info(f"""
╔═══════════════════════════════════════════════════════════════╗
║         🔥 AGGRESSIVE IQ OPTION BOT v3 🔥                     ║
╚═══════════════════════════════════════════════════════════════╝
🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌍 Session: {self.current_session['name'] if self.current_session else 'N/A'}
💰 Balance: ${self.balance:.2f} (Start: ${self.start_balance:.2f})
📊 Trades: {self.total_trades} | W:{self.wins} L:{self.losses} T:{self.ties}
🎯 Win Rate: {win_rate:.1f}%
💵 Total P&L: ${self.total_profit:+.2f}
💵 Daily P&L: ${self.daily_pnl:+.2f}
⚡ Hourly: {self.trades_this_hour}/{self.max_trades_per_hour}
📈 Assets: {len(self.available_assets)} available
🔄 Recovery Level: {recovery_status['current_level']}/{self.recovery.max_levels}
📊 Next Trade: ${recovery_status['next_amount']:.2f}
""")
    
    def run(self):
        """Main loop"""
        logger.info("🚀 Starting AGGRESSIVE 24/7 trading bot v3...")
        logger.info(f"💰 Base Amount: ${self.base_trade_amount}")
        logger.info(f"⚡ Max Trades/Hour: {self.max_trades_per_hour}")
        logger.info(f"🎯 Daily Target: ${self.daily_profit_target}")
        logger.info(f"🛡️ Daily Loss Limit: ${self.daily_loss_limit}")
        
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
                
                time.sleep(25)  # Slightly faster cycles
                
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
    bot = AggressiveIQOptionBot()
    bot.run()
