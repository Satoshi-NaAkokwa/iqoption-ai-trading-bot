#!/usr/bin/env python3
"""
IQ Option 24/7 Learning Bot v5
- TRUE 24/7 trading - no session restrictions
- Learns from ALL market conditions
- Tracks performance by hour, day, volatility, trend
- Adaptive strategy selection based on conditions
- Continuous optimization through reinforcement
- Detailed market condition logging for analysis
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
from collections import deque, defaultdict
import math

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


class MarketConditionAnalyzer:
    """Analyze and classify market conditions for learning"""
    
    @staticmethod
    def classify_volatility(prices: List[float]) -> str:
        """Classify market volatility"""
        if len(prices) < 20:
            return "unknown"
        
        returns = [(prices[i] - prices[i-1]) / prices[i-1] * 100 for i in range(1, len(prices))]
        std = math.sqrt(sum((r - sum(returns)/len(returns))**2 for r in returns) / len(returns))
        
        if std < 0.02:
            return "low"
        elif std < 0.05:
            return "medium"
        elif std < 0.10:
            return "high"
        else:
            return "extreme"
    
    @staticmethod
    def classify_trend(prices: List[float]) -> str:
        """Classify market trend"""
        if len(prices) < 20:
            return "unknown"
        
        sma_short = sum(prices[-5:]) / 5
        sma_long = sum(prices[-20:]) / 20
        
        if sma_short > sma_long * 1.002:
            return "strong_uptrend"
        elif sma_short > sma_long:
            return "uptrend"
        elif sma_short < sma_long * 0.998:
            return "strong_downtrend"
        elif sma_short < sma_long:
            return "downtrend"
        else:
            return "ranging"
    
    @staticmethod
    def get_time_context() -> dict:
        """Get time-based context for trading"""
        utc_now = datetime.now(pytz.UTC)
        
        # Market sessions overlap analysis
        tokyo_open = 0 <= utc_now.hour < 9
        london_open = 7 <= utc_now.hour < 16
        ny_open = 13 <= utc_now.hour < 22
        
        session_overlap = ""
        if tokyo_open and london_open:
            session_overlap = "tokyo_london"
        elif london_open and ny_open:
            session_overlap = "london_ny"
        elif tokyo_open:
            session_overlap = "tokyo"
        elif london_open:
            session_overlap = "london"
        elif ny_open:
            session_overlap = "ny"
        else:
            session_overlap = "quiet"
        
        return {
            'hour': utc_now.hour,
            'day_of_week': utc_now.weekday(),  # 0=Monday
            'session_overlap': session_overlap,
            'is_weekend': utc_now.weekday() >= 5
        }


class AdvancedTradingMemory:
    """Enhanced memory with market condition learning"""
    
    def __init__(self, memory_file: str = 'trading_memory_v5.json'):
        self.memory_file = memory_file
        
        # Core stats
        self.asset_direction_stats = {}  # {asset: {direction: {wins, losses, total_pnl}}}
        self.strategy_stats = {}  # {strategy: {wins, losses, total_pnl, conditions: {}}}
        
        # Market condition tracking
        self.condition_stats = {
            'volatility': {},  # {low/medium/high/extreme: {wins, losses}}
            'trend': {},       # {uptrend/downtrend/ranging: {wins, losses}}
            'session': {},     # {tokyo/london/ny/overlap: {wins, losses}}
            'hour': {},        # {0-23: {wins, losses}}
        }
        
        # Strategy performance by condition
        self.strategy_by_condition = defaultdict(lambda: defaultdict(lambda: {'wins': 0, 'losses': 0}))
        
        # Recent trades for pattern analysis
        self.recent_trades = deque(maxlen=200)
        
        # Learning rates
        self.learning_rate = 0.1
        self.exploration_rate = 0.15  # 15% random exploration
        
        self.load()
    
    def load(self):
        """Load memory from file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.asset_direction_stats = data.get('asset_direction_stats', {})
                    self.strategy_stats = data.get('strategy_stats', {})
                    self.condition_stats = data.get('condition_stats', {
                        'volatility': {}, 'trend': {}, 'session': {}, 'hour': {}
                    })
                    self.learning_rate = data.get('learning_rate', 0.1)
                    self.exploration_rate = data.get('exploration_rate', 0.15)
                    logger.info(f"📊 Loaded advanced memory: {len(self.asset_direction_stats)} assets, {len(self.strategy_stats)} strategies")
        except Exception as e:
            logger.warning(f"Could not load memory: {e}")
    
    def save(self):
        """Save memory to file"""
        try:
            data = {
                'asset_direction_stats': self.asset_direction_stats,
                'strategy_stats': self.strategy_stats,
                'condition_stats': self.condition_stats,
                'learning_rate': self.learning_rate,
                'exploration_rate': self.exploration_rate,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.memory_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save memory: {e}")
    
    def record_trade(self, asset: str, direction: str, strategy: str,
                     conditions: dict, won: bool, pnl: float, confidence: float):
        """Record trade with full context"""
        
        # Asset + Direction stats
        if asset not in self.asset_direction_stats:
            self.asset_direction_stats[asset] = {}
        if direction not in self.asset_direction_stats[asset]:
            self.asset_direction_stats[asset][direction] = {'wins': 0, 'losses': 0, 'total_pnl': 0}
        
        stats = self.asset_direction_stats[asset][direction]
        if won:
            stats['wins'] += 1
        else:
            stats['losses'] += 1
        stats['total_pnl'] += pnl
        
        # Strategy stats
        if strategy not in self.strategy_stats:
            self.strategy_stats[strategy] = {'wins': 0, 'losses': 0, 'total_pnl': 0}
        
        strat_stats = self.strategy_stats[strategy]
        if won:
            strat_stats['wins'] += 1
        else:
            strat_stats['losses'] += 1
        strat_stats['total_pnl'] += pnl
        
        # Condition stats
        volatility = conditions.get('volatility', 'unknown')
        trend = conditions.get('trend', 'unknown')
        session = conditions.get('session', 'unknown')
        hour = conditions.get('hour', -1)
        
        for condition_type, condition_value in [
            ('volatility', volatility),
            ('trend', trend),
            ('session', session),
            ('hour', str(hour))
        ]:
            if condition_value not in self.condition_stats[condition_type]:
                self.condition_stats[condition_type][condition_value] = {'wins': 0, 'losses': 0}
            if won:
                self.condition_stats[condition_type][condition_value]['wins'] += 1
            else:
                self.condition_stats[condition_type][condition_value]['losses'] += 1
        
        # Strategy by condition
        condition_key = f"{volatility}_{trend}_{session}"
        if won:
            self.strategy_by_condition[condition_key][strategy]['wins'] += 1
        else:
            self.strategy_by_condition[condition_key][strategy]['losses'] += 1
        
        # Recent trades
        self.recent_trades.append({
            'asset': asset,
            'direction': direction,
            'strategy': strategy,
            'conditions': conditions,
            'won': won,
            'pnl': pnl,
            'confidence': confidence,
            'time': datetime.now().isoformat()
        })
        
        # Adaptive learning rate
        if len(self.recent_trades) % 50 == 0:
            self._adapt_learning_parameters()
        
        # Save periodically
        if len(self.recent_trades) % 10 == 0:
            self.save()
    
    def _adapt_learning_parameters(self):
        """Adjust learning parameters based on performance"""
        recent = list(self.recent_trades)[-50:]
        if len(recent) < 20:
            return
        
        wins = sum(1 for t in recent if t['won'])
        win_rate = wins / len(recent)
        
        # Increase exploration if win rate is low
        if win_rate < 0.45:
            self.exploration_rate = min(0.30, self.exploration_rate + 0.02)
            logger.info(f"🔍 Increasing exploration to {self.exploration_rate:.0%} (win rate: {win_rate:.1%})")
        elif win_rate > 0.65:
            self.exploration_rate = max(0.05, self.exploration_rate - 0.02)
            logger.info(f"🎯 Reducing exploration to {self.exploration_rate:.0%} (win rate: {win_rate:.1%})")
    
    def get_asset_direction_score(self, asset: str, direction: str) -> float:
        """Get score for asset+direction combination"""
        if asset not in self.asset_direction_stats:
            return 0.5
        if direction not in self.asset_direction_stats[asset]:
            return 0.5
        
        stats = self.asset_direction_stats[asset][direction]
        total = stats['wins'] + stats['losses']
        if total < 3:
            return 0.5
        
        return stats['wins'] / total
    
    def get_best_strategy_for_conditions(self, conditions: dict) -> Tuple[str, float]:
        """Get best performing strategy for current conditions"""
        volatility = conditions.get('volatility', 'unknown')
        trend = conditions.get('trend', 'unknown')
        session = conditions.get('session', 'unknown')
        
        condition_key = f"{volatility}_{trend}_{session}"
        
        strategies = self.strategy_by_condition.get(condition_key, {})
        if not strategies:
            return None, 0.0
        
        best_strategy = None
        best_score = 0.0
        
        for strat, stats in strategies.items():
            total = stats['wins'] + stats['losses']
            if total < 2:
                continue
            score = stats['wins'] / total
            if score > best_score:
                best_score = score
                best_strategy = strat
        
        return best_strategy, best_score
    
    def get_condition_score(self, conditions: dict) -> float:
        """Get overall score for current conditions"""
        scores = []
        
        for condition_type in ['volatility', 'trend', 'session']:
            value = conditions.get(condition_type, 'unknown')
            stats = self.condition_stats[condition_type].get(value, {'wins': 0, 'losses': 0})
            total = stats['wins'] + stats['losses']
            if total > 0:
                scores.append(stats['wins'] / total)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def should_explore(self) -> bool:
        """Determine if we should explore (try new strategies)"""
        import random
        return random.random() < self.exploration_rate


class AdaptiveStrategy:
    """Strategy system that adapts to market conditions"""
    
    def __init__(self, memory: AdvancedTradingMemory):
        self.memory = memory
        self.condition_analyzer = MarketConditionAnalyzer()
        self.last_signal_time = {}
        self.min_signal_interval = 45  # Faster cycles for more trades
    
    def get_signal(self, asset: str, candles: List[dict]) -> Tuple[Optional[str], float, str, dict]:
        """
        Generate adaptive trading signal
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
        
        # Analyze market conditions
        volatility = self.condition_analyzer.classify_volatility(prices)
        trend = self.condition_analyzer.classify_trend(prices)
        time_context = self.condition_analyzer.get_time_context()
        
        conditions = {
            'volatility': volatility,
            'trend': trend,
            'session': time_context['session_overlap'],
            'hour': time_context['hour'],
            'day_of_week': time_context['day_of_week']
        }
        
        # Exploration mode - try random strategies
        if self.memory.should_explore():
            direction, strategy, info = self._explore_strategy(asset, prices, conditions)
            if direction:
                self.last_signal_time[asset] = now
                return direction, 0.55, strategy, {**info, 'exploration': True, 'conditions': conditions}
        
        # Get best strategy for conditions
        best_strat, best_strat_score = self.memory.get_best_strategy_for_conditions(conditions)
        
        # Calculate indicators
        rsi = self._calculate_rsi(prices)
        stoch_k, stoch_d = self._calculate_stochastic(prices)
        bb_upper, bb_lower, current, bb_pos = self._calculate_bollinger(prices)
        macd_line, signal_line, hist = self._calculate_macd(prices)
        
        signals = []
        
        # 1. RSI Strategies
        if rsi < 25:
            signals.append(('CALL', 0.72, 'rsi_extreme_oversold', {'rsi': rsi}))
        elif rsi > 75:
            signals.append(('PUT', 0.72, 'rsi_extreme_overbought', {'rsi': rsi}))
        elif rsi < 30:
            signals.append(('CALL', 0.60, 'rsi_oversold', {'rsi': rsi}))
        elif rsi > 70:
            signals.append(('PUT', 0.60, 'rsi_overbought', {'rsi': rsi}))
        
        # 2. Stochastic
        if stoch_k < 15 and stoch_d < 20:
            signals.append(('CALL', 0.68, 'stoch_oversold', {'k': stoch_k, 'd': stoch_d}))
        elif stoch_k > 85 and stoch_d > 80:
            signals.append(('PUT', 0.68, 'stoch_overbought', {'k': stoch_k, 'd': stoch_d}))
        
        # 3. Bollinger Bands
        if bb_pos < 0.08:
            signals.append(('CALL', 0.70, 'bb_lower_bounce', {'bb_pos': bb_pos}))
        elif bb_pos > 0.92:
            signals.append(('PUT', 0.70, 'bb_upper_bounce', {'bb_pos': bb_pos}))
        
        # 4. Trend-following (for ranging markets)
        if trend in ['uptrend', 'strong_uptrend'] and rsi > 40 and rsi < 65:
            signals.append(('CALL', 0.58, 'trend_follow_up', {'trend': trend}))
        elif trend in ['downtrend', 'strong_downtrend'] and rsi > 35 and rsi < 60:
            signals.append(('PUT', 0.58, 'trend_follow_down', {'trend': trend}))
        
        # 5. Counter-trend (for extreme conditions)
        if trend == 'strong_uptrend' and rsi > 70:
            signals.append(('PUT', 0.62, 'counter_trend_up', {'trend': trend, 'rsi': rsi}))
        elif trend == 'strong_downtrend' and rsi < 30:
            signals.append(('CALL', 0.62, 'counter_trend_down', {'trend': trend, 'rsi': rsi}))
        
        # 6. MACD
        if macd_line > signal_line and hist > 0 and hist < 0.1:
            signals.append(('CALL', 0.60, 'macd_bullish', {'macd': macd_line}))
        elif macd_line < signal_line and hist < 0 and hist > -0.1:
            signals.append(('PUT', 0.60, 'macd_bearish', {'macd': macd_line}))
        
        if not signals:
            return None, 0, "no_signal", {'conditions': conditions}
        
        # Boost signals from best-performing strategies
        if best_strat and best_strat_score > 0.55:
            for i, (dir_, conf, strat, info) in enumerate(signals):
                if strat == best_strat:
                    signals[i] = (dir_, conf * 1.2, strat, {**info, 'condition_boost': True})
        
        # Apply asset-specific learning
        for i, (dir_, conf, strat, info) in enumerate(signals):
            asset_score = self.memory.get_asset_direction_score(asset, dir_)
            if asset_score > 0.6:
                signals[i] = (dir_, conf * 1.1, strat, {**info, 'asset_boost': True})
            elif asset_score < 0.4:
                signals[i] = (dir_, conf * 0.9, strat, {**info, 'asset_penalty': True})
        
        # Select best signal
        best = max(signals, key=lambda x: x[1])
        direction, confidence, strategy, info = best
        
        # Minimum threshold
        if confidence < 0.52:
            return None, 0, "low_confidence", {'confidence': confidence, 'conditions': conditions}
        
        self.last_signal_time[asset] = now
        return direction, min(confidence, 0.85), strategy, {**info, 'conditions': conditions}
    
    def _explore_strategy(self, asset: str, prices: List[float], conditions: dict) -> Tuple[str, str, dict]:
        """Explore different strategies for learning"""
        import random
        
        strategies = ['rsi_extreme', 'stoch_cross', 'bb_bounce', 'trend_follow', 'counter_trend']
        directions = ['CALL', 'PUT']
        
        # Weighted random selection
        rsi = self._calculate_rsi(prices)
        trend = conditions.get('trend', 'ranging')
        
        # Bias exploration based on current conditions
        if rsi < 35:
            direction = 'CALL'
        elif rsi > 65:
            direction = 'PUT'
        else:
            direction = random.choice(directions)
        
        strategy = random.choice(strategies)
        
        return direction, f"explore_{strategy}", {'exploration': True}
    
    # Technical indicators (same as before)
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
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
    
    def _calculate_stochastic(self, prices: List[float], k_period: int = 14) -> Tuple[float, float]:
        if len(prices) < k_period:
            return 50, 50
        high = max(prices[-k_period:])
        low = min(prices[-k_period:])
        close = prices[-1]
        if high == low:
            return 50, 50
        k = ((close - low) / (high - low)) * 100
        d = k * 0.9
        return k, d
    
    def _calculate_bollinger(self, prices: List[float], period: int = 20) -> Tuple[float, float, float, float]:
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
    
    def _calculate_macd(self, prices: List[float]) -> Tuple[float, float, float]:
        if len(prices) < 26:
            return 0, 0, 0
        ema_12 = sum(prices[-12:]) / 12
        ema_26 = sum(prices[-26:]) / 26
        macd_line = ema_12 - ema_26
        signal_line = macd_line * 0.9
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram


class SmartRecovery:
    """Intelligent Martingale with condition-aware recovery"""
    
    def __init__(self, base_amount: float = 10.0, max_levels: int = 4):
        self.base_amount = base_amount
        self.max_levels = max_levels
        self.current_level = 0
        self.multiplier = 1.5
        self.consecutive_losses = 0
        self.total_recovered = 0.0
        self.pause_until = None
        self.pause_duration = 180  # 3 minutes
    
    def get_trade_amount(self) -> float:
        amount = self.base_amount * (self.multiplier ** self.current_level)
        return round(amount, 2)
    
    def record_trade(self, won: bool, pnl: float = 0):
        if won:
            if self.current_level > 0:
                self.total_recovered += pnl
                logger.info(f"💰 Recovery win: +${pnl:.2f}")
            self.current_level = 0
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
            if self.consecutive_losses >= 2:
                self.current_level = min(self.current_level + 1, self.max_levels - 1)
                if self.consecutive_losses >= self.max_levels:
                    self.pause_until = time.time() + self.pause_duration
                    logger.warning(f"⏸️ Pausing for {self.pause_duration}s after {self.consecutive_losses} losses")
    
    def should_pause(self) -> bool:
        if self.pause_until and time.time() < self.pause_until:
            return True
        if self.pause_until and time.time() >= self.pause_until:
            self.pause_until = None
            self.reset()
        return False
    
    def reset(self):
        self.current_level = 0
        self.consecutive_losses = 0
        self.pause_until = None
    
    def get_status(self) -> dict:
        return {
            'level': self.current_level,
            'losses': self.consecutive_losses,
            'next_amount': self.get_trade_amount(),
            'paused': self.pause_until is not None
        }


class IQOption247LearningBot:
    """24/7 Trading Bot with continuous learning"""
    
    def __init__(self):
        # API
        self.api = None
        self.email = os.environ.get('IQOPTION_EMAIL')
        self.password = os.environ.get('IQOPTION_PASSWORD')
        
        # 24/7 Parameters - NO LIMITS
        self.base_trade_amount = 10.0
        self.max_trades_per_hour = 30  # More trades = more learning
        self.daily_profit_target = 10000.0  # Very high - don't stop
        self.daily_loss_limit = 5000.0  # High limit for learning
        
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
        self.memory = AdvancedTradingMemory()
        self.recovery = SmartRecovery(base_amount=self.base_trade_amount)
        self.strategy = AdaptiveStrategy(self.memory)
        
        # Assets
        self.available_assets = []
        self.current_conditions = {}
        
        # Session tracking for analysis
        self.session_stats = defaultdict(lambda: {'trades': 0, 'wins': 0, 'pnl': 0})
    
    def connect(self) -> bool:
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
    
    def get_available_assets(self) -> List[str]:
        """Get all available OTC assets"""
        otc_assets = ['EURUSD-OTC', 'GBPUSD-OTC', 'EURJPY-OTC',
                      'EURGBP-OTC', 'GBPJPY-OTC', 'USDCHF-OTC',
                      'AUDUSD-OTC', 'NZDUSD-OTC', 'USDCAD-OTC']
        available = []
        
        for asset in otc_assets[:6]:  # Check first 6
            try:
                result = self.api.buy(1, asset, 'CALL', 1)
                if result and result[0]:
                    available.append(asset)
                time.sleep(0.2)
            except:
                pass
        
        return available if available else otc_assets[:6]
    
    def get_candles(self, asset: str, timeframe: int = 60, count: int = 100) -> List[dict]:
        try:
            candles = self.api.get_candles(asset, timeframe, count, time.time())
            return candles if candles else []
        except:
            return []
    
    def place_trade(self, asset: str, direction: str, amount: float) -> Optional[int]:
        try:
            logger.info(f"🎯 {direction} {asset} ${amount:.2f}")
            result, trade_id = self.api.buy(amount, asset, direction, 1)
            if result:
                logger.info(f"✅ Trade #{self.total_trades + 1}: {trade_id}")
                return trade_id
        except Exception as e:
            logger.error(f"Trade error: {e}")
        return None
    
    def check_trade_result(self, trade_id: int, timeout: int = 90) -> Optional[float]:
        start = time.time()
        while time.time() - start < timeout:
            try:
                result = self.api.check_win_v3(trade_id)
                if result is not None:
                    return result
            except:
                pass
            time.sleep(2)
        return None
    
    def run_trading_cycle(self):
        """Execute one trading cycle - NO SESSION RESTRICTIONS"""
        # Hourly reset
        now = datetime.now()
        if (now - self.last_hour_reset).total_seconds() >= 3600:
            self.trades_this_hour = 0
            self.last_hour_reset = now
            logger.info(f"⏰ New hour - trades reset. Hourly PnL: ${self.daily_pnl:.2f}")
        
        # Check limits (but keep trading for learning)
        if self.trades_this_hour >= self.max_trades_per_hour:
            return
        
        if self.recovery.should_pause():
            return
        
        # Get assets
        if not self.available_assets or self.total_trades % 15 == 0:
            self.available_assets = self.get_available_assets()
        
        trade_amount = self.recovery.get_trade_amount()
        
        # Check each asset for signals
        for asset in self.available_assets[:3]:
            candles = self.get_candles(asset)
            if not candles:
                continue
            
            direction, confidence, strategy, info = self.strategy.get_signal(asset, candles)
            
            if direction and confidence >= 0.52:
                conditions = info.get('conditions', {})
                self.current_conditions = conditions
                
                logger.info(f"📈 {strategy}: {direction} {asset} @ {confidence*100:.0f}%")
                logger.info(f"📊 Conditions: vol={conditions.get('volatility')}, trend={conditions.get('trend')}, session={conditions.get('session')}")
                
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
                                                      conditions, True, profit, confidence)
                            logger.info(f"✅ WIN: +${profit:.2f}")
                        else:
                            loss = trade_amount + result
                            self.losses += 1
                            self.total_profit -= loss
                            self.daily_pnl -= loss
                            self.recovery.record_trade(False, -loss)
                            self.memory.record_trade(asset, direction, strategy,
                                                      conditions, False, -loss, confidence)
                            logger.info(f"❌ LOSS: -${loss:.2f}")
                        
                        self.balance = self.api.get_balance()
                        
                        # Track session stats
                        session = conditions.get('session', 'unknown')
                        self.session_stats[session]['trades'] += 1
                        if result > 0:
                            self.session_stats[session]['wins'] += 1
                            self.session_stats[session]['pnl'] += profit
                        
                        return
        
        # Save memory periodically
        if self.total_trades % 5 == 0:
            self.memory.save()
    
    def print_status(self):
        """Print detailed status"""
        win_rate = (self.wins / self.total_trades * 100) if self.total_trades > 0 else 0
        recovery = self.recovery.get_status()
        
        logger.info(f"""
╔═══════════════════════════════════════════════════════════════╗
║         🧠 IQ OPTION 24/7 LEARNING BOT v5 🧠                  ║
╚═══════════════════════════════════════════════════════════════╝
🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📊 Trades: {self.total_trades} | W:{self.wins} L:{self.losses} | Win Rate: {win_rate:.1f}%
💰 Balance: ${self.balance:.2f} | P&L: ${self.total_profit:+.2f}
💵 Session P&L: ${self.daily_pnl:+.2f}
⚡ Trades/Hour: {self.trades_this_hour}/{self.max_trades_per_hour}
📈 Assets: {len(self.available_assets)} | Strategies: {len(self.memory.strategy_stats)}
🔍 Exploration: {self.memory.exploration_rate:.0%}
🔄 Recovery: Level {recovery['level']} | Next: ${recovery['next_amount']:.2f}
📊 Current: vol={self.current_conditions.get('volatility','-')} trend={self.current_conditions.get('trend','-')} session={self.current_conditions.get('session','-')}
""")
        
        # Print best strategies
        if self.memory.strategy_stats:
            sorted_strats = sorted(
                self.memory.strategy_stats.items(),
                key=lambda x: x[1].get('total_pnl', 0),
                reverse=True
            )[:5]
            logger.info("📈 Top Strategies:")
            for strat, stats in sorted_strats:
                total = stats['wins'] + stats['losses']
                if total > 0:
                    wr = stats['wins'] / total * 100
                    pnl = stats.get('total_pnl', 0)
                    logger.info(f"   {strat}: {wr:.0f}% WR, ${pnl:+.2f} PnL ({total} trades)")
    
    def run(self):
        """Main loop - TRUE 24/7"""
        logger.info("🚀 Starting 24/7 LEARNING BOT v5...")
        logger.info("💡 Trading continuously to learn all market conditions")
        logger.info(f"💰 Base: ${self.base_trade_amount} | Max/Hour: {self.max_trades_per_hour}")
        
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
                
                if cycle % 12 == 0:  # Every 6 minutes
                    self.print_status()
                
                time.sleep(30)  # 30-second cycles
                
                # Reconnect if needed
                if not self.api or not self.api.check_connect():
                    logger.info("🔄 Reconnecting...")
                    if not self.connect():
                        time.sleep(60)
            
            except Exception as e:
                logger.error(f"Error: {e}")
                time.sleep(60)
                
                if not self.api or not self.api.check_connect():
                    self.connect()
        
        self.memory.save()
        logger.info("Bot stopped - memory saved")


if __name__ == "__main__":
    bot = IQOption247LearningBot()
    bot.run()
