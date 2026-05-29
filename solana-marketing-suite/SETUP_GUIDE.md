# Solana AI Marketing Suite - Complete Setup Guide

## Prerequisites Checklist

### ✅ Required Environment Variables
```bash
# Add these to ~/.openclaw-env
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_WALLET_PRIVATE_KEY=your_private_key_here
DISCORD_BOT_TOKEN=your_discord_bot_token
TWITTER_API_KEY=your_twitter_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
COINMARKETCAP_API_KEY=your_coinmarketcap_key
COINGECKO_API_KEY=your_coingecko_key
```

### ✅ Required NPM Packages
```bash
npm install @solana/web3.js bs58 tweetnacl axios dotenv
```

## Agent Setup Instructions

### 1. Airdrop Agent Setup

**Configuration:**
```javascript
// scripts/agent-airdrop.js
const config = {
    targetWallets: {
        whales: { balance: 10000, reward: 500 },
        active: { balance: 100, reward: 50 },
        casual: { balance: 10, reward: 5 }
    },
    airdropAmount: 1000, // Total tokens to distribute
    batchSize: 100, // Transactions per batch
    delayBetweenBatches: 5000 // ms
};
```

**Smart Wallet Targeting Criteria:**
- **Whale Tier**: >10k SOL balance, high transaction volume
- **Active Tier**: 100-10k SOL, regular transactions
- **Casual Tier**: 10-100 SOL, occasional activity

**Usage:**
```bash
# Run airdrop targeting analysis
node scripts/agent-airdrop.js analyze

# Execute airdrop
node scripts/agent-airdrop.js execute --amount 5000

# Track claim rates
node scripts/agent-airdrop.js track
```

### 2. Community Agent Setup

**Platform Setup:**

**Discord:**
```bash
# Create Discord bot: https://discord.com/developers/applications
# Get bot token and add to ~/.openclaw-env
# Invite bot with permissions: Read Messages, Send Messages, Embed Links

# Add to ~/.openclaw-env:
DISCORD_BOT_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.GhIjKx.abCdEfGhIjKlMnOpQrStUvWxYz
```

**Twitter/X:**
```bash
# Create app: https://developer.twitter.com/
# Add to ~/.openclaw-env:
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
```

**Telegram:**
```bash
# Create bot: https://t.me/BotFather
# Add to ~/.openclaw-env:
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

**Content Strategy:**
```javascript
// Auto-posting schedule
const postingSchedule = {
    twitter: {
        frequency: 'daily',
        bestTimes: ['09:00', '12:00', '18:00', '21:00'],
        hashtags: ['#Solana', '#DeFi', '#Crypto', '#Airdrop']
    },
    discord: {
        channels: ['#announcements', '#general', '#trading'],
        dailyDigest: true,
        weeklySummary: true
    },
    telegram: {
        channels: ['-1001234567890'],
        postingInterval: 3600000 // 1 hour
    }
};
```

### 3. Analytics Agent Setup

**Integration Setup:**
```bash
# Add tracking codes to your dApp/website
<script src="https://cdn.jsdelivr.net/npm/@solana/web3.js"></script>
<script>
    // Track wallet connections
    window.addEventListener('walletConnected', (event) => {
        fetch('/api/track-wallet', {
            method: 'POST',
            body: JSON.stringify({
                wallet: event.wallet,
                timestamp: Date.now(),
                source: 'webapp'
            })
        });
    });
</script>
```

**Metrics to Track:**
- Daily active wallets
- Token transfer volume
- Social media engagement
- Website traffic sources
- Conversion funnel stages

**Analytics Dashboard:**
```bash
# Start analytics server
node scripts/agent-analytics.js server --port 3000

# View dashboard at http://localhost:3000
```

### 4. Influencer Agent Setup

**Influencer Database:**
```javascript
// Top Solana influencers to target
const influencerDatabase = {
    categories: {
        defi: [
            { handle: '@defi_god', followers: 50000, engagement: 5.2 },
            { handle: '@solana_whale', followers: 120000, engagement: 4.8 }
        ],
        nft: [
            { handle: '@nft_collector', followers: 80000, engagement: 6.1 },
            { handle: '@solana_nfts', followers: 45000, engagement: 5.5 }
        ],
        trading: [
            { handle: '@crypto_trader', followers: 200000, engagement: 4.2 },
            { handle: '@solana_signals', followers: 150000, engagement: 4.9 }
        ]
    }
};
```

**Deal Templates:**
```javascript
const dealTemplates = {
    sponsoredTweet: {
        basePrice: 500, // USDT
        pricePer1kFollowers: 10,
        deliverables: ['1 tweet', '1 retweet', '24h pin']
    },
    discordShill: {
        basePrice: 300,
        pricePer1kMembers: 5,
        deliverables: ['announcement post', 'community Q&A']
    },
    youtubeReview: {
        basePrice: 1000,
        pricePer10kViews: 20,
        deliverables: ['5-10 min review', 'description link']
    }
};
```

### 5. NFT Agent Setup

**NFT Collection Configuration:**
```javascript
// Configure NFT utility
const nftUtility = {
    tiers: {
        bronze: {
            requiredTokens: 1000,
            benefits: ['exclusive discord role', 'early access to features'],
            maxSupply: 1000
        },
        silver: {
            requiredTokens: 5000,
            benefits: ['bronze benefits', 'monthly airdrops', 'voting rights'],
            maxSupply: 500
        },
        gold: {
            requiredTokens: 10000,
            benefits: ['silver benefits', '1-on-1 with team', 'founder access'],
            maxSupply: 100
        }
    }
};
```

**NFT Gating Implementation:**
```javascript
// Check if wallet owns required NFT
async function checkNFTOwnership(walletAddress) {
    const nfts = await connection.getNftsByOwner(new PublicKey(walletAddress));
    return nfts.some(nft => 
        nft.collection?.address.toString() === yourCollectionAddress
    );
}
```

### 6. Quest Agent Setup

**Quest Templates:**
```javascript
const questTemplates = {
    welcome: {
        name: 'Welcome Quest',
        tasks: [
            { type: 'social_follow', platform: 'twitter', reward: 50 },
            { type: 'discord_join', server: 'your_server_id', reward: 30 },
            { type: 'telegram_join', channel: 'your_channel_id', reward: 20 }
        ],
        totalReward: 100,
        timeLimit: 7 * 24 * 60 * 60 * 1000 // 7 days
    },
    trading: {
        name: 'Trading Master',
        tasks: [
            { type: 'swap', amount: 100, reward: 200 },
            { type: 'liquidity_provide', amount: 500, reward: 300 },
            { type: 'hold', duration: 30 * 24 * 60 * 60 * 1000, reward: 150 }
        ],
        totalReward: 650,
        prerequisites: ['welcome']
    }
};
```

**Leaderboard System:**
```javascript
// Track quest completion
const leaderboard = {
    update: async (wallet, questId, points) => {
        await redis.zincrby('quest_leaderboard', points, wallet);
        await redis.hset('quest_progress', wallet, JSON.stringify({
            questId,
            completedAt: Date.now(),
            points
        }));
    },
    getTop: async (limit = 10) => {
        return await redis.zrevrange('quest_leaderboard', 0, limit - 1, 'WITHSCORES');
    }
};
```

### 7. Content Agent Setup

**Content Templates:**
```javascript
const contentTemplates = {
    blogPost: {
        structure: [
            'introduction',
            'problem_statement', 
            'solution',
            'benefits',
            'use_cases',
            'roadmap',
            'conclusion'
        ],
        seoKeywords: ['#Solana', '#DeFi', 'token economics', 'blockchain']
    },
    twitterThread: {
        maxTweets: 10,
        hookTypes: ['question', 'statistic', 'story'],
        ctaVariations: ['check it out', 'learn more', 'join the community']
    },
    youtubeScript: {
        duration: '5-10 minutes',
        sections: ['intro', 'demo', 'benefits', 'tutorial', 'outro']
    }
};
```

**Content Calendar:**
```javascript
const contentCalendar = {
    weeklySchedule: [
        { day: 'Monday', type: 'blog_post', topic: 'technical_deep_dive' },
        { day: 'Wednesday', type: 'twitter_thread', topic: 'market_update' },
        { day: 'Friday', type: 'video', topic: 'tutorial' },
        { day: 'Sunday', type: 'newsletter', topic: 'weekly_roundup' }
    ]
};
```

## Launch Day Checklist

### Pre-Launch (1 week before)
- [ ] Set up all environment variables
- [ ] Create social media accounts
- [ ] Build Discord server structure
- [ ] Test all agent integrations
- [ ] Prepare launch content
- [ ] Set up analytics tracking
- [ ] Create landing page

### Launch Day
- [ ] Run Airdrop Agent with targeted wallets
- [ ] Start Community Agent auto-posting
- [ ] Activate Quest Agent with welcome quest
- [ ] Begin Content Agent content generation
- [ ] Monitor Analytics Agent in real-time
- [ ] Engage with initial community members

### Post-Launch (Week 1)
- [ ] Analyze initial metrics
- [ ] Adjust posting schedules based on engagement
- [ ] Scale successful campaigns
- [ ] Initiate Influencer Agent partnerships
- [ ] Launch NFT Agent for exclusive access
- [ ] Optimize quest difficulty and rewards

## Troubleshooting Guide

### Common Issues

**Issue: Wallet connection fails**
```bash
# Check RPC endpoint status
curl -X POST https://api.mainnet-beta.solana.com -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"getHealth"}'

# Try alternative RPCs
SOLANA_RPC_URL=https://solana-api.projectserum.com
```

**Issue: Discord bot not responding**
```bash
# Check bot token
echo $DISCORD_BOT_TOKEN

# Verify bot permissions
# 1. Go to Discord Developer Portal
# 2. Check bot has: Read Messages, Send Messages, Embed Links
```

**Issue: Twitter API rate limits**
```javascript
// Implement rate limiting
const rateLimiter = {
    tweetsPer15Min: 200,
    lastTweet: 0,
    canTweet: function() {
        const now = Date.now();
        if (now - this.lastTweet < 45000) { // 45s between tweets
            return false;
        }
        this.lastTweet = now;
        return true;
    }
};
```

## Performance Optimization

### Database Optimization
```bash
# Use Redis for caching
npm install redis

# Index important database fields
CREATE INDEX idx_wallet_balance ON wallets(balance);
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp);
```

### Caching Strategy
```javascript
const cache = {
    set: (key, value, ttl = 3600) => {
        redis.setex(key, ttl, JSON.stringify(value));
    },
    get: async (key) => {
        const data = await redis.get(key);
        return data ? JSON.parse(data) : null;
    }
};
```

### Batch Processing
```javascript
// Process large datasets in batches
async function processBatch(items, batchSize = 100, processor) {
    for (let i = 0; i < items.length; i += batchSize) {
        const batch = items.slice(i, i + batchSize);
        await Promise.all(batch.map(processor));
        await new Promise(resolve => setTimeout(resolve, 1000)); // Rate limiting
    }
}
```

## Security Best Practices

### Private Key Management
```bash
# Never commit private keys to git
# Use environment variables
# Encrypt sensitive data at rest
# Rotate API keys regularly
```

### Rate Limiting
```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
});

app.use('/api/', limiter);
```

### Input Validation
```javascript
const Joi = require('joi');

const walletSchema = Joi.string().length(44).pattern(/^[1-9A-HJ-NP-Za-km-z]+$/);

function validateWallet(address) {
    const { error } = walletSchema.validate(address);
    if (error) {
        throw new Error('Invalid wallet address');
    }
}
```

## Monitoring & Alerts

### Health Checks
```bash
# Create health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        timestamp: Date.now()
    });
});
```

### Error Tracking
```javascript
// Implement error logging
const winston = require('winston');

const logger = winston.createLogger({
    level: 'info',
    format: winston.format.json(),
    transports: [
        new winston.transports.File({ filename: 'error.log', level: 'error' }),
        new winston.transports.File({ filename: 'combined.log' })
    ]
});
```

## Next Steps

1. **Start Small**: Begin with Airdrop Agent and Community Agent
2. **Measure Everything**: Use Analytics Agent from day one
3. **Iterate Quickly**: Adjust based on real-time data
4. **Scale Gradually**: Add more agents as community grows
5. **Stay Secure**: Regular security audits and key rotation

For additional support or customization, refer to individual agent documentation in `/scripts/` directory.