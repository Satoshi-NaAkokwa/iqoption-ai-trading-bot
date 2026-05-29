"""
Technical Analysis Indicators
Calculates various technical indicators for trading analysis
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """Technical analysis indicators"""

    def __init__(self, config):
        """
        Initialize technical analyzer

        Args:
            config: Configuration object
        """
        self.config = config
        self.indicators_config = config.indicators

    def candles_to_dataframe(self, candles: List[Dict]) -> pd.DataFrame:
        """
        Convert candle data to pandas DataFrame

        Args:
            candles: List of candle dictionaries

        Returns:
            DataFrame with OHLC data
        """
        if not candles:
            return pd.DataFrame()

        data = []
        for candle in candles:
            data.append({
                'timestamp': candle.get('from'),
                'open': candle.get('open'),
                'high': candle.get('max'),
                'low': candle.get('min'),
                'close': candle.get('close'),
                'volume': candle.get('volume', 0)
            })

        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('timestamp', inplace=True)

        return df

    def calculate_rsi(self, df: pd.DataFrame, period: Optional[int] = None) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)

        Args:
            df: DataFrame with OHLC data
            period: RSI period

        Returns:
            Series with RSI values
        """
        if df.empty:
            return pd.Series()

        period = period or self.indicators_config.rsi_period

        try:
            # Calculate price changes
            delta = df['close'].diff()

            # Separate gains and losses
            gains = delta.where(delta > 0, 0)
            losses = -delta.where(delta < 0, 0)

            # Calculate average gains and losses
            avg_gains = gains.rolling(window=period).mean()
            avg_losses = losses.rolling(window=period).mean()

            # Calculate RS and RSI
            rs = avg_gains / avg_losses
            rsi = 100 - (100 / (1 + rs))

            return rsi

        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return pd.Series()

    def calculate_macd(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Calculate Moving Average Convergence Divergence (MACD)

        Args:
            df: DataFrame with OHLC data

        Returns:
            Dictionary with MACD, signal, and histogram
        """
        if df.empty:
            return {}

        try:
            fast = self.indicators_config.macd_fast
            slow = self.indicators_config.macd_slow
            signal = self.indicators_config.macd_signal

            # Calculate EMAs
            ema_fast = df['close'].ewm(span=fast).mean()
            ema_slow = df['close'].ewm(span=slow).mean()

            # Calculate MACD line
            macd_line = ema_fast - ema_slow

            # Calculate signal line
            signal_line = macd_line.ewm(span=signal).mean()

            # Calculate histogram
            histogram = macd_line - signal_line

            return {
                'macd': macd_line,
                'signal': signal_line,
                'histogram': histogram
            }

        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return {}

    def calculate_bollinger_bands(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands

        Args:
            df: DataFrame with OHLC data

        Returns:
            Dictionary with upper, middle, and lower bands
        """
        if df.empty:
            return {}

        try:
            period = self.indicators_config.bollinger_period
            std = self.indicators_config.bollinger_std

            # Calculate middle band (SMA)
            middle = df['close'].rolling(window=period).mean()

            # Calculate standard deviation
            rolling_std = df['close'].rolling(window=period).std()

            # Calculate upper and lower bands
            upper = middle + (rolling_std * std)
            lower = middle - (rolling_std * std)

            return {
                'upper': upper,
                'middle': middle,
                'lower': lower
            }

        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return {}

    def calculate_ma(self, df: pd.DataFrame, period: int) -> pd.Series:
        """
        Calculate Simple Moving Average (SMA)

        Args:
            df: DataFrame with OHLC data
            period: MA period

        Returns:
            Series with MA values
        """
        if df.empty:
            return pd.Series()

        try:
            return df['close'].rolling(window=period).mean()
        except Exception as e:
            logger.error(f"Error calculating MA: {e}")
            return pd.Series()

    def calculate_ema(self, df: pd.DataFrame, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average (EMA)

        Args:
            df: DataFrame with OHLC data
            period: EMA period

        Returns:
            Series with EMA values
        """
        if df.empty:
            return pd.Series()

        try:
            return df['close'].ewm(span=period).mean()
        except Exception as e:
            logger.error(f"Error calculating EMA: {e}")
            return pd.Series()

    def calculate_all_indicators(self, candles: List[Dict]) -> Dict:
        """
        Calculate all technical indicators

        Args:
            candles: List of candle data

        Returns:
            Dictionary with all indicators
        """
        df = self.candles_to_dataframe(candles)

        if df.empty:
            logger.warning("No data for indicator calculation")
            return {}

        try:
            indicators = {}

            # RSI
            indicators['rsi'] = self.calculate_rsi(df)

            # MACD
            macd_data = self.calculate_macd(df)
            indicators['macd'] = macd_data.get('macd')
            indicators['macd_signal'] = macd_data.get('signal')
            indicators['macd_histogram'] = macd_data.get('histogram')

            # Bollinger Bands
            bb_data = self.calculate_bollinger_bands(df)
            indicators['bb_upper'] = bb_data.get('upper')
            indicators['bb_middle'] = bb_data.get('middle')
            indicators['bb_lower'] = bb_data.get('lower')

            # Moving Averages
            indicators['ma_fast'] = self.calculate_ma(df, self.indicators_config.ma_fast)
            indicators['ma_slow'] = self.calculate_ma(df, self.indicators_config.ma_slow)

            # Current values
            if len(df) > 0:
                current_close = df['close'].iloc[-1]
                indicators['current_price'] = current_close
                indicators['price_change'] = df['close'].pct_change().iloc[-1] if len(df) > 1 else 0

            logger.debug(f"Calculated {len(indicators)} indicators")
            return indicators

        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return {}

    def get_signal_strength(self, indicators: Dict) -> Dict[str, float]:
        """
        Calculate signal strength from indicators

        Args:
            indicators: Dictionary of indicators

        Returns:
            Dictionary with signal strengths (-1 to 1)
        """
        signals = {}

        try:
            # RSI signal
            if 'rsi' in indicators and len(indicators['rsi']) > 0:
                rsi_current = indicators['rsi'].iloc[-1]
                if rsi_current < self.indicators_config.rsi_oversold:
                    signals['rsi'] = 0.8  # Strong buy
                elif rsi_current > self.indicators_config.rsi_overbought:
                    signals['rsi'] = -0.8  # Strong sell
                else:
                    signals['rsi'] = 0.0

            # MACD signal
            if 'macd_histogram' in indicators and len(indicators['macd_histogram']) > 1:
                macd_hist = indicators['macd_histogram'].iloc[-1]
                macd_hist_prev = indicators['macd_histogram'].iloc[-2]

                if macd_hist > 0 and macd_hist > macd_hist_prev:
                    signals['macd'] = 0.6  # Buy
                elif macd_hist < 0 and macd_hist < macd_hist_prev:
                    signals['macd'] = -0.6  # Sell
                else:
                    signals['macd'] = 0.0

            # Bollinger Bands signal
            if 'bb_upper' in indicators and 'bb_lower' in indicators and 'current_price' in indicators:
                price = indicators['current_price']
                bb_upper = indicators['bb_upper'].iloc[-1]
                bb_lower = indicators['bb_lower'].iloc[-1]

                bb_position = (price - bb_lower) / (bb_upper - bb_lower)

                if bb_position < 0.2:
                    signals['bollinger'] = 0.7  # Buy (near lower band)
                elif bb_position > 0.8:
                    signals['bollinger'] = -0.7  # Sell (near upper band)
                else:
                    signals['bollinger'] = 0.0

            # Moving Average signal
            if 'ma_fast' in indicators and 'ma_slow' in indicators:
                if len(indicators['ma_fast']) > 0 and len(indicators['ma_slow']) > 0:
                    ma_fast = indicators['ma_fast'].iloc[-1]
                    ma_slow = indicators['ma_slow'].iloc[-1]

                    if ma_fast > ma_slow:
                        signals['ma'] = 0.5  # Buy
                    elif ma_fast < ma_slow:
                        signals['ma'] = -0.5  # Sell
                    else:
                        signals['ma'] = 0.0

        except Exception as e:
            logger.error(f"Error calculating signal strength: {e}")

        return signals