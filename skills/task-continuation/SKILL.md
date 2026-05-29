# Task Continuation Skill

Persist work state across session timeouts. Use when working on long-running multi-turn tasks that may exceed idle timeout limits.

## When to Use

- Multi-hour code refactoring
- Batch processing multiple videos
- Complex multi-step tasks
- When user asks "continue from where we stopped"

## How It Works

1. **Check for pending tasks** - Read `TASK_CONTINUATION.md`
2. **Load state** - Restore variables, files, context
3. **Continue work** - Resume from last checkpoint
4. **Update state** - Save progress after each step
5. **Mark complete** - Remove task when done

## File Format

`/home/openclaw/.openclaw/workspace/TASK_CONTINUATION.md`

```markdown
# Active Tasks

## [TASK_ID] Task Name
**Status:** pending|in_progress|complete|paused
**Started:** 2024-01-01 12:00:00 GMT+8
**Last Updated:** 2024-01-01 14:30:00 GMT+8

### Description
Brief task description

### Steps Completed
- [x] Step 1 description
- [x] Step 2 description
- [ ] Step 3 description

### Current Step
**Step 3:** Description of what to do next
- File: `/path/to/file.py`
- Line: 150
- Context: "Need to add XYZ function"

### State
```json
{
  "last_operation": "created_session_filter",
  "next_asset": "GBPUSD-OTC",
  "progress": 3,
  "total": 5
}
```

### Notes
Any important notes or context

---

## [TASK_ID_2] Another Task
...
```

## Usage

### Start a Task

```python
TASK_ID = "iq_bot_v6_upgrade"  # Use a unique ID

# Write to TASK_CONTINUATION.md
```

### Check for Pending Tasks

1. Read `TASK_CONTINUATION.md`
2. Find tasks with status `pending` or `in_progress`
3. Ask user if they want to continue

### Resume a Task

1. Load the task's state
2. Restore any saved variables
3. Continue from "Current Step"
4. Update "Last Updated" timestamp
5. Mark steps as complete

### Complete a Task

Change status to `complete` and add completion notes. Archive or remove after 7 days.

## Best Practices

1. **Check after timeout:** Always read `TASK_CONTINUATION.md` after returning from a long pause
2. **Save frequently:** Update the file after each meaningful step
3. **Be descriptive:** Include file paths, line numbers, and context
4. **Clean up:** Remove completed tasks periodically
5. **One task at a time:** Focus on the oldest pending task first

## Example

**Before timeout:**
```markdown
## [BOT_V6] IQ Option Bot v6 Upgrade
**Status:** in_progress
**Last Updated:** 2024-01-28 22:00:00 GMT+8

### Steps Completed
- [x] Add session filter
- [x] Add multi-asset support
- [ ] Add news calendar filter
- [ ] YouTube channel transcription
- [ ] GitHub update

### Current Step
**Step 3:** News calendar filter
- Need to create `news_filter.py`
- Use ForexFactory API
- Add to bot initialization
```

**After timeout (on resume):**
```markdown
## [BOT_V6] IQ Option Bot v6 Upgrade
**Status:** in_progress
**Last Updated:** 2024-01-28 23:30:00 GMT+8

### Steps Completed
- [x] Add session filter
- [x] Add multi-asset support
- [x] Add news calendar filter
- [ ] YouTube channel transcription
- [ ] GitHub update

### Current Step
**Step 4:** YouTube channel transcription
- Channel: https://youtube.com/@katietutorialsofficial
- Sub-agent spawned, waiting for results
- Session ID: abc123
```

## Auto-Resume Pattern

When a session resumes from timeout, automatically check:

```python
# Check for pending tasks
task_file = "/home/openclaw/.openclaw/workspace/TASK_CONTINUATION.md"
if os.path.exists(task_file):
    content = read(task_file)
    # Find in_progress tasks
    # Ask user: "Found 1 pending task: [TASK_ID]. Resume?"
```