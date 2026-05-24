#!/usr/bin/env python3
"""
Test IQ Option connection
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from iqoptionapi.stable_api import IQ_Option

email = os.getenv("IQOPTION_EMAIL")
password = os.getenv("IQOPTION_PASSWORD")

print(f"\n📧 Email: {email}")
print(f"🎮 Demo Mode: True")

if not email or not password:
    print("\n❌ Credentials not configured!")
    sys.exit(1)

print("\n🔌 Connecting to IQ Option...")

try:
    api = IQ_Option(email, password)
    check, reason = api.connect()
    
    if check:
        print("✅ Connected successfully!")
        
        # Switch to practice/demo mode
        api.change_balance("PRACTICE")
        print("🎮 Switched to PRACTICE (demo) mode")
        
        balance = api.get_balance()
        print(f"💰 Balance: ${balance:.2f}")
        
        print("\n✅ Connection test PASSED!")
        print("🤖 Bot is ready to trade with paper money.")
        
    else:
        print(f"❌ Connection failed: {reason}")
        sys.exit(1)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
