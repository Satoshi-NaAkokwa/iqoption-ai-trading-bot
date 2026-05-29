module.exports = {
  apps: [
    {
      name: "iqoption-market-adaptive-v6",
      script: "bot_market_adaptive_v6.py",
      interpreter: "/home/openclaw/.openclaw/workspace/iqoption-ai-trading-bot-new/venv/bin/python3",
      cwd: "/home/openclaw/.openclaw/workspace/iqoption-ai-trading-bot-new",
      env: {
        PYTHONUNBUFFERED: "1"
      },
      error_file: "./logs/error.log",
      out_file: "./logs/out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      merge_logs: true,
      max_restarts: 10,
      restart_delay: 5000,
      watch: false,
      autorestart: true
    }
  ]
};
