# Claude Code Log Rotation Guide

**Automated log rotation and aging strategy for `.claude/logs/` directory**

---

## Overview

This guide documents the log rotation system for Claude Code logs in `.claude/logs/`. The system prevents indefinite log accumulation while preserving important debugging information.

### Current Logging Setup

**Size-Based Rotation** (existing):
- Configured in `.claude/tools/logging/config.py`
- Uses Python's `RotatingFileHandler`
- Max file size: 10MB
- Backup count: 5 files
- Files: `claude.log`, `claude.log.1` through `claude.log.5`

**Time-Based Rotation** (new):
- Configured via `.claude/tools/logging/rotation.py`
- Complements size-based rotation with age-based cleanup
- Prevents unlimited accumulation of old logs

---

## Log Files Managed

### 1. Main Logs (`claude.log.*`)

**Location:** `.claude/logs/claude.log` and `.claude/logs/claude.log.X`

**Contents:**
- Hook executions (SessionStart, SessionEnd, PreToolUse, etc.)
- Tool operations (validation, scripts, utilities)
- Maintenance tasks (scheduled cleanup, insights)
- Agent operations (tracking, optimization)
- Headless Claude executions

**Size:** Typically 2-10MB per file (rotates at 10MB)

**Rotation Strategy:**
- **Size-based:** Automatic rotation at 10MB (via `RotatingFileHandler`)
- **Age-based:** Keep for 14 days, then archive/delete
- **Archive:** Compressed to `.claude/logs/archived/` before deletion

### 2. Agent Usage Logs (`agent_usage/*.jsonl`)

**Location:** `.claude/logs/agent_usage/session_*.jsonl`

**Contents:**
- Per-session agent delegation logs
- Agent invocations, parameters, results
- Session-specific tracking data

**Size:** Typically 4KB per session (small JSONL files)

**Count:** ~190 files currently (one per session)

**Rotation Strategy:**
- **Age-based:** Keep for 30 days, then archive/delete
- **Archive:** Compressed to `.claude/logs/agent_usage/archived/`

**Analysis:** 76 files are currently older than 7 days (eligible for earlier cleanup if needed)

---

## Rotation Configuration

### Default Settings

```python
LogRotationConfig(
    main_log_retention_days=14,      # Main logs: 2 weeks
    agent_log_retention_days=30,      # Agent logs: 1 month
    archive_before_delete=True,       # Always archive (compress)
    archive_dir="archived",           # Archive subdirectory name
    dry_run=False                     # False = actually rotate
)
```

### Configuration Options

**Main Log Retention** (`main_log_retention_days`):
- Default: 14 days
- Recommended: 7-30 days
- Reasoning: Debugging typically needs recent logs only

**Agent Log Retention** (`agent_log_retention_days`):
- Default: 30 days
- Recommended: 14-60 days
- Reasoning: Historical analysis benefits from longer retention

**Archive Before Delete** (`archive_before_delete`):
- Default: `True` (recommended)
- Archives (gzip) logs before deletion
- Compression ratio: ~10:1 for text logs
- Archive location: `.claude/logs/archived/` and `.claude/logs/agent_usage/archived/`

**Dry Run** (`dry_run`):
- Default: `True` when run manually
- Set to `False` for actual rotation
- SessionEnd hook uses `dry_run=False`

---

## Usage

### Automatic Rotation (SessionEnd Hook)

**Configured in:** `.claude/settings.json` → `SessionEnd` hook

**Triggers:** When Claude Code session ends

**Behavior:**
1. Checks for old files (>14 days for main, >30 days for agent)
2. If found, rotates logs with conservative defaults
3. Archives before deletion (compressed)
4. Logs summary to `claude.log`

**Configuration:**
```json
{
  "hooks": {
    "SessionEnd": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session_end/rotate_logs.py",
            "timeout": 10000
          }
        ]
      }
    ]
  }
}
```

**Note:** SessionEnd hooks run when sessions end normally (not on interrupts/crashes).

### Manual Rotation

#### Dry Run (Preview Only)

```bash
# See what would be rotated (no changes)
python .claude/tools/logging/rotation.py
```

**Output:**
```
============================================================
DRY RUN MODE - No changes will be made
============================================================

Claude Code Log Rotation Report
============================================================

Log Directory: /Users/.../your_project/.claude/logs
Dry Run: Yes (no changes made)

Configuration:
  Main log retention: 14 days
  Agent log retention: 30 days
  Archive before delete: True

Main Logs (claude.log.*):
  Processed: 1
  Deleted: 0
  Archived: 0

Agent Logs (agent_usage/*.jsonl):
  Processed: 190
  Deleted: 0
  Archived: 0

Space:
  Freed: 0.0 B
  Archived: 0.0 B
============================================================
```

#### Execute Rotation

```bash
# Actually rotate logs
python .claude/tools/logging/rotation.py --execute
```

#### Programmatic Usage

```python
from pathlib import Path
from .claude.tools.logging.rotation import rotate_claude_logs

# Dry run
results = rotate_claude_logs(dry_run=True)
print(results)

# Execute with custom retention
results = rotate_claude_logs(
    main_retention_days=7,      # More aggressive
    agent_retention_days=14,
    archive=True,
    dry_run=False
)

# Check results
print(f"Freed: {results['summary']['bytes_freed']} bytes")
print(f"Deleted: {results['summary']['main_logs_deleted']} main logs")
```

---

## Directory Structure

### Before Rotation

```
.claude/logs/
├── claude.log                    # 2.9MB (active)
├── claude.log.1                  # 10MB (rotated yesterday)
├── claude.log.2                  # 10MB (rotated 3 days ago)
├── claude.log.3                  # 10MB (rotated 7 days ago)
├── claude.log.4                  # 10MB (rotated 12 days ago)
├── claude.log.5                  # 10MB (rotated 16 days ago) ← Would be deleted
└── agent_usage/
    ├── session_007dd9b4-....jsonl  # 4KB (today)
    ├── session_01571588-....jsonl  # 4KB (7 days ago)
    └── ... (190 total files)
```

### After Rotation

```
.claude/logs/
├── claude.log                    # 2.9MB (active)
├── claude.log.1                  # 10MB (rotated yesterday)
├── claude.log.2                  # 10MB (rotated 3 days ago)
├── claude.log.3                  # 10MB (rotated 7 days ago)
├── claude.log.4                  # 10MB (rotated 12 days ago)
├── archived/
│   └── claude.log.5_20251023.gz  # 1MB (compressed, 16 days old)
└── agent_usage/
    ├── session_007dd9b4-....jsonl  # 4KB (today)
    ├── session_01571588-....jsonl  # 4KB (7 days ago)
    └── archived/
        └── session_<old_id>.gz     # Compressed (>30 days old)
```

---

## Customization

### Change Retention Periods

**Option 1: Modify SessionEnd Hook**

Edit `.claude/hooks/session_end/rotate_logs.py`:

```python
config = LogRotationConfig(
    main_log_retention_days=7,   # Changed from 14
    agent_log_retention_days=14,  # Changed from 30
    archive_before_delete=True,
    dry_run=False,
)
```

**Option 2: Environment Variables** (future enhancement)

```bash
export CLAUDE_LOG_RETENTION_DAYS=7
export CLAUDE_AGENT_LOG_RETENTION_DAYS=14
```

### Disable Archiving

If you want to delete without archiving (saves disk space):

```python
config = LogRotationConfig(
    main_log_retention_days=14,
    agent_log_retention_days=30,
    archive_before_delete=False,  # Changed from True
    dry_run=False,
)
```

**Trade-off:** Saves disk space but loses ability to recover old logs.

### Change Archive Location

```python
config = LogRotationConfig(
    main_log_retention_days=14,
    agent_log_retention_days=30,
    archive_before_delete=True,
    archive_dir="archive_2025",  # Custom subdirectory
    dry_run=False,
)
```

---

## Safety Features

### 1. Never Deletes Active Logs

The rotator **never** touches `claude.log` (active file):

```python
def _is_active_log(self, log_file: Path) -> bool:
    """Active log is always 'claude.log' (no number suffix)."""
    return log_file.name == "claude.log"
```

### 2. Dry Run by Default

When run manually, defaults to dry run to prevent accidental deletion:

```bash
# Safe: Shows what would happen
python .claude/tools/logging/rotation.py

# Explicit flag required to execute
python .claude/tools/logging/rotation.py --execute
```

### 3. Archive Before Delete

Default configuration archives (compresses) logs before deletion:
- Compressed with gzip (~10:1 ratio)
- Stored in `archived/` subdirectories
- Can recover if needed

### 4. Fail-Safe Error Handling

SessionEnd hook catches errors and logs them without failing:

```python
except Exception as e:
    log_error("Log rotation failed", "rotate_logs", exception=e)
    return {"error": str(e)}
```

**Impact:** If rotation fails, session still ends normally.

---

## Monitoring

### Check Rotation Status

**View recent rotation events:**

```bash
# Check last rotation
tail -20 .claude/logs/claude.log | grep "rotate_logs"
```

**Expected output:**
```
2025-10-23 11:00:00 [HOOK:rotate_logs] [INFO] Rotating logs (2 main, 15 agent files to process)
2025-10-23 11:00:01 [HOOK:rotate_logs] [INFO] Rotation complete: 2 main + 15 agent logs cleaned | bytes_freed=25.5 MB, bytes_archived=2.8 MB
```

### Check Archive Contents

```bash
# List archived files
ls -lh .claude/logs/archived/
ls -lh .claude/logs/agent_usage/archived/

# Uncompress to view (non-destructive)
gunzip -c .claude/logs/archived/claude.log.5_20251023.gz | less
```

### Disk Usage Analysis

```bash
# Current log usage
du -sh .claude/logs/
du -sh .claude/logs/agent_usage/

# Archive usage
du -sh .claude/logs/archived/
du -sh .claude/logs/agent_usage/archived/

# Detailed breakdown
du -h .claude/logs/* | sort -rh | head -10
```

---

## Troubleshooting

### Rotation Not Running

**Check SessionEnd hook is registered:**

```bash
# View hooks configuration
cat .claude/disabled.settings.json | jq '.hooks.SessionEnd'
```

**Expected:**
```json
[
  {
    "matcher": ".*",
    "hooks": [
      {
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session_end/rotate_logs.py",
        "timeout": 10000
      }
    ]
  }
]
```

**Check hook is executable:**

```bash
ls -l .claude/hooks/session_end/rotate_logs.py
# Should show: -rwxr-xr-x (executable)

# If not executable:
chmod +x .claude/hooks/session_end/rotate_logs.py
```

### Old Logs Not Being Deleted

**Check current retention settings:**

View `.claude/hooks/session_end/rotate_logs.py` for `LogRotationConfig` parameters.

**Verify file ages:**

```bash
# Check main log ages
find .claude/logs -name "claude.log.*" -type f -mtime +14

# Check agent log ages
find .claude/logs/agent_usage -name "session_*.jsonl" -type f -mtime +30
```

**Test rotation manually:**

```bash
# Dry run to see what would be rotated
python .claude/tools/logging/rotation.py

# Execute if needed
python .claude/tools/logging/rotation.py --execute
```

### Logs Growing Too Fast

**Reduce log verbosity:**

```bash
# Set environment variable
export HOOK_LOG_LEVEL=WARNING  # Instead of INFO/DEBUG

# Add to .claude/disabled.settings.json env section
{
  "env": {
    "HOOK_LOG_LEVEL": "WARNING"
  }
}
```

**More aggressive rotation:**

Edit `.claude/hooks/session_end/rotate_logs.py`:

```python
config = LogRotationConfig(
    main_log_retention_days=7,   # Reduced from 14
    agent_log_retention_days=14,  # Reduced from 30
    archive_before_delete=True,
    dry_run=False,
)
```

### Cannot Find Log Directory

**Error:** `Cannot locate .claude/logs directory`

**Solutions:**

1. **Set `CLAUDE_PROJECT_DIR`:**
   ```bash
   export CLAUDE_PROJECT_DIR=/path/to/your_project
   ```

2. **Run from project root:**
   ```bash
   cd /path/to/your_project
   python .claude/tools/logging/rotation.py
   ```

3. **Specify log directory explicitly:**
   ```python
   from pathlib import Path
   from .claude.tools.logging.rotation import ClaudeLogRotator, LogRotationConfig

   config = LogRotationConfig(main_log_retention_days=14)
   rotator = ClaudeLogRotator(config, log_dir=Path("/path/to/.claude/logs"))
   results = rotator.rotate_all()
   ```

---

## Integration with Existing Systems

### OpenTelemetry Logs (Separate System)

**Important:** This rotation system is for `.claude/logs/` (Claude Code logs), NOT for `./logs/` (application OpenTelemetry logs).

**Application logs** (OpenTelemetry):
- Location: `./logs/your_project.log`
- Managed by: `src/your_project/core/monitoring/`
- Rotation: Via `OTELConfiguration` (10MB, 5 backups)

**Claude Code logs** (this system):
- Location: `.claude/logs/claude.log`
- Managed by: `.claude/tools/logging/`
- Rotation: Via `ClaudeLogRotator` (size + age-based)

### Log Levels

Both systems respect log level environment variables:

```bash
# Application logs
export LOG_LEVEL=INFO
export FASTMCP_LOG_LEVEL=INFO

# Hook logs
export HOOK_LOG_LEVEL=INFO
```

---

## Performance Considerations

### SessionEnd Hook Overhead

**Typical execution time:** <1 second when no rotation needed

**With rotation:** 2-5 seconds (depends on file count)

**Timeout:** 10 seconds (configured in `.claude/settings.json`)

**Optimization:** Hook checks if old files exist before doing expensive operations:

```python
# Only rotate if we found old files
if old_main_logs > 0 or old_agent_logs > 0:
    results = rotator.rotate_all()
else:
    return {"skipped": True, "reason": "No old files to rotate"}
```

### Disk Space Impact

**Before rotation** (example scenario):
- Main logs: 5 × 10MB = 50MB
- Agent logs: 190 × 4KB = 760KB
- **Total:** ~51MB

**After rotation** (with archiving):
- Main logs: 4 × 10MB = 40MB
- Archived (compressed): 1 × 1MB = 1MB
- Agent logs: 114 × 4KB = 456KB (76 old files archived)
- Archived agents: 76 × 400 bytes = 30KB
- **Total:** ~42MB (saves ~9MB, plus 1MB archived)

**Without archiving:** Saves full 10MB + 304KB

---

## Future Enhancements

### Environment Variable Configuration

```bash
export CLAUDE_LOG_RETENTION_DAYS=7
export CLAUDE_AGENT_LOG_RETENTION_DAYS=14
export CLAUDE_LOG_ARCHIVE=false
```

### Cron-Based Rotation

For long-running systems:

```bash
# Add to crontab (daily at 2am)
0 2 * * * cd /path/to/project && python .claude/tools/logging/rotation.py --execute
```

### Selective Archiving

Archive only certain log types:

```python
config = LogRotationConfig(
    main_log_retention_days=14,
    agent_log_retention_days=30,
    archive_before_delete=True,
    archive_patterns=["claude.log.*"],  # Only archive main logs
    dry_run=False,
)
```

### Size Limits

Add maximum archive size limits:

```python
config = LogRotationConfig(
    main_log_retention_days=14,
    agent_log_retention_days=30,
    archive_before_delete=True,
    max_archive_size_mb=100,  # Delete oldest archives if >100MB
    dry_run=False,
)
```

---

## Summary

**Automatic rotation on SessionEnd:**
- Main logs: 14 days → archive → delete
- Agent logs: 30 days → archive → delete
- Safe, tested, integrated

**Manual rotation when needed:**
```bash
python .claude/tools/logging/rotation.py --execute
```

**Monitoring:**
```bash
tail -f .claude/logs/claude.log | grep rotate_logs
```

**Customization:** Edit `.claude/hooks/session_end/rotate_logs.py` config

**Safety:** Dry run by default, never touches active logs, archives before deletion

---

**Last Updated:** 2025-10-23
**Version:** 1.0.0
**Maintainer:** Claude Code Hooks System
