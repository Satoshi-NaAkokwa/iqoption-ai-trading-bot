#!/usr/bin/env python3
"""
API Connection Tester - Verify Binance API setup
"""

import sys
from binance.client import Client
import os
from dotenv import load_dotenv


def test_api_connection():
    """Test Binance API connection and permissions"""

    print("="*70)
    print(" BINANCE API CONNECTION TESTER")
    print("="*70)
    print()

    # Load environment variables
    load_dotenv()

    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')

    # Check if credentials are set
    if not api_key or api_key == 'your_api_key_here':
        print("❌ API Key not configured!")
        print("   Please set BINANCE_API_KEY in .env file")
        return False

    if not secret_key or secret_key == 'your_secret_key_here':
        print("❌ Secret Key not configured!")
        print("   Please set BINANCE_SECRET_KEY in .env file")
        return False

    print("✅ API credentials found in .env")
    print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
    print()

    try:
        # Initialize client
        print("🔄 Connecting to Binance API...")
        client = Client(api_key, secret_key)

        # Test connection
        print("🔄 Testing API connection...")
        account = client.get_account()

        print("✅ API Connection Successful!")
        print()

        # Display account info
        print("📊 Account Information:")
        print(f"   Account Type: {account.get('accountType', 'N/A')}")
        print(f"   Can Trade: {account.get('canTrade', False)}")
        print(f"   Can Withdraw: {account.get('canWithdraw', False)}")
        print(f"   Can Deposit: {account.get('canDeposit', False)}")
        print()

        # Check balances
        print("💰 Current Balances:")
        usdt_balance = 0.0
        usdc_balance = 0.0

        for balance in account.get('balances', []):
            asset = balance['asset']
            free = float(balance['free'])
            locked = float(balance['locked'])

            if free > 0 or locked > 0:
                print(f"   {asset}: {free:.4f} (locked: {locked:.4f})")

                if asset == 'USDT':
                    usdt_balance = free
                elif asset == 'USDC':
                    usdc_balance = free

        print()

        # Test trading pair
        print("📈 Testing Trading Pair (USDCUSDT)...")
        try:
            ticker = client.get_symbol_ticker(symbol='USDCUSDT')
            price = float(ticker['price'])
            print(f"✅ USDCUSDT is tradable")
            print(f"   Current Price: ${price:.4f}")
        except Exception as e:
            print(f"❌ USDCUSDT trading issue: {e}")
            return False

        print()

        # Test order book
        print("📊 Testing Order Book Access...")
        try:
            order_book = client.get_order_book(symbol='USDCUSDT', limit=5)
            bids = order_book['bids'][:3]
            asks = order_book['asks'][:3]

            print(f"   Top 3 Bids: {[(float(bid[0]), float(bid[1])) for bid in bids]}")
            print(f"   Top 3 Asks: {[(float(ask[0]), float(ask[1])) for ask in asks]}")
            print("✅ Order book access working")
        except Exception as e:
            print(f"❌ Order book access issue: {e}")
            return False

        print()

        # Final verification
        print("="*70)
        print(" VERIFICATION RESULTS")
        print("="*70)

        issues = []

        if not account.get('canTrade', False):
            issues.append("❌ Spot Trading permission not enabled")
            print("❌ Spot Trading permission not enabled")
            print("   Please enable 'Spot Trading' in API Management")
        else:
            print("✅ Spot Trading permission enabled")

        if account.get('canWithdraw', False):
            issues.append("⚠️  Withdrawal permission enabled (NOT RECOMMENDED)")
            print("⚠️  Withdrawal permission enabled (NOT RECOMMENDED)")
            print("   Please disable 'Withdrawal' permission in API Management")
        else:
            print("✅ Withdrawal permission disabled (Good!)")

        if usdt_balance < 100:
            issues.append(f"⚠️  Low USDT balance: ${usdt_balance:.2f}")
            print(f"⚠️  Low USDT balance: ${usdt_balance:.2f}")
            print("   Minimum $100 recommended for grid trading")
        else:
            print(f"✅ Sufficient USDT balance: ${usdt_balance:.2f}")

        print()

        if issues:
            print("⚠️  Issues Found:")
            for issue in issues:
                print(f"   {issue}")
            print()
            print("Please resolve these issues before running the bot.")
            return False
        else:
            print("✅ ALL CHECKS PASSED!")
            print()
            print("Your Binance API is properly configured for trading.")
            print("You can now proceed with paper trading (DRY_RUN=true).")
            return True

    except Exception as e:
        print()
        print("="*70)
        print(" CONNECTION FAILED")
        print("="*70)
        print(f"❌ Error: {e}")
        print()

        # Provide troubleshooting suggestions
        print("TROUBLESHOOTING:")
        print("-" * 70)
        if "API-key format invalid" in str(e):
            print("• API key format is invalid")
            print("• Check that you copied the entire key")
        elif "Timestamp for this request is outside of the recvWindow" in str(e):
            print("• Time synchronization issue")
            print("• Check your system time is accurate")
        elif "Invalid API-key, IP, or permissions" in str(e):
            print("• Invalid API key or permissions")
            print("• Verify API key is still active")
            print("• Check IP restrictions if enabled")
        else:
            print("• Check your API credentials")
            print("• Verify your account is in good standing")
            print("• Ensure API key has 'Spot Trading' permission")

        print()
        print("For more help:")
        print("• Check Binance API documentation")
        print("• Review BINANCE_SETUP_GUIDE.md")
        print("• Contact Binance support if issues persist")

        return False


if __name__ == "__main__":
    success = test_api_connection()
    sys.exit(0 if success else 1)