# Solana AI Marketing Suite

**Complete AI-powered marketing automation for Solana tokens**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Solana](https://img.shields.io/badge/Solana-Compatible-purple)

---

## 🎯 Overview

The Solana AI Marketing Suite is a comprehensive toolkit for launching and scaling Solana token projects. It includes 7 specialized AI agents that automate every aspect of token marketing:

1. **🪂 Airdrop Agent** - Smart wallet targeting and distribution
2. **💬 Community Agent** - Social media automation across Discord, Twitter, Telegram
3. **📊 Analytics Agent** - Real-time tracking and optimization
4. **📢 Influencer Agent** - Campaign management and ROI tracking
5. **🎨 NFT Agent** - NFT-gated features and utility
6. **🎯 Quest Agent** - Gamified user onboarding
7. **✍️ Content Agent** - AI content generation at scale

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn
- Solana wallet with private key
- (Optional) Discord bot token
- (Optional) Twitter API credentials
- (Optional) Telegram bot token

### Installation

```bash
# Clone or navigate to the suite
cd solana-marketing-suite

# Run quick start script
chmod +x quick-start.sh
./quick-start.sh
```

### Configuration

Add your credentials to `~/.openclaw-env`:

```bash
# Required
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_WALLET_PRIVATE_KEY=your_private_key_here

# Optional (for Community Agent)
DISCORD_BOT_TOKEN=your_discord_bot_token
TWITTER_API_KEY=your_twitter_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

### Start All Agents

```bash
# Start all agents in background
chmod +x start-all-agents.sh
./start-all-agents.sh

# Check status
./start-all-agents.sh status

# Stop all agents
./start-all-agents.sh stop
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [SETUP_GUIDE.md](./SETUP_GUIDE.md) | Detailed setup instructions |
| [EXAMPLES.md](./EXAMPLES.md) | Practical use cases and examples |
| [API_REFERENCE.md](./API_REFERENCE.md) | API documentation (coming soon) |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Production deployment guide (coming soon) |

---

## 🤖 Agent Details

### 1. Airdrop Agent (`agent-airdrop.js`)

**Purpose**: Automate token distribution with smart targeting.

**Features**:
- Wallet targeting based on SOL balance and activity
- Tiered reward system (whales, active users, casual users)
- Batch processing for gas optimization
- Claim tracking and analytics
- Anti-bot protection

**Usage**:
```bash
# Analyze target wallets
node scripts/agent-airdrop.js analyze

# Execute airdrop
node scripts/agent-airdrop.js execute --amount 10000

# Track claims
node scripts/agent-airdrop.js track
```

**Configuration**: `config/airdrop-config.json`

---

### 2. Community Agent (`agent-community.js`)

**Purpose**: Automate community management across multiple platforms.

**Features**:
- Discord: Welcome messages, moderation, daily digests
- Twitter: Auto-posting, engagement, thread creation
- Telegram: Announcements, price alerts, community updates
- Cross-platform content distribution
- Sentiment analysis

**Usage**:
```bash
# Start Discord automation
node scripts/agent-community.js discord

# Start Twitter automation
node scripts/agent-community.js twitter

# Start Telegram automation
node scripts/agent-community.js telegram
```

**Configuration**: `config/community-config.json`

---

### 3. Analytics Agent (`agent-analytics.js`)

**Purpose**: Track and optimize marketing performance.

**Features**:
- Real-time metrics tracking
- Multi-channel attribution
- ROI calculation
- A/B testing
- Automated reporting
- Anomaly detection

**Usage**:
```bash
# Start analytics server
node scripts/agent-analytics.js server --port 3000

# Generate report
node scripts/agent-analytics.js report --period 30d

# View dashboard
open http://localhost:3000/dashboard
```

**Configuration**: `config/analytics-config.json`

---

### 4. Influencer Agent (`agent-influencer.js`)

**Purpose**: Manage influencer relationships and campaigns.

**Features**:
- Influencer discovery and vetting
- Deal negotiation automation
- Campaign tracking and analytics
- Performance-based payments
- ROI optimization

**Usage**:
```bash
# Discover influencers
node scripts/agent-influencer.js discover --category defi

# Launch campaign
node scripts/agent-influencer.js launch --config config/influencer-campaign.json

# Track performance
node scripts/agent-influencer.js track --campaign launch-promotion
```

**Configuration**: `config/influencer-config.json`

---

### 5. NFT Agent (`agent-nft.js`)

**Purpose**: Create NFT-gated utility and exclusive features.

**Features**:
- NFT collection deployment
- Token-gated access control
- Tiered membership system
- Cross-platform NFT integration
- Royalty management

**Usage**:
```bash
# Deploy NFT collection
node scripts/agent-nft.js deploy --config config/nft-gating.json

# Setup gating rules
node scripts/agent-nft.js setup-gates

# Mint NFTs
node scripts/agent-nft.js mint --tier gold
```

**Configuration**: `config/nft-config.json`

---

### 6. Quest Agent (`agent-quest.js`)

**Purpose**: Gamify user onboarding and engagement.

**Features**:
- Interactive quests and challenges
- Achievement system
- Leaderboards
- Referral tracking
- Reward distribution

**Usage**:
```bash
# Create quest
node scripts/agent-quest.js create --config config/quest-onboarding.json

# Launch quest
node scripts/agent-quest.js launch --quest new_user_journey

# Monitor progress
node scripts/agent-quest.js monitor --live
```

**Configuration**: `config/quest-config.json`

---

### 7. Content Agent (`agent-content.js`)

**Purpose**: Automate content creation and distribution.

**Features**:
- Blog post generation
- Twitter thread creation
- YouTube script writing
- SEO optimization
- Content calendar management

**Usage**:
```bash
# Generate content
node scripts/agent-content.js generate --type blog --topic "Tokenomics"

# Auto-publish
node scripts/agent-content.js autopublish

# Create content calendar
node scripts/agent-content.js calendar
```

**Configuration**: `config/content-config.json`

---

## 📊 Architecture

```
solana-marketing-suite/
├── scripts/
│   ├── agent-airdrop.js        # Airdrop automation
│   ├── agent-community.js      # Community management
│   ├── agent-analytics.js      # Analytics & tracking
│   ├── agent-influencer.js     # Influencer marketing
│   ├── agent-nft.js           # NFT utility
│   ├── agent-quest.js         # Quest/gamification
│   ├── agent-content.js       # Content generation
│   ├── launch-30-days.js      # 30-day orchestrator
│   └── status-check.sh        # Status monitoring
├── config/
│   ├── airdrop-config.json
│   ├── community-config.json
│   ├── analytics-config.json
│   ├── influencer-config.json
│   ├── nft-config.json
│   ├── quest-config.json
│   └── content-config.json
├── logs/
│   └── *.log                  # Agent logs
├── data/
│   └── *.json                 # Runtime data
├── cache/
│   └── *                      # Cached responses
├── quick-start.sh             # Setup script
├── start-all-agents.sh        # Start all agents
├── SETUP_GUIDE.md             # Detailed setup guide
├── EXAMPLES.md                # Practical examples
└── README.md                  # This file
```

---

## 🔧 Configuration

### Global Configuration

All agents share these environment variables:

```bash
# Solana Configuration
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_WALLET_PRIVATE_KEY=your_private_key

# Optional: Custom RPC (better rate limits)
SOLANA_RPC_URL=https://your-custom-rpc.com

# Optional: Helius RPC (recommended)
SOLANA_RPC_URL=https://rpc.helius.io/?api-key=your_key
```

### Agent-Specific Configuration

Each agent has its own config file in `config/`:

- **airdrop-config.json**: Wallet targeting criteria, reward tiers, batch settings
- **community-config.json**: Posting schedules, hashtags, moderation rules
- **analytics-config.json**: Metrics to track, reporting frequency
- **influencer-config.json**: Budget, criteria, deal templates
- **nft-config.json**: Collection details, tier benefits, gating rules
- **quest-config.json**: Quest steps, rewards, prerequisites
- **content-config.json**: Content types, topics, SEO keywords

---

## 🎮 30-Day Launch Plan

Execute a complete token launch in 30 days:

```bash
# Create launch config
echo '{
  "startDate": "2026-06-01",
  "budget": {
    "airdrop": 10000,
    "influencers": 5000,
    "content": 2000
  }
}' > config/launch-config.json

# Run 30-day orchestrator
node scripts/launch-30-days.js --start-date 2026-06-01
```

The orchestrator will automatically:
- **Week 1**: Setup and preparation
- **Week 2**: Community building and early adopters
- **Week 3**: Public launch and growth
- **Week 4**: Optimization and retention

See [EXAMPLES.md](./EXAMPLES.md#complete-launch-strategy) for detailed breakdown.

---

## 📈 Monitoring & Analytics

### Real-time Dashboard

```bash
# Start analytics dashboard
node scripts/agent-analytics.js server --port 3000

# Open in browser
open http://localhost:3000/dashboard
```

### Status Checks

```bash
# Check all agent statuses
./scripts/status-check.sh

# Check specific agent
node scripts/agent-airdrop.js status
```

### Logs

```bash
# View all logs
tail -f logs/*.log

# View specific agent log
tail -f logs/agent-airdrop.log

# Search logs
grep "ERROR" logs/*.log
```

---

## 🔒 Security Best Practices

### Private Key Management

```bash
# ✅ DO: Use environment variables
echo 'SOLANA_WALLET_PRIVATE_KEY=xxx' >> ~/.openclaw-env

# ✅ DO: Set proper permissions
chmod 600 ~/.openclaw-env

# ❌ DON'T: Commit private keys to git
# ❌ DON'T: Share keys in plain text
# ❌ DON'T: Use main wallet - create dedicated marketing wallet
```

### Rate Limiting

All agents implement rate limiting:

```javascript
// Built-in rate limiting
const rateLimiter = {
    maxRequests: 100,
    perWindow: 60000, // 1 minute
    backoff: 'exponential'
};
```

### Anti-Bot Protection

Airdrop agent includes anti-bot measures:

```json
{
  "antiBot": {
    "captcha": true,
    "walletAge": "7d",
    "maxClaimsPerIP": 1,
    "suspiciousActivityDetection": true
  }
}
```

---

## 💰 Cost Estimation

### Solana Network Fees

- **Transaction fee**: ~0.000005 SOL ($0.001)
- **Airdrop (1000 wallets)**: ~0.005 SOL ($1)
- **Token creation**: ~0.02 SOL ($4)

### Agent Operational Costs

| Agent | Monthly Cost | Notes |
|-------|-------------|-------|
| Airdrop | $5-50 | Depends on volume |
| Community | $0-20 | API rate limits |
| Analytics | $0 | Self-hosted |
| Influencer | Variable | Campaign budget |
| NFT | $50-200 | Collection deployment |
| Quest | $0 | Self-hosted |
| Content | $0-100 | Optional AI API |

### Recommended Budget

**Minimum Launch**: $500-1,000
- Basic airdrop: $100
- Community setup: $0
- Content creation: $0 (AI-generated)
- Analytics: $0

**Professional Launch**: $5,000-10,000
- Targeted airdrop: $1,000
- Influencer campaigns: $3,000
- NFT collection: $500
- Premium RPC: $100/month

---

## 🆘 Troubleshooting

### Common Issues

**Issue: "Missing SOLANA_WALLET_PRIVATE_KEY"**
```bash
# Solution: Add to ~/.openclaw-env
echo 'SOLANA_WALLET_PRIVATE_KEY=your_key' >> ~/.openclaw-env
```

**Issue: "Rate limit exceeded"**
```bash
# Solution: Use custom RPC
# Get free RPC at https://helius.dev
SOLANA_RPC_URL=https://rpc.helius.io/?api-key=your_key
```

**Issue: "Insufficient balance"**
```bash
# Solution: Check wallet balance
node scripts/status-check.sh

# Or manually
solana balance
```

**Issue: "Agent not starting"**
```bash
# Solution: Check logs
tail -f logs/agent-*.log

# Check dependencies
npm install
```

### Debug Mode

```bash
# Enable debug logging
DEBUG=* node scripts/agent-airdrop.js

# Verbose output
node scripts/agent-airdrop.js --verbose
```

---

## 🤝 Support

### Documentation
- [SETUP_GUIDE.md](./SETUP_GUIDE.md) - Detailed setup
- [EXAMPLES.md](./EXAMPLES.md) - Use cases
- [Solana Docs](https://docs.solana.com)

### Community
- Discord: https://discord.gg/clawd
- GitHub Issues: https://github.com/openclaw/openclaw/issues

---

## 📝 License

MIT License - See [LICENSE](./LICENSE) for details.

---

## 🙏 Acknowledgments

Built with:
- [Solana Web3.js](https://github.com/solana-labs/solana-web3.js)
- [OpenClaw](https://openclaw.ai)
- [Discord.js](https://discord.js.org)
- [Twitter API](https://developer.twitter.com)

---

**Happy launching! 🚀**