/**
 * SDK for Solana Marketing Suite
 * High-level wrapper for common operations
 */

const { Connection, Keypair, PublicKey, Transaction, SystemProgram, LAMPORTS_PER_SOL } = require('@solana/web3.js');
const bs58 = require('bs58');
const fs = require('fs');
const path = require('path');

class SolanaMarketingSDK {
    constructor(options = {}) {
        this.connection = new Connection(options.rpcUrl || process.env.SOLANA_RPC_URL, 'confirmed');
        this.wallet = this.loadWallet(options.privateKey || process.env.SOLANA_WALLET_PRIVATE_KEY);
        this.config = this.loadConfig(options.configPath);
        this.dataDir = options.dataDir || path.join(__dirname, '../data');
    }

    loadWallet(privateKey) {
        if (!privateKey) {
            throw new Error('Private key required');
        }
        
        const secretKey = bs58.decode(privateKey);
        return Keypair.fromSecretKey(secretKey);
    }

    loadConfig(configPath) {
        if (configPath && fs.existsSync(configPath)) {
            return JSON.parse(fs.readFileSync(configPath, 'utf8'));
        }
        return {};
    }

    // ==================== WALLET UTILITIES ====================

    async getBalance() {
        const balance = await this.connection.getBalance(this.wallet.publicKey);
        return balance / LAMPORTS_PER_SOL;
    }

    async getWalletAddress() {
        return this.wallet.publicKey.toString();
    }

    async airdropSol(amount = 1) {
        const signature = await this.connection.requestAirdrop(
            this.wallet.publicKey,
            amount * LAMPORTS_PER_SOL
        );
        await this.connection.confirmTransaction(signature);
        return signature;
    }

    // ==================== TOKEN UTILITIES ====================

    async getTokenBalance(tokenMint) {
        const tokenAccounts = await this.connection.getParsedTokenAccountsByOwner(
            this.wallet.publicKey,
            { mint: new PublicKey(tokenMint) }
        );

        if (tokenAccounts.value.length === 0) {
            return 0;
        }

        return tokenAccounts.value[0].account.data.parsed.info.tokenAmount.uiAmount;
    }

    async transferToken(tokenMint, to, amount) {
        // Implementation would use SPL Token library
        console.log(`Transfer ${amount} tokens to ${to}`);
        return { signature: 'mock_signature' };
    }

    // ==================== AIRDROP UTILITIES ====================

    async analyzeWallet(walletAddress) {
        try {
            const pubkey = new PublicKey(walletAddress);
            const balance = await this.connection.getBalance(pubkey);
            const accountInfo = await this.connection.getAccountInfo(pubkey);
            
            return {
                address: walletAddress,
                balance: balance / LAMPORTS_PER_SOL,
                exists: accountInfo !== null,
                isExecutable: accountInfo?.executable || false,
                owner: accountInfo?.owner?.toString()
            };
        } catch (error) {
            return {
                address: walletAddress,
                error: error.message
            };
        }
    }

    async batchAnalyzeWallets(wallets) {
        const results = [];
        
        for (const wallet of wallets) {
            const analysis = await this.analyzeWallet(wallet);
            results.push(analysis);
        }

        return results;
    }

    categorizeWallets(wallets, criteria = {}) {
        const {
            whaleThreshold = 10000,
            activeThreshold = 100,
            casualThreshold = 10
        } = criteria;

        return {
            whales: wallets.filter(w => w.balance >= whaleThreshold),
            active: wallets.filter(w => w.balance >= activeThreshold && w.balance < whaleThreshold),
            casual: wallets.filter(w => w.balance >= casualThreshold && w.balance < activeThreshold),
            inactive: wallets.filter(w => w.balance < casualThreshold)
        };
    }

    // ==================== NFT UTILITIES ====================

    async getNFTsByOwner(walletAddress) {
        try {
            const pubkey = new PublicKey(walletAddress);
            const nfts = await this.connection.getParsedProgramAccounts(
                new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'),
                {
                    filters: [
                        { dataSize: 165 },
                        { memcmp: { offset: 32, bytes: pubkey.toBase58() } }
                    ]
                }
            );

            return nfts.map(nft => ({
                mint: nft.account.data.parsed.info.mint,
                owner: nft.account.data.parsed.info.owner
            }));
        } catch (error) {
            console.error('Error fetching NFTs:', error.message);
            return [];
        }
    }

    async verifyNFTOwnership(walletAddress, collectionMint) {
        const nfts = await this.getNFTsByOwner(walletAddress);
        return nfts.some(nft => nft.mint === collectionMint);
    }

    // ==================== TRANSACTION UTILITIES ====================

    async getTransactionHistory(walletAddress, limit = 100) {
        try {
            const pubkey = new PublicKey(walletAddress);
            const signatures = await this.connection.getSignaturesForAddress(pubkey, { limit });
            
            return signatures.map(sig => ({
                signature: sig.signature,
                slot: sig.slot,
                blockTime: sig.blockTime,
                confirmationStatus: sig.confirmationStatus
            }));
        } catch (error) {
            console.error('Error fetching transaction history:', error.message);
            return [];
        }
    }

    async getRecentTransactions(limit = 10) {
        return this.getTransactionHistory(this.wallet.publicKey.toString(), limit);
    }

    // ==================== DATA STORAGE ====================

    saveData(filename, data) {
        const filePath = path.join(this.dataDir, filename);
        fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
        return filePath;
    }

    loadData(filename) {
        const filePath = path.join(this.dataDir, filename);
        if (fs.existsSync(filePath)) {
            return JSON.parse(fs.readFileSync(filePath, 'utf8'));
        }
        return null;
    }

    // ==================== ENCRYPTION UTILITIES ====================

    hashData(data) {
        const crypto = require('crypto');
        return crypto.createHash('sha256').update(JSON.stringify(data)).digest('hex');
    }

    generateId() {
        const crypto = require('crypto');
        return crypto.randomBytes(16).toString('hex');
    }

    // ==================== VALIDATION ====================

    isValidWalletAddress(address) {
        try {
            new PublicKey(address);
            return true;
        } catch {
            return false;
        }
    }

    isValidSignature(signature) {
        try {
            bs58.decode(signature);
            return signature.length >= 87 && signature.length <= 88;
        } catch {
            return false;
        }
    }

    // ==================== RATE LIMITING ====================

    createRateLimiter(maxRequests, windowMs) {
        const requests = new Map();

        return {
            check: (key) => {
                const now = Date.now();
                const windowStart = now - windowMs;

                if (!requests.has(key)) {
                    requests.set(key, []);
                }

                const userRequests = requests.get(key);
                const recentRequests = userRequests.filter(time => time > windowStart);

                if (recentRequests.length >= maxRequests) {
                    return { allowed: false, remaining: 0 };
                }

                recentRequests.push(now);
                requests.set(key, recentRequests);

                return { allowed: true, remaining: maxRequests - recentRequests.length };
            }
        };
    }

    // ==================== BATCH PROCESSING ====================

    async processBatch(items, processor, batchSize = 10, delay = 1000) {
        const results = [];

        for (let i = 0; i < items.length; i += batchSize) {
            const batch = items.slice(i, i + batchSize);
            const batchResults = await Promise.all(batch.map(processor));
            results.push(...batchResults);

            if (i + batchSize < items.length) {
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }

        return results;
    }

    // ==================== MONITORING ====================

    async getNetworkStatus() {
        const slot = await this.connection.getSlot();
        const health = await this.connection.getHealth();
        const version = await this.connection.getVersion();

        return {
            slot,
            health,
            version: version['solana-core'],
            timestamp: new Date().toISOString()
        };
    }

    async waitForConfirmation(signature, timeout = 30000) {
        const start = Date.now();

        while (Date.now() - start < timeout) {
            const status = await this.connection.getSignatureStatus(signature);

            if (status?.value?.confirmationStatus === 'confirmed' || 
                status?.value?.confirmationStatus === 'finalized') {
                return status.value;
            }

            if (status?.value?.err) {
                throw new Error(`Transaction failed: ${JSON.stringify(status.value.err)}`);
            }

            await new Promise(resolve => setTimeout(resolve, 1000));
        }

        throw new Error('Transaction confirmation timeout');
    }
}

module.exports = SolanaMarketingSDK;

// Usage example
/*
const sdk = new SolanaMarketingSDK({
    rpcUrl: 'https://api.mainnet-beta.solana.com',
    privateKey: process.env.SOLANA_WALLET_PRIVATE_KEY
});

// Get wallet balance
const balance = await sdk.getBalance();
console.log(`Balance: ${balance} SOL`);

// Analyze wallet
const analysis = await sdk.analyzeWallet('ABC123...');
console.log(analysis);

// Categorize wallets
const wallets = [
    { address: 'abc...', balance: 15000 },
    { address: 'def...', balance: 500 },
    { address: 'ghi...', balance: 50 }
];
const categorized = sdk.categorizeWallets(wallets);
console.log(categorized);

// Rate limiting
const limiter = sdk.createRateLimiter(100, 60000);
const check = limiter.check('user_123');
console.log(check); // { allowed: true, remaining: 99 }

// Batch processing
const items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
const results = await sdk.processBatch(
    items,
    async (item) => item * 2,
    3,
    1000
);
console.log(results); // [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
*/