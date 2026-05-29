#!/usr/bin/env node

/**
 * 30-Day Token Launch Orchestrator
 * Automatically executes marketing campaigns based on timeline
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');

// Load environment variables
require('dotenv').config({ path: path.join(require('os').homedir(), '.openclaw-env') });

class LaunchOrchestrator {
    constructor(configPath) {
        this.config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        this.startDate = new Date(this.config.startDate);
        this.currentDay = this.getCurrentDay();
        this.logs = [];
    }

    getCurrentDay() {
        const now = new Date();
        const diff = Math.floor((now - this.startDate) / (1000 * 60 * 60 * 24));
        return diff + 1; // Day 1-indexed
    }

    log(message) {
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] ${message}`;
        this.logs.push(logMessage);
        console.log(logMessage);
        
        // Write to file
        fs.appendFileSync(
            path.join(__dirname, '../logs/launch.log'),
            logMessage + '\n'
        );
    }

    async executeScript(scriptPath, args = []) {
        return new Promise((resolve, reject) => {
            const child = spawn('node', [scriptPath, ...args], {
                cwd: path.join(__dirname, '..'),
                env: process.env,
                stdio: 'inherit'
            });

            child.on('close', (code) => {
                if (code === 0) {
                    resolve();
                } else {
                    reject(new Error(`Script exited with code ${code}`));
                }
            });

            child.on('error', (err) => {
                reject(err);
            });
        });
    }

    async runDay(day) {
        this.log(`Starting Day ${day} execution...`);

        switch (day) {
            case 1:
            case 2:
            case 3:
                // Setup phase
                await this.setupPhase();
                break;

            case 4:
            case 5:
                // Community building
                await this.communitySetup();
                break;

            case 6:
            case 7:
                // Content preparation
                await this.contentPreparation();
                break;

            case 8:
            case 9:
            case 10:
                // Early adopters
                await this.earlyAdopterPhase();
                break;

            case 11:
            case 12:
                // Quest launch
                await this.questLaunch();
                break;

            case 13:
            case 14:
                // Influencer campaign
                await this.influencerSoftLaunch();
                break;

            case 15:
                // LAUNCH DAY
                await this.publicLaunch();
                break;

            case 16:
            case 17:
                // Support & engagement
                await this.postLaunchSupport();
                break;

            case 18:
            case 19:
            case 20:
            case 21:
                // Growth phase
                await this.growthPhase();
                break;

            case 22:
            case 23:
            case 24:
                // Analysis
                await this.analysisPhase();
                break;

            case 25:
            case 26:
            case 27:
                // Scaling
                await this.scalingPhase();
                break;

            case 28:
            case 29:
            case 30:
                // Retention
                await this.retentionPhase();
                break;
        }

        this.log(`Day ${day} execution completed.`);
    }

    async setupPhase() {
        this.log('🏗️  Setup Phase');
        
        // Create necessary directories
        const dirs = ['logs', 'data', 'config', 'cache'];
        dirs.forEach(dir => {
            if (!fs.existsSync(path.join(__dirname, '..', dir))) {
                fs.mkdirSync(path.join(__dirname, '..', dir), { recursive: true });
            }
        });

        // Install dependencies
        this.log('Installing dependencies...');
        execSync('npm install', { cwd: path.join(__dirname, '..'), stdio: 'inherit' });

        // Check environment variables
        this.log('Checking environment variables...');
        const requiredVars = ['SOLANA_RPC_URL', 'SOLANA_WALLET_PRIVATE_KEY'];
        const missing = requiredVars.filter(v => !process.env[v]);
        if (missing.length > 0) {
            throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
        }

        this.log('✅ Setup completed');
    }

    async communitySetup() {
        this.log('👥 Community Setup');

        // Setup Discord
        try {
            await this.executeScript(
                path.join(__dirname, 'agent-community.js'),
                ['setup-discord']
            );
            this.log('✅ Discord setup completed');
        } catch (err) {
            this.log(`⚠️  Discord setup failed: ${err.message}`);
        }

        // Setup Telegram
        try {
            await this.executeScript(
                path.join(__dirname, 'agent-community.js'),
                ['setup-telegram']
            );
            this.log('✅ Telegram setup completed');
        } catch (err) {
            this.log(`⚠️  Telegram setup failed: ${err.message}`);
        }
    }

    async contentPreparation() {
        this.log('📝 Content Preparation');

        // Generate launch content
        try {
            await this.executeScript(
                path.join(__dirname, 'agent-content.js'),
                ['prepare-launch-content']
            );
            this.log('✅ Launch content prepared');
        } catch (err) {
            this.log(`⚠️  Content preparation failed: ${err.message}`);
        }

        // Schedule announcements
        try {
            await this.executeScript(
                path.join(__dirname, 'agent-content.js'),
                ['schedule-announcements']
            );
            this.log('✅ Announcements scheduled');
        } catch (err) {
            this.log(`⚠️  Scheduling failed: ${err.message}`);
        }
    }

    async earlyAdopterPhase() {
        this.log('🚀 Early Adopter Phase');

        // Target early adopters
        try {
            await this.executeScript(
                path.join(__dirname, 'agent-airdrop.js'),
                ['early-adopters', '--amount', '5000']
            );
            this.log('✅ Early adopter airdrop completed');
        } catch (err) {
            this.log(`⚠️  Airdrop failed: ${err.message}`);
        }
    }

    async questLaunch() {
        this.log('🎯 Quest Launch');

        // Create quest
        try {
            await this.executeScript(
                path.join(__dirname, 'agent-quest.js'),
                ['create', '--config', 'config/quest-onboarding.json']
            );
            this.log('✅ Quest created');
        } catch (err) {
            this.log(`⚠️  Quest creation failed: ${err.message}`);
        }

        // Launch quest
        try {
            await this.executeScript(
                path.join(__dirname, 'agent-quest.js'),
                ['launch', '--quest', 'new_user_journey']
            );
            this.log('✅ Quest launched');
        } catch (err) {
            this.log(`⚠️  Quest launch failed: ${err.message}`);
        }
    }

    async influencerSoftLaunch() {
        this.log('📢 Influencer Soft Launch');

        try {
            await this.executeScript(
                path.join(__dirname, 'agent-influencer.js'),
                ['launch', '--campaign', 'soft-launch']
            );
            this.log('✅ Influencer campaign launched');
        } catch (err) {
            this.log(`⚠️  Influencer launch failed: ${err.message}`);
        }
    }

    async publicLaunch() {
        this.log('🎉 PUBLIC LAUNCH DAY!');

        // Execute airdrop
        try {
            await this.executeScript(
                path.join(__dirname, 'agent-airdrop.js'),
                ['execute', '--campaign', 'launch']
            );
            this.log('✅ Launch airdrop executed');
        } catch (err) {
            this.log(`⚠️  Airdrop failed: ${err.message}`);
        }

        // Announce on all channels
        try {
            await this.executeScript(
                path.join(__dirname, 'agent-community.js'),
                ['announce-launch']
            );
            this.log('✅ Launch announced');
        } catch (err) {
            this.log(`⚠️  Announcement failed: ${err.message}`);
        }

        // Publish content
        try {
            await this.executeScript(
                path.join(__dirname, 'agent-content.js'),
                ['publish-announcement']
            );
            this.log('✅ Announcement published');
        } catch (err) {
            this.log(`⚠️  Publishing failed: ${err.message}`);
        }
    }

    async postLaunchSupport() {
        this.log('🛟 Post-Launch Support');

        // Monitor engagement
        try {
            await this.executeScript(
                path.join(__dirname, 'agent-community.js'),
                ['monitor-engagement']
            );
            this.log('✅ Engagement monitored');
        } catch (err) {
            this.log(`⚠️  Monitoring failed: ${err.message}`);
        }

        // Track realtime metrics
        try {
            await this.executeScript(
                path.join(__dirname, 'agent-analytics.js'),
                ['track-realtime']
            );
            this.log('✅ Realtime tracking active');
        } catch (err) {
            this.log(`⚠️  Tracking failed: ${err.message}`);
        }
    }

    async growthPhase() {
        this.log('📈 Growth Phase');

        // Scale influencer campaigns
        try {
            await this.executeScript(
                path.join(__dirname, 'agent-influencer.js'),
                ['scale', '--budget', '2000']
            );
            this.log('✅ Influencer campaigns scaled');
        } catch (err) {
            this.log(`⚠️  Scaling failed: ${err.message}`);
        }

        // Optimize quest rewards
        try {
            await this.executeScript(
                path.join(__dirname, 'agent-quest.js'),
                ['optimize-rewards']
            );
            this.log('✅ Quest rewards optimized');
        } catch (err) {
            this.log(`⚠️  Optimization failed: ${err.message}`);
        }
    }

    async analysisPhase() {
        this.log('📊 Analysis Phase');

        // Generate reports
        try {
            await this.executeScript(
                path.join(__dirname, 'agent-analytics.js'),
                ['generate-report', '--period', '7d']
            );
            this.log('✅ Report generated');
        } catch (err) {
            this.log(`⚠️  Report generation failed: ${err.message}`);
        }

        // Identify top channels
        try {
            await this.executeScript(
                path.join(__dirname, 'agent-analytics.js'),
                ['identify-top-channels']
            );
            this.log('✅ Top channels identified');
        } catch (err) {
            this.log(`⚠️  Channel analysis failed: ${err.message}`);
        }
    }

    async scalingPhase() {
        this.log('🚀 Scaling Phase');

        // Scale successful campaigns
        try {
            await this.executeScript(
                path.join(__dirname, 'agent-airdrop.js'),
                ['scale-successful-campaigns']
            );
            this.log('✅ Campaigns scaled');
        } catch (err) {
            this.log(`⚠️  Scaling failed: ${err.message}`);
        }

        // Increase content frequency
        try {
            await this.executeScript(
                path.join(__dirname, 'agent-content.js'),
                ['increase-frequency']
            );
            this.log('✅ Content frequency increased');
        } catch (err) {
            this.log(`⚠️  Frequency adjustment failed: ${err.message}`);
        }
    }

    async retentionPhase() {
        this.log('🔒 Retention Phase');

        // Launch NFT collection
        try {
            await this.executeScript(
                path.join(__dirname, 'agent-nft.js'),
                ['launch', '--config', 'config/nft-gating.json']
            );
            this.log('✅ NFT collection launched');
        } catch (err) {
            this.log(`⚠️  NFT launch failed: ${err.message}`);
        }

        // Run retention campaign
        try {
            await this.executeScript(
                path.join(__dirname, 'agent-community.js'),
                ['retention-campaign']
            );
            this.log('✅ Retention campaign started');
        } catch (err) {
            this.log(`⚠️  Retention campaign failed: ${err.message}`);
        }
    }

    async start() {
        this.log('========================================');
        this.log('🚀 30-Day Launch Orchestrator Started');
        this.log(`Start Date: ${this.startDate.toISOString()}`);
        this.log(`Current Day: ${this.currentDay}`);
        this.log('========================================');

        if (this.currentDay < 1) {
            this.log('❌ Launch date is in the future. Waiting...');
            return;
        }

        if (this.currentDay > 30) {
            this.log('❌ Launch period has ended.');
            return;
        }

        try {
            await this.runDay(this.currentDay);
        } catch (err) {
            this.log(`❌ Error on Day ${this.currentDay}: ${err.message}`);
            throw err;
        }
    }
}

// CLI
const args = process.argv.slice(2);
const configPath = args.find(a => a.startsWith('--config'))?.split('=')[1] || 'config/launch-config.json';
const startDate = args.find(a => a.startsWith('--start-date'))?.split('=')[1];

// Create default config if not exists
if (!fs.existsSync(configPath)) {
    const defaultConfig = {
        startDate: startDate || new Date().toISOString().split('T')[0],
        budget: {
            airdrop: 10000,
            influencers: 5000,
            content: 2000,
            total: 17000
        },
        targets: {
            day30: {
                communityMembers: 10000,
                tokenHolders: 5000,
                volume: 1000000
            }
        }
    };
    
    fs.mkdirSync(path.dirname(configPath), { recursive: true });
    fs.writeFileSync(configPath, JSON.stringify(defaultConfig, null, 2));
    console.log(`Created default config at ${configPath}`);
}

const orchestrator = new LaunchOrchestrator(configPath);
orchestrator.start().catch(console.error);