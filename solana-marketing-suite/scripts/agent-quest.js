#!/usr/bin/env node

/**
 * Quest Agent - Gamified user onboarding
 * 
 * Features:
 * - Interactive quests and challenges
 * - Achievement system
 * - Leaderboards
 * - Referral tracking
 * - Reward distribution
 */

const fs = require('fs');
const path = require('path');
const { Connection, Keypair, PublicKey } = require('@solana/web3.js');
const bs58 = require('bs58');

// Load environment variables
require('dotenv').config({ path: path.join(require('os').homedir(), '.openclaw-env') });

class QuestAgent {
    constructor(configPath = '../config/quest-config.json') {
        this.config = this.loadConfig(configPath);
        this.quests = new Map();
        this.userProgress = new Map();
        this.leaderboard = [];
        this.logs = [];
    }

    loadConfig(configPath) {
        const fullPath = path.join(__dirname, configPath);
        if (fs.existsSync(fullPath)) {
            return JSON.parse(fs.readFileSync(fullPath, 'utf8'));
        }
        return {
            welcomeQuest: {
                name: 'Welcome Quest',
                tasks: [],
                totalReward: 100
            },
            leaderboard: {
                enabled: true,
                rewards: [100, 50, 25, 10, 5]
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
        fs.appendFileSync(path.join(logDir, 'agent-quest.log'), logMessage + '\n');
    }

    async initialize() {
        this.log('🎯 Initializing Quest Agent...');

        // Load quests from config
        this.loadQuests();

        this.log('✓ Quest agent initialized');
        return true;
    }

    loadQuests() {
        // Load welcome quest
        if (this.config.welcomeQuest) {
            this.quests.set('welcomeQuest', {
                id: 'welcomeQuest',
                ...this.config.welcomeQuest,
                participants: 0,
                completions: 0,
                active: true
            });
            this.log(`  Loaded quest: ${this.config.welcomeQuest.name}`);
        }

        // Load trading quest
        if (this.config.tradingQuest) {
            this.quests.set('tradingQuest', {
                id: 'tradingQuest',
                ...this.config.tradingQuest,
                participants: 0,
                completions: 0,
                active: true
            });
            this.log(`  Loaded quest: ${this.config.tradingQuest.name}`);
        }

        // Load community quest
        if (this.config.communityQuest) {
            this.quests.set('communityQuest', {
                id: 'communityQuest',
                ...this.config.communityQuest,
                participants: 0,
                completions: 0,
                active: true
            });
            this.log(`  Loaded quest: ${this.config.communityQuest.name}`);
        }

        this.log(`Total quests loaded: ${this.quests.size}`);
    }

    async createQuest(questConfig) {
        this.log(`📋 Creating quest: ${questConfig.name}...`);

        const questId = `quest_${Date.now()}`;
        const quest = {
            id: questId,
            name: questConfig.name,
            description: questConfig.description,
            enabled: questConfig.enabled !== false,
            timeLimit: questConfig.timeLimit || null,
            prerequisites: questConfig.prerequisites || [],
            tasks: questConfig.tasks.map((task, index) => ({
                id: index + 1,
                ...task,
                completed: false
            })),
            totalReward: questConfig.totalReward || 0,
            bonusReward: questConfig.bonusReward || null,
            participants: 0,
            completions: 0,
            active: true,
            createdAt: new Date().toISOString()
        };

        this.quests.set(questId, quest);
        this.log(`✓ Quest created: ${questId}`);

        return quest;
    }

    async launchQuest(questId) {
        const quest = this.quests.get(questId);
        if (!quest) {
            throw new Error(`Quest ${questId} not found`);
        }

        this.log(`🚀 Launching quest: ${quest.name}...`);

        quest.active = true;
        quest.launchedAt = new Date().toISOString();

        // Save quest state
        this.saveQuestState(questId);

        this.log(`✓ Quest launched: ${questId}`);
        return quest;
    }

    async joinQuest(questId, walletAddress) {
        const quest = this.quests.get(questId);
        if (!quest) {
            throw new Error(`Quest ${questId} not found`);
        }

        if (!quest.active) {
            throw new Error(`Quest ${questId} is not active`);
        }

        this.log(`👤 User ${walletAddress.slice(0, 8)} joining quest ${quest.name}...`);

        // Check prerequisites
        if (quest.prerequisites && quest.prerequisites.length > 0) {
            for (const prereqId of quest.prerequisites) {
                const prereqProgress = this.userProgress.get(`${walletAddress}_${prereqId}`);
                if (!prereqProgress || !prereqProgress.completed) {
                    throw new Error(`Prerequisite quest ${prereqId} not completed`);
                }
            }
        }

        // Initialize user progress
        const progressKey = `${walletAddress}_${questId}`;
        const progress = {
            wallet: walletAddress,
            questId: questId,
            startedAt: new Date().toISOString(),
            completedTasks: [],
            earnedReward: 0,
            completed: false,
            expiresAt: quest.timeLimit ? 
                new Date(Date.now() + this.parseDuration(quest.timeLimit)).toISOString() : 
                null
        };

        this.userProgress.set(progressKey, progress);
        quest.participants++;

        this.log(`✓ User joined quest`);
        return progress;
    }

    async completeTask(questId, walletAddress, taskId) {
        const quest = this.quests.get(questId);
        if (!quest) {
            throw new Error(`Quest ${questId} not found`);
        }

        const progressKey = `${walletAddress}_${questId}`;
        const progress = this.userProgress.get(progressKey);
        if (!progress) {
            throw new Error('User has not joined this quest');
        }

        const task = quest.tasks.find(t => t.id === taskId);
        if (!task) {
            throw new Error(`Task ${taskId} not found`);
        }

        this.log(`✅ Task ${taskId} completed by ${walletAddress.slice(0, 8)}...`);

        // Mark task as completed
        if (!progress.completedTasks.includes(taskId)) {
            progress.completedTasks.push(taskId);
            progress.earnedReward += task.reward;
        }

        // Check if quest is complete
        if (progress.completedTasks.length === quest.tasks.length) {
            progress.completed = true;
            progress.completedAt = new Date().toISOString();
            quest.completions++;

            // Add bonus reward if applicable
            if (quest.bonusReward) {
                progress.earnedReward += quest.bonusReward.tokens || 0;
            }

            this.log(`🎉 Quest completed by ${walletAddress.slice(0, 8)}!`);

            // Update leaderboard
            if (this.config.leaderboard?.enabled) {
                this.updateLeaderboard(walletAddress, progress.earnedReward);
            }
        }

        this.userProgress.set(progressKey, progress);
        this.saveQuestState(questId);

        return progress;
    }

    updateLeaderboard(walletAddress, points) {
        const existing = this.leaderboard.find(e => e.wallet === walletAddress);
        if (existing) {
            existing.points += points;
            existing.questsCompleted++;
        } else {
            this.leaderboard.push({
                wallet: walletAddress,
                points: points,
                questsCompleted: 1,
                lastUpdated: new Date().toISOString()
            });
        }

        // Sort by points
        this.leaderboard.sort((a, b) => b.points - a.points);
    }

    getLeaderboard(limit = 10) {
        return this.leaderboard.slice(0, limit);
    }

    async getQuestStats(questId) {
        const quest = this.quests.get(questId);
        if (!quest) {
            throw new Error(`Quest ${questId} not found`);
        }

        const stats = {
            questId: questId,
            name: quest.name,
            participants: quest.participants,
            completions: quest.completions,
            completionRate: quest.participants > 0 ? 
                (quest.completions / quest.participants * 100).toFixed(2) : 0,
            totalRewardsDistributed: quest.completions * quest.totalReward,
            tasks: quest.tasks.map(task => {
                // Would track actual completion rates per task
                return {
                    id: task.id,
                    name: task.name,
                    completionRate: 0
                };
            })
        };

        return stats;
    }

    async getUserProgress(walletAddress) {
        const progress = [];
        
        for (const [key, value] of this.userProgress.entries()) {
            if (key.startsWith(walletAddress)) {
                progress.push(value);
            }
        }

        return progress;
    }

    parseDuration(duration) {
        const match = duration.match(/^(\d+)(d|h|m|s)$/);
        if (!match) return 0;

        const value = parseInt(match[1]);
        const unit = match[2];

        switch (unit) {
            case 'd': return value * 24 * 60 * 60 * 1000;
            case 'h': return value * 60 * 60 * 1000;
            case 'm': return value * 60 * 1000;
            case 's': return value * 1000;
            default: return 0;
        }
    }

    saveQuestState(questId) {
        const dataDir = path.join(__dirname, '../data');
        if (!fs.existsSync(dataDir)) {
            fs.mkdirSync(dataDir, { recursive: true });
        }

        // Save quest
        const quest = this.quests.get(questId);
        fs.writeFileSync(
            path.join(dataDir, `quest_${questId}.json`),
            JSON.stringify(quest, null, 2)
        );

        // Save leaderboard
        fs.writeFileSync(
            path.join(dataDir, 'quest-leaderboard.json'),
            JSON.stringify(this.leaderboard, null, 2)
        );
    }

    optimizeRewards() {
        this.log('⚡ Optimizing quest rewards...');

        const optimizations = [];

        for (const [questId, quest] of this.quests.entries()) {
            const stats = this.getQuestStats(questId);
            
            // Adjust rewards based on completion rate
            if (stats.completionRate < 10) {
                optimizations.push({
                    questId: questId,
                    action: 'increase_rewards',
                    reason: 'Low completion rate'
                });
            } else if (stats.completionRate > 90) {
                optimizations.push({
                    questId: questId,
                    action: 'dease_rewards',
                    reason: 'Too easy, rewards may be too high'
                });
            }
        }

        this.log(`Generated ${optimizations.length} optimization suggestions`);
        return optimizations;
    }

    async run() {
        await this.initialize();

        this.log('Starting quest agent...');

        // Monitor quests
        setInterval(async () => {
            for (const [questId, quest] of this.quests.entries()) {
                await this.getQuestStats(questId);
            }
        }, 300000); // Every 5 minutes

        process.on('SIGINT', () => {
            this.log('Shutting down...');
            process.exit(0);
        });
    }
}

// CLI Interface
const args = process.argv.slice(2);
const agent = new QuestAgent();

if (args[0] === 'create') {
    const config = args.find(a => a.startsWith('--config'))?.split('=')[1];
    agent.initialize().then(() => {
        const cfg = config ? JSON.parse(fs.readFileSync(config, 'utf8')) : {};
        agent.createQuest(cfg);
    });
} else if (args[0] === 'launch') {
    const quest = args.find(a => a.startsWith('--quest'))?.split('=')[1];
    agent.initialize().then(() => agent.launchQuest(quest));
} else if (args[0] === 'join') {
    const quest = args.find(a => a.startsWith('--quest'))?.split('=')[1];
    const wallet = args.find(a => a.startsWith('--wallet'))?.split('=')[1];
    agent.initialize().then(() => agent.joinQuest(quest, wallet));
} else if (args[0] === 'stats') {
    const quest = args.find(a => a.startsWith('--quest'))?.split('=')[1];
    agent.initialize().then(async () => {
        const stats = await agent.getQuestStats(quest);
        console.log(JSON.stringify(stats, null, 2));
    });
} else if (args[0] === 'leaderboard') {
    agent.initialize().then(() => {
        const leaderboard = agent.getLeaderboard(10);
        console.log(JSON.stringify(leaderboard, null, 2));
    });
} else if (args[0] === 'optimize') {
    agent.initialize().then(() => agent.optimizeRewards());
} else if (args[0] === 'monitor') {
    agent.initialize().then(() => {
        console.log('Monitoring quests...');
        setInterval(() => {
            console.log(`Active quests: ${agent.quests.size}`);
            console.log(`Total participants: ${agent.userProgress.size}`);
        }, 60000);
    });
} else if (args[0] === 'start' || args.length === 0) {
    agent.run();
} else {
    console.log(`
Quest Agent - Gamified user onboarding

Usage:
  node agent-quest.js [command] [options]

Commands:
  start       Start the agent (default)
  create      Create a new quest
  launch      Launch a quest
  join        Join a quest
  stats       Get quest statistics
  leaderboard View leaderboard
  optimize    Optimize quest rewards
  monitor     Monitor quest progress

Options:
  --config=N   Quest config file
  --quest=N    Quest ID
  --wallet=N   Wallet address

Examples:
  node agent-quest.js create --config quest.json
  node agent-quest.js launch --quest welcomeQuest
  node agent-quest.js stats --quest welcomeQuest
  node agent-quest.js leaderboard
    `);
}

module.exports = QuestAgent;