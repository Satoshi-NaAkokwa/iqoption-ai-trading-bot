#!/bin/bash

# Trading Bot Deployment Script
# Automates setup and deployment of the trading bot

echo "=========================================="
echo "  TRADING BOT DEPLOYMENT SCRIPT"
echo "=========================================="
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi
echo "✅ Python 3 found"
echo ""

# Check if we're in the right directory
if [ ! -f "trading_bot.py" ]; then
    echo "❌ trading_bot.py not found. Please run from trading-bot directory."
    exit 1
fi
echo "✅ In correct directory"
echo ""

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

# Check .env file
echo "🔍 Checking configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "✅ Created .env from template"
    echo ""
    echo "⚠️  IMPORTANT: Please configure your .env file:"
    echo "   1. Open .env in a text editor"
    echo "   2. Set BINANCE_API_KEY and BINANCE_SECRET_KEY"
    echo "   3. Adjust other parameters as needed"
    echo "   4. Keep DRY_RUN=true for initial testing"
    echo ""
    echo "When ready, run: bash deploy.sh"
    exit 0
fi

# Check if API keys are configured
if grep -q "your_api_key_here" .env; then
    echo "⚠️  API keys not configured in .env"
    echo ""
    echo "Please configure your Binance API credentials:"
    echo "   1. Create API key in Binance (Spot Trading only)"
    echo "   2. Update BINANCE_API_KEY in .env"
    echo "   3. Update BINANCE_SECRET_KEY in .env"
    echo "   4. Run: python3 test_api_connection.py"
    echo ""
    echo "For detailed instructions: cat BINANCE_SETUP_GUIDE.md"
    exit 0
fi

echo "✅ Configuration file found"
echo ""

# Test API connection
echo "🔄 Testing Binance API connection..."
python3 test_api_connection.py
if [ $? -ne 0 ]; then
    echo "❌ API connection test failed"
    echo ""
    echo "Please resolve API connection issues before continuing"
    echo "   1. Check your API credentials in .env"
    echo "   2. Verify API permissions in Binance"
    echo "   3. Check IP restrictions if enabled"
    echo "   4. Review BINANCE_SETUP_GUIDE.md"
    exit 1
fi
echo "✅ API connection successful"
echo ""

# Run simulation tests
echo "🧪 Running simulation tests..."
python3 simulate_bot.py > simulation_results.log 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Simulation tests failed"
    echo "   Check simulation_results.log for details"
    exit 1
fi
echo "✅ Simulation tests completed"
echo "   Results saved to simulation_results.log"
echo ""

# Check dry-run mode
echo "🔍 Checking deployment mode..."
if grep -q "DRY_RUN=true" .env; then
    echo "📋 Dry-run mode enabled (safe for testing)"
    echo ""
    echo "Starting bot in dry-run mode..."
    echo "   This will NOT place real trades"
    echo "   Press Ctrl+C to stop the bot"
    echo ""
    echo "Bot will start in 3 seconds..."
    sleep 3
    python3 trading_bot.py
else
    echo "⚠️  LIVE TRADING MODE ENABLED"
    echo ""
    echo "⚠️  WARNING: This will place REAL trades with REAL money!"
    echo ""
    echo "Before continuing, ensure you have:"
    echo "   [ ] Completed 1-2 weeks of paper trading"
    echo "   [ ] Tested with small capital ($100-500)"
    echo "   [ ] Monitored performance closely"
    echo "   [ ] Configured Telegram notifications"
    echo "   [ ] Set up emergency procedures"
    echo ""
    read -p "Are you sure you want to continue with LIVE trading? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        echo "Deployment cancelled. Set DRY_RUN=true in .env for testing."
        exit 0
    fi

    echo ""
    echo "🚀 Starting bot in LIVE trading mode..."
    echo "   This will place REAL trades!"
    echo "   Press Ctrl+C to stop the bot"
    echo ""
    echo "Bot will start in 5 seconds... (Ctrl+C to cancel)"
    sleep 5
    python3 trading_bot.py
fi

echo ""
echo "=========================================="
echo "  DEPLOYMENT COMPLETE"
echo "=========================================="
echo ""
echo "Next steps:"
echo "   • Monitor logs: tail -f trading_bot.log"
echo "   • Check performance: python3 status_check.py"
echo "   • Review documentation: cat README.md"
echo ""