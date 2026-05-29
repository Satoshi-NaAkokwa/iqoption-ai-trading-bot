#!/bin/bash
# Weekly 7-Day IQ Option Bot Summary Report
# Runs every Monday at 00:00 via cron
# Provides full 7-day analysis without adding to hourly token costs

TELEGRAM_TOKEN=$(grep TELEGRAM_BOT_TOKEN /home/openclaw/.openclaw-env 2>/dev/null | cut -d'=' -f2)
CHAT_ID="5622980863"

LOG_FILE="/home/openclaw/.openclaw/workspace/iqoption-ai-trading-bot-new/trading.log"
REPORT_DIR="/home/openclaw/.openclaw/workspace/reports"
mkdir -p "$REPORT_DIR"

# Calculate date range
END_DATE=$(date '+%Y-%m-%d')
START_DATE=$(date -d "7 days ago" '+%Y-%m-%d')
WEEK_NUM=$(date '+%Y-W%V')

# Extract 7-day data from logs
WEEKLY_DATA=$(sed -n "/${START_DATE}/,/${END_DATE}/p" "$LOG_FILE" 2>/dev/null)

# Count trades and wins
TOTAL_TRADES=$(echo "$WEEKLY_DATA" | grep -c "Trade #" || echo "0")
TOTAL_WINS=$(echo "$WEEKLY_DATA" | grep -c "WIN" || echo "0")
TOTAL_LOSSES=$(echo "$WEEKLY_DATA" | grep -c "LOSS" || echo "0")

# Calculate P&L from 7-day period
WEEKLY_PNL=$(echo "$WEEKLY_DATA" | grep "WIN\|LOSS" | grep -oP '\$[+-][0-9.]+' | awk '{sum+=$1} END {print sum}' || echo "0")

# Extract hourly stats (per hour of day)
HOURLY_BREAKDOWN=$(echo "$WEEKLY_DATA" | grep -oP '\d{2}:\d{2}:\d{2}' | cut -d':' -f1 | sort | uniq -c | sort -rn | head -10)

# Best performing hours
BEST_HOUR=$(echo "$HOURLY_BREAKDOWN" | head -1 | awk '{print $2}' || echo "N/A")

# Extract asset performance
ASSET_STATS=$(echo "$WEEKLY_DATA" | grep -oP '(CALL|PUT) [A-Z]{6}-OTC' | sort | uniq -c | sort -rn | head -5)

# Best asset
BEST_ASSET=$(echo "$ASSET_STATS" | head -1 | awk '{print $2, $3}' || echo "N/A")

# Extract strategy performance
STRATEGY_STATS=$(echo "$WEEKLY_DATA" | grep -oP '\w+:\s[0-9]+%' | head -10)

# Calculate win rate
if [ "$TOTAL_TRADES" -gt 0 ]; then
    WIN_RATE=$(echo "scale=1; $TOTAL_WINS * 100 / $TOTAL_TRADES" | bc 2>/dev/null || echo "0")
else
    WIN_RATE="0"
fi

# Format weekly P&L
if [[ "$WEEKLY_PNL" =~ ^- ]]; then
    WEEKLY_PNL_DISPLAY="$WEEKLY_PNL"
else
    WEEKLY_PNL_DISPLAY="+$WEEKLY_PNL"
fi

# Get current balance
CURRENT_BALANCE=$(grep -A 15 "╔════════════════" "$LOG_FILE" 2>/dev/null | grep "Balance:" | grep -oP 'Balance: \$\K[0-9.]+' | tail -1)

# Get starting balance from 7 days ago
START_BALANCE=$(sed -n "/${START_DATE}/p" "$LOG_FILE" 2>/dev/null | grep "Balance:" | head -1 | grep -oP 'Balance: \$\K[0-9.]+' || echo "N/A")

# Calculate balance change
if [ "$START_BALANCE" != "N/A" ] && [ "$CURRENT_BALANCE" != "N/A" ]; then
    BALANCE_CHANGE=$(echo "$CURRENT_BALANCE - $START_BALANCE" | bc 2>/dev/null || echo "0")
    if [[ "$BALANCE_CHANGE" =~ ^- ]]; then
        BALANCE_CHANGE_DISPLAY="$BALANCE_CHANGE"
    else
        BALANCE_CHANGE_DISPLAY="+$BALANCE_CHANGE"
    fi
else
    BALANCE_CHANGE_DISPLAY="N/A"
fi

# Calculate trades per day
TRADES_PER_DAY=$(echo "scale=1; $TOTAL_TRADES / 7" | bc 2>/dev/null || echo "0")

# Get top strategies
TOP_STRATEGIES=$(echo "$WEEKLY_DATA" | grep -A 10 "Top Strategies:" | grep -v "Top Strategies:" | head -5 || echo "No strategy data")

# Format full weekly report
MESSAGE="📊 *🗓️ IQ Option Bot - Weekly 7-Day Report*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 ${START_DATE} to ${END_DATE} | Week ${WEEK_NUM}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*💰 FINANCIALS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Starting Balance: \$${START_BALANCE}
Current Balance:  \$${CURRENT_BALANCE}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 7-Day P&L: \$${WEEKLY_PNL_DISPLAY}
💵 Balance Change: \$${BALANCE_CHANGE_DISPLAY}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*📊 TRADING STATS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Trades: ${TOTAL_TRADES}
✅ Wins: ${TOTAL_WINS}
❌ Losses: ${TOTAL_LOSSES}
🎯 Win Rate: ${WIN_RATE}%
📊 Trades/Day: ${TRADES_PER_DAY}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*⚡ BEST PERFORMERS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 Best Hour: ${BEST_HOUR}:00
💹 Best Asset: ${BEST_ASSET}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Top Strategies:
$(echo "$TOP_STRATEGIES" | sed 's/^/│ /' | head -3)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 *Asset Breakdown (Top 5):*
$(echo "$ASSET_STATS" | sed 's/^/│ /')

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*🏆 KEY INSIGHTS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$(if [ "$WIN_RATE" -ge 60 ]; then
    echo "✅ Excellent win rate (>60%)"
elif [ "$WIN_RATE" -ge 50 ]; then
    echo "⚠️ Moderate win rate - optimize strategies"
else
    echo "❌ Low win rate - review strategy selection"
fi)

$(if [[ "$WEEKLY_PNL" =~ ^[0-9] ]]; then
    echo "✅ Profitable week - continue current approach"
else
    echo "❌ Losses this week - consider tightening risk"
fi)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Full 7-day context analyzed
Next weekly report: $(date -d "next Monday" '+%Y-%m-%d')
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Send to Telegram
if [ -n "$TELEGRAM_TOKEN" ]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
        -d "chat_id=${CHAT_ID}" \
        -d "text=${MESSAGE}" \
        -d "parse_mode=Markdown" > /dev/null 2>&1
fi

# Save to report archive
REPORT_FILE="${REPORT_DIR}/weekly-report-${WEEK_NUM}.log"
echo "Weekly Report - Week ${WEEK_NUM}" > "$REPORT_FILE"
echo "Date Range: ${START_DATE} to ${END_DATE}" >> "$REPORT_FILE"
echo "Total Trades: ${TOTAL_TRADES}" >> "$REPORT_FILE"
echo "Wins: ${TOTAL_WINS} | Losses: ${TOTAL_LOSSES}" >> "$REPORT_FILE"
echo "Win Rate: ${WIN_RATE}%" >> "$REPORT_FILE"
echo "7-Day P&L: \$${WEEKLY_PNL_DISPLAY}" >> "$REPORT_FILE"
echo "Balance Change: \$${BALANCE_CHANGE_DISPLAY}" >> "$REPORT_FILE"
echo "Best Hour: ${BEST_HOUR}" >> "$REPORT_FILE"
echo "Best Asset: ${BEST_ASSET}" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "Top Strategies:" >> "$REPORT_FILE"
echo "$TOP_STRATEGIES" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "Asset Breakdown:" >> "$REPORT_FILE"
echo "$ASSET_STATS" >> "$REPORT_FILE"

echo "Weekly report saved to ${REPORT_FILE}"