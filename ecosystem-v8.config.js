module.exports = {
  apps: [{
    name: "iqoption-v8-high-winrate",
    script: "bot_high_winrate_v8.py",
    cwd: "/home/openclaw/.openclaw/workspace/iqoption-ai-trading-bot-new",
    interpreter: "/home/openclaw/.openclaw/workspace/iqoption-ai-trading-bot-new/venv/bin/python",
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: "500M",
    error_file: "./logs/error-v8.log",
    out_file: "./logs/out-v8.log",
    log_file: "./logs/combined-v8.log",
    time: true,
    merge_logs: true,
    log_date_format: "YYYY-MM-DD HH:mm:ss"
  }]
};
