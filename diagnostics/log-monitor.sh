#!/bin/bash
# Monitor OpenClaw gateway logs in real-time
# Shows only relevant events (errors, warnings, agent starts/ends)

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "OpenClaw Log Monitor"
echo "=========================================="
echo "Press Ctrl+C to exit"
echo ""
echo "Legend:"
echo -e "  ${GREEN}[INFO]${NC}    Informational messages"
echo -e "  ${YELLOW}[WARN]${NC}    Warnings"
echo -e "  ${RED}[ERROR]${NC}   Errors"
echo -e "  ${BLUE}[AGENT]${NC}   Agent lifecycle events"
echo ""
echo "=========================================="
echo ""

journalctl -u openclaw-gateway -f | while read line; do
    if echo "$line" | grep -qi "error"; then
        echo -e "${RED}[ERROR]${NC} $line"
    elif echo "$line" | grep -qi "warn"; then
        echo -e "${YELLOW}[WARN]${NC} $line"
    elif echo "$line" | grep -qi "agent.*end"; then
        echo -e "${BLUE}[AGENT]${NC} $line"
    elif echo "$line" | grep -qi "agent.*start"; then
        echo -e "${BLUE}[AGENT]${NC} $line"
    elif echo "$line" | grep -qi "session.*repair"; then
        echo -e "${YELLOW}[WARN]${NC} $line"
    elif echo "$line" | grep -qi "stuck.*session"; then
        echo -e "${YELLOW}[WARN]${NC} $line"
    elif echo "$line" | grep -qi "rate.*limit"; then
        echo -e "${RED}[ERROR]${NC} $line"
    fi
done