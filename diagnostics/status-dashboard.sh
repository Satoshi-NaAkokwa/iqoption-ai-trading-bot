#!/bin/bash
# Real-time status dashboard

clear

while true; do
    clear
    
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║         OpenClaw Real-Time Status Dashboard                    ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    
    echo "📊 System Resources"
    echo "────────────────────────────────────────────────────────────────"
    
    # Memory
    MEM=$(free | awk '/Mem/{printf "%.1f%% (%.1fGB available)", $3/$2 * 100.0, $7/1024}')
    echo "  Memory:     $MEM"
    
    # CPU
    CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    echo "  CPU:        $CPU%"
    
    # Disk
    DISK=$(df -h / | awk 'NR==2{printf "%s used, %s free", $5, $4}')
    echo "  Disk:       $DISK"
    
    # Load
    LOAD=$(uptime | awk -F'load average:' '{print $2}')
    echo "  Load:       $LOAD"
    
    echo ""
    echo "🚀 Gateway Status"
    echo "────────────────────────────────────────────────────────────────"
    
    # Gateway status
    GATEWAY=$(systemctl is-active openclaw-gateway 2>/dev/null || echo "unknown")
    echo "  Status:     $GATEWAY"
    
    # Gateway process
    GW_PID=$(pgrep -f openclaw-gateway | head -1)
    if [ -n "$GW_PID" ]; then
        GW_MEM=$(ps -p "$GW_PID" -o rss= | awk '{printf "%.1fMB", $1/1024}')
        echo "  PID:        $GW_PID"
        echo "  Memory:     $GW_MEM"
    fi
    
    # Sessions
    SESSIONS=$(ls ~/.openclaw/agents/main/sessions/ 2>/dev/null | wc -l)
    echo "  Sessions:   $SESSIONS"
    
    echo ""
    echo "🔌 Network"
    echo "────────────────────────────────────────────────────────────────"
    
    # LLM API health
    API_STATUS=$(curl -s http://10.1.160.84:9527/v1/models 2>/dev/null | grep -o '"success":true' || echo "failed")
    if [ "$API_STATUS" = '"success":true' ]; then
        echo "  LLM API:    ✅ Connected"
    else
        echo "  LLM API:    ❌ Failed"
    fi
    
    # Recent errors
    ERRORS=$(journalctl -u openclaw-gateway --since "5 minutes ago" 2>/dev/null | grep -i error | wc -l)
    echo "  Errors:     $ERRORS (last 5min)"
    
    echo ""
    echo "📁 Background Processes"
    echo "────────────────────────────────────────────────────────────────"
    
    # Trading monitors
    MONITORS=$(ps aux | grep -E '(auto-monitor|continuous-trading-monitor)' | grep -v grep | wc -l)
    echo "  Monitors:   $MONITORS running"
    
    if [ "$MONITORS" -gt 0 ]; then
        ps aux | grep -E '(auto-monitor|continuous-trading-monitor)' | grep -v grep | while read line; do
            echo "    $line" | awk '{print "      PID:", $2, "CPU:", $3"%", "MEM:", $4"%", "CMD:", $11, $12}'
        done
    fi
    
    echo ""
    echo "📋 Quick Actions"
    echo "────────────────────────────────────────────────────────────────"
    echo "  [1] Run health check"
    echo "  [2] View logs (live)"
    echo "  [3] Test LLM API"
    echo "  [4] Generate report"
    echo "  [q] Quit"
    echo ""
    
    echo "Last updated: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo "Press any key to refresh, [q] to quit..."
    
    read -t 10 -n 1 key
    if [ "$key" = "q" ]; then
        break
    fi
done

echo ""
echo "Dashboard closed."
echo ""
echo "Quick access to tools:"
echo "  cd ~/.openclaw/workspace/diagnostics"
echo "  ./menu.sh"
