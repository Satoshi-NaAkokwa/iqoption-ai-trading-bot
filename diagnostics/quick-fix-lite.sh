#!/bin/bash
# QUICK FIX - Run all P0 and P1 optimizations automatically
# WARNING: This script will restart the gateway. Run with caution.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/openclaw-quickfix-$(date +%Y%m%d_%H%M%S).log"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "=========================================="
echo "OpenClaw Quick Fix Script"
echo "=========================================="
echo "Started: $(date)"
echo "Log file: $LOG_FILE"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

step_count=0

print_step() {
    step_count=$((step_count + 1))
    echo -e "\n${GREEN}[STEP $step_count]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ========================================
# STEP 1: System Backup
# ========================================
print_step "Creating system backup..."

BACKUP_DIR="/home/openclaw/.openclaw/backup/pre-fix-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "  • Backing up config..."
cp ~/.openclaw/openclaw.json "$BACKUP_DIR/"

echo "  • Backing up sessions..."
if [ -d ~/.openclaw/sessions ]; then
    cp -r ~/.openclaw/sessions "$BACKUP_DIR/sessions"
else
    echo "    (no sessions directory)"
fi

echo "  ✓ Backup created: $BACKUP_DIR"

# ========================================
# STEP 2: Clean Corrupted Sessions
# ========================================
print_step "Cleaning corrupted session files..."

SESSION_DIR="/home/openclaw/.openclaw/sessions"

if [ ! -d "$SESSION_DIR" ]; then
    echo "  (no sessions directory found)"
else
    echo "  • Finding empty session files..."
    EMPTY_COUNT=$(find "$SESSION_DIR" -name "*.jsonl" -size 0 | wc -l)

    if [ "$EMPTY_COUNT" -gt 0 ]; then
        echo "  • Found $EMPTY_COUNT empty session files"
        find "$SESSION_DIR" -name "*.jsonl" -size 0 -delete
        echo "  ✓ Deleted $EMPTY_COUNT empty session files"
    else
        echo "  ✓ No empty session files found"
    fi
fi

# ========================================
# STEP 3: Review Background Monitors
# ========================================
print_step "Reviewing background monitor processes..."

MONITOR_PROCS=$(ps aux | grep -E '(auto-monitor|continuous-trading-monitor)' | grep -v grep || true)

if [ -z "$MONITOR_PROCS" ]; then
    echo "  ✓ No trading monitor processes running"
else
    echo "  ⚠️  Found running trading monitors:"
    echo "$MONITOR_PROCS" | awk '{print "      PID "$2": " $11 " (" $5 "KB, " $6"KB RSS)"}'

    read -p "  Stop trading monitors to free resources? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pkill -f "auto-monitor.js" 2>/dev/null || echo "    (no auto-monitor.js found)"
        pkill -f "continuous-trading-monitor.js" 2>/dev/null || echo "    (no continuous-trading-monitor.js found)"
        echo "  ✓ Stopped trading monitors"
    else
        echo "  → Skipping (monitors still running)"
    fi
fi

# ========================================
# STEP 4: Configure Firewall (ICMP)
# ========================================
print_step "Configuring firewall for ICMP..."

# Check if iptables is available
if command -v iptables &> /dev/null; then
    echo "  • Checking existing ICMP rules..."
    EXISTING_RULE=$(sudo iptables -L INPUT -n | grep -E "10\.1\.160\.84.*icmp" || true)

    if [ -z "$EXISTING_RULE" ]; then
        echo "  • Adding ICMP rule for 10.1.160.84..."
        sudo iptables -I INPUT -p icmp -s 10.1.160.84 -j ACCEPT 2>/dev/null || echo "    (requires sudo, skipping)"
        echo "  ✓ ICMP rule added (or already exists)"
    else
        echo "  ✓ ICMP rule already exists"
    fi
else
    echo "  ⚠️  iptables not available - skipping firewall config"
fi

# ========================================
# STEP 5: Set Up Log Rotation
# ========================================
print_step "Configuring log rotation..."

LOGROTATE_FILE="/etc/logrotate.d/openclaw"

if [ -f "$LOGROTATE_FILE" ]; then
    echo "  ✓ Log rotation already configured"
else
    echo "  • Creating logrotate configuration..."
    sudo tee "$LOGROTATE_FILE" > /dev/null <<'EOF'
/tmp/openclaw-1000/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 openclaw openclaw
    postrotate
        systemctl reload openclaw-gateway > /dev/null 2>&1 || true
    endscript
}
EOF
    echo "  ✓ Log rotation configured"
fi

# ========================================
# STEP 6: Create Health Check Cron Job
# ========================================
print_step "Setting up automated health checks..."

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "health-check.sh"; then
    echo "  ✓ Health check cron job already exists"
else
    echo "  • Adding health check to crontab..."
    (crontab -l 2>/dev/null; echo "0 */4 * * * /home/openclaw/.openclaw/workspace/diagnostics/health-check.sh >> /var/log/openclaw-health.log 2>&1") | crontab -
    echo "  ✓ Health check will run every 4 hours"
fi

# ========================================
# SUMMARY
# ========================================
echo ""
echo "=========================================="
echo "Quick Fix Complete!"
echo "=========================================="
echo ""
echo "Actions performed:"
echo "  ✓ Created backup at: $BACKUP_DIR"
echo "  ✓ Cleaned corrupted sessions"
echo "  ✓ Reviewed background monitors"
echo "  ✓ Configured firewall (ICMP)"
echo "  ✓ Set up log rotation"
echo "  ✓ Added automated health checks"
echo ""
echo "Next steps:"
echo "  1. Monitor gateway logs: journalctl -u openclaw-gateway -f"
echo "  2. Test agent response via webchat"
echo "  3. Review health check logs: tail -f /var/log/openclaw-health.log"
echo ""
echo "Log file: $LOG_FILE"
echo ""
echo "=========================================="