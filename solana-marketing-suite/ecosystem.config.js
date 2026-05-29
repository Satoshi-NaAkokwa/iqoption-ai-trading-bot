// PM2 Ecosystem Configuration
// Use this for production deployment with auto-restart and clustering

module.exports = {
  apps: [
    {
      name: 'airdrop-agent',
      script: './scripts/agent-airdrop.js',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production',
        LOG_LEVEL: 'info'
      },
      env_development: {
        NODE_ENV: 'development',
        LOG_LEVEL: 'debug'
      },
      error_file: './logs/airdrop-error.log',
      out_file: './logs/airdrop-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      cron_restart: '0 0 * * *', // Restart daily at midnight
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000
    },
    {
      name: 'community-agent',
      script: './scripts/agent-community.js',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/community-error.log',
      out_file: './logs/community-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      cron_restart: '0 0 * * *',
      min_uptime: '10s',
      max_restarts: 10
    },
    {
      name: 'analytics-agent',
      script: './scripts/agent-analytics.js',
      args: 'server --port 3000',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      },
      error_file: './logs/analytics-error.log',
      out_file: './logs/analytics-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      cron_restart: '0 0 * * *',
      min_uptime: '10s',
      max_restarts: 10
    },
    {
      name: 'influencer-agent',
      script: './scripts/agent-influencer.js',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/influencer-error.log',
      out_file: './logs/influencer-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      cron_restart: '0 0 * * *',
      min_uptime: '10s',
      max_restarts: 10
    },
    {
      name: 'nft-agent',
      script: './scripts/agent-nft.js',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/nft-error.log',
      out_file: './logs/nft-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      cron_restart: '0 0 * * *',
      min_uptime: '10s',
      max_restarts: 10
    },
    {
      name: 'quest-agent',
      script: './scripts/agent-quest.js',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/quest-error.log',
      out_file: './logs/quest-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      cron_restart: '0 0 * * *',
      min_uptime: '10s',
      max_restarts: 10
    },
    {
      name: 'content-agent',
      script: './scripts/agent-content.js',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/content-error.log',
      out_file: './logs/content-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      cron_restart: '0 0 * * *',
      min_uptime: '10s',
      max_restarts: 10
    }
  ],

  deploy: {
    production: {
      user: 'deploy',
      host: ['your-server.com'],
      ref: 'origin/main',
      repo: 'git@github.com:your-org/solana-marketing-suite.git',
      path: '/var/www/solana-marketing-suite',
      'post-deploy': 'npm install && pm2 reload ecosystem.config.js --env production',
      'pre-setup': 'apt-get install git -y'
    },
    staging: {
      user: 'deploy',
      host: ['staging.your-server.com'],
      ref: 'origin/develop',
      repo: 'git@github.com:your-org/solana-marketing-suite.git',
      path: '/var/www/solana-marketing-suite-staging',
      'post-deploy': 'npm install && pm2 reload ecosystem.config.js --env development',
      env: {
        NODE_ENV: 'staging'
      }
    }
  }
};