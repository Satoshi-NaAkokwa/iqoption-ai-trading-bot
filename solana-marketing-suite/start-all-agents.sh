#!/bin/bash

# Start All Marketing Agents
# This script starts all agents in background mode

echo "🚀 Starting Solana Marketing Suite Agents..."
echo "============================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to project directory
cd "$PROJECT_DIR"

# Check environment variables
if [ -z "$SOLANA_RPC_URL" ] || [ -z "$SOLANA_WALLET_PRIVATE_KEY" ]; then
    echo -e "${RED}✗ Missing required environment variables${NC}"
    echo "  Set SOLANA_RPC_URL and SOLANA_WALLET_PRIVATE_KEY in ~/.openclaw-env"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Function to start agent
start_agent() {
    local agent_name=$1
    local script_name=$2
    
    echo -e "${YELLOW}Starting $agent_name...${NC}"
    
    # Check if already running
    if pgrep -f "$script_name" > /dev/null; then
        echo -e "${GREEN}✓ $agent_name already running${NC}"
        return 0
    fi
    
    # Start in background
    nohup node "$SCRIPT_DIR/$script_name" > "logs/${script_name%.js}.log" 2>&1 &
    local pid=$!
    
    # Wait a moment and check if process is still running
    sleep 2
    if ps -p $pid > /dev/null; then
        echo -e "${GREEN}✓ $agent_name started (PID: $pid)${NC}"
        echo $pid > "logs/${script_name%.js}.pid"
    else
        echo -e "${RED}✗ $agent_name failed to start${NC}"
        tail -n 20 "logs/${script_name%.js}.log"
        return 1
    fi
}

# Stop all agents
stop_all() {
    echo -e "${YELLOW}Stopping all agents...${NC}"
    
    for pid_file in logs/*.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            if ps -p $pid > /dev/null 2>&1; then
                kill $pid
                echo -e "${GREEN}✓ Stopped PID $pid${NC}"
            fi
            rm "$pid_file"
        fi
    done
    
    # Kill any remaining agent processes
    pkill -f "agent-.*\.js" 2>/dev/null
    
    echo -e "${GREEN}✓ All agents stopped${NC}"
    exit 0
}

# Handle Ctrl+C
trap stop_all INT TERM

# Check for stop argument
if [ "$1" = "stop" ]; then
    stop_all
fi

# Check for status argument
if [ "$1" = "status" ]; then
    echo "Agent Status:"
    echo "-------------"
    
    for agent in airdrop community analytics influencer nft quest content; do
        if pgrep -f "agent-${agent}.js" > /dev/null; then
            pid=$(pgrep -f "agent-${agent}.js")
            echo -e "${GREEN}✓ agent-${agent}.js running (PID: $pid)${NC}"
        else
            echo -e "${RED}✗ agent-${agent}.js not running${NC}"
        fi
    done
    
    exit 0
fi

# Start all agents
echo ""
start_agent "Airdrop Agent" "agent-airdrop.js"
start_agent "Community Agent" "agent-community.js"
start_agent "Analytics Agent" "agent-analytics.js"
start_agent "Influencer Agent" "agent-influencer.js"
start_agent "NFT Agent" "agent-nft.js"
start_agent "Quest Agent" "agent-quest.js"
start_agent "Content Agent" "agent-content.js"

echo ""
echo "============================================"
echo -e "${GREEN}✅ All agents started!${NC}"
echo ""
echo "Monitor logs:"
echo "  tail -f logs/*.log"
echo ""
echo "Check status:"
echo "  ./start-all-agents.sh status"
echo ""
echo "Stop all agents:"
echo "  ./start-all-agents.sh stop"
echo ""
echo "Or press Ctrl+C to stop all agents"
echo "============================================"

# Keep script running to handle signals
if [ "$1" = "--foreground" ]; then
    echo ""
    echo "Running in foreground mode..."
    echo "Press Ctrl+C to stop all agents"
    echo ""
    
    # Tail all logs
    tail -f logs/*.log
fi

# Wait for all background processes
wait