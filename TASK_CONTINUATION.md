# Active Tasks

## [IQ_BOT_V6] IQ Option Bot v6 Upgrade
**Status:** pending
**Started:** 2026-05-28 22:57 GMT+8
**Last Updated:** 2026-05-28 23:30 GMT+8

### Description
Upgrade IQ Option 24/7 Learning Bot v5 to v6 with:
1. Session-based trading filters
2. Multi-asset support (4 assets)
3. News calendar filter to avoid high-impact events
4. Extract strategies from YouTube channel (katietutorialsofficial)
5. Push improvements to GitHub

### Steps Completed
- [ ] Task 1: Session filter + multi-asset support
- [ ] Task 2: YouTube channel transcription (sub-agent batch)
- [ ] Task 3: News calendar filter
- [ ] Task 4: GitHub update

### Current Step
**Step 1:** Session filter + multi-asset support

**Details:**
- Modify `/home/openclaw/.openclaw/workspace/iqoption-ai-trading-bot-new/bot_247_learning_v5.py`
- Add session filter to disable trading during low-volatility hours (22:00-23:00 GMT+8)
- Add 3 more assets: GBPUSD-OTC, EURJPY-OTC, GBPJPY-OTC (currently only EURUSD-OTC)
- Adjust confidence threshold from 52% to 65%
- Save as `bot_247_learning_v6.py`

**Next Actions:**
1. Read current bot code
2. Add `SessionFilter` class
3. Update `get_available_assets()` to check 4 assets
4. Update `run_trading_cycle()` to check session filter
5. Update confidence threshold check from 0.52 to 0.65
6. Save as v6
7. Test locally
8. Update PM2 to use v6

### State
```json
{
  "current_step": 1,
  "total_steps": 4,
  "bot_file": "/home/openclaw/.openclaw/workspace/iqoption-ai-trading-bot-new/bot_247_learning_v5.py",
  "new_bot_file": "/home/openclaw/.openclaw/workspace/iqoption-ai-trading-bot-new/bot_247_learning_v6.py",
  "assets": ["EURUSD-OTC", "GBPUSD-OTC", "EURJPY-OTC", "GBPJPY-OTC"],
  "confident_threshold": 0.65,
  "session_filter": {
    "disabled_hours": [22, 23],
    "timezone": "GMT+8"
  },
  "youtube_channel": "https://youtube.com/@katietutorialsofficial",
  "github_repo": "https://github.com/Satoshi-NaAkokwa/iqoption-ai-trading-bot"
}
```

### Notes
- User wants entire YouTube channel transcribed, but this is too large for one session
- Will use sub-agent to batch process 20 videos at a time
- Need API key for news calendar (ForexFactory or TradingView)
- Remember to restart PM2 with v6 when complete

---

## [ARCHIVED] Previous completed tasks
*Keep these for reference, remove after 7 days*

- [HOURLY_REPORT] Hourly Telegram reports - **COMPLETE** (2026-05-28 21:03 GMT+8)