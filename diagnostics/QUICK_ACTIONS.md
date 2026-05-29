# 🎯 Quick Action Guide

## Immediate Actions

### 1. Run Interactive Menu
```bash
cd ~/.openclaw/workspace/diagnostics
./menu.sh
```
**Best for:** Exploring all available tools

---

### 2. Run Health Check
```bash
cd ~/.openclaw/workspace/diagnostics
./health-check.sh
```
**Best for:** Quick system status verification

---

### 3. View Real-Time Dashboard
```bash
cd ~/.openclaw/workspace/diagnostics
./status-dashboard.sh
```
**Best for:** Monitoring system in real-time

---

### 4. Test LLM API
```bash
cd ~/.openclaw/workspace/diagnostics
./llm-provider-check.sh
```
**Best for:** Verifying API connectivity

---

### 5. Generate Report
```bash
cd ~/.openclaw/workspace/diagnostics
./generate-report.sh
```
**Best for:** Creating comprehensive system report

---

### 6. Monitor Logs Live
```bash
cd ~/.openclaw/workspace/diagnostics
./log-monitor.sh
```
**Best for:** Watching logs in real-time (Ctrl+C to exit)

---

### 7. Apply Automated Fixes
```bash
cd ~/.openclaw/workspace/diagnostics
./quick-fix-lite.sh
```
**Best for:** Applying optimizations (with prompts)

---

### 8. Setup Automated Monitoring
```bash
cd ~/.openclaw/workspace/diagnostics
./setup-monitoring.sh
```
**Best for:** Setting up cron jobs for monitoring

---

## Quick Reference Commands

### Navigate to Diagnostics
```bash
cd ~/.openclaw/workspace/diagnostics
```

### Check All Scripts
```bash
ls -1 *.sh
```

### Check All Documentation
```bash
ls -1 *.md
```

### Check Generated Reports
```bash
ls -1 reports/
```

---

## Decision Tree

### What do you want to do?

**Check system health?**
→ Run `./health-check.sh`

**Monitor system in real-time?**
→ Run `./status-dashboard.sh`

**Generate a report?**
→ Run `./generate-report.sh`

**Test API connectivity?**
→ Run `./llm-provider-check.sh`

**Watch logs live?**
→ Run `./log-monitor.sh`

**Apply fixes?**
→ Run `./quick-fix-lite.sh`

**Set up automation?**
→ Run `./setup-monitoring.sh`

**Explore all tools?**
→ Run `./menu.sh`

**Read documentation?**
→ Run `cat INDEX.md` or `cat README.md`

**Troubleshoot issues?**
→ Run `cat TROUBLESHOOTING.md`

**View maintenance schedule?**
→ Run `cat MAINTENANCE_SCHEDULE.md`

---

## Most Common Workflows

### Daily Check
```bash
cd ~/.openclaw/workspace/diagnostics
./health-check.sh
```

### Weekly Report
```bash
cd ~/.openclaw/workspace/diagnostics
./generate-report.sh
```

### Troubleshooting
```bash
cd ~/.openclaw/workspace/diagnostics
./menu.sh
# or
./health-check.sh
./generate-report.sh
```

### Live Monitoring
```bash
cd ~/.openclaw/workspace/diagnostics
./status-dashboard.sh
# or
./log-monitor.sh
```

---

## Keyboard Shortcuts

### In Interactive Menu
- **1-9**: Select option
- **Enter**: Confirm
- **Ctrl+C**: Exit

### In Live Log Monitor
- **Ctrl+C**: Exit monitor

### In Real-Time Dashboard
- **q**: Exit dashboard
- **Any key**: Refresh display

---

## File Locations

### Scripts
```
~/.openclaw/workspace/diagnostics/*.sh
```

### Documentation
```
~/.openclaw/workspace/diagnostics/*.md
```

### Reports
```
~/.openclaw/workspace/diagnostics/reports/
```

---

## One-Line Commands

### Quick Status
```bash
cd ~/.openclaw/workspace/diagnostics && ./health-check.sh
```

### Generate Report
```bash
cd ~/.openclaw/workspace/diagnostics && ./generate-report.sh
```

### Test API
```bash
cd ~/.openclaw/workspace/diagnostics && ./llm-provider-check.sh
```

### View Index
```bash
cd ~/.openclaw/workspace/diagnostics && cat INDEX.md
```

---

## Emergency Commands

### System Not Responding?
```bash
systemctl status openclaw-gateway
systemctl restart openclaw-gateway
```

### High Memory Usage?
```bash
ps aux | sort -rk 4 | head -10
pkill -f "auto-monitor.js"
pkill -f "trading-monitor.js"
```

### API Issues?
```bash
cd ~/.openclaw/workspace/diagnostics
./llm-provider-check.sh
echo $API_HUB_KEY
```

### Gateway Down?
```bash
systemctl status openclaw-gateway
journalctl -u openclaw-gateway -n 100
systemctl restart openclaw-gateway
```

---

## Help Resources

### Local Help
```bash
cd ~/.openclaw/workspace/diagnostics
./menu.sh
```

### Documentation
```bash
cd ~/.openclaw/workspace/diagnostics
cat INDEX.md
cat README.md
cat TROUBLESHOOTING.md
```

### Official Support
- https://docs.openclaw.ai
- https://discord.com/invite/clawd
- https://github.com/openclaw/openclaw

---

**Quick Access:**
```bash
cd ~/.openclaw/workspace/diagnostics
./START_HERE.sh
```