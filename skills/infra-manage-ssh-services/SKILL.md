---
name: infra-manage-ssh-services
description: |
  Discover, test, and manage remote SSH infrastructure hosts and Docker services across
  5 hosts (infra.local, deus, homeassistant, pi4-motor, armitage). Use when checking
  infrastructure status, verifying service connectivity, managing Docker containers,
  troubleshooting remote services, or before using remote resources (MongoDB, Langfuse,
  OTLP, Neo4j). Triggers on "check infrastructure", "connect to infra/deus/ha",
  "test MongoDB on infra", "view Docker services", "verify connectivity", "troubleshoot
  remote service", "what services are running", or when remote connections fail. Works
  with SSH commands, Docker remote management, and infrastructure health checks.
allowed-tools:
  - Read
  - Bash
---

# Infrastructure SSH Service Management

## Quick Start

**Discover available infrastructure:**
```bash
# List all hosts and their status
ping -c 1 -W 1 infra.local && echo "✅ infra.local (primary)" || echo "❌ infra.local"
ping -c 1 -W 1 192.168.68.135 && echo "✅ deus (development)" || echo "❌ deus"
ping -c 1 -W 1 homeassistant.local && echo "✅ homeassistant.local" || echo "❌ homeassistant.local"
```

**Check primary infrastructure services:**
```bash
# View all running Docker services on infra.local
ssh infra "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

# Quick MongoDB health check (MongoDB 4.4 uses 'mongo' not 'mongosh')
ssh infra "docker exec local-infra-mongodb-1 mongo off --quiet --eval 'db.runCommand({ping: 1})'" 2>/dev/null
```

**Before using remote MongoDB (NomNom project):**
```bash
# Verify MongoDB is accessible
nc -z infra.local 27017 && echo "✅ MongoDB port open" || echo "❌ MongoDB unreachable"
```

## Connection Reference

**To connect to infra.local, you have three equivalent options:**

```bash
# Option 1: Use the connect function (recommended)
connect infra

# Option 2: Use the SSH alias from ~/.ssh/config
ssh infra

# Option 3: Use the full hostname
ssh dawiddutoit@infra.local
```

**All three commands do the same thing:**
- Connect to `infra.local`
- Authenticate as user `dawiddutoit`
- Use SSH key `~/.ssh/id_ed25519`

**First-time setup (if SSH key not yet copied):**
```bash
connect infra --setup
# This copies your SSH public key to infra.local for passwordless authentication
```

**For other hosts:**
```bash
connect deus        # or: ssh deus        # or: ssh dawiddutoit@192.168.68.135
connect ha          # or: ssh ha          # or: ssh root@homeassistant.local
connect motor       # or: ssh motor       # or: ssh dawiddutoit@pi4-motor.local
connect armitage    # or: ssh unit@armitage.local
```

**Running commands on infra.local (without interactive shell):**
```bash
# Execute single command
ssh infra "docker ps"

# Execute multiple commands
ssh infra "cd ~/projects/local-infra && docker compose ps"

# Chain commands
ssh infra "docker ps -f name=mongodb && docker logs --tail 10 local-infra-mongodb-1"
```

## Table of Contents

1. [When to Use This Skill](#when-to-use-this-skill)
2. [What This Skill Does](#what-this-skill-does)
3. [Instructions](#instructions)
   - 3.1 [Discovery Phase - Find Available Hosts and Services](#31-discovery-phase)
   - 3.2 [Health Check Phase - Verify Connectivity](#32-health-check-phase)
   - 3.3 [Execution Phase - Manage Services](#33-execution-phase)
4. [Supporting Files](#supporting-files)
5. [Common Workflows](#common-workflows)
6. [Expected Outcomes](#expected-outcomes)
7. [Integration Points](#integration-points)
8. [Expected Benefits](#expected-benefits)
9. [Requirements](#requirements)
10. [Red Flags to Avoid](#red-flags-to-avoid)

## When to Use This Skill

### Explicit Triggers (User Requests)
- "Check infrastructure status"
- "Connect to infra/deus/ha"
- "View Docker services on infra"
- "Test MongoDB connectivity"
- "What services are running on infra.local?"
- "Troubleshoot remote MongoDB connection"
- "Check Langfuse status"
- "View OTLP collector logs"

### Implicit Triggers (Contextual Needs)
- Before using remote MongoDB in NomNom project
- When remote service connection fails (MongoDB, Neo4j, Langfuse)
- Before starting development session that uses remote resources
- When planning to use OpenTelemetry/Langfuse observability
- When investigating service availability for integration work

### Debugging/Troubleshooting Triggers
- Connection refused errors to infra.local services
- MongoDB ServerSelectionTimeoutError
- SSH authentication failures
- Docker container not responding
- Service appears running but not accessible
- Neo4j or Infinity in restart loop

## What This Skill Does

This skill provides systematic workflows for:

1. **Service Discovery** - Identify available hosts (5 total) and running services (16+ on infra.local)
2. **Connectivity Testing** - Verify network reachability, port availability, SSH access
3. **Docker Management** - View, restart, and monitor remote Docker containers
4. **Health Verification** - Check service health status and logs
5. **Troubleshooting** - Diagnose connection issues and service failures
6. **Infrastructure Integration** - Ensure remote resources (MongoDB, Langfuse, OTLP) are ready for use

## Instructions

### 3.1 Discovery Phase

**Step 1: Identify Target Host**

Use the `connect` function to determine which host you need:

```bash
# View available hosts
connect
# Output: Hosts: infra, armitage, deus, ha, motor
```

**Infrastructure Inventory:**

| Host | Connection | Status | Primary Services |
|------|------------|--------|------------------|
| **infra.local** | `connect infra` | ✅ Online | MongoDB, Langfuse, OTLP, Jaeger, Neo4j, Infinity, PostgreSQL, Redis, MinIO, Mosquitto, Caddy |
| **deus** | `connect deus` | ✅ Online | None detected (development machine) |
| **homeassistant.local** | `connect ha` | ✅ Online | Home Assistant (port 8123) |
| **pi4-motor.local** | `connect motor` | ❌ Offline | Motor control (Raspberry Pi 4) |
| **armitage.local** | `connect armitage` | ❌ Offline | Neo4j, Infinity Embeddings (WSL2 PC) |

**Step 2: Test Host Reachability**

```bash
# Quick network ping test
ping -c 1 -W 1 infra.local

# Test specific port availability
nc -z infra.local 27017  # MongoDB
nc -z infra.local 3000   # Langfuse
nc -z infra.local 4317   # OTLP Collector
nc -z infra.local 7687   # Neo4j (if not in restart loop)
```

**Step 3: Discover Running Services**

```bash
# View all Docker containers on infra.local
ssh infra "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

# Count running services
ssh infra "docker ps --format '{{.Names}}' | wc -l"

# Check specific service
ssh infra "docker ps -f name=mongodb"
```

### 3.2 Health Check Phase

**Step 1: Verify SSH Connectivity**

```bash
# Test basic SSH connection
ssh infra "echo 'Connection OK'"

# If SSH fails, check SSH agent
ssh-add -l

# Copy SSH key if needed (first-time setup)
connect infra --setup
```

**Step 2: Check Service Health**

```bash
# MongoDB health check
ssh infra "docker inspect --format='{{.State.Health.Status}}' local-infra-mongodb-1"
ssh infra "docker exec local-infra-mongodb-1 mongo off --quiet --eval 'db.runCommand({ping: 1})'"

# Langfuse health check (HTTP)
curl -s -o /dev/null -w "%{http_code}" http://infra.local:3000

# OTLP Collector health check
ssh infra "docker inspect --format='{{.State.Status}}' local-infra-otel-collector-1"

# View container logs for errors
ssh infra "docker logs --tail 50 local-infra-mongodb-1"
```

**Step 3: Verify Application-Level Connectivity**

For **MongoDB** (NomNom project):
```bash
# Test from application environment
cd ~/projects/play/nomnom
python -c "from motor.motor_asyncio import AsyncIOMotorClient; import asyncio; asyncio.run(AsyncIOMotorClient('mongodb://infra.local:27017').admin.command('ping'))" && echo "✅ MongoDB reachable"
```

For **Langfuse**:
```bash
# Check web UI accessibility
curl -I http://infra.local:3000 | grep "HTTP"
```

### 3.3 Execution Phase

**Service Management Commands:**

```bash
# Restart single service
ssh infra "cd ~/projects/local-infra && docker compose restart mongodb"

# Restart all services
ssh infra "cd ~/projects/local-infra && docker compose restart"

# Stop service
ssh infra "cd ~/projects/local-infra && docker compose stop mongodb"

# Start service
ssh infra "cd ~/projects/local-infra && docker compose up -d mongodb"

# View Docker Compose configuration
ssh infra "cd ~/projects/local-infra && docker compose config"
```

**Monitoring Commands:**

```bash
# Follow logs in real-time
ssh infra "docker logs -f local-infra-mongodb-1"

# View last 100 lines
ssh infra "docker logs --tail 100 local-infra-langfuse-web-1"

# View logs for all services
ssh infra "cd ~/projects/local-infra && docker compose logs -f"

# Check resource usage
ssh infra "docker stats --no-stream"
```

**File Synchronization:**

```bash
# Push file to infra.local
syncpi push ~/path/to/file

# Pull file from infra.local
syncpi pull ~/path/to/file

# Sync zsh configuration
syncpi zsh push
syncpi zsh pull
```

## Supporting Files

### references/infrastructure_guide.md

**Complete infrastructure documentation** - Read this for:
- Detailed service inventory with ports and URLs
- Environment variable mappings
- Docker Compose management on infra.local
- Troubleshooting guides for specific services
- Security notes and credential locations

**When to read:** Before performing any infrastructure operations, when troubleshooting connection issues, or when needing detailed service information.

**Location:** `/Users/dawiddutoit/.claude/artifacts/2026-01-01/infrastructure/SSH_INFRASTRUCTURE_GUIDE.md`

### scripts/health_check.sh

**Quick health check script** - Automated connectivity and service status checks.

**Usage:**
```bash
# Run comprehensive health check
bash /Users/dawiddutoit/.claude/skills/infra-manage-ssh-services/scripts/health_check.sh

# Check specific host
bash /Users/dawiddutoit/.claude/skills/infra-manage-ssh-services/scripts/health_check.sh infra
```

## Common Workflows

### Workflow 1: Starting NomNom Development

**Goal:** Verify MongoDB is ready before starting NomNom backend

```bash
# 1. Check infra.local is reachable
ping -c 1 infra.local || { echo "❌ infra.local unreachable"; exit 1; }

# 2. Verify MongoDB container is running
ssh infra "docker ps -f name=mongodb -q" | grep -q . || { echo "❌ MongoDB not running"; exit 1; }

# 3. Test MongoDB connectivity
nc -z infra.local 27017 || { echo "❌ MongoDB port closed"; exit 1; }

# 4. Verify MongoDB responds to ping
ssh infra "docker exec local-infra-mongodb-1 mongo off --quiet --eval 'db.runCommand({ping: 1})'" 2>/dev/null | grep -q "ok" || { echo "❌ MongoDB not responding"; exit 1; }

# 5. Start NomNom backend
cd ~/projects/play/nomnom && ./start.sh
```

### Workflow 2: Checking Claude Code Telemetry

**Goal:** Verify observability infrastructure is capturing Claude Code sessions

```bash
# 1. Check OTLP Collector is running
ssh infra "docker ps -f name=otel-collector -q" | grep -q . && echo "✅ OTLP Collector running"

# 2. Check Langfuse is accessible
curl -s -o /dev/null -w "%{http_code}" http://infra.local:3000 | grep -q "200" && echo "✅ Langfuse accessible"

# 3. View OTLP logs (last 50 lines)
ssh infra "docker logs --tail 50 local-infra-otel-collector-1"

# 4. Open Langfuse dashboard
open http://infra.local:3000

# 5. Open Jaeger for trace visualization
open http://infra.local:16686
```

### Workflow 3: Troubleshooting Remote Service Connection

**Goal:** Diagnose why a service connection is failing

```bash
# 1. Verify network connectivity
ping -c 3 infra.local || { echo "❌ Network unreachable"; exit 1; }

# 2. Test port availability
nc -z infra.local 27017 || { echo "❌ Port 27017 closed"; exit 1; }

# 3. Check SSH access
ssh infra "echo 'SSH OK'" || { echo "❌ SSH authentication failed"; exit 1; }

# 4. Verify container is running
ssh infra "docker ps -f name=mongodb"

# 5. Check container health
ssh infra "docker inspect --format='{{.State.Health.Status}}' local-infra-mongodb-1"

# 6. View container logs for errors
ssh infra "docker logs --tail 100 local-infra-mongodb-1"

# 7. Restart container if unhealthy
ssh infra "cd ~/projects/local-infra && docker compose restart mongodb"

# 8. Wait 10 seconds and verify
sleep 10 && ssh infra "docker inspect --format='{{.State.Health.Status}}' local-infra-mongodb-1"
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

## Integration Points

### With NomNom Project

**MongoDB dependency verification:**
```bash
# Before ./start.sh in NomNom, verify:
nc -z infra.local 27017 || { echo "❌ Run 'connect infra' and check MongoDB"; exit 1; }
```

**Environment variables:**
```env
MONGODB_URL=mongodb://infra.local:27017
MONGODB_DATABASE=off
```

### With Observability Skills

**Before using observability skills:**
```bash
# Verify OTLP Collector is running
ssh infra "docker ps -f name=otel-collector -q" | grep -q . || echo "⚠️ OTLP Collector offline"

# Then use skills:
# - observability-analyze-logs
# - observability-analyze-session-logs
```

### With Home Assistant Skills

**Before using HA skills:**
```bash
# Verify Home Assistant is accessible
curl -s -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" http://192.168.68.123:8123/api/ | grep -q "message" && echo "✅ HA API accessible"

# Then use skills:
# - ha-dashboard-create
# - ha-custom-cards
# - ha-mushroom-cards
```

### With Quality Gates

**Infrastructure verification as quality gate:**
```bash
# Add to pre-start checks
if ! nc -z infra.local 27017; then
  echo "❌ QUALITY GATE FAILED: MongoDB unreachable"
  echo "Run: ssh infra 'cd ~/projects/local-infra && docker compose restart mongodb'"
  exit 1
fi
```

## Expected Benefits

| Metric | Before Skill | After Skill | Improvement |
|--------|--------------|-------------|-------------|
| **Discovery Time** | 5-10 min (manual SSH, guessing) | 30 sec (automated checks) | 10-20x faster |
| **Troubleshooting Time** | 10-30 min (trial and error) | 2-5 min (systematic workflow) | 5-6x faster |
| **Connection Failures** | 30-40% (no verification) | <5% (proactive health checks) | 6-8x reduction |
| **Service Availability Awareness** | Unknown until failure | Real-time status | Proactive visibility |
| **Documentation Access** | Search files, guess locations | Single skill reference | Immediate context |

## Success Metrics

1. **Discovery Success Rate** - Can identify all online hosts and services in <30 seconds
2. **Health Check Coverage** - Verify critical services (MongoDB, Langfuse, OTLP) before use
3. **Troubleshooting Efficiency** - Resolve 80% of connection issues within 5 minutes
4. **Proactive Usage** - Check infrastructure before remote operations (NomNom, observability)
5. **Zero Surprise Failures** - No "connection refused" errors due to unchecked infrastructure

## Requirements

### Tools
- Bash (for SSH commands and connectivity tests)
- Read (for comprehensive infrastructure guide)

### Environment
- SSH access to remote hosts (via `~/.ssh/config`)
- SSH keys configured (use `connect <host> --setup` if needed)
- Network connectivity to infra.local (primary), deus, homeassistant.local
- `connect` function in `~/.zshrc` (lines 290-306)
- Optional: `syncpi` function for file synchronization

### Knowledge
- Basic SSH command syntax
- Understanding of Docker and Docker Compose
- Familiarity with port-based service discovery (nc, curl)
- Environment variables for service endpoints

## Utility Scripts

### scripts/health_check.sh

**Purpose:** Run comprehensive health checks across all infrastructure hosts

**Usage:**
```bash
# Check all hosts
bash /Users/dawiddutoit/.claude/skills/infra-manage-ssh-services/scripts/health_check.sh

# Check specific host
bash /Users/dawiddutoit/.claude/skills/infra-manage-ssh-services/scripts/health_check.sh infra

# Verbose output
bash /Users/dawiddutoit/.claude/skills/infra-manage-ssh-services/scripts/health_check.sh --verbose
```

**Checks performed:**
1. Network reachability (ping)
2. SSH connectivity
3. Docker daemon status
4. Container health for critical services
5. Port availability for key services
6. Service-specific health endpoints

## Red Flags to Avoid

1. **Assuming local MongoDB** - MongoDB runs on infra.local, NOT localhost
2. **Skipping connectivity checks** - Always verify before using remote services
3. **Ignoring offline hosts** - armitage.local and pi4-motor.local are offline (environment variables may point to them)
4. **Missing SSH key setup** - Run `connect <host> --setup` on first use
5. **Not checking container health** - Container "Up" ≠ healthy (use `docker inspect` for health)
6. **Hardcoding IPs** - Use hostnames (infra.local, homeassistant.local) for mDNS resolution
7. **Ignoring restart loops** - Neo4j and Infinity are restarting on infra.local (check logs)
8. **Skipping logs when debugging** - Always view logs before restarting services
9. **Not testing ports** - Use `nc -z` to verify port availability before connection attempts
10. **Missing Docker Compose context** - Always `cd ~/projects/local-infra` before Docker Compose commands

## Notes

**Key Infrastructure Facts:**

- **Primary Host:** infra.local (16+ services, always online)
- **MongoDB:** 632K OpenFoodFacts products already imported
- **Telemetry:** All Claude Code sessions automatically send OTLP to infra.local:4317
- **Offline Services:** Neo4j and Infinity Embeddings in restart loop on infra.local
- **Alternative Endpoints:** armitage.local has Neo4j/Infinity but is currently offline
- **Home Assistant:** Separate host with 16 related skills in ~/.claude/skills/

**Environment Variable Locations:**
- SSH config: `~/.ssh/config`
- Secrets: `~/.zshrc` (lines 366-540)
- Project .env: `~/projects/play/nomnom/.env` (MongoDB URL)

**Related Documentation:**
- Complete infrastructure guide: `/Users/dawiddutoit/.claude/artifacts/2026-01-01/infrastructure/SSH_INFRASTRUCTURE_GUIDE.md`
- NomNom MongoDB setup: `/Users/dawiddutoit/projects/play/nomnom/CLAUDE.md` (lines 224-235)
- Observability skills: `~/.claude/CLAUDE.md` (search "observability-*")
- Home Assistant skills: `~/.claude/CLAUDE.md` (search "ha-*")
