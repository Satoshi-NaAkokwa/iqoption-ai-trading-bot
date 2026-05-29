/**
 * API Server - RESTful API for Solana Marketing Suite
 * Provides HTTP endpoints for all agent operations
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const compression = require('compression');
const morgan = require('morgan');
const fs = require('fs');
const path = require('path');

// Import agents
const AirdropAgent = require('../scripts/agent-airdrop');
const CommunityAgent = require('../scripts/agent-community');
const AnalyticsAgent = require('../scripts/agent-analytics');
const InfluencerAgent = require('../scripts/agent-influencer');
const NFTAgent = require('../scripts/agent-nft');
const QuestAgent = require('../scripts/agent-quest');
const ContentAgent = require('../scripts/agent-content');

// Load environment
require('dotenv').config({ path: path.join(require('os').homedir(), '.openclaw-env') });

class APIServer {
    constructor(port = 3000) {
        this.port = port;
        this.app = express();
        this.agents = {};
        this.setupMiddleware();
        this.setupRoutes();
        this.setupErrorHandling();
    }

    setupMiddleware() {
        // Security
        this.app.use(helmet());
        this.app.use(cors());
        
        // Compression
        this.app.use(compression());
        
        // Body parsing
        this.app.use(express.json({ limit: '10mb' }));
        this.app.use(express.urlencoded({ extended: true }));
        
        // Logging
        this.app.use(morgan('combined', {
            stream: fs.createWriteStream(path.join(__dirname, '../logs/api.log'), { flags: 'a' })
        }));
        
        // Rate limiting
        const limiter = rateLimit({
            windowMs: 15 * 60 * 1000, // 15 minutes
            max: 100, // limit each IP to 100 requests per windowMs
            message: { error: 'Too many requests, please try again later.' }
        });
        this.app.use('/api/', limiter);
    }

    setupRoutes() {
        // Health check
        this.app.get('/health', (req, res) => {
            res.json({
                status: 'healthy',
                timestamp: new Date().toISOString(),
                uptime: process.uptime()
            });
        });

        // API status
        this.app.get('/api/status', (req, res) => {
            res.json({
                version: '1.0.0',
                agents: {
                    airdrop: !!this.agents.airdrop,
                    community: !!this.agents.community,
                    analytics: !!this.agents.analytics,
                    influencer: !!this.agents.influencer,
                    nft: !!this.agents.nft,
                    quest: !!this.agents.quest,
                    content: !!this.agents.content
                },
                environment: process.env.NODE_ENV || 'development'
            });
        });

        // ==================== AIRDROP ROUTES ====================
        
        this.app.post('/api/airdrop/create', async (req, res) => {
            try {
                const campaign = req.body;
                // Create campaign logic
                const result = { id: `airdrop_${Date.now()}`, ...campaign };
                res.json({ success: true, data: result });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.post('/api/airdrop/:id/execute', async (req, res) => {
            try {
                const { id } = req.params;
                const options = req.body;
                // Execute airdrop logic
                res.json({ success: true, campaignId: id, status: 'executing' });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.get('/api/airdrop/:id/status', async (req, res) => {
            try {
                const { id } = req.params;
                // Get status logic
                res.json({
                    campaignId: id,
                    status: 'active',
                    progress: 45,
                    distributed: 4500,
                    recipients: 90
                });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // ==================== QUEST ROUTES ====================
        
        this.app.post('/api/quest/create', async (req, res) => {
            try {
                const quest = req.body;
                const result = { id: `quest_${Date.now()}`, ...quest };
                res.json({ success: true, data: result });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.get('/api/quest/:id', async (req, res) => {
            try {
                const { id } = req.params;
                res.json({
                    id,
                    name: 'Welcome Quest',
                    totalReward: 100,
                    participants: 250,
                    completions: 150
                });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.post('/api/quest/:id/join', async (req, res) => {
            try {
                const { id } = req.params;
                const { wallet } = req.body;
                res.json({ success: true, questId: id, wallet, status: 'joined' });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.post('/api/quest/:id/complete-task', async (req, res) => {
            try {
                const { id } = req.params;
                const { wallet, taskId, proof } = req.body;
                res.json({ 
                    success: true, 
                    questId: id, 
                    taskId, 
                    completed: true,
                    earnedReward: 20
                });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.get('/api/quest/leaderboard', async (req, res) => {
            try {
                const { category, limit } = req.query;
                res.json([
                    { rank: 1, wallet: 'ABC123...', points: 1500 },
                    { rank: 2, wallet: 'DEF456...', points: 1200 },
                    { rank: 3, wallet: 'GHI789...', points: 1000 }
                ]);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // ==================== NFT ROUTES ====================
        
        this.app.post('/api/nft/deploy', async (req, res) => {
            try {
                const collection = req.body;
                const result = { 
                    id: `collection_${Date.now()}`, 
                    ...collection,
                    status: 'deployed' 
                };
                res.json({ success: true, data: result });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.get('/api/nft/collection/:id', async (req, res) => {
            try {
                const { id } = req.params;
                res.json({
                    id,
                    name: 'Project NFT',
                    totalSupply: 1000,
                    minted: 350,
                    holders: 280
                });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.post('/api/nft/mint', async (req, res) => {
            try {
                const { collectionId, tier, recipient } = req.body;
                res.json({
                    success: true,
                    nftId: `nft_${Date.now()}`,
                    collectionId,
                    tier,
                    recipient
                });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.get('/api/nft/ownership/:wallet', async (req, res) => {
            try {
                const { wallet } = req.params;
                const { collection } = req.query;
                res.json({
                    wallet,
                    nfts: [
                        { tier: 'gold', tokenId: 'nft_123' },
                        { tier: 'silver', tokenId: 'nft_456' }
                    ]
                });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // ==================== INFLUENCER ROUTES ====================
        
        this.app.post('/api/influencer/discover', async (req, res) => {
            try {
                const criteria = req.body;
                res.json([
                    { id: 'inf_001', handle: '@solana_defi', followers: 125000, engagement: 4.8 },
                    { id: 'inf_002', handle: '@crypto_whale', followers: 89000, engagement: 5.2 }
                ]);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.get('/api/influencer/:id', async (req, res) => {
            try {
                const { id } = req.params;
                res.json({
                    id,
                    handle: '@solana_defi',
                    platform: 'twitter',
                    followers: 125000,
                    engagement: 4.8,
                    rating: 4.7
                });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.post('/api/influencer/campaign/create', async (req, res) => {
            try {
                const campaign = req.body;
                const result = { id: `campaign_${Date.now()}`, ...campaign };
                res.json({ success: true, data: result });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.get('/api/influencer/campaign/:id/performance', async (req, res) => {
            try {
                const { id } = req.params;
                res.json({
                    campaignId: id,
                    impressions: 125000,
                    engagement: 6250,
                    clicks: 1875,
                    conversions: 94,
                    roi: 2.8
                });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // ==================== ANALYTICS ROUTES ====================
        
        this.app.post('/api/track', async (req, res) => {
            try {
                const { eventType, data } = req.body;
                // Track event logic
                res.json({ success: true, tracked: true });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.get('/api/metrics', async (req, res) => {
            try {
                const { period } = req.query;
                res.json({
                    period: period || '7d',
                    totalUsers: 1250,
                    activeUsers: 450,
                    newUsers: 87,
                    totalVolume: 125000,
                    transactions: 3420
                });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.get('/api/report', async (req, res) => {
            try {
                const { type } = req.query;
                res.json({
                    type: type || 'daily',
                    date: new Date().toISOString(),
                    metrics: {
                        users: { total: 1250, new: 87, active: 450 },
                        transactions: { total: 3420, volume: 125000 },
                        engagement: { rate: 4.5, growth: '+12%' }
                    }
                });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.get('/api/attribution', async (req, res) => {
            try {
                res.json([
                    { channel: 'twitter', users: 500, conversions: 50, roi: 3.2 },
                    { channel: 'discord', users: 300, conversions: 30, roi: 2.5 },
                    { channel: 'influencers', users: 200, conversions: 40, roi: 4.1 }
                ]);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // ==================== CONTENT ROUTES ====================
        
        this.app.post('/api/content/generate', async (req, res) => {
            try {
                const { type, topic, options } = req.body;
                res.json({
                    success: true,
                    content: {
                        id: `content_${Date.now()}`,
                        type,
                        topic,
                        generated: true
                    }
                });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.get('/api/content/calendar', async (req, res) => {
            try {
                res.json({
                    monday: { type: 'blog', topic: 'Technical Deep Dive' },
                    tuesday: { type: 'twitter', topic: 'Market Analysis' },
                    wednesday: { type: 'video', topic: 'Tutorial' },
                    thursday: { type: 'blog', topic: 'Community Spotlight' },
                    friday: { type: 'twitter', topic: 'AMA Summary' }
                });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.post('/api/content/schedule', async (req, res) => {
            try {
                const { contentId, publishAt, platforms } = req.body;
                res.json({ success: true, scheduled: true, publishAt });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // ==================== COMMUNITY ROUTES ====================
        
        this.app.post('/api/community/post', async (req, res) => {
            try {
                const { message, platforms } = req.body;
                res.json({ 
                    success: true, 
                    posted: true,
                    platforms: platforms || ['discord', 'twitter', 'telegram']
                });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.get('/api/community/stats', async (req, res) => {
            try {
                res.json({
                    discord: { members: 2500, online: 450 },
                    twitter: { followers: 5600, engagement: 4.2 },
                    telegram: { members: 1800, active: 320 }
                });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.get('/api/community/engagement', async (req, res) => {
            try {
                const { platform, period } = req.query;
                res.json({
                    platform: platform || 'all',
                    period: period || '7d',
                    metrics: {
                        posts: 125,
                        reactions: 450,
                        comments: 89,
                        shares: 34
                    }
                });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // Dashboard
        this.app.get('/dashboard', (req, res) => {
            res.send(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Solana Marketing Suite - Dashboard</title>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <style>
                        * { margin: 0; padding: 0; box-sizing: border-box; }
                        body { 
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                            color: #fff;
                            min-height: 100vh;
                            padding: 20px;
                        }
                        .container { max-width: 1200px; margin: 0 auto; }
                        h1 { 
                            font-size: 2.5em; 
                            margin-bottom: 10px;
                            background: linear-gradient(135deg, #00ff88 0%, #00d4ff 100%);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                        }
                        .subtitle { color: #888; margin-bottom: 30px; }
                        .grid { 
                            display: grid; 
                            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
                            gap: 20px; 
                            margin-bottom: 30px;
                        }
                        .card {
                            background: rgba(255, 255, 255, 0.05);
                            backdrop-filter: blur(10px);
                            border: 1px solid rgba(255, 255, 255, 0.1);
                            border-radius: 15px;
                            padding: 25px;
                            transition: transform 0.3s, box-shadow 0.3s;
                        }
                        .card:hover {
                            transform: translateY(-5px);
                            box-shadow: 0 10px 30px rgba(0, 255, 136, 0.2);
                        }
                        .card h2 { 
                            font-size: 1.2em; 
                            margin-bottom: 15px;
                            color: #00ff88;
                        }
                        .metric { 
                            font-size: 2.5em; 
                            font-weight: bold;
                            background: linear-gradient(135deg, #00ff88 0%, #00d4ff 100%);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                        }
                        .label { color: #888; font-size: 0.9em; margin-top: 5px; }
                        .agents { margin-top: 20px; }
                        .agent-status {
                            display: flex;
                            align-items: center;
                            justify-content: space-between;
                            padding: 15px;
                            background: rgba(255, 255, 255, 0.05);
                            border-radius: 10px;
                            margin-bottom: 10px;
                        }
                        .status-dot {
                            width: 10px;
                            height: 10px;
                            border-radius: 50%;
                            background: #00ff88;
                            animation: pulse 2s infinite;
                        }
                        @keyframes pulse {
                            0%, 100% { opacity: 1; }
                            50% { opacity: 0.5; }
                        }
                        .footer {
                            text-align: center;
                            margin-top: 40px;
                            color: #888;
                        }
                        .refresh {
                            background: linear-gradient(135deg, #00ff88 0%, #00d4ff 100%);
                            color: #1a1a2e;
                            border: none;
                            padding: 10px 20px;
                            border-radius: 8px;
                            cursor: pointer;
                            font-weight: bold;
                            margin-top: 20px;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>📊 Solana Marketing Suite</h1>
                        <p class="subtitle">Real-time analytics dashboard</p>
                        
                        <div class="grid">
                            <div class="card">
                                <h2>👥 Total Users</h2>
                                <div class="metric" id="totalUsers">1,250</div>
                                <p class="label">+87 this week</p>
                            </div>
                            <div class="card">
                                <h2>💼 Wallet Connections</h2>
                                <div class="metric" id="wallets">450</div>
                                <p class="label">Active users</p>
                            </div>
                            <div class="card">
                                <h2>💸 Total Volume</h2>
                                <div class="metric" id="volume">$125K</div>
                                <p class="label">Last 7 days</p>
                            </div>
                            <div class="card">
                                <h2>🎯 Quest Completions</h2>
                                <div class="metric" id="quests">150</div>
                                <p class="label">This week</p>
                            </div>
                        </div>

                        <div class="card">
                            <h2>🤖 Agent Status</h2>
                            <div class="agents">
                                <div class="agent-status">
                                    <span>🪂 Airdrop Agent</span>
                                    <div class="status-dot"></div>
                                </div>
                                <div class="agent-status">
                                    <span>💬 Community Agent</span>
                                    <div class="status-dot"></div>
                                </div>
                                <div class="agent-status">
                                    <span>📊 Analytics Agent</span>
                                    <div class="status-dot"></div>
                                </div>
                                <div class="agent-status">
                                    <span>📢 Influencer Agent</span>
                                    <div class="status-dot"></div>
                                </div>
                                <div class="agent-status">
                                    <span>🎨 NFT Agent</span>
                                    <div class="status-dot"></div>
                                </div>
                                <div class="agent-status">
                                    <span>🎯 Quest Agent</span>
                                    <div class="status-dot"></div>
                                </div>
                                <div class="agent-status">
                                    <span>✍️ Content Agent</span>
                                    <div class="status-dot"></div>
                                </div>
                            </div>
                            <button class="refresh" onclick="location.reload()">🔄 Refresh Data</button>
                        </div>

                        <div class="footer">
                            <p>Solana Marketing Suite v1.0.0 | Powered by OpenClaw</p>
                        </div>
                    </div>
                    <script>
                        // Auto-refresh every 30 seconds
                        setTimeout(() => location.reload(), 30000);
                    </script>
                </body>
                </html>
            `);
        });
    }

    setupErrorHandling() {
        // 404 handler
        this.app.use((req, res) => {
            res.status(404).json({ error: 'Not found' });
        });

        // Error handler
        this.app.use((err, req, res, next) => {
            console.error(err.stack);
            res.status(500).json({ error: 'Internal server error' });
        });
    }

    async start() {
        return new Promise((resolve) => {
            this.server = this.app.listen(this.port, () => {
                console.log(`\n🚀 API Server running on port ${this.port}`);
                console.log(`📊 Dashboard: http://localhost:${this.port}/dashboard`);
                console.log(`🔌 API: http://localhost:${this.port}/api`);
                console.log(`💚 Health: http://localhost:${this.port}/health\n`);
                resolve();
            });
        });
    }

    stop() {
        if (this.server) {
            this.server.close();
        }
    }
}

// CLI
if (require.main === module) {
    const args = process.argv.slice(2);
    const port = args.find(a => a.startsWith('--port'))?.split('=')[1] || 3000;
    
    const server = new APIServer(port);
    server.start();

    process.on('SIGINT', () => {
        console.log('\nShutting down...');
        server.stop();
        process.exit(0);
    });
}

module.exports = APIServer;