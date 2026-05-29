#!/bin/bash
# MASTER MENU - All diagnostic tools in one place

clear

echo "=========================================="
echo "  OpenClaw Diagnostics Suite"
echo "=========================================="
echo ""
echo "System Status:"
echo "  Gateway: $(systemctl is-active openclaw-gateway 2>/dev/null || echo 'unknown')"
echo "  Memory:  $(free | awk '/Mem/{printf "%.1f%%", $3/$2 * 100.0}')"
echo "  CPU:     $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo ""
echo "=========================================="
echo "  Select an Option:"
echo "=========================================="
echo ""
echo "  [1] Run Health Check"
echo "  [2] Monitor Logs (Live)"
echo "  [3] Test LLM API"
echo "  [4] Run Automated Fixes"
echo "  [5] Generate Full Report"
echo "  [6] View System Status"
echo "  [7] View Documentation"
echo "  [8] View Recent Errors"
echo "  [9] Exit"
echo ""
echo "=========================================="
read -p "Enter choice [1-9]: " choice

case $choice in
    1)
        echo ""
        echo "Running health check..."
        cd ~/.openclaw/workspace/diagnostics && ./health-check.sh
        ;;
    2)
        echo ""
        echo "Starting log monitor (Ctrl+C to exit)..."
        cd ~/.openclaw/workspace/diagnostics && ./log-monitor.sh
        ;;
    3)
        echo ""
        echo "Testing LLM API..."
        cd ~/.openclaw/workspace/diagnostics && ./llm-provider-check.sh
        ;;
    4)
        echo ""
        echo "⚠️  This will create backups and may stop background processes."
        read -p "Continue? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cd ~/.openclaw/workspace/diagnostics && ./quick-fix-lite.sh
        else
            echo "Cancelled."
        fi
        ;;
    5)
        echo ""
        echo "Generating report..."
        cd ~/.openclaw/workspace/diagnostics && ./generate-report.sh
        ;;
    6)
        echo ""
        echo "=== System Status ==="
        echo ""
        echo "Gateway:"
        systemctl status openclaw-gateway --no-pager | head -10
        echo ""
        echo "Memory:"
        free -h
        echo ""
        echo "Disk:"
        df -h
        echo ""
        echo "Processes:"
        ps aux | grep -E '(openclaw-gateway|auto-monitor|trading-monitor)' | grep -v grep
        ;;
    7)
        echo ""
        echo "=== Documentation ==="
        echo ""
        echo "Available documentation:"
        echo ""
        echo "  1. README.md                    - Complete usage guide"
        echo "  2. SYSTEM_VERDICT.md            - Detailed analysis"
        echo "  3. FINAL_REPORT.md              - Current status"
        echo "  4. COMPLETE_SUMMARY.md          - Executive summary"
        echo ""
        read -p "View which file? [1-4]: " doc_choice
        case $doc_choice in
            1) cat README.md | less ;;
            2) cat SYSTEM_VERDICT.md | less ;;
            3) cat FINAL_REPORT.md | less ;;
            4) cat COMPLETE_SUMMARY.md | less ;;
            *) echo "Invalid choice" ;;
        esac
        ;;
    8)
        echo ""
        echo "=== Recent Errors (Last 10 minutes) ==="
        echo ""
        journalctl -u openclaw-gateway --since "10 minutes ago" | grep -i error
        ;;
    9)
        echo ""
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo ""
        echo "Invalid choice. Please enter 1-9."
        ;;
esac

echo ""
read -p "Press Enter to continue..."