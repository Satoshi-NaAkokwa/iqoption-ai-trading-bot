/**
 * Testing Framework for Solana Marketing Suite
 * Comprehensive test suite for all agents
 */

const { expect } = require('chai');
const path = require('path');

// Load environment
require('dotenv').config({ path: path.join(require('os').homedir(), '.openclaw-env') });

class TestSuite {
    constructor() {
        this.tests = [];
        this.results = {
            passed: 0,
            failed: 0,
            skipped: 0
        };
    }

    test(name, fn) {
        this.tests.push({ name, fn });
    }

    async run() {
        console.log('\n🧪 Running Test Suite\n');
        console.log('═'.repeat(60));

        for (const test of this.tests) {
            try {
                console.log(`\n📝 ${test.name}`);
                await test.fn();
                this.results.passed++;
                console.log(`✅ PASSED`);
            } catch (error) {
                this.results.failed++;
                console.log(`❌ FAILED: ${error.message}`);
                console.log(`   ${error.stack}`);
            }
        }

        console.log('\n' + '═'.repeat(60));
        console.log('\n📊 Test Results:');
        console.log(`   ✅ Passed: ${this.results.passed}`);
        console.log(`   ❌ Failed: ${this.results.failed}`);
        console.log(`   ⏭️ Skipped: ${this.results.skipped}`);
        console.log(`   📈 Total: ${this.tests.length}`);
        console.log('');

        return this.results;
    }
}

// Helper functions
const helpers = {
    // Test wallet address validation
    isValidWallet: (address) => {
        const regex = /^[1-9A-HJ-NP-Za-km-z]{44}$/;
        return regex.test(address);
    },

    // Test signature validation
    isValidSignature: (signature) => {
        const regex = /^[1-9A-HJ-NP-Za-km-z]{87,88}$/;
        return regex.test(signature);
    },

    // Test file existence
    fileExists: (filepath) => {
        const fs = require('fs');
        return fs.existsSync(filepath);
    },

    // Test JSON parsing
    parseJSON: (str) => {
        try {
            return JSON.parse(str);
        } catch {
            return null;
        }
    },

    // Test configuration loading
    loadConfig: (agent) => {
        const fs = require('fs');
        const path = require('path');
        const configPath = path.join(__dirname, `../config/${agent}-config.json`);
        
        if (!fs.existsSync(configPath)) {
            throw new Error(`Config not found: ${configPath}`);
        }
        
        return JSON.parse(fs.readFileSync(configPath, 'utf8'));
    },

    // Test environment variable
    getEnv: (key) => {
        return process.env[key];
    },

    // Test JSON schema validation
    validateSchema: (obj, schema) => {
        const errors = [];
        
        for (const [key, type] of Object.entries(schema)) {
            if (!(key in obj)) {
                errors.push(`Missing required field: ${key}`);
                continue;
            }
            
            if (typeof obj[key] !== type) {
                errors.push(`Field ${key} should be ${type}, got ${typeof obj[key]}`);
            }
        }
        
        return errors.length === 0 ? null : errors;
    }
};

// Create test suite
const suite = new TestSuite();

// ==================== ENVIRONMENT TESTS ====================

suite.test('Environment: SOLANA_RPC_URL is set', () => {
    const rpcUrl = helpers.getEnv('SOLANA_RPC_URL');
    expect(rpcUrl).to.not.be.undefined;
    expect(rpcUrl).to.include('http');
});

suite.test('Environment: SOLANA_WALLET_PRIVATE_KEY is set', () => {
    const privateKey = helpers.getEnv('SOLANA_WALLET_PRIVATE_KEY');
    expect(privateKey).to.not.be.undefined;
    expect(privateKey).to.have.length.greaterThan(50);
});

// ==================== CONFIGURATION TESTS ====================

suite.test('Config: Airdrop config exists and is valid', () => {
    const config = helpers.loadConfig('airdrop');
    expect(config).to.be.an('object');
    expect(config).to.have.property('targetWallets');
    expect(config.targetWallets).to.have.property('whales');
    expect(config.targetWallets).to.have.property('active');
    expect(config.targetWallets).to.have.property('casual');
});

suite.test('Config: Community config exists and is valid', () => {
    const config = helpers.loadConfig('community');
    expect(config).to.be.an('object');
    expect(config).to.have.property('posting');
    expect(config).to.have.property('hashtags');
});

suite.test('Config: Analytics config exists and is valid', () => {
    const config = helpers.loadConfig('analytics');
    expect(config).to.be.an('object');
    expect(config).to.have.property('tracking');
    expect(config).to.have.property('reporting');
});

suite.test('Config: All 7 config files exist', () => {
    const agents = ['airdrop', 'community', 'analytics', 'influencer', 'nft', 'quest', 'content'];
    
    for (const agent of agents) {
        const exists = helpers.fileExists(`config/${agent}-config.json`);
        expect(exists).to.be.true;
    }
});

// ==================== AGENT SCRIPT TESTS ====================

suite.test('Agents: All agent scripts exist', () => {
    const agents = [
        'agent-airdrop.js',
        'agent-community.js',
        'agent-analytics.js',
        'agent-influencer.js',
        'agent-nft.js',
        'agent-quest.js',
        'agent-content.js'
    ];
    
    for (const agent of agents) {
        const exists = helpers.fileExists(`scripts/${agent}`);
        expect(exists).to.be.true;
    }
});

suite.test('Agents: Airdrop agent can be required', () => {
    const AirdropAgent = require('../scripts/agent-airdrop');
    expect(AirdropAgent).to.be.a('function');
});

suite.test('Agents: Community agent can be required', () => {
    const CommunityAgent = require('../scripts/agent-community');
    expect(CommunityAgent).to.be.a('function');
});

// ==================== VALIDATION TESTS ====================

suite.test('Validation: Valid wallet address', () => {
    const validWallet = '7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU';
    expect(helpers.isValidWallet(validWallet)).to.be.true;
});

suite.test('Validation: Invalid wallet address', () => {
    const invalidWallet = 'invalid-wallet';
    expect(helpers.isValidWallet(invalidWallet)).to.be.false;
});

suite.test('Validation: Valid signature', () => {
    const validSig = '5X7d8iKjPXLmL6gUqRnNKF7zS8KvZcL6XQ5J3g9eR2yKzN8sJw6XyQ9F3vR2cK8jZv';
    expect(helpers.isValidSignature(validSig)).to.be.true;
});

suite.test('Validation: Invalid signature', () => {
    const invalidSig = 'invalid-signature';
    expect(helpers.isValidSignature(invalidSig)).to.be.false;
});

// ==================== SCHEMA TESTS ====================

suite.test('Schema: Airdrop campaign schema validation', () => {
    const campaign = {
        campaign: 'test_campaign',
        amount: 10000,
        recipients: ['wallet1', 'wallet2']
    };
    
    const schema = {
        campaign: 'string',
        amount: 'number',
        recipients: 'object'
    };
    
    const errors = helpers.validateSchema(campaign, schema);
    expect(errors).to.be.null;
});

suite.test('Schema: Quest schema validation', () => {
    const quest = {
        name: 'Test Quest',
        totalReward: 100,
        tasks: [
            { type: 'discord_join', reward: 20 }
        ]
    };
    
    const schema = {
        name: 'string',
        totalReward: 'number',
        tasks: 'object'
    };
    
    const errors = helpers.validateSchema(quest, schema);
    expect(errors).to.be.null;
});

// ==================== INTEGRATION TESTS ====================

suite.test('Integration: SDK can be imported', () => {
    const SDK = require('../lib/sdk');
    expect(SDK).to.be.a('function');
});

suite.test('Integration: API client can be imported', () => {
    const Client = require('../lib/client');
    expect(Client).to.be.a('function');
});

suite.test('Integration: API server can be imported', () => {
    const APIServer = require('../lib/api-server');
    expect(APIServer).to.be.a('function');
});

// ==================== FILE STRUCTURE TESTS ====================

suite.test('Files: Documentation files exist', () => {
    const docs = [
        'README.md',
        'SETUP_GUIDE.md',
        'EXAMPLES.md',
        'GETTING_STARTED.md',
        'DEPLOYMENT.md',
        'QUICK_REFERENCE.md',
        'PROJECT_SUMMARY.md'
    ];
    
    for (const doc of docs) {
        const exists = helpers.fileExists(doc);
        expect(exists).to.be.true;
    }
});

suite.test('Files: Infrastructure files exist', () => {
    const files = [
        'docker-compose.yml',
        'Dockerfile',
        'ecosystem.config.js',
        'nginx.conf',
        'Makefile',
        'package.json'
    ];
    
    for (const file of files) {
        const exists = helpers.fileExists(file);
        expect(exists).to.be.true;
    }
});

// ==================== SECURITY TESTS ====================

suite.test('Security: Environment file has proper permissions', () => {
    const fs = require('fs');
    const envPath = path.join(require('os').homedir(), '.openclaw-env');
    
    if (fs.existsSync(envPath)) {
        const stats = fs.statSync(envPath);
        // File should be readable by owner only (mode 600)
        const mode = (stats.mode & parseInt('777', 8)).toString(8);
        expect(mode).to.equal('600');
    }
});

suite.test('Security: No private keys in config files', () => {
    const fs = require('fs');
    const configDir = 'config';
    const configFiles = fs.readdirSync(configDir).filter(f => f.endsWith('.json'));
    
    for (const file of configFiles) {
        const content = fs.readFileSync(`${configDir}/${file}`, 'utf8');
        expect(content).to.not.include('private_key');
        expect(content).to.not.include('PRIVATE_KEY');
    }
});

// ==================== UTILITY TESTS ====================

suite.test('Utilities: Helper functions exist', () => {
    expect(helpers).to.be.an('object');
    expect(helpers.isValidWallet).to.be.a('function');
    expect(helpers.isValidSignature).to.be.a('function');
    expect(helpers.fileExists).to.be.a('function');
    expect(helpers.parseJSON).to.be.a('function');
});

// ==================== PERFORMANCE TESTS ====================

suite.test('Performance: Config loading is fast (< 100ms)', async () => {
    const start = Date.now();
    helpers.loadConfig('airdrop');
    const duration = Date.now() - start;
    expect(duration).to.be.lessThan(100);
});

// ==================== RUN TESTS ====================

if (require.main === module) {
    suite.run().then((results) => {
        process.exit(results.failed > 0 ? 1 : 0);
    });
}

module.exports = { suite, helpers };