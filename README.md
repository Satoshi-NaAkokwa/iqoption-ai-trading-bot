# IQ Option AI Trading Bot

An intelligent trading bot for IQ Option platform with LLM-powered market analysis and strategy learning capabilities.

## 🚀 Bot Versions

| Version | File | Description | Trade Amount | Risk Level |
|---------|------|-------------|--------------|------------|
| **v1** | `main.py` | Original LLM-powered bot | $1 | Conservative |
| **v2** | `bot_24_7.py` | 24/7 OTC trading | $1 | Moderate |
| **v3** | `bot_adaptive.py` | Adaptive with session awareness | $1 | Moderate |
| **v4** | `bot_adaptive_v2.py` | Dynamic asset switching | $1 | Moderate |
| **v5** | `bot_aggressive_v3.py` | **Aggressive Martingale** | $100-$3200 | **HIGH** |

## ⚠️ IMPORTANT WARNING

**The aggressive bot (v5) uses a Martingale loss recovery system with trades up to $3,200!**

- This is HIGH RISK trading
- Only use on PRACTICE/DEMO accounts
- The bot can hit recovery pause after 5 consecutive losses
- Current status shows it hit the pause limit

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

```bash
pip install iqoptionapi numpy pandas ta-lib requests websockets
pip install openai  # or your preferred LLM provider
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

### 24/7 OTC Trading (Recommended)

```bash
# Adaptive bot with session awareness
python bot_adaptive_v2.py
```

### Aggressive Trading (HIGH RISK - DEMO ONLY!)

```bash
# ⚠️ WARNING: Uses Martingale up to $3,200 per trade!
python bot_aggressive_v3.py
```

### Run with PM2 (Production)

```bash
pm2 start ecosystem.config.js
pm2 logs iqoption-aggressive-bot
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

The bot supports multiple strategies:

### Technical Analysis Strategies
1. **RSI Reversal**: Oversold (<30) = CALL, Overbought (>70) = PUT
2. **Stochastic Oscillator**: K/D crossovers in extreme zones
3. **Bollinger Bands Breakout**: Price near bands = reversal
4. **MACD Crossover**: Momentum-based signals
5. **Support/Resistance Bounce**: Price at key levels

### Advanced Strategies (v5)
6. **Candlestick Patterns**: Hammer, Engulfing, Doji detection
7. **Momentum Reversal**: Counter-trend trading
8. **Session-Aware**: Different strategies per market session

### Loss Recovery (Aggressive v5)
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

View real-time performance:

```bash
python performance.py
```

Generate performance reports:

```bash
python generate_report.py
```

## Troubleshooting

### Connection Issues

If you experience connection issues:

1. Check your internet connection
2. Verify IQ Option credentials
3. Check API rate limits
4. Enable debug logging

### Trading Not Executing

If trades are not executing:

1. Check account balance
2. Verify demo/real mode settings
3. Check market hours
4. Review risk management settings

## Safety Features

- Paper trading mode for testing
- Configurable risk limits
- Trade confirmation before execution (optional)
- Emergency stop functionality
- Comprehensive logging

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

**IMPORTANT**: Trading involves significant risk. This bot is for educational purposes only. Past performance does not guarantee future results. Always trade responsibly and never risk more than you can afford to lose.

**USE AT YOUR OWN RISK**

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

## Acknowledgments

- IQ Option API team for the excellent API library
- LLM providers for AI capabilities
- Open source trading community

---

**Remember**: Start with demo mode, test thoroughly, and use proper risk management!