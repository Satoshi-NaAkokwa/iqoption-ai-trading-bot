"""
LLM Analyst for Market Analysis
Uses LLM for intelligent market analysis and prediction
"""

import logging
from typing import Dict, Optional, List
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMAnalyst:
    """Uses LLM for market analysis and trading decisions"""

    def __init__(self, config):
        """
        Initialize LLM analyst

        Args:
            config: Configuration object
        """
        self.config = config
        self.llm_config = config.llm
        self.enabled = False

        # Check if LLM is available
        if self.llm_config.api_key:
            self.enabled = True
            logger.info(f"LLM Analyst enabled (provider: {self.llm_config.provider})")
        else:
            logger.warning("LLM Analyst disabled - no API key provided")

    def analyze_market(self, asset: str, indicators: Dict, price_data: Dict) -> Optional[Dict]:
        """
        Analyze market conditions using LLM

        Args:
            asset: Asset name
            indicators: Technical indicators
            price_data: Price and volume data

        Returns:
            Analysis result with recommendation
        """
        if not self.enabled:
            return None

        try:
            # Prepare market context
            market_context = self._prepare_market_context(asset, indicators, price_data)

            # Create analysis prompt
            prompt = self._create_analysis_prompt(market_context)

            # Get LLM response
            response = self._query_llm(prompt)

            if response:
                return self._parse_llm_response(response, market_context)

        except Exception as e:
            logger.error(f"Error in LLM market analysis: {e}")

        return None

    def _prepare_market_context(self, asset: str, indicators: Dict, price_data: Dict) -> Dict:
        """
        Prepare market context for LLM

        Args:
            asset: Asset name
            indicators: Technical indicators
            price_data: Price data

        Returns:
            Market context dictionary
        """
        context = {
            'asset': asset,
            'timestamp': datetime.now().isoformat(),
            'price': price_data.get('current_price', 0),
            'price_change': price_data.get('price_change', 0),
        }

        # Add indicators
        for key, value in indicators.items():
            if hasattr(value, 'iloc'):
                # It's a pandas Series, get last value
                context[key] = float(value.iloc[-1]) if len(value) > 0 else None
            elif isinstance(value, (int, float)):
                context[key] = value
            else:
                context[key] = str(value)[:100]  # Limit string length

        # Add key levels
        if 'bb_upper' in context and 'bb_lower' in context:
            context['bb_upper'] = context['bb_upper']
            context['bb_lower'] = context['bb_lower']

        return context

    def _create_analysis_prompt(self, context: Dict) -> str:
        """
        Create analysis prompt for LLM

        Args:
            context: Market context

        Returns:
            Analysis prompt
        """
        prompt = f"""You are an expert trading analyst specializing in binary options trading on IQ Option.

Current Market Data for {context['asset']}:
- Current Price: {context.get('price', 0)}
- Price Change: {context.get('price_change', 0):.4f}

Technical Indicators:
- RSI: {context.get('rsi', 0):.2f} (Overbought: 70, Oversold: 30)
- MACD Histogram: {context.get('macd_histogram', 0):.4f}
- Bollinger Upper: {context.get('bb_upper', 0):.4f}
- Bollinger Lower: {context.get('bb_lower', 0):.4f}
- Fast MA: {context.get('ma_fast', 0):.4f}
- Slow MA: {context.get('ma_slow', 0):.4f}

Please analyze this market situation and provide:
1. Market trend direction (BULLISH/BEARISH/NEUTRAL)
2. Confidence level (0-100)
3. Trade recommendation (CALL/PUT/HOLD)
4. Reasoning for your recommendation
5. Risk assessment (LOW/MEDIUM/HIGH)
6. Key support and resistance levels

Format your response as JSON:
{{
    "trend": "BULLISH|BEARISH|NEUTRAL",
    "confidence": 0-100,
    "recommendation": "CALL|PUT|HOLD",
    "reasoning": "Brief explanation",
    "risk": "LOW|MEDIUM|HIGH",
    "support": price_level,
    "resistance": price_level
}}

Provide only the JSON response, no additional text."""

        return prompt

    def _query_llm(self, prompt: str) -> Optional[str]:
        """
        Query LLM API

        Args:
            prompt: Prompt to send

        Returns:
            LLM response
        """
        try:
            if self.llm_config.provider == "openai":
                return self._query_openai(prompt)
            else:
                logger.warning(f"LLM provider {self.llm_config.provider} not implemented")
                return None

        except Exception as e:
            logger.error(f"Error querying LLM: {e}")
            return None

    def _query_openai(self, prompt: str) -> Optional[str]:
        """
        Query OpenAI API

        Args:
            prompt: Prompt to send

        Returns:
            OpenAI response
        """
        try:
            import openai

            client = openai.OpenAI(api_key=self.llm_config.api_key)

            response = client.chat.completions.create(
                model=self.llm_config.model,
                messages=[
                    {"role": "system", "content": "You are an expert trading analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.llm_config.temperature,
                max_tokens=self.llm_config.max_tokens
            )

            return response.choices[0].message.content

        except ImportError:
            logger.error("OpenAI library not installed. Run: pip install openai")
            return None
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None

    def _parse_llm_response(self, response: str, context: Dict) -> Optional[Dict]:
        """
        Parse LLM response

        Args:
            response: LLM response string
            context: Market context

        Returns:
            Parsed analysis result
        """
        try:
            # Try to parse JSON
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}')

            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx+1]
                analysis = json.loads(json_str)

                # Add context metadata
                analysis['timestamp'] = context['timestamp']
                analysis['asset'] = context['asset']

                # Convert confidence to signal strength
                if analysis.get('recommendation') == 'CALL':
                    analysis['signal'] = analysis.get('confidence', 50) / 100.0
                elif analysis.get('recommendation') == 'PUT':
                    analysis['signal'] = -analysis.get('confidence', 50) / 100.0
                else:
                    analysis['signal'] = 0.0

                logger.info(f"LLM Analysis: {analysis.get('trend')} - {analysis.get('recommendation')} (confidence: {analysis.get('confidence')})")
                return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing LLM JSON response: {e}")
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")

        return None

    def get_strategy_recommendation(self, market_analysis: Dict, timeframe: str) -> Optional[Dict]:
        """
        Get strategy recommendation based on LLM analysis

        Args:
            market_analysis: LLM market analysis
            timeframe: Trading timeframe

        Returns:
            Strategy recommendation
        """
        if not market_analysis:
            return None

        try:
            recommendation = {
                'action': market_analysis.get('recommendation', 'HOLD'),
                'confidence': market_analysis.get('confidence', 0),
                'signal': market_analysis.get('signal', 0),
                'reasoning': market_analysis.get('reasoning', ''),
                'risk': market_analysis.get('risk', 'MEDIUM'),
                'support': market_analysis.get('support'),
                'resistance': market_analysis.get('resistance'),
                'timeframe': timeframe,
                'source': 'LLM_ANALYST'
            }

            return recommendation

        except Exception as e:
            logger.error(f"Error creating strategy recommendation: {e}")
            return None

    def learn_from_video(self, video_transcript: str, strategy_name: str) -> bool:
        """
        Learn trading strategy from video transcript

        Args:
            video_transcript: Transcript of trading strategy video
            strategy_name: Name of the strategy

        Returns:
            True if successful
        """
        if not self.enabled:
            logger.warning("LLM Analyst disabled - cannot learn from video")
            return False

        try:
            prompt = f"""Analyze this trading strategy from a YouTube video transcript and extract key trading rules:

Strategy Name: {strategy_name}

Transcript:
{video_transcript[:5000]}

Extract and return in JSON format:
{{
    "strategy_name": "{strategy_name}",
    "entry_conditions": ["condition1", "condition2"],
    "exit_conditions": ["condition1", "condition2"],
    "indicators": ["RSI", "MACD", etc.],
    "timeframes": ["1M", "5M"],
    "risk_management": {{
        "stop_loss": "description",
        "take_profit": "description",
        "position_sizing": "description"
    }},
    "notes": "Additional notes"
}}"""

            response = self._query_llm(prompt)

            if response:
                # Save strategy to file
                strategy_file = f"strategies/{strategy_name.lower().replace(' ', '_')}.json"

                try:
                    with open(strategy_file, 'w') as f:
                        f.write(response)
                    logger.info(f"Saved strategy: {strategy_name} to {strategy_file}")
                    return True
                except Exception as e:
                    logger.error(f"Error saving strategy: {e}")

        except Exception as e:
            logger.error(f"Error learning from video: {e}")

        return False