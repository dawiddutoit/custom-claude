# Home Assistant Notification Examples

Comprehensive examples for sending notifications to Home Assistant via REST API.

## Basic Notification

Simple text message:

```bash
source /Users/dawiddutoit/projects/play/network-infrastructure/.env

curl -X POST "${HA_BASE_URL}/api/services/notify/mobile_app_phone" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Infrastructure monitoring started",
    "title": "Network Infrastructure"
  }'
```

## Notification with Priority

```bash
curl -X POST "${HA_BASE_URL}/api/services/notify/mobile_app_phone" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Cloudflare Tunnel disconnected",
    "title": "Critical Alert",
    "data": {
      "priority": "high",
      "ttl": 0,
      "importance": "high"
    }
  }'
```

**Priority levels:**
- `high` - Heads-up notification, sound/vibration
- `normal` - Standard notification
- `low` - Silent notification

## Notification with Tag (Replaces Previous)

Use tags to update existing notifications instead of creating new ones:

```bash
# First notification
curl -X POST "${HA_BASE_URL}/api/services/notify/mobile_app_phone" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Checking tunnel status...",
    "title": "Infrastructure Health",
    "data": {
      "tag": "tunnel_status"
    }
  }'

# This replaces the first notification (same tag)
curl -X POST "${HA_BASE_URL}/api/services/notify/mobile_app_phone" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tunnel connected successfully",
    "title": "Infrastructure Health",
    "data": {
      "tag": "tunnel_status"
    }
  }'
```

## Notification with Actions

Interactive notifications with action buttons:

```bash
curl -X POST "${HA_BASE_URL}/api/services/notify/mobile_app_phone" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Cloudflare Tunnel is down. Auto-recovery failed.",
    "title": "Critical Infrastructure Alert",
    "data": {
      "priority": "high",
      "tag": "tunnel_alert",
      "actions": [
        {
          "action": "restart_tunnel",
          "title": "Restart Tunnel"
        },
        {
          "action": "check_logs",
          "title": "View Logs"
        },
        {
          "action": "dismiss",
          "title": "Dismiss"
        }
      ]
    }
  }'
```

**Handle actions in HA automation:**

```yaml
automation:
  - alias: "Handle Infrastructure Actions"
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: restart_tunnel
    action:
      - service: shell_command.restart_tunnel
```

## Notification with URL

Opens URL when tapped:

```bash
curl -X POST "${HA_BASE_URL}/api/services/notify/mobile_app_phone" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "SSL certificate expires in 7 days",
    "title": "Certificate Expiration Warning",
    "data": {
      "url": "https://pihole.temet.ai",
      "clickAction": "https://pihole.temet.ai"
    }
  }'
```

## Notification with Image

```bash
curl -X POST "${HA_BASE_URL}/api/services/notify/mobile_app_phone" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Infrastructure health report attached",
    "title": "Daily Report",
    "data": {
      "image": "https://example.com/health-report.png",
      "attachment": {
        "url": "https://example.com/health-report.png"
      }
    }
  }'
```

## Critical Notification (Bypasses Do Not Disturb)

```bash
curl -X POST "${HA_BASE_URL}/api/services/notify/mobile_app_phone" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "All infrastructure services are down!",
    "title": "CRITICAL FAILURE",
    "data": {
      "priority": "high",
      "ttl": 0,
      "importance": "high",
      "channel": "alarm_stream",
      "vibrationPattern": "100, 1000, 100, 1000, 100"
    }
  }'
```

## Persistent Notification (HA UI)

Notification appears in Home Assistant web interface:

```bash
curl -X POST "${HA_BASE_URL}/api/services/notify/persistent_notification" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Infrastructure monitoring detected 3 issues",
    "title": "Health Check Summary"
  }'
```

## Group Notification

Send to multiple devices:

```bash
# Send to notification group (configured in HA configuration.yaml)
curl -X POST "${HA_BASE_URL}/api/services/notify/infrastructure_alerts" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tunnel auto-recovered after 5 minutes",
    "title": "Infrastructure Auto-Recovery"
  }'
```

**Configuration for group:**

```yaml
# In configuration.yaml
notify:
  - name: infrastructure_alerts
    platform: group
    services:
      - service: mobile_app_phone1
      - service: mobile_app_phone2
      - service: persistent_notification
```

## Infrastructure Monitoring Example

Complete example from `infrastructure-monitor.sh`:

```bash
#!/bin/bash
source /Users/dawiddutoit/projects/play/network-infrastructure/.env

send_ha_notification() {
    local priority="$1"  # 1=low, 3=default, 4=high, 5=urgent
    local title="$2"
    local message="$3"

    if [[ "$HA_NOTIFICATIONS_ENABLED" != "true" ]] || [[ -z "$HA_ACCESS_TOKEN" ]]; then
        return 0
    fi

    # Map monitoring priorities to HA priorities
    local ha_priority="normal"
    case "$priority" in
        5) ha_priority="high" ;;      # Critical
        4) ha_priority="high" ;;      # Warning
        3) ha_priority="normal" ;;    # Info
        *) ha_priority="normal" ;;
    esac

    # Map priority to emoji
    local emoji=""
    case "$priority" in
        5) emoji="🔴" ;;  # Critical
        4) emoji="⚠️" ;;  # Warning
        3) emoji="🔄" ;;  # Info
        *) emoji="ℹ️" ;;  # Low
    esac

    local json_payload
    json_payload=$(cat <<EOF
{
    "message": "${message}",
    "title": "${emoji} ${title}",
    "data": {
        "priority": "${ha_priority}",
        "tag": "infrastructure_monitoring",
        "group": "Infrastructure"
    }
}
EOF
)

    local service_name="${HA_NOTIFY_SERVICE#*.}"
    local api_endpoint="${HA_BASE_URL}/api/services/notify/${service_name}"

    curl -s -X POST "$api_endpoint" \
        -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "$json_payload" \
        --max-time 10 >/dev/null 2>&1
}

# Usage examples
send_ha_notification 5 "Tunnel Down" "Cloudflare Tunnel disconnected. Auto-recovery failed."
send_ha_notification 4 "Network Isolation" "Docker network isolation detected. Attempting recovery..."
send_ha_notification 3 "Auto-Recovery" "Tunnel auto-recovered successfully"
send_ha_notification 1 "Interface Warning" "Using WiFi instead of Ethernet"
```

## Notification Best Practices

### Use Tags for Updates

```bash
# Initial notification
send_notification "tunnel_check" "Checking tunnel..." "low"

# Update same notification (replaces instead of new)
send_notification "tunnel_check" "Tunnel connected" "normal"
```

### Rate Limiting

Avoid spam by tracking last sent time:

```bash
STATE_FILE="/var/tmp/infrastructure-monitor-state.txt"
ALERT_COOLDOWN=1800  # 30 minutes

send_alert_once() {
    local alert_key="$1"
    local title="$2"
    local message="$3"

    # Check last alert time
    if [[ -f "$STATE_FILE" ]]; then
        last_alert=$(grep "^${alert_key}:" "$STATE_FILE" 2>/dev/null | cut -d: -f2)
        if [[ -n "$last_alert" ]]; then
            elapsed=$(($(date +%s) - last_alert))
            if [[ $elapsed -lt $ALERT_COOLDOWN ]]; then
                return 0  # Skip, too soon
            fi
        fi
    fi

    # Send notification
    send_ha_notification 4 "$title" "$message"

    # Record alert time
    sed -i "/^${alert_key}:/d" "$STATE_FILE" 2>/dev/null || true
    echo "${alert_key}:$(date +%s)" >> "$STATE_FILE"
}
```

### Error Handling

```bash
send_ha_notification_safe() {
    local title="$1"
    local message="$2"

    local response
    response=$(curl -s -X POST "${HA_BASE_URL}/api/services/notify/${SERVICE_NAME}" \
        -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$message\", \"title\": \"$title\"}" \
        --max-time 10 \
        2>&1)

    local exit_code=$?

    if [[ $exit_code -ne 0 ]]; then
        echo "WARNING: Failed to send HA notification: $response" >&2
        return 1
    fi

    echo "HA notification sent successfully"
    return 0
}
```

## Testing Notifications

### Test from Command Line

```bash
source /Users/dawiddutoit/projects/play/network-infrastructure/.env

# Extract service name
SERVICE_NAME="${HA_NOTIFY_SERVICE#*.}"

# Send test notification
curl -v -X POST "${HA_BASE_URL}/api/services/notify/${SERVICE_NAME}" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test notification from infrastructure monitoring",
    "title": "Test Alert",
    "data": {"priority": "high"}
  }'

# Check response
# Success: [] (empty array)
# Failure: Error message with details
```

### Verify Service Exists

```bash
# List all notify services
curl -s "${HA_BASE_URL}/api/services" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" | \
  jq '.[] | select(.domain == "notify") | .services | keys'

# Example output:
# [
#   "mobile_app_phone",
#   "persistent_notification",
#   "notify"
# ]
```

### Check Notification History

In Home Assistant:
1. Developer Tools → Events
2. Listen to event: `mobile_app_notification_action`
3. Trigger notification with action
4. View event data

## Common Issues

### No Notification Received

**Check:**
1. Service name is correct: `notify.mobile_app_phone` (not just `mobile_app_phone`)
2. HA Companion app is installed and logged in
3. Notification permissions enabled on phone
4. Access token is valid
5. HA_NOTIFICATIONS_ENABLED=true in .env

**Test:**
```bash
# Send to persistent_notification (always works)
curl -X POST "${HA_BASE_URL}/api/services/notify/persistent_notification" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test", "title": "Test"}'

# Check HA UI for notification
```

### 401 Unauthorized

Access token is invalid or expired.

**Fix:**
1. Create new long-lived access token in HA
2. Update HA_ACCESS_TOKEN in .env
3. Restart monitoring service

### 404 Not Found

Service name doesn't exist.

**Fix:**
1. List available services: `curl -s "${HA_BASE_URL}/api/services" -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" | jq`
2. Verify service name in HA Developer Tools → Services
3. Update HA_NOTIFY_SERVICE in .env

### Notification Spam

Too many notifications sent.

**Fix:**
- Use tags to update existing notifications
- Implement cooldown periods (30-60 minutes)
- Use alert state tracking
- Group similar alerts

## See Also

- HA REST API Reference: `references/api-endpoints.md`
- Service Call Examples: `examples/service-call-examples.md`
- Main SKILL.md: Section 3.4 (Sending Notifications)
