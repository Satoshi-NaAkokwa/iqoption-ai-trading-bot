#!/bin/bash
# SYSTEM CLEANUP - Clean up old logs, sessions, and temporary files

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

TOTAL_FREED=0

print_header() {
    clear
    cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║         OpenClaw System Cleanup Utility                        ║
╚════════════════════════════════════════════════════════════════╝

This utility will clean up old logs, sessions, and temporary files.

Press Ctrl+C to cancel.
EOF
}

print_header

echo ""
read -p "Continue with cleanup? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo -e "${BLUE}Starting cleanup...${NC}"
echo ""

# Clean old session files
echo -e "${BLUE}[1/5] Cleaning old session files...${NC}"
SESSION_COUNT=$(ls -1 ~/.openclaw/agents/main/sessions/*.jsonl 2>/dev/null | wc -l)
if [ "$SESSION_COUNT" -gt 0 ]; then
    echo "  Found $SESSION_COUNT session files"
    read -p "  Delete session files older than 7 days? (yes/no): " delete_sessions
    if [ "$delete_sessions" = "yes" ]; then
        FREED=$(du -sh ~/.openclaw/agents/main/sessions/ 2>/dev/null | cut -f1)
        find ~/.openclaw/agents/main/sessions/ -name "*.jsonl" -mtime +7 -delete 2>/dev/null || true
        echo -e "  ${GREEN}✓ Old session files deleted${NC}"
        TOTAL_FREED=$((TOTAL_FREED + 1))
    else
        echo "  Skipped session files"
    fi
else
    echo -e "  ${GREEN}✓ No old session files found${NC}"
fi

# Clean old logs
echo ""
echo -e "${BLUE}[2/5] Cleaning old log files...${NC}"
LOG_COUNT=$(ls -1 /tmp/openclaw-1000/*.log 2>/dev/null | wc -l)
if [ "$LOG_COUNT" -gt 0 ]; then
    echo "  Found $LOG_COUNT log files"
    read -p "  Delete log files older than 7 days? (yes/no): " delete_logs
    if [ "$delete_logs" = "yes" ]; then
        FREED=$(du -sh /tmp/openclaw-1000/ 2>/dev/null | cut -f1)
        find /tmp/openclaw-1000/ -name "*.log" -mtime +7 -delete 2>/dev/null || true
        echo -e "  ${GREEN}✓ Old log files deleted${NC}"
        TOTAL_FREED=$((TOTAL_FREED + 1))
    else
        echo "  Skipped log files"
    fi
else
    echo -e "  ${GREEN}✓ No old log files found${NC}"
fi

# Clean old benchmark data
echo ""
echo -e "${BLUE}[3/5] Cleaning old benchmark data...${NC}"
BENCHMARK_COUNT=$(ls -1 ~/.openclaw/benchmarks/*.json 2>/dev/null | wc -l)
if [ "$BENCHMARK_COUNT" -gt 30 ]; then
    echo "  Found $BENCHMARK_COUNT benchmark files (keeping last 30)"
    read -p "  Delete old benchmark files? (yes/no): " delete_benchmarks
    if [ "$delete_benchmarks" = "yes" ]; then
        ls -t ~/.openclaw/benchmarks/*.json | tail -n +31 | xargs rm -f 2>/dev/null || true
        echo -e "  ${GREEN}✓ Old benchmark files deleted${NC}"
        TOTAL_FREED=$((TOTAL_FREED + 1))
    else
        echo "  Skipped benchmark files"
    fi
else
    echo -e "  ${GREEN}✓ No old benchmark files to clean${NC}"
fi

# Clean old reports
echo ""
echo -e "${BLUE}[4/5] Cleaning old reports...${NC}"
REPORT_COUNT=$(ls -1 ~/.openclaw/workspace/diagnostics/reports/*.md 2>/dev/null | wc -l)
if [ "$REPORT_COUNT" -gt 10 ]; then
    echo "  Found $REPORT_COUNT report files (keeping last 10)"
    read -p "  Delete old report files? (yes/no): " delete_reports
    if [ "$delete_reports" = "yes" ]; then
        ls -t ~/.openclaw/workspace/diagnostics/reports/*.md | tail -n +11 | xargs rm -f 2>/dev/null || true
        echo -e "  ${GREEN}✓ Old report files deleted${NC}"
        TOTAL_FREED=$((TOTAL_FREED + 1))
    else
        echo "  Skipped report files"
    fi
else
    echo -e "  ${GREEN}✓ No old report files to clean${NC}"
fi

# Clean old backups
echo ""
echo -e "${BLUE}[5/5] Cleaning old backups...${NC}"
BACKUP_COUNT=$(ls -1 ~/.openclaw-backups/*.tar.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 7 ]; then
    echo "  Found $BACKUP_COUNT backup files (keeping last 7)"
    read -p "  Delete old backup files? (yes/no): " delete_backups
    if [ "$delete_backups" = "yes" ]; then
        ls -t ~/.openclaw-backups/*.tar.gz | tail -n +8 | xargs rm -f 2>/dev/null || true
        echo -e "  ${GREEN}✓ Old backup files deleted${NC}"
        TOTAL_FREED=$((TOTAL_FREED + 1))
    else
        echo "  Skipped backup files"
    fi
else
    echo -e "  ${GREEN}✓ No old backup files to clean${NC}"
fi

# Summary
echo ""
echo "═════════════════════════════════════════════════════════════════"
echo ""
echo -e "${BLUE}Cleanup Summary${NC}"
echo ""
echo "Actions completed: $TOTAL_FREED"
echo ""

if [ $TOTAL_FREED -eq 0 ]; then
    echo -e "${GREEN}No cleanup needed - system is clean${NC}"
else
    echo -e "${GREEN}✓ Cleanup completed successfully${NC}"
fi

echo ""
echo "Timestamp: $(date)"
echo ""

# Show current disk usage
echo "Current disk usage:"
df -h / | awk 'NR==2{printf "  /: %s used, %s available\n", $5, $4}'

echo ""
echo "Recommendations:"
echo "  1. Run cleanup monthly"
echo "  2. Keep backups up to date: ./backup-restore.sh backup"
echo "  3. Monitor disk space regularly"
echo ""