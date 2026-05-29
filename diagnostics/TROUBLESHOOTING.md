# 🔧 OpenClaw Troubleshooting Guide

## Common Issues and Solutions

### Issue: High Memory Usage (>1GB)

**Symptoms:**
- Gateway using excessive memory
- System slowdowns
- OOM warnings

**Diagnosis:**
```bash
# Check memory
free -h

# Check gateway memory
ps aux | grep openclaw-gateway

# Check all processes
ps aux | sort -rk 4 | head -10
```

**Solutions:**
1. Stop background monitors:
```bash
pkill -f "auto-monitor.js"
pkill -f "trading-monitor.js"
```

2. Restart gateway:
```bash
systemctl restart openclaw-gateway
```

3. Check for memory leaks:
```bash
cd ~/.openclaw/workspace/diagnostics
./generate-report.sh
```

---

### Issue: High CPU Usage (>50%)

**Symptoms:**
- System sluggish
- High CPU load average
- Slow responses

**Diagnosis:**
```bash
# Check CPU
top -bn1 | grep "Cpu(s)"

# Check processes
ps aux | sort -rk 3 | head -10

# Check load average
uptime
```

**Solutions:**
1. Identify heavy processes:
```bash
ps aux | sort -rk 3 | head -5
```

2. Stop if necessary:
```bash
# Identify PID, then stop
kill -9 <PID>
```

3. Restart gateway:
```bash
systemctl restart openclaw-gateway
```

---

### Issue: LLM API Errors

**Symptoms:**
- API timeouts
- 401/403 errors
- Rate limit errors

**Diagnosis:**
```bash
# Test API
cd ~/.openclaw/workspace/diagnostics
./llm-provider-check.sh

# Check logs
journalctl -u openclaw-gateway --since "1 hour ago" | grep -i api

# Test connectivity
curl http://10.1.160.84:9527/v1/models
```

**Solutions:**
1. Verify API key:
```bash
echo $API_HUB_KEY
```

2. Check network:
```bash
ping 10.1.160.84  # Note: May be blocked
curl http://10.1.160.84:9527/v1/models
```

3. Restart gateway:
```bash
systemctl restart openclaw-gateway
```

---

### Issue: Gateway Not Starting

**Symptoms:**
- Gateway service failed
- Cannot start service
- Service crashes immediately

**Diagnosis:**
```bash
# Check status
systemctl status openclaw-gateway

# Check logs
journalctl -u openclaw-gateway -n 100

# Check for errors
journalctl -u openclaw-gateway --since "5 minutes ago" | grep -i error
```

**Solutions:**
1. Check configuration:
```bash
cat ~/.openclaw/openclaw.json
```

2. Verify dependencies:
```bash
openclau --version
node --version
```

3. Reset configuration:
```bash
# Backup first
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup

# Then restart
systemctl restart openclaw-gateway
```

---

### Issue: Session Corruption

**Symptoms:**
- Gateway constantly rewriting sessions
- Session errors in logs
- Loss of session data

**Diagnosis:**
```bash
# Check sessions
ls -lh ~/.openclaw/agents/main/sessions/

# Check for empty files
find ~/.openclaw/agents/main/sessions -name "*.jsonl" -size 0

# Check logs for corruption
journalctl -u openclaw-gateway | grep -i corrupt
```

**Solutions:**
1. Backup sessions:
```bash
cp -r ~/.openclaw/agents/main/sessions ~/.openclaw/agents/main/sessions.backup.$(date +%Y%m%d)
```

2. Clean corrupted sessions:
```bash
find ~/.openclaw/agents/main/sessions -name "*.jsonl" -size 0 -delete
```

3. Restart gateway:
```bash
systemctl restart openclaw-gateway
```

---

### Issue: Network Connectivity Problems

**Symptoms:**
- Cannot reach LLM API
- Network timeouts
- Connection refused

**Diagnosis:**
```bash
# Test HTTP (working)
curl http://10.1.160.84:9527/v1/models

# Test ICMP (may be blocked)
ping 10.1.160.84

# Check DNS
nslookup 10.1.160.84

# Check firewall
sudo iptables -L | grep 10.1.160.84
```

**Solutions:**
1. Note: ICMP blocked is expected (security measure)
2. HTTP should work fine
3. If HTTP fails, check firewall rules

---

### Issue: Log Files Too Large

**Symptoms:**
- Disk space filling up
- Large log files
- Slow log reading

**Diagnosis:**
```bash
# Check log sizes
ls -lh /tmp/openclaw-1000/*.log

# Check total size
du -sh /tmp/openclaw-1000/
```

**Solutions:**
1. Manual log rotation:
```bash
# Archive old logs
cd /tmp/openclaw-1000
mv openclaw-2026-05-20.log openclaw-2026-05-20.log.archived

# Compress
gzip openclaw-2026-05-20.log.archived
```

2. Automated rotation:
```bash
# Delete logs older than 7 days
find /tmp/openclaw-1000/*.log -mtime +7 -delete
```

3. Set up rotation:
```bash
cd ~/.openclaw/workspace/diagnostics
./setup-monitoring.sh
```

---

## Quick Troubleshooting Checklist

### First Steps
1. Run health check:
```bash
cd ~/.openclaw/workspace/diagnostics
./health-check.sh
```

2. Check logs:
```bash
journalctl -u openclaw-gateway -n 50
```

3. Generate report:
```bash
./generate-report.sh
```

### Based on Symptoms

| Symptom | First Action |
|---------|-------------|
| High memory | `ps aux | sort -rk 4 | head -10` |
| High CPU | `ps aux | sort -rk 3 | head -10` |
| API errors | `./llm-provider-check.sh` |
| Gateway down | `systemctl status openclaw-gateway` |
| Network issues | `curl http://10.1.160.84:9527/v1/models` |
| Session issues | `ls -lh ~/.openclaw/agents/main/sessions/` |
| Disk full | `df -h` and `du -sh /tmp/openclaw-1000/` |

## Advanced Troubleshooting

### Enable Debug Logging

1. Edit config:
```bash
nano ~/.openclaw/openclaw.json
```

2. Add debug level:
```json
{
  "logging": {
    "level": "debug"
  }
}
```

3. Restart gateway:
```bash
systemctl restart openclaw-gateway
```

### Monitor Resources Real-Time

```bash
# CPU and memory
top

# Disk I/O
iostat -x 1

# Network
iftop

# Combined
htop
```

### Capture System State

```bash
# Generate full report
cd ~/.openclaw/workspace/diagnostics
./generate-report.sh

# Save system info
systeminfo > system-info.txt

# Save process list
ps aux > processes.txt

# Save network status
netstat -tuln > network.txt
```

## Recovery Procedures

### Full System Reset

⚠️ **WARNING: This will reset all settings**

1. Stop gateway:
```bash
systemctl stop openclaw-gateway
```

2. Backup configuration:
```bash
cp -r ~/.openclaw ~/.openclaw.backup.$(date +%Y%m%d)
```

3. Remove corrupted data:
```bash
rm -rf ~/.openclaw/agents/main/sessions/*
```

4. Start gateway:
```bash
systemctl start openclaw-gateway
```

### Restore from Backup

```bash
# Stop gateway
systemctl stop openclaw-gateway

# Restore from backup
cp -r ~/.openclaw.backup.YYYYMMDD/* ~/.openclaw/

# Start gateway
systemctl start openclaw-gateway

# Verify
systemctl status openclaw-gateway
```

## Getting Help

### Self-Service

1. Run diagnostics:
```bash
cd ~/.openclaw/workspace/diagnostics
./menu.sh
```

2. Check documentation:
```bash
cat README.md
cat SYSTEM_VERDICT.md
cat ARCHITECTURE_ANALYSIS.md
```

3. Generate report:
```bash
./generate-report.sh
```

### Community Support

- Discord: https://discord.com/invite/clawd
- GitHub: https://github.com/openclaw/openclaw/issues
- Docs: https://docs.openclaw.ai

### Escalation Path

1. Self-service (5 min)
2. Community support (1 hour)
3. Official support (24 hours)

---

**Last Updated:** 2026-05-21
**Version:** 1.0
**Status:** Production Ready
