# OpenClaw Diagnostic Report

**Generated:** $(date)
**System:** vm-axvC6iBU
**OpenClaw Version:** $(openclaw --version 2>/dev/null || echo "N/A")

---

## 1. System Overview

### Host Information
```
Linux vm-axvC6iBU 5.15.0-174-generic #184-Ubuntu SMP Fri Mar 13 18:41:50 UTC 2026 x86_64 x86_64 x86_64 GNU/Linux
```

### Uptime
```
 08:53:09 up 1 day,  1:12,  0 users,  load average: 0.68, 0.51, 0.28
```

### CPU Info
```
CPU op-mode(s):                          32-bit, 64-bit
CPU(s):                                  4
Model name:                              Intel(R) Xeon(R) Platinum
CPU family:                              6
Thread(s) per core:                      2
Core(s) per socket:                      2
```

### Memory Usage
```
               total        used        free      shared  buff/cache   available
Mem:           7.1Gi       1.3Gi       2.7Gi       2.0Mi       3.0Gi       5.5Gi
Swap:             0B          0B          0B
```

### Disk Usage
```
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           727M  1.1M  726M   1% /run
/dev/vda3        40G   11G   28G  28% /
tmpfs           3.6G     0  3.6G   0% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
/dev/vda2       197M  6.1M  191M   4% /boot/efi
/dev/vdb         98G  2.8G   91G   4% /home/openclaw
```

## 2. Gateway Status

### Service Status
```
● openclaw-gateway.service - OpenClaw Gateway
     Loaded: loaded (/etc/systemd/system/openclaw-gateway.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-05-20 07:40:37 +08; 1 day 1h ago
   Main PID: 1329 (openclaw)
      Tasks: 44 (limit: 8631)
     Memory: 2.3G
        CPU: 4h 43min 55.000s
     CGroup: /system.slice/openclaw-gateway.service
             ├─ 1329 openclaw "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" ""
             ├─ 1342 openclaw-gateway "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" ""
             ├─ 7860 node auto-monitor.js
             ├─12736 node continuous-trading-monitor.js
             ├─28318 /bin/bash ./generate-report.sh
             ├─28331 systemctl status openclaw-gateway --no-pager
             └─28332 head -15
```

### Gateway Process
```
openclaw    1342 18.4 14.4 33718716 1074564 ?    Sl   May20 279:49 openclaw-gateway
```

## 3. Network Status

### LLM API Endpoint
```
Base URL: http://10.1.160.84:9527/v1
Health Check:
{"status":"ok"}
```

### API Models Available
```
{"data":[{"id":"claude-sonnet-4_6","object":"model","created":1626777600,"owned_by":"custom","supported_endpoint_types":["openai"]},{"id":"glm-5","object":"model","created":1626777600,"owned_by":"zhipu_4v","supported_endpoint_types":["openai"]},{"id":"glm-4.7","object":"model","created":1626777600,"owned_by":"zhipu_4v","supported_endpoint_types":["openai"]},{"id":"claude-sonnet-4-6","object":"model","created":1626777600,"owned_by":"vertex-ai","supported_endpoint_types":["openai"]}],"object":"list","success":true}```

## 4. Recent Errors (Last 30 minutes)
```
May 21 08:47:29 vm-axvC6iBU openclaw[1342]: 2026-05-21T08:47:29.755+08:00 [agent/embedded] [context-overflow-diag] sessionKey=agent:main:main provider=occ/glm-4.7 source=assistantError messages=115 sessionFile=/home/openclaw/.openclaw/agents/main/sessions/570a5976-fe59-44a9-afae-85df70621c50.jsonl diagId=ovf-mperu47s-HgGvCw compactionAttempts=0 observedTokens=unknown error=Context overflow: estimated context size exceeds safe threshold during tool loop.
```

## 5. Session Information

### Session Count
```
0
```

### Session Sizes
```
No sessions directory
```

## 6. Background Processes

### Trading Monitors
```
openclaw    7860  0.0  1.1 1474120 86724 ?       Ssl  May20   0:28 node auto-monitor.js
openclaw   12736  0.0  1.1 1472264 84492 ?       Ssl  01:50   0:10 node continuous-trading-monitor.js
```

## 7. Log Files

### OpenClaw Logs
```
-rw-r--r-- 1 openclaw openclaw 612K May 20 23:48 /tmp/openclaw-1000/openclaw-2026-05-20.log
-rw-r--r-- 1 openclaw openclaw 437K May 21 08:52 /tmp/openclaw-1000/openclaw-2026-05-21.log
```

### Total OpenClaw Directory Size
```
1.9G	/home/openclaw/.openclaw
```

## 8. Recommendations

See `SYSTEM_VERDICT.md` for detailed optimization plan.

### Quick Actions

1. **Check API Key:** Ensure `API_HUB_KEY` is valid
2. **Clean Sessions:** Run `./quick-fix.sh`
3. **Review Monitors:** Check if trading monitors are needed
4. **Monitor Logs:** Run `./log-monitor.sh`

### Long-term Actions

1. **Set up log rotation:** (configured by quick-fix.sh)
2. **Configure monitoring:** Add health checks to crontab
3. **Review configuration:** Apply config patches after testing
4. **Update OpenClaw:** `openclaw update`

---

**Report Generation:** Complete
**Next Steps:** Review recommendations and implement fixes

For more details, see: `SYSTEM_VERDICT.md`

**Diagnostic Scripts:**
- `./health-check.sh` - Quick health status
- `./log-monitor.sh` - Live log monitoring
- `./llm-provider-check.sh` - API connectivity test
- `./quick-fix.sh` - Automated fixes (with prompts)
