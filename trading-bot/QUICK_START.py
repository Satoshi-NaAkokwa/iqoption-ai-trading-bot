#!/usr/bin/env python3
"""
Quick Start Guide - Get your trading bot running in 5 minutes
"""

import os
import sys


def print_header(text):
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70)

def print_step(step_num, text):
    print(f"\n📌 Step {step_num}: {text}")
    print("-"*70)

def main():
    print_header("TRADING BOT - QUICK START GUIDE")

    print("""
🎯 Get your stablecoin grid trading bot running in 5 minutes!

This guide will help you:
1. Configure the bot
2. Run simulations
3. Start paper trading
4. Monitor performance
""")

    # Step 1
    print_step(1, "Configure Environment Variables")
    print("""
Open the .env file and configure your settings:

BINANCE_API_KEY=your_api_key_here          # Get from Binance
BINANCE_SECRET_KEY=your_secret_key_here    # Get from Binance
TRADING_PAIR=USDCUSDT                      # Trading pair
GRID_SIZE=0.0001                           # Price gap between orders
TOTAL_INVESTMENT=100                       # Starting capital (USDT)

# Safety Settings
DRY_RUN=true                               # Set to false for real trading
MAX_POSITION_SIZE=0.7                      # Never risk >70% of capital
MAX_ORDERS_PER_SIDE=10                     # Limit concurrent orders
STOP_PRICE_DEVIATION=0.002                 # Stop if price moves 0.2%
""")

    # Step 2
    print_step(2, "Test with Simulation")
    print("""
Run the simulation to test the bot without real money:

    python3 simulate_bot.py

This will run multiple scenarios and show you how the bot performs.
Expected results:
- Low volatility: Fewer trades, stable performance
- Normal volatility: Optimal performance
- High volatility: More trades, higher exposure
""")

    # Step 3
    print_step(3, "Start Paper Trading")
    print("""
Run the bot in dry-run mode to test with real API:

    python3 trading_bot.py

The bot will:
- Connect to Binance (using your API keys)
- Place orders (simulated, no real trades)
- Track performance
- Generate logs

Monitor the logs:
    tail -f trading_bot.log
""")

    # Step 4
    print_step(4, "Enable Telegram Notifications (Optional)")
    print("""
Add to your .env file:

TELEGRAM_BOT_TOKEN=your_bot_token       # Get from @BotFather
TELEGRAM_CHAT_ID=your_chat_id           # Get from @userinfobot

The bot will send you:
- Trade execution alerts
- Daily performance reports
- Error notifications
- Status updates
""")

    # Step 5
    print_step(5, "Go Live (When Ready)")
    print("""
⚠️  IMPORTANT: Only do this after 1-2 weeks of paper trading!

1. Update .env:
   DRY_RUN=false
   TOTAL_INVESTMENT=100-500  # Start small!

2. Run the bot:
   python3 trading_bot.py

3. Monitor closely:
   - Check daily logs
   - Review P&L
   - Verify risk limits
   - Keep Telegram notifications on

4. Scale gradually:
   - Week 1: $100
   - Week 2-4: $500
   - Month 2+: $1000+ (based on performance)
""")

    # Additional Tips
    print_header("💡 PRO TIPS")

    print("""
1. START SMALL
   - Begin with $100-500
   - Never risk more than you can lose
   - Scale gradually based on performance

2. MONITOR DAILY
   - Check logs: tail -f trading_bot.log
   - Review P&L
   - Verify risk limits are working

3. KEEP API KEYS SECURE
   - Never commit .env to Git
   - Use IP restrictions
   - Enable 2FA on Binance
   - Trading-only permissions (no withdrawals)

4. EXPECT CONSISTENCY, NOT GET-RICH-QUICK
   - Target: 8-12% monthly returns
   - Small, frequent profits
   - Long-term compounding

5. HAVE AN EXIT PLAN
   - Set maximum drawdown limit
   - Know when to stop
   - Keep emergency procedures handy
""")

    # Troubleshooting
    print_header("🔧 COMMON ISSUES")

    print("""
❌ "No module named 'binance'"
   Solution: pip install -r requirements.txt

❌ "API connection failed"
   Solution: Check API keys and internet connection

❌ "Insufficient balance"
   Solution: Reduce TOTAL_INVESTMENT or add more USDT

❌ "Order failed validation"
   Solution: Check risk limits and balance

❌ "Price deviation exceeds limit"
   Solution: Market conditions unusual, bot auto-stops for safety
""")

    # Safety Checklist
    print_header("✅ SAFETY CHECKLIST")

    print("""
Before going live, make sure you have:

[ ] Binance account with 2FA enabled
[ ] API keys with "Spot Trading" only (NO withdrawals)
[ ] IP restrictions configured
[ ] Minimum capital you can afford to lose ($100-500)
[ ] Completed 1-2 weeks of paper trading
[ ] Tested emergency procedures
[ ] Telegram notifications enabled
[ ] Daily monitoring plan
[ ] Maximum drawdown limit set
[ ] Exit strategy defined
""")

    # Support
    print_header("📞 SUPPORT")

    print("""
Documentation:
- README.md - Complete user guide
- FINAL_SUMMARY.md - Project overview
- IMPLEMENTATION_STATUS.md - Progress tracking
- trading-bot-research.md - Research findings

Quick Commands:
- python3 status_check.py      # Check bot status
- python3 simulate_bot.py      # Run simulations
- python3 trading_bot.py       # Start bot
- tail -f trading_bot.log     # View logs

Emergency Stop:
- Ctrl+C to stop bot gracefully
- Bot will cancel all orders on shutdown
""")

    print_header("READY TO START?")

    print("""
Let's begin! Follow these commands:

1. Navigate to bot directory:
   cd /home/openclaw/.openclaw/workspace/trading-bot

2. Check your configuration:
   cat .env

3. Run simulation:
   python3 simulate_bot.py

4. Start paper trading:
   python3 trading_bot.py

Good luck! 🚀
""")

    # Check current status
    if os.path.exists('.env'):
        print_header("CURRENT STATUS")
        print("✅ Configuration file exists (.env)")

        with open('.env', 'r') as f:
            lines = f.readlines()
            config_complete = True

            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('=')
                    if len(parts) == 2:
                        key, value = parts
                        if 'API_KEY' in key:
                            if value == 'your_api_key_here':
                                print("⚠️  API key needs configuration")
                                config_complete = False
                            else:
                                print("✅ API key configured")
                        elif 'SECRET_KEY' in key:
                            if value == 'your_secret_key_here':
                                print("⚠️  Secret key needs configuration")
                                config_complete = False
                            else:
                                print("✅ Secret key configured")
                        elif 'DRY_RUN' in key:
                            if value.lower() == 'true':
                                print("✅ Dry-run mode enabled (safe)")
                            else:
                                print("⚠️  LIVE TRADING MODE - Be careful!")

            if config_complete:
                print("\n🎉 Configuration looks good! You can start paper trading.")
            else:
                print("\n⚠️  Please complete configuration first.")

    else:
        print("⚠️  Configuration file not found. Copy .env.example to .env first:")
        print("   cp .env.example .env")

    print("\n" + "="*70)
    print(" QUICK START GUIDE COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()