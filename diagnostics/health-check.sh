#!/bin/bash
# Health monitoring script for OpenClaw
# Run this periodically to check system health

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1"
    fi
}

warn_status() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo "=========================================="
echo "OpenClaw Health Check"
echo "=========================================="
echo "Time: $(date)"
echo ""

# 1. Gateway Status
echo "[1] Gateway Status"
systemctl is-active openclaw-gateway && check_status "Gateway is running" || check_status "Gateway is NOT running"

# 2. Memory Usage
echo -e "\n[2] Memory Usage"
MEM_USAGE=$(free | awk '/Mem/{printf "%.1f", $3/$2 * 100.0}')
MEM_AVAIL=$(free -h | awk '/Mem/{print $7}')
echo "  Used: $MEM_USAGE%"
echo "  Available: $MEM_AVAIL"

if (( $(echo "$MEM_USAGE > 80" | bc -l) )); then
    warn_status "Memory usage above 80%"
fi

# 3. CPU Usage
echo -e "\n[3] CPU Usage"
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
echo "  CPU: ${CPU_USAGE}%"

if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    warn_status "CPU usage above 80%"
fi

# 4. Disk Usage
echo -e "\n[4] Disk Usage"
DISK_USAGE=$(df -h / | awk 'NR==2{print $5}' | tr -d '%')
echo "  Root: ${DISK_USAGE}%"

if [ "$DISK_USAGE" -gt 80 ]; then
    warn_status "Disk usage above 80%"
fi

# 5. LLM API Health
echo -e "\n[5] LLM API Health"
if [ -n "$API_HUB_KEY" ]; then
    API_RESPONSE=$(curl -s -w "\n%{http_code}" http://10.1.160.84:9527/health)
    API_CODE=$(echo "$API_RESPONSE" | tail -1)
    if [ "$API_CODE" = "200" ]; then
        check_status "LLM API responding (HTTP 200)"
    else
        check_status "LLM API not responding (HTTP $API_CODE)"
    fi
else
    echo "  ⚠ API_HUB_KEY not set, skipping test"
fi

# 6. Recent Errors
echo -e "\n[6] Recent Errors (last 5 minutes)"
ERROR_COUNT=$(journalctl -u openclaw-gateway --since "5 minutes ago" | grep -i error | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    check_status "No errors in last 5 minutes"
else
    warn_status "$ERROR_COUNT errors in last 5 minutes"
fi

# 7. Session Files
echo -e "\n[7] Session Files"
SESSION_COUNT=$(find ~/.openclaw/sessions -name "*.jsonl" 2>/dev/null | wc -l)
echo "  Total sessions: $SESSION_COUNT"

# 8. Background Processes
echo -e "\n[8] Background Processes"
MONITOR_COUNT=$(ps aux | grep -E '(auto-monitor|continuous-trading-monitor)' | grep -v grep | wc -l)
if [ "$MONITOR_COUNT" -eq 0 ]; then
    check_status "No trading monitors running"
else
    warn_status "$MONITOR_COUNT trading monitor(s) running"
fi

# 9. Network Connectivity
echo -e "\n[9] Network Connectivity"
curl -s --connect-timeout 2 http://10.1.160.84:9527/health > /dev/null && check_status "Can reach LLM API" || check_status "Cannot reach LLM API"

# 10. Gateway Process
echo -e "\n[10] Gateway Process"
if pgrep -f "openclaw-gateway" > /dev/null; then
    GATEWAY_PID=$(pgrep -f "openclaw-gateway")
    GATEWAY_MEM=$(ps -p "$GATEWAY_PID" -o rss= | awk '{print int($1/1024)"MB"}')
    check_status "Gateway process running (PID $GATEWAY_PID, $GATEWAY_MEM)"
else
    check_status "Gateway process not found"
fi

echo ""
echo "=========================================="
echo "Health Check Complete"
echo "=========================================="