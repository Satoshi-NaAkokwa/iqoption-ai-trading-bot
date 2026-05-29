#!/bin/bash
# AUTOMATED HEALTH MONITOR - Run comprehensive checks and alert on issues

set -e

ALERT_EMAIL=""  # Set your email for alerts
ALERT_THRESHOLD_MEMORY=80  # Alert if memory > 80%
ALERT_THRESHOLD_CPU=90    # Alert if CPU > 90%
ALERT_THRESHOLD_ERRORS=10 # Alert if errors > 10 in 5 min

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

ISSUES_FOUND=0

alert() {
    local message="$1"
    echo -e "${RED}⚠ ALERT: $message${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))

    # Send email if configured
    if [ -n "$ALERT_EMAIL" ]; then
        echo "Subject: OpenClaw Alert - $message" | \
            mail -s "OpenClaw Alert - $message" "$ALERT_EMAIL" 2>/dev/null || true
    fi
}

warning() {
    local message="$1"
    echo -e "${YELLOW}⚠ WARNING: $message${NC}"
}

success() {
    local message="$1"
    echo -e "${GREEN}✓ $message${NC}"
}

info() {
    local message="$1"
    echo -e "${BLUE}ℹ $message${NC}"
}

print_header() {
    clear
    cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║         OpenClaw Automated Health Monitor                      ║
╚════════════════════════════════════════════════════════════════╝

EOF
}

check_gateway() {
    echo -e "${BLUE}Checking Gateway Status...${NC}"

    if systemctl is-active --quiet openclaw-gateway; then
        success "Gateway is running"
    else
        alert "Gateway is not running!"
    fi
}

check_memory() {
    echo ""
    echo -e "${BLUE}Checking Memory Usage...${NC}"

    MEMORY_PERCENT=$(free | awk 'NR==2{printf "%.1f", $3/$2*100}')
    MEMORY_AVAILABLE=$(free -h | awk 'NR==2{print $7}')

    echo "  Memory Usage: $MEMORY_PERCENT% ($MEMORY_AVAILABLE available)"

    if (( $(echo "$MEMORY_PERCENT > $ALERT_THRESHOLD_MEMORY" | bc -l) )); then
        alert "Memory usage is above threshold ($MEMORY_PERCENT% > ${ALERT_THRESHOLD_MEMORY}%)"
    elif (( $(echo "$MEMORY_PERCENT > 60" | bc -l) )); then
        warning "Memory usage is elevated ($MEMORY_PERCENT%)"
    else
        success "Memory usage is normal"
    fi
}

check_cpu() {
    echo ""
    echo -e "${BLUE}Checking CPU Usage...${NC}"

    CPU_PERCENT=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)

    echo "  CPU Usage: $CPU_PERCENT%"

    if (( $(echo "$CPU_PERCENT > $ALERT_THRESHOLD_CPU" | bc -l) )); then
        alert "CPU usage is above threshold ($CPU_PERCENT% > ${ALERT_THRESHOLD_CPU}%)"
    elif (( $(echo "$CPU_PERCENT > 50" | bc -l) )); then
        warning "CPU usage is elevated ($CPU_PERCENT%)"
    else
        success "CPU usage is normal"
    fi
}

check_disk() {
    echo ""
    echo -e "${BLUE}Checking Disk Usage...${NC}"

    DISK_PERCENT=$(df -h / | awk 'NR==2{print $5}' | sed 's/%//')

    echo "  Disk Usage: $DISK_PERCENT%"

    if [ "$DISK_PERCENT" -gt 90 ]; then
        alert "Disk usage is critical ($DISK_PERCENT%)"
    elif [ "$DISK_PERCENT" -gt 80 ]; then
        warning "Disk usage is elevated ($DISK_PERCENT%)"
    else
        success "Disk usage is normal"
    fi
}

check_api() {
    echo ""
    echo -e "${BLUE}Checking LLM API Health...${NC}"

    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 https://api.openai.com/v1/models 2>/dev/null || echo "000")

    if [ "$HTTP_STATUS" = "200" ]; then
        success "LLM API is responding (HTTP 200)"
    else
        alert "LLM API is not responding (HTTP $HTTP_STATUS)"
    fi
}

check_errors() {
    echo ""
    echo -e "${BLUE}Checking Recent Errors...${NC}"

    ERRORS=$(journalctl -u openclaw-gateway --since "5 minutes ago" 2>/dev/null | grep -i error | wc -l)

    echo "  Errors in last 5 minutes: $ERRORS"

    if [ "$ERRORS" -gt "$ALERT_THRESHOLD_ERRORS" ]; then
        alert "High error rate detected ($ERRORS errors in 5 minutes)"
    elif [ "$ERRORS" -gt 5 ]; then
        warning "Elevated error rate ($ERRORS errors in 5 minutes)"
    else
        success "Error rate is normal"
    fi
}

check_sessions() {
    echo ""
    echo -e "${BLUE}Checking Session Files...${NC}"

    SESSION_COUNT=$(ls -1 ~/.openclaw/agents/main/sessions/*.jsonl 2>/dev/null | wc -l)

    echo "  Session files: $SESSION_COUNT"

    if [ "$SESSION_COUNT" -gt 100 ]; then
        warning "High number of session files ($SESSION_COUNT)"
    else
        success "Session count is normal"
    fi
}

check_network() {
    echo ""
    echo -e "${BLUE}Checking Network Connectivity...${NC}"

    if ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1; then
        success "Network connectivity is working"
    else
        warning "Network connectivity issues detected"
    fi
}

check_monitors() {
    echo ""
    echo -e "${BLUE}Checking Background Processes...${NC}"

    MONITOR_COUNT=$(pgrep -f -E '(auto-monitor|trading-monitor)' | wc -l)

    echo "  Background monitors: $MONITOR_COUNT"

    if [ "$MONITOR_COUNT" -gt 5 ]; then
        warning "High number of background monitors running ($MONITOR_COUNT)"
    else
        info "Background monitors: $MONITOR_COUNT"
    fi
}

print_summary() {
    echo ""
    echo "═════════════════════════════════════════════════════════════════"
    echo ""
    echo -e "${BLUE}Health Check Summary${NC}"
    echo ""

    if [ $ISSUES_FOUND -eq 0 ]; then
        echo -e "${GREEN}✓ No issues found - System is healthy${NC}"
    elif [ $ISSUES_FOUND -eq 1 ]; then
        echo -e "${YELLOW}⚠ 1 issue found${NC}"
    else
        echo -e "${RED}⚠ $ISSUES_FOUND issues found${NC}"
    fi

    echo ""
    echo "Timestamp: $(date)"
    echo ""

    if [ $ISSUES_FOUND -gt 0 ]; then
        echo "Recommendations:"
        echo "  1. Review the alerts above"
        echo "  2. Run full diagnostics: cd ~/.openclaw/workspace/diagnostics && ./menu.sh"
        echo "  3. Check logs: journalctl -u openclaw-gateway -f"
        echo ""
    fi
}

# Main execution
print_header
check_gateway
check_memory
check_cpu
check_disk
check_api
check_errors
check_sessions
check_network
check_monitors
print_summary

# Exit code
if [ $ISSUES_FOUND -eq 0 ]; then
    exit 0
else
    exit 1
fi