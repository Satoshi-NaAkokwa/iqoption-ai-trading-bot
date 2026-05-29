# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## OpenClaw Gateway

The openclaw gateway runs as a systemd service on this machine. Do NOT use `openclaw gateway restart`.

To restart the gateway:

```bash
sudo systemctl restart openclaw-gateway
```

To check gateway status:

```bash
sudo systemctl status openclaw-gateway
```

### Custom Environment Variables

To add or override env vars for the gateway (custom MCP API keys, etc.), edit
`/home/openclaw/.openclaw-env` (you own this file, mode 600):

```bash
echo 'MY_API_KEY=xxx' >> /home/openclaw/.openclaw-env
sudo systemctl restart openclaw-gateway
```

This file is loaded AFTER the system-managed `/etc/clawcloud/env`, so values
here override anything pushed from the cloud. It is NEVER touched by
subscription/tier changes — entries here survive Free ↔ Plus ↔ Pro upgrades.

Do NOT put custom env in `/etc/clawcloud/env` — that file is owned by the
control plane and gets full-replaced on tier changes.

---

Add whatever helps you do your job. This is your cheat sheet.
