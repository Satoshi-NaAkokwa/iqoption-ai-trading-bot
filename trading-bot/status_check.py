#!/usr/bin/env python3
"""
Quick Status Check - Shows simulation progress and bot readiness
"""

import os
import subprocess
import time
from datetime import datetime

def check_bot_status():
    """Check if bot is running"""
    try:
        result = subprocess.run(['pgrep', '-f', 'simulate_bot.py'], capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, None
    except:
        return False, None

def check_logs():
    """Get recent log entries"""
    if not os.path.exists('trading_bot.log'):
        return "No log file found"

    try:
        with open('trading_bot.log', 'r') as f:
            lines = f.readlines()
            if len(lines) > 20:
                return '\n'.join(lines[-20:])
            return '\n'.join(lines)
    except:
        return "Error reading logs"

def main():
    print("="*60)
    print("TRADING BOT STATUS CHECK")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check if simulation is running
    is_running, pid = check_bot_status()
    if is_running:
        print(f"✅ Simulation Running (PID: {pid})")
    else:
        print("❌ Simulation Not Running")

    print()

    # Show recent logs
    print("Recent Log Entries:")
    print("-" * 60)
    logs = check_logs()
    print(logs)

    print()
    print("="*60)
    print("STATUS SUMMARY")
    print("="*60)

    # Check components
    components = {
        'trading_bot.py': 'Main bot orchestrator',
        'binance_client.py': 'Binance API client',
        'grid_manager.py': 'Grid strategy logic',
        'risk_manager.py': 'Risk management',
        'simulate_bot.py': 'Simulation engine'
    }

    for filename, description in components.items():
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✅ {filename:<25} ({description}) - {size:,} bytes")
        else:
            print(f"❌ {filename:<25} ({description}) - MISSING")

    print()
    print("Configuration:")
    print("-" * 60)
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            # Show safe config values only
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Hide sensitive values
                    if 'API_KEY' in line or 'SECRET' in line:
                        parts = line.split('=')
                        if len(parts) == 2:
                            print(f"{parts[0]}=***HIDDEN***")
                    else:
                        print(line)

    print()
    print("="*60)
    print("DEPLOYMENT READINESS")
    print("="*60)

    readiness_checks = [
        ('Bot Framework Developed', True),
        ('Risk Controls Implemented', True),
        ('Simulation Testing', 'IN PROGRESS'),
        ('Binance API Credentials', False),
        ('Paper Trading Validated', False),
        ('Monitoring System', False),
        ('Emergency Procedures', True),
    ]

    for check, status in readiness_checks:
        status_icon = "✅" if status == True else "⏳" if status == "IN PROGRESS" else "❌"
        print(f"{status_icon} {check}")

    print()
    print("="*60)
    print("QUICK ACTIONS")
    print("="*60)
    print("Run simulation: python3 simulate_bot.py")
    print("Run bot (dry-run): python3 trading_bot.py")
    print("View logs: tail -f trading_bot.log")
    print("Check status: python3 status_check.py")
    print()

if __name__ == "__main__":
    main()