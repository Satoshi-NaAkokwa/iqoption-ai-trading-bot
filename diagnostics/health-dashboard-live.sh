#!/bin/bash
# SYSTEM HEALTH DASHBOARD - Real-time system health display

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

clear

while true; do
    clear

    cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║              OpenClaw System Health Dashboard                   ║
╚══════════════════════════════════════════════════════════════╝

EOF

    echo -e "${CYAN}System Health Overview${NC}"
    echo ""

    # Gateway Status
    GATEWAY_STATUS=$(systemctl is-active openclaw-gateway 2>/dev/null || echo "unknown")
    if [ "$GATEWAY_STATUS" = "active" ]; then
        echo -e "${GREEN}✅ Gateway Status:${NC}        Active"
    else
        echo -e "${RED}✗ Gateway Status:${NC}        Inactive"
    fi

    # Memory Usage
    MEMORY_PERCENT=$(free | awk 'NR==2{printf "%.1f", $3/$2*100}')
    MEMORY_AVAILABLE=$(free -h | awk 'NR==2{print $7}')
    if (( $(echo "$MEMORY_PERCENT < 50" | bc -l) )); then
        COLOR="$GREEN"
    elif (( $(echo "$MEMORY_PERCENT < 80" | bc -l) )); then
        COLOR="$YELLOW"
    else
        COLOR="$RED"
    fi
    echo -e "${COLOR}✓ Memory Usage:${NC}           $MEMORY_PERCENT% ($MEMORY_AVAILABLE available)"

    # CPU Usage
    CPU_PERCENT=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    if (( $(echo "$CPU_PERCENT < 50" | bc -l) )); then
        COLOR="$GREEN"
    elif (( $(echo "$CPU_PERCENT < 90" | bc -l) )); then
        COLOR="$YELLOW"
    else
        COLOR="$RED"
    fi
    echo -e "${COLOR}✓ CPU Usage:${NC}              $CPU_PERCENT%"

    # Disk Usage
    DISK_PERCENT=$(df -h / | awk 'NR==2{print $5}' | sed 's/%//')
    if [ "$DISK_PERCENT" -lt 80 ]; then
        COLOR="$GREEN"
    elif [ "$DISK_PERCENT" -lt 90 ]; then
        COLOR="$YELLOW"
    else
        COLOR="$RED"
    fi
    echo -e "${COLOR}✓ Disk Usage:${NC}             $DISK_PERCENT%"

    # API Status
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 https://api.openai.com/v1/models 2>/dev/null || echo "000")
    if [ "$HTTP_STATUS" = "200" ]; then
        echo -e "${GREEN}✓ LLM API Health:${NC}        200 OK"
    else
        echo -e "${RED}✗ LLM API Health:${NC}        $HTTP_STATUS"
    fi

    # Recent Errors
    ERRORS=$(journalctl -u openclaw-gateway --since "5 minutes ago" 2>/dev/null | grep -i error | wc -l)
    if [ "$ERRORS" -eq 0 ]; then
        echo -e "${GREEN}✓ Recent Errors:${NC}        0 in last 5 min"
    else
        echo -e "${YELLOW}⚠ Recent Errors:${NC}        $ERRORS in last 5 min"
    fi

    # Session Files
    SESSION_COUNT=$(ls -1 ~/.openclaw/agents/main/sessions/*.jsonl 2>/dev/null | wc -l)
    echo -e "${BLUE}ℹ Session Files:${NC}         $SESSION_COUNT"

    # Background Processes
    MONITOR_COUNT=$(pgrep -f -E '(auto-monitor|trading-monitor)' | wc -l)
    echo -e "${BLUE}ℹ Background Monitors:${NC}   $MONITOR_COUNT"

    # Load Average
    LOAD_1MIN=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}')
    echo -e "${BLUE}ℹ Load Average (1m):${NC}     $LOAD_1MIN"

    # Network Status
    if ping -c 1 -W 1 8.8.8.8 >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Network Connectivity:${NC}  Working"
    else
        echo -e "${RED}✗ Network Connectivity:${NC}  Issues detected"
    fi

    # Calculate Overall Health Score
    SCORE=100

    # Gateway (20 points)
    if [ "$GATEWAY_STATUS" != "active" ]; then
        SCORE=$((SCORE - 20))
    fi

    # Memory (20 points)
    if (( $(echo "$MEMORY_PERCENT > 80" | bc -l) )); then
        SCORE=$((SCORE - 20))
    elif (( $(echo "$MEMORY_PERCENT > 50" | bc -l) )); then
        SCORE=$((SCORE - 10))
    fi

    # CPU (15 points)
    if (( $(echo "$CPU_PERCENT > 90" | bc -l) )); then
        SCORE=$((SCORE - 15))
    elif (( $(echo "$CPU_PERCENT > 50" | bc -l) )); then
        SCORE=$((SCORE - 7))
    fi

    # Disk (15 points)
    if [ "$DISK_PERCENT" -gt 90 ]; then
        SCORE=$((SCORE - 15))
    elif [ "$DISK_PERCENT" -gt 80 ]; then
        SCORE=$((SCORE - 7))
    fi

    # API (15 points)
    if [ "$HTTP_STATUS" != "200" ]; then
        SCORE=$((SCORE - 15))
    fi

    # Errors (15 points)
    if [ "$ERRORS" -gt 10 ]; then
        SCORE=$((SCORE - 15))
    elif [ "$ERRORS" -gt 5 ]; then
        SCORE=$((SCORE - 7))
    fi

    echo ""
    echo "═════════════════════════════════════════════════════════════════"
    echo ""
    echo -e "${CYAN}Overall Health Score:${NC}"
    echo ""

    if [ $SCORE -ge 90 ]; then
        echo -e "${GREEN}🎉 $SCORE/100 - EXCELLENT${NC}"
    elif [ $SCORE -ge 70 ]; then
        echo -e "${YELLOW}⚠ $SCORE/100 - GOOD${NC}"
    elif [ $SCORE -ge 50 ]; then
        echo -e "${YELLOW}⚠ $SCORE/100 - FAIR${NC}"
    else
        echo -e "${RED}❌ $SCORE/100 - POOR${NC}"
    fi

    echo ""
    echo -e "${BLUE}Timestamp:${NC} $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo -e "${BLUE}Refreshing in 10 seconds... (Press Ctrl+C to exit)${NC}"

    sleep 10
done