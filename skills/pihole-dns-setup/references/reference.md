# Pi-hole DNS Setup - Reference Guide

Complete technical reference for Pi-hole DNS configuration, internals, and troubleshooting.

## Table of Contents

1. [Pi-hole DNS Architecture](#pi-hole-dns-architecture)
2. [Configuration Methods](#configuration-methods)
3. [DNS Entry Format](#dns-entry-format)
4. [Verification Commands](#verification-commands)
5. [Pi-hole Internals](#pi-hole-internals)
6. [Troubleshooting Reference](#troubleshooting-reference)
7. [Router DNS Configuration](#router-dns-configuration)

---

## Pi-hole DNS Architecture

### How Local DNS Resolution Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    LOCAL DNS FLOW                                │
│                                                                  │
│  Device Query                                                    │
│      │                                                           │
│      ▼                                                           │
│  ┌─────────────┐    Local DNS Match?    ┌──────────────────┐   │
│  │   Router    │ ──────────────────────►│     Pi-hole      │   │
│  │  (DHCP)     │                        │  (192.168.68.135) │   │
│  └─────────────┘                        └────────┬─────────┘   │
│                                                   │             │
│                              Yes ◄───────────────┼─────► No    │
│                               │                   │       │     │
│                               ▼                   │       ▼     │
│                    Return Local IP              Forward to      │
│                   (192.168.68.135)              Upstream DNS    │
│                                                 (1.1.1.1)       │
└─────────────────────────────────────────────────────────────────┘
```

### Dual-Path Resolution

| Query Source | DNS Server | Resolution Path |
|-------------|------------|-----------------|
| Home Wi-Fi | Pi-hole (192.168.68.135) | Local DNS -> Caddy -> Service |
| Mobile/Remote | Cloudflare DNS | CNAME -> Tunnel -> Service |

### DNS Resolution Priority

Pi-hole resolves queries in this order:

1. **Custom DNS entries** (FTLCONF_dns_hosts) - Highest priority
2. **Local hostnames** (/etc/hosts)
3. **DHCP leases** (if DHCP enabled)
4. **Upstream DNS** (1.1.1.1, 8.8.8.8)

---

## Configuration Methods

### Method 1: Automated via domains.toml (Recommended)

**How it works:**
1. Edit `domains.toml` to add/modify service
2. Run `./scripts/manage-domains.sh apply`
3. Script generates DNS entries and updates docker-compose.yml
4. Pi-hole restarts with new configuration

**Example domains.toml entry:**
```toml
[[services]]
name = "My Service"
subdomain = "myservice"
backend = "192.168.68.135:8080"
dns_ip = "192.168.68.135"  # This creates the DNS entry
```

**Script that processes this:**
```bash
./scripts/generate-pihole-dns.py
```

### Method 2: Direct docker-compose.yml Edit

**Location:** `/home/dawiddutoit/projects/network/docker-compose.yml`

**Edit the FTLCONF_dns_hosts section:**
```yaml
services:
  pihole:
    environment:
      FTLCONF_dns_hosts: |
        192.168.68.135 pihole.temet.ai
        192.168.68.135 jaeger.temet.ai
        192.168.68.135 langfuse.temet.ai
        192.168.68.135 ha.temet.ai
        192.168.68.135 code.temet.ai
        192.168.68.105 sprinkler.temet.ai
        192.168.68.135 webhook.temet.ai
        192.168.68.135 temet.ai
```

**Apply changes:**
```bash
docker compose -f /home/dawiddutoit/projects/network/docker-compose.yml restart pihole
```

### Method 3: Pi-hole Web UI (Not Recommended)

**Why not recommended:**
- Entries lost on container recreation
- Not version controlled
- Out of sync with domains.toml

**If you must use it:**
1. Access: http://localhost:8081/admin or https://pihole.temet.ai
2. Navigate: Local DNS -> DNS Records
3. Add domain and IP
4. Click "Add"

### Method 4: Pi-hole CLI

**Add entry via CLI:**
```bash
docker exec pihole pihole -a addcustomdns pihole.temet.ai 192.168.68.135
```

**Remove entry:**
```bash
docker exec pihole pihole -a removecustomdns pihole.temet.ai
```

**Note:** CLI changes persist in container but lost on recreation.

---

## DNS Entry Format

### FTLCONF_dns_hosts Syntax

```yaml
FTLCONF_dns_hosts: |
  <IP_ADDRESS> <FQDN>
  <IP_ADDRESS> <FQDN>
```

**Rules:**
- One entry per line
- IP address first, then domain
- Space-separated (not tab)
- Fully qualified domain name (include .temet.ai)
- No trailing comments

### Valid Examples

```yaml
# Standard service on Pi
192.168.68.135 pihole.temet.ai

# IoT device with own IP
192.168.68.105 sprinkler.temet.ai

# Root domain
192.168.68.135 temet.ai

# Multiple subdomains same IP
192.168.68.135 service1.temet.ai
192.168.68.135 service2.temet.ai
```

### Invalid Examples

```yaml
# WRONG: Tab-separated
192.168.68.135	pihole.temet.ai

# WRONG: Missing IP
pihole.temet.ai

# WRONG: Comment in line
192.168.68.135 pihole.temet.ai  # This is pihole

# WRONG: Partial domain
192.168.68.135 pihole
```

---

## Verification Commands

### Test DNS Resolution

**From Pi (using localhost):**
```bash
dig @localhost pihole.temet.ai +short
# Expected: 192.168.68.135
```

**From Pi (using Pi's IP):**
```bash
dig @192.168.68.135 pihole.temet.ai +short
```

**From another device on LAN:**
```bash
dig @192.168.68.135 pihole.temet.ai +short
```

**Full DNS query details:**
```bash
dig @localhost pihole.temet.ai
```

**Reverse lookup:**
```bash
dig @localhost -x 192.168.68.135 +short
```

### Batch Verification Script

```bash
#!/bin/bash
# Test all configured domains

PI_IP="192.168.68.135"
DOMAINS=("pihole" "jaeger" "langfuse" "ha" "code" "sprinkler" "webhook")

echo "Testing DNS resolution via Pi-hole..."
echo "========================================"

for domain in "${DOMAINS[@]}"; do
  full_domain="${domain}.temet.ai"
  result=$(dig @$PI_IP $full_domain +short 2>/dev/null)

  if [ -z "$result" ]; then
    echo "[FAIL] $full_domain -> No response"
  else
    echo "[OK]   $full_domain -> $result"
  fi
done
```

### Check Pi-hole Status

```bash
# Pi-hole service status
docker exec pihole pihole status

# DNS service status
docker exec pihole pihole -t
# (Shows live query log - Ctrl+C to exit)

# Statistics
docker exec pihole pihole -c
# (Chronometer - shows stats)
```

### Check Container Health

```bash
# Container status
docker ps | grep pihole

# Container logs
docker logs pihole --tail 50

# Check listening ports
docker exec pihole netstat -tulpn | grep 53
```

---

## Pi-hole Internals

### Configuration Files (inside container)

| File | Purpose |
|------|---------|
| `/etc/pihole/custom.list` | Custom DNS entries |
| `/etc/pihole/pihole-FTL.conf` | FTL configuration |
| `/etc/dnsmasq.d/` | dnsmasq configuration |
| `/etc/pihole/setupVars.conf` | Pi-hole setup variables |

### How FTLCONF_dns_hosts Works

1. Docker Compose sets environment variable `FTLCONF_dns_hosts`
2. Pi-hole container entrypoint reads this variable
3. Writes entries to `/etc/pihole/custom.list`
4. dnsmasq reads custom.list and serves DNS
5. Queries for listed domains return configured IP

### DNS Query Flow

```
Query: pihole.temet.ai
         │
         ▼
┌─────────────────┐
│   FTL (DNS)     │ Checks custom.list first
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  custom.list    │ Found: 192.168.68.135 pihole.temet.ai
└────────┬────────┘
         │
         ▼
   Return: 192.168.68.135
```

### TTL (Time To Live)

Default TTL for local DNS entries: 2 seconds (Pi-hole default)

To change (not recommended):
```bash
docker exec pihole pihole -a setcache 300
# Sets cache TTL to 300 seconds
```

---

## Troubleshooting Reference

### Error: DNS Not Resolving

**Symptoms:**
- `dig @localhost domain.temet.ai` returns NXDOMAIN
- Browser shows "DNS_PROBE_FINISHED_NXDOMAIN"

**Diagnosis:**
```bash
# Check if Pi-hole is running
docker ps | grep pihole

# Check if entry exists in container
docker exec pihole cat /etc/pihole/custom.list | grep domain

# Check Pi-hole logs
docker logs pihole | tail 20
```

**Solutions:**

1. Entry not in docker-compose.yml:
```bash
# Check FTLCONF_dns_hosts in docker-compose.yml
grep -A 20 "FTLCONF_dns_hosts" /home/dawiddutoit/projects/network/docker-compose.yml
```

2. Pi-hole needs restart:
```bash
docker compose -f /home/dawiddutoit/projects/network/docker-compose.yml restart pihole
```

3. Re-run domain configuration:
```bash
./scripts/manage-domains.sh apply
```

### Error: Wrong IP Returned

**Symptoms:**
- `dig` returns old/wrong IP
- Cached response

**Solutions:**

1. Clear Pi-hole cache:
```bash
docker exec pihole pihole restartdns reload-lists
```

2. Flush local DNS cache (on querying device):
```bash
# Linux
sudo systemd-resolve --flush-caches

# macOS
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
```

3. Check for duplicate entries:
```bash
grep "domain.temet.ai" /home/dawiddutoit/projects/network/docker-compose.yml
```

### Error: Works on Pi, Not on Other Devices

**Symptoms:**
- `dig @localhost` works on Pi
- `dig @192.168.68.135` fails from other devices

**Diagnosis:**
```bash
# Check Pi-hole listening interface
docker exec pihole netstat -tulpn | grep :53

# Check firewall on Pi
sudo iptables -L -n | grep 53
```

**Solutions:**

1. Router not using Pi-hole as DNS:
   - Configure router DHCP to set Pi-hole as DNS server

2. Pi-hole not listening on all interfaces:
   - Check `DNSMASQ_LISTENING: "all"` in docker-compose.yml

3. Device using cached DNS:
   - Disconnect/reconnect to Wi-Fi
   - Renew DHCP lease

### Error: Pi-hole Container Won't Start

**Symptoms:**
- `docker ps` doesn't show pihole
- Container restart loop

**Diagnosis:**
```bash
docker logs pihole
docker compose -f /home/dawiddutoit/projects/network/docker-compose.yml logs pihole
```

**Common Causes:**

1. Port 53 already in use:
```bash
sudo netstat -tulpn | grep :53
# Kill conflicting service (usually systemd-resolved)
sudo systemctl disable systemd-resolved
sudo systemctl stop systemd-resolved
```

2. Invalid FTLCONF_dns_hosts format:
```bash
# Validate format - check for tabs, extra spaces
cat -A /home/dawiddutoit/projects/network/docker-compose.yml | grep -A 20 FTLCONF
```

---

## Router DNS Configuration

### Common Router Interfaces

**Most Routers:**
1. Access router admin (192.168.68.1 or similar)
2. Find DHCP settings
3. Set DNS servers:
   - Primary: 192.168.68.135 (Pi-hole)
   - Secondary: 1.1.1.1 (fallback)

**Google Nest WiFi:**
1. Open Google Home app
2. WiFi settings -> Advanced Networking
3. DNS: Custom
4. Primary: 192.168.68.135
5. Secondary: 1.1.1.1

**Ubiquiti/UniFi:**
1. UniFi Controller -> Networks
2. Edit network -> DHCP Name Server
3. Manual -> 192.168.68.135

### Verify Router DNS Configuration

After changing router DNS, verify on client devices:

```bash
# Linux/Mac
cat /etc/resolv.conf
# Should show: nameserver 192.168.68.135

# Windows
ipconfig /all | findstr "DNS"
# Should show: DNS Servers: 192.168.68.135
```

### Per-Device DNS Override

If router configuration isn't possible:

**Linux:**
Edit `/etc/resolv.conf`:
```
nameserver 192.168.68.135
```

**macOS:**
System Preferences -> Network -> Advanced -> DNS -> Add 192.168.68.135

**Windows:**
Network adapter -> Properties -> IPv4 -> DNS -> 192.168.68.135

---

## Quick Reference Commands

```bash
# Check Pi-hole status
docker exec pihole pihole status

# View live DNS queries
docker exec pihole pihole -t

# Restart DNS service
docker exec pihole pihole restartdns

# Clear DNS cache
docker exec pihole pihole restartdns reload-lists

# Test DNS resolution
dig @192.168.68.135 pihole.temet.ai +short

# Check custom DNS entries
docker exec pihole cat /etc/pihole/custom.list

# Apply all domain changes
./scripts/manage-domains.sh apply

# List configured domains
./scripts/manage-domains.sh list
```
