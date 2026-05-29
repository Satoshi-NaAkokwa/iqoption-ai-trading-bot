# IQ Option AI Trading Bot

An intelligent trading bot for IQ Option platform with LLM-powered market analysis and adaptive strategy capabilities.

## 🚀 Bot Versions

| Version | File | Description | Trade Amount | Risk Level | Status |
|---------|------|-------------|--------------|------------|--------|
| **v6** | `bot_market_adaptive_v6.py` | **MARKET ADAPTIVE (PRODUCTION)** | $10-$66 | Smart | ✅ Active |
| v5 | `bot_247_learning_v5.py` | 24/7 Learning Bot | $100-$3200 | **HIGH** | Legacy |
| v4 | `bot_intelligent_v4.py` | Intelligent Bot | $1 | Moderate | Legacy |
| v3 | `bot_aggressive_v3.py` | Aggressive Martingale | $100-$3200 | **HIGH** | Deprecated |
| v2 | `bot_adaptive_v2.py` | Dynamic Asset Switching | $1 | Moderate | Legacy |
| v1 | `main.py` | Original LLM-powered | $1 | Conservative | Legacy |

## ⭐ Recommended Version: v6 Market Adaptive Bot

**v6 is the current production bot with the following features:**
- 🎯 **High Win Rate**: 65%+ target through multi-indicator confluence
- 🌍 **Dynamic Market Trading**: OTC + Normal market switching
- ⏰ **Session Detection**: Tokyo/London/NY opening/closing detection
- 📊 **Adaptive Conditions**: Volatility, trend, and hour-based optimization
- 🔍 **Multi-Timeframe**: 1min + 5min alignment required
- 💎 **75%+ Confidence**: High-probability setups only
- 📈 **Trend Filtering**: Only trade WITH the trend
- 🎚️ **Support/Resistance**: Entry at key levels only

See [CHANGELOG.md](CHANGELOG.md) for version history.

## ⚠️ IMPORTANT WARNING

**Trading involves significant risk. Always start with DEMO accounts!**

- All bots should be tested on DEMO/Practice accounts first
- Never risk more than you can afford to lose
- The v5 aggressive bot uses Martingale with trades up to $3,200 (HIGH RISK)
- v6 Market Adaptive is the recommended production bot with smart risk management
- Past performance does not guarantee future results

**USE AT YOUR OWN RISK**

## Features

- Real-time market data streaming via WebSocket
- Multi-timeframe analysis (1M, 5M, 15M candles)
- LLM-powered prediction and market analysis
- Strategy learning from multiple sources
- Technical analysis indicators (RSI, MACD, Bollinger Bands, Stochastic, etc.)
- **Session-aware trading** (Asian/London/New York)
- **Martingale loss recovery system** (aggressive version)
- Risk management and position sizing
- Automated trading execution
- Trade history and performance tracking
- **24/7 OTC asset support**

## Prerequisites

- Python 3.8+
- IQ Option account
- LLM API credentials (OpenAI or compatible)

```bash
pip install iqoptionapi numpy pandas requests websockets
```

## Installation

```bash
git clone https://github.com/your-username/iqoption-ai-trading-bot.git
cd iqoption-ai-trading-bot
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`
2. Add your IQ Option credentials
3. Add your LLM API credentials
4. Configure your trading parameters

```bash
cp .env.example .env
nano .env
```

## Usage

### Basic Usage (Conservative Bot)

```bash
# Activate virtual environment first
source venv/bin/activate

# Run conservative LLM-powered bot
python main.py
```

### v6 Market Adaptive Bot (Recommended - Production)

```bash
# Main production bot with 65%+ win rate target
python bot_market_adaptive_v6.py
```

### v5 24/7 Learning Bot (Legacy)

```bash
# Continuous learning with OTC support
python bot_247_learning_v5.py
```

### Aggressive Trading (HIGH RISK - DEMO ONLY!)

```bash
# ⚠️ WARNING: Uses Martingale up to $3,200 per trade!
python bot_aggressive_v3.py
```

### Run with PM2 (Production - Recommended)

```bash
# Start the v6 bot with PM2 for process management
pm2 start ecosystem.config.js

# View logs
pm2 logs iqoption-v6-bot

# Monitor performance
pm2 monit

# Stop the bot
pm2 stop iqoption-v6-bot

# Restart the bot
pm2 restart iqoption-v6-bot
```

## Architecture

### Components

1. **Data Collector**: Fetches real-time market data via IQ Option API
2. **Technical Analyzer**: Calculates technical indicators
3. **LLM Analyst**: Uses LLM for market analysis and prediction
4. **Strategy Engine**: Implements trading strategies
5. **Risk Manager**: Manages position sizing and risk
6. **Trade Executor**: Executes trades on IQ Option
7. **Performance Tracker**: Tracks trade history and performance

### Data Flow

```
Market Data → Technical Analyzer → LLM Analyst → Strategy Engine → Risk Manager → Trade Executor → Performance Tracker
```

## Strategies

### v6 Market Adaptive Strategies

The v6 bot uses a comprehensive multi-indicator approach:

1. **RSI + Stochastic Confluence**: Both indicators must agree
2. **Multi-Timeframe Alignment**: 1min + 5min must show same signal
3. **Trend Filter**: Only trade WITH the trend (MAs + ADX)
4. **Support/Resistance**: Entry at key price levels
5. **Session Optimization**: Different settings for Tokyo/London/NY
6. **Volatility Adaptation**: Adjust based on market volatility
7. **High Confidence Threshold**: 75%+ confluence required

### Legacy Strategies (v1-v5)

**Technical Analysis Strategies:**
1. **RSI Reversal**: Oversold (<30) = CALL, Overbought (>70) = PUT
2. **Stochastic Oscillator**: K/D crossovers in extreme zones
3. **Bollinger Bands Breakout**: Price near bands = reversal
4. **MACD Crossover**: Momentum-based signals
5. **Support/Resistance Bounce**: Price at key levels

**Advanced Strategies (v5):**
6. **Candlestick Patterns**: Hammer, Engulfing, Doji detection
7. **Momentum Reversal**: Counter-trend trading
8. **Session-Aware**: Different strategies per market session

**Loss Recovery (Aggressive v5):**
- **Martingale System**: 2x multiplier after losses
- **Max 5 levels**: $100 → $200 → $400 → $800 → $1600 → $3200
- **Auto-pause**: Stops after 5 consecutive losses

## Risk Management

- Position sizing based on account balance
- Stop-loss and take-profit levels
- Daily loss limits
- Maximum concurrent trades
- Risk/reward ratio optimization

## LLM Integration

The bot uses LLM for:

- Market sentiment analysis
- Pattern recognition
- Strategy optimization
- Risk assessment
- Trade decision support

## API Documentation

### IQ Option API

The bot uses the official `iqoptionapi` library.

Documentation: https://iqoptionapi.github.io/iqoptionapi/en/

## Configuration Parameters

See `config.py` for all configurable parameters:

- Trading timeframes
- Risk management settings
- Technical indicator parameters
- LLM settings
- Strategy selection

## Performance Monitoring

### v6 Bot Logs

```bash
# View real-time trading logs
tail -f trading_v6.log

# View recent trades
tail -100 trading_v6.log | grep "TRADE EXECUTED"

# Check win rate
grep "WIN RATE" trading_v6.log | tail -5
```

### PM2 Monitoring

```bash
# View PM2 logs
pm2 logs iqoption-v6-bot

# Monitor process metrics
pm2 monit

# Check process status
pm2 status
```

## Troubleshooting

### v6 Bot Issues

**Bot not starting:**
1. Check Python version (3.8+ required)
2. Verify all dependencies installed: `pip install -r requirements.txt`
3. Check `.env` file is configured correctly
4. Verify IQ Option credentials

**Low win rate:**
1. Check market session - different sessions have different conditions
2. Verify indicators are aligned (75%+ confluence required)
3. Check trend filter - ensure trading WITH the trend
4. Review logs for signal strength issues

**Connection Issues:**
1. Check internet connection
2. Verify IQ Option API is working
3. Check for rate limiting (reduce frequency if needed)
4. Enable debug logging: Change `logging.INFO` to `logging.DEBUG`

**Trading Not Executing:**
1. Check account balance
2. Verify asset is available in current market
3. Check market hours (OTC vs Normal market)
4. Review confidence threshold - may need adjustment
5. Check PM2 logs: `pm2 logs iqoption-v6-bot`

## Safety Features

- Paper trading mode for testing
- Configurable risk limits
- Trade confirmation before execution (optional)
- Emergency stop functionality
- Comprehensive logging

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

- Report bugs and suggest enhancements
- Submit pull requests with clear documentation
- Test changes on demo accounts first
- Follow code style guidelines (PEP 8)

## Disclaimer

**IMPORTANT**: Trading involves significant risk. This bot is for educational purposes only. Past performance does not guarantee future results. Always trade responsibly and never risk more than you can afford to lose.

**USE AT YOUR OWN RISK**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## Support

For issues and questions, please open an issue on GitHub.

## Acknowledgments

- IQ Option API team for the excellent API library
- LLM providers for AI capabilities
- Open source trading community

---

**Remember**: Start with demo mode, test thoroughly, and use proper risk management! 🚀

---

**Remember**: Start with demo mode, test thoroughly, and use proper risk management!