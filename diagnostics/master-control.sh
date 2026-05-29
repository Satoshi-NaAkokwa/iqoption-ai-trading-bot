#!/bin/bash
# MASTER CONTROL - Central command center for all diagnostics

clear

cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║          OpenClaw Diagnostics Master Control Center            ║
╚════════════════════════════════════════════════════════════════╝

EOF

echo -e "\033[1;36mAvailable Commands:\033[0m"
echo ""

echo "  [1] Quick Health Check (10 seconds)"
echo "  [2] Full Health Check (1 minute)"
echo "  [3] Interactive Menu"
echo "  [4] Generate Report"
echo "  [5] Status Dashboard"
echo "  [6] Performance Benchmark"
echo "  [7] Create Backup"
echo "  [8] System Cleanup"
echo "  [9] Emergency Recovery"
echo " [10] View Documentation"
echo " [11] Daily Maintenance"
echo " [12] Exit"
echo ""

read -p "Enter option [1-12]: " choice

case "$choice" in
    1)
        echo ""
        echo -e "\033[1;32mRunning Quick Health Check...\033[0m"
        echo ""
        ./quick-health.sh 2>/dev/null || echo "Gateway: $(systemctl is-active openclaw-gateway 2>/dev/null || echo 'unknown') | Memory: $(free | awk 'NR==2{printf "%.1f%%", $3/$2*100}') | CPU: $(top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1)% | API: $(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 2 https://api.openai.com/v1/models 2>/dev/null || echo '000') | Errors: $(journalctl -u openclaw-gateway --since '5 minutes ago' 2>/dev/null | grep -i error | wc -l)"
        ;;
    2)
        echo ""
        echo -e "\033[1;32mRunning Full Health Check...\033[0m"
        echo ""
        ./health-check.sh
        ;;
    3)
        echo ""
        echo -e "\033[1;32mOpening Interactive Menu...\033[0m"
        echo ""
        ./menu.sh
        ;;
    4)
        echo ""
        echo -e "\033[1;32mGenerating Report...\033[0m"
        echo ""
        ./generate-report.sh
        ;;
    5)
        echo ""
        echo -e "\033[1;32mOpening Status Dashboard...\033[0m"
        echo ""
        ./status-dashboard.sh
        ;;
    6)
        echo ""
        echo -e "\033[1;32mRunning Performance Benchmark...\033[0m"
        echo ""
        ./performance-benchmark.sh
        ;;
    7)
        echo ""
        echo -e "\033[1;32mCreating Backup...\033[0m"
        echo ""
        ./backup-restore.sh backup
        ;;
    8)
        echo ""
        echo -e "\033[1;32mRunning System Cleanup...\033[0m"
        echo ""
        ./system-cleanup.sh
        ;;
    9)
        echo ""
        echo -e "\033[1;32mOpening Emergency Recovery...\033[0m"
        echo ""
        ./emergency-recovery.sh
        ;;
    10)
        echo ""
        echo -e "\033[1;32mAvailable Documentation:\033[0m"
        echo ""
        echo "  PROJECT_CERTIFICATE.md  - Project completion certificate"
        echo "  PROJECT_SUMMARY.md       - Project completion summary"
        echo "  WHAT_TO_DO_NOW.md        - What to do next"
        echo "  README_COMPLETE.md       - Complete README"
        echo "  TROUBLESHOOTING.md       - Troubleshooting guide"
        echo "  ADVANCED_TOOLS.md        - Advanced tools guide"
        echo ""
        read -p "View which file? " doc_file
        if [ -f "$doc_file" ]; then
            cat "$doc_file"
        else
            echo "File not found: $doc_file"
        fi
        ;;
    11)
        echo ""
        echo -e "\033[1;32mRunning Daily Maintenance...\033[0m"
        echo ""
        ./daily-maintenance.sh
        ;;
    12)
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
echo "Quick status: Gateway: $(systemctl is-active openclaw-gateway 2>/dev/null || echo 'unknown') | Memory: $(free | awk 'NR==2{printf "%.1f%%", $3/$2*100}') | CPU: $(top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1)%"
echo ""
echo "For more options: ./menu.sh"
echo ""