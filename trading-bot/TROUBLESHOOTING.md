# 🔧 Troubleshooting Guide - Trading Bot

Complete guide to diagnosing and fixing common issues.

---

## 🚨 Emergency Procedures

### Immediate Bot Stop
```bash
# Find the bot process
ps aux | grep trading_bot.py

# Stop gracefully (cancels all orders)
kill -SIGTERM <PID>

# Force stop if needed
kill -9 <PID>

# Cancel all orders manually
python3 -c "
from binance.client import Client
from dotenv import load_dotenv
import os

load_dotenv()
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_SECRET_KEY'))
client.cancel_all_orders('USDCUSDT')
print('All orders canceled')
"
```

### Account Lockout Prevention
If you hit rate limits:
1. Stop the bot immediately
2. Wait 15-30 minutes
3. Increase `CHECK_INTERVAL` in .env
4. Restart bot

---

## 🔍 Common Issues & Solutions

### 1. Installation Issues

#### "No module named 'binance'"
```bash
# Solution: Install dependencies
pip3 install -r requirements.txt

# If that fails, try:
pip3 install python-binance python-dotenv pandas numpy requests
```

#### "Permission denied" when running scripts
```bash
# Solution: Make scripts executable
chmod +x deploy.sh
chmod +x test_api_connection.py

# Or run with python3 directly
python3 deploy.sh
python3 test_api_connection.py
```

#### "Python version too old"
```bash
# Check Python version
python3 --version

# Need Python 3.8+
# Install newer Python if needed
```

---

### 2. Configuration Issues

#### "API key not configured"
```bash
# Solution: Check .env file
cat .env | grep API_KEY

# Should see actual keys, not "your_api_key_here"

# Copy template if .env doesn't exist
cp .env.example .env

# Edit with your credentials
nano .env  # or use your preferred editor
```

#### "API key format invalid"
```bash
# Solution: Verify you copied the entire key
# Binance API keys should look like:
# BINANCE_API_KEY=abc123def456...
# (64 characters)

# Check you didn't include quotes or spaces
```

#### "File .env not found"
```bash
# Solution: Create from template
cd /home/openclaw/.openclaw/workspace/trading-bot
cp .env.example .env

# Then edit with your credentials
nano .env
```

---

### 3. API Connection Issues

#### "API connection failed"
```bash
# Test API connection
python3 test_api_connection.py

# Common causes:
# 1. Wrong API keys - double-check .env
# 2. Internet connection - test with: ping binance.com
# 3. Binance API down - check: https://status.binance.com/
# 4. IP restrictions - check your IP: curl ipinfo.io/ip
```

#### "Invalid API-key, IP, or permissions"
```bash
# Solutions:

# 1. Check API key status in Binance
#    Go to API Management → Check your API key

# 2. Verify IP restrictions
#    If enabled, add your current IP

# 3. Check permissions
#    Ensure "Spot Trading" is enabled
#    "Withdrawals" should be disabled

# 4. Verify key is still active
#    Keys can expire or be revoked
```

#### "Timestamp for this request outside recvWindow"
```bash
# Solution: System time synchronization issue
# Check system time:
date

# If time is wrong, sync with NTP:
sudo apt install ntp
sudo ntpdate pool.ntp.org

# Or on macOS:
sudo sntp -sS time.apple.com
```

---

### 4. Trading Issues

#### "Insufficient balance"
```bash
# Solution 1: Add USDT to Binance
#    Go to Wallet → Fiat and Spot → Deposit

# Solution 2: Reduce investment amount
#    Edit .env: TOTAL_INVESTMENT=50

# Solution 3: Check locked funds
#    Some funds may be in open orders
python3 -c "
from binance.client import Client
from dotenv import load_dotenv
import os

load_dotenv()
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_SECRET_KEY'))
orders = client.get_open_orders(symbol='USDCUSDT')
print(f'Open orders: {len(orders)}')

# Cancel if needed
for order in orders:
    client.cancel_order(symbol='USDCUSDT', orderId=order['orderId'])
print('All orders canceled')
"
```

#### "Order failed validation"
```bash
# Check risk limits
grep -E "(MAX_POSITION|MAX_ORDERS|STOP_PRICE)" .env

# Common issues:
# 1. Position size > 70% of balance
# 2. Too many orders (10 max per side)
# 3. Price deviation > 0.002 from $1
# 4. Insufficient balance

# Check logs for specific reason
tail -20 trading_bot.log
```

#### "No orders being placed"
```bash
# Check if bot is actually running
ps aux | grep trading_bot.py

# Check logs for errors
tail -50 trading_bot.log

# Verify configuration
grep -E "(DRY_RUN|TRADING_PAIR|GRID_SIZE)" .env

# Common causes:
# 1. Bot not running
# 2. DRY_RUN=false but no API configured
# 3. Price outside normal range (0.998-1.002)
# 4. Risk limits too restrictive
```

---

### 5. Performance Issues

#### "Bot running but no profits"
```bash
# Normal in low volatility periods
# Stablecoins trade in narrow range

# Check current conditions
python3 -c "
from binance.client import Client
from dotenv import load_dotenv
import os

load_dotenv()
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_SECRET_KEY'))
ticker = client.get_symbol_ticker(symbol='USDCUSDT')
price = float(ticker['price'])
print(f'Current price: ${price:.4f}')
print(f'Deviation from $1: {abs(price-1.0)*100:.3f}%')
"

# If deviation < 0.01%, low activity is normal
# Increase grid size for more activity
# Edit .env: GRID_SIZE=0.00008
```

#### "Too many failed orders"
```bash
# Check API rate limits
grep "rate limit" trading_bot.log | tail -10

# Increase check interval
# Edit .env: CHECK_INTERVAL=60  # seconds

# Reduce grid levels
# Edit .env: GRID_LEVELS=15
```

#### "High memory usage"
```bash
# Check bot memory usage
ps aux | grep trading_bot.py

# Restart bot if using >500MB
kill <PID>
python3 trading_bot.py

# Normal usage: 50-200MB
```

---

### 6. Monitoring Issues

#### "Can't access logs"
```bash
# Check if logs exist
ls -la trading_bot.log

# If not, check bot is running
ps aux | grep trading_bot.py

# If bot running but no logs:
# 1. Check log level
grep LOG_LEVEL .env

# 2. Check file permissions
ls -la *.log

# 3. Restart bot
kill <PID>
python3 trading_bot.py
```

#### "Telegram notifications not working"
```bash
# Check Telegram configuration
grep -E "(TELEGRAM_BOT_TOKEN|TELEGRAM_CHAT_ID)" .env

# Test connection
python3 telegram_bot.py

# Common issues:
# 1. Bot token incorrect - get from @BotFather
# 2. Chat ID incorrect - get from @userinfobot
# 3. Bot not started - send /start to your bot
# 4. Network issues - test internet connection
```

#### "Status check not working"
```bash
# Check if script exists
ls -la status_check.py

# Run with verbose output
python3 status_check.py 2>&1

# Check Python dependencies
python3 -c "import binance; print('binance installed')"
python3 -c "import dotenv; print('dotenv installed')"
```

---

## 🐛 Debug Mode

### Enable Debug Logging
```bash
# Edit .env
LOG_LEVEL=DEBUG

# Restart bot to apply
kill <PID>
python3 trading_bot.py

# Now you'll see detailed debug logs
tail -f trading_bot.log
```

### Enable Verbose API Calls
```bash
# Add to binance_client.py temporarily
# In __init__ method:
import logging
logging.getLogger('binance').setLevel(logging.DEBUG)
```

### Manual API Testing
```bash
# Test individual API calls
python3 -c "
from binance.client import Client
from dotenv import load_dotenv
import os

load_dotenv()
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_SECRET_KEY'))

# Test each function
print('Testing get_account...')
try:
    account = client.get_account()
    print(f'✅ Account: {account.get(\"accountType\")}')
except Exception as e:
    print(f'❌ Error: {e}')

print('Testing get_symbol_ticker...')
try:
    ticker = client.get_symbol_ticker(symbol='USDCUSDT')
    print(f'✅ Price: {ticker[\"price\"]}')
except Exception as e:
    print(f'❌ Error: {e}')

print('Testing get_open_orders...')
try:
    orders = client.get_open_orders(symbol='USDCUSDT')
    print(f'✅ Open orders: {len(orders)}')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

---

## 📊 Performance Tuning

### Reduce API Calls
```bash
# Increase check interval
CHECK_INTERVAL=60  # from 30

# Reduce grid levels
GRID_LEVELS=15  # from 20

# Reduce order refresh frequency
# (requires code modification)
```

### Optimize Grid Settings
```bash
# Low volatility market
GRID_SIZE=0.00008  # Tighter grid
GRID_LEVELS=25     # More levels

# High volatility market
GRID_SIZE=0.00015  # Wider grid
GRID_LEVELS=15     # Fewer levels
```

### Adjust Risk Limits
```bash
# More conservative
MAX_POSITION_SIZE=0.5  # from 0.7
MAX_ORDERS_PER_SIDE=5   # from 10
STOP_PRICE_DEVIATION=0.001  # from 0.002

# More aggressive
MAX_POSITION_SIZE=0.8  # from 0.7
MAX_ORDERS_PER_SIDE=15  # from 10
STOP_PRICE_DEVIATION=0.003  # from 0.002
```

---

## 🔄 Recovery Procedures

### Bot Crashes
```bash
# 1. Check error logs
tail -50 trading_bot.log | grep ERROR

# 2. Identify the error
# Common causes: API issues, network problems, configuration errors

# 3. Fix the issue (see sections above)

# 4. Restart bot
python3 trading_bot.py

# 5. Monitor closely
tail -f trading_bot.log
```

### API Key Compromised
```bash
# 1. IMMEDIATELY disable in Binance
#    Go to API Management → Delete API key

# 2. Generate new API key
#    Create new key with same permissions

# 3. Update .env
nano .env
# Update BINANCE_API_KEY and BINANCE_SECRET_KEY

# 4. Test new connection
python3 test_api_connection.py

# 5. Restart bot with new credentials
```

### Market Anomaly
```bash
# If USDT/USDC price deviates >0.5% from $1
# Bot should auto-stop via risk manager

# Manual stop if needed:
kill <PID>

# Check price:
python3 -c "
from binance.client import Client
from dotenv import load_dotenv
import os

load_dotenv()
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_SECRET_KEY'))
ticker = client.get_symbol_ticker(symbol='USDCUSDT')
print(f'Price: ${ticker[\"price\"]}')
"

# Wait for normal conditions (price back to 0.998-1.002)
# Then restart
python3 trading_bot.py
```

---

## 📞 Getting Help

### Self-Diagnosis Checklist
- [ ] Checked logs for errors?
- [ ] Tested API connection?
- [ ] Verified configuration?
- [ ] Checked Binance status?
- [ ] Verified API permissions?
- [ ] Checked internet connection?
- [ ] Tried restarting bot?

### Information to Provide
When asking for help, include:
1. Error message (exact text)
2. Log file output (last 50 lines)
3. Configuration (.env without secrets)
4. System information (OS, Python version)
5. Steps to reproduce the issue

### Useful Commands
```bash
# System info
python3 --version
pip3 list | grep binance

# Bot status
ps aux | grep trading_bot.py
ls -la trading_bot.log

# Configuration
cat .env | grep -v "SECRET\|API"

# Recent logs
tail -50 trading_bot.log

# API test
python3 test_api_connection.py
```

---

## ⚠️ When to Contact Support

### Issues Requiring Help
- Persistent API errors after troubleshooting
- Unexpected behavior not covered in this guide
- Security concerns (compromised API keys)
- Data inconsistencies
- Performance degradation

### Before Contacting
1. Read this troubleshooting guide
2. Check documentation (README.md)
3. Review logs for specific errors
4. Try common solutions
5. Gather information (see above)

---

## 🎯 Prevention

### Regular Maintenance
```bash
# Weekly checks
- Review logs for errors
- Check API usage in Binance
- Verify balance and positions
- Update documentation if needed

# Monthly maintenance
- Review performance metrics
- Optimize parameters
- Rotate API keys
- Update dependencies
- Backup configuration

# Quarterly review
- Overall performance assessment
- Risk evaluation
- Strategy optimization
- Security audit
```

### Backup Procedures
```bash
# Backup configuration
cp .env .env.backup
cp .env.example .env.backup

# Backup logs
cp trading_bot.log trading_bot.log.backup

# Backup trade history
# (if you implement trade history storage)

# Store backups securely
# - Use encrypted storage
# - Keep multiple versions
# - Store off-site
```

---

**Remember:** Most issues have simple solutions. Start with the basics (check logs, test API, verify config) before proceeding to more complex troubleshooting.

**Quick Reference:** See STATUS_CARD.md for essential commands and information.