#!/bin/bash

# Solana Marketing Suite - Quick Start Script
# This script sets up and initializes all agents

echo "🚀 Solana AI Marketing Suite - Quick Start"
echo "=========================================="

# Check for required tools
check_requirements() {
    echo "✓ Checking requirements..."
    
    if ! command -v node &> /dev/null; then
        echo "✗ Node.js not found. Please install Node.js 18+"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        echo "✗ npm not found. Please install npm"
        exit 1
    fi
    
    echo "  ✓ Node.js version: $(node -v)"
    echo "  ✓ npm version: $(npm -v)"
}

# Install dependencies
install_dependencies() {
    echo ""
    echo "📦 Installing dependencies..."
    npm install @solana/web3.js bs58 tweetnacl axios dotenv
    npm install winston express rate-limiter-flexible
    echo "  ✓ Dependencies installed"
}

# Check environment variables
check_env_vars() {
    echo ""
    echo "🔑 Checking environment variables..."
    
    local missing_vars=()
    
    # Required for all agents
    if [ -z "$SOLANA_RPC_URL" ]; then
        missing_vars+=("SOLANA_RPC_URL")
    fi
    
    if [ -z "$SOLANA_WALLET_PRIVATE_KEY" ]; then
        missing_vars+=("SOLANA_WALLET_PRIVATE_KEY")
    fi
    
    # Optional for specific agents
    if [ -z "$DISCORD_BOT_TOKEN" ]; then
        echo "  ⚠ DISCORD_BOT_TOKEN not set (Community Agent will have limited functionality)"
    fi
    
    if [ -z "$TWITTER_API_KEY" ]; then
        echo "  ⚠ TWITTER_API_KEY not set (Community Agent will have limited functionality)"
    fi
    
    if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
        echo "  ⚠ TELEGRAM_BOT_TOKEN not set (Community Agent will have limited functionality)"
    fi
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        echo ""
        echo "✗ Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        echo ""
        echo "Add them to ~/.openclaw-env:"
        echo "  echo 'SOLANA_RPC_URL=your_rpc_url' >> ~/.openclaw-env"
        echo "  echo 'SOLANA_WALLET_PRIVATE_KEY=your_private_key' >> ~/.openclaw-env"
        exit 1
    fi
    
    echo "  ✓ All required environment variables are set"
}

# Create necessary directories
create_directories() {
    echo ""
    echo "📁 Creating directory structure..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p config
    mkdir -p cache
    
    echo "  ✓ Directories created"
}

# Initialize configuration files
init_configs() {
    echo ""
    echo "⚙️  Initializing configuration files..."
    
    # Airdrop config
    if [ ! -f config/airdrop-config.json ]; then
        cat > config/airdrop-config.json << 'EOF'
{
  "targetWallets": {
    "whales": { "minBalance": 10000, "reward": 500 },
    "active": { "minBalance": 100, "reward": 50 },
    "casual": { "minBalance": 10, "reward": 5 }
  },
  "airdropAmount": 10000,
  "batchSize": 100,
  "delayBetweenBatches": 5000,
  "gasReserve": 0.1
}
EOF
        echo "  ✓ Created config/airdrop-config.json"
    fi
    
    # Community config
    if [ ! -f config/community-config.json ]; then
        cat > config/community-config.json << 'EOF'
{
  "posting": {
    "twitter": { "enabled": true, "interval": 3600000 },
    "discord": { "enabled": true, "interval": 1800000 },
    "telegram": { "enabled": true, "interval": 3600000 }
  },
  "hashtags": ["#Solana", "#DeFi", "#Crypto", "#Airdrop"],
  "bestTimes": ["09:00", "12:00", "18:00", "21:00"],
  "autoEngage": true,
  "sentimentThreshold": 0.6
}
EOF
        echo "  ✓ Created config/community-config.json"
    fi
    
    # Analytics config
    if [ ! -f config/analytics-config.json ]; then
        cat > config/analytics-config.json << 'EOF'
{
  "tracking": {
    "walletConnections": true,
    "tokenTransfers": true,
    "socialEngagement": true,
    "websiteTraffic": true
  },
  "reporting": {
    "daily": true,
    "weekly": true,
    "monthly": true
  },
  "retentionDays": 90,
  "sampleRate": 1.0
}
EOF
        echo "  ✓ Created config/analytics-config.json"
    fi
    
    # Influencer config
    if [ ! -f config/influencer-config.json ]; then
        cat > config/influencer-config.json << 'EOF'
{
  "budget": {
    "total": 10000,
    "perCampaign": 1000,
    "minROI": 2.0
  },
  "criteria": {
    "minFollowers": 10000,
    "minEngagement": 3.0,
    "categories": ["defi", "nft", "trading"]
  },
  "platforms": ["twitter", "youtube", "discord"],
  "paymentStructure": "performance_based"
}
EOF
        echo "  ✓ Created config/influencer-config.json"
    fi
    
    # NFT config
    if [ ! -f config/nft-config.json ]; then
        cat > config/nft-config.json << 'EOF'
{
  "tiers": {
    "bronze": { "requiredTokens": 1000, "supply": 1000, "benefits": ["discord_role", "early_access"] },
    "silver": { "requiredTokens": 5000, "supply": 500, "benefits": ["bronze", "monthly_airdrop", "voting"] },
    "gold": { "requiredTokens": 10000, "supply": 100, "benefits": ["silver", "founder_access", "1on1"] }
  },
  "minting": {
    "price": 0.1,
    "startDate": "2026-06-01T00:00:00Z",
    "duration": "30d"
  }
}
EOF
        echo "  ✓ Created config/nft-config.json"
    fi
    
    # Quest config
    if [ ! -f config/quest-config.json ]; then
        cat > config/quest-config.json << 'EOF'
{
  "welcomeQuest": {
    "name": "Welcome Quest",
    "tasks": [
      { "type": "twitter_follow", "reward": 50 },
      { "type": "discord_join", "reward": 30 },
      { "type": "telegram_join", "reward": 20 }
    ],
    "timeLimit": "7d"
  },
  "tradingQuest": {
    "name": "Trading Master",
    "tasks": [
      { "type": "swap", "amount": 100, "reward": 200 },
      { "type": "provide_liquidity", "amount": 500, "reward": 300 }
    ],
    "prerequisites": ["welcomeQuest"]
  },
  "leaderboard": {
    "enabled": true,
    "rewards": [1000, 500, 250, 100, 50],
    "resetInterval": "monthly"
  }
}
EOF
        echo "  ✓ Created config/quest-config.json"
    fi
    
    # Content config
    if [ ! -f config/content-config.json ]; then
        cat > config/content-config.json << 'EOF'
{
  "generation": {
    "blogPosts": { "frequency": "weekly", "wordCount": 1500 },
    "twitterThreads": { "frequency": "daily", "tweetCount": 8 },
    "youtubeScripts": { "frequency": "biweekly", "duration": "10m" }
  },
  "topics": [
    "tokenomics",
    "roadmap_updates",
    "market_analysis",
    "user_tutorials",
    "community_spotlight"
  ],
  "seo": {
    "keywords": ["Solana", "DeFi", "blockchain", "cryptocurrency"],
    "optimizeFor": "google"
  }
}
EOF
        echo "  ✓ Created config/content-config.json"
    fi
}

# Test connections
test_connections() {
    echo ""
    echo "🔌 Testing connections..."
    
    # Test Solana RPC
    node -e "
        const { Connection } = require('@solana/web3.js');
        const conn = new Connection(process.env.SOLANA_RPC_URL);
        conn.getHealth().then(() => {
            console.log('  ✓ Solana RPC connection successful');
        }).catch(err => {
            console.log('  ✗ Solana RPC connection failed:', err.message);
        });
    "
    
    # Test wallet
    node -e "
        const { Connection, Keypair } = require('@solana/web3.js');
        const bs58 = require('bs58');
        
        try {
            const secretKey = bs58.decode(process.env.SOLANA_WALLET_PRIVATE_KEY);
            const wallet = Keypair.fromSecretKey(secretKey);
            console.log('  ✓ Wallet loaded successfully:', wallet.publicKey.toString().slice(0, 8) + '...');
        } catch (err) {
            console.log('  ✗ Wallet loading failed:', err.message);
        }
    "
}

# Display next steps
show_next_steps() {
    echo ""
    echo "✅ Setup Complete!"
    echo "=================="
    echo ""
    echo "Next Steps:"
    echo ""
    echo "1. Start Individual Agents:"
    echo "   node scripts/agent-airdrop.js"
    echo "   node scripts/agent-community.js"
    echo "   node scripts/agent-analytics.js"
    echo ""
    echo "2. Run All Agents (Background):"
    echo "   ./start-all-agents.sh"
    echo ""
    echo "3. Configure Settings:"
    echo "   Edit files in config/ directory"
    echo ""
    echo "4. Monitor Logs:"
    echo "   tail -f logs/*.log"
    echo ""
    echo "5. Check Status:"
    echo "   ./scripts/status-check.sh"
    echo ""
    echo "📚 Documentation: SETUP_GUIDE.md"
    echo "💡 Quick Examples: EXAMPLES.md"
    echo ""
}

# Main execution
main() {
    check_requirements
    install_dependencies
    check_env_vars
    create_directories
    init_configs
    test_connections
    show_next_steps
}

main