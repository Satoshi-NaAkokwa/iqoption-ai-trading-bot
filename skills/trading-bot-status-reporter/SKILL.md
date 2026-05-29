# Trading Bot Status Reporter Skill

## Purpose
Provide clear, detailed status updates to the user about trading bot activities, decisions, and any required actions.

## Status Report Format

### 📊 BOT STATUS REPORT
```
Date/Time: [Current Time]
Bot Name: [KuCoin/IQ Option]
Status: [Running/Stopped/Error]
Uptime: [Duration]
```

### 💰 PORTFOLIO STATUS
```
Total Value: $[Amount]
Assets:
- [Asset]: [Amount] ($[Value])
- [Asset]: [Amount] ($[Value])
Available USDT: $[Amount]
```

### 📈 MARKET CONDITIONS
```
Sentiment: [BULLISH/BEARISH/NEUTRAL]
Fear/Greed Index: [Number]
Active Signals: [List]
```

### 🎯 TRADING ACTIVITY
```
Recent Actions: [List]
Pending Orders: [List]
Open Positions: [List]
```

### ✅ COMPLETED TASKS
- [Task 1]
- [Task 2]

### ⚠️ ISSUES/ALERTS
- [Issue 1]
- [Issue 2]

### 📝 REQUIRED ACTIONS
- [Action 1] - [Status: PENDING/AUTHORIZED]
- [Action 2] - [Status: PENDING/AUTHORIZED]

### 🤔 QUESTIONS FOR USER
- [Question 1]
- [Question 2]

## Communication Rules
1. ALWAYS provide status updates when changes occur
2. NEVER run silent background loops
3. ASK for authorization before critical actions
4. SUMMARIZE what was done and what's next
5. BE TRANSPARENT about issues and failures

## Update Frequency
- Every 2-4 hours during active trading
- Immediately when issues occur
- On every trade execution
- When user asks

## Authorization Required For:
- Selling existing positions
- Changing bot configuration
- Starting/stopping bots
- Depositing/withdrawing funds
- Changing risk parameters