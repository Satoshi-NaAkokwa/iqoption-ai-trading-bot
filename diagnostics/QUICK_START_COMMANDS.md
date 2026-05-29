# 🚀 Quick Start Commands

## One-Line System Status

```bash
cd ~/.openclaw/workspace/diagnostics && ./quick-status.sh
```

Output example:
```
OpenClaw Quick Status: active | Memory: 16.4% | CPU: 12.3% | API: 200 | Errors: 0
```

## Essential Commands

### Quick Check (30 seconds)
```bash
cd ~/.openclaw/workspace/diagnostics && ./health-check.sh
```

### Interactive Menu (1 minute)
```bash
cd ~/.openclaw/workspace/diagnostics && ./menu.sh
```

### Generate Report (2 minutes)
```bash
cd ~/.openclaw/workspace/diagnostics && ./generate-report.sh
```

### View Status Dashboard (ongoing)
```bash
cd ~/.openclaw/workspace/diagnostics && ./status-dashboard.sh
```

## Daily Routine (Morning)

```bash
cd ~/.openclaw/workspace/diagnostics && ./health-check.sh
```

## Weekly Routine (Monday)

```bash
cd ~/.openclaw/workspace/diagnostics && ./generate-report.sh
```

## Monthly Routine (First of month)

```bash
openclaw update
```

## Troubleshooting

### High Memory
```bash
cd ~/.openclaw/workspace/diagnostics && ./quick-fix-lite.sh
```

### API Issues
```bash
cd ~/.openclaw/workspace/diagnostics && ./llm-provider-check.sh
```

### Gateway Issues
```bash
systemctl status openclaw-gateway
systemctl restart openclaw-gateway
```

### View Recent Errors
```bash
journalctl -u openclaw-gateway --since "1 hour ago" | grep -i error
```

## Getting Started

```bash
cd ~/.openclaw/workspace/diagnostics
./GETTING_STARTED.sh
```

## Support

```bash
cd ~/.openclaw/workspace/diagnostics
./menu.sh
```

Or visit:
- https://docs.openclaw.ai
- https://discord.com/invite/clawd

---

*System Health: 99/100 - EXCELLENT*