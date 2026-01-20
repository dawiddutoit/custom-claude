# Pi-hole DNS Setup - Examples

Real-world examples of configuring Pi-hole DNS for various scenarios.

## Table of Contents

1. [Initial DNS Setup](#1-initial-dns-setup)
2. [Adding a New Service](#2-adding-a-new-service)
3. [IoT Device with Custom IP](#3-iot-device-with-custom-ip)
4. [Troubleshooting DNS Resolution](#4-troubleshooting-dns-resolution)
5. [Migrating Services to New IP](#5-migrating-services-to-new-ip)
6. [Fresh Pi-hole Installation](#6-fresh-pi-hole-installation)
7. [Bulk DNS Verification](#7-bulk-dns-verification)
8. [Router DNS Configuration](#8-router-dns-configuration)

---

## 1. Initial DNS Setup

**Scenario:** First-time setup of Pi-hole DNS for all services.

**User Request:** "Set up Pi-hole DNS for my services"

**Steps:**

1. **Detect Pi's IP address:**
```bash
hostname -I | awk '{print $1}'
# Output: 192.168.68.135
```

2. **Verify domains.toml has dns_ip entries:**
```bash
grep "dns_ip" /home/dawiddutoit/projects/network/domains.toml
```

3. **Apply configuration:**
```bash
cd /home/dawiddutoit/projects/network && ./scripts/manage-domains.sh apply
```

4. **Verify DNS resolution:**
```bash
for domain in pihole jaeger langfuse ha code webhook sprinkler; do
  echo -n "$domain.temet.ai -> "
  dig @localhost $domain.temet.ai +short
done
```

**Expected Output:**
```
pihole.temet.ai -> 192.168.68.135
jaeger.temet.ai -> 192.168.68.135
langfuse.temet.ai -> 192.168.68.135
ha.temet.ai -> 192.168.68.135
code.temet.ai -> 192.168.68.135
webhook.temet.ai -> 192.168.68.135
sprinkler.temet.ai -> 192.168.68.105
```

5. **Reminder about router DNS:**
```
Configure your router to use Pi-hole as DNS:
- Primary DNS: 192.168.68.135
- Secondary DNS: 1.1.1.1

Access router admin at: http://192.168.68.1 (typically)
Look for: DHCP Settings -> DNS Server
```

---

## 2. Adding a New Service

**Scenario:** Adding Grafana dashboard that needs local DNS resolution.

**User Request:** "Add DNS for grafana.temet.ai pointing to the Pi"

**Steps:**

1. **Add to domains.toml:**
```toml
[[services]]
name = "Grafana Dashboard"
subdomain = "grafana"
backend = "192.168.68.135:3001"
enable_https = true
enable_http = false
dns_ip = "192.168.68.135"
require_auth = true
```

2. **Apply changes:**
```bash
./scripts/manage-domains.sh apply
```

3. **Verify the new entry:**
```bash
dig @localhost grafana.temet.ai +short
# Expected: 192.168.68.135
```

4. **Test browser access:**
```
Navigate to: https://grafana.temet.ai
Should connect to local Grafana instance
```

---

## 3. IoT Device with Custom IP

**Scenario:** Adding a smart thermostat at a different IP than the Pi.

**User Request:** "Add DNS for thermostat.temet.ai at 192.168.68.110"

**Steps:**

1. **Verify the device is reachable:**
```bash
ping -c 3 192.168.68.110
```

2. **Add to domains.toml:**
```toml
[[services]]
name = "Smart Thermostat"
subdomain = "thermostat"
backend = "192.168.68.110:80"
enable_https = false
enable_http = true
dns_ip = "192.168.68.110"  # Device's actual IP for direct local access
require_auth = true
strip_cf_headers = true
```

3. **Apply and verify:**
```bash
./scripts/manage-domains.sh apply

dig @localhost thermostat.temet.ai +short
# Expected: 192.168.68.110
```

**Note:** IoT devices typically use their own IP for dns_ip because:
- Local access goes directly to the device (faster)
- Caddy doesn't need to proxy local IoT traffic
- Remote access still goes through Cloudflare Tunnel

---

## 4. Troubleshooting DNS Resolution

**Scenario:** User reports "pihole.temet.ai doesn't work locally"

**Diagnosis Steps:**

1. **Check Pi-hole container is running:**
```bash
docker ps | grep pihole
# Should show: pihole running
```

2. **Test DNS from Pi:**
```bash
dig @localhost pihole.temet.ai +short
```

3. **If no response, check if entry exists:**
```bash
docker exec pihole cat /etc/pihole/custom.list | grep pihole
# Should show: 192.168.68.135 pihole.temet.ai
```

4. **If entry missing, check docker-compose.yml:**
```bash
grep -A 10 "FTLCONF_dns_hosts" /home/dawiddutoit/projects/network/docker-compose.yml
```

5. **Regenerate and apply:**
```bash
./scripts/manage-domains.sh apply
```

6. **If works from Pi but not from device:**
```bash
# Check device is using Pi-hole as DNS
# On the device:
cat /etc/resolv.conf
# Should show: nameserver 192.168.68.135

# If not, device is using different DNS
# Solution: Configure router DHCP to use Pi-hole
```

**Common Issues and Fixes:**

| Issue | Diagnosis | Fix |
|-------|-----------|-----|
| NXDOMAIN | Entry not in custom.list | Run `./scripts/manage-domains.sh apply` |
| Wrong IP | Stale cache | `docker exec pihole pihole restartdns reload-lists` |
| Works on Pi only | Router DNS misconfigured | Set router DNS to Pi-hole IP |
| Intermittent | Pi-hole container restarting | Check `docker logs pihole` |

---

## 5. Migrating Services to New IP

**Scenario:** Moving services from Pi at 192.168.68.135 to new Pi at 192.168.68.140

**Steps:**

1. **Update domains.toml with new IPs:**
```toml
# Change all dns_ip entries
[global]
pi_ip = "192.168.68.140"  # Update default IP

[[services]]
dns_ip = "192.168.68.140"  # Update each service
```

2. **Regenerate DNS configuration:**
```bash
python3 /home/dawiddutoit/projects/network/scripts/generate-pihole-dns.py
```

3. **View the changes before applying:**
```bash
grep -A 10 "FTLCONF_dns_hosts" /home/dawiddutoit/projects/network/docker-compose.yml
```

4. **Apply changes (on new Pi):**
```bash
docker compose -f /home/dawiddutoit/projects/network/docker-compose.yml up -d
```

5. **Update router DNS to point to new Pi:**
```
Router DHCP DNS: 192.168.68.140
```

6. **Clear DNS caches:**
```bash
# On new Pi-hole
docker exec pihole pihole restartdns reload-lists

# On client devices - reconnect to WiFi or:
sudo systemd-resolve --flush-caches  # Linux
sudo dscacheutil -flushcache         # macOS
```

---

## 6. Fresh Pi-hole Installation

**Scenario:** Setting up DNS on a brand new Pi-hole installation.

**Prerequisites:**
- Pi-hole container running
- domains.toml exists with services defined

**Steps:**

1. **Verify Pi-hole is running:**
```bash
docker ps | grep pihole
# Should show healthy pihole container
```

2. **Check Pi-hole can resolve external domains:**
```bash
dig @localhost google.com +short
# Should return Google's IP addresses
```

3. **Run full domain setup:**
```bash
cd /home/dawiddutoit/projects/network && ./scripts/manage-domains.sh apply
```

4. **Verify all DNS entries created:**
```bash
docker exec pihole cat /etc/pihole/custom.list
```

Expected output:
```
192.168.68.135 code.temet.ai
192.168.68.135 ha.temet.ai
192.168.68.135 jaeger.temet.ai
192.168.68.135 langfuse.temet.ai
192.168.68.135 pihole.temet.ai
192.168.68.105 sprinkler.temet.ai
192.168.68.135 temet.ai
192.168.68.135 webhook.temet.ai
```

5. **Test resolution for each domain:**
```bash
./scripts/verify-dns.sh  # If script exists
# Or manually test each domain
```

6. **Configure router DNS:**
```
IMPORTANT: Configure your router to use Pi-hole as DNS server.

Without this, devices won't use Pi-hole for DNS resolution.

Router admin: http://192.168.68.1
DHCP settings -> DNS:
  Primary: 192.168.68.135
  Secondary: 1.1.1.1
```

---

## 7. Bulk DNS Verification

**Scenario:** Verify all DNS entries are working correctly.

**Quick Check:**
```bash
# One-liner to test all domains
for d in $(grep "^subdomain" /home/dawiddutoit/projects/network/domains.toml | cut -d'"' -f2 | grep -v "^$"); do
  echo -n "$d.temet.ai: "
  dig @localhost $d.temet.ai +short || echo "FAILED"
done
```

**Detailed Verification Script:**
```bash
#!/bin/bash
# save as verify-dns.sh

PI_IP="192.168.68.135"
DOMAINS=(
  "pihole:192.168.68.135"
  "jaeger:192.168.68.135"
  "langfuse:192.168.68.135"
  "ha:192.168.68.135"
  "code:192.168.68.135"
  "sprinkler:192.168.68.105"
  "webhook:192.168.68.135"
)

echo "DNS Verification Report"
echo "======================="
echo ""

passed=0
failed=0

for entry in "${DOMAINS[@]}"; do
  domain="${entry%%:*}"
  expected="${entry##*:}"
  full_domain="${domain}.temet.ai"

  actual=$(dig @$PI_IP $full_domain +short 2>/dev/null)

  if [ "$actual" = "$expected" ]; then
    echo "[PASS] $full_domain -> $actual"
    ((passed++))
  else
    echo "[FAIL] $full_domain -> Expected: $expected, Got: ${actual:-NXDOMAIN}"
    ((failed++))
  fi
done

echo ""
echo "Results: $passed passed, $failed failed"

if [ $failed -gt 0 ]; then
  echo ""
  echo "To fix failed entries, run:"
  echo "  ./scripts/manage-domains.sh apply"
fi
```

**Sample Output:**
```
DNS Verification Report
=======================

[PASS] pihole.temet.ai -> 192.168.68.135
[PASS] jaeger.temet.ai -> 192.168.68.135
[PASS] langfuse.temet.ai -> 192.168.68.135
[PASS] ha.temet.ai -> 192.168.68.135
[PASS] code.temet.ai -> 192.168.68.135
[PASS] sprinkler.temet.ai -> 192.168.68.105
[PASS] webhook.temet.ai -> 192.168.68.135

Results: 7 passed, 0 failed
```

---

## 8. Router DNS Configuration

**Scenario:** Configure router to use Pi-hole as DNS server.

### Google Nest WiFi

1. Open Google Home app on phone
2. Tap Wi-Fi -> Settings (gear icon)
3. Advanced networking
4. DNS: Automatic -> Custom
5. Primary server: 192.168.68.135
6. Secondary server: 1.1.1.1
7. Save

### Generic Router (Web Interface)

1. Access router: http://192.168.68.1 (or your router's IP)
2. Login with admin credentials
3. Navigate to: LAN Settings -> DHCP
4. Find: DNS Server settings
5. Change from Automatic to Manual
6. Primary DNS: 192.168.68.135
7. Secondary DNS: 1.1.1.1
8. Save and apply

### Verify Router Configuration

After router restart, test from a device:

```bash
# Release and renew DHCP lease
# Linux:
sudo dhclient -r && sudo dhclient

# Check DNS server assigned
cat /etc/resolv.conf
# Should show: nameserver 192.168.68.135

# Or test directly
dig @192.168.68.135 pihole.temet.ai +short
```

### Fallback: Per-Device Configuration

If router config isn't possible:

**Linux (NetworkManager):**
```bash
# Edit connection
nmcli con mod "Wi-Fi Connection" ipv4.dns "192.168.68.135"
nmcli con mod "Wi-Fi Connection" ipv4.ignore-auto-dns yes
nmcli con up "Wi-Fi Connection"
```

**macOS:**
```bash
# Via System Preferences:
# Network -> Wi-Fi -> Advanced -> DNS -> Add 192.168.68.135
# Drag it to top of list

# Or via terminal:
networksetup -setdnsservers Wi-Fi 192.168.68.135 1.1.1.1
```

---

## Quick Reference

### Common Commands

```bash
# Apply all DNS changes
./scripts/manage-domains.sh apply

# Test single domain
dig @localhost pihole.temet.ai +short

# Test all domains
./scripts/manage-domains.sh list

# Check Pi-hole DNS entries
docker exec pihole cat /etc/pihole/custom.list

# Restart Pi-hole DNS
docker exec pihole pihole restartdns

# View live DNS queries
docker exec pihole pihole -t
```

### DNS Entry Examples

| Domain | IP | Use Case |
|--------|-----|----------|
| pihole.temet.ai | 192.168.68.135 | Pi-hole admin |
| jaeger.temet.ai | 192.168.68.135 | Tracing UI |
| sprinkler.temet.ai | 192.168.68.105 | IoT device |
| ha.temet.ai | 192.168.68.135 | Home Assistant |
| temet.ai | 192.168.68.135 | Root domain |
