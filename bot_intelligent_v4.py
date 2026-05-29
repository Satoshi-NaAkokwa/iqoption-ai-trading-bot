#!/usr/bin/env python3
"""
IQ Option INTELLIGENT Recovery Bot v4
- Learns from past trading patterns
- Adaptive strategy weights based on performance
- Smart Martingale with reduced risk
- Asset-specific win rate tracking
- Session-aware with best-performing assets
- Memory persistence for continuous learning
"""
import os
import sys
import time
import logging
import signal
import json
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


class TradingMemory:
    """Persistent memory for learning from trades"""
    
    def __init__(self, memory_file: str = 'trading_memory.json'):
        self.memory_file = memory_file
        self.asset_stats = {}  # {asset: {direction: {wins, losses}}}
        self.strategy_stats = {}  # {strategy: {wins, losses}}
        self.session_stats = {}  # {session: {wins, losses}}
        self.hourly_stats = {}  # {hour: {wins, losses}}
        self.recent_trades = deque(maxlen=50)
        self.load()
    
    def load(self):
        """Load memory from file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.asset_stats = data.get('asset_stats', {})
                    self.strategy_stats = data.get('strategy_stats', {})
                    self.session_stats = data.get('session_stats', {})
                    self.hourly_stats = data.get('hourly_stats', {})
                    logger.info(f"📊 Loaded trading memory from {self.memory_file}")
        except Exception as e:
            logger.warning(f"Could not load memory: {e}")
    
    def save(self):
        """Save memory to file"""
        try:
            data = {
                'asset_stats': self.asset_stats,
                'strategy_stats': self.strategy_stats,
                'session_stats': self.session_stats,
                'hourly_stats': self.hourly_stats,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.memory_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save memory: {e}")
    
    def record_trade(self, asset: str, direction: str, strategy: str, 
                     session: str, won: bool, pnl: float):
        """Record a trade for learning"""
        # Asset stats
        if asset not in self.asset_stats:
            self.asset_stats[asset] = {'CALL': {'wins': 0, 'losses': 0}, 
                                        'PUT': {'wins': 0, 'losses': 0}}
        if won:
            self.asset_stats[asset][direction]['wins'] += 1
        else:
            self.asset_stats[asset][direction]['losses'] += 1
        
        # Strategy stats
        if strategy not in self.strategy_stats:
            self.strategy_stats[strategy] = {'wins': 0, 'losses': 0}
        if won:
            self.strategy_stats[strategy]['wins'] += 1
        else:
            self.strategy_stats[strategy]['losses'] += 1
        
        # Session stats
        if session not in self.session_stats:
            self.session_stats[session] = {'wins': 0, 'losses': 0}
        if won:
            self.session_stats[session]['wins'] += 1
        else:
            self.session_stats[session]['losses'] += 1
        
        # Hourly stats
        hour = datetime.now().hour
        if hour not in self.hourly_stats:
            self.hourly_stats[hour] = {'wins': 0, 'losses': 0}
        if won:
            self.hourly_stats[hour]['wins'] += 1
        else:
            self.hourly_stats[hour]['losses'] += 1
        
        # Recent trades
        self.recent_trades.append({
            'asset': asset,
            'direction': direction,
            'strategy': strategy,
            'won': won,
            'pnl': pnl,
            'time': datetime.now().isoformat()
        })
        
        # Save periodically
        if len(self.recent_trades) % 5 == 0:
            self.save()
    
    def get_asset_win_rate(self, asset: str, direction: str) -> float:
        """Get win rate for asset+direction"""
        if asset not in self.asset_stats:
            return 0.5  # No data, neutral
        stats = self.asset_stats[asset].get(direction, {'wins': 0, 'losses': 0})
        total = stats['wins'] + stats['losses']
        if total == 0:
            return 0.5
        return stats['wins'] / total
    
    def get_strategy_weight(self, strategy: str) -> float:
        """Get weight multiplier for strategy based on performance"""
        if strategy not in self.strategy_stats:
            return 1.0
        stats = self.strategy_stats[strategy]
        total = stats['wins'] + stats['losses']
        if total < 3:
            return 1.0  # Not enough data
        win_rate = stats['wins'] / total
        # Boost winning strategies, penalize losing ones
        if win_rate > 0.6:
            return 1.5  # Boost good strategies
        elif win_rate < 0.4:
            return 0.5  # Penalize poor strategies
        return 1.0
    
    def get_best_assets(self, session: str = None, limit: int = 3) -> List[str]:
        """Get best performing assets"""
        scores = []
        for asset, directions in self.asset_stats.items():
            total_wins = sum(d['wins'] for d in directions.values())
            total_losses = sum(d['losses'] for d in directions.values())
            total = total_wins + total_losses
            if total >= 3:  # Minimum trades
                win_rate = total_wins / total
                scores.append((asset, win_rate, total))
        
        # Sort by win rate, then by number of trades
        scores.sort(key=lambda x: (x[1], x[2]), reverse=True)
        return [s[0] for s in scores[:limit]]
    
    def get_best_direction(self, asset: str) -> str:
        """Get best performing direction for asset"""
        call_rate = self.get_asset_win_rate(asset, 'CALL')
        put_rate = self.get_asset_win_rate(asset, 'PUT')
        if call_rate > put_rate + 0.1:
            return 'CALL'
        elif put_rate > call_rate + 0.1:
            return 'PUT'
        return None  # No preference
    
    def get_recent_streak(self) -> Tuple[int, str]:
        """Get current win/loss streak"""
        if not self.recent_trades:
            return 0, 'none'
        
        streak = 0
        last_result = None
        for trade in reversed(list(self.recent_trades)):
            if last_result is None:
                last_result = 'win' if trade['won'] else 'loss'
                streak = 1
            elif (trade['won'] and last_result == 'win') or (not trade['won'] and last_result == 'loss'):
                streak += 1
            else:
                break
        
        return streak, last_result


class SmartRecovery:
    """Intelligent Martingale with risk management"""
    
    def __init__(self, base_amount: float = 10.0, max_levels: int = 5):
        self.base_amount = base_amount
        self.max_levels = max_levels
        self.current_level = 0
        self.multiplier = 1.6  # Reduced from 2.0 for safer recovery
        self.consecutive_losses = 0
        self.total_recovered = 0.0
        self.recovery_active = False
        self.pause_start_time = None
        self.pause_duration_minutes = 5  # Reset after 5 minutes
    
    def get_trade_amount(self) -> float:
        """Calculate trade amount based on recovery level"""
        amount = self.base_amount * (self.multiplier ** self.current_level)
        return round(amount, 2)
    
    def record_trade(self, won: bool, pnl: float = 0):
        """Record trade result and adjust recovery"""
        if won:
            if self.recovery_active:
                self.total_recovered += pnl
                logger.info(f"💰 Recovery progress: +${pnl:.2f} (total recovered: ${self.total_recovered:.2f})")
            
            # Reset on win
            self.current_level = 0
            self.consecutive_losses = 0
            self.recovery_active = False
        else:
            self.consecutive_losses += 1
            
            # Only start recovery after 2 losses
            if self.consecutive_losses >= 2:
                self.current_level = min(self.current_level + 1, self.max_levels - 1)
                self.recovery_active = True
                logger.warning(f"⚠️ Recovery level {self.current_level}: next trade ${self.get_trade_amount():.2f}")
    
    def should_pause(self) -> bool:
        """Check if we should pause (max losses reached)"""
        if self.consecutive_losses >= self.max_levels:
            # Start tracking pause time
            if self.pause_start_time is None:
                self.pause_start_time = time.time()
                logger.warning(f"⏸️ Recovery pause started - will reset in {self.pause_duration_minutes} minutes")
            
            # Check if pause duration exceeded
            elapsed = time.time() - self.pause_start_time
            if elapsed >= self.pause_duration_minutes * 60:
                logger.info(f"🔄 Recovery pause timeout - resetting to base trade")
                self.reset()
                return False
            
            return True
        return False
    
    def reset(self):
        """Reset recovery state"""
        self.current_level = 0
        self.consecutive_losses = 0
        self.recovery_active = False
        self.pause_start_time = None
        logger.info("✅ Recovery state reset - starting fresh")
    
    def get_status(self) -> dict:
        return {
            'current_level': self.current_level,
            'max_levels': self.max_levels,
            'next_amount': self.get_trade_amount(),
            'consecutive_losses': self.consecutive_losses,
            'recovery_active': self.recovery_active,
            'total_recovered': self.total_recovered
        }


class IntelligentStrategy:
    """Adaptive multi-strategy system with learning"""
    
    def __init__(self, memory: TradingMemory):
        self.memory = memory
        self.ta = TechnicalAnalysis()
        self.last_signal_time = {}
        self.min_signal_interval = 60  # Seconds between signals
    
    def get_signal(self, asset: str, candles: List[dict], session: dict) -> Tuple[Optional[str], float, str, dict]:
        """
        Generate intelligent trading signal
        Returns: (direction, confidence, strategy_name, info)
        """
        if not candles or len(candles) < 20:
            return None, 0, "insufficient_data", {}
        
        # Check cooldown
        now = time.time()
        if asset in self.last_signal_time:
            if now - self.last_signal_time[asset] < self.min_signal_interval:
                return None, 0, "cooldown", {}
        
        prices = [c['close'] for c in candles]
        signals = []
        
        # Get asset's historical performance
        best_direction = self.memory.get_best_direction(asset)
        
        # Calculate all indicators
        rsi = self.ta.calculate_rsi(prices)
        stoch_k, stoch_d = self.ta.calculate_stochastic(prices)
        bb_upper, bb_lower, current, bb_pos = self.ta.calculate_bollinger_bands(prices)
        macd_line, signal_line, hist = self.ta.calculate_macd(prices)
        momentum = self.ta.calculate_momentum(prices)
        support, resistance = self.ta.calculate_support_resistance(prices)
        
        # 1. RSI Extreme Reversal (most reliable)
        if rsi < 20:  # Extremely oversold
            conf = 0.75
            weight = self.memory.get_strategy_weight('rsi_extreme')
            signals.append(('CALL', conf * weight, 'rsi_extreme', 
                           {'rsi': rsi, 'weight': weight}))
        elif rsi > 80:  # Extremely overbought
            conf = 0.75
            weight = self.memory.get_strategy_weight('rsi_extreme')
            signals.append(('PUT', conf * weight, 'rsi_extreme', 
                           {'rsi': rsi, 'weight': weight}))
        elif rsi < 30:
            conf = 0.62
            weight = self.memory.get_strategy_weight('rsi_oversold')
            signals.append(('CALL', conf * weight, 'rsi_oversold', 
                           {'rsi': rsi, 'weight': weight}))
        elif rsi > 70:
            conf = 0.62
            weight = self.memory.get_strategy_weight('rsi_overbought')
            signals.append(('PUT', conf * weight, 'rsi_overbought', 
                           {'rsi': rsi, 'weight': weight}))
        
        # 2. Stochastic Crossover (good for reversals)
        if stoch_k < 15 and stoch_d < 15:
            conf = 0.68
            weight = self.memory.get_strategy_weight('stoch_oversold')
            signals.append(('CALL', conf * weight, 'stoch_oversold', 
                           {'stoch_k': stoch_k, 'stoch_d': stoch_d}))
        elif stoch_k > 85 and stoch_d > 85:
            conf = 0.68
            weight = self.memory.get_strategy_weight('stoch_overbought')
            signals.append(('PUT', conf * weight, 'stoch_overbought', 
                           {'stoch_k': stoch_k, 'stoch_d': stoch_d}))
        
        # 3. Bollinger Band Bounce
        if bb_pos < 0.05:
            conf = 0.70
            weight = self.memory.get_strategy_weight('bb_bounce')
            signals.append(('CALL', conf * weight, 'bb_bounce', 
                           {'bb_pos': bb_pos, 'weight': weight}))
        elif bb_pos > 0.95:
            conf = 0.70
            weight = self.memory.get_strategy_weight('bb_bounce')
            signals.append(('PUT', conf * weight, 'bb_bounce', 
                           {'bb_pos': bb_pos, 'weight': weight}))
        
        # 4. Support/Resistance Bounce
        price_range = resistance - support
        if price_range > 0:
            near_support = (current - support) / price_range < 0.1
            near_resistance = (resistance - current) / price_range < 0.1
            
            if near_support:
                conf = 0.65
                weight = self.memory.get_strategy_weight('support_bounce')
                signals.append(('CALL', conf * weight, 'support_bounce', 
                               {'support': support, 'current': current}))
            elif near_resistance:
                conf = 0.65
                weight = self.memory.get_strategy_weight('resistance_bounce')
                signals.append(('PUT', conf * weight, 'resistance_bounce', 
                               {'resistance': resistance, 'current': current}))
        
        # 5. Momentum Reversal (counter-trend for binary)
        if momentum > 1.0 and rsi > 60:  # Strong up momentum, expect reversal
            conf = 0.58
            weight = self.memory.get_strategy_weight('momentum_reversal')
            signals.append(('PUT', conf * weight, 'momentum_reversal', 
                           {'momentum': momentum}))
        elif momentum < -1.0 and rsi < 40:  # Strong down momentum
            conf = 0.58
            weight = self.memory.get_strategy_weight('momentum_reversal')
            signals.append(('CALL', conf * weight, 'momentum_reversal', 
                           {'momentum': momentum}))
        
        # 6. Combined Signal (multiple indicators agree)
        call_votes = sum(1 for s in signals if s[0] == 'CALL')
        put_votes = sum(1 for s in signals if s[0] == 'PUT')
        
        if call_votes >= 3:
            # Strong CALL signal
            avg_conf = sum(s[1] for s in signals if s[0] == 'CALL') / call_votes
            signals.append(('CALL', min(avg_conf * 1.2, 0.85), 'combined', 
                           {'votes': call_votes, 'strategies': call_votes}))
        elif put_votes >= 3:
            # Strong PUT signal
            avg_conf = sum(s[1] for s in signals if s[0] == 'PUT') / put_votes
            signals.append(('PUT', min(avg_conf * 1.2, 0.85), 'combined', 
                           {'votes': put_votes, 'strategies': put_votes}))
        
        if not signals:
            return None, 0, "no_signal", {}
        
        # Filter by historical asset performance
        if best_direction:
            # Boost signals matching best direction
            for i, (dir_, conf, strat, info) in enumerate(signals):
                if dir_ == best_direction:
                    signals[i] = (dir_, conf * 1.15, strat, {**info, 'asset_boost': True})
        
        # Select best signal
        best = max(signals, key=lambda x: x[1])
        direction, confidence, strategy, info = best
        
        # Apply minimum confidence threshold
        min_confidence = 0.55
        if confidence < min_confidence:
            return None, 0, "low_confidence", {'confidence': confidence}
        
        self.last_signal_time[asset] = now
        return direction, confidence, strategy, info


class TechnicalAnalysis:
    """Technical analysis calculations"""
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        if len(prices) < period + 1:
            return 50
        gains, losses = [], []
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
    def calculate_stochastic(prices: List[float], k_period: int = 14) -> Tuple[float, float]:
        if len(prices) < k_period:
            return 50, 50
        high = max(prices[-k_period:])
        low = min(prices[-k_period:])
        close = prices[-1]
        if high == low:
            return 50, 50
        k = ((close - low) / (high - low)) * 100
        # Simplified %D
        d = k * 0.9
        return k, d
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20) -> Tuple[float, float, float, float]:
        if len(prices) < period:
            return 0, 0, 0, 0.5
        sma = sum(prices[-period:]) / period
        variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
        std = variance ** 0.5
        upper = sma + (2 * std)
        lower = sma - (2 * std)
        current = prices[-1]
        if upper != lower:
            position = (current - lower) / (upper - lower)
        else:
            position = 0.5
        return upper, lower, current, position
    
    @staticmethod
    def calculate_macd(prices: List[float]) -> Tuple[float, float, float]:
        if len(prices) < 26:
            return 0, 0, 0
        ema_12 = sum(prices[-12:]) / 12
        ema_26 = sum(prices[-26:]) / 26
        macd_line = ema_12 - ema_26
        signal_line = macd_line * 0.9
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_momentum(prices: List[float], period: int = 10) -> float:
        if len(prices) < period:
            return 0
        return (prices[-1] - prices[-period]) / prices[-period] * 100
    
    @staticmethod
    def calculate_support_resistance(prices: List[float], period: int = 20) -> Tuple[float, float]:
        if len(prices) < period:
            return prices[-1] * 0.99, prices[-1] * 1.01
        return min(prices[-period:]), max(prices[-period:])


class IntelligentIQOptionBot:
    """Main bot class with intelligent recovery"""
    
    def __init__(self):
        # API
        self.api = None
        self.email = os.environ.get('IQOPTION_EMAIL')
        self.password = os.environ.get('IQOPTION_PASSWORD')
        
        # Trading parameters
        self.base_trade_amount = 10.0  # Conservative $10 base
        self.max_trades_per_hour = 20
        self.daily_profit_target = 100.0
        self.daily_loss_limit = 200.0
        
        # State
        self.balance = 0
        self.start_balance = 0
        self.total_trades = 0
        self.wins = 0
        self.losses = 0
        self.total_profit = 0.0
        self.daily_pnl = 0.0
        self.trades_this_hour = 0
        self.last_hour_reset = datetime.now()
        self.running = False
        
        # Components
        self.memory = TradingMemory()
        self.recovery = SmartRecovery(base_amount=self.base_trade_amount)
        self.strategy = IntelligentStrategy(self.memory)
        
        # Assets
        self.available_assets = []
        self.current_session = None
        
        # Session tracking
        self.trades_by_session = {'Asian': 0, 'London': 0, 'New York': 0, 'Off-Hours': 0}
    
    def connect(self) -> bool:
        """Connect to IQ Option"""
        try:
            self.api = IQ_Option(self.email, self.password)
            check, reason = self.api.connect()
            
            if check:
                self.api.change_balance('PRACTICE')
                self.balance = self.api.get_balance()
                self.start_balance = self.balance
                logger.info(f"✅ Connected! Balance: ${self.balance:.2f}")
                return True
            else:
                logger.error(f"❌ Connection failed: {reason}")
                return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def get_current_session(self) -> dict:
        """Determine current trading session"""
        utc_now = datetime.now(pytz.UTC)
        
        sessions = [
            {'name': 'Asian', 'tz': 'Asia/Tokyo', 'hours': (0, 8)},
            {'name': 'London', 'tz': 'Europe/London', 'hours': (8, 16)},
            {'name': 'New York', 'tz': 'America/New_York', 'hours': (13, 21)},
        ]
        
        for session in sessions:
            tz = pytz.timezone(session['tz'])
            local_time = utc_now.astimezone(tz)
            if session['hours'][0] <= local_time.hour < session['hours'][1]:
                return session
        
        return {'name': 'Off-Hours', 'tz': 'UTC', 'hours': None}
    
    def get_available_assets(self) -> List[str]:
        """Get list of available OTC assets"""
        otc_assets = ['EURUSD-OTC', 'GBPUSD-OTC', 'EURJPY-OTC', 
                      'EURGBP-OTC', 'GBPJPY-OTC', 'USDCHF-OTC']
        available = []
        
        for asset in otc_assets:
            try:
                result = self.api.buy(1, asset, 'CALL', 1)
                if result and result[0]:
                    available.append(asset)
                time.sleep(0.3)
            except:
                pass
        
        # Prioritize best performing assets
        best_assets = self.memory.get_best_assets(limit=4)
        
        # Sort: best assets first, then others
        sorted_assets = []
        for asset in best_assets:
            if asset in available:
                sorted_assets.append(asset)
        for asset in available:
            if asset not in sorted_assets:
                sorted_assets.append(asset)
        
        return sorted_assets if sorted_assets else available
    
    def get_candles(self, asset: str, timeframe: int = 60, count: int = 100) -> List[dict]:
        """Get candle data"""
        try:
            candles = self.api.get_candles(asset, timeframe, count, time.time())
            if candles:
                return candles
        except Exception as e:
            logger.debug(f"Candle error for {asset}: {e}")
        return []
    
    def place_trade(self, asset: str, direction: str, amount: float) -> Optional[int]:
        """Place a binary option trade"""
        try:
            logger.info(f"🎯 Placing {direction} trade on {asset} for ${amount:.2f}")
            # Use 1-minute expiry for faster results
            result, trade_id = self.api.buy(amount, asset, direction, 1)
            logger.info(f"📊 Trade result: {result}, trade_id: {trade_id}")
            if result:
                logger.info(f"✅ Trade placed successfully: {trade_id}")
                return trade_id
            else:
                logger.warning(f"⚠️ Trade rejected: result={result}")
        except Exception as e:
            logger.error(f"❌ Trade error: {e}")
        return None
    
    def check_trade_result(self, trade_id: int, timeout: int = 120) -> Optional[float]:
        """Wait for trade result"""
        logger.info(f"⏳ Waiting for result of trade {trade_id}...")
        start = time.time()
        check_count = 0
        while time.time() - start < timeout:
            try:
                check_count += 1
                result = self.api.check_win_v3(trade_id)
                logger.debug(f"Check #{check_count}: result={result}")
                if result is not None:
                    logger.info(f"🎯 Trade {trade_id} result: {result}")
                    return result
            except Exception as e:
                logger.warning(f"⚠️ Error checking trade result (attempt {check_count}): {e}")
            time.sleep(2)
        logger.error(f"❌ Timeout waiting for trade {trade_id} result after {timeout}s")
        return None
    
    def run_trading_cycle(self):
        """Execute one trading cycle"""
        # Reset hourly counter
        now = datetime.now()
        if (now - self.last_hour_reset).total_seconds() >= 3600:
            self.trades_this_hour = 0
            self.last_hour_reset = now
        
        # Check limits
        if self.trades_this_hour >= self.max_trades_per_hour:
            return
        
        if self.daily_pnl <= -self.daily_loss_limit:
            logger.warning(f"🛑 Daily loss limit reached: ${-self.daily_pnl:.2f}")
            return
        
        if self.daily_pnl >= self.daily_profit_target:
            logger.info(f"🎯 Daily profit target reached: ${self.daily_pnl:.2f}")
            return
        
        # Check recovery pause
        if self.recovery.should_pause():
            streak, _ = self.memory.get_recent_streak()
            logger.warning(f"⏸️ Recovery pause: {streak} consecutive losses")
            return
        
        # Update session
        self.current_session = self.get_current_session()
        
        # Update assets periodically
        if not self.available_assets or self.total_trades % 10 == 0:
            self.available_assets = self.get_available_assets()
            logger.info(f"📈 Available assets: {self.available_assets}")
        
        # Get trade amount
        trade_amount = self.recovery.get_trade_amount()
        
        # Find signals
        for asset in self.available_assets[:4]:  # Check top 4 assets
            candles = self.get_candles(asset)
            if not candles:
                continue
            
            direction, confidence, strategy, info = self.strategy.get_signal(
                asset, candles, self.current_session
            )
            
            if direction and confidence >= 0.55:
                logger.info(f"📈 Signal: {direction} {asset} @ {confidence*100:.0f}% | {strategy} | {info}")
                
                trade_id = self.place_trade(asset, direction, trade_amount)
                
                if trade_id:
                    self.trades_this_hour += 1
                    self.total_trades += 1
                    
                    result = self.check_trade_result(trade_id)
                    
                    if result is not None:
                        if result > 0:
                            profit = result
                            self.wins += 1
                            self.total_profit += profit
                            self.daily_pnl += profit
                            self.recovery.record_trade(True, profit)
                            self.memory.record_trade(asset, direction, strategy, 
                                                      self.current_session['name'], True, profit)
                            logger.info(f"✅ WIN: +${profit:.2f} (#{self.total_trades})")
                        elif result < 0:
                            loss = trade_amount + result
                            self.losses += 1
                            self.total_profit -= loss
                            self.daily_pnl -= loss
                            self.recovery.record_trade(False, -loss)
                            self.memory.record_trade(asset, direction, strategy,
                                                      self.current_session['name'], False, -loss)
                            logger.info(f"❌ LOSS: -${loss:.2f} (#{self.total_trades})")
                        else:
                            logger.info(f"🤝 TIE (#{self.total_trades})")
                        
                        self.balance = self.api.get_balance()
                        return  # One trade per cycle
        
        # Save memory periodically
        if self.total_trades % 5 == 0:
            self.memory.save()
    
    def print_status(self):
        """Print detailed status"""
        win_rate = (self.wins / self.total_trades * 100) if self.total_trades > 0 else 0
        recovery_status = self.recovery.get_status()
        
        logger.info(f"""
╔═══════════════════════════════════════════════════════════════╗
║         🧠 INTELLIGENT IQ OPTION BOT v4 🧠                    ║
╚═══════════════════════════════════════════════════════════════╝
🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌍 Session: {self.current_session['name'] if self.current_session else 'N/A'}
💰 Balance: ${self.balance:.2f} (Start: ${self.start_balance:.2f})
📊 Trades: {self.total_trades} | W:{self.wins} L:{self.losses}
🎯 Win Rate: {win_rate:.1f}%
💵 Total P&L: ${self.total_profit:+.2f}
💵 Daily P&L: ${self.daily_pnl:+.2f}
⚡ Hourly: {self.trades_this_hour}/{self.max_trades_per_hour}
📈 Assets: {len(self.available_assets)} available
🔄 Recovery Level: {recovery_status['current_level']}/{self.recovery.max_levels}
📊 Next Trade: ${recovery_status['next_amount']:.2f}
🧠 Memory: {len(self.memory.asset_stats)} assets tracked
""")
    
    def run(self):
        """Main loop"""
        logger.info("🚀 Starting INTELLIGENT trading bot v4...")
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
            self.memory.save()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        cycle = 0
        
        while self.running:
            try:
                cycle += 1
                
                self.run_trading_cycle()
                
                if cycle % 10 == 0:
                    self.print_status()
                
                time.sleep(30)  # 30-second cycles
                
                # Reconnect if needed
                if not self.api or not self.api.check_connect():
                    logger.info("🔄 Reconnecting...")
                    self.connect()
            
            except Exception as e:
                logger.error(f"Error: {e}")
                time.sleep(60)
                
                if not self.api or not self.api.check_connect():
                    self.connect()
        
        # Save memory on exit
        self.memory.save()
        logger.info("Bot stopped - memory saved")


if __name__ == "__main__":
    bot = IntelligentIQOptionBot()
    bot.run()
