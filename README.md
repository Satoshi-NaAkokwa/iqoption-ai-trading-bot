# IQ Option V8 Trading Bot - 90%+ Win Rate Target

## 🎯 Overview

Self-learning trading bot for IQ Option with adaptive parameters, hour-based filtering, and asset optimization.

## ✨ Features

### High Win Rate Strategy
- **Minimum 85% confidence** required for trades
- **5+ indicator confluence** (RSI, MACD, Bollinger, Stochastic, Trend, Patterns)
- **No counter-trend trades** - trend must align with direction

### 🧠 Self-Learning & Self-Improvement
- **Adaptive confidence thresholds** based on recent performance
- **Hour filtering** - automatically skips low-performing hours
- **Asset optimization** - focuses on best-performing assets
- **Parameter adjustment** - learns from wins and losses

### 📊 Smart Filtering
- **Best Hours**: 0, 3, 7, 8, 9, 13, 14, 17, 21, 23 (70%+ WR)
- **Skip Hours**: 6, 12, 16, 20, 22 (below 50% WR)
- **Best Assets**: EURUSD-OTC (64% WR), EURJPY-OTC (58% WR)

### 🛡️ Loss Recovery
- Pause after 2 consecutive losses
- 30-minute cooldown period
- Automatic recovery mode

### 📱 Telegram Reporting
- Hourly performance reports
- Trade notifications
- Loss recovery alerts

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/Satoshi-NaAkokwa/iqoption-ai-trading-bot.git
cd iqoption-ai-trading-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## ⚙️ Configuration

Create `.env` file:
```env
IQOPTION_EMAIL=your_email@example.com
IQOPTION_PASSWORD=your_password
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## 🚀 Running

### Direct
```bash
source venv/bin/activate
python bot_high_winrate_v8.py
```

### With PM2 (Recommended)
```bash
pm2 start ecosystem-v8.config.js
pm2 save
```

## 📁 File Structure

```
├── bot_high_winrate_v8.py    # Main bot with self-learning
├── ecosystem-v8.config.js    # PM2 configuration
├── requirements.txt          # Python dependencies
├── .env                      # Credentials (not in git)
├── trading_memory_v8.json    # Trade history (auto-generated)
└── learning_config_v8.json   # Learned parameters (auto-generated)
```

## 🧠 How Self-Learning Works

1. **After every 10 trades**, the bot analyzes performance
2. **Adjusts skip hours** based on hourly win rates
3. **Updates asset list** based on asset performance
4. **Modifies confidence threshold** based on recent win rate
5. **Tracks indicator accuracy** for future improvements

### Learning Example

```
🧠 Learning update: Skip hours=[6, 12, 16, 20, 22], Best hours=[0, 3, 7, 8, 9, 13, 14]
🧠 Assets: ['EURUSD-OTC', 'EURJPY-OTC'], Confidence adj: -2
```

## 📊 Expected Performance

| Metric | Target |
|--------|--------|
| Win Rate | 85-95% |
| Daily Trades | 20-50 |
| Risk per Trade | $10 |
| Max Drawdown | 10% |

## ⚠️ Risk Warning

- This bot is for **PRACTICE account only**
- Trading involves significant risk of loss
- Past performance does not guarantee future results
- Never trade with money you cannot afford to lose

## 📜 Version History

| Version | Changes |
|---------|---------|
| **V8** | Self-learning, hour filtering, asset optimization, 85% min confidence |
| V7 | Multi-timeframe analysis, 80% confidence (deprecated) |
| V6 | Market adaptive (deprecated) |
| V5 | 24/7 learning (deprecated) |

## 📄 License

MIT License - Use at your own risk.
