#!/usr/bin/env python3
"""
IQ Option V8 Bot - 90%+ WIN RATE TARGET
=======================================
FEATURES:
1. Fixed confidence calculation (no counter-trend trades)
2. Hour-based filtering (skip bad hours)
3. Asset filtering (best performers only)
4. 5+ indicator confluence required
5. Loss recovery system
6. SELF-LEARNING: Adapts based on performance
7. SELF-IMPROVEMENT: Auto-adjusts parameters
"""
import os
import sys
import time
import logging
import signal
import json
import math
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict
from collections import defaultdict
import pytz

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
with open(env_path) as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, val = line.strip().split('=', 1)
            os.environ[key] = val

from iqoptionapi.stable_api import IQ_Option

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_v8.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ============================================
# SELF-LEARNING CONFIGURATION
# ============================================

class SelfLearningConfig:
    """Dynamic configuration that learns from trading results"""
    
    def __init__(self, memory_file: str = 'learning_config_v8.json'):
        self.memory_file = memory_file
        self.config = {
            # Base parameters
            'min_confidence': 85,
            'min_indicators': 5,
            'base_amount': 10.0,
            
            # Hours to skip (learned from data)
            'skip_hours': [6, 12, 16, 20, 22],
            'best_hours': [0, 3, 7, 8, 9, 13, 14, 17, 21, 23],
            
            # Assets (learned from performance)
            'assets': ['EURUSD-OTC', 'EURJPY-OTC'],
            'asset_performance': {},
            
            # Loss recovery
            'max_consecutive_losses': 2,
            'pause_minutes': 30,
            
            # Learning metrics
            'hourly_performance': {},
            'indicator_accuracy': {
                'rsi': 0.5,
                'macd': 0.5,
                'bollinger': 0.5,
                'stochastic': 0.5,
                'trend': 0.5,
                'pattern': 0.5
            },
            
            # Adaptive thresholds
            'adaptive_confidence': True,
            'confidence_adjustment': 0,
            
            # Last update
            'last_learning_update': None,
            'total_trades_analyzed': 0
        }
        self.load()
    
    def load(self):
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
                logger.info(f"📚 Loaded learning config from {self.memory_file}")
        except Exception as e:
            logger.warning(f"Config load error: {e}")
    
    def save(self):
        try:
            self.config['last_learning_update'] = datetime.now().isoformat()
            with open(self.memory_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.warning(f"Config save error: {e}")
    
    def update_from_trades(self, trades: List[Dict]):
        """Learn from recent trades and adapt parameters"""
        if len(trades) < 10:
            return
        
        # Analyze hourly performance
        hour_wins = defaultdict(lambda: {'wins': 0, 'losses': 0})
        for trade in trades:
            hour = str(trade.get('hour', 0))
            if trade['result'] == 'WIN':
                hour_wins[hour]['wins'] += 1
            else:
                hour_wins[hour]['losses'] += 1
        
        # Update skip/best hours based on performance
        new_skip_hours = []
        new_best_hours = []
        
        for hour, stats in hour_wins.items():
            total = stats['wins'] + stats['losses']
            if total >= 3:  # Need minimum trades
                wr = stats['wins'] / total
                if wr < 0.45:  # Skip hours below 45% WR
                    new_skip_hours.append(int(hour))
                elif wr > 0.70:  # Best hours above 70% WR
                    new_best_hours.append(int(hour))
        
        if new_skip_hours:
            self.config['skip_hours'] = list(set(self.config['skip_hours'] + new_skip_hours))
        if new_best_hours:
            self.config['best_hours'] = list(set(self.config['best_hours'] + new_best_hours))
        
        # Analyze asset performance
        asset_perf = defaultdict(lambda: {'wins': 0, 'losses': 0, 'pnl': 0})
        for trade in trades:
            asset = trade['asset']
            asset_perf[asset]['pnl'] += trade.get('pnl', 0)
            if trade['result'] == 'WIN':
                asset_perf[asset]['wins'] += 1
            else:
                asset_perf[asset]['losses'] += 1
        
        # Remove underperforming assets
        good_assets = []
        for asset, stats in asset_perf.items():
            total = stats['wins'] + stats['losses']
            if total >= 5:
                wr = stats['wins'] / total
                if wr >= 0.55 and stats['pnl'] > 0:
                    good_assets.append(asset)
        
        if good_assets:
            self.config['assets'] = list(set(good_assets))
        
        # Analyze indicator accuracy
        for trade in trades[-50:]:  # Last 50 trades
            indicators = trade.get('indicators', {})
            result = trade['result']
            
            # RSI contribution
            rsi = float(indicators.get('rsi', 50))
            if result == 'WIN':
                if (rsi < 40 and trade['direction'] == 'CALL') or (rsi > 60 and trade['direction'] == 'PUT'):
                    self.config['indicator_accuracy']['rsi'] = min(1.0, self.config['indicator_accuracy']['rsi'] + 0.02)
            else:
                self.config['indicator_accuracy']['rsi'] = max(0.1, self.config['indicator_accuracy']['rsi'] - 0.01)
        
        # Adaptive confidence adjustment
        recent_wr = sum(1 for t in trades[-20:] if t['result'] == 'WIN') / min(20, len(trades))
        
        if recent_wr > 0.75:
            # Doing well, can be slightly less strict
            self.config['confidence_adjustment'] = max(-5, self.config['confidence_adjustment'] - 1)
        elif recent_wr < 0.55:
            # Doing poorly, be more strict
            self.config['confidence_adjustment'] = min(10, self.config['confidence_adjustment'] + 2)
        
        self.config['total_trades_analyzed'] = len(trades)
        self.save()
        
        logger.info(f"🧠 Learning update: Skip hours={self.config['skip_hours']}, Best hours={self.config['best_hours']}")
        logger.info(f"🧠 Assets: {self.config['assets']}, Confidence adj: {self.config['confidence_adjustment']}")
    
    def get_min_confidence(self) -> int:
        """Get adaptive minimum confidence"""
        base = self.config['min_confidence']
        adj = self.config['confidence_adjustment']
        return max(80, min(95, base + adj))


class TelegramReporter:
    """Send trading reports to Telegram"""
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID', '')
        self.enabled = bool(self.bot_token and self.chat_id)
        
    def send_message(self, text: str) -> bool:
        if not self.enabled:
            return False
        try:
            import urllib.request
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = json.dumps({
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            urllib.request.urlopen(req, timeout=10)
            return True
        except Exception as e:
            logger.warning(f"Telegram send failed: {e}")
            return False
    
    def send_trade(self, direction: str, asset: str, amount: float, 
                   confidence: float, result: str = None):
        if result:
            emoji = "✅" if result == "WIN" else "❌"
            text = f"{emoji} <b>{result}</b>\n{direction} {asset}\n${amount:.2f} @ {confidence:.0f}%"
        else:
            text = f"🎯 <b>{direction}</b> {asset}\n${amount:.2f} @ {confidence:.0f}%"
        self.send_message(text)
    
    def send_hourly_report(self, stats: Dict, session: str, learning: Dict = None):
        wr = stats['win_rate']
        wr_emoji = "🟢" if wr >= 70 else "🟡" if wr >= 55 else "🔴"
        
        text = f"📊 <b>V8 BOT - Hourly Report</b>\n\n"
        text += f"{wr_emoji} Win Rate: <b>{wr:.1f}%</b>\n"
        text += f"📈 Trades: {stats['total']} (W:{stats['wins']} L:{stats['losses']})\n"
        text += f"💰 Balance: ${stats['balance']:.2f}\n"
        text += f"💵 P&L: ${stats['pnl']:.2f}\n"
        
        if learning:
            text += f"\n🧠 <b>Learning:</b>\n"
            text += f"Min Conf: {learning.get('min_confidence', 85)}%\n"
            text += f"Assets: {len(learning.get('assets', []))}\n"
        
        text += f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        self.send_message(text)


class MarketSessionDetector:
    """Detect market sessions"""

    @staticmethod
    def get_market_session() -> Dict:
        utc_now = datetime.now(pytz.UTC)
        hour = utc_now.hour

        tokyo_open = 0 <= hour < 9
        london_open = 7 <= hour < 16
        ny_open = 13 <= hour < 22

        if tokyo_open and london_open:
            session, quality = "tokyo_london_overlap", "high"
        elif london_open and ny_open:
            session, quality = "london_ny_overlap", "very_high"
        elif tokyo_open:
            session, quality = "tokyo", "medium"
        elif london_open:
            session, quality = "london", "high"
        elif ny_open:
            session, quality = "new_york", "high"
        else:
            session, quality = "quiet", "low"

        return {
            'session': session,
            'quality': quality,
            'hour': hour,
            'is_weekend': utc_now.weekday() >= 5,
            'is_overlap': 'overlap' in session
        }


class TechnicalAnalyzer:
    """Technical analysis with proper calculations"""
    
    def ema(self, data: List[float], period: int) -> float:
        if len(data) < period:
            return data[-1] if data else 0
        k = 2 / (period + 1)
        ema_val = data[0]
        for price in data[1:]:
            ema_val = price * k + ema_val * (1 - k)
        return ema_val

    def sma(self, data: List[float], period: int) -> float:
        if len(data) < period:
            return sum(data) / len(data) if data else 0
        return sum(data[-period:]) / period

    def rsi(self, prices: List[float], period: int = 14) -> float:
        if len(prices) < period + 1:
            return 50.0

        gains, losses = [], []
        for i in range(1, len(prices)):
            change = prices[i] - prices[i - 1]
            gains.append(change if change > 0 else 0)
            losses.append(abs(change) if change < 0 else 0)

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100.0
        return 100 - (100 / (1 + avg_gain / avg_loss))

    def macd(self, prices: List[float]) -> Tuple[float, float, float]:
        if len(prices) < 26:
            return 0.0, 0.0, 0.0

        ema_12 = self.ema(prices, 12)
        ema_26 = self.ema(prices, 26)
        macd_line = ema_12 - ema_26

        macd_history = []
        for i in range(26, len(prices)):
            e12 = self.ema(prices[:i+1], 12)
            e26 = self.ema(prices[:i+1], 26)
            macd_history.append(e12 - e26)

        signal_line = self.ema(macd_history, 9) if len(macd_history) >= 9 else 0
        return macd_line, signal_line, macd_line - signal_line

    def bollinger(self, prices: List[float], period: int = 20) -> Tuple[float, float, float, float]:
        if len(prices) < period:
            current = prices[-1] if prices else 0
            return current, current, current, 0

        sma_val = self.sma(prices, period)
        variance = sum((p - sma_val) ** 2 for p in prices[-period:]) / period
        std = math.sqrt(variance)

        return sma_val + (2 * std), sma_val, sma_val - (2 * std), (2 * std) / sma_val * 100 if sma_val > 0 else 0

    def stochastic(self, prices: List[float], k_period: int = 14) -> Tuple[float, float]:
        if len(prices) < k_period:
            return 50.0, 50.0

        high_max = max(prices[-k_period:])
        low_min = min(prices[-k_period:])
        
        if high_max == low_min:
            return 50.0, 50.0

        k = ((prices[-1] - low_min) / (high_max - low_min)) * 100
        
        k_values = []
        for i in range(k_period, len(prices) + 1):
            h = max(prices[i-k_period:i])
            l = min(prices[i-k_period:i])
            if h != l:
                k_values.append(((prices[i-1] - l) / (h - l)) * 100)
            else:
                k_values.append(50)
        
        return k, self.sma(k_values[-3:], 3) if len(k_values) >= 3 else 50

    def trend(self, prices: List[float]) -> Tuple[str, str]:
        if len(prices) < 30:
            return "ranging", "weak"

        sma_10 = self.sma(prices[-10:], 10)
        sma_20 = self.sma(prices[-20:], 20)
        sma_30 = self.sma(prices[-30:], 30)

        if sma_10 > sma_20 > sma_30:
            return "uptrend", "strong"
        elif sma_10 > sma_20:
            return "uptrend", "moderate"
        elif sma_10 < sma_20 < sma_30:
            return "downtrend", "strong"
        elif sma_10 < sma_20:
            return "downtrend", "moderate"
        return "ranging", "weak"

    def candlestick_pattern(self, opens: List[float], highs: List[float], 
                           lows: List[float], closes: List[float]) -> Dict:
        if len(closes) < 3:
            return {'pattern': None, 'signal': None, 'strength': 0}

        o3, c3 = opens[-1], closes[-1]
        upper_wick = highs[-1] - max(o3, c3)
        lower_wick = min(o3, c3) - lows[-1]
        body = abs(c3 - o3)

        patterns = []

        # Pinbar
        if lower_wick > body * 2 and lower_wick > upper_wick * 2:
            patterns.append(('pinbar_bullish', 'CALL', 15))
        elif upper_wick > body * 2 and upper_wick > lower_wick * 2:
            patterns.append(('pinbar_bearish', 'PUT', 15))

        # Engulfing
        o2, c2 = opens[-2], closes[-2]
        if c2 < o2 and c3 > o3 and c3 > o2 and o3 < c2:
            patterns.append(('bullish_engulfing', 'CALL', 20))
        elif c2 > o2 and c3 < o3 and c3 < o2 and o3 > c2:
            patterns.append(('bearish_engulfing', 'PUT', 20))

        # Three soldiers/crows
        o1, c1 = opens[-3], closes[-3]
        if c1 > o1 and c2 > opens[-2] and c3 > o3:
            if c2 > c1 and c3 > c2:
                patterns.append(('three_white_soldiers', 'CALL', 25))
        elif c1 < o1 and closes[-2] < opens[-2] and c3 < o3:
            if c2 < c1 and c3 < c2:
                patterns.append(('three_black_crows', 'PUT', 25))

        if not patterns:
            return {'pattern': None, 'signal': None, 'strength': 0}

        best = max(patterns, key=lambda x: x[2])
        return {'pattern': best[0], 'signal': best[1], 'strength': best[2]}


class V8Strategy:
    """V8 Strategy with strict requirements"""

    def __init__(self, analyzer: TechnicalAnalyzer, config: SelfLearningConfig):
        self.analyzer = analyzer
        self.config = config

    def generate_signal(self, candles_1m: List[Dict], candles_5m: List[Dict]) -> Optional[Dict]:
        if len(candles_1m) < 50 or len(candles_5m) < 20:
            return None

        close_1m = [c['close'] for c in candles_1m]
        close_5m = [c['close'] for c in candles_5m]
        open_1m = [c['open'] for c in candles_1m]
        high_1m = [c['max'] for c in candles_1m]
        low_1m = [c['min'] for c in candles_1m]

        current_price = close_1m[-1]
        min_confidence = self.config.get_min_confidence()
        min_indicators = self.config.config['min_indicators']

        # Trend analysis FIRST
        trend_5m, strength_5m = self.analyzer.trend(close_5m)
        trend_1m, strength_1m = self.analyzer.trend(close_1m)

        if trend_5m == "ranging" and trend_1m == "ranging":
            return None

        main_trend = trend_5m if trend_5m != "ranging" else trend_1m

        # Indicator analysis
        indicators = {}
        call_signals, put_signals, confidence = 0, 0, 0

        # RSI
        rsi = self.analyzer.rsi(close_1m)
        indicators['rsi'] = rsi
        
        if rsi < 30:
            call_signals += 1
            confidence += 20
        elif rsi < 40:
            call_signals += 1
            confidence += 10
        elif rsi > 70:
            put_signals += 1
            confidence += 20
        elif rsi > 60:
            put_signals += 1
            confidence += 10

        # MACD
        macd_line, signal_line, histogram = self.analyzer.macd(close_1m)
        indicators['macd'] = macd_line
        indicators['macd_histogram'] = histogram

        if macd_line > signal_line and histogram > 0:
            call_signals += 1
            confidence += 15
        elif macd_line < signal_line and histogram < 0:
            put_signals += 1
            confidence += 15

        # Bollinger
        bb_upper, bb_middle, bb_lower, _ = self.analyzer.bollinger(close_1m)
        bb_pos = (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5
        indicators['bb_position'] = bb_pos

        if bb_pos < 0.15:
            call_signals += 1
            confidence += 15
        elif bb_pos > 0.85:
            put_signals += 1
            confidence += 15

        # Stochastic
        stoch_k, stoch_d = self.analyzer.stochastic(close_1m)
        indicators['stoch_k'] = stoch_k

        if stoch_k < 20 and stoch_d < 20:
            call_signals += 1
            confidence += 15
        elif stoch_k > 80 and stoch_d > 80:
            put_signals += 1
            confidence += 15

        # Trend (MANDATORY)
        indicators['trend_5m'] = trend_5m
        indicators['trend_1m'] = trend_1m

        if 'uptrend' in main_trend:
            call_signals += 1
            confidence += 25
        elif 'downtrend' in main_trend:
            put_signals += 1
            confidence += 25

        # Pattern
        pattern = self.analyzer.candlestick_pattern(open_1m, high_1m, low_1m, close_1m)
        indicators['candle_pattern'] = pattern

        if pattern['signal'] == 'CALL':
            call_signals += 1
            confidence += pattern['strength']
        elif pattern['signal'] == 'PUT':
            put_signals += 1
            confidence += pattern['strength']

        # Signal resolution
        max_signals = max(call_signals, put_signals)
        
        if max_signals < min_indicators:
            return None

        if call_signals > put_signals:
            direction = 'CALL'
            if 'downtrend' in main_trend:
                return None  # NO counter-trend
        elif put_signals > call_signals:
            direction = 'PUT'
            if 'uptrend' in main_trend:
                return None  # NO counter-trend
        else:
            return None

        confidence = min(100, (max_signals / 7) * 100)

        if confidence < min_confidence:
            return None

        return {
            'direction': direction,
            'confidence': confidence,
            'indicators': indicators,
            'trend_aligned': True
        }


class TradingMemory:
    """Track and persist trading performance"""

    def __init__(self, memory_file: str = 'trading_memory_v8.json'):
        self.memory_file = memory_file
        self.data = {
            'trades': [],
            'by_asset': defaultdict(lambda: {'wins': 0, 'losses': 0, 'pnl': 0}),
            'by_hour': defaultdict(lambda: {'wins': 0, 'losses': 0, 'pnl': 0}),
            'total_trades': 0,
            'total_wins': 0,
            'total_losses': 0,
            'total_pnl': 0,
            'consecutive_losses': 0
        }
        self.load()

    def load(self):
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    loaded = json.load(f)
                    for key in self.data:
                        if key in loaded:
                            if isinstance(self.data[key], defaultdict):
                                self.data[key] = defaultdict(lambda: {'wins': 0, 'losses': 0, 'pnl': 0}, loaded[key])
                            else:
                                self.data[key] = loaded[key]
                logger.info(f"📊 Loaded memory: {self.data['total_trades']} trades, {self.get_win_rate():.1f}% WR")
        except Exception as e:
            logger.warning(f"Memory load error: {e}")

    def save(self):
        try:
            to_save = {k: dict(v) if isinstance(v, defaultdict) else v for k, v in self.data.items()}
            with open(self.memory_file, 'w') as f:
                json.dump(to_save, f, indent=2)
        except Exception as e:
            logger.warning(f"Memory save error: {e}")

    def record_trade(self, asset: str, direction: str, session: str, hour: int,
                     confidence: float, result: str, pnl: float, indicators: Dict):
        self.data['total_trades'] += 1
        self.data['total_pnl'] += pnl

        if result == 'WIN':
            self.data['total_wins'] += 1
            self.data['consecutive_losses'] = 0
            self.data['by_asset'][asset]['wins'] += 1
            self.data['by_hour'][str(hour)]['wins'] += 1
        else:
            self.data['total_losses'] += 1
            self.data['consecutive_losses'] += 1
            self.data['by_asset'][asset]['losses'] += 1
            self.data['by_hour'][str(hour)]['losses'] += 1

        self.data['by_asset'][asset]['pnl'] += pnl
        self.data['by_hour'][str(hour)]['pnl'] += pnl

        self.data['trades'].append({
            'time': datetime.now().isoformat(),
            'asset': asset,
            'direction': direction,
            'session': session,
            'hour': hour,
            'confidence': confidence,
            'result': result,
            'pnl': pnl,
            'indicators': {k: str(v) for k, v in indicators.items()}
        })

        if self.data['total_trades'] % 5 == 0:
            self.save()

    def get_win_rate(self) -> float:
        if self.data['total_trades'] == 0:
            return 0.0
        return (self.data['total_wins'] / self.data['total_trades']) * 100

    def get_stats(self, balance: float) -> Dict:
        return {
            'total': self.data['total_trades'],
            'wins': self.data['total_wins'],
            'losses': self.data['total_losses'],
            'win_rate': self.get_win_rate(),
            'pnl': self.data['total_pnl'],
            'balance': balance,
            'consecutive_losses': self.data['consecutive_losses']
        }


class V8Bot:
    """V8 Trading Bot with Self-Learning"""

    def __init__(self):
        self.email = os.getenv('IQOPTION_EMAIL', '')
        self.password = os.getenv('IQOPTION_PASSWORD', '')

        self.api = IQ_Option(self.email, self.password)
        self.learning = SelfLearningConfig()
        self.analyzer = TechnicalAnalyzer()
        self.strategy = V8Strategy(self.analyzer, self.learning)
        self.memory = TradingMemory()
        self.telegram = TelegramReporter()

        self.base_amount = self.learning.config['base_amount']
        self.max_trades_hour = 10
        self.trades_this_hour = 0
        self.last_hour = datetime.now().hour
        self.running = True
        self.connected = False
        self.balance = 0

        self.pause_until = None
        self.last_report_time = datetime.now()
        self.report_interval = 3600  # 1 hour

    def connect(self) -> bool:
        for attempt in range(3):
            logger.info(f"🔌 Connecting... (attempt {attempt + 1}/3)")
            
            try:
                result = self.api.connect()
                
                if result and result[0]:
                    try:
                        self.api.change_balance('PRACTICE')
                    except:
                        pass
                    
                    self.balance = self.api.get_balance()
                    self.connected = True
                    logger.info(f"✅ Connected! Balance: ${self.balance:.2f}")
                    return True
                    
            except Exception as e:
                logger.warning(f"⚠️ Connection error: {e}")
            
            time.sleep(2)

        logger.error("❌ Failed to connect")
        return False

    def get_candles(self, asset: str, timeframe: int = 60, count: int = 100) -> List[Dict]:
        try:
            candles = self.api.get_candles(asset, timeframe, count, time.time())
            return candles if candles else []
        except Exception as e:
            logger.error(f"Candle fetch error: {e}")
            return []

    def should_trade_hour(self, hour: int) -> Tuple[bool, str]:
        if self.pause_until and datetime.now() < self.pause_until:
            remaining = (self.pause_until - datetime.now()).seconds // 60
            return False, f"PAUSED ({remaining}m remaining)"

        if hour in self.learning.config['skip_hours']:
            return False, f"SKIPPED HOUR {hour} (low WR)"

        return True, "GOOD HOUR" if hour in self.learning.config['best_hours'] else "OK"

    def execute_trade(self, signal: Dict, asset: str) -> Optional[int]:
        try:
            amount = self.base_amount
            direction = signal['direction']
            
            success, trade_id = self.api.buy(amount, asset, direction, 1)
            
            if success:
                logger.info(f"✅ Trade #{trade_id}: {direction} {asset} ${amount:.2f} @ {signal['confidence']:.0f}%")
                self.telegram.send_trade(direction, asset, amount, signal['confidence'])
                return trade_id
            else:
                logger.warning(f"❌ Trade execution failed")
                return None
        except Exception as e:
            logger.error(f"❌ Trade error: {e}")
            return None

    def check_result(self, trade_id: int) -> Tuple[Optional[str], float]:
        try:
            result = self.api.check_win_v3(trade_id)
            if result > 0:
                logger.info(f"✅ WIN: +${result:.2f}")
                return 'WIN', result
            else:
                logger.info(f"❌ LOSS: ${result:.2f}")
                return 'LOSS', result
        except Exception as e:
            logger.error(f"❌ Result check error: {e}")
            return None, 0

    def handle_loss_recovery(self):
        if self.memory.data['consecutive_losses'] >= self.learning.config['max_consecutive_losses']:
            pause_min = self.learning.config['pause_minutes']
            self.pause_until = datetime.now() + timedelta(minutes=pause_min)
            logger.warning(f"⏸️ Pausing {pause_min}m after {self.memory.data['consecutive_losses']} losses")
            self.telegram.send_message(
                f"⏸️ <b>LOSS RECOVERY</b>\nPausing {pause_min} minutes after consecutive losses"
            )

    def send_hourly_report(self):
        stats = self.memory.get_stats(self.balance)
        session = MarketSessionDetector.get_market_session()['session']
        learning_info = {
            'min_confidence': self.learning.get_min_confidence(),
            'assets': self.learning.config['assets']
        }
        self.telegram.send_hourly_report(stats, session, learning_info)
        self.last_report_time = datetime.now()

    def run(self):
        logger.info("🚀 Starting V8 Bot with Self-Learning...")
        logger.info(f"🎯 Target: 90%+ WR | Min Confidence: {self.learning.get_min_confidence()}%")
        logger.info(f"📊 Best Hours: {self.learning.config['best_hours']}")
        logger.info(f"🚫 Skip Hours: {self.learning.config['skip_hours']}")
        logger.info(f"💰 Assets: {self.learning.config['assets']}")

        while self.running:
            try:
                current_hour = datetime.now().hour
                
                if current_hour != self.last_hour:
                    self.trades_this_hour = 0
                    self.last_hour = current_hour
                    self.balance = self.api.get_balance()
                    
                    # Hourly report
                    if (datetime.now() - self.last_report_time).total_seconds() >= self.report_interval:
                        self.send_hourly_report()
                    
                    # Self-learning update every 10 trades
                    if self.memory.data['total_trades'] > 0 and self.memory.data['total_trades'] % 10 == 0:
                        self.learning.update_from_trades(self.memory.data['trades'])
                    
                    wr = self.memory.get_win_rate()
                    logger.info(f"🕐 Hour {current_hour:02d} | Balance: ${self.balance:.2f} | WR: {wr:.1f}%")

                session_info = MarketSessionDetector.get_market_session()
                
                if session_info['is_weekend']:
                    session_info['session'] = 'quiet'
                    logger.info("🌙 Weekend - trading OTC")

                if self.trades_this_hour >= self.max_trades_hour:
                    time.sleep(60)
                    continue

                should_trade, reason = self.should_trade_hour(current_hour)
                if not should_trade:
                    logger.info(f"⏭️ {reason}")
                    time.sleep(60)
                    continue

                for asset in self.learning.config['assets']:
                    try:
                        candles_1m = self.get_candles(asset, 60, 100)
                        candles_5m = self.get_candles(asset, 300, 50)

                        if len(candles_1m) < 50 or len(candles_5m) < 20:
                            continue

                        signal = self.strategy.generate_signal(candles_1m, candles_5m)

                        if signal and signal['confidence'] >= self.learning.get_min_confidence():
                            trade_id = self.execute_trade(signal, asset)

                            if trade_id:
                                self.trades_this_hour += 1
                                time.sleep(62)

                                result, pnl = self.check_result(trade_id)

                                if result:
                                    self.memory.record_trade(
                                        asset=asset,
                                        direction=signal['direction'],
                                        session=session_info['session'],
                                        hour=current_hour,
                                        confidence=signal['confidence'],
                                        result=result,
                                        pnl=pnl if result == 'WIN' else -self.base_amount,
                                        indicators=signal['indicators']
                                    )

                                    if result == 'LOSS':
                                        self.handle_loss_recovery()

                                    wr = self.memory.get_win_rate()
                                    logger.info(f"📊 Win Rate: {wr:.1f}% | Trades: {self.memory.data['total_trades']}")

                                time.sleep(5)
                                break

                    except Exception as e:
                        logger.error(f"Asset error: {e}")
                        continue

                time.sleep(15)

            except KeyboardInterrupt:
                logger.info("⏹️ Stopping...")
                self.running = False
            except Exception as e:
                logger.error(f"❌ Main loop error: {e}")
                time.sleep(30)

        self.memory.save()
        self.learning.save()
        self.send_hourly_report()
        logger.info("👋 Bot stopped")


def main():
    logger.info("=" * 60)
    logger.info("🚀 IQ OPTION V8 BOT - SELF-LEARNING")
    logger.info("🎯 Target: 90%+ Win Rate")
    logger.info("🧠 Features: Adaptive parameters, Hour filtering, Asset optimization")
    logger.info("=" * 60)

    bot = V8Bot()

    def signal_handler(signum, frame):
        bot.running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if bot.connect():
        bot.run()
    else:
        logger.error("❌ Failed to connect")
        sys.exit(1)


if __name__ == "__main__":
    main()
