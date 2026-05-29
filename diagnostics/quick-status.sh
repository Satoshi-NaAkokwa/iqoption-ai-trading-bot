#!/bin/bash
# QUICK DIAGNOSTIC SUMMARY - One-line system status

echo "OpenClaw Quick Status: $(systemctl is-active openclaw-gateway 2>/dev/null || echo 'unknown') | Memory: $(free | awk 'NR==2{printf "%.1f%%", $3/$2*100}') | CPU: $(top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1)% | API: $(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 2 https://api.openai.com/v1/models 2>/dev/null || echo '000') | Errors: $(journalctl -u openclaw-gateway --since '5 minutes ago' 2>/dev/null | grep -i error | wc -l)"