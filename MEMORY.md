# MEMORY.md - Trading Bot Status & Context

## Current Date: 2026-05-26 06:48 GMT+8

## 📊 DAILY REPORTS - AUTOMATED ✅
- **Cron Job**: `daily-bot-report` runs at 23:00 GMT+8 daily
- **Reports saved to**: `/home/openclaw/.openclaw/workspace/bot-reports.log`
- **Archived reports**: `/home/openclaw/.openclaw/workspace/reports/report-YYYY-MM-DD.log`
- **Script**: `/home/openclaw/.openclaw/workspace/daily-bot-report.sh`

## 🔴 BOT STATUS ISSUES

### IQ Option Bot (v4 Intelligent)
- ✅ Running via PM2 but NOT trading
- **Reason**: In "Off-Hours" session mode (trades during market hours only)
- **Yesterday (May 25)**: 22 trades, +$107.10 profit (but this seems to be carryover display issue)
- **Today (May 26)**: 0 trades so far

### KuCoin Bot
- ❌ NOT RUNNING - was stopped
- **Portfolio**: $9.66 total (mostly in BTC/ETH/KCS, ~$0 USDT available)
- **Cannot trade**: Insufficient USDT to open positions

---

## 🔍 IQ OPTION BOT - ROOT CAUSE ANALYSIS (RESOLVED)

### What Went Wrong (v3 Aggressive Bot)

1. **Martingale Too Aggressive**: 2x multiplier hit $3,200 trades, drained account
2. **No Learning**: Bot didn't track which assets/strategies worked
3. **Low Win Rate**: 49.3% (needs 59%+ for profit with 85% payout)
4. **Poor Asset Selection**: Traded worst performers (PUT EURGBP-OTC: 13 losses)

### ✅ FIXES IN v4 INTELLIGENT BOT

- **TradingMemory**: Tracks win rate per asset/direction/strategy
- **SmartRecovery**: 1.6x multiplier, starts after 2 losses
- **Conservative Base**: $10 trades (vs $100 before)
- **Adaptive Weights**: Boosts winning strategies, penalizes losers

### 📊 Best/Worst Assets (from 152 trades)

**AVOID**: PUT EURGBP-OTC, CALL EURUSD-OTC, CALL USDCHF-OTC
**PREFER**: CALL GBPJPY-OTC, PUT GBPUSD-OTC, PUT EURJPY-OTC

---

## Previous Status (2026-05-24)

## ✅ KUCOIN BOT: RUNNING WITH PM2!

### KuCoin Bot - PM2 Configured ✅
- **Status**: Bot running via PM2 (process: `agbara-kucoin-bot`)
- **PM2**: Auto-restart enabled, max 10 restarts, 500MB memory limit
- **Logs**: `/home/openclaw/.openclaw/workspace/agbara-advanced-kucoin-bot/logs/`
- **API**: Connection successful
- **LLM**: Using rule-based fallback (no local LLM available)

### Portfolio:
- Total: ~$9.67 USDT
- Open Positions: 0
- Daily PnL: $0.00

### ⚠️ PM2 Startup Script - NEEDS SUDO
Run this command to enable PM2 auto-start on boot:
```bash
sudo env PATH=$PATH:/usr/bin /opt/openclaw/npm-global/lib/node_modules/pm2/bin/pm2 startup systemd -u openclaw --hp /home/openclaw
```

## 📦 IQ OPTION BOT - GitHub Pushed ✅

### Repository Live ✅
- **URL**: https://github.com/Satoshi-NaAkokwa/iqoption-ai-trading-bot
- **Status**: Code pushed successfully
- **Files**: All Python files, README, LICENSE, .gitignore

### ⚠️ IQ Option Credentials - INVALID
The credentials provided are being rejected by IQ Option:
- **Error**: "You entered the wrong credentials. Please ensure that your login/password is correct."
- **Action Required**: User needs to verify IQ Option login credentials

### Bot Setup Status:
- ✅ Python virtual environment created
- ✅ iqoptionapi v6.8.9.1 installed (from GitHub source)
- ✅ data_collector.py updated for correct API
- ❌ Cannot test - credentials invalid

## 🔧 FIXES APPLIED

### 2026-05-24 08:55 GMT+8
- Pushed IQ Option bot to GitHub (new repo created)
- Installed iqoptionapi from GitHub source (v6.8.9.1)
- Updated data_collector.py for correct API usage
- Connection test failed - credentials rejected by IQ Option

### 2026-05-24 06:22 GMT+8
- Set up PM2 with ecosystem.config.js for KuCoin bot
- PM2 auto-restart enabled (max 10 restarts)
- Created IQ Option bot repo with LICENSE and .gitignore

### 2026-05-24 02:29 GMT+8
- Fixed KuCoin API header: `KC-API-KEY-VERSION` → `KC-API-VERSION`