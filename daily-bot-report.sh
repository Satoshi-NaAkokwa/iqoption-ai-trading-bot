#!/bin/bash
# Daily Bot Report Generator
# Run at 23:00 GMT+8 each day

TODAY=$(date '+%Y-%m-%d')
LOG_FILE="/home/openclaw/.openclaw/workspace/bot-reports.log"
REPORT_DIR="/home/openclaw/.openclaw/workspace/reports"

mkdir -p "$REPORT_DIR"

echo "========================================" >> "$LOG_FILE"
echo "📊 DAILY BOT REPORT - $TODAY" >> "$LOG_FILE"
echo "Generated: $(date '+%Y-%m-%d %H:%M %Z')" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# IQ Option Bot
IQ_LOG="/home/openclaw/.openclaw/workspace/iqoption-ai-trading-bot-new/trading.log"
IQ_TRADES=$(grep -E "$TODAY.*(WIN|LOSS)" "$IQ_LOG" 2>/dev/null | wc -l)
IQ_WINS=$(grep -E "$TODAY.*WIN" "$IQ_LOG" 2>/dev/null | wc -l)
IQ_LOSSES=$(grep -E "$TODAY.*LOSS" "$IQ_LOG" 2>/dev/null | wc -l)
IQ_BALANCE=$(grep -E "$TODAY.*Balance:" "$IQ_LOG" 2>/dev/null | tail -1 | grep -oP 'Balance: \$\K[0-9.]+' || echo "N/A")

echo "" >> "$LOG_FILE"
echo "🧠 IQ OPTION BOT:" >> "$LOG_FILE"
echo "   Trades: $IQ_TRADES (W:$IQ_WINS L:$IQ_LOSSES)" >> "$LOG_FILE"
echo "   Balance: \$$IQ_BALANCE" >> "$LOG_FILE"

# KuCoin Bot
KU_STATE="/home/openclaw/.openclaw/workspace/agbara-advanced-kucoin-bot/bot-state.json"
if [ -f "$KU_STATE" ]; then
    KU_BALANCE=$(cat "$KU_STATE" | grep -oP '"totalValue":\s*\K[0-9.]+' || echo "N/A")
    KU_TRADES=$(cat "$KU_STATE" | grep -oP '"totalTrades":\s*\K[0-9]+' || echo "0")
    KU_PNL=$(cat "$KU_STATE" | grep -oP '"dailyPnL":\s*\K[-0-9.]+' || echo "0")
    KU_RUNNING=$(pm2 list 2>/dev/null | grep -c "kucoin.*online" 2>/dev/null || echo "0")
    
    echo "" >> "$LOG_FILE"
    echo "📈 KUCOIN BOT:" >> "$LOG_FILE"
    echo "   Running: $(if [ "$KU_RUNNING" -gt 0 ] 2>/dev/null; then echo 'Yes'; else echo 'No'; fi)" >> "$LOG_FILE"
    echo "   Portfolio: \$$KU_BALANCE" >> "$LOG_FILE"
    echo "   Daily PnL: \$$KU_PNL" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Also save to dated file
cp "$LOG_FILE" "$REPORT_DIR/report-$TODAY.log" 2>/dev/null

echo "Report generated for $TODAY"
