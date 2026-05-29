# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [6.0.0] - 2026-05-30

### Added
- **Market Adaptive Bot** - Main production bot with dynamic market switching
- High win rate target (65%+) through multi-indicator confluence
- Dynamic OTC + Normal market switching
- Session detection (Tokyo/London/NY opening/closing)
- Adaptive conditions based on volatility, trend, and hour-based optimization
- Multi-timeframe analysis (1min + 5min alignment required)
- 75%+ confidence threshold for high-probability setups
- Trend filtering - only trade WITH the trend
- Support/Resistance detection for entry at key levels
- PM2 ecosystem configuration for production deployment
- Comprehensive logging with trading_v6.log

### Changed
- Base trade amount: $10 (adaptive up to $66)
- Risk level: Smart/Adaptive
- Enhanced technical analysis with multiple confluence signals
- Improved market session detection and classification

### Performance
- Designed for consistent 65%+ win rate
- Session-aware trading for optimal market conditions
- Dynamic asset switching based on market availability

## [5.0.0] - 2026-05-26

### Added
- **24/7 Learning Bot** - Continuous learning system
- OTC market support for 24/7 trading
- Advanced strategy learning and adaptation
- Martingale loss recovery system
- Recovery pause after 5 consecutive losses

### Changed
- Trade amount: $100-$3200 (aggressive)
- Risk level: HIGH
- Learning from past trades for optimization

### Removed
- Fixed trading hours (now 24/7)

## [4.0.0] - 2026-05-25

### Added
- **Intelligent Bot** - Advanced decision making
- Dynamic asset switching
- Improved technical analysis
- Risk management system

### Changed
- Trade amount: $1
- Risk level: Moderate
- Better market condition detection

## [3.0.0] - 2026-05-24

### Added
- **Aggressive Bot** - Higher risk trading
- Martingale system (2x multiplier)
- Multi-level recovery (up to 5 levels)

### Changed
- Trade amount: $100-$3200
- Risk level: HIGH
- Recovery system for losses

### Warning
- High risk trading - only for demo accounts

## [2.0.0] - 2026-05-24

### Added
- **24/7 Trading Bot** - OTC market support
- Session awareness
- Adaptive strategies per session

### Changed
- Trade amount: $1
- Risk level: Moderate

## [1.0.0] - 2026-05-22

### Added
- **Initial Release** - LLM-powered trading bot
- Real-time market data streaming
- Multi-timeframe analysis
- Technical analysis indicators (RSI, MACD, Bollinger Bands, Stochastic)
- LLM-powered prediction and market analysis
- Basic risk management
- Trade execution on IQ Option
- Trade history and performance tracking

### Features
- WebSocket connection for real-time data
- Technical indicator calculations
- Strategy engine with multiple strategies
- Risk manager with position sizing
- Trade executor for automated trading

---