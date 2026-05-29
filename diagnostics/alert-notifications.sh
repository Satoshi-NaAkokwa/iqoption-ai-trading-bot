#!/bin/bash
# ALERT NOTIFICATIONS - Send alerts when issues are detected

set -e

# Configuration
ALERT_METHOD="log"  # Options: log, email, slack, telegram
ALERT_EMAIL=""     # Set your email for email alerts
SLACK_WEBHOOK=""   # Set your Slack webhook URL
TELEGRAM_BOT=""   # Set your Telegram bot token
TELEGRAM_CHAT=""   # Set your Telegram chat ID

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

# Alert levels
LEVEL_ERROR=1
LEVEL_WARNING=2
LEVEL_INFO=3

# Alert history
ALERT_LOG="$HOME/.openclaw/alerts.log"
mkdir -p "$(dirname "$ALERT_LOG")"

send_alert() {
    local level=$1
    local message=$2
    local timestamp=$(date -Iseconds)

    case $ALERT_METHOD in
        log)
            log_alert "$level" "$message" "$timestamp"
            ;;
        email)
            send_email_alert "$level" "$message" "$timestamp"
            ;;
        slack)
            send_slack_alert "$level" "$message" "$timestamp"
            ;;
        telegram)
            send_telegram_alert "$level" "$message" "$timestamp"
            ;;
        *)
            log_alert "$level" "$message" "$timestamp"
            ;;
    esac
}

log_alert() {
    local level=$1
    local message=$2
    local timestamp=$3

    local level_text
    case $level in
        $LEVEL_ERROR) level_text="ERROR" ;;
        $LEVEL_WARNING) level_text="WARNING" ;;
        $LEVEL_INFO) level_text="INFO" ;;
        *) level_text="UNKNOWN" ;;
    esac

    echo "[$timestamp] [$level_text] $message" >> "$ALERT_LOG"

    case $level in
        $LEVEL_ERROR) echo -e "${RED}⚠ ALERT: $message${NC}" ;;
        $LEVEL_WARNING) echo -e "${YELLOW}⚠ WARNING: $message${NC}" ;;
        $LEVEL_INFO) echo -e "${GREEN}ℹ INFO: $message${NC}" ;;
    esac
}

send_email_alert() {
    local level=$1
    local message=$2
    local timestamp=$3

    if [ -z "$ALERT_EMAIL" ]; then
        echo "Email not configured"
        return
    fi

    local subject="[OpenClaw Alert] $(date +%Y-%m-%d) - $message"

    echo "Timestamp: $timestamp" | \
    mail -s "$subject" "$ALERT_EMAIL" 2>/dev/null || true

    echo "Email alert sent to $ALERT_EMAIL"
}

send_slack_alert() {
    local level=$1
    local message=$2
    local timestamp=$3

    if [ -z "$SLACK_WEBHOOK" ]; then
        echo "Slack not configured"
        return
    fi

    local color
    case $level in
        $LEVEL_ERROR) color="#FF0000" ;;
        $LEVEL_WARNING) color="#FFFF00" ;;
        $LEVEL_INFO) color="#00FF00" ;;
        *) color="#808080" ;;
    esac

    curl -X POST "$SLACK_WEBHOOK" \
        -H 'Content-Type: application/json' \
        -d "{
            \"attachments\": [{
                \"color\": \"$color\",
                \"title\": \"OpenClaw Alert\",
                \"text\": \"$message\",
                \"fields\": [{
                    \"title\": \"Timestamp\",
                    \"value\": \"$timestamp\",
                    \"short\": true
                }]
            }]
        }" >/dev/null 2>&1 || true

    echo "Slack alert sent"
}

send_telegram_alert() {
    local level=$1
    local message=$2
    local timestamp=$3

    if [ -z "$TELEGRAM_BOT" ] || [ -z "$TELEGRAM_CHAT" ]; then
        echo "Telegram not configured"
        return
    fi

    local emoji
    case $level in
        $LEVEL_ERROR) emoji="🚨" ;;
        $LEVEL_WARNING) emoji="⚠️" ;;
        $LEVEL_INFO) emoji="ℹ️" ;;
        *) emoji="📢" ;;
    esac

    curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT/sendMessage" \
        -d "chat_id=$TELEGRAM_CHAT" \
        -d "text=$emoji OpenClaw Alert: $message%0ATimestamp: $timestamp" >/dev/null 2>&1 || true

    echo "Telegram alert sent"
}

# Example alert functions
alert_gateway_down() {
    send_alert $LEVEL_ERROR "Gateway is not running!"
}

alert_high_memory() {
    local usage=$1
    send_alert $LEVEL_WARNING "High memory usage: $usage%"
}

alert_api_failure() {
    send_alert $LEVEL_ERROR "LLM API is not responding"
}

alert_error_spike() {
    local count=$1
    send_alert $LEVEL_ERROR "High error rate: $count errors in 5 minutes"
}

# Main menu
case "$1" in
    test)
        echo "Testing alert system..."
        send_alert $LEVEL_INFO "Test alert message"
        echo "Check alert log: $ALERT_LOG"
        ;;

    history)
        echo "Alert history:"
        cat "$ALERT_LOG"
        ;;

    clear)
        echo "Clearing alert log..."
        > "$ALERT_LOG"
        echo "Alert log cleared"
        ;;

    *)
        echo "OpenClaw Alert Notifications Utility"
        echo ""
        echo "Usage: $0 {test|history|clear}"
        echo ""
        echo "Alert Methods: $ALERT_METHOD"
        echo "Alert Log: $ALERT_LOG"
        echo ""
        echo "Configuration:"
        echo "  ALERT_METHOD=$ALERT_METHOD"
        echo "  ALERT_EMAIL=$ALERT_EMAIL"
        echo "  SLACK_WEBHOOK=$SLACK_WEBHOOK"
        echo "  TELEGRAM_BOT=$TELEGRAM_BOT"
        echo "  TELEGRAM_CHAT=$TELEGRAM_CHAT"
        echo ""
        echo "To configure alerts, edit this file and set your credentials."
        ;;
esac