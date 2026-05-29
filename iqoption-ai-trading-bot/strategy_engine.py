"""
Strategy Engine - Implements trading strategies
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class StrategyEngine:
    """Implements various trading strategies"""

    def __init__(self, config):
        """
        Initialize strategy engine

        Args:
            config: Configuration object
        """
        self.config = config
        self.active_strategies = config.trading.active_strategies
        self.indicators_config = config.indicators

        logger.info(f"Strategy Engine initialized with strategies: {self.active_strategies}")

    def evaluate_strategies(self, indicators: Dict, llm_analysis: Optional[Dict]) -> Dict:
        """
        Evaluate all active strategies

        Args:
            indicators: Technical indicators
            llm_analysis: LLM analysis (if available)

        Returns:
            Combined strategy signals
        """
        signals = {}

        for strategy in self.active_strategies:
            try:
                if strategy == "rsi":
                    signals["rsi"] = self._rsi_strategy(indicators)
                elif strategy == "macd":
                    signals["macd"] = self._macd_strategy(indicators)
                elif strategy == "bollinger":
                    signals["bollinger"] = self._bollinger_strategy(indicators)
                elif strategy == "llm" and llm_analysis:
                    signals["llm"] = self._llm_strategy(llm_analysis)

            except Exception as e:
                logger.error(f"Error evaluating {strategy} strategy: {e}")
                signals[strategy] = {"signal": 0, "action": "HOLD"}

        # Combine signals
        combined = self._combine_signals(signals)

        logger.debug(f"Strategy signals: {signals}")
        logger.info(f"Combined signal: {combined.get('action')} (strength: {combined.get('strength', 0):.2f})")

        return combined

    def _rsi_strategy(self, indicators: Dict) -> Dict:
        """
        RSI-based trading strategy

        Args:
            indicators: Technical indicators

        Returns:
            Trading signal
        """
        try:
            if 'rsi' not in indicators or len(indicators['rsi']) == 0:
                return {"signal": 0, "action": "HOLD", "reasoning": "No RSI data"}

            rsi = indicators['rsi'].iloc[-1]
            overbought = self.indicators_config.rsi_overbought
            oversold = self.indicators_config.rsi_oversold

            if rsi < oversold:
                # Oversold - Buy signal
                strength = (oversold - rsi) / oversold
                return {
                    "signal": min(strength, 1.0),
                    "action": "CALL",
                    "reasoning": f"RSI oversold ({rsi:.2f} < {oversold})"
                }
            elif rsi > overbought:
                # Overbought - Sell signal
                strength = (rsi - overbought) / (100 - overbought)
                return {
                    "signal": -min(strength, 1.0),
                    "action": "PUT",
                    "reasoning": f"RSI overbought ({rsi:.2f} > {overbought})"
                }
            else:
                # Neutral
                return {
                    "signal": 0,
                    "action": "HOLD",
                    "reasoning": f"RSI neutral ({rsi:.2f})"
                }

        except Exception as e:
            logger.error(f"Error in RSI strategy: {e}")
            return {"signal": 0, "action": "HOLD", "reasoning": "Error"}

    def _macd_strategy(self, indicators: Dict) -> Dict:
        """
        MACD-based trading strategy

        Args:
            indicators: Technical indicators

        Returns:
            Trading signal
        """
        try:
            if 'macd_histogram' not in indicators or len(indicators['macd_histogram']) < 2:
                return {"signal": 0, "action": "HOLD", "reasoning": "No MACD data"}

            histogram = indicators['macd_histogram']
            current = histogram.iloc[-1]
            previous = histogram.iloc[-2]

            # MACD crossover
            if current > 0 and previous <= 0:
                # Bullish crossover
                return {
                    "signal": 0.7,
                    "action": "CALL",
                    "reasoning": "MACD bullish crossover"
                }
            elif current < 0 and previous >= 0:
                # Bearish crossover
                return {
                    "signal": -0.7,
                    "action": "PUT",
                    "reasoning": "MACD bearish crossover"
                }
            elif current > 0 and current > previous:
                # Momentum strengthening
                return {
                    "signal": 0.5,
                    "action": "CALL",
                    "reasoning": "MACD momentum bullish"
                }
            elif current < 0 and current < previous:
                # Momentum weakening
                return {
                    "signal": -0.5,
                    "action": "PUT",
                    "reasoning": "MACD momentum bearish"
                }
            else:
                return {
                    "signal": 0,
                    "action": "HOLD",
                    "reasoning": "MACD neutral"
                }

        except Exception as e:
            logger.error(f"Error in MACD strategy: {e}")
            return {"signal": 0, "action": "HOLD", "reasoning": "Error"}

    def _bollinger_strategy(self, indicators: Dict) -> Dict:
        """
        Bollinger Bands-based trading strategy

        Args:
            indicators: Technical indicators

        Returns:
            Trading signal
        """
        try:
            if 'bb_upper' not in indicators or 'bb_lower' not in indicators or 'current_price' not in indicators:
                return {"signal": 0, "action": "HOLD", "reasoning": "No Bollinger data"}

            price = indicators['current_price']
            bb_upper = indicators['bb_upper'].iloc[-1]
            bb_lower = indicators['bb_lower'].iloc[-1]

            # Calculate position within bands
            band_width = bb_upper - bb_lower
            position = (price - bb_lower) / band_width if band_width > 0 else 0.5

            if position < 0.2:
                # Near lower band - Buy signal
                strength = (0.2 - position) / 0.2
                return {
                    "signal": min(strength, 0.8),
                    "action": "CALL",
                    "reasoning": f"Price near lower BB ({position:.2f})"
                }
            elif position > 0.8:
                # Near upper band - Sell signal
                strength = (position - 0.8) / 0.2
                return {
                    "signal": -min(strength, 0.8),
                    "action": "PUT",
                    "reasoning": f"Price near upper BB ({position:.2f})"
                }
            else:
                return {
                    "signal": 0,
                    "action": "HOLD",
                    "reasoning": f"Price within BB range ({position:.2f})"
                }

        except Exception as e:
            logger.error(f"Error in Bollinger strategy: {e}")
            return {"signal": 0, "action": "HOLD", "reasoning": "Error"}

    def _llm_strategy(self, llm_analysis: Dict) -> Dict:
        """
        LLM-based trading strategy

        Args:
            llm_analysis: LLM market analysis

        Returns:
            Trading signal
        """
        try:
            if not llm_analysis:
                return {"signal": 0, "action": "HOLD", "reasoning": "No LLM analysis"}

            recommendation = llm_analysis.get('recommendation', 'HOLD')
            confidence = llm_analysis.get('confidence', 0)
            signal = llm_analysis.get('signal', 0)
            reasoning = llm_analysis.get('reasoning', '')

            return {
                "signal": signal,
                "action": recommendation,
                "reasoning": f"LLM: {reasoning}",
                "confidence": confidence,
                "risk": llm_analysis.get('risk', 'MEDIUM')
            }

        except Exception as e:
            logger.error(f"Error in LLM strategy: {e}")
            return {"signal": 0, "action": "HOLD", "reasoning": "Error"}

    def _combine_signals(self, signals: Dict) -> Dict:
        """
        Combine signals from all strategies

        Args:
            signals: Dictionary of strategy signals

        Returns:
            Combined signal
        """
        if not signals:
            return {"signal": 0, "action": "HOLD", "strength": 0}

        # Calculate weighted average signal
        total_weight = 0
        weighted_signal = 0
        reasons = []
        confidence_scores = []

        for strategy, signal_data in signals.items():
            signal = signal_data.get('signal', 0)
            confidence = signal_data.get('confidence', 0)

            # Weight: LLM gets higher weight if available
            if strategy == 'llm' and confidence > 50:
                weight = 2.0
            else:
                weight = 1.0

            if confidence > 0:
                confidence_scores.append(confidence)

            weighted_signal += signal * weight
            total_weight += weight

            reasons.append(f"{strategy.upper()}: {signal_data.get('reasoning', '')}")

        # Calculate combined signal
        if total_weight > 0:
            combined_signal = weighted_signal / total_weight
        else:
            combined_signal = 0

        # Determine action
        threshold = 0.3  # Minimum signal strength to trade

        if combined_signal > threshold:
            action = "CALL"
        elif combined_signal < -threshold:
            action = "PUT"
        else:
            action = "HOLD"

        # Calculate strength (0-1)
        strength = abs(combined_signal)

        # Calculate average confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

        return {
            "signal": combined_signal,
            "action": action,
            "strength": strength,
            "confidence": avg_confidence,
            "reasoning": " | ".join(reasons),
            "individual_signals": signals
        }

    def should_trade(self, combined_signal: Dict, config) -> bool:
        """
        Determine if we should execute a trade

        Args:
            combined_signal: Combined strategy signal
            config: Configuration

        Returns:
            True if we should trade
        """
        action = combined_signal.get('action', 'HOLD')

        if action == 'HOLD':
            return False

        # Check signal strength
        if combined_signal.get('strength', 0) < 0.4:
            logger.debug("Signal strength too low")
            return False

        # Check confidence
        if combined_signal.get('confidence', 0) < 55:
            logger.debug("Confidence too low")
            return False

        # Check min win rate requirement
        # (This would be checked against historical performance)
        # For now, we'll trust the confidence

        return True