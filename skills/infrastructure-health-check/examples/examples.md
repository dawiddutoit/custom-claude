# Health Check Examples

Example outputs from the infrastructure health check in various scenarios.

## All Checks Passing

```
==========================================
  Infrastructure Health Report
  Generated: 2025-12-06 14:30:15
  Host: raspberrypi
==========================================

DOCKER CONTAINERS
-----------------
[PASS] pihole: running (healthy)
[PASS] caddy: running (no-healthcheck)
[PASS] cloudflared: running (no-healthcheck)
[PASS] webhook: running (no-healthcheck)

HTTPS ENDPOINTS
---------------
[PASS] pihole.temet.ai: HTTP/2 302
[PASS] jaeger.temet.ai: HTTP/2 200
[PASS] langfuse.temet.ai: HTTP/2 200
[PASS] ha.temet.ai: HTTP/2 302
[PASS] code.temet.ai: HTTP/2 302

DNS RESOLUTION
--------------
[PASS] Local DNS (Pi-hole): pihole.temet.ai -> 192.168.68.135
[PASS] Host DNS: pihole.temet.ai -> 192.168.68.135
[PASS] Pi-hole DNS service: running

CLOUDFLARE TUNNEL
-----------------
[PASS] Cloudflared process: running
[PASS] Tunnel connection: established

WEBHOOK ENDPOINT
----------------
[PASS] Local webhook (localhost:9000): responding
[PASS] Webhook via tunnel: accessible

SSL CERTIFICATES
----------------
[PASS] pihole.temet.ai: valid (67 days remaining)
[PASS] jaeger.temet.ai: valid (67 days remaining)
[PASS] langfuse.temet.ai: valid (67 days remaining)
[PASS] ha.temet.ai: valid (67 days remaining)
[PASS] code.temet.ai: valid (67 days remaining)

CLOUDFLARE ACCESS
-----------------
[PASS] pihole.temet.ai: protected by Access
[PASS] jaeger.temet.ai: protected by Access
[PASS] langfuse.temet.ai: protected by Access
[PASS] ha.temet.ai: protected by Access
[PASS] sprinkler.temet.ai: protected by Access
[PASS] code.temet.ai: protected by Access
[PASS] webhook.temet.ai: bypass (public access)

==========================================
  Summary: 25 passed, 0 failed, 0 warnings
==========================================
  Overall Status: ALL CHECKS PASSED
==========================================
```

---

## Container Down

```
==========================================
  Infrastructure Health Report
  Generated: 2025-12-06 14:30:15
  Host: raspberrypi
==========================================

DOCKER CONTAINERS
-----------------
[PASS] pihole: running (healthy)
[FAIL] caddy: exited
[PASS] cloudflared: running (no-healthcheck)
[PASS] webhook: running (no-healthcheck)

HTTPS ENDPOINTS
---------------
[FAIL] pihole.temet.ai: no response (timeout or unreachable)
[FAIL] jaeger.temet.ai: no response (timeout or unreachable)
[FAIL] langfuse.temet.ai: no response (timeout or unreachable)
[FAIL] ha.temet.ai: no response (timeout or unreachable)
[FAIL] code.temet.ai: no response (timeout or unreachable)

...

==========================================
  Summary: 15 passed, 6 failed, 0 warnings
==========================================
  Overall Status: FAILURES DETECTED
==========================================
```

**Recovery:**
```bash
docker compose up -d caddy
docker logs caddy --tail 20  # Check for errors
```

---

## Tunnel Disconnected

```
CLOUDFLARE TUNNEL
-----------------
[PASS] Cloudflared process: running
[WARN] Tunnel connection: no recent connection logs
[WARN] Recent tunnel errors detected (check logs)
[INFO]   2025-12-06T14:25:30Z ERR connection failed
[INFO]   2025-12-06T14:26:30Z ERR connection failed
[INFO]   2025-12-06T14:27:30Z ERR connection failed

WEBHOOK ENDPOINT
----------------
[PASS] Local webhook (localhost:9000): responding
[WARN] Webhook via tunnel: not accessible (tunnel may be down)
```

**Recovery:**
```bash
# Check internet connectivity
ping -c 3 cloudflare.com

# Restart cloudflared
docker compose restart cloudflared

# Check new logs
docker logs cloudflared --tail 30
```

---

## Certificate Expiring Soon

```
SSL CERTIFICATES
----------------
[PASS] pihole.temet.ai: valid (67 days remaining)
[WARN] jaeger.temet.ai: expires soon (Sun Dec 15 23:59:59 2024 GMT)
[PASS] langfuse.temet.ai: valid (67 days remaining)
[PASS] ha.temet.ai: valid (67 days remaining)
[PASS] code.temet.ai: valid (67 days remaining)
```

**Recovery:**
```bash
# Force Caddy to check certificates
docker compose restart caddy

# Watch for renewal
docker logs caddy -f | grep -i renew
```

---

## DNS Resolution Failure

```
DNS RESOLUTION
--------------
[FAIL] Local DNS (Pi-hole): not resolving
[WARN] Host DNS: not using Pi-hole as resolver
[FAIL] Pi-hole DNS service: not running
```

**Recovery:**
```bash
# Check Pi-hole container
docker logs pihole --tail 30

# Restart Pi-hole
docker compose restart pihole

# Verify DNS service
docker exec pihole pihole status
```

---

## Quick Check Mode Output

```bash
$ ./scripts/health-check.sh --quick
```

```
==========================================
  Infrastructure Health Report
  Generated: 2025-12-06 14:30:15
  Host: raspberrypi
==========================================

DOCKER CONTAINERS
-----------------
[PASS] pihole: running (healthy)
[PASS] caddy: running (no-healthcheck)
[PASS] cloudflared: running (no-healthcheck)
[PASS] webhook: running (no-healthcheck)

HTTPS ENDPOINTS
---------------
[PASS] pihole.temet.ai: HTTP/2 302
[PASS] jaeger.temet.ai: HTTP/2 200
[PASS] langfuse.temet.ai: HTTP/2 200
[PASS] ha.temet.ai: HTTP/2 302
[PASS] code.temet.ai: HTTP/2 302

DNS RESOLUTION
--------------
[PASS] Local DNS (Pi-hole): pihole.temet.ai -> 192.168.68.135
[PASS] Host DNS: pihole.temet.ai -> 192.168.68.135
[PASS] Pi-hole DNS service: running

CLOUDFLARE TUNNEL
-----------------
[PASS] Cloudflared process: running
[PASS] Tunnel connection: established

WEBHOOK ENDPOINT
----------------
[PASS] Local webhook (localhost:9000): responding
[PASS] Webhook via tunnel: accessible

==========================================
  Summary: 16 passed, 0 failed, 0 warnings
==========================================
  Overall Status: ALL CHECKS PASSED
==========================================
```

---

## JSON Output Mode

```bash
$ ./scripts/health-check.sh --json
```

```json
{
  "timestamp": "2025-12-06T14:30:15+02:00",
  "hostname": "raspberrypi",
  "summary": {
    "passed": 25,
    "failed": 0,
    "warnings": 0
  },
  "status": "healthy"
}
```

---

## Quiet Mode Output

```bash
$ ./scripts/health-check.sh --quiet
HEALTHY
```

```bash
$ ./scripts/health-check.sh --quiet  # with failures
UNHEALTHY: 2 failures, 1 warnings
```

---

## Full Mode Output (Verbose)

```bash
$ ./scripts/health-check.sh --full
```

```
SSL CERTIFICATES
----------------
[PASS] pihole.temet.ai: valid (67 days remaining)
[INFO]   Issuer: C = US, O = Let's Encrypt, CN = R11
[INFO]   Expires: Sat Mar  7 12:34:56 2026 GMT
[PASS] jaeger.temet.ai: valid (67 days remaining)
[INFO]   Issuer: C = US, O = Let's Encrypt, CN = R11
[INFO]   Expires: Sat Mar  7 12:35:01 2026 GMT
...
```

---

## Manual Check Commands

Individual checks without the script:

**Check containers:**
```bash
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Health}}"
```

**Check HTTPS:**
```bash
curl -sI https://pihole.temet.ai --max-time 5 | head -1
```

**Check DNS:**
```bash
dig @localhost pihole.temet.ai +short
```

**Check tunnel:**
```bash
docker logs cloudflared --tail 20 | grep -iE "connected|error"
```

**Check certificates:**
```bash
echo | openssl s_client -servername pihole.temet.ai \
  -connect pihole.temet.ai:443 2>/dev/null | \
  openssl x509 -noout -dates
```
