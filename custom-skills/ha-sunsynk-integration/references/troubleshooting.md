# Sunsynk Integration Troubleshooting

Comprehensive troubleshooting guide for Sunsynk/Deye solar inverter integration issues.

## Table of Contents

1. "No Permissions" Error
2. Authentication Failures
3. No Entities Created
4. Data Not Updating
5. Local Modbus Not Working
6. WiFi Dongle Limitations
7. Common Configuration Issues

## 1. "No Permissions" Error

**Symptom:**
```
Error: No Permissions to access inverter E47W23428459
```

**Root Cause:** Using WiFi dongle serial instead of inverter serial

**How to Identify:**
- Dongle serials start with `E4` (e.g., `E47W23428459`)
- Inverter serials start with `23` or `24` (e.g., `2305178402`)

**Solution:**

**Step 1: Find Inverter Serial**
```bash
# Check physical label on inverter unit
# OR use Sunsynk mobile app:
# Settings → Plant Info → Inverter Details → "Inverter Serial"
# NOT "Dongle Serial"
```

**Step 2: Update Configuration**
```yaml
# In add-on configuration, change:
sunsynk_serial: "E47W23428459"  # ❌ WRONG (dongle serial)
# To:
sunsynk_serial: "2305178402"    # ✅ CORRECT (inverter serial)
```

**Step 3: Restart Add-on**
```bash
# In Home Assistant:
# Settings → Add-ons → SolarSynkV3 → Restart
```

**Verification:**
```bash
# Check add-on logs after restart:
# http://192.168.68.123:8123/hassio/addon/d4ae3b04_solar_synkv3/logs

# Expected:
# ✅ "Successfully logged in to Sunsynk API"
# ✅ "Retrieved inverter data for serial 2305178402"
```

## 2. Authentication Failures

**Symptom:**
```
Error: Authentication failed for user@example.com
```

**Possible Causes:**

### Cause 1: Wrong Username/Password

**Diagnostic:**
```bash
# Test credentials in Sunsynk mobile app
# If app login fails, password is wrong
```

**Solution:**
1. Use password reset in mobile app/web portal
2. Update add-on configuration with new password
3. Restart add-on

### Cause 2: Wrong API Server

**Diagnostic:**
```bash
# Check your region:
# South Africa → api.sunsynk.net
# Europe → api-eu.sunsynk.net
# Asia Pacific → api-ap.sunsynk.net
# Americas → api-us.sunsynk.net
```

**Solution:**
```yaml
# Update API_Server in configuration:
API_Server: "api.sunsynk.net"  # For South Africa/Region 2
```

### Cause 3: Account Locked

**Symptom:** Too many failed login attempts

**Solution:**
1. Wait 15 minutes for auto-unlock
2. Don't restart add-on during waiting period
3. Verify credentials before restarting

## 3. No Entities Created

**Symptom:** Add-on starts successfully but no sensors appear in Home Assistant

### Diagnostic Workflow

**Step 1: Check Add-on Logs**
```bash
# View logs at: http://192.168.68.123:8123/hassio/addon/d4ae3b04_solar_synkv3/logs

# Look for entity creation messages:
# ✅ "Created sensor.solarsynkv3_2305178402_battery_soc"
# ✅ "Created sensor.solarsynkv3_2305178402_pv_pac"

# If missing, proceed to Step 2
```

**Step 2: Verify HA Long-Lived Token**
```bash
# Test token works:
curl -s "http://192.168.68.123:8123/api/" \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN"

# Expected: {"message": "API running."}
# If error: Token is invalid, create new one
```

**Step 3: Create New Token**
```bash
# In Home Assistant:
# 1. Profile (bottom left)
# 2. Scroll to "Long-Lived Access Tokens"
# 3. Delete old "SolarSynkV3" token
# 4. Create new token
# 5. Copy token (shown once only)
# 6. Update add-on config with new token
# 7. Restart add-on
```

**Step 4: Check IP/Port Configuration**
```bash
# Verify HA is accessible at configured IP:
curl -s "http://192.168.68.123:8123/api/states" \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" \
  | wc -l

# Should return line count (200+)
# If connection refused: Wrong IP or port
```

**Step 5: Verify Network Access**
```bash
# From HA host, test API connectivity:
ping -c 3 api.sunsynk.net

# Check DNS resolution:
nslookup api.sunsynk.net

# If ping fails: Network/firewall issue
```

**Step 6: Restart Add-on**
```bash
# Sometimes a restart after config changes is needed
# Settings → Add-ons → SolarSynkV3 → Stop → Start
# Wait 30 seconds
# Check logs for entity creation
```

## 4. Data Not Updating

**Symptom:** Entities exist but show stale/old data

### Check 1: Verify Refresh Rate

**Issue:** Refresh rate set too low causes API rate limiting

**Solution:**
```yaml
# In add-on configuration:
Refresh_rate: 300  # 5 minutes (minimum recommended)

# If experiencing rate limiting:
Refresh_rate: 600  # 10 minutes
```

**Why:** Sunsynk API has rate limits. Polling too frequently results in HTTP 429 errors and data stops updating.

### Check 2: API Rate Limiting

**Diagnostic:**
```bash
# Check add-on logs for:
# ❌ "Rate limit exceeded"
# ❌ "Too many requests"
# ❌ "HTTP 429"
```

**Solution:**
```yaml
# Increase refresh rate:
Refresh_rate: 600  # 10 minutes

# Restart add-on
# Wait at least 15 minutes before checking again
```

### Check 3: Internet Connection

**Diagnostic:**
```bash
# Add-on requires internet to reach api.sunsynk.net
# Test from HA host:
ping -c 5 api.sunsynk.net

# Check DNS resolution:
nslookup api.sunsynk.net

# Test HTTPS connectivity:
curl -I https://api.sunsynk.net
```

**Solution:**
- Check firewall rules allow outbound HTTPS
- Verify DNS server is working
- Check router/gateway connectivity
- Test with alternative DNS (8.8.8.8)

### Check 4: Add-on Still Running

**Diagnostic:**
```bash
# Check add-on status in Home Assistant:
# Settings → Add-ons → SolarSynkV3
# Status should show "Started"

# If stopped: Check logs for crash errors
```

**Solution:**
```bash
# Enable watchdog to auto-restart on crash:
# Add-on page → Configuration → Enable "Watchdog"
# Click "Start" to restart add-on
```

## 5. Local Modbus Not Working

**Symptom:** kellerza/sunsynk integration can't connect to inverter

**Root Cause:** Stock Sunsynk WiFi dongles don't support local Modbus access

### Verification

```bash
# Find your dongle IP from router DHCP
# Test Modbus ports:
nc -zv 192.168.68.XXX 502   # Modbus TCP
nc -zv 192.168.68.XXX 8899  # Sunsynk protocol

# Result: Connection refused (ports closed by firmware)
```

### Why This Happens

Stock Sunsynk WiFi dongles are configured for cloud-only operation:
- Ports 502 and 8899 are disabled in firmware
- Only outbound connections to api.sunsynk.net allowed
- No local Modbus TCP support
- No HTTP management interface

### Solutions

See section 6 (WiFi Dongle Limitations) for workarounds.

## 6. WiFi Dongle Limitations

Stock Sunsynk WiFi dongles are **cloud-only**. They don't expose Modbus TCP ports for local access.

### Workarounds for Local Access

#### Option 1: Replace WiFi Dongle

**Hardware:**
- Purchase: Solarman LSW-3 WiFi dongle
- Supports local Modbus TCP access (port 8899)
- Drop-in replacement (same connector)
- Cost: ~$50-80

**Configuration:**
```bash
# After replacing dongle:
# 1. Connect to dongle's WiFi AP
# 2. Configure for local network
# 3. Note dongle IP address
# 4. Use kellerza/sunsynk integration
# 5. Configure Modbus host: <dongle-ip>:8899
```

#### Option 2: Flash Custom Firmware

**Requirements:**
- Dongle uses ESP8266 chip (not always the case)
- Serial/UART access to dongle
- ESPHome or Tasmota firmware

**Risk:** May brick dongle if wrong chip or failed flash

**Benefit:** Local MQTT integration, no cloud dependency

#### Option 3: Direct RS485 Connection

**Hardware:**
- RS485 cable from inverter COM port
- USB-RS485 adapter OR Ethernet-RS485 converter
- Run cable to Home Assistant server location

**Pros:**
- Most reliable local access
- No dongle needed
- Fastest response times

**Cons:**
- Cable installation required
- Physical access to inverter needed

#### Option 4: Waveshare RS485 to Ethernet

**Hardware:**
- Waveshare RS485 to Ethernet converter (~$40)
- RS485 cable to inverter COM port
- Network connection to converter

**Configuration:**
```bash
# Waveshare provides Modbus TCP server
# Configure kellerza/sunsynk:
# Host: <waveshare-ip>
# Port: 502 (Modbus TCP)
# Inverter ID: 1 (default)
```

**Recommendation:** Stick with SolarSynkV3 cloud integration unless you need:
- <5 minute refresh rates
- Offline operation
- Real-time control/automation

## 7. Common Configuration Issues

### Issue: Wrong Home_Assistant_IP

**Symptom:** Add-on can't create entities

**Solution:**
```yaml
# Use local IP, NOT DNS name:
Home_Assistant_IP: "192.168.68.123"  # ✅ Correct
Home_Assistant_IP: "ha.temet.ai"     # ❌ Wrong (DNS may not resolve from container)
```

### Issue: HTTPS Enabled Without SSL

**Symptom:** Add-on can't connect to HA API

**Solution:**
```yaml
# Only enable if HA has valid SSL certificate:
Enable_HTTPS: false  # For standard HTTP setup
Enable_HTTPS: true   # Only if using Let's Encrypt/valid cert
```

### Issue: Wrong Region API Server

**Symptom:** Authentication fails or slow response

**Solution:**
```yaml
# Match API server to your region:
API_Server: "api.sunsynk.net"      # South Africa (Region 2)
API_Server: "api-eu.sunsynk.net"   # Europe (Region 1)
API_Server: "api-ap.sunsynk.net"   # Asia Pacific (Region 3)
API_Server: "api-us.sunsynk.net"   # Americas (Region 4)
```

### Issue: Token in Version Control

**Symptom:** Security risk if repo is public

**Solution:**
```yaml
# Never commit HA_LongLiveToken to git
# Add to .gitignore:
# .env
# secrets.yaml
# *_config.yaml

# Use secrets management:
HA_LongLiveToken: !secret ha_token
```

### Issue: Add-on Not Starting on Boot

**Symptom:** Manual restart needed after HA reboot

**Solution:**
```bash
# Enable "Start on boot":
# Settings → Add-ons → SolarSynkV3 → Toggle "Start on boot"
```

### Issue: Inverter Serial Changed

**Symptom:** After inverter replacement/firmware update, entities stop working

**Solution:**
```yaml
# Update serial in configuration:
sunsynk_serial: "2405123456"  # New serial

# Restart add-on
# Old entities may need manual cleanup:
# Settings → Devices & Services → Entities → Filter "solarsynkv3"
# Delete old entities with previous serial
```

## Quick Diagnostic Checklist

Run through this checklist for any integration issue:

```bash
# 1. Verify inverter serial (NOT dongle serial)
# Format: 23XXXXXXXX or 24XXXXXXXX

# 2. Test HA API access
curl -s "http://192.168.68.123:8123/api/" \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN"

# 3. Test Sunsynk API credentials in mobile app
# Open app → Verify login works

# 4. Check add-on logs
# http://192.168.68.123:8123/hassio/addon/d4ae3b04_solar_synkv3/logs

# 5. Verify add-on is running
# Settings → Add-ons → SolarSynkV3 → Status: Started

# 6. Check refresh rate (>=300 seconds)
# Add-on Configuration → Refresh_rate: 300

# 7. Test internet connectivity
ping -c 3 api.sunsynk.net

# 8. Verify entities exist
curl -s "http://192.168.68.123:8123/api/states" \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" \
  | grep -c "solarsynkv3"
# Should return 30+ if working
```

## Getting Help

If issues persist after troubleshooting:

**Collect Diagnostic Information:**
```bash
# 1. Add-on logs (last 100 lines)
# 2. Add-on configuration (REMOVE token before sharing)
# 3. Home Assistant version
# 4. Add-on version
# 5. Inverter model and serial format
# 6. Error messages (exact text)
```

**Where to Get Help:**
- GitHub Issues: https://github.com/martinville/solarsynkv3/issues
- Home Assistant Community: https://community.home-assistant.io
- Sunsynk support: For inverter-specific issues

**Security Note:** Never share your `HA_LongLiveToken` or `sunsynk_pass` publicly. Redact these fields before posting logs or configurations.
