#!/usr/bin/env python3
"""
Performance Dashboard - Real-time trading bot monitoring
"""

import time
import json
from datetime import datetime
from typing import Dict, List


class PerformanceDashboard:
    """Track and display trading bot performance metrics"""

    def __init__(self):
        self.metrics = {
            'start_time': datetime.now(),
            'total_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'buy_orders': 0,
            'sell_orders': 0,
            'total_volume': 0.0,
            'pnl': 0.0,
            'max_balance': 2000.0,
            'min_balance': 2000.0,
            'current_balance': 2000.0,
            'price_history': [],
            'balance_history': [],
            'trade_history': []
        }

    def record_trade(self, trade_type: str, price: float, quantity: float, pnl: float = 0.0):
        """Record a completed trade"""
        self.metrics['total_trades'] += 1
        self.metrics['total_volume'] += price * quantity

        if trade_type == 'BUY':
            self.metrics['buy_orders'] += 1
        else:
            self.metrics['sell_orders'] += 1

        self.metrics['pnl'] += pnl

        # Update balance tracking
        self.metrics['current_balance'] += pnl
        self.metrics['max_balance'] = max(self.metrics['max_balance'], self.metrics['current_balance'])
        self.metrics['min_balance'] = min(self.metrics['min_balance'], self.metrics['current_balance'])

        # Record trade
        trade = {
            'time': datetime.now().isoformat(),
            'type': trade_type,
            'price': price,
            'quantity': quantity,
            'pnl': pnl
        }
        self.metrics['trade_history'].append(trade)

    def update_balance(self, price: float, usdt_balance: float, usdc_balance: float):
        """Update current balance and price history"""
        total_value = usdt_balance + (usdc_balance * price)
        self.metrics['current_balance'] = total_value
        self.metrics['price_history'].append(price)
        self.metrics['balance_history'].append(total_value)

        # Keep history manageable
        if len(self.metrics['price_history']) > 100:
            self.metrics['price_history'].pop(0)
            self.metrics['balance_history'].pop(0)

    def get_metrics(self) -> Dict:
        """Get current performance metrics"""
        runtime = datetime.now() - self.metrics['start_time']
        success_rate = 0
        if self.metrics['total_trades'] > 0:
            success_rate = (self.metrics['successful_trades'] / self.metrics['total_trades']) * 100

        max_drawdown = 0
        if self.metrics['max_balance'] > 0:
            max_drawdown = (self.metrics['max_balance'] - self.metrics['min_balance']) / self.metrics['max_balance']

        return {
            'runtime_seconds': runtime.total_seconds(),
            'total_trades': self.metrics['total_trades'],
            'successful_trades': self.metrics['successful_trades'],
            'failed_trades': self.metrics['failed_trades'],
            'success_rate': success_rate,
            'buy_orders': self.metrics['buy_orders'],
            'sell_orders': self.metrics['sell_orders'],
            'total_volume': self.metrics['total_volume'],
            'pnl': self.metrics['pnl'],
            'pnl_percent': (self.metrics['pnl'] / 2000.0) * 100,
            'max_drawdown': max_drawdown,
            'current_balance': self.metrics['current_balance'],
            'current_price': self.metrics['price_history'][-1] if self.metrics['price_history'] else 0.0
        }

    def display_dashboard(self):
        """Display current performance dashboard"""
        metrics = self.get_metrics()
        runtime_hours = metrics['runtime_seconds'] / 3600

        print()
        print("="*70)
        print(" " * 15 + "TRADING BOT PERFORMANCE DASHBOARD")
        print("="*70)
        print(f"📊 Runtime: {runtime_hours:.2f} hours")
        print(f"💰 Current Balance: ${metrics['current_balance']:.2f}")
        print(f"📈 Net P&L: ${metrics['pnl']:.2f} ({metrics['pnl_percent']:+.2f}%)")
        print(f"📊 Total Volume: ${metrics['total_volume']:.2f}")
        print()
        print("📋 Trading Statistics:")
        print(f"   Total Trades: {metrics['total_trades']}")
        print(f"   Buy Orders: {metrics['buy_orders']}")
        print(f"   Sell Orders: {metrics['sell_orders']}")
        print(f"   Success Rate: {metrics['success_rate']:.1f}%")
        print()
        print("⚠️ Risk Metrics:")
        print(f"   Max Drawdown: {metrics['max_drawdown']*100:.2f}%")
        print(f"   Current Price: ${metrics['current_price']:.4f}")
        print("="*70)

    def save_report(self, filename: str = 'performance_report.json'):
        """Save performance report to JSON file"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.get_metrics(),
            'trade_history': self.metrics['trade_history'][-20:]  # Last 20 trades
        }

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Performance report saved to {filename}")

    def print_recent_trades(self, limit: int = 10):
        """Print recent trading activity"""
        if not self.metrics['trade_history']:
            print("No trades recorded yet.")
            return

        print()
        print("📜 RECENT TRADES")
        print("-"*70)
        print(f"{'Time':<20} {'Type':<6} {'Price':<10} {'Quantity':<12} {'P&L':<10}")
        print("-"*70)

        recent_trades = self.metrics['trade_history'][-limit:]
        for trade in reversed(recent_trades):
            time_str = datetime.fromisoformat(trade['time']).strftime('%H:%M:%S')
            pnl_str = f"${trade['pnl']:.4f}" if trade['pnl'] != 0 else "-"
            print(f"{time_str:<20} {trade['type']:<6} ${trade['price']:.4f}   {trade['quantity']:<12.4f} {pnl_str:<10}")

        print("-"*70)


if __name__ == "__main__":
    # Test the dashboard
    dashboard = PerformanceDashboard()

    # Simulate some trades
    dashboard.record_trade('BUY', 1.0000, 10.0, -0.05)
    time.sleep(0.5)
    dashboard.record_trade('SELL', 1.0002, 10.0, 0.08)
    time.sleep(0.5)
    dashboard.record_trade('BUY', 0.9999, 15.0, -0.12)
    time.sleep(0.5)
    dashboard.record_trade('SELL', 1.0001, 15.0, 0.15)

    dashboard.update_balance(1.0001, 1000.05, 1000.0)

    # Display results
    dashboard.display_dashboard()
    dashboard.print_recent_trades()
    dashboard.save_report()

    print()
    print("Dashboard test complete!")