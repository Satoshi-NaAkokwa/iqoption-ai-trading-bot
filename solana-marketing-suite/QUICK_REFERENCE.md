# Quick Reference Card - Solana AI Marketing Suite

## 🚀 Quick Start Commands

```bash
# Setup
make setup                          # Install dependencies and create directories
make check-env                      # Verify environment variables

# Start/Stop
make start                          # Start all agents
make stop                           # Stop all agents
make restart                        # Restart all agents
make status                         # Check agent status

# Individual Agents
make start-airdrop                  # Start Airdrop Agent
make start-community                # Start Community Agent
make start-analytics                # Start Analytics Agent (with dashboard)
make start-influencer               # Start Influencer Agent
make start-nft                      # Start NFT Agent
make start-quest                    # Start Quest Agent
make start-content                  # Start Content Agent

# Logs
make logs                           # View all logs
make logs-airdrop                   # View Airdrop Agent logs
make logs-analytics                 # View Analytics Agent logs

# Docker
make docker-up                      # Start all services with Docker
make docker-down                    # Stop all Docker services
make docker-logs                    # View Docker logs

# PM2 (Production)
make pm2-start                      # Start all agents with PM2
make pm2-stop                       # Stop all PM2 processes
make pm2-status                     # Show PM2 status
make pm2-logs                       # View PM2 logs
make pm2-monit                      # Open PM2 monitor

# Utilities
make clean                          # Clean logs and cache
make backup                         # Backup data and config
make health                         # Run health check
make monitor                        # Open monitoring dashboard

# Database
make db-setup                       # Setup PostgreSQL and Redis
make db-reset                       # Reset database
```

---

## 📊 API Endpoints (Analytics Dashboard)

Base URL: `http://localhost:3000`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/metrics` | GET | Get metrics |
| `/api/report/:period` | GET | Get report (daily/weekly/monthly) |
| `/api/track` | POST | Track event |
| `/dashboard` | GET | Web dashboard |

---

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `config/airdrop-config.json` | Airdrop targeting and rewards |
| `config/community-config.json` | Social media automation |
| `config/analytics-config.json` | Metrics and reporting |
| `config/influencer-config.json` | Campaign management |
| `config/nft-config.json` | NFT collection settings |
| `config/quest-config.json` | Quest and rewards |
| `config/content-config.json` | Content generation |

---

## 🎯 Agent Features

### 🪂 Airdrop Agent
- **Target**: Whales (10k+ SOL), Active (100+ SOL), Casual (10+ SOL)
- **Rewards**: Tiered (500/50/5 tokens)
- **Batch Size**: 100 transactions
- **Anti-Bot**: Captcha, wallet age, IP limits

### 💬 Community Agent
- **Discord**: Welcome, moderation, daily digest
- **Twitter**: Auto-posting, threads, engagement
- **Telegram**: Announcements, price alerts
- **Cross-Post**: Multi-platform distribution

### 📊 Analytics Agent
- **Dashboard**: Real-time metrics
- **Reports**: Daily, weekly, monthly
- **Attribution**: Multi-channel ROI
- **Alerts**: Anomaly detection

### 📢 Influencer Agent
- **Discovery**: Category-based search
- **Vetting**: Audience quality, engagement
- **Campaigns**: Deal tracking, ROI
- **Database**: Pre-loaded profiles

### 🎨 NFT Agent
- **Tiers**: Bronze, Silver, Gold
- **Gating**: Discord channels, features
- **Utility**: Staking, governance
- **Marketplaces**: Magic Eden, Tensor

### 🎯 Quest Agent
- **Welcome Quest**: 100 tokens
- **Trading Quest**: 1,200 tokens
- **Community Quest**: 700 tokens
- **Leaderboards**: Daily, weekly, monthly

### ✍️ Content Agent
- **Blog Posts**: 1,500 words, SEO
- **Twitter Threads**: 8-tweet threads
- **YouTube Scripts**: 10-minute tutorials
- **Newsletters**: Weekly roundups

---

## 🌐 Environment Variables

### Required
```bash
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_WALLET_PRIVATE_KEY=your_base58_key
```

### Optional
```bash
DISCORD_BOT_TOKEN=your_token
TWITTER_API_KEY=your_key
TELEGRAM_BOT_TOKEN=your_token
OPENAI_API_KEY=your_key
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://...
```

---

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f analytics-agent

# Restart service
docker-compose restart analytics-agent

# Stop all
docker-compose down

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

---

## 📦 PM2 Commands

```bash
# Start all
pm2 start ecosystem.config.js

# View status
pm2 status

# Logs
pm2 logs
pm2 logs airdrop-agent

# Monitor
pm2 monit

# Restart
pm2 restart all
pm2 restart airdrop-agent

# Stop
pm2 stop all
pm2 stop airdrop-agent

# Save config
pm2 save

# Startup script
pm2 startup
```

---

## 🏥 Health Check

```bash
# Quick check
./scripts/health-check.sh check

# Continuous monitoring
./scripts/health-check.sh monitor

# Generate report
./scripts/health-check.sh report
```

---

## 🔍 Troubleshooting

### Agent won't start
```bash
# Check logs
tail -f logs/agent-*.log

# Check dependencies
npm install

# Verify environment
make check-env
```

### RPC connection failed
```bash
# Test RPC
curl -X POST $SOLANA_RPC_URL \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"getHealth"}'

# Try alternative RPC
SOLANA_RPC_URL=https://rpc.helius.io/?api-key=your_key
```

### Insufficient balance
```bash
# Check balance
npm run wallet:balance

# Devnet airdrop
solana airdrop 1
```

---

## 📈 Metrics to Track

### Daily
- New users
- Active users
- Transaction volume
- Community growth

### Weekly
- Retention rate
- Conversion rate
- ROI by channel
- Quest completion rate

### Monthly
- Total holders
- Market cap
- Community size
- Campaign performance

---

## 💰 Cost Estimates

### Minimum Launch ($500-1,000)
- Airdrop: $100
- Tools: $0
- Content: $0 (AI)
- Analytics: $0

### Professional Launch ($5,000-10,000)
- Airdrop: $1,000
- Influencers: $3,000
- NFT collection: $500
- Premium RPC: $100/mo

---

## 📞 Support

- **Docs**: README.md, SETUP_GUIDE.md, EXAMPLES.md
- **Discord**: https://discord.gg/clawd
- **GitHub**: https://github.com/openclaw/openclaw/issues
- **Email**: support@openclaw.ai

---

## 🔗 Quick Links

| Resource | URL |
|----------|-----|
| Dashboard | http://localhost:3000/dashboard |
| Health API | http://localhost:3000/health |
| Metrics API | http://localhost:3000/api/metrics |
| Logs | `logs/*.log` |
| Config | `config/*.json` |
| Data | `data/*.json` |

---

**Version:** 1.0.0 | **Updated:** May 24, 2026