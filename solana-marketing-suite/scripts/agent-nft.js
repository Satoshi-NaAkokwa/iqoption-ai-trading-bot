#!/usr/bin/env node

/**
 * NFT Agent - NFT-gated features and utility
 * 
 * Features:
 * - NFT collection deployment
 * - Token-gated access control
 * - Tiered membership system
 * - Cross-platform NFT integration
 */

const fs = require('fs');
const path = require('path');
const { Connection, Keypair, PublicKey } = require('@solana/web3.js');
const bs58 = require('bs58');

// Load environment variables
require('dotenv').config({ path: path.join(require('os').homedir(), '.openclaw-env') });

class NFTAgent {
    constructor(configPath = '../config/nft-config.json') {
        this.config = this.loadConfig(configPath);
        this.connection = null;
        this.wallet = null;
        this.collection = null;
        this.logs = [];
    }

    loadConfig(configPath) {
        const fullPath = path.join(__dirname, configPath);
        if (fs.existsSync(fullPath)) {
            return JSON.parse(fs.readFileSync(fullPath, 'utf8'));
        }
        return {
            collection: {
                name: 'Project NFT',
                symbol: 'PNFT',
                totalSupply: 1000,
                price: 1.0
            },
            tiers: {
                bronze: { nfts: 500, price: 0.5 },
                silver: { nfts: 350, price: 1.0 },
                gold: { nfts: 150, price: 2.5 }
            }
        };
    }

    log(message, level = 'INFO') {
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] [${level}] ${message}`;
        this.logs.push(logMessage);
        console.log(logMessage);
        
        const logDir = path.join(__dirname, '../logs');
        if (!fs.existsSync(logDir)) {
            fs.mkdirSync(logDir, { recursive: true });
        }
        fs.appendFileSync(path.join(logDir, 'agent-nft.log'), logMessage + '\n');
    }

    async initialize() {
        this.log('🎨 Initializing NFT Agent...');

        if (!process.env.SOLANA_RPC_URL) {
            throw new Error('SOLANA_RPC_URL not set');
        }
        if (!process.env.SOLANA_WALLET_PRIVATE_KEY) {
            throw new Error('SOLANA_WALLET_PRIVATE_KEY not set');
        }

        this.connection = new Connection(process.env.SOLANA_RPC_URL, 'confirmed');
        this.log('✓ Connected to Solana RPC');

        const secretKey = bs58.decode(process.env.SOLANA_WALLET_PRIVATE_KEY);
        this.wallet = Keypair.fromSecretKey(secretKey);
        this.log(`✓ Wallet loaded: ${this.wallet.publicKey.toString().slice(0, 8)}...`);

        return true;
    }

    async deployCollection(config = null) {
        const collectionConfig = config || this.config.collection;
        this.log(`🚀 Deploying NFT collection: ${collectionConfig.name}...`);

        // In production, would use Metaplex SDK
        const collection = {
            id: `col_${Date.now()}`,
            name: collectionConfig.name,
            symbol: collectionConfig.symbol,
            description: collectionConfig.description,
            totalSupply: collectionConfig.totalSupply,
            price: collectionConfig.price,
            royalties: collectionConfig.royalties,
            mintAddress: null, // Would be set after deployment
            status: 'deployed',
            createdAt: new Date().toISOString(),
            tiers: {}
        };

        // Deploy tiers
        for (const [tierName, tierConfig] of Object.entries(this.config.tiers)) {
            collection.tiers[tierName] = {
                ...tierConfig,
                minted: 0,
                available: tierConfig.nfts,
                holders: []
            };
            this.log(`  Deployed tier: ${tierName} (${tierConfig.nfts} NFTs)`);
        }

        this.collection = collection;
        this.log(`✓ Collection deployed with ID: ${collection.id}`);

        return collection;
    }

    async setupGating() {
        if (!this.collection) {
            throw new Error('No collection deployed');
        }

        this.log('🔐 Setting up NFT gating...');

        const gatingRules = {
            discordChannels: this.config.gating.discordChannels || {},
            features: this.config.gating.features || {},
            events: this.config.gating.events || {}
        };

        // Configure Discord channel access
        for (const [tier, channels] of Object.entries(gatingRules.discordChannels)) {
            this.log(`  Configuring Discord access for ${tier}: ${channels.join(', ')}`);
        }

        // Configure feature access
        for (const [tier, features] of Object.entries(gatingRules.features)) {
            this.log(`  Configuring feature access for ${tier}: ${features.join(', ')}`);
        }

        this.log('✓ NFT gating configured');
        return gatingRules;
    }

    async checkOwnership(walletAddress, tier = null) {
        this.log(`🔍 Checking NFT ownership for ${walletAddress.slice(0, 8)}...`);

        // In production, would query the blockchain
        const ownership = {
            wallet: walletAddress,
            nfts: [],
            tier: null,
            benefits: []
        };

        if (ownership.nfts.length > 0) {
            ownership.tier = 'bronze'; // Would be determined by NFT properties
            ownership.benefits = this.config.tiers[ownership.tier].benefits || [];
        }

        return ownership;
    }

    async mintNFT(tier, recipientWallet) {
        if (!this.collection) {
            throw new Error('No collection deployed');
        }

        const tierConfig = this.collection.tiers[tier];
        if (!tierConfig) {
            throw new Error(`Tier ${tier} not found`);
        }

        if (tierConfig.minted >= tierConfig.nfts) {
            throw new Error(`Tier ${tier} sold out`);
        }

        this.log(`🎫 Minting ${tier} NFT for ${recipientWallet.slice(0, 8)}...`);

        // In production, would execute mint transaction
        const nft = {
            id: `nft_${Date.now()}`,
            collection: this.collection.id,
            tier: tier,
            owner: recipientWallet,
            mintAddress: null, // Would be set after minting
            mintedAt: new Date().toISOString(),
            benefits: tierConfig.benefits
        };

        // Update tier stats
        tierConfig.minted++;
        tierConfig.holders.push(recipientWallet);

        this.log(`✓ NFT minted: ${nft.id}`);
        return nft;
    }

    async getCollectionStats() {
        if (!this.collection) {
            throw new Error('No collection deployed');
        }

        const stats = {
            collection: this.collection.id,
            name: this.collection.name,
            totalSupply: this.collection.totalSupply,
            totalMinted: 0,
            totalHolders: 0,
            tiers: {}
        };

        for (const [tierName, tierConfig] of Object.entries(this.collection.tiers)) {
            stats.tiers[tierName] = {
                supply: tierConfig.nfts,
                minted: tierConfig.minted,
                available: tierConfig.available,
                holders: tierConfig.holders.length,
                sellThroughRate: (tierConfig.minted / tierConfig.nfts * 100).toFixed(2)
            };
            stats.totalMinted += tierConfig.minted;
            stats.totalHolders += tierConfig.holders.length;
        }

        return stats;
    }

    async run() {
        await this.initialize();

        this.log('Starting NFT agent...');

        // Monitor collection stats
        setInterval(async () => {
            if (this.collection) {
                const stats = await this.getCollectionStats();
                this.saveStats(stats);
            }
        }, 300000); // Every 5 minutes

        process.on('SIGINT', () => {
            this.log('Shutting down...');
            process.exit(0);
        });
    }

    saveStats(stats) {
        const dataDir = path.join(__dirname, '../data');
        if (!fs.existsSync(dataDir)) {
            fs.mkdirSync(dataDir, { recursive: true });
        }
        fs.writeFileSync(
            path.join(dataDir, 'nft-stats.json'),
            JSON.stringify(stats, null, 2)
        );
    }
}

// CLI Interface
const args = process.argv.slice(2);
const agent = new NFTAgent();

if (args[0] === 'deploy') {
    const config = args.find(a => a.startsWith('--config'))?.split('=')[1];
    agent.initialize().then(() => {
        const cfg = config ? JSON.parse(fs.readFileSync(config, 'utf8')) : null;
        agent.deployCollection(cfg);
    });
} else if (args[0] === 'setup-gates') {
    agent.initialize().then(() => agent.setupGating());
} else if (args[0] === 'mint') {
    const tier = args.find(a => a.startsWith('--tier'))?.split('=')[1];
    const recipient = args.find(a => a.startsWith('--recipient'))?.split('=')[1];
    const allowlist = args.includes('--allowlist');
    agent.initialize().then(() => agent.mintNFT(tier, recipient));
} else if (args[0] === 'stats') {
    agent.initialize().then(async () => {
        const stats = await agent.getCollectionStats();
        console.log(JSON.stringify(stats, null, 2));
    });
} else if (args[0] === 'check') {
    const wallet = args.find(a => !a.startsWith('--'));
    agent.initialize().then(async () => {
        const ownership = await agent.checkOwnership(wallet);
        console.log(JSON.stringify(ownership, null, 2));
    });
} else if (args[0] === 'start' || args.length === 0) {
    agent.run();
} else {
    console.log(`
NFT Agent - NFT-gated features and utility

Usage:
  node agent-nft.js [command] [options]

Commands:
  start         Start the agent (default)
  deploy        Deploy NFT collection
  setup-gates   Setup NFT gating rules
  mint          Mint NFT to recipient
  stats         Get collection statistics
  check         Check NFT ownership for wallet

Options:
  --config=N    Config file path
  --tier=N      Tier name (bronze, silver, gold)
  --recipient=N Recipient wallet address
  --allowlist   Mint from allowlist

Examples:
  node agent-nft.js deploy --config nft-config.json
  node agent-nft.js setup-gates
  node agent-nft.js mint --tier gold --recipient ABC123...
  node agent-nft.js stats
  node agent-nft.js check ABC123...
    `);
}

module.exports = NFTAgent;