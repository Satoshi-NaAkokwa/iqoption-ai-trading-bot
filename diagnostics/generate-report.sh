#!/bin/bash
# Create a comprehensive report combining all diagnostics

set -e

REPORT_DIR="/home/openclaw/.openclaw/workspace/diagnostics/reports"
mkdir -p "$REPORT_DIR"

REPORT_FILE="$REPORT_DIR/diagnostic-report-$(date +%Y%m%d_%H%M%S).md"

cat > "$REPORT_FILE" << 'HEADER'
# OpenClaw Diagnostic Report

**Generated:** $(date)
**System:** vm-axvC6iBU
**OpenClaw Version:** $(openclaw --version 2>/dev/null || echo "N/A")

---

## 1. System Overview

HEADER

# Gather system info
{
    echo "### Host Information"
    echo '```'
    uname -a
    echo '```'
    echo ""
    echo "### Uptime"
    echo '```'
    uptime
    echo '```'
    echo ""
    echo "### CPU Info"
    echo '```'
    lscpu | grep -E '^CPU|^Core|^Thread|^Model name'
    echo '```'
    echo ""
} >> "$REPORT_FILE"

# Memory info
{
    echo "### Memory Usage"
    echo '```'
    free -h
    echo '```'
    echo ""
} >> "$REPORT_FILE"

# Disk info
{
    echo "### Disk Usage"
    echo '```'
    df -h
    echo '```'
    echo ""
} >> "$REPORT_FILE"

# Gateway status
{
    echo "## 2. Gateway Status"
    echo ""
    echo "### Service Status"
    echo '```'
    systemctl status openclaw-gateway --no-pager | head -15
    echo '```'
    echo ""
} >> "$REPORT_FILE"

# Process info
{
    echo "### Gateway Process"
    echo '```'
    ps aux | grep openclaw-gateway | grep -v grep
    echo '```'
    echo ""
} >> "$REPORT_FILE"

# Network info
{
    echo "## 3. Network Status"
    echo ""
    echo "### LLM API Endpoint"
    echo '```'
    echo "Base URL: $API_HUB_BASE_URL"
    echo "Health Check:"
    curl -s http://10.1.160.84:9527/health
    echo ""
    echo '```'
    echo ""
    echo "### API Models Available"
    echo '```'
    if [ -n "$API_HUB_KEY" ]; then
        curl -s -H "Authorization: Bearer $API_HUB_KEY" http://10.1.160.84:9527/v1/models
    else
        echo "API_HUB_KEY not set"
    fi
    echo '```'
    echo ""
} >> "$REPORT_FILE"

# Recent errors
{
    echo "## 4. Recent Errors (Last 30 minutes)"
    echo '```'
    journalctl -u openclaw-gateway --since "30 minutes ago" | grep -i error | tail -20
    echo '```'
    echo ""
} >> "$REPORT_FILE"

# Session info
{
    echo "## 5. Session Information"
    echo ""
    echo "### Session Count"
    echo '```'
    find ~/.openclaw/sessions -name "*.jsonl" 2>/dev/null | wc -l
    echo '```'
    echo ""
    echo "### Session Sizes"
    echo '```'
    du -sh ~/.openclaw/sessions 2>/dev/null || echo "No sessions directory"
    echo '```'
    echo ""
} >> "$REPORT_FILE"

# Background processes
{
    echo "## 6. Background Processes"
    echo ""
    echo "### Trading Monitors"
    echo '```'
    ps aux | grep -E '(auto-monitor|continuous-trading-monitor)' | grep -v grep || echo "None running"
    echo '```'
    echo ""
} >> "$REPORT_FILE"

# Log file sizes
{
    echo "## 7. Log Files"
    echo ""
    echo "### OpenClaw Logs"
    echo '```'
    ls -lh /tmp/openclaw-1000/*.log 2>/dev/null | tail -5
    echo '```'
    echo ""
    echo "### Total OpenClaw Directory Size"
    echo '```'
    du -sh ~/.openclaw
    echo '```'
    echo ""
} >> "$REPORT_FILE"

# Recommendations
{
    echo "## 8. Recommendations"
    echo ""
    echo "See \`SYSTEM_VERDICT.md\` for detailed optimization plan."
    echo ""
    echo "### Quick Actions"
    echo ""
    echo "1. **Check API Key:** Ensure \`API_HUB_KEY\` is valid"
    echo "2. **Clean Sessions:** Run \`./quick-fix.sh\`"
    echo "3. **Review Monitors:** Check if trading monitors are needed"
    echo "4. **Monitor Logs:** Run \`./log-monitor.sh\`"
    echo ""
    echo "### Long-term Actions"
    echo ""
    echo "1. **Set up log rotation:** (configured by quick-fix.sh)"
    echo "2. **Configure monitoring:** Add health checks to crontab"
    echo "3. **Review configuration:** Apply config patches after testing"
    echo "4. **Update OpenClaw:** \`openclaw update\`"
    echo ""
} >> "$REPORT_FILE"

# Footer
{
    echo "---"
    echo ""
    echo "**Report Generation:** Complete"
    echo "**Next Steps:** Review recommendations and implement fixes"
    echo ""
    echo "For more details, see: \`SYSTEM_VERDICT.md\`"
    echo ""
    echo "**Diagnostic Scripts:**"
    echo "- \`./health-check.sh\` - Quick health status"
    echo "- \`./log-monitor.sh\` - Live log monitoring"
    echo "- \`./llm-provider-check.sh\` - API connectivity test"
    echo "- \`./quick-fix.sh\` - Automated fixes (with prompts)"
} >> "$REPORT_FILE"

echo "=========================================="
echo "Diagnostic Report Generated"
echo "=========================================="
echo ""
echo "Report saved to: $REPORT_FILE"
echo ""
echo "View report with:"
echo "  cat $REPORT_FILE"
echo ""
echo "Or:"
echo "  less $REPORT_FILE"
echo ""