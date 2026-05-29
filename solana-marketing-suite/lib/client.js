/**
 * API Client Library for Solana Marketing Suite
 * Easy-to-use client for integrating with the marketing suite API
 */

const axios = require('axios');

class SolanaMarketingClient {
    constructor(options = {}) {
        this.baseURL = options.baseURL || 'http://localhost:3000';
        this.apiKey = options.apiKey;
        this.timeout = options.timeout || 30000;
        
        this.client = axios.create({
            baseURL: this.baseURL,
            timeout: this.timeout,
            headers: {
                'Content-Type': 'application/json',
                ...(this.apiKey && { 'X-API-Key': this.apiKey })
            }
        });
    }

    // ==================== AIRDROP ====================

    /**
     * Create a new airdrop campaign
     */
    async createAirdrop(campaign) {
        const response = await this.client.post('/api/airdrop/create', campaign);
        return response.data;
    }

    /**
     * Execute an airdrop
     */
    async executeAirdrop(airdropId, options = {}) {
        const response = await this.client.post(`/api/airdrop/${airdropId}/execute`, options);
        return response.data;
    }

    /**
     * Get airdrop status
     */
    async getAirdropStatus(airdropId) {
        const response = await this.client.get(`/api/airdrop/${airdropId}/status`);
        return response.data;
    }

    /**
     * Get airdrop recipients
     */
    async getAirdropRecipients(airdropId, filters = {}) {
        const response = await this.client.get(`/api/airdrop/${airdropId}/recipients`, {
            params: filters
        });
        return response.data;
    }

    // ==================== QUESTS ====================

    /**
     * Create a new quest
     */
    async createQuest(quest) {
        const response = await this.client.post('/api/quest/create', quest);
        return response.data;
    }

    /**
     * Get quest details
     */
    async getQuest(questId) {
        const response = await this.client.get(`/api/quest/${questId}`);
        return response.data;
    }

    /**
     * Join a quest
     */
    async joinQuest(questId, walletAddress) {
        const response = await this.client.post(`/api/quest/${questId}/join`, {
            wallet: walletAddress
        });
        return response.data;
    }

    /**
     * Complete a quest task
     */
    async completeTask(questId, walletAddress, taskId, proof = {}) {
        const response = await this.client.post(`/api/quest/${questId}/complete-task`, {
            wallet: walletAddress,
            taskId,
            proof
        });
        return response.data;
    }

    /**
     * Get user quest progress
     */
    async getQuestProgress(questId, walletAddress) {
        const response = await this.client.get(`/api/quest/${questId}/progress/${walletAddress}`);
        return response.data;
    }

    /**
     * Get leaderboard
     */
    async getLeaderboard(category = 'all_time', limit = 10) {
        const response = await this.client.get('/api/quest/leaderboard', {
            params: { category, limit }
        });
        return response.data;
    }

    // ==================== NFT ====================

    /**
     * Deploy NFT collection
     */
    async deployNFTCollection(collection) {
        const response = await this.client.post('/api/nft/deploy', collection);
        return response.data;
    }

    /**
     * Get collection details
     */
    async getCollection(collectionId) {
        const response = await this.client.get(`/api/nft/collection/${collectionId}`);
        return response.data;
    }

    /**
     * Mint NFT
     */
    async mintNFT(collectionId, tier, recipientWallet) {
        const response = await this.client.post('/api/nft/mint', {
            collectionId,
            tier,
            recipient: recipientWallet
        });
        return response.data;
    }

    /**
     * Check NFT ownership
     */
    async checkNFTOwnership(walletAddress, collectionId = null) {
        const response = await this.client.get(`/api/nft/ownership/${walletAddress}`, {
            params: { collection: collectionId }
        });
        return response.data;
    }

    /**
     * Get collection stats
     */
    async getCollectionStats(collectionId) {
        const response = await this.client.get(`/api/nft/collection/${collectionId}/stats`);
        return response.data;
    }

    // ==================== INFLUENCER ====================

    /**
     * Discover influencers
     */
    async discoverInfluencers(criteria = {}) {
        const response = await this.client.post('/api/influencer/discover', criteria);
        return response.data;
    }

    /**
     * Get influencer profile
     */
    async getInfluencer(influencerId) {
        const response = await this.client.get(`/api/influencer/${influencerId}`);
        return response.data;
    }

    /**
     * Create influencer campaign
     */
    async createInfluencerCampaign(campaign) {
        const response = await this.client.post('/api/influencer/campaign/create', campaign);
        return response.data;
    }

    /**
     * Get campaign performance
     */
    async getCampaignPerformance(campaignId) {
        const response = await this.client.get(`/api/influencer/campaign/${campaignId}/performance`);
        return response.data;
    }

    // ==================== ANALYTICS ====================

    /**
     * Track event
     */
    async trackEvent(eventType, data = {}) {
        const response = await this.client.post('/api/track', {
            eventType,
            data,
            timestamp: new Date().toISOString()
        });
        return response.data;
    }

    /**
     * Get metrics
     */
    async getMetrics(period = '7d', filters = {}) {
        const response = await this.client.get('/api/metrics', {
            params: { period, ...filters }
        });
        return response.data;
    }

    /**
     * Get analytics report
     */
    async getReport(type = 'daily', filters = {}) {
        const response = await this.client.get('/api/report', {
            params: { type, ...filters }
        });
        return response.data;
    }

    /**
     * Get attribution data
     */
    async getAttribution(filters = {}) {
        const response = await this.client.get('/api/attribution', {
            params: filters
        });
        return response.data;
    }

    // ==================== CONTENT ====================

    /**
     * Generate content
     */
    async generateContent(type, topic, options = {}) {
        const response = await this.client.post('/api/content/generate', {
            type,
            topic,
            options
        });
        return response.data;
    }

    /**
     * Get content calendar
     */
    async getContentCalendar() {
        const response = await this.client.get('/api/content/calendar');
        return response.data;
    }

    /**
     * Schedule content
     */
    async scheduleContent(contentId, publishAt, platforms = []) {
        const response = await this.client.post('/api/content/schedule', {
            contentId,
            publishAt,
            platforms
        });
        return response.data;
    }

    // ==================== COMMUNITY ====================

    /**
     * Post to all platforms
     */
    async postToAll(message, options = {}) {
        const response = await this.client.post('/api/community/post', {
            message,
            ...options
        });
        return response.data;
    }

    /**
     * Get community stats
     */
    async getCommunityStats() {
        const response = await this.client.get('/api/community/stats');
        return response.data;
    }

    /**
     * Get engagement metrics
     */
    async getEngagementMetrics(platform = 'all', period = '7d') {
        const response = await this.client.get('/api/community/engagement', {
            params: { platform, period }
        });
        return response.data;
    }

    // ==================== UTILITY ====================

    /**
     * Health check
     */
    async healthCheck() {
        const response = await this.client.get('/health');
        return response.data;
    }

    /**
     * Get API status
     */
    async getStatus() {
        const response = await this.client.get('/api/status');
        return response.data;
    }

    /**
     * Test connection
     */
    async testConnection() {
        try {
            await this.healthCheck();
            return { connected: true };
        } catch (error) {
            return { connected: false, error: error.message };
        }
    }
}

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SolanaMarketingClient;
}

if (typeof window !== 'undefined') {
    window.SolanaMarketingClient = SolanaMarketingClient;
}

// Usage example
/*
const client = new SolanaMarketingClient({
    baseURL: 'http://localhost:3000',
    apiKey: 'your-api-key'
});

// Create airdrop
const airdrop = await client.createAirdrop({
    name: 'Launch Campaign',
    amount: 10000,
    recipients: ['wallet1', 'wallet2']
});

// Create quest
const quest = await client.createQuest({
    name: 'Welcome Quest',
    tasks: [
        { type: 'discord_join', reward: 20 },
        { type: 'twitter_follow', reward: 20 }
    ]
});

// Track event
await client.trackEvent('wallet_connected', {
    wallet: 'ABC123...',
    source: 'website'
});

// Get metrics
const metrics = await client.getMetrics('7d');
*/