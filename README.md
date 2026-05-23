# IQ Option AI Trading Bot

An intelligent trading bot for IQ Option platform with LLM-powered market analysis and strategy learning capabilities.

## Features

- Real-time market data streaming via WebSocket
- Multi-timeframe analysis (1M, 5M, 15M candles)
- LLM-powered prediction and market analysis
- Strategy learning from multiple sources
- Technical analysis indicators (RSI, MACD, Bollinger Bands, etc.)
- Risk management and position sizing
- Automated trading execution
- Trade history and performance tracking

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

### Basic Usage

```bash
python main.py
```

### Trading on Specific Timeframes

```bash
python main.py --timeframe 1M  # 1-minute candles
python main.py --timeframe 5M  # 5-minute candles
python main.py --timeframe 15M # 15-minute candles
```

### Demo Mode (Paper Trading)

```bash
python main.py --demo
```

### Real Trading

```bash
python main.py --real
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

1. **RSI Strategy**: Based on Relative Strength Index
2. **MACD Strategy**: Based on Moving Average Convergence Divergence
3. **Bollinger Bands Strategy**: Based on Bollinger Bands
4. **LLM-Powered Strategy**: Uses LLM for market analysis
5. **Hybrid Strategy**: Combines multiple strategies

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