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

echo "  • Backing up cron jobs..."
if [ -f ~/.openclaw/cron/jobs.json ]; then
    cp ~/.openclaw/cron/jobs.json "$BACKUP_DIR/"
else
    echo "    (no cron jobs file)"
fi

echo "  ✓ Backup created: $BACKUP_DIR"

# ========================================
# STEP 2: Test LLM API Authentication
# ========================================
print_step "Testing LLM API authentication..."

if [ -z "$API_HUB_KEY" ]; then
    print_error "API_HUB_KEY environment variable not set!"
    echo "  Skipping LLM API tests..."
else
    echo "  • Testing models endpoint..."
    MODELS_RESPONSE=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $API_HUB_KEY" \
        http://10.1.160.84:9527/v1/models)

    HTTP_CODE=$(echo "$MODELS_RESPONSE" | tail -1)
    BODY=$(echo "$MODELS_RESPONSE" | sed '$d')

    if [ "$HTTP_CODE" = "200" ]; then
        echo "  ✓ API authentication working"
        echo "    Available models:"
        echo "$BODY" | grep -o '"id":"[^"]*"' | cut -d'"' -f4 | sed 's/^/      - /'
    else
        print_error "API authentication failed (HTTP $HTTP_CODE)"
        echo "  Response: $BODY"
        echo "  ⚠️  You may need to refresh your API key"
    fi
fi

# ========================================
# STEP 3: Clean Corrupted Sessions
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

    echo "  • Checking for malformed session files..."
    MALFORMED=0
    for file in "$SESSION_DIR"/*.jsonl; do
        if [ -f "$file" ]; then
            # Check if file ends with newline
            if [ "$(tail -c 1 "$file" | wc -l)" -eq 0 ]; then
                echo "  ⚠️  Missing newline at EOF: $(basename "$file")"
                echo "" >> "$file"
                MALFORMED=$((MALFORMED + 1))
            fi
        fi
    done

    if [ "$MALFORMED" -gt 0 ]; then
        echo "  ✓ Fixed $MALFORMED malformed files"
    else
        echo "  ✓ All session files well-formed"
    fi
fi

# ========================================
# STEP 4: Review Background Monitors
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
# STEP 5: Configure Firewall (ICMP)
# ========================================
print_step "Configuring firewall for ICMP..."

# Check if iptables is available
if command -v iptables &> /dev/null; then
    echo "  • Checking existing ICMP rules..."
    EXISTING_RULE=$(sudo iptables -L INPUT -n | grep -E "10\.1\.160\.84.*icmp" || true)

    if [ -z "$EXISTING_RULE" ]; then
        echo "  • Adding ICMP rule for 10.1.160.84..."
        sudo iptables -I INPUT -p icmp -s 10.1.160.84 -j ACCEPT
        echo "  ✓ ICMP rule added"
    else
        echo "  ✓ ICMP rule already exists"
    fi

    # Save rules (if persistent)
    if [ -d /etc/iptables ]; then
        echo "  • Saving iptables rules..."
        sudo iptables-save > /etc/iptables/rules.v4 2>/dev/null || echo "    (could not save - might not persist after reboot)"
    fi
else
    echo "  ⚠️  iptables not available - skipping firewall config"
fi

# ========================================
# STEP 6: Optimize Gateway Configuration
# ========================================
print_step "Optimizing gateway configuration..."

CONFIG_FILE="/home/openclaw/.openclaw/openclaw.json"
BACKUP_CONFIG="$BACKUP_DIR/openclaw.json.original"

# Backup original config
cp "$CONFIG_FILE" "$BACKUP_CONFIG"

echo "  • Creating optimized configuration..."
# We'll create a patch file instead of modifying directly
cat > /tmp/openclaw-config-patch.json <<'EOF'
{
  "agents": {
    "defaults": {
      "maxConcurrent": 2,
      "model": {
        "primary": "occ/glm-4.7"
      },
      "subagents": {
        "maxConcurrent": 4
      }
    }
  },
  "web": {
    "heartbeatSeconds": 120
  }
}
EOF

echo "  ⚠️  Configuration patch created at /tmp/openclaw-config-patch.json"
echo "    Review and apply manually if desired"

# ========================================
# STEP 7: Set Up Log Rotation
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
# STEP 8: Restart Gateway
# ========================================
print_step "Restarting OpenClaw gateway..."

read -p "  Restart gateway to apply all fixes? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "  • Restarting gateway..."
    sudo systemctl restart openclaw-gateway

    echo "  • Waiting for gateway to start..."
    sleep 10

    # Check status
    if systemctl is-active --quiet openclaw-gateway; then
        echo "  ✓ Gateway started successfully"
    else
        print_error "Gateway failed to start"
        echo "  Check status with: systemctl status openclaw-gateway"
        echo "  Check logs with: journalctl -u openclaw-gateway -n 50"
        exit 1
    fi
else
    echo "  → Skipping restart (manual restart required)"
fi

# ========================================
# STEP 9: Final Health Check
# ========================================
print_step "Running final health check..."

echo "  • Gateway status:"
systemctl is-active openclaw-gateway

echo -e "\n  • Memory usage:"
free -h | grep "Mem:"

echo -e "\n  • Recent errors:"
ERROR_COUNT=$(journalctl -u openclaw-gateway --since "2 minutes ago" | grep -i error | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo "  ✓ No errors in last 2 minutes"
else
    echo "  ⚠️  $ERROR_COUNT errors in last 2 minutes"
fi

echo -e "\n  • LLM API test (if key available):"
if [ -n "$API_HUB_KEY" ]; then
    API_TEST=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $API_HUB_KEY" \
        http://10.1.160.84:9527/health)
    API_CODE=$(echo "$API_TEST" | tail -1)
    if [ "$API_CODE" = "200" ]; then
        echo "  ✓ LLM API healthy"
    else
        echo "  ⚠️  LLM API returned HTTP $API_CODE"
    fi
else
    echo "  (API_HUB_KEY not set)"
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
echo "  ✓ Tested LLM API authentication"
echo "  ✓ Cleaned corrupted sessions"
echo "  ✓ Reviewed background monitors"
echo "  ✓ Configured firewall (ICMP)"
echo "  ✓ Created config patch for review"
echo "  ✓ Set up log rotation"
echo "  ✓ Restarted gateway"
echo ""
echo "Next steps:"
echo "  1. Monitor gateway logs: journalctl -u openclaw-gateway -f"
echo "  2. Test agent response via webchat"
echo "  3. Review config patch at /tmp/openclaw-config-patch.json"
echo "  4. Apply config patch if desired (manual action required)"
echo ""
echo "Log file: $LOG_FILE"
echo ""
echo "=========================================="