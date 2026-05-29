# 🚀 Binance API Setup Guide

Complete guide to configure your trading bot with Binance API credentials.

## 🔐 Step-by-Step Setup

### 1. Create Binance Account

If you don't already have a Binance account:

1. Go to https://www.binance.com/en/register
2. Sign up with email or phone
3. Complete KYC verification (required for trading)
4. Enable 2-Factor Authentication (CRITICAL!)

### 2. Generate API Keys

1. Log into Binance
2. Navigate to: **API Management** (under your profile)
3. Click **Create API**
4. Label your key (e.g., "Grid Trading Bot")
5. Complete 2FA verification

### 3. Configure API Permissions ⚠️ CRITICAL

When creating your API key, **ONLY** enable:

✅ **Spot Trading** - REQUIRED
❌ **Withdrawals** - DO NOT ENABLE
❌ **Futures Trading** - DO NOT ENABLE  
❌ **Margin Trading** - DO NOT ENABLE
❌ **Sub-account** - DO NOT ENABLE

### 4. Security Settings

#### IP Restrictions (Highly Recommended)
1. Click **Edit** next to your API key
2. Under **IP Access Restriction**, click **Add IP**
3. Add your server's IP address
4. If using dynamic IP, consider using a VPN with static IP

#### API Key Security
- ✅ Store API keys in `.env` file (NEVER commit to Git)
- ✅ Use different API keys for different bots
- ✅ Rotate keys every 3-6 months
- ✅ Never share API keys
- ✅ Delete old API keys when no longer needed

### 5. Test API Connection

Before going live, test your API keys:

```bash
# From the trading-bot directory
python3 -c "
from binance.client import Client
import os
from dotenv import load_dotenv

load_dotenv()
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_SECRET_KEY'))

# Test connection
account = client.get_account()
print('✅ API Connection Successful!')
print(f'Account Type: {account.get(\"accountType\", \"N/A\")}')
print(f'Can Trade: {account.get(\"canTrade\", False)}')
"
```

### 6. Configure Environment Variables

Update your `.env` file:

```bash
# Binance API Credentials
BINANCE_API_KEY=your_actual_api_key_here
BINANCE_SECRET_KEY=your_actual_secret_key_here

# Trading Configuration
TRADING_PAIR=USDCUSDT
GRID_SIZE=0.0001
GRID_LEVELS=20
TOTAL_INVESTMENT=100

# Risk Management
MAX_POSITION_SIZE=0.7
MAX_ORDERS_PER_SIDE=10
STOP_PRICE_DEVIATION=0.002

# Bot Configuration
CHECK_INTERVAL=30
DRY_RUN=true  # Start with true!
LOG_LEVEL=INFO
```

---

## 🔒 Security Best Practices

### Never Do This ❌
- Commit API keys to Git
- Share API keys in screenshots
- Store API keys in plain text files
- Use the same API keys for multiple bots
- Enable withdrawal permissions
- Disable 2FA on your Binance account

### Always Do This ✅
- Use `.env` files with proper permissions (chmod 600)
- Enable IP restrictions
- Keep API keys secret
- Use separate keys for production/testing
- Rotate keys periodically
- Monitor API usage in Binance dashboard

---

## 🧪 Test Your Configuration

### Paper Trading Test

Run the bot in dry-run mode first:

```bash
# Make sure DRY_RUN=true in .env
python3 trading_bot.py
```

Monitor the logs:
```bash
tail -f trading_bot.log
```

Expected output:
```
✅ Bot started successfully
📊 Current price: $1.0001
💵 USDT Balance: $1000.00
🎯 Placed 10 BUY orders + 10 SELL orders
```

### API Limits Test

Check if you're hitting rate limits:

```python
from binance.client import Client
import os
from dotenv import load_dotenv
import time

load_dotenv()
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_SECRET_KEY'))

# Test rate limiting
print("Testing API rate limits...")
for i in range(10):
    try:
        client.get_account()
        print(f"Request {i+1}/10: ✅ Success")
        time.sleep(0.1)  # 100ms between requests
    except Exception as e:
        print(f"Request {i+1}/10: ❌ Failed - {e}")
```

---

## 📊 Monitor API Usage

### Check API Usage in Binance

1. Go to **API Management** in Binance
2. Click on your API key
3. View **API Usage Statistics**
4. Monitor for unusual activity

### Set Up Alerts

If Binance offers API usage alerts, enable them to notify you of:
- Unusual API activity
- Rate limit hits
- Failed authentication attempts
- Permission changes

---

## 🚨 Troubleshooting

### Common Issues

#### "API key not valid"
**Solution:**
- Double-check API key and secret
- Make sure you copied the entire key
- Check if the key is still active

#### "Insufficient permissions"
**Solution:**
- Verify "Spot Trading" is enabled
- Check API key status in Binance dashboard
- Ensure account has proper verification

#### "IP address not allowed"
**Solution:**
- Check IP restrictions in Binance
- Verify your current IP: `curl ipinfo.io/ip`
- Add your IP to allowed list

#### "Rate limit exceeded"
**Solution:**
- The bot has built-in rate limiting (100ms)
- If still hitting limits, increase `CHECK_INTERVAL`
- Consider upgrading API limits (if needed)

---

## 📝 API Key Rotation

### When to Rotate
- Every 3-6 months
- If you suspect compromise
- After security incidents
- When changing development/production environments

### How to Rotate
1. Create new API key in Binance
2. Update `.env` with new credentials
3. Test new credentials
4. Delete old API key after verification

---

## 🔍 Verification Checklist

Before going live, verify:

- [ ] Binance account created and verified
- [ ] 2FA enabled on Binance account
- [ ] API keys generated (Spot Trading only)
- [ ] IP restrictions configured
- [ ] `.env` file configured correctly
- [ ] API connection tested successfully
- [ ] Paper trading working for 1+ weeks
- [ ] No withdrawal permissions enabled
- [ ] Telegram notifications set up (optional)
- [ ] Emergency procedures documented
- [ ] Monitoring plan established

---

## 📞 Support

### Binance Support
- Binance API Documentation: https://binance-docs.github.io/apidocs/
- Binance Support Center: https://www.binance.com/en/support

### Bot Support
- Check logs: `tail -f trading_bot.log`
- Run diagnostics: `python3 status_check.py`
- Review documentation: `README.md`

---

## 🎯 Next Steps

After API Setup:

1. **Week 1:** Paper trading validation
   ```bash
   python3 trading_bot.py  # DRY_RUN=true
   ```

2. **Week 2:** Small capital test
   ```bash
   # Update .env: TOTAL_INVESTMENT=100, DRY_RUN=false
   python3 trading_bot.py
   ```

3. **Week 3-4:** Scale gradually
   - Increase capital based on performance
   - Monitor risk metrics
   - Optimize parameters

---

## ⚠️ Final Security Warning

**Your API keys are the keys to your trading account.**

- Never share them
- Never commit them to version control
- Always use IP restrictions
- Never enable withdrawal permissions
- Monitor usage regularly
- Rotate them periodically

**Remember:** If your API keys are compromised, someone could drain your trading account. Treat them like your bank account credentials.

---

**Setup Complete!** Your trading bot is now configured to connect to Binance safely and securely.

**Ready for:** Paper trading phase 🚀