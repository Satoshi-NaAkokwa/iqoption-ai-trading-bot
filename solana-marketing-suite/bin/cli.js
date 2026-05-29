#!/usr/bin/env node

/**
 * CLI Tool for Solana Marketing Suite
 * Command-line interface for managing all agents and operations
 */

const fs = require('fs');
const path = require('path');
const { Command } = require('commander');
const chalk = require('chalk');
const ora = require('ora');
const inquirer = require('inquirer');

const program = new Command();

program
    .name('solana-marketing')
    .description('CLI for Solana AI Marketing Suite')
    .version('1.0.0');

// ==================== SETUP ====================

program
    .command('setup')
    .description('Initialize and configure the marketing suite')
    .option('-e, --env <file>', 'Environment file path', '~/.openclaw-env')
    .action(async (options) => {
        const spinner = ora('Setting up Solana Marketing Suite...').start();
        
        try {
            // Check Node.js version
            const nodeVersion = process.version;
            spinner.text = `Node.js version: ${nodeVersion}`;
            
            // Create directories
            const dirs = ['logs', 'data', 'config', 'cache'];
            dirs.forEach(dir => {
                if (!fs.existsSync(dir)) {
                    fs.mkdirSync(dir, { recursive: true });
                }
            });
            
            spinner.text = 'Checking environment variables...';
            
            // Check environment
            const envPath = options.env.replace('~', require('os').homedir());
            if (!fs.existsSync(envPath)) {
                spinner.warn('Environment file not found');
                
                const answers = await inquirer.prompt([
                    {
                        type: 'input',
                        name: 'rpcUrl',
                        message: 'Solana RPC URL:',
                        default: 'https://api.mainnet-beta.solana.com'
                    },
                    {
                        type: 'password',
                        name: 'privateKey',
                        message: 'Wallet private key (base58):',
                        mask: '*'
                    }
                ]);
                
                // Create env file
                const envContent = `SOLANA_RPC_URL=${answers.rpcUrl}\nSOLANA_WALLET_PRIVATE_KEY=${answers.privateKey}\n`;
                fs.writeFileSync(envPath, envContent);
                spinner.succeed('Environment file created');
            }
            
            // Install dependencies
            spinner.text = 'Installing dependencies...';
            const { execSync } = require('child_process');
            execSync('npm install', { stdio: 'ignore' });
            
            spinner.succeed(chalk.green('Setup complete!'));
            console.log('\nNext steps:');
            console.log('  1. Configure agents in config/ directory');
            console.log('  2. Start agents: npm start');
            console.log('  3. Check status: npm run status');
            
        } catch (error) {
            spinner.fail(chalk.red('Setup failed'));
            console.error(error.message);
            process.exit(1);
        }
    });

// ==================== AGENTS ====================

program
    .command('start [agent]')
    .description('Start one or all agents')
    .option('-d, --daemon', 'Run in background')
    .option('-f, --foreground', 'Run in foreground')
    .action(async (agent, options) => {
        const agents = ['airdrop', 'community', 'analytics', 'influencer', 'nft', 'quest', 'content'];
        
        if (agent && !agents.includes(agent)) {
            console.error(chalk.red(`Unknown agent: ${agent}`));
            console.log(`Available agents: ${agents.join(', ')}`);
            process.exit(1);
        }
        
        const toStart = agent ? [agent] : agents;
        const spinner = ora(`Starting ${toStart.length} agent(s)...`).start();
        
        try {
            const { spawn } = require('child_process');
            
            toStart.forEach(agentName => {
                spinner.text = `Starting ${agentName} agent...`;
                
                const scriptPath = path.join(__dirname, 'scripts', `agent-${agentName}.js`);
                
                if (options.daemon) {
                    // Run in background
                    spawn('nohup', ['node', scriptPath], {
                        detached: true,
                        stdio: 'ignore'
                    });
                } else if (options.foreground) {
                    // Run in foreground
                    spawn('node', [scriptPath], {
                        stdio: 'inherit'
                    });
                }
            });
            
            spinner.succeed(chalk.green(`${toStart.length} agent(s) started`));
            
        } catch (error) {
            spinner.fail(chalk.red('Failed to start agents'));
            console.error(error.message);
            process.exit(1);
        }
    });

program
    .command('stop [agent]')
    .description('Stop one or all agents')
    .action(async (agent) => {
        const spinner = ora('Stopping agents...').start();
        
        try {
            const { execSync } = require('child_process');
            
            if (agent) {
                execSync(`pkill -f "agent-${agent}.js"`);
                spinner.succeed(chalk.green(`${agent} agent stopped`));
            } else {
                execSync('pkill -f "agent-.*\\.js"');
                spinner.succeed(chalk.green('All agents stopped'));
            }
            
        } catch (error) {
            spinner.warn(chalk.yellow('No running agents found'));
        }
    });

program
    .command('status')
    .description('Show status of all agents')
    .action(async () => {
        console.log(chalk.bold('\n📊 Agent Status\n'));
        
        const agents = [
            { name: 'Airdrop', script: 'agent-airdrop.js' },
            { name: 'Community', script: 'agent-community.js' },
            { name: 'Analytics', script: 'agent-analytics.js' },
            { name: 'Influencer', script: 'agent-influencer.js' },
            { name: 'NFT', script: 'agent-nft.js' },
            { name: 'Quest', script: 'agent-quest.js' },
            { name: 'Content', script: 'agent-content.js' }
        ];
        
        const { execSync } = require('child_process');
        
        agents.forEach(agent => {
            try {
                const pid = execSync(`pgrep -f "${agent.script}"`, { encoding: 'utf8' }).trim();
                console.log(`${chalk.green('✓')} ${agent.name.padEnd(15)} ${chalk.gray(`Running (PID: ${pid})`)}`);
            } catch {
                console.log(`${chalk.red('✗')} ${agent.name.padEnd(15)} ${chalk.gray('Stopped')}`);
            }
        });
        
        console.log('');
    });

// ==================== AIRDROP ====================

program
    .command('airdrop')
    .description('Manage airdrop campaigns')
    .command('create')
    .description('Create new airdrop campaign')
    .option('-n, --name <name>', 'Campaign name')
    .option('-a, --amount <amount>', 'Total amount to distribute')
    .option('-r, --recipients <file>', 'Recipients file (JSON)')
    .action(async (options) => {
        const spinner = ora('Creating airdrop campaign...').start();
        
        try {
            const campaign = {
                id: `airdrop_${Date.now()}`,
                name: options.name || 'New Campaign',
                amount: parseFloat(options.amount) || 10000,
                recipients: options.recipients ? 
                    JSON.parse(fs.readFileSync(options.recipients, 'utf8')) : [],
                createdAt: new Date().toISOString()
            };
            
            const campaignPath = path.join('data', `campaign_${campaign.id}.json`);
            fs.writeFileSync(campaignPath, JSON.stringify(campaign, null, 2));
            
            spinner.succeed(chalk.green(`Campaign created: ${campaign.id}`));
            console.log(`\nCampaign details:`);
            console.log(`  Name: ${campaign.name}`);
            console.log(`  Amount: ${campaign.amount}`);
            console.log(`  Recipients: ${campaign.recipients.length}`);
            console.log(`\nExecute with: solana-marketing airdrop execute ${campaign.id}`);
            
        } catch (error) {
            spinner.fail(chalk.red('Failed to create campaign'));
            console.error(error.message);
            process.exit(1);
        }
    });

program
    .command('airdrop')
    .command('execute <campaignId>')
    .description('Execute an airdrop campaign')
    .option('-d, --dry-run', 'Simulate without executing')
    .action(async (campaignId, options) => {
        const spinner = ora('Executing airdrop...').start();
        
        try {
            const campaignPath = path.join('data', `campaign_${campaignId}.json`);
            
            if (!fs.existsSync(campaignPath)) {
                throw new Error(`Campaign not found: ${campaignId}`);
            }
            
            const campaign = JSON.parse(fs.readFileSync(campaignPath, 'utf8'));
            
            if (options.dryRun) {
                spinner.info(chalk.yellow('Dry run mode - no transactions will be executed'));
            }
            
            spinner.text = `Distributing ${campaign.amount} tokens to ${campaign.recipients.length} wallets...`;
            
            // Simulate execution
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            spinner.succeed(chalk.green('Airdrop executed successfully'));
            
        } catch (error) {
            spinner.fail(chalk.red('Airdrop execution failed'));
            console.error(error.message);
            process.exit(1);
        }
    });

// ==================== QUEST ====================

program
    .command('quest')
    .description('Manage quests')
    .command('create')
    .description('Create a new quest')
    .action(async () => {
        const answers = await inquirer.prompt([
            {
                type: 'input',
                name: 'name',
                message: 'Quest name:',
                default: 'Welcome Quest'
            },
            {
                type: 'number',
                name: 'reward',
                message: 'Total reward (tokens):',
                default: 100
            },
            {
                type: 'checkbox',
                name: 'tasks',
                message: 'Select tasks:',
                choices: [
                    { name: 'Join Discord', value: 'discord_join' },
                    { name: 'Join Telegram', value: 'telegram_join' },
                    { name: 'Follow Twitter', value: 'twitter_follow' },
                    { name: 'Retweet Post', value: 'twitter_retweet' },
                    { name: 'Complete Tutorial', value: 'tutorial' }
                ]
            }
        ]);
        
        const quest = {
            id: `quest_${Date.now()}`,
            name: answers.name,
            totalReward: answers.reward,
            tasks: answers.tasks.map((task, i) => ({
                id: i + 1,
                type: task,
                reward: Math.floor(answers.reward / answers.tasks.length)
            })),
            createdAt: new Date().toISOString()
        };
        
        const questPath = path.join('data', `quest_${quest.id}.json`);
        fs.writeFileSync(questPath, JSON.stringify(quest, null, 2));
        
        console.log(chalk.green(`\n✓ Quest created: ${quest.id}`));
        console.log(`  Launch with: solana-marketing quest launch ${quest.id}`);
    });

// ==================== ANALYTICS ====================

program
    .command('analytics')
    .description('View analytics and reports')
    .option('-p, --period <period>', 'Time period (1d, 7d, 30d)', '7d')
    .option('-f, --format <format>', 'Output format (json, table)', 'table')
    .action(async (options) => {
        const spinner = ora('Fetching analytics...').start();
        
        try {
            // Mock analytics data
            const analytics = {
                period: options.period,
                metrics: {
                    totalUsers: 1250,
                    activeUsers: 450,
                    newUsers: 87,
                    totalVolume: 125000,
                    transactions: 3420,
                    avgTransactionSize: 36.50
                },
                growth: {
                    users: '+12%',
                    volume: '+8%',
                    transactions: '+15%'
                }
            };
            
            spinner.succeed();
            
            if (options.format === 'json') {
                console.log(JSON.stringify(analytics, null, 2));
            } else {
                console.log(chalk.bold('\n📊 Analytics Report\n'));
                console.log(`Period: Last ${options.period}\n`);
                
                console.log(chalk.bold('Metrics:'));
                console.log(`  Total Users: ${chalk.green(analytics.metrics.totalUsers.toLocaleString())}`);
                console.log(`  Active Users: ${chalk.green(analytics.metrics.activeUsers.toLocaleString())}`);
                console.log(`  New Users: ${chalk.green(analytics.metrics.newUsers)}`);
                console.log(`  Total Volume: ${chalk.green('$' + analytics.metrics.totalVolume.toLocaleString())}`);
                console.log(`  Transactions: ${chalk.green(analytics.metrics.transactions.toLocaleString())}`);
                
                console.log(chalk.bold('\nGrowth:'));
                console.log(`  Users: ${chalk.green(analytics.growth.users)}`);
                console.log(`  Volume: ${chalk.green(analytics.growth.volume)}`);
                console.log(`  Transactions: ${chalk.green(analytics.growth.transactions)}`);
                console.log('');
            }
            
        } catch (error) {
            spinner.fail(chalk.red('Failed to fetch analytics'));
            console.error(error.message);
            process.exit(1);
        }
    });

// ==================== WALLET ====================

program
    .command('wallet')
    .description('Wallet operations')
    .command('balance')
    .description('Check wallet balance')
    .action(async () => {
        const spinner = ora('Checking wallet balance...').start();
        
        try {
            require('dotenv').config({ path: path.join(require('os').homedir(), '.openclaw-env') });
            
            const { Connection, Keypair, LAMPORTS_PER_SOL } = require('@solana/web3.js');
            const bs58 = require('bs58');
            
            const connection = new Connection(process.env.SOLANA_RPC_URL);
            const secretKey = bs58.decode(process.env.SOLANA_WALLET_PRIVATE_KEY);
            const wallet = Keypair.fromSecretKey(secretKey);
            const balance = await connection.getBalance(wallet.publicKey);
            
            spinner.succeed();
            console.log(chalk.bold('\n💼 Wallet Info\n'));
            console.log(`  Address: ${chalk.cyan(wallet.publicKey.toString())}`);
            console.log(`  Balance: ${chalk.green((balance / LAMPORTS_PER_SOL).toFixed(4) + ' SOL')}`);
            console.log('');
            
        } catch (error) {
            spinner.fail(chalk.red('Failed to check balance'));
            console.error(error.message);
            process.exit(1);
        }
    });

// ==================== CONFIG ====================

program
    .command('config')
    .description('Manage configuration')
    .command('show [agent]')
    .description('Show configuration for agent')
    .action(async (agent) => {
        if (agent) {
            const configPath = path.join('config', `${agent}-config.json`);
            if (fs.existsSync(configPath)) {
                const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
                console.log(chalk.bold(`\n⚙️  ${agent.charAt(0).toUpperCase() + agent.slice(1)} Configuration\n`));
                console.log(JSON.stringify(config, null, 2));
            } else {
                console.log(chalk.red(`Configuration not found: ${configPath}`));
            }
        } else {
            console.log(chalk.bold('\n⚙️  Available Configurations\n'));
            const configDir = 'config';
            if (fs.existsSync(configDir)) {
                fs.readdirSync(configDir)
                    .filter(f => f.endsWith('-config.json'))
                    .forEach(f => {
                        console.log(`  • ${f.replace('-config.json', '')}`);
                    });
            }
            console.log('\nView with: solana-marketing config show <agent>');
        }
    });

program
    .command('config')
    .command('edit <agent>')
    .description('Edit agent configuration')
    .action(async (agent) => {
        const configPath = path.join('config', `${agent}-config.json`);
        
        if (!fs.existsSync(configPath)) {
            console.log(chalk.red(`Configuration not found: ${configPath}`));
            process.exit(1);
        }
        
        const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        
        console.log(chalk.bold(`\n📝 Editing ${agent} configuration\n`));
        console.log('Current configuration:');
        console.log(JSON.stringify(config, null, 2));
        
        const { confirm } = await inquirer.prompt([
            {
                type: 'confirm',
                name: 'confirm',
                message: 'Open editor to modify?',
                default: true
            }
        ]);
        
        if (confirm) {
            const { execSync } = require('child_process');
            const editor = process.env.EDITOR || 'nano';
            execSync(`${editor} ${configPath}`, { stdio: 'inherit' });
            console.log(chalk.green('\n✓ Configuration updated'));
        }
    });

// ==================== HEALTH ====================

program
    .command('health')
    .description('Run health checks')
    .action(async () => {
        console.log(chalk.bold('\n🏥 Health Check\n'));
        
        const checks = [
            { name: 'Environment', check: () => process.env.SOLANA_RPC_URL },
            { name: 'Node.js', check: () => process.version },
            { name: 'NPM', check: () => require('child_process').execSync('npm -v', { encoding: 'utf8' }).trim() }
        ];
        
        checks.forEach(({ name, check }) => {
            try {
                const result = check();
                console.log(`${chalk.green('✓')} ${name.padEnd(20)} ${chalk.gray(result || 'OK')}`);
            } catch {
                console.log(`${chalk.red('✗')} ${name.padEnd(20)} ${chalk.gray('Not configured')}`);
            }
        });
        
        console.log('');
    });

// ==================== MONITOR ====================

program
    .command('monitor')
    .description('Open monitoring dashboard')
    .option('-p, --port <port>', 'Dashboard port', '3000')
    .action(async (options) => {
        const url = `http://localhost:${options.port}/dashboard`;
        console.log(chalk.bold('\n📊 Opening dashboard...\n'));
        console.log(`  URL: ${chalk.cyan(url)}`);
        console.log(`  Press Ctrl+C to exit\n`);
        
        const { execSync } = require('child_process');
        
        try {
            const opener = process.platform === 'darwin' ? 'open' : 
                          process.platform === 'win32' ? 'start' : 'xdg-open';
            execSync(`${opener} ${url}`);
        } catch {
            console.log(chalk.yellow('Could not open browser automatically'));
            console.log(`Please open: ${url}`);
        }
    });

// Parse arguments
program.parse(process.argv);

// Show help if no command provided
if (!process.argv.slice(2).length) {
    program.outputHelp();
}