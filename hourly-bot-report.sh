#!/bin/bash
# Hourly IQ Option Bot Report to Telegram
# Chat ID: 5622980863
# Uses 2-day context for cost efficiency

TELEGRAM_TOKEN=$(grep TELEGRAM_BOT_TOKEN /home/openclaw/.openclaw-env 2>/dev/null | cut -d'=' -f2)
CHAT_ID="5622980863"

# Get latest stats from PM2 logs (last 2 days)
PM2_LOG="/home/openclaw/.pm2/logs/iqoption-247-learning-out.log"
LOG_FILE="/home/openclaw/.openclaw/workspace/iqoption-ai-trading-bot-new/trading.log"

# Extract from last 2 days of logs (more efficient parsing)
SINCE=$(date -d "2 days ago" '+%Y-%m-%d %H:%M:%S')

# Parse from trading.log (primary source)
LATEST=$(grep -A 15 "╔════════════════" "$LOG_FILE" 2>/dev/null | tail -20)

# Parse values
BALANCE=$(echo "$LATEST" | grep "Balance:" | grep -oP 'Balance: \$\K[0-9.]+' | tail -1)
TRADES=$(echo "$LATEST" | grep "Trades:" | grep -oP 'Trades: \K[0-9]+' | tail -1)
WINS=$(echo "$LATEST" | grep -oP 'W:\K[0-9]+' | tail -1)
LOSSES=$(echo "$LATEST" | grep -oP 'L:\K[0-9]+' | tail -1)
PNL=$(echo "$LATEST" | grep "P&L:" | grep -oP 'P&L: \$\K[+-0-9.]+' | tail -1)
WIN_RATE=$(echo "$LATEST" | grep "Win Rate:" | grep -oP 'Win Rate: \K[0-9.]+' | tail -1)
HOUR=$(date '+%H:%M')
DATE=$(date '+%Y-%m-%d')

# Calculate hourly performance from last hour
LAST_HOUR=$(date -d "1 hour ago" '+%Y-%m-%d %H:')
HOURLY_TRADES=$(grep "${LAST_HOUR}" "$LOG_FILE" 2>/dev/null | grep -c "Trade #" || echo "0")
HOURLY_WINS=$(grep "${LAST_HOUR}" "$LOG_FILE" 2>/dev/null | grep -c "WIN" || echo "0")
HOURLY_PNL=$(grep "${LAST_HOUR}" "$LOG_FILE" 2>/dev/null | grep -oP '\$[+-][0-9.]+' | awk '{sum+=$1} END {print sum}' || echo "0")

# Calculate win rate if not found
if [ -z "$WIN_RATE" ] && [ -n "$WINS" ] && [ -n "$TRADES" ]; then
    WIN_RATE=$(echo "scale=1; $WINS * 100 / $TRADES" | bc 2>/dev/null || echo "0")
fi

# Format hourly P&L
if [[ "$HOURLY_PNL" =~ ^- ]]; then
    HOURLY_PNL_DISPLAY="$HOURLY_PNL"
else
    HOURLY_PNL_DISPLAY="+$HOURLY_PNL"
fi

# Format message with detailed 2-day context
MESSAGE="📊 *IQ Option Bot - Hourly Report*
🕐 ${HOUR} GMT+8 | ${DATE}

💰 Balance: \$${BALANCE:-N/A}
📈 Total Trades: ${TRADES:-N/A}
🎯 Win Rate: ${WIN_RATE:-N/A}%
💵 Total P&L: \$${PNL:-N/A}

━━━━━━━━━━━━━━━
*Last Hour:*
📊 Trades: ${HOURLY_TRADES} | W: ${HOURLY_WINS}
💵 Hourly P&L: \$${HOURLY_PNL_DISPLAY}
━━━━━━━━━━━━━━━
📊 Context: Last 2 days of activity"

# Send to Telegram
if [ -n "$TELEGRAM_TOKEN" ]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
        -d "chat_id=${CHAT_ID}" \
        -d "text=${MESSAGE}" \
        -d "parse_mode=Markdown" \
        -d "disable_notification=true" > /dev/null 2>&1
fi

# Also log to local report file
echo "[${DATE} ${HOUR}] Balance: ${BALANCE:-N/A} | Trades: ${TRADES:-N/A} | Win Rate: ${WIN_RATE:-N/A}% | P&L: ${PNL:-N/A}" >> /home/openclaw/.openclaw/workspace/bot-reports.log