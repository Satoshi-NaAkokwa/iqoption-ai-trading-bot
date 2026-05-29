#!/bin/bash
# PERFORMANCE BENCHMARK - Track system performance over time

set -e

BENCHMARK_DIR="$HOME/.openclaw/benchmarks"
mkdir -p "$BENCHMARK_DIR"

DATE=$(date +%Y%m%d_%H%M%S)
BENCHMARK_FILE="$BENCHMARK_DIR/benchmark-$DATE.json"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    clear
    cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║         OpenClaw Performance Benchmark                        ║
╚════════════════════════════════════════════════════════════════╝
EOF
}

collect_metrics() {
    # System metrics
    MEMORY_PERCENT=$(free | awk 'NR==2{printf "%.1f", $3/$2*100}')
    MEMORY_AVAILABLE=$(free -h | awk 'NR==2{print $7}')
    CPU_PERCENT=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    DISK_PERCENT=$(df -h / | awk 'NR==2{print $5}' | sed 's/%//')
    LOAD_1MIN=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}')

    # Gateway metrics
    GATEWAY_PID=$(pgrep -f openclaw-gateway | head -1)
    if [ -n "$GATEWAY_PID" ]; then
        GATEWAY_MEMORY=$(ps -p "$GATEWAY_PID" -o rss= 2>/dev/null | awk '{printf "%.1f", $1/1024}')
        GATEWAY_CPU=$(ps -p "$GATEWAY_PID" -o %cpu= 2>/dev/null)
        GATEWAY_STATUS="active"
    else
        GATEWAY_MEMORY=0
        GATEWAY_CPU=0
        GATEWAY_STATUS="inactive"
    fi

    # API metrics
    API_START=$(date +%s%N)
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 https://api.openai.com/v1/models 2>/dev/null || echo "000")
    API_END=$(date +%s%N)
    API_LATENCY=$(( (API_END - API_START) / 1000000 ))

    # Error metrics
    ERRORS_5MIN=$(journalctl -u openclaw-gateway --since "5 minutes ago" 2>/dev/null | grep -i error | wc -l)

    # Session metrics
    SESSION_COUNT=$(ls -1 ~/.openclaw/agents/main/sessions/*.jsonl 2>/dev/null | wc -l)

    # Background processes
    MONITOR_COUNT=$(pgrep -f -E '(auto-monitor|trading-monitor)' | wc -l)
}

generate_benchmark() {
    cat > "$BENCHMARK_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "date": "$DATE",
  "system": {
    "memory_percent": $MEMORY_PERCENT,
    "memory_available": "$MEMORY_AVAILABLE",
    "cpu_percent": $CPU_PERCENT,
    "disk_percent": $DISK_PERCENT,
    "load_1min": $LOAD_1MIN
  },
  "gateway": {
    "status": "$GATEWAY_STATUS",
    "pid": $GATEWAY_PID,
    "memory_mb": $GATEWAY_MEMORY,
    "cpu_percent": $GATEWAY_CPU
  },
  "api": {
    "status_code": $HTTP_STATUS,
    "latency_ms": $API_LATENCY,
    "available": $([ "$HTTP_STATUS" = "200" ] && echo "true" || echo "false")
  },
  "errors": {
    "last_5_min": $ERRORS_5MIN
  },
  "sessions": {
    "count": $SESSION_COUNT
  },
  "monitors": {
    "running": $MONITOR_COUNT
  }
}
EOF
}

display_results() {
    print_header

    echo -e "${BLUE}Performance Benchmark Results${NC}"
    echo ""
    echo "Timestamp: $(date)"
    echo ""

    echo -e "${GREEN}System Metrics:${NC}"
    echo "  Memory Usage:     $MEMORY_PERCENT% ($MEMORY_AVAILABLE available)"
    echo "  CPU Usage:        $CPU_PERCENT%"
    echo "  Disk Usage:       $DISK_PERCENT%"
    echo "  Load Average:     $LOAD_1MIN"
    echo ""

    echo -e "${GREEN}Gateway Metrics:${NC}"
    echo "  Status:           $GATEWAY_STATUS"
    echo "  Memory:           $GATEWAY_MEMORY MB"
    echo "  CPU:              $GATEWAY_CPU%"
    echo ""

    echo -e "${GREEN}API Metrics:${NC}"
    echo "  Status Code:      $HTTP_STATUS"
    echo "  Latency:          ${API_LATENCY}ms"
    echo ""

    echo -e "${GREEN}Error Metrics:${NC}"
    echo "  Errors (5min):    $ERRORS_5MIN"
    echo ""

    echo -e "${GREEN}Session Metrics:${NC}"
    echo "  Sessions:         $SESSION_COUNT"
    echo ""

    echo -e "${GREEN}Monitor Metrics:${NC}"
    echo "  Running:          $MONITOR_COUNT"
    echo ""

    echo -e "${YELLOW}Benchmark saved to:${NC}"
    echo "  $BENCHMARK_FILE"
    echo ""
}

compare_benchmarks() {
    LATEST=$(ls -t "$BENCHMARK_DIR"/benchmark-*.json 2>/dev/null | head -1)

    if [ -z "$LATEST" ]; then
        echo "No previous benchmarks to compare."
        return
    fi

    echo ""
    echo -e "${BLUE}Comparison with latest benchmark:$(basename $LATEST)${NC}"
    echo ""

    PREV_MEMORY=$(jq '.system.memory_percent' "$LATEST")
    PREV_CPU=$(jq '.system.cpu_percent' "$LATEST")

    MEMORY_CHANGE=$(awk "BEGIN {printf \"%.1f\", $MEMORY_PERCENT - $PREV_MEMORY}")
    CPU_CHANGE=$(awk "BEGIN {printf \"%.1f\", $CPU_PERCENT - $PREV_CPU}")

    if [ $(echo "$MEMORY_CHANGE < 0" | bc -l) -eq 1 ]; then
        MEMORY_COLOR="$GREEN"
        MEMORY_SIGN=""
    else
        MEMORY_COLOR="$YELLOW"
        MEMORY_SIGN="+"
    fi

    if [ $(echo "$CPU_CHANGE < 0" | bc -l) -eq 1 ]; then
        CPU_COLOR="$GREEN"
        CPU_SIGN=""
    else
        CPU_COLOR="$YELLOW"
        CPU_SIGN="+"
    fi

    echo "  Memory Change:   ${MEMORY_COLOR}${MEMORY_SIGN}${MEMORY_CHANGE}%${NC}"
    echo "  CPU Change:      ${CPU_COLOR}${CPU_SIGN}${CPU_CHANGE}%${NC}"
}

show_history() {
    echo ""
    echo -e "${BLUE}Benchmark History:${NC}"
    echo ""

    if [ -d "$BENCHMARK_DIR" ] && [ "$(ls -A $BENCHMARK_DIR/*.json 2>/dev/null)" ]; then
        ls -lt "$BENCHMARK_DIR"/benchmark-*.json 2>/dev/null | head -10 | awk '{
            printf "  %s  %s\n", $9, $6 " " $7 " " $8
        }' | sed 's|.*/||'
    else
        echo "  No benchmarks found"
    fi
}

# Main execution
collect_metrics
generate_benchmark
display_results
compare_benchmarks
show_history

echo -e "${GREEN}✓ Benchmark completed successfully${NC}"
echo ""
echo "To compare specific benchmarks:"
echo "  cat $BENCHMARK_FILE | jq ."
echo ""
echo "To view benchmark history:"
echo "  ls -lt ~/.openclaw/benchmarks/"