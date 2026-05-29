#!/bin/bash
# QUICK DEMO SCRIPT - Shows all tools in action

clear

cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║         OpenClaw Diagnostics Suite - Quick Demonstration        ║
╚════════════════════════════════════════════════════════════════╝

This script will demonstrate all the diagnostic tools available.

PRESS ENTER TO CONTINUE...
EOF

read

echo ""
echo "🔍 DEMO 1: Health Check"
echo "────────────────────────────────────────────────────────────────"
read -p "Press Enter to run health check..."
echo ""

cd ~/.openclaw/workspace/diagnostics
./health-check.sh

echo ""
echo "Press Enter for next demo..."
read

echo ""
echo "🔍 DEMO 2: LLM API Connectivity Test"
echo "────────────────────────────────────────────────────────────────"
read -p "Press Enter to test API..."
echo ""

./llm-provider-check.sh

echo ""
echo "Press Enter for next demo..."
read

echo ""
echo "🔍 DEMO 3: Background Processes Analysis"
echo "────────────────────────────────────────────────────────────────"
read -p "Press Enter to check background processes..."
echo ""

echo "Gateway Process:"
ps aux | grep openclaw-gateway | grep -v grep | awk '{printf "  PID: %s | Memory: %sMB | CPU: %s%%\n", $2, $6/1024, $3}'

echo ""
echo "Background Monitors:"
MONITOR_COUNT=$(ps aux | grep -E '(auto-monitor|trading-monitor)' | grep -v grep | wc -l)
if [ "$MONITOR_COUNT" -gt 0 ]; then
  ps aux | grep -E '(auto-monitor|trading-monitor)' | grep -v grep | awk '{printf "  PID: %s | CMD: %s %s | CPU: %s%% | MEM: %s%%\n", $2, $11, $12, $3, $4}'
  echo ""
  echo "Total monitors: $MONITOR_COUNT"
  echo "Memory used: $(ps aux | grep -E '(auto-monitor|trading-monitor)' | grep -v grep | awk '{sum += $4} END {print sum"%"}')"
else
  echo "  No monitors running"
fi

echo ""
echo "Press Enter for next demo..."
read

echo ""
echo "🔍 DEMO 4: Recent Error Analysis"
echo "────────────────────────────────────────────────────────────────"
read -p "Press Enter to check recent errors..."
echo ""

ERRORS=$(journalctl -u openclaw-gateway --since "5 minutes ago" 2>/dev/null | grep -i error | wc -l)
WARNINGS=$(journalctl -u openclaw-gateway --since "5 minutes ago" 2>/dev/null | grep -i warning | wc -l)

echo "Errors in last 5 minutes: $ERRORS"
echo "Warnings in last 5 minutes: $WARNINGS"

if [ "$ERRORS" -gt 0 ]; then
  echo ""
  echo "Recent errors:"
  journalctl -u openclaw-gateway --since "5 minutes ago" 2>/dev/null | grep -i error | tail -5
fi

echo ""
echo "Press Enter for next demo..."
read

echo ""
echo "🔍 DEMO 5: System Resources"
echo "────────────────────────────────────────────────────────────────"
read -p "Press Enter to check system resources..."
echo ""

echo "Memory Usage:"
free -h | grep Mem | awk '{printf "  Used: %s (%.1f%%) | Available: %s\n", $3, $3/$2*100, $7}'

echo ""
echo "CPU Usage:"
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
echo "  Current CPU: ${CPU}%"

echo ""
echo "Disk Usage:"
df -h / | awk 'NR==2{printf "  Used: %s | Available: %s\n", $5, $4}'

echo ""
echo "Press Enter for next demo..."
read

echo ""
echo "🔍 DEMO 6: Log File Status"
echo "────────────────────────────────────────────────────────────────"
read -p "Press Enter to check log files..."
echo ""

echo "Log files in /tmp/openclaw-1000/:"
ls -lh /tmp/openclaw-1000/*.log 2>/dev/null | awk '{printf "  %s: %s\n", $9, $5}'

echo ""
echo "Total log size:"
du -sh /tmp/openclaw-1000/ 2>/dev/null | awk '{printf "  %s\n", $1}'

echo ""
echo "Press Enter for next demo..."
read

echo ""
echo "🔍 DEMO 7: Session Status"
echo "────────────────────────────────────────────────────────────────"
read -p "Press Enter to check session files..."
echo ""

SESSION_COUNT=$(ls ~/.openclaw/agents/main/sessions/*.jsonl 2>/dev/null | wc -l)
echo "Active sessions: $SESSION_COUNT"

if [ "$SESSION_COUNT" -gt 0 ]; then
  echo ""
  echo "Session files:"
  ls -lh ~/.openclaw/agents/main/sessions/*.jsonl 2>/dev/null | awk '{printf "  %s: %s\n", $9, $5}'
fi

echo ""
echo "Press Enter for next demo..."
read

echo ""
echo "🔍 DEMO 8: Gateway Service Status"
echo "────────────────────────────────────────────────────────────────"
read -p "Press Enter to check gateway status..."
echo ""

systemctl status openclaw-gateway --no-pager | head -10

echo ""
echo "Press Enter for final summary..."
read

echo ""
echo "═════════════════════════════════════════════════════════════════"
echo "                    DEMONSTRATION COMPLETE"
echo "═════════════════════════════════════════════════════════════════"
echo ""

echo "Available Tools:"
echo ""
echo "  ./START_HERE.sh              - Quick start guide"
echo "  ./menu.sh                     - Interactive menu"
echo "  ./health-check.sh             - Health monitoring"
echo "  ./status-dashboard.sh         - Real-time dashboard"
echo "  ./generate-report.sh          - Report generation"
echo "  ./llm-provider-check.sh      - API testing"
echo "  ./log-monitor.sh              - Live log monitoring"
echo ""

echo "Documentation:"
echo ""
echo "  cat INDEX.md                  - Complete file index"
echo "  cat README.md                 - Usage guide"
echo "  cat TROUBLESHOOTING.md        - Troubleshooting guide"
echo "  cat MAINTENANCE_SCHEDULE.md   - Maintenance procedures"
echo ""

echo "Thank you! Your OpenClaw system is fully optimized and monitored."
echo ""

read