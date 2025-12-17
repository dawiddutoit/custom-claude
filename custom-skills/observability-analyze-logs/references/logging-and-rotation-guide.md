# Claude Logs Rotation & Management Guide

## Overview

Claude Code logs in this project use **automatic log rotation** to prevent disk space issues. This document explains the current setup and how to manage logs.

---

## Current Configuration

### Primary Log File

```
.claude/logs/claude.log
```

**Settings:**
- **Max file size**: 10MB (auto-rotates when reached)
- **Backup count**: 5 files (claude.log.1 through claude.log.5)
- **Retention**: Rotated files kept indefinitely (age-based cleanup optional)
- **Format**: `[timestamp] [CATEGORY:module] [LEVEL] message`

### Log Categories

All logs are tagged with categories for easy filtering:

- `HOOK` - Hook executions (PreToolUse, PostToolUse, SessionStart, etc.)
- `MAINTENANCE` - Scheduled maintenance and cleanup tasks
- `INSIGHTS` - Daily insights generation and analysis
- `AGENT` - Agent usage tracking and logging
- `HEADLESS` - Headless Claude executions
- `TOOLS` - General tool operations
- `CRON` - Cron job executions

---

## How Rotation Works

### Automatic Size-Based Rotation

Implemented via Python's `RotatingFileHandler` in `.claude/tools/logging/config.py`:

```python
file_handler = logging.handlers.RotatingFileHandler(
    log_dir / log_filename,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
)
```

**What happens when claude.log reaches 10MB:**
1. `claude.log` → `claude.log.1` (current file renamed)
2. `claude.log.1` → `claude.log.2` (previous backup rotated)
3. `claude.log.2` → `claude.log.3` (and so on...)
4. `claude.log.5` → deleted (oldest backup removed)
5. New empty `claude.log` created

### Manual Age-Based Cleanup

Run the cleanup script to remove old timestamped logs:

```bash
python .claude/scripts/cleanup_old_logs.py
```

**What it does:**
- Removes old timestamped log files (pattern: `*_YYYYMMDD_HHMMSS.log`)
- Deletes logs older than 7 days (configurable)
- Safe to run anytime - doesn't touch active rotation files

---

## Monitoring Log Files

### Check Current Log Status

```bash
# View log file sizes
ls -lh .claude/logs/*.log

# View current log tail
tail -f .claude/logs/claude.log

# Count total log storage
du -sh .claude/logs/
```

### Expected Output

```
-rw-r--r--  1 user  staff   2.7M Oct 23 10:34 claude.log
-rw-r--r--  1 user  staff    10M Oct 22 18:33 claude.log.1
```

**Total disk usage**: ~60MB maximum (6 files × 10MB)

---

## Configuration Reference

### Log Configuration Location

**File**: `.claude/tools/logging/config.py`

**Key function**: `get_logger()`

```python
def get_logger(
    name: str,
    category: str = "TOOLS",
    log_filename: str = "claude.log",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    level: str = "INFO",
    console_output: bool = True,
    subdirectory: str | None = None,
) -> logging.Logger:
```

### Customizing Rotation Settings

To change rotation behavior, update the defaults in `config.py`:

```python
# Increase max file size to 50MB
max_bytes: int = 50 * 1024 * 1024

# Keep more backups (10 files)
backup_count: int = 10

# Change retention period in cleanup_old_logs()
def cleanup_old_logs(days: int = 30):  # Changed from 7 to 30 days
```

### Environment Variables

Control logging behavior via environment variables:

```bash
# Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
export LOG_LEVEL=DEBUG

# Custom log directory
export LOG_DIR=/custom/path/to/logs

# Custom log file path
export LOG_FILE_PATH=/custom/path/to/claude.log

# Override max bytes
export LOG_MAX_BYTES=52428800  # 50MB in bytes

# Override backup count
export LOG_BACKUP_COUNT=10
```

---

## Integration with Hooks

All hooks use the centralized logging system via `BaseHook` class:

### Hook Logging Example

```python
from hooks.utils.base_hook import BaseHook

class MyHook(BaseHook):
    def run(self):
        # Logs automatically go to claude.log with rotation
        self.success("Hook completed successfully")

if __name__ == "__main__":
    hook = MyHook("my_hook_name")
    hook.execute()
```

**Automatic features:**
- Hook lifecycle logging (start, stop, error)
- Environment variable capture
- Execution time tracking
- Categorized output (`[HOOK:my_hook_name]`)

---

## Comparison to Application Logs

This project has **two separate logging systems**:

| Aspect | Claude Logs | Application Logs (OpenTelemetry) |
|--------|-------------|----------------------------------|
| **Purpose** | Hook execution, maintenance, insights | Application code execution traces |
| **Location** | `.claude/logs/claude.log` | `logs/your_project.log` |
| **Rotation** | RotatingFileHandler (10MB/5 backups) | RotatingFileHandler (10MB/5 backups) |
| **Format** | Timestamped + Category | OpenTelemetry structured (trace/span IDs) |
| **Usage** | Debugging hook behavior | Debugging application logic |
| **Skill** | `analyze-session-logs` (JSONL files) | `analyze-logs` (OpenTelemetry traces) |

**Important**: Don't confuse these systems! Use the right tool for the job:
- Hook debugging → `tail -f .claude/logs/claude.log`
- Application debugging → `Skill(command: "analyze-logs")`

---

## Testing Rotation

Verify log rotation is working:

```bash
# Run comprehensive rotation tests
python .claude/scripts/test_log_rotation.py
```

**Test coverage:**
- ✅ Rotation interval configuration
- ✅ Log file writability
- ✅ Entry writing and file growth
- ✅ Manual rotation trigger
- ✅ Backup file creation
- ✅ Backup count limits
- ✅ No orphaned version files

Expected output:
```
🧪 LOG ROTATION TEST SUITE
============================================================

🧪 TESTING HOOKS.LOG ROTATION
============================================================
✅ Rotation interval defined
✅ Log file exists
✅ Initial log state
✅ Log entries written
✅ File size increased
✅ Manual rotation triggered
...

🎉 ALL TESTS PASSED!
```

---

## Troubleshooting

### Issue: Log file not rotating

**Symptoms**: claude.log grows beyond 10MB

**Causes**:
1. File permissions issue (log file not writable)
2. Handler misconfiguration
3. Multiple logger instances overwriting handler

**Solution**:
```bash
# Check file permissions
ls -l .claude/logs/claude.log

# Make writable if needed
chmod 644 .claude/logs/claude.log

# Run rotation test
python .claude/scripts/test_log_rotation.py
```

### Issue: Too many backup files

**Symptoms**: More than 5 `.log.N` files exist

**Causes**:
1. Multiple logging configurations with different backup counts
2. Manual backups not cleaned up

**Solution**:
```bash
# Remove excess backups manually
cd .claude/logs
rm claude.log.6 claude.log.7 claude.log.8  # etc.

# Or run cleanup script
python .claude/scripts/cleanup_old_logs.py
```

### Issue: Disk space still filling up

**Symptoms**: Logs directory exceeds 100MB

**Causes**:
1. Orphaned timestamped log files
2. Subdirectory logs not rotated
3. Agent usage logs accumulating

**Solution**:
```bash
# Check total disk usage
du -sh .claude/logs/*

# Find large files
find .claude/logs -type f -size +10M

# Run cleanup script
python .claude/scripts/cleanup_old_logs.py

# Consider reducing retention period
# Edit cleanup_old_logs.py: days=7 → days=3
```

---

## Best Practices

### DO ✅

- **Use `get_logger()` from `config.py`** - Ensures rotation is configured
- **Use categorized logging** - Makes filtering easier (`category="HOOK"`)
- **Run cleanup periodically** - Weekly or monthly via cron/hook
- **Monitor log sizes** - Check `du -sh .claude/logs/` occasionally
- **Test rotation** - Run test script after config changes

### DON'T ❌

- **Don't create custom log files** - Use the centralized system
- **Don't disable rotation** - Prevents disk space issues
- **Don't hardcode paths** - Use `$CLAUDE_PROJECT_DIR` environment variable
- **Don't mix logging systems** - Claude logs vs OpenTelemetry logs serve different purposes
- **Don't commit log files** - Add `.claude/logs/*.log` to `.gitignore`

---

## Future Enhancements (Optional)

### Automated Age-Based Cleanup

Add SessionEnd hook to trigger cleanup:

```python
# .claude/hooks/session_end/cleanup_logs.py
from tools.logging.config import cleanup_old_logs

def run():
    cleanup_old_logs(days=7)  # Remove logs older than 7 days
```

### Configurable Retention Period

Add settings to `.claude/settings.json`:

```json
{
  "logging": {
    "max_bytes": 10485760,
    "backup_count": 5,
    "retention_days": 7
  }
}
```

### Log Compression

Compress old backups to save space:

```bash
# Add to cleanup script
gzip .claude/logs/claude.log.[5-9]
```

---

## Summary

**Current state**: ✅ **Fully functional rotating log system**

- Automatic size-based rotation (10MB threshold)
- 5 backup files maintained
- Manual age-based cleanup available
- Consistent with OpenTelemetry pattern
- Tested and verified

**No action required** - the system is already optimal for preventing log accumulation!

**Optional improvements**: Automate age-based cleanup, add monitoring, make retention configurable.

---

**Last Updated**: 2025-10-23
**Maintainer**: Claude Code Hooks System
**Related Files**:
- `.claude/tools/logging/config.py` - Logging configuration
- `.claude/scripts/cleanup_old_logs.py` - Age-based cleanup
- `.claude/scripts/test_log_rotation.py` - Rotation tests
- `.claude/hooks/utils/base_hook.py` - Hook base class with logging
