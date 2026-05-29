#!/bin/bash
# EMERGENCY RECOVERY - Quick recovery procedures

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

clear

cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║            OpenClaw Emergency Recovery Guide                   ║
╚════════════════════════════════════════════════════════════════╝

This tool provides quick recovery procedures for common issues.

EOF

echo ""
echo -e "${BLUE}Select an issue:${NC}"
echo ""
echo "  [1] Gateway is down"
echo "  [2] High memory usage"
echo "  [3] High CPU usage"
echo "  [4] API not working"
echo "  [5] System unresponsive"
echo "  [6] Corrupted files"
echo "  [7] Backup restore"
echo "  [8] Exit"
echo ""
read -p "Enter option [1-8]: " choice

case "$choice" in
    1)
        echo ""
        echo -e "${YELLOW}[1/4] Checking gateway status...${NC}"
        systemctl status openclaw-gateway --no-pager | head -5
        
        echo ""
        echo -e "${YELLOW}[2/4] Restarting gateway...${NC}"
        sudo systemctl restart openclaw-gateway
        
        sleep 3
        echo ""
        echo -e "${YELLOW}[3/4] Verifying gateway is running...${NC}"
        if systemctl is-active --quiet openclaw-gateway; then
            echo -e "${GREEN}✓ Gateway is now running${NC}"
        else
            echo -e "${RED}✗ Gateway failed to start${NC}"
            echo "Check logs: journalctl -u openclaw-gateway -f"
        fi
        
        echo ""
        echo -e "${YELLOW}[4/4] Running health check...${NC}"
        cd ~/.openclaw/workspace/diagnostics && ./health-check.sh | tail -15
        ;;
        
    2)
        echo ""
        echo -e "${YELLOW}[1/3] Checking memory usage...${NC}"
        free -h
        
        echo ""
        echo -e "${YELLOW}[2/3] Identifying top memory consumers...${NC}"
        ps aux | sort -rk 4 | head -10 | awk '{printf "  %s %s %s %s\n", $2, $11, $3, $4}'
        
        echo ""
        read -p "Stop background monitors? (yes/no): " stop_monitors
        if [ "$stop_monitors" = "yes" ]; then
            echo -e "${YELLOW}[3/3] Stopping monitors...${NC}"
            pkill -f "auto-monitor.js"
            pkill -f "trading-monitor.js"
            echo -e "${GREEN}✓ Monitors stopped${NC}"
        fi
        ;;
        
    3)
        echo ""
        echo -e "${YELLOW}[1/3] Checking CPU usage...${NC}"
        top -bn1 | grep "Cpu(s)"
        
        echo ""
        echo -e "${YELLOW}[2/3] Identifying top CPU consumers...${NC}"
        ps aux | sort -rk 3 | head -10 | awk '{printf "  %s %s %s %s\n", $2, $11, $3, $4}'
        
        echo ""
        echo -e "${YELLOW}[3/3] System load...${NC}"
        uptime
        ;;
        
    4)
        echo ""
        echo -e "${YELLOW}[1/3] Testing API connectivity...${NC}"
        cd ~/.openclaw/workspace/diagnostics
        ./llm-provider-check.sh
        
        echo ""
        echo -e "${YELLOW}[2/3] Checking API key...${NC}"
        if [ -n "$API_HUB_KEY" ]; then
            echo -e "${GREEN}✓ API key is set${NC}"
            echo "  Key length: ${#API_HUB_KEY} characters"
        else
            echo -e "${RED}✗ API key not found${NC}"
            echo "  Set with: export API_HUB_KEY=your-key"
        fi
        
        echo ""
        echo -e "${YELLOW}[3/3] Checking network connectivity...${NC}"
        if ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1; then
            echo -e "${GREEN}✓ Network is working${NC}"
        else
            echo -e "${RED}✗ Network issues detected${NC}"
        fi
        ;;
        
    5)
        echo ""
        echo -e "${YELLOW}[1/4] Checking system responsiveness...${NC}"
        echo -n "Testing response time: "
        START=$(date +%s%N)
        sleep 0.1
        END=$(date +%s%N)
        LATENCY=$(( (END - START) / 1000000 ))
        echo "${LATENCY}ms"
        
        echo ""
        echo -e "${YELLOW}[2/4] Checking load average...${NC}"
        uptime
        
        echo ""
        echo -e "${YELLOW}[3/4] Checking critical services...${NC}"
        echo "  Gateway: $(systemctl is-active openclaw-gateway)"
        echo "  Network: $(ping -c 1 -W 1 8.8.8.8 >/dev/null 2>&1 && echo "Working" || echo "Issues")"
        
        echo ""
        echo -e "${YELLOW}[4/4] Recommendations...${NC}"
        echo "  1. Check for runaway processes"
        echo "  2. Review logs: journalctl -u openclaw-gateway -f"
        echo "  3. Restart gateway if needed"
        ;;
        
    6)
        echo ""
        echo -e "${YELLOW}[1/3] Checking session files...${NC}"
        SESSION_COUNT=$(ls -1 ~/.openclaw/agents/main/sessions/*.jsonl 2>/dev/null | wc -l)
        echo "  Session files: $SESSION_COUNT"
        
        echo ""
        echo -e "${YELLOW}[2/3] Checking log files...${NC}"
        LOG_SIZE=$(du -sh /tmp/openclaw-1000/ 2>/dev/null | cut -f1)
        echo "  Log directory size: $LOG_SIZE"
        
        echo ""
        read -p "Clean up old files? (yes/no): " cleanup
        if [ "$cleanup" = "yes" ]; then
            echo -e "${YELLOW}[3/3] Cleaning up...${NC}"
            cd ~/.openclaw/workspace/diagnostics
            ./system-cleanup.sh
        fi
        ;;
        
    7)
        echo ""
        echo -e "${YELLOW}[1/2] Listing available backups...${NC}"
        cd ~/.openclaw/workspace/diagnostics
        ./backup-restore.sh list
        
        echo ""
        read -p "Enter backup name to restore: " backup_name
        if [ -n "$backup_name" ]; then
            echo -e "${YELLOW}[2/2] Restoring backup...${NC}"
            ./backup-restore.sh restore "$backup_name"
        fi
        ;;
        
    8)
        echo ""
        echo "Exiting..."
        exit 0
        ;;
        
    *)
        echo ""
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo "═════════════════════════════════════════════════════════════════"
echo ""
echo "For more help:"
echo "  cd ~/.openclaw/workspace/diagnostics"
echo "  ./menu.sh"
echo "  cat TROUBLESHOOTING.md"
echo ""