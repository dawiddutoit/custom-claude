# Detailed Infrastructure Management Workflows

Comprehensive workflows for managing SSH infrastructure and debugging common issues.

## Common Workflows

### Workflow 1: Before Starting NomNom Development

**Goal:** Ensure MongoDB on infra.local is accessible before starting NomNom

```bash
# 1. Check if infra.local is reachable
ping -c 1 -W 1 infra.local && echo "✅ infra.local reachable" || { echo "❌ infra.local offline"; exit 1; }

# 2. Verify MongoDB port is open
nc -z infra.local 27017 && echo "✅ MongoDB port open" || { echo "❌ MongoDB unreachable"; exit 1; }

# 3. Check MongoDB health
ssh infra "docker exec local-infra-mongodb-1 mongo off --quiet --eval 'db.runCommand({ping: 1})'" 2>/dev/null && echo "✅ MongoDB healthy"

# 4. Start NomNom
cd ~/projects/play/nomnom && ./start.sh
```

### Workflow 2: Debugging "Connection Refused" Error

**Goal:** Diagnose why a service connection is failing

```bash
# 1. Identify the service and port
# Example: MongoDB (infra.local:27017), Langfuse (infra.local:3000), Neo4j (infra.local:7687)

# 2. Check if host is online
ping -c 1 -W 1 infra.local && echo "✅ Host online" || { echo "❌ Host offline"; exit 1; }

# 3. Check if port is open
nc -z infra.local 27017 && echo "✅ Port open" || { echo "❌ Port closed"; exit 1; }

# 4. Check if container is running
ssh infra "docker ps -f name=mongodb -q" | grep -q . && echo "✅ Container running" || { echo "❌ Container not running"; exit 1; }

# 5. Check container health
ssh infra "docker inspect --format='{{.State.Health.Status}}' local-infra-mongodb-1"

# 6. View logs to find error
ssh infra "docker logs --tail 100 local-infra-mongodb-1"

# 7. If unhealthy, restart service
ssh infra "cd ~/projects/local-infra && docker compose restart mongodb"
```

### Workflow 3: Discovering Available Services on New Host

**Goal:** Find out what services are running on infra.local

```bash
# 1. Check SSH connectivity
ssh infra "echo 'SSH works'" || { echo "❌ SSH failed"; exit 1; }

# 2. List all running Docker containers
ssh infra "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

# 3. Identify critical services
ssh infra "docker ps --format '{{.Names}}'" | grep -E 'mongodb|langfuse|neo4j|otel|infinity'

# 4. Check which ports are listening
ssh infra "netstat -tuln | grep LISTEN"

# 5. Test service endpoints
nc -z infra.local 27017 && echo "✅ MongoDB (27017)"
nc -z infra.local 3000 && echo "✅ Langfuse (3000)"
nc -z infra.local 7687 && echo "✅ Neo4j (7687)"
nc -z infra.local 4317 && echo "✅ OTLP Collector (4317)"
nc -z infra.local 7997 && echo "✅ Infinity Embeddings (7997)"
```

### Workflow 4: Investigating Service in Restart Loop

**Goal:** Diagnose why Neo4j or Infinity is restarting repeatedly

```bash
# 1. Check current status
ssh infra "docker ps -a -f name=neo4j"

# 2. View logs to find error
ssh infra "docker logs --tail 200 local-infra-neo4j-1"

# 3. Check Docker Compose configuration
ssh infra "cd ~/projects/local-infra && docker compose config | grep -A 20 neo4j"

# 4. Try manual stop/start
ssh infra "cd ~/projects/local-infra && docker compose stop neo4j"
sleep 5
ssh infra "cd ~/projects/local-infra && docker compose up -d neo4j"

# 5. Follow logs in real-time
ssh infra "docker logs -f local-infra-neo4j-1"
```

### Workflow 5: Setting Up SSH Access to New Host

**Goal:** Configure passwordless SSH authentication to a new host

```bash
# 1. Test SSH with password (first time)
ssh dawiddutoit@infra.local

# 2. If SSH key doesn't exist, create it
if [ ! -f ~/.ssh/id_ed25519 ]; then
  ssh-keygen -t ed25519 -C "dawiddutoit@mbp"
fi

# 3. Copy public key to remote host
ssh-copy-id dawiddutoit@infra.local

# 4. Test passwordless authentication
ssh dawiddutoit@infra.local "echo 'SSH key works'"

# 5. Add to ~/.ssh/config for convenience
cat >> ~/.ssh/config <<EOF

Host infra
  HostName infra.local
  User dawiddutoit
  IdentityFile ~/.ssh/id_ed25519
EOF

# 6. Test alias
ssh infra "echo 'Alias works'"
```

### Workflow 6: Verifying OTLP Telemetry Pipeline

**Goal:** Ensure Claude Code telemetry reaches infra.local

```bash
# 1. Check OTLP Collector is running
ssh infra "docker ps -f name=otel-collector -q" | grep -q . && echo "✅ Collector running"

# 2. Verify port 4317 is open
nc -z infra.local 4317 && echo "✅ OTLP port open"

# 3. Check Collector logs for recent traces
ssh infra "docker logs --tail 50 local-infra-otel-collector-1 | grep -i trace"

# 4. Verify Jaeger UI is accessible
curl -s http://infra.local:16686 | grep -q "Jaeger" && echo "✅ Jaeger UI accessible"

# 5. Check Langfuse for traces
curl -s http://infra.local:3000 | grep -q "Langfuse" && echo "✅ Langfuse accessible"
```

### Workflow 7: Syncing Files to Remote Host

**Goal:** Copy local files to infra.local for testing

```bash
# 1. Test SSH connectivity
ssh infra "echo 'SSH works'" || exit 1

# 2. Create remote directory if needed
ssh infra "mkdir -p ~/projects/test"

# 3. Sync files using rsync
rsync -avz --progress ~/local/project/ infra:~/projects/test/

# 4. Or use the syncpi function (if configured)
syncpi ~/local/project infra:~/projects/test
```

## Expected Outcomes

### Successful Discovery

```
✅ Infrastructure Discovery Complete

Online Hosts: 3/5
  ✅ infra.local (16 services running)
  ✅ deus (0 services running)
  ✅ homeassistant.local (1 service running)

Offline Hosts: 2/5
  ❌ pi4-motor.local
  ❌ armitage.local

Critical Services Status:
  ✅ MongoDB (infra.local:27017) - healthy
  ✅ Langfuse (infra.local:3000) - healthy
  ✅ OTLP Collector (infra.local:4317) - healthy
  ⚠️ Neo4j (infra.local:7687) - restarting
  ⚠️ Infinity Embeddings (infra.local:7997) - restarting
```

### Successful Health Check

```
✅ Health Check Passed

Host: infra.local
SSH: Connected
Docker: 16 containers running

MongoDB:
  Container: local-infra-mongodb-1
  Status: healthy
  Port: 27017 (open)
  Database: off (632K products)
  Ping: 1ms response

Langfuse:
  Container: local-infra-langfuse-web-1
  Status: healthy
  Port: 3000 (open)
  HTTP: 200 OK

Ready for development!
```

### Failed Health Check

```
❌ Health Check Failed

Host: infra.local
SSH: ✅ Connected
Docker: ✅ Running

MongoDB:
  Container: local-infra-mongodb-1
  Status: ❌ unhealthy
  Port: 27017 (closed)
  Error: Connection refused

Recommended actions:
1. View logs: ssh infra "docker logs --tail 100 local-infra-mongodb-1"
2. Restart service: ssh infra "cd ~/projects/local-infra && docker compose restart mongodb"
3. Check disk space: ssh infra "df -h"
```

### Service Restart Loop Diagnosis

```
🔍 Investigating Neo4j Restart Loop

Container Status:
  Name: local-infra-neo4j-1
  State: Restarting
  Restart Count: 47
  Last Restart: 2 seconds ago

Log Analysis:
  ERROR: Unable to create lock file /data/lock.txt
  ERROR: Permission denied
  ERROR: Exiting with code 1

Root Cause: File permissions on /data volume

Fix Applied:
  ssh infra "docker exec local-infra-neo4j-1 chown -R neo4j:neo4j /data"
  ssh infra "cd ~/projects/local-infra && docker compose restart neo4j"

Result: ✅ Neo4j started successfully
```

## Integration Examples

### Integration with NomNom Project

**MongoDB dependency verification in NomNom start script:**

```bash
#!/bin/bash
# File: ~/projects/play/nomnom/start.sh

# Verify MongoDB on infra.local before starting
nc -z infra.local 27017 || {
  echo "❌ MongoDB unreachable on infra.local"
  echo "Run: ssh infra 'cd ~/projects/local-infra && docker compose restart mongodb'"
  exit 1
}

echo "✅ MongoDB accessible"

# Continue with NomNom startup...
poetry run python src/nomnom/api_server.py
```

### Integration with Observability Skills

**Before using observability-analyze-logs:**

```bash
# Verify OTLP Collector is running
ssh infra "docker ps -f name=otel-collector -q" | grep -q . || {
  echo "⚠️ OTLP Collector offline"
  ssh infra "cd ~/projects/local-infra && docker compose restart otel-collector"
}

# Verify Jaeger is accessible
curl -s http://infra.local:16686 | grep -q "Jaeger" || {
  echo "⚠️ Jaeger UI unreachable"
  exit 1
}

# Now use observability skills
# - observability-analyze-logs
# - observability-analyze-session-logs
```

### Integration with Home Assistant Skills

**Before using HA skills:**

```bash
# Verify Home Assistant is accessible
ping -c 1 -W 1 192.168.68.123 || {
  echo "❌ Home Assistant offline"
  exit 1
}

# Verify API is responding
curl -s -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" \
  http://192.168.68.123:8123/api/ | grep -q "message" && echo "✅ HA API accessible"

# Then use skills:
# - ha-dashboard-create
# - ha-custom-cards
# - ha-mushroom-cards
```

### Integration with Quality Gates

**Infrastructure verification as quality gate:**

```bash
# File: .github/workflows/test.yml or pre-commit hook

# Add to pre-start checks
if ! nc -z infra.local 27017; then
  echo "❌ QUALITY GATE FAILED: MongoDB unreachable"
  echo "Run: ssh infra 'cd ~/projects/local-infra && docker compose restart mongodb'"
  exit 1
fi

echo "✅ Infrastructure quality gate passed"
```

## Troubleshooting Guide

### Issue: "Connection Refused" to MongoDB

**Symptoms:**
- Application cannot connect to MongoDB
- `nc -z infra.local 27017` fails
- Error: "Connection refused"

**Diagnosis:**
```bash
# 1. Check if infra.local is reachable
ping -c 1 -W 1 infra.local

# 2. Check if MongoDB container is running
ssh infra "docker ps -f name=mongodb"

# 3. Check container logs
ssh infra "docker logs --tail 100 local-infra-mongodb-1"

# 4. Check container health
ssh infra "docker inspect --format='{{.State.Health.Status}}' local-infra-mongodb-1"
```

**Resolution:**
```bash
# If container is unhealthy or not running
ssh infra "cd ~/projects/local-infra && docker compose restart mongodb"

# If disk space is full
ssh infra "df -h"
ssh infra "docker system prune -af"
```

### Issue: SSH "Permission Denied"

**Symptoms:**
- Cannot SSH to host
- Error: "Permission denied (publickey)"

**Diagnosis:**
```bash
# 1. Check if SSH key exists
ls -la ~/.ssh/id_ed25519

# 2. Check SSH config
cat ~/.ssh/config | grep -A 5 infra

# 3. Test SSH with verbose logging
ssh -v infra
```

**Resolution:**
```bash
# 1. Generate SSH key if missing
ssh-keygen -t ed25519 -C "dawiddutoit@mbp"

# 2. Copy key to remote host
ssh-copy-id dawiddutoit@infra.local

# 3. Test connection
ssh infra "echo 'SSH works'"
```

### Issue: Service in Restart Loop

**Symptoms:**
- Container restarts repeatedly
- `docker ps` shows "Restarting"
- Logs show errors

**Diagnosis:**
```bash
# 1. Check restart count
ssh infra "docker inspect --format='{{.RestartCount}}' local-infra-neo4j-1"

# 2. View logs for errors
ssh infra "docker logs --tail 200 local-infra-neo4j-1"

# 3. Check resource constraints
ssh infra "docker stats --no-stream local-infra-neo4j-1"
```

**Resolution:**
```bash
# Common fixes:

# 1. Fix file permissions
ssh infra "docker exec local-infra-neo4j-1 chown -R neo4j:neo4j /data"

# 2. Increase memory limit in docker-compose.yml
ssh infra "cd ~/projects/local-infra && vi docker-compose.yml"
# Edit: mem_limit: 2g -> mem_limit: 4g

# 3. Clear corrupted data
ssh infra "cd ~/projects/local-infra && docker compose down neo4j"
ssh infra "rm -rf /path/to/neo4j/data"
ssh infra "cd ~/projects/local-infra && docker compose up -d neo4j"
```

### Issue: Slow SSH Connections

**Symptoms:**
- SSH takes >5 seconds to connect
- Delay before password prompt or command execution

**Diagnosis:**
```bash
# 1. Test with verbose logging
time ssh -v infra "echo 'test'"

# 2. Check DNS resolution
time nslookup infra.local

# 3. Check SSH config
cat ~/.ssh/config | grep -A 10 infra
```

**Resolution:**
```bash
# Add to ~/.ssh/config
Host infra
  HostName infra.local
  User dawiddutoit
  IdentityFile ~/.ssh/id_ed25519
  GSSAPIAuthentication no
  UseDNS no
  TCPKeepAlive yes
  ServerAliveInterval 60
```

## Advanced Techniques

### Running Complex Commands Remotely

```bash
# Multi-line command with proper escaping
ssh infra << 'EOF'
  cd ~/projects/local-infra
  docker compose ps
  docker compose logs --tail 20 mongodb
EOF

# With variable substitution
SERVICE="mongodb"
ssh infra "cd ~/projects/local-infra && docker compose logs --tail 20 $SERVICE"
```

### Monitoring Services in Real-Time

```bash
# Watch Docker container stats
ssh infra "docker stats"

# Follow logs in real-time
ssh infra "docker logs -f local-infra-mongodb-1"

# Watch port availability
watch -n 2 'nc -z infra.local 27017 && echo "✅ MongoDB" || echo "❌ MongoDB"'
```

### Batch Health Checks

```bash
# Check all critical services
for service in "27017:MongoDB" "3000:Langfuse" "4317:OTLP" "7687:Neo4j"; do
  port="${service%%:*}"
  name="${service##*:}"
  nc -z infra.local $port && echo "✅ $name ($port)" || echo "❌ $name ($port)"
done
```
