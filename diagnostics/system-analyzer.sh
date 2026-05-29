#!/bin/bash
# SYSTEM ANALYZER - Deep system analysis with recommendations

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

RECOMMENDATIONS=0

clear

cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║              OpenClaw Deep System Analyzer                     ║
╚════════════════════════════════════════════════════════════════╝

EOF

echo -e "${CYAN}Performing Deep System Analysis...${NC}"
echo ""

# 1. Gateway Analysis
echo -e "${BLUE}[1/10] Gateway Analysis...${NC}"
GATEWAY_STATUS=$(systemctl is-active openclaw-gateway 2>/dev/null || echo "unknown")
GATEWAY_PID=$(pgrep -f openclaw-gateway | head -1)

if [ "$GATEWAY_STATUS" = "active" ]; then
    echo -e "  ${GREEN}✓ Gateway is running${NC}"
    echo -e "  PID: $GATEWAY_PID"
    echo -e "  Uptime: $(systemctl show openclaw-gateway -p ActiveEnterTimestampMonotonic | cut -d= -f2 | awk '{printf "%.0f hours", $1/3600000000}')"
else
    echo -e "  ${RED}✗ Gateway is not running${NC}"
    echo -e "  ${YELLOW}Recommendation: Start the gateway${NC}"
    RECOMMENDATIONS=$((RECOMMENDATIONS + 1))
fi

# 2. Memory Analysis
echo ""
echo -e "${BLUE}[2/10] Memory Analysis...${NC}"
MEMORY_TOTAL=$(free | awk 'NR==2{print $2}')
MEMORY_USED=$(free | awk 'NR==2{print $3}')
MEMORY_PERCENT=$(free | awk 'NR==2{printf "%.1f", $3/$2*100}')
MEMORY_AVAILABLE=$(free -h | awk 'NR==2{print $7}')

echo -e "  Total: $(free -h | awk 'NR==2{print $2}')"
echo -e "  Used: $(free -h | awk 'NR==2{print $3}') ($MEMORY_PERCENT%)"
echo -e "  Available: $MEMORY_AVAILABLE"

if (( $(echo "$MEMORY_PERCENT > 80" | bc -l) )); then
    echo -e "  ${RED}⚠ High memory usage detected${NC}"
    echo -e "  ${YELLOW}Recommendation: Stop unnecessary background processes${NC}"
    RECOMMENDATIONS=$((RECOMMENDATIONS + 1))
elif (( $(echo "$MEMORY_PERCENT > 50" | bc -l) )); then
    echo -e "  ${YELLOW}⚠ Memory usage is elevated${NC}"
fi

# 3. CPU Analysis
echo ""
echo -e "${BLUE}[3/10] CPU Analysis...${NC}"
CPU_PERCENT=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
CPU_CORES=$(nproc)
LOAD_1MIN=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}')
LOAD_5MIN=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $2}')

echo -e "  CPU Usage: $CPU_PERCENT%"
echo -e "  CPU Cores: $CPU_CORES"
echo -e "  Load Average (1m): $LOAD_1MIN"
echo -e "  Load Average (5m): $LOAD_5MIN"

if (( $(echo "$CPU_PERCENT > 90" | bc -l) )); then
    echo -e "  ${RED}⚠ High CPU usage detected${NC}"
    echo -e "  ${YELLOW}Recommendation: Check for runaway processes${NC}"
    RECOMMENDATIONS=$((RECOMMENDATIONS + 1))
elif (( $(echo "$CPU_PERCENT > 50" | bc -l) )); then
    echo -e "  ${YELLOW}⚠ CPU usage is elevated${NC}"
fi

# 4. Disk Analysis
echo ""
echo -e "${BLUE}[4/10] Disk Analysis...${NC}"
DISK_PERCENT=$(df -h / | awk 'NR==2{print $5}' | sed 's/%//')
DISK_AVAILABLE=$(df -h / | awk 'NR==2{print $4}')
DISK_USED=$(df -h / | awk 'NR==2{print $3}')
DISK_TOTAL=$(df -h / | awk 'NR==2{print $2}')

echo -e "  Disk Usage: $DISK_PERCENT%"
echo -e "  Used: $DISK_USED / $DISK_TOTAL"
echo -e "  Available: $DISK_AVAILABLE"

if [ "$DISK_PERCENT" -gt 90 ]; then
    echo -e "  ${RED}⚠ Critical disk usage${NC}"
    echo -e "  ${YELLOW}Recommendation: Clean up old files and logs${NC}"
    RECOMMENDATIONS=$((RECOMMENDATIONS + 1))
elif [ "$DISK_PERCENT" -gt 80 ]; then
    echo -e "  ${YELLOW}⚠ Disk usage is elevated${NC}"
fi

# 5. API Analysis
echo ""
echo -e "${BLUE}[5/10] LLM API Analysis...${NC}"
API_START=$(date +%s%N)
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 https://api.openai.com/v1/models 2>/dev/null || echo "000")
API_END=$(date +%s%N)
API_LATENCY=$(( (API_END - API_START) / 1000000 ))

echo -e "  Status Code: $HTTP_STATUS"
echo -e "  Latency: ${API_LATENCY}ms"

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "  ${GREEN}✓ API is responding${NC}"
    if [ $API_LATENCY -gt 1000 ]; then
        echo -e "  ${YELLOW}⚠ High latency detected${NC}"
        echo -e "  ${YELLOW}Recommendation: Check network connectivity${NC}"
    fi
else
    echo -e "  ${RED}✗ API is not responding${NC}"
    echo -e "  ${YELLOW}Recommendation: Check API key and network${NC}"
    RECOMMENDATIONS=$((RECOMMENDATIONS + 1))
fi

# 6. Error Analysis
echo ""
echo -e "${BLUE}[6/10] Error Analysis...${NC}"
ERRORS_5MIN=$(journalctl -u openclaw-gateway --since "5 minutes ago" 2>/dev/null | grep -i error | wc -l)
ERRORS_1HOUR=$(journalctl -u openclaw-gateway --since "1 hour ago" 2>/dev/null | grep -i error | wc -l)
ERRORS_24HOURS=$(journalctl -u openclaw-gateway --since "24 hours ago" 2>/dev/null | grep -i error | wc -l)

echo -e "  Errors (5 min): $ERRORS_5MIN"
echo -e "  Errors (1 hour): $ERRORS_1HOUR"
echo -e "  Errors (24 hours): $ERRORS_24HOURS"

if [ "$ERRORS_5MIN" -gt 10 ]; then
    echo -e "  ${RED}⚠ High error rate${NC}"
    echo -e "  ${YELLOW}Recommendation: Check logs for error patterns${NC}"
    RECOMMENDATIONS=$((RECOMMENDATIONS + 1))
elif [ "$ERRORS_5MIN" -gt 0 ]; then
    echo -e "  ${YELLOW}⚠ Some errors detected${NC}"
fi

# 7. Session Analysis
echo ""
echo -e "${BLUE}[7/10] Session Analysis...${NC}"
SESSION_COUNT=$(ls -1 ~/.openclaw/agents/main/sessions/*.jsonl 2>/dev/null | wc -l)
SESSION_SIZE=$(du -sh ~/.openclaw/agents/main/sessions/ 2>/dev/null | cut -f1)

echo -e "  Session Files: $SESSION_COUNT"
echo -e "  Total Size: $SESSION_SIZE"

if [ "$SESSION_COUNT" -gt 100 ]; then
    echo -e "  ${YELLOW}⚠ High number of session files${NC}"
    echo -e "  ${YELLOW}Recommendation: Clean up old sessions${NC}"
    RECOMMENDATIONS=$((RECOMMENDATIONS + 1))
fi

# 8. Background Process Analysis
echo ""
echo -e "${BLUE}[8/10] Background Process Analysis...${NC}"
MONITOR_COUNT=$(pgrep -f -E '(auto-monitor|trading-monitor)' | wc -l)
GATEWAY_PID=$(pgrep -f openclaw-gateway | head -1)

echo -e "  Trading Monitors: $MONITOR_COUNT"
echo -e "  Gateway PID: $GATEWAY_PID"

if [ -n "$GATEWAY_PID" ]; then
    GATEWAY_MEMORY=$(ps -p "$GATEWAY_PID" -o rss= 2>/dev/null | awk '{printf "%.1f", $1/1024}')
    GATEWAY_CPU=$(ps -p "$GATEWAY_PID" -o %cpu= 2>/dev/null)
    echo -e "  Gateway Memory: ${GATEWAY_MEMORY}MB"
    echo -e "  Gateway CPU: ${GATEWAY_CPU}%"

    if (( $(echo "$GATEWAY_MEMORY > 1000" | bc -l) )); then
        echo -e "  ${YELLOW}⚠ High gateway memory usage${NC}"
        echo -e "  ${YELLOW}Recommendation: Consider restart${NC}"
    fi
fi

# 9. Network Analysis
echo ""
echo -e "${BLUE}[9/10] Network Analysis...${NC}"
DNS_WORKS=$(nslookup google.com >/dev/null 2>&1 && echo "yes" || echo "no")
PING_RESULT=$(ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1 && echo "yes" || echo "no")

echo -e "  DNS Resolution: $([ "$DNS_WORKS" = "yes" ] && echo "${GREEN}Working${NC}" || echo "${RED}Failed${NC}")"
echo -e "  Internet Connectivity: $([ "$PING_RESULT" = "yes" ] && echo "${GREEN}Working${NC}" || echo "${RED}Failed${NC}")"

if [ "$DNS_WORKS" = "no" ] || [ "$PING_RESULT" = "no" ]; then
    echo -e "  ${YELLOW}Recommendation: Check network configuration${NC}"
    RECOMMENDATIONS=$((RECOMMENDATIONS + 1))
fi

# 10. Log Analysis
echo ""
echo -e "${BLUE}[10/10] Log Analysis...${NC}"
LOG_SIZE=$(du -sh /tmp/openclaw-1000/ 2>/dev/null | cut -f1)
LOG_FILES=$(ls -1 /tmp/openclaw-1000/*.log 2>/dev/null | wc -l)

echo -e "  Log Directory Size: $LOG_SIZE"
echo -e "  Log Files: $LOG_FILES"

# Summary
echo ""
echo "═════════════════════════════════════════════════════════════════"
echo ""
echo -e "${CYAN}Analysis Summary${NC}"
echo ""

if [ $RECOMMENDATIONS -eq 0 ]; then
    echo -e "${GREEN}✓ No issues found - System is healthy${NC}"
else
    echo -e "${YELLOW}⚠ $RECOMMENDATIONS recommendation(s) found${NC}"
    echo ""
    echo "Recommendations:"
    echo "  1. Review the analysis above"
    echo "  2. Run health check: cd ~/.openclaw/workspace/diagnostics && ./health-check.sh"
    echo "  3. Check logs: journalctl -u openclaw-gateway -f"
    echo "  4. Run optimization: cd ~/.openclaw/workspace/diagnostics && ./quick-fix-lite.sh"
fi

echo ""
echo -e "${BLUE}Timestamp:${NC} $(date)"
echo ""