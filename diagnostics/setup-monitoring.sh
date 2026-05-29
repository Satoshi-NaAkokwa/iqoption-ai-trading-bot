#!/bin/bash
# AUTOMATED MONITORING SETUP - Set up cron jobs for ongoing monitoring

clear

cat << 'EOF'
================================================================================
                    AUTOMATED MONITORING SETUP
================================================================================

This script will set up automated monitoring for your OpenClaw system.

Options:
  [1] Daily health check (at 9 AM)
  [2] Weekly report generation (at 10 AM on Monday)
  [3] Log rotation (daily at midnight)
  [4] All of the above
  [5] Show current crontab
  [6] Exit

================================================================================

EOF

read -p "Select option [1-6]: " choice

case $choice in
    1)
        echo ""
        echo "Setting up daily health check at 9 AM..."
        (crontab -l 2>/dev/null | grep -v "health-check"; echo "0 9 * * * cd ~/.openclaw/workspace/diagnostics && ./health-check.sh >> /var/log/openclaw-health.log 2>&1") | crontab -
        echo "✅ Daily health check scheduled for 9 AM"
        echo "   Logs will be saved to: /var/log/openclaw-health.log"
        ;;
    2)
        echo ""
        echo "Setting up weekly report generation (Monday at 10 AM)..."
        (crontab -l 2>/dev/null | grep -v "generate-report"; echo "0 10 * * 1 cd ~/.openclaw/workspace/diagnostics && ./generate-report.sh >> /var/log/openclaw-reports.log 2>&1") | crontab -
        echo "✅ Weekly report scheduled for Monday at 10 AM"
        echo "   Logs will be saved to: /var/log/openclaw-reports.log"
        ;;
    3)
        echo ""
        echo "Setting up log rotation (daily at midnight)..."
        (crontab -l 2>/dev/null | grep -v "log-rotation"; echo "0 0 * * * find /tmp/openclaw-1000/*.log -mtime +7 -delete && find ~/.openclaw/workspace/diagnostics/reports/*.md -mtime +30 -delete >> /var/log/openclaw-cleanup.log 2>&1") | crontab -
        echo "✅ Log rotation scheduled for daily at midnight"
        echo "   Old logs (>7 days) will be deleted"
        echo "   Old reports (>30 days) will be deleted"
        ;;
    4)
        echo ""
        echo "Setting up all automated monitoring tasks..."
        (
            crontab -l 2>/dev/null | grep -v "health-check" | grep -v "generate-report" | grep -v "log-rotation";
            echo "# OpenClaw automated monitoring"
            echo "0 9 * * * cd ~/.openclaw/workspace/diagnostics && ./health-check.sh >> /var/log/openclaw-health.log 2>&1"
            echo "0 10 * * 1 cd ~/.openclaw/workspace/diagnostics && ./generate-report.sh >> /var/log/openclaw-reports.log 2>&1"
            echo "0 0 * * * find /tmp/openclaw-1000/*.log -mtime +7 -delete && find ~/.openclaw/workspace/diagnostics/reports/*.md -mtime +30 -delete >> /var/log/openclaw-cleanup.log 2>&1"
        ) | crontab -
        echo "✅ All monitoring tasks scheduled:"
        echo "   - Daily health check at 9 AM"
        echo "   - Weekly report on Monday at 10 AM"
        echo "   - Log rotation at midnight"
        ;;
    5)
        echo ""
        echo "Current crontab:"
        echo "────────────────────────────────────────"
        crontab -l 2>/dev/null || echo "No crontab entries found"
        echo "────────────────────────────────────────"
        ;;
    6)
        echo ""
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo ""
        echo "Invalid option. Please enter 1-6."
        ;;
esac

echo ""
echo "To view scheduled tasks: crontab -l"
echo "To edit scheduled tasks: crontab -e"
echo "To remove all tasks: crontab -r"
echo ""