#!/bin/bash

# Health Check Script for Solana Marketing Suite
# Monitors all agents and services, sends alerts on failures

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
LOG_FILE="logs/health-check.log"
ALERT_WEBHOOK="${DISCORD_WEBHOOK_URL:-}"
CHECK_INTERVAL=60  # seconds
MAX_RETRIES=3

# Metrics
HEALTH_STATUS="healthy"
ISSUES=()

log() {
    local message="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo -e "$message"
    echo "$message" >> "$LOG_FILE"
}

send_alert() {
    local title="$1"
    local message="$2"
    local color="$3"
    
    if [ -n "$ALERT_WEBHOOK" ]; then
        curl -s -X POST "$ALERT_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{
                \"embeds\": [{
                    \"title\": \"$title\",
                    \"description\": \"$message\",
                    \"color\": $color,
                    \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
                }]
            }" > /dev/null
    fi
}

check_process() {
    local name="$1"
    local pattern="$2"
    
    if pgrep -f "$pattern" > /dev/null; then
        local pid=$(pgrep -f "$pattern")
        log "${GREEN}✓${NC} $name is running (PID: $pid)"
        return 0
    else
        log "${RED}✗${NC} $name is NOT running"
        ISSUES+=("$name is not running")
        HEALTH_STATUS="unhealthy"
        return 1
    fi
}

check_port() {
    local service="$1"
    local port="$2"
    
    if nc -z localhost "$port" 2>/dev/null; then
        log "${GREEN}✓${NC} $service is listening on port $port"
        return 0
    else
        log "${RED}✗${NC} $service is NOT listening on port $port"
        ISSUES+=("$service not responding on port $port")
        HEALTH_STATUS="unhealthy"
        return 1
    fi
}

check_url() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$response" = "$expected_status" ]; then
        log "${GREEN}✓${NC} $name is responding (HTTP $response)"
        return 0
    else
        log "${RED}✗${NC} $name returned HTTP $response (expected $expected_status)"
        ISSUES+=("$name returned HTTP $response")
        HEALTH_STATUS="unhealthy"
        return 1
    fi
}

check_disk_space() {
    local threshold="${1:-90}"
    
    local usage=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
    
    if [ "$usage" -lt "$threshold" ]; then
        log "${GREEN}✓${NC} Disk usage: ${usage}%"
        return 0
    else
        log "${RED}✗${NC} Disk usage: ${usage}% (threshold: ${threshold}%)"
        ISSUES+=("Disk usage at ${usage}%")
        HEALTH_STATUS="unhealthy"
        return 1
    fi
}

check_memory() {
    local threshold="${1:-90}"
    
    local mem_info=$(free | grep Mem)
    local total=$(echo $mem_info | awk '{print $2}')
    local used=$(echo $mem_info | awk '{print $3}')
    local usage=$((used * 100 / total))
    
    if [ "$usage" -lt "$threshold" ]; then
        log "${GREEN}✓${NC} Memory usage: ${usage}%"
        return 0
    else
        log "${YELLOW}⚠${NC} Memory usage: ${usage}% (threshold: ${threshold}%)"
        ISSUES+=("Memory usage at ${usage}%")
        return 1
    fi
}

check_solana_connection() {
    local rpc_url="${SOLANA_RPC_URL:-https://api.mainnet-beta.solana.com}"
    
    local response=$(curl -s -X POST "$rpc_url" \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","id":1,"method":"getHealth"}' \
        --max-time 10 2>/dev/null || echo '{"error":"timeout"}')
    
    if echo "$response" | grep -q '"result":"ok"'; then
        log "${GREEN}✓${NC} Solana RPC connection healthy"
        return 0
    else
        log "${RED}✗${NC} Solana RPC connection failed"
        ISSUES+=("Solana RPC connection failed")
        HEALTH_STATUS="unhealthy"
        return 1
    fi
}

check_wallet_balance() {
    if [ -z "$SOLANA_WALLET_PRIVATE_KEY" ]; then
        log "${YELLOW}○${NC} Wallet not configured"
        return 0
    fi
    
    local balance=$(node -e "
        const { Connection, Keypair, LAMPORTS_PER_SOL } = require('@solana/web3.js');
        const bs58 = require('bs58');
        
        (async () => {
            try {
                const secretKey = bs58.decode(process.env.SOLANA_WALLET_PRIVATE_KEY);
                const wallet = Keypair.fromSecretKey(secretKey);
                const conn = new Connection(process.env.SOLANA_RPC_URL);
                const bal = await conn.getBalance(wallet.publicKey);
                console.log(bal / LAMPORTS_PER_SOL);
            } catch (err) {
                console.log('error');
            }
        })();
    " 2>/dev/null || echo "error")
    
    if [ "$balance" != "error" ] && [ $(echo "$balance > 0.1" | bc -l 2>/dev/null || echo "0") -eq 1 ]; then
        log "${GREEN}✓${NC} Wallet balance: ${balance} SOL"
        return 0
    else
        log "${RED}✗${NC} Wallet balance low or error: ${balance} SOL"
        ISSUES+=("Wallet balance low: ${balance} SOL")
        HEALTH_STATUS="unhealthy"
        return 1
    fi
}

check_redis() {
    if command -v redis-cli > /dev/null; then
        if redis-cli ping > /dev/null 2>&1; then
            log "${GREEN}✓${NC} Redis is running"
            return 0
        else
            log "${YELLOW}○${NC} Redis not running (optional)"
            return 0
        fi
    else
        log "${YELLOW}○${NC} Redis not installed (optional)"
        return 0
    fi
}

check_postgres() {
    if command -v psql > /dev/null; then
        if psql -c "SELECT 1" > /dev/null 2>&1; then
            log "${GREEN}✓${NC} PostgreSQL is running"
            return 0
        else
            log "${YELLOW}○${NC} PostgreSQL not running (optional)"
            return 0
        fi
    else
        log "${YELLOW}○${NC} PostgreSQL not installed (optional)"
        return 0
    fi
}

check_agent_logs() {
    local log_dir="logs"
    local error_count=0
    
    if [ -d "$log_dir" ]; then
        # Check for errors in last hour
        error_count=$(grep -r "ERROR" "$log_dir"/*.log 2>/dev/null | \
            grep "$(date '+%Y-%m-%d %H')" | wc -l)
        
        if [ "$error_count" -lt 10 ]; then
            log "${GREEN}✓${NC} No critical errors in logs ($error_count errors in last hour)"
            return 0
        else
            log "${YELLOW}⚠${NC} High error count: $error_count errors in last hour"
            ISSUES+=("High error count: $error_count")
            return 1
        fi
    fi
}

check_api_endpoints() {
    # Check analytics dashboard
    if curl -s http://localhost:3000/health > /dev/null 2>&1; then
        log "${GREEN}✓${NC} Analytics API responding"
    else
        log "${YELLOW}○${NC} Analytics API not running (start with: make start-analytics)"
    fi
}

generate_report() {
    local report_file="logs/health-report-$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$report_file" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "status": "$HEALTH_STATUS",
    "issues": $(printf '%s\n' "${ISSUES[@]}" | jq -R . | jq -s .),
    "checks": {
        "agents": {
            "airdrop": $(pgrep -f "agent-airdrop" > /dev/null && echo "true" || echo "false"),
            "community": $(pgrep -f "agent-community" > /dev/null && echo "true" || echo "false"),
            "analytics": $(pgrep -f "agent-analytics" > /dev/null && echo "true" || echo "false"),
            "influencer": $(pgrep -f "agent-influencer" > /dev/null && echo "true" || echo "false"),
            "nft": $(pgrep -f "agent-nft" > /dev/null && echo "true" || echo "false"),
            "quest": $(pgrep -f "agent-quest" > /dev/null && echo "true" || echo "false"),
            "content": $(pgrep -f "agent-content" > /dev/null && echo "true" || echo "false")
        },
        "system": {
            "disk_usage": "$(df -h . | tail -1 | awk '{print $5}')",
            "memory_usage": "$(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100}')",
            "load_average": "$(cat /proc/loadavg | awk '{print $1}')"
        }
    }
}
EOF
    
    log "Report saved to $report_file"
}

run_checks() {
    log "${BLUE}════════════════════════════════════════${NC}"
    log "${BLUE}     Solana Marketing Suite - Health Check${NC}"
    log "${BLUE}════════════════════════════════════════${NC}"
    log ""
    
    # Agent checks
    log "${YELLOW}Agent Status:${NC}"
    check_process "Airdrop Agent" "agent-airdrop.js"
    check_process "Community Agent" "agent-community.js"
    check_process "Analytics Agent" "agent-analytics.js"
    check_process "Influencer Agent" "agent-influencer.js"
    check_process "NFT Agent" "agent-nft.js"
    check_process "Quest Agent" "agent-quest.js"
    check_process "Content Agent" "agent-content.js"
    log ""
    
    # Service checks
    log "${YELLOW}Service Status:${NC}"
    check_port "Analytics Dashboard" 3000
    check_url "Health Endpoint" "http://localhost:3000/health" 200
    log ""
    
    # External connectivity
    log "${YELLOW}External Connectivity:${NC}"
    check_solana_connection
    check_wallet_balance
    log ""
    
    # System health
    log "${YELLOW}System Health:${NC}"
    check_disk_space 90
    check_memory 90
    check_redis
    check_postgres
    log ""
    
    # Logs check
    log "${YELLOW}Log Analysis:${NC}"
    check_agent_logs
    log ""
    
    # Summary
    log "${BLUE}════════════════════════════════════════${NC}"
    if [ "$HEALTH_STATUS" = "healthy" ]; then
        log "${GREEN}✓ Overall Status: HEALTHY${NC}"
    else
        log "${RED}✗ Overall Status: UNHEALTHY${NC}"
        log "${RED}Issues Found:${NC}"
        for issue in "${ISSUES[@]}"; do
            log "  - $issue"
        done
        
        # Send alert
        send_alert "⚠️ Health Check Failed" "$(IFS=', '; echo "${ISSUES[*]}")" 15158332
    fi
    log "${BLUE}════════════════════════════════════════${NC}"
    
    # Generate report
    generate_report
}

# Continuous monitoring mode
monitor() {
    log "Starting continuous monitoring (interval: ${CHECK_INTERVAL}s)..."
    
    while true; do
        # Reset status
        HEALTH_STATUS="healthy"
        ISSUES=()
        
        run_checks
        
        sleep "$CHECK_INTERVAL"
    done
}

# CLI
case "${1:-check}" in
    check)
        run_checks
        ;;
    monitor)
        monitor
        ;;
    report)
        generate_report
        ;;
    *)
        echo "Usage: $0 {check|monitor|report}"
        echo ""
        echo "Commands:"
        echo "  check   - Run health checks once"
        echo "  monitor - Continuous monitoring"
        echo "  report  - Generate health report"
        exit 1
        ;;
esac