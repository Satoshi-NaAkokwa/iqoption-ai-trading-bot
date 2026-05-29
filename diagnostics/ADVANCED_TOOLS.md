# Advanced Tools & Automation Guide

This guide covers the advanced diagnostic tools for automated monitoring, benchmarking, and backup management.

## 📦 Backup & Restore Utility

### Creating Backups

```bash
cd ~/.openclaw/workspace/diagnostics
./backup-restore.sh backup
```

This creates a complete backup of your OpenClaw configuration including:
- Configuration files
- Agent settings
- Session data
- Custom scripts

Backup location: `~/.openclaw-backups/openclaw-backup-YYYYMMDD_HHMMSS.tar.gz`

### Restoring Backups

```bash
cd ~/.openclaw/workspace/diagnostics
./backup-restore.sh restore openclaw-backup-20260521_100000
```

**⚠️ Warning:** This will overwrite your current configuration!

### Listing Backups

```bash
cd ~/.openclaw/workspace/diagnostics
./backup-restore.sh list
```

### Cleaning Old Backups

```bash
cd ~/.openclaw/workspace/diagnostics
./backup-restore.sh clean
```

## 📊 Performance Benchmark

### Running a Benchmark

```bash
cd ~/.openclaw/workspace/diagnostics
./performance-benchmark.sh
```

This measures:
- System metrics (memory, CPU, disk, load)
- Gateway metrics (status, memory, CPU)
- API metrics (response time, availability)
- Error metrics (error count)
- Session metrics (active sessions)
- Monitor metrics (background processes)

### Viewing Benchmark Data

Benchmarks are saved as JSON in `~/.openclaw/benchmarks/`

View specific benchmark:
```bash
cat ~/.openclaw/benchmarks/benchmark-20260521_100000.json | jq .
```

View all benchmarks:
```bash
ls -lt ~/.openclaw/benchmarks/
```

### Benchmark Output Example

```
╔════════════════════════════════════════════════════════════════╗
║         OpenClaw Performance Benchmark                        ║
╚════════════════════════════════════════════════════════════════╝

Performance Benchmark Results

Timestamp: 2026-05-21 10:30:00

System Metrics:
  Memory Usage:     16.5% (5.6Gi available)
  CPU Usage:        12.3%
  Disk Usage:       28%
  Load Average:     0.36

Gateway Metrics:
  Status:           active
  Memory:           893.0 MB
  CPU:              18.2%

API Metrics:
  Status Code:      200
  Latency:          234ms

Error Metrics:
  Errors (5min):    0

Session Metrics:
  Sessions:         0

Monitor Metrics:
  Running:          2
```

## 🚨 Automated Health Monitor

### Running the Monitor

```bash
cd ~/.openclaw/workspace/diagnostics
./health-monitor-automated.sh
```

This checks:
- Gateway status
- Memory usage (alerts if > 80%)
- CPU usage (alerts if > 90%)
- Disk usage (alerts if > 90%)
- API health
- Recent errors (alerts if > 10 in 5 min)
- Session files
- Network connectivity
- Background processes

### Configuring Alerts

Edit the script to set your email address:

```bash
ALERT_EMAIL="your-email@example.com"
ALERT_THRESHOLD_MEMORY=80
ALERT_THRESHOLD_CPU=90
ALERT_THRESHOLD_ERRORS=10
```

### Monitor Exit Codes

- `0` - No issues found
- `1` - Issues detected

This makes it suitable for cron jobs and monitoring systems.

### Example Cron Setup

Add to crontab (`crontab -e`):

```bash
# Run health monitor every 30 minutes
*/30 * * * * cd ~/.openclaw/workspace/diagnostics && ./health-monitor-automated.sh

# Run benchmark every day at midnight
0 0 * * * cd ~/.openclaw/workspace/diagnostics && ./performance-benchmark.sh

# Create backup every Sunday at 2 AM
0 2 * * 0 cd ~/.openclaw/workspace/diagnostics && ./backup-restore.sh backup
```

## 🔧 Advanced Troubleshooting

### Performance Regression Detection

1. Run benchmarks regularly
2. Compare results over time
3. Identify degrading metrics

```bash
# Run benchmark
./performance-benchmark.sh

# Compare with previous
jq -r '.system.memory_percent' ~/.openclaw/benchmarks/benchmark-*.json | tail -2 | \
  awk '{print $1 - $2}'
```

### Automated Issue Detection

Create a cron job to run the health monitor and log results:

```bash
*/30 * * * * cd ~/.openclaw/workspace/diagnostics && \
  ./health-monitor-automated.sh >> /var/log/openclaw-health.log 2>&1
```

### Scheduled Backup Rotation

```bash
# Keep last 7 backups
0 3 * * * cd ~/.openclaw/workspace/diagnostics && \
  ./backup-restore.sh backup && \
  find ~/.openclaw-backups -name "*.tar.gz" -mtime +7 -delete
```

## 📈 Integration with Monitoring Systems

### Prometheus Metrics Export

Export benchmark metrics to Prometheus:

```bash
# Create metrics endpoint
cat > /tmp/openclaw-metrics.sh << 'EOF'
#!/bin/bash
BENCHMARK=$(ls -t ~/.openclaw/benchmarks/*.json 2>/dev/null | head -1)
if [ -f "$BENCHMARK" ]; then
  echo "# HELP openclaw_memory_percent Memory usage percentage"
  echo "# TYPE openclaw_memory_percent gauge"
  echo "openclaw_memory_percent $(jq '.system.memory_percent' $BENCHMARK)"

  echo "# HELP openclaw_cpu_percent CPU usage percentage"
  echo "# TYPE openclaw_cpu_percent gauge"
  echo "openclaw_cpu_percent $(jq '.system.cpu_percent' $BENCHMARK)"

  echo "# HELP openclaw_api_latency API latency in milliseconds"
  echo "# TYPE openclaw_api_latency gauge"
  echo "openclaw_api_latency $(jq '.api.latency_ms' $BENCHMARK)"
fi
EOF

chmod +x /tmp/openclaw-metrics.sh
```

### Grafana Dashboard

Create a Grafana dashboard to visualize:
- Memory usage over time
- CPU usage over time
- API latency trends
- Error rates
- Gateway uptime

## 🔒 Security Best Practices

### Backup Encryption

Encrypt backups with GPG:

```bash
./backup-restore.sh backup
gpg --symmetric --cipher-algo AES256 ~/.openclaw-backups/openclaw-backup-*.tar.gz
rm ~/.openclaw-backups/openclaw-backup-*.tar.gz
```

### Access Control

Restrict access to diagnostic tools:

```bash
chmod 750 ~/.openclaw/workspace/diagnostics
chmod 640 ~/.openclaw/benchmarks/*.json
```

### Audit Logging

Log all backup and restore operations:

```bash
# Add to backup-restore.sh
logger -t openclaw-backup "Backup created: $BACKUP_NAME"
logger -t openclaw-backup "Backup restored: $2"
```

## 📚 Additional Resources

### Related Documentation

- `TROUBLESHOOTING.md` - Comprehensive troubleshooting guide
- `MAINTENANCE_SCHEDULE.md` - Maintenance procedures
- `QUICK_REFERENCE.md` - Quick reference card

### Official Resources

- https://docs.openclaw.ai
- https://discord.com/invite/clawd
- https://github.com/openclaw/openclaw

---

*Last updated: 2026-05-21*