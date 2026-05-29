#!/bin/bash

# Solana Marketing Suite - Status Check Script
# Provides overview of all agent statuses and metrics

echo "========================================="
echo "📊 Solana Marketing Suite - Status Check"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running
check_process() {
    local process_name=$1
    local pid=$(pgrep -f "$process_name")
    
    if [ -n "$pid" ]; then
        echo -e "${GREEN}✓${NC} $process_name is running (PID: $pid)"
        return 0
    else
        echo -e "${RED}✗${NC} $process_name is not running"
        return 1
    fi
}

# Check environment variables
check_env() {
    echo -e "${BLUE}🔑 Environment Variables${NC}"
    echo "-----------------------------------"
    
    # Required
    if [ -n "$SOLANA_RPC_URL" ]; then
        echo -e "${GREEN}✓${NC} SOLANA_RPC_URL is set"
    else
        echo -e "${RED}✗${NC} SOLANA_RPC_URL is not set"
    fi
    
    if [ -n "$SOLANA_WALLET_PRIVATE_KEY" ]; then
        echo -e "${GREEN}✓${NC} SOLANA_WALLET_PRIVATE_KEY is set"
    else
        echo -e "${RED}✗${NC} SOLANA_WALLET_PRIVATE_KEY is not set"
    fi
    
    # Optional
    [ -n "$DISCORD_BOT_TOKEN" ] && echo -e "${GREEN}✓${NC} DISCORD_BOT_TOKEN is set" || echo -e "${YELLOW}○${NC} DISCORD_BOT_TOKEN not set"
    [ -n "$TWITTER_API_KEY" ] && echo -e "${GREEN}✓${NC} TWITTER_API_KEY is set" || echo -e "${YELLOW}○${NC} TWITTER_API_KEY not set"
    [ -n "$TELEGRAM_BOT_TOKEN" ] && echo -e "${GREEN}✓${NC} TELEGRAM_BOT_TOKEN is set" || echo -e "${YELLOW}○${NC} TELEGRAM_BOT_TOKEN not set"
    
    echo ""
}

# Check agent processes
check_agents() {
    echo -e "${BLUE}🤖 Agent Status${NC}"
    echo "-----------------------------------"
    
    check_process "agent-airdrop.js"
    check_process "agent-community.js"
    check_process "agent-analytics.js"
    check_process "agent-influencer.js"
    check_process "agent-nft.js"
    check_process "agent-quest.js"
    check_process "agent-content.js"
    
    echo ""
}

# Check Solana connection
check_solana() {
    echo -e "${BLUE}🌐 Solana Network${NC}"
    echo "-----------------------------------"
    
    if [ -n "$SOLANA_RPC_URL" ]; then
        # Test RPC connection
        response=$(curl -s -X POST "$SOLANA_RPC_URL" \
            -H "Content-Type: application/json" \
            -d '{"jsonrpc":"2.0","id":1,"method":"getHealth"}' 2>&1)
        
        if echo "$response" | grep -q '"result":"ok"'; then
            echo -e "${GREEN}✓${NC} Solana RPC connected"
            
            # Get slot
            slot=$(curl -s -X POST "$SOLANA_RPC_URL" \
                -H "Content-Type: application/json" \
                -d '{"jsonrpc":"2.0","id":1,"method":"getSlot"}' | jq -r '.result')
            echo -e "  Current slot: ${GREEN}$slot${NC}"
        else
            echo -e "${RED}✗${NC} Solana RPC connection failed"
        fi
    fi
    
    echo ""
}

# Check wallet
check_wallet() {
    echo -e "${BLUE}💼 Wallet Status${NC}"
    echo "-----------------------------------"
    
    if [ -n "$SOLANA_WALLET_PRIVATE_KEY" ]; then
        # Get wallet address
        wallet_info=$(node -e "
            const { Connection, Keypair, LAMPORTS_PER_SOL } = require('@solana/web3.js');
            const bs58 = require('bs58');
            
            (async () => {
                try {
                    const secretKey = bs58.decode(process.env.SOLANA_WALLET_PRIVATE_KEY);
                    const wallet = Keypair.fromSecretKey(secretKey);
                    const conn = new Connection(process.env.SOLANA_RPC_URL);
                    const balance = await conn.getBalance(wallet.publicKey);
                    
                    console.log(JSON.stringify({
                        address: wallet.publicKey.toString(),
                        balance: balance / LAMPORTS_PER_SOL
                    }));
                } catch (err) {
                    console.log(JSON.stringify({ error: err.message }));
                }
            })();
        " 2>&1)
        
        if echo "$wallet_info" | jq -e '.address' > /dev/null 2>&1; then
            address=$(echo "$wallet_info" | jq -r '.address')
            balance=$(echo "$wallet_info" | jq -r '.balance')
            
            echo -e "${GREEN}✓${NC} Wallet loaded"
            echo -e "  Address: ${GREEN}${address:0:8}...${address: -8}${NC}"
            echo -e "  Balance: ${GREEN}${balance} SOL${NC}"
        else
            echo -e "${RED}✗${NC} Failed to load wallet"
        fi
    fi
    
    echo ""
}

# Check logs
check_logs() {
    echo -e "${BLUE}📋 Recent Logs${NC}"
    echo "-----------------------------------"
    
    if [ -d "logs" ]; then
        for log in logs/*.log; do
            if [ -f "$log" ]; then
                echo -e "\n${YELLOW}$(basename $log)${NC}:"
                tail -n 5 "$log"
            fi
        done
    else
        echo "No logs directory found"
    fi
    
    echo ""
}

# Check metrics
check_metrics() {
    echo -e "${BLUE}📈 Quick Metrics${NC}"
    echo "-----------------------------------"
    
    # Check if data files exist
    if [ -f "data/community-stats.json" ]; then
        echo -e "\n${YELLOW}Community Stats:${NC}"
        jq '.' data/community-stats.json 2>/dev/null || echo "  Unable to parse"
    fi
    
    if [ -f "data/airdrop-stats.json" ]; then
        echo -e "\n${YELLOW}Airdrop Stats:${NC}"
        jq '.' data/airdrop-stats.json 2>/dev/null || echo "  Unable to parse"
    fi
    
    if [ -f "data/analytics-stats.json" ]; then
        echo -e "\n${YELLOW}Analytics Stats:${NC}"
        jq '.' data/analytics-stats.json 2>/dev/null || echo "  Unable to parse"
    fi
    
    echo ""
}

# Check disk usage
check_disk() {
    echo -e "${BLUE}💾 Disk Usage${NC}"
    echo "-----------------------------------"
    
    df -h . | tail -n 1 | awk '{print "  Used: "$3" / "$2" ("$5")"}'
    
    echo ""
    echo "Directory sizes:"
    du -sh logs data config cache 2>/dev/null | awk '{print "  "$2": "$1}'
    
    echo ""
}

# Main
main() {
    check_env
    check_agents
    check_solana
    check_wallet
    check_metrics
    check_logs
    check_disk
    
    echo "========================================="
    echo "✅ Status check complete"
    echo "========================================="
}

# Run
main