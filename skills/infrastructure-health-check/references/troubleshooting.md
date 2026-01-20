# Troubleshooting Reference

Common issues and solutions for infrastructure health check failures.

## Docker Container Issues

### Container Not Running

**Symptom:** `[FAIL] pihole: exited` or similar

**Solutions:**

1. **Check why container stopped:**
   ```bash
   docker logs pihole --tail 50
   docker inspect pihole --format='{{.State.ExitCode}}'
   ```

2. **Restart container:**
   ```bash
   cd /home/dawiddutoit/projects/network
   docker compose up -d pihole
   ```

3. **Check disk space:**
   ```bash
   df -h
   docker system df
   ```

4. **Check for port conflicts:**
   ```bash
   sudo netstat -tulpn | grep -E "53|80|443|9000"
   ```

### Container Unhealthy

**Symptom:** `[WARN] pihole: running (unhealthy)`

**Solutions:**

1. **Check health check logs:**
   ```bash
   docker inspect pihole --format='{{json .State.Health}}' | python3 -m json.tool
   ```

2. **Restart container:**
   ```bash
   docker compose restart pihole
   ```

3. **Check container resources:**
   ```bash
   docker stats --no-stream
   ```

---

## HTTPS Endpoint Issues

### No Response / Timeout

**Symptom:** `[FAIL] pihole.temet.ai: no response`

**Possible Causes:**
- Caddy container not running
- DNS not resolving
- Firewall blocking port 443

**Solutions:**

1. **Check Caddy status:**
   ```bash
   docker compose ps caddy
   docker logs caddy --tail 30
   ```

2. **Test local Caddy:**
   ```bash
   curl -I http://localhost:80 --resolve pihole.temet.ai:80:127.0.0.1
   ```

3. **Verify DNS resolution:**
   ```bash
   dig pihole.temet.ai +short
   ```

4. **Check firewall:**
   ```bash
   sudo iptables -L -n | grep -E "443|80"
   ```

### HTTP 502 Bad Gateway

**Symptom:** `[FAIL] pihole.temet.ai: HTTP/2 502`

**Cause:** Caddy cannot reach the backend service.

**Solutions:**

1. **Verify backend is running:**
   ```bash
   docker compose ps
   curl http://pihole:80 --resolve pihole:80:172.17.0.X  # (Docker IP)
   ```

2. **Check Caddyfile backend address:**
   ```bash
   grep -A5 "pihole.temet.ai" /home/dawiddutoit/projects/network/config/Caddyfile
   ```

3. **Check Docker network:**
   ```bash
   docker network inspect network_default
   ```

### HTTP 500 Internal Server Error

**Symptom:** `[FAIL] service.temet.ai: HTTP/2 500`

**Cause:** Backend service error.

**Solutions:**

1. **Check backend service logs:**
   ```bash
   docker logs pihole --tail 50
   ```

2. **Test backend directly:**
   ```bash
   docker exec caddy curl -I http://pihole:80
   ```

---

## DNS Resolution Issues

### Local DNS Not Resolving

**Symptom:** `[FAIL] Local DNS (Pi-hole): not resolving`

**Solutions:**

1. **Check Pi-hole container:**
   ```bash
   docker exec pihole pihole status
   ```

2. **Test DNS directly:**
   ```bash
   docker exec pihole dig +short @127.0.0.1 pihole.temet.ai
   ```

3. **Check Pi-hole custom DNS entries:**
   ```bash
   docker exec pihole cat /etc/pihole/custom.list
   ```

4. **Restart Pi-hole DNS:**
   ```bash
   docker exec pihole pihole restartdns
   ```

### Host Not Using Pi-hole

**Symptom:** `[WARN] Host DNS: not using Pi-hole as resolver`

**Cause:** Host `/etc/resolv.conf` doesn't point to Pi-hole.

**Solutions:**

1. **Check current DNS:**
   ```bash
   cat /etc/resolv.conf
   ```

2. **Update to use Pi-hole:**
   ```bash
   # Temporary (until reboot)
   sudo sh -c 'echo "nameserver 127.0.0.1" > /etc/resolv.conf'
   ```

3. **Check router DHCP settings:**
   - Set primary DNS to Pi's IP (192.168.68.135)

---

## Cloudflare Tunnel Issues

### Tunnel Not Connected

**Symptom:** `[WARN] Tunnel connection: no recent connection logs`

**Solutions:**

1. **Check tunnel token:**
   ```bash
   grep CLOUDFLARE_TUNNEL_TOKEN /home/dawiddutoit/projects/network/.env
   ```

2. **Restart cloudflared:**
   ```bash
   docker compose restart cloudflared
   ```

3. **Check full logs:**
   ```bash
   docker logs cloudflared --tail 100
   ```

4. **Verify tunnel in Cloudflare dashboard:**
   - Go to https://one.dash.cloudflare.com
   - Access -> Tunnels
   - Check tunnel status

### Tunnel Connection Errors

**Symptom:** `[WARN] Recent tunnel errors detected`

**Common Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `connection refused` | Backend unreachable | Check Caddy is running |
| `timeout` | Network latency | Check internet connection |
| `authentication failed` | Invalid token | Regenerate tunnel token |
| `too many connections` | Rate limiting | Wait and retry |

**Solutions:**

1. **Check Cloudflare status:**
   - https://www.cloudflarestatus.com/

2. **Test internet connectivity:**
   ```bash
   curl -I https://cloudflare.com
   ```

3. **Regenerate tunnel token:**
   - Cloudflare dashboard -> Tunnels -> Configure -> Generate new token
   - Update `.env` and restart cloudflared

---

## Webhook Issues

### Local Webhook Not Responding

**Symptom:** `[FAIL] Local webhook (localhost:9000): not responding`

**Solutions:**

1. **Check webhook container:**
   ```bash
   docker compose ps webhook
   docker logs webhook --tail 30
   ```

2. **Check hooks.json configuration:**
   ```bash
   cat /home/dawiddutoit/projects/network/config/hooks.json | python3 -m json.tool
   ```

3. **Restart webhook:**
   ```bash
   docker compose restart webhook
   ```

### Webhook Not Accessible via Tunnel

**Symptom:** `[WARN] Webhook via tunnel: not accessible`

**Cause:** Tunnel may be down or route not configured.

**Solutions:**

1. **Check tunnel status first**
2. **Verify tunnel route in Cloudflare dashboard:**
   - Access -> Tunnels -> pi-home -> Public Hostname
   - Should have `webhook.temet.ai` -> `http://caddy:80`

---

## SSL Certificate Issues

### Unable to Retrieve Certificate

**Symptom:** `[FAIL] domain.temet.ai: unable to retrieve certificate`

**Solutions:**

1. **Check Caddy logs for cert errors:**
   ```bash
   docker logs caddy | grep -i "certificate\|error\|tls"
   ```

2. **Verify Cloudflare API token:**
   ```bash
   # Should not be empty
   docker exec caddy env | grep CLOUDFLARE_API_KEY
   ```

3. **Force certificate renewal:**
   ```bash
   docker compose restart caddy
   # Wait 1-2 minutes for certificate
   docker logs caddy -f | grep -i certificate
   ```

### Certificate Expiring Soon

**Symptom:** `[WARN] domain.temet.ai: expires soon`

**Cause:** Auto-renewal may have failed.

**Solutions:**

1. **Check Caddy renewal logs:**
   ```bash
   docker logs caddy | grep -i "renew"
   ```

2. **Force renewal:**
   ```bash
   # Caddy auto-renews at 30 days remaining
   # To force, restart Caddy
   docker compose restart caddy
   ```

3. **Check API token permissions:**
   - Must have "Edit zone DNS" for temet.ai

---

## Cloudflare Access Issues

### Unable to Retrieve Access Applications

**Symptom:** `[FAIL] Unable to retrieve Cloudflare Access applications`

**Solutions:**

1. **Check API credentials:**
   ```bash
   grep -E "CLOUDFLARE_ACCOUNT_ID|CLOUDFLARE_ACCESS_API_TOKEN" /home/dawiddutoit/projects/network/.env
   ```

2. **Test API manually:**
   ```bash
   source /home/dawiddutoit/projects/network/.env
   curl -s "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/apps" \
     -H "Authorization: Bearer ${CLOUDFLARE_ACCESS_API_TOKEN}" | python3 -m json.tool
   ```

3. **Regenerate API token:**
   - https://dash.cloudflare.com/profile/api-tokens
   - Create token with Zero Trust + Access permissions

### Service Not Protected by Access

**Symptom:** `[WARN] domain.temet.ai: not protected by Access`

**Solutions:**

1. **Run Access setup:**
   ```bash
   ./scripts/cf-access-setup.sh setup
   ```

2. **Manually create in dashboard:**
   - https://one.dash.cloudflare.com
   - Access -> Applications -> Add application

---

## Quick Recovery Commands

**Full restart (nuclear option):**
```bash
cd /home/dawiddutoit/projects/network
docker compose down
docker compose up -d
sleep 30  # Wait for services to start
./scripts/health-check.sh
```

**Clear and rebuild:**
```bash
cd /home/dawiddutoit/projects/network
docker compose down -v  # WARNING: Removes volumes
docker compose build --no-cache
docker compose up -d
```

**Check all logs at once:**
```bash
docker compose logs --tail 50
```

**Service-specific restarts:**
```bash
docker compose restart pihole
docker compose restart caddy
docker compose restart cloudflared
docker compose restart webhook
```

---

## Diagnostic Information to Gather

When reporting issues, collect:

```bash
# System info
uname -a
docker --version
docker compose version

# Service status
docker compose ps

# Recent logs
docker compose logs --tail 20

# Network info
ip addr | grep -E "inet |eth|wlan"
cat /etc/resolv.conf

# Health check output
./scripts/health-check.sh --full
```
