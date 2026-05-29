#!/bin/bash
# DAILY MAINTENANCE ROUTINE - Run this daily for optimal system health

echo "═════════════════════════════════════════════════════════════════"
echo "           OpenClaw Daily Maintenance Routine"
echo "═════════════════════════════════════════════════════════════════"
echo ""
echo "Timestamp: $(date)"
echo ""

# Navigate to diagnostics
cd ~/.openclaw/workspace/diagnostics

echo "📊 [1/5] Running System Health Check..."
echo ""
./health-check.sh
echo ""

echo "📊 [2/5] Quick Status Check..."
echo ""
./quick-status.sh
echo ""

echo "📊 [3/5] Checking API Connectivity..."
echo ""
./llm-provider-check.sh 2>&1 | grep -E "(Status|Response|✓|✗)" | head -5
echo ""

echo "📊 [4/5] Recent Error Summary..."
echo ""
ERRORS=$(journalctl -u openclaw-gateway --since "5 minutes ago" 2>/dev/null | grep -i error | wc -l)
echo "Errors in last 5 minutes: $ERRORS"
echo ""

echo "📊 [5/5] System Summary..."
echo ""
echo "Gateway: $(systemctl is-active openclaw-gateway 2>/dev/null || echo 'unknown')"
echo "Memory: $(free | awk 'NR==2{printf "%.1f%%", $3/$2*100}')"
echo "Disk: $(df -h / | awk 'NR==2{print $5}')"
echo ""

echo "═════════════════════════════════════════════════════════════════"
echo ""
echo "✅ Daily maintenance complete"
echo ""
echo "Next steps:"
echo "  • Review any warnings above"
echo "  • Run full diagnostics if needed: ./menu.sh"
echo "  • Generate weekly report on Monday"
echo ""
echo "For detailed troubleshooting:"
echo "  cat README_COMPLETE.md"
echo "  cat TROUBLESHOOTING.md"
echo ""