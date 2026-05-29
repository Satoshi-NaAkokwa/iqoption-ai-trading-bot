# 🚨 Alert Configuration Guide

This guide explains how to configure and use the OpenClaw alert notification system.

## Overview

The `alert-notifications.sh` script provides a flexible alerting system that can notify you when issues are detected in your OpenClaw system.

## Supported Alert Methods

1. **Log** (Default) - Logs alerts to a file
2. **Email** - Sends email alerts
3. **Slack** - Posts alerts to Slack channels
4. **Telegram** - Sends Telegram messages

## Configuration

### Step 1: Open the alert script

```bash
cd ~/.openclaw/workspace/diagnostics
nano alert-notifications.sh
```

### Step 2: Configure Alert Method

Edit the `ALERT_METHOD` variable:

```bash
# Options: log, email, slack, telegram
ALERT_METHOD="log"
```

### Step 3: Configure Your Preferred Method

#### Email Alerts

```bash
ALERT_METHOD="email"
ALERT_EMAIL="your-email@example.com"
```

Requirements:
- `mail` command must be installed
- SMTP must be configured

#### Slack Alerts

```bash
ALERT_METHOD="slack"
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

How to get Slack webhook:
1. Go to https://api.slack.com/apps
2. Create a new app
3. Enable "Incoming Webhooks"
4. Create a new webhook
5. Copy the webhook URL

#### Telegram Alerts

```bash
ALERT_METHOD="telegram"
TELEGRAM_BOT="YOUR_BOT_TOKEN"
TELEGRAM_CHAT="YOUR_CHAT_ID"
```

How to get Telegram bot token:
1. Start a chat with @BotFather on Telegram
2. Create a new bot: `/newbot`
3. Follow the instructions
4. Copy the bot token

How to get Telegram chat ID:
1. Start a chat with your bot
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Find your chat ID in the response

## Testing Alerts

After configuration, test the alert system:

```bash
cd ~/.openclaw/workspace/diagnostics
./alert-notifications.sh test
```

This will send a test alert using your configured method.

## Viewing Alert History

```bash
cd ~/.openclaw/workspace/diagnostics
./alert-notifications.sh history
```

Alerts are logged to: `~/.openclaw/alerts.log`

## Clearing Alert History

```bash
cd ~/.openclaw/workspace/diagnostics
./alert-notifications.sh clear
```

## Integration with Health Monitor

The alert system can be integrated with `health-monitor-automated.sh`:

```bash
# Add to health-monitor-automated.sh
source ~/.openclaw/workspace/diagnostics/alert-notifications.sh

# Then use alert functions
if systemctl is-inactive --quiet openclaw-gateway; then
    alert_gateway_down
fi
```

## Alert Levels

The system supports three alert levels:

1. **ERROR** (`LEVEL_ERROR=1`) - Critical issues
2. **WARNING** (`LEVEL_WARNING=2`) - Potential issues
3. **INFO** (`LEVEL_INFO=3`) - Informational messages

## Available Alert Functions

```bash
alert_gateway_down           # Gateway is not running
alert_high_memory <usage>    # High memory usage (percentage)
alert_api_failure            # LLM API not responding
alert_error_spike <count>    # High error rate
```

## Custom Alerts

You can create custom alert functions in the script:

```bash
alert_custom_issue() {
    local details=$1
    send_alert $LEVEL_WARNING "Custom issue: $details"
}

# Usage
alert_custom_issue "Disk usage is above 90%"
```

## Setting Up Automated Alerts

### Method 1: Cron Job

```bash
# Add to crontab
crontab -e

# Check health every 30 minutes and send alerts
*/30 * * * * cd ~/.openclaw/workspace/diagnostics && ./health-monitor-automated.sh
```

### Method 2: Systemd Service

Create `/etc/systemd/system/openclaw-alerts.service`:

```ini
[Unit]
Description=OpenClaw Health Monitor
After=openclaw-gateway.service

[Service]
Type=oneshot
User=openclaw
WorkingDirectory=/home/openclaw/.openclaw/workspace/diagnostics
ExecStart=/home/openclaw/.openclaw/workspace/diagnostics/health-monitor-automated.sh

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/openclaw-alerts.timer`:

```ini
[Unit]
Description=Run OpenClaw health monitor every 30 minutes

[Timer]
OnCalendar=*:0/30
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl enable openclaw-alerts.timer
sudo systemctl start openclaw-alerts.timer
```

## Troubleshooting

### Email Not Sending

Check if `mail` is installed:
```bash
which mail
```

If not installed:
```bash
sudo apt-get install mailutils  # Ubuntu/Debian
sudo yum install mailx          # CentOS/RHEL
```

Test SMTP:
```bash
echo "Test" | mail -s "Test Subject" your-email@example.com
```

### Slack Webhook Not Working

Test webhook directly:
```bash
curl -X POST "YOUR_WEBHOOK_URL" \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test message"}'
```

### Telegram Not Working

Test bot token:
```bash
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getMe"
```

Test sending message:
```bash
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/sendMessage?chat_id=YOUR_CHAT_ID&text=Test"
```

## Best Practices

1. **Test alerts before relying on them**
   ```bash
   ./alert-notifications.sh test
   ```

2. **Start with log alerts only**
   ```bash
   ALERT_METHOD="log"
   ```

3. **Gradually enable more aggressive alerting**
   - Start with ERROR level only
   - Add WARNING level after testing
   - Add INFO level for comprehensive monitoring

4. **Monitor alert history regularly**
   ```bash
   ./alert-notifications.sh history
   ```

5. **Don't alert on non-critical issues**
   - Use appropriate alert levels
   - Avoid alert fatigue

6. **Set up escalation procedures**
   - Define what to do when alerts fire
   - Document response procedures

## Example Configuration

### Minimal Configuration (Log Only)
```bash
ALERT_METHOD="log"
```

### Email Configuration
```bash
ALERT_METHOD="email"
ALERT_EMAIL="admin@example.com"
```

### Slack Configuration
```bash
ALERT_METHOD="slack"
SLACK_WEBHOOK="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
```

### Telegram Configuration
```bash
ALERT_METHOD="telegram"
TELEGRAM_BOT="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
TELEGRAM_CHAT="123456789"
```

## Support

For issues with alerts:
1. Check alert history: `./alert-notifications.sh history`
2. Test alert system: `./alert-notifications.sh test`
3. Review configuration in the script
4. Consult main documentation: `cat TROUBLESHOOTING.md`

---

*Last updated: 2026-05-21*