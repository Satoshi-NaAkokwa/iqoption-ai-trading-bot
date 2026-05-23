"""
Configuration file for IQ Option AI Trading Bot
"""

import os
from dataclasses import dataclass
from typing import List

@dataclass
class IQOptionConfig:
    """IQ Option API configuration"""
    email: str
    password: str
    demo_mode: bool = True
    practice_mode: bool = True

@dataclass
class LLMConfig:
    """LLM API configuration"""
    provider: str = "openai"  # openai, anthropic, etc.
    api_key: str = ""
    model: str = "gpt-4"
    temperature: float = 0.3
    max_tokens: int = 1000

@dataclass
class TradingConfig:
    """Trading parameters"""
    timeframes: List[str] = None
    default_amount: float = 1.0
    max_concurrent_trades: int = 3
    daily_loss_limit: float = 10.0
    max_risk_per_trade: float = 0.02  # 2% of account balance
    risk_reward_ratio: float = 2.0
    min_win_rate: float = 0.55  # Minimum win rate to trade

    def __post_init__(self):
        if self.timeframes is None:
            self.timeframes = ["1M", "5M", "15M"]

@dataclass
class RiskManagementConfig:
    """Risk management parameters"""
    max_daily_trades: int = 20
    max_loss_per_day: float = 5.0
    max_drawdown: float = 0.10  # 10% of account balance
    stop_loss_percentage: float = 0.05  # 5%
    take_profit_percentage: float = 0.10  # 10%
    martingale_multiplier: float = 1.5
    max_martingale_levels: int = 3

@dataclass
class TechnicalIndicatorsConfig:
    """Technical indicators configuration"""
    rsi_period: int = 14
    rsi_overbought: int = 70
    rsi_oversold: int = 30

    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9

    bollinger_period: int = 20
    bollinger_std: float = 2.0

    ma_fast: int = 5
    ma_slow: int = 20

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    log_file: str = "trading_bot.log"
    log_trades: bool = True
    log_signals: bool = True

class Config:
    """Main configuration class"""

    def __init__(self):
        # Load from environment variables
        self.iqoption = IQOptionConfig(
            email=os.getenv("IQOPTION_EMAIL", ""),
            password=os.getenv("IQOPTION_PASSWORD", ""),
            demo_mode=os.getenv("IQOPTION_DEMO_MODE", "true").lower() == "true",
            practice_mode=os.getenv("IQOPTION_PRACTICE_MODE", "true").lower() == "true"
        )

        self.llm = LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "openai"),
            api_key=os.getenv("LLM_API_KEY", ""),
            model=os.getenv("LLM_MODEL", "gpt-4"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1000"))
        )

        self.trading = TradingConfig()
        self.risk_management = RiskManagementConfig()
        self.indicators = TechnicalIndicatorsConfig()
        self.logging = LoggingConfig()

        # Active assets (EUR/USD, GBP/USD, etc.)
        self.active_assets = [
            "EUR/USD",
            "GBP/USD",
            "USD/JPY",
            "USD/CHF",
            "AUD/USD",
            "USD/CAD"
        ]

        # Trading hours (UTC)
        self.trading_hours = {
            "start": "09:00",
            "end": "21:00"
        }

        # Strategy selection
        self.active_strategies = [
            "rsi",
            "macd",
            "bollinger",
            "llm"
        ]

    def validate(self) -> bool:
        """Validate configuration"""
        if not self.iqoption.email or not self.iqoption.password:
            print("ERROR: IQ Option credentials not set")
            return False

        if self.llm.provider == "openai" and not self.llm.api_key:
            print("WARNING: OpenAI API key not set, LLM features will be disabled")

        return True

# Global config instance
config = Config()