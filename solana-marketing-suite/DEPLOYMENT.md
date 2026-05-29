# Deployment Guide - Solana AI Marketing Suite

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Development Deployment](#development-deployment)
4. [Production Deployment](#production-deployment)
5. [Docker Deployment](#docker-deployment)
6. [PM2 Deployment](#pm2-deployment)
7. [Monitoring & Logging](#monitoring--logging)
8. [Security Hardening](#security-hardening)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: 20GB+ free space
- **CPU**: 2+ cores

### Software Requirements
- Node.js 18+ (LTS recommended)
- npm 9+ or yarn
- Docker & Docker Compose (optional)
- PM2 (optional, for production)
- Git

### External Services
- Solana RPC endpoint (mainnet or devnet)
- Solana wallet with SOL for operations
- (Optional) Discord bot token
- (Optional) Twitter API credentials
- (Optional) Telegram bot token

---

## Environment Setup

### 1. Install Node.js

```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# Or using package manager
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS
brew install node@18
```

### 2. Clone and Setup

```bash
# Navigate to project
cd /path/to/solana-marketing-suite

# Install dependencies
npm install

# Create directories
mkdir -p logs data config cache
```

### 3. Configure Environment Variables

```bash
# Copy example env file
cp .env.example ~/.openclaw-env

# Edit with your credentials
nano ~/.openclaw-env
```

Required variables:
```bash
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_WALLET_PRIVATE_KEY=your_base58_private_key_here
```

Optional variables:
```bash
DISCORD_BOT_TOKEN=your_discord_bot_token
TWITTER_API_KEY=your_twitter_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

---

## Development Deployment

### Quick Start

```bash
# Setup
make setup

# Check environment
make check-env

# Start all agents
make start

# Check status
make status

# View logs
make logs
```

### Individual Agent Development

```bash
# Start specific agent
npm run agent:airdrop
npm run agent:community
npm run agent:analytics

# Or directly
node scripts/agent-airdrop.js start
node scripts/agent-community.js start
node scripts/agent-analytics.js server --port 3000
```

### Development Mode with Auto-Restart

```bash
# Install nodemon for development
npm install -g nodemon

# Run with auto-restart
nodemon scripts/agent-airdrop.js
```

---

## Production Deployment

### Option 1: PM2 (Recommended)

PM2 provides process management, auto-restart, clustering, and monitoring.

#### Install PM2

```bash
npm install -g pm2
```

#### Start with PM2

```bash
# Start all agents
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Setup PM2 startup script
pm2 startup
```

#### PM2 Commands

```bash
# View status
pm2 status

# View logs
pm2 logs

# Monitor
pm2 monit

# Restart specific agent
pm2 restart airdrop-agent

# Restart all
pm2 restart all

# Stop all
pm2 stop all

# Delete all
pm2 delete all
```

#### PM2 Monitoring

```bash
# Install PM2 monitoring
pm2 install pm2-logrotate

# Configure log rotation
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
```

### Option 2: Systemd Service

Create systemd service for each agent.

#### Create Service File

```bash
sudo nano /etc/systemd/system/solana-airdrop.service
```

```ini
[Unit]
Description=Solana Marketing Suite - Airdrop Agent
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/solana-marketing-suite
Environment="NODE_ENV=production"
EnvironmentFile=/home/your-username/.openclaw-env
ExecStart=/usr/bin/node /path/to/solana-marketing-suite/scripts/agent-airdrop.js
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=solana-airdrop

[Install]
WantedBy=multi-user.target
```

#### Enable and Start

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable solana-airdrop

# Start service
sudo systemctl start solana-airdrop

# Check status
sudo systemctl status solana-airdrop

# View logs
sudo journalctl -u solana-airdrop -f
```

---

## Docker Deployment

### Quick Start with Docker

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Stop all
docker-compose down
```

### Individual Container

```bash
# Build image
docker build -t solana-marketing-suite .

# Run container
docker run -d \
  --name analytics-agent \
  -p 3000:3000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config \
  -e SOLANA_RPC_URL=$SOLANA_RPC_URL \
  -e SOLANA_WALLET_PRIVATE_KEY=$SOLANA_WALLET_PRIVATE_KEY \
  solana-marketing-suite
```

### Docker Compose Services

The `docker-compose.yml` includes:
- **Redis**: Caching and rate limiting
- **PostgreSQL**: Persistent data storage
- **Airdrop Agent**: Token distribution
- **Community Agent**: Social media automation
- **Analytics Agent**: Metrics and dashboards
- **Influencer Agent**: Campaign management
- **NFT Agent**: NFT operations
- **Quest Agent**: Gamification
- **Content Agent**: Content generation
- **Nginx**: Reverse proxy (optional)

### Production Docker Compose

```bash
# Start with production config
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Monitoring & Logging

### Application Logs

```bash
# View all logs
tail -f logs/*.log

# View specific agent
tail -f logs/agent-airdrop.log

# Search logs
grep "ERROR" logs/*.log

# Real-time monitoring
tail -f logs/*.log | grep --color "ERROR\|WARN\|INFO"
```

### Health Checks

```bash
# Run health check
./scripts/health-check.sh check

# Continuous monitoring
./scripts/health-check.sh monitor

# Generate report
./scripts/health-check.sh report
```

### Analytics Dashboard

```bash
# Start analytics dashboard
node scripts/agent-analytics.js server --port 3000

# Access at
http://localhost:3000/dashboard
```

### Log Aggregation (Optional)

#### Using ELK Stack

```yaml
# docker-compose.logging.yml
services:
  elasticsearch:
    image: elasticsearch:8.9.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  kibana:
    image: kibana:8.9.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

  filebeat:
    image: elastic/filebeat:8.9.0
    volumes:
      - ./logs:/logs
      - ./filebeat.yml:/usr/share/filebeat/filebeat.yml
```

---

## Security Hardening

### 1. Environment Variables

```bash
# Set proper permissions
chmod 600 ~/.openclaw-env

# Never commit env files
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
```

### 2. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 3000/tcp  # Analytics dashboard (optional)

# Enable firewall
sudo ufw enable
```

### 3. Rate Limiting

```javascript
// Built-in rate limiting in agents
const rateLimiter = {
    maxRequests: 100,
    perWindow: 60000, // 1 minute
    backoff: 'exponential'
};
```

### 4. Input Validation

All agents validate inputs:
```javascript
const Joi = require('joi');

const walletSchema = Joi.string().length(44).pattern(/^[1-9A-HJ-NP-Za-km-z]+$/);
```

### 5. Private Key Security

```bash
# Use dedicated wallet for operations
# Never use main wallet

# Encrypt sensitive data
openssl enc -aes-256-cbc -salt -in wallet.json -out wallet.enc

# Rotate keys regularly
# Use hardware wallet for large operations
```

### 6. Audit Logging

All operations are logged:
```bash
# View audit logs
tail -f logs/audit.log
```

---

## Scaling

### Horizontal Scaling

```bash
# Run multiple instances with PM2
pm2 start ecosystem.config.js -i max

# Or specify number of instances
pm2 start ecosystem.config.js -i 4
```

### Load Balancing

Use Nginx or HAProxy:
```nginx
upstream analytics_cluster {
    least_conn;
    server localhost:3000;
    server localhost:3001;
    server localhost:3002;
}
```

### Database Scaling

```bash
# Use connection pooling
# Add Redis for caching
# Consider read replicas for PostgreSQL
```

---

## Backup & Recovery

### Backup Script

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/solana-marketing-suite"

mkdir -p $BACKUP_DIR

# Backup data
tar -czf $BACKUP_DIR/data_$DATE.tar.gz data/

# Backup config
tar -czf $BACKUP_DIR/config_$DATE.tar.gz config/

# Backup database
pg_dump solana_marketing > $BACKUP_DIR/db_$DATE.sql

# Remove old backups (keep last 7 days)
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

### Automated Backups

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/backup.sh >> /var/log/backup.log 2>&1
```

### Recovery

```bash
# Restore data
tar -xzf data_20240101_020000.tar.gz

# Restore database
psql solana_marketing < db_20240101_020000.sql
```

---

## Troubleshooting

### Common Issues

#### 1. "Missing SOLANA_RPC_URL"

```bash
# Solution: Add to environment
echo 'SOLANA_RPC_URL=https://api.mainnet-beta.solana.com' >> ~/.openclaw-env
```

#### 2. "Rate limit exceeded"

```bash
# Solution: Use custom RPC
# Get free RPC at https://helius.dev
SOLANA_RPC_URL=https://rpc.helius.io/?api-key=your_key
```

#### 3. "Insufficient balance"

```bash
# Solution: Check wallet balance
npm run wallet:balance

# Airdrop SOL (devnet only)
solana airdrop 1
```

#### 4. "Agent not starting"

```bash
# Check logs
tail -f logs/agent-*.log

# Check dependencies
npm install

# Check Node version
node --version  # Should be 18+
```

#### 5. "Discord bot not responding"

```bash
# Verify bot token
echo $DISCORD_BOT_TOKEN

# Check bot permissions
# 1. Go to Discord Developer Portal
# 2. Verify bot has: Read Messages, Send Messages, Embed Links

# Re-invite bot with correct permissions
```

### Debug Mode

```bash
# Enable debug logging
DEBUG=* node scripts/agent-airdrop.js

# Verbose output
node scripts/agent-airdrop.js --verbose

# Test mode
node scripts/agent-airdrop.js test
```

### Performance Issues

```bash
# Check system resources
htop

# Check Node memory
node --max-old-space-size=4096 scripts/agent-airdrop.js

# Profile performance
node --prof scripts/agent-airdrop.js
```

---

## Maintenance

### Regular Tasks

```bash
# Daily
- Monitor logs for errors
- Check wallet balances
- Review agent status

# Weekly
- Backup data and config
- Update dependencies
- Review performance metrics

# Monthly
- Rotate API keys
- Audit access logs
- Update documentation
```

### Updates

```bash
# Pull latest code
git pull origin main

# Install dependencies
npm install

# Restart agents
pm2 restart all

# Or with docker
docker-compose down
docker-compose pull
docker-compose up -d
```

---

## Support

### Documentation
- README.md - Main documentation
- SETUP_GUIDE.md - Detailed setup
- EXAMPLES.md - Use cases
- PROJECT_SUMMARY.md - Overview

### Community
- Discord: https://discord.gg/clawd
- GitHub Issues: https://github.com/openclaw/openclaw/issues

### Professional Support
- Email: support@openclaw.ai
- Priority support available for enterprise users

---

**Last Updated:** May 24, 2026
**Version:** 1.0.0