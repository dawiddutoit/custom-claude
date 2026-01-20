# GitHub Webhook Setup - Reference Guide

Complete reference for hooks.json schema, webhook container configuration, and troubleshooting.

## Table of Contents

1. [hooks.json Schema](#hooksjson-schema)
2. [Trigger Rules Reference](#trigger-rules-reference)
3. [Webhook Container Configuration](#webhook-container-configuration)
4. [GitHub Webhook Events](#github-webhook-events)
5. [Security Considerations](#security-considerations)
6. [Troubleshooting Guide](#troubleshooting-guide)

---

## hooks.json Schema

### Complete Hook Object

```json
{
  "id": "string (required)",
  "execute-command": "string (required)",
  "command-working-directory": "string (optional)",
  "pass-arguments-to-command": [
    {
      "source": "string",
      "name": "string"
    }
  ],
  "pass-environment-to-command": [
    {
      "source": "string",
      "envname": "string",
      "name": "string"
    }
  ],
  "trigger-rule": {
    "and": [],
    "or": [],
    "not": {},
    "match": {}
  },
  "response-message": "string (optional)",
  "response-headers": [
    {
      "name": "string",
      "value": "string"
    }
  ],
  "include-command-output-in-response": "boolean (default: false)",
  "include-command-output-in-response-on-error": "boolean (default: false)",
  "parse-parameters-as-json": [
    {
      "source": "string",
      "name": "string"
    }
  ]
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier, used in URL path |
| `execute-command` | string | Yes | Command or script to execute |
| `command-working-directory` | string | No | Working directory for command |
| `pass-arguments-to-command` | array | No | Arguments passed to command |
| `pass-environment-to-command` | array | No | Environment variables for command |
| `trigger-rule` | object | No | Conditions that must be met to trigger |
| `response-message` | string | No | Custom response on success |
| `include-command-output-in-response` | boolean | No | Include stdout in response |

### Argument Sources

| Source | Description | Example Name |
|--------|-------------|--------------|
| `payload` | JSON body from request | `repository.full_name` |
| `header` | HTTP request header | `X-GitHub-Event` |
| `query` | URL query parameter | `token` |
| `string` | Literal string value | (use `name` as value) |

### Environment Variable Sources

```json
{
  "source": "payload",
  "envname": "REPO_NAME",
  "name": "repository.full_name"
}
```

This passes `repository.full_name` from payload as `REPO_NAME` env var.

---

## Trigger Rules Reference

### HMAC Signature Verification (Required for GitHub)

```json
{
  "match": {
    "type": "payload-hmac-sha256",
    "secret": "WEBHOOK_SECRET",
    "parameter": {
      "source": "header",
      "name": "X-Hub-Signature-256"
    }
  }
}
```

**Note:** `"secret": "WEBHOOK_SECRET"` references the environment variable, not a literal value.

### Branch Matching

**Main branch only:**
```json
{
  "match": {
    "type": "value",
    "value": "refs/heads/main",
    "parameter": {
      "source": "payload",
      "name": "ref"
    }
  }
}
```

**Multiple branches (using regex):**
```json
{
  "match": {
    "type": "regex",
    "regex": "^refs/heads/(main|master|develop)$",
    "parameter": {
      "source": "payload",
      "name": "ref"
    }
  }
}
```

### Event Type Matching

```json
{
  "match": {
    "type": "value",
    "value": "push",
    "parameter": {
      "source": "header",
      "name": "X-GitHub-Event"
    }
  }
}
```

### Combining Rules

**AND (all must match):**
```json
{
  "and": [
    { "match": { ... } },
    { "match": { ... } }
  ]
}
```

**OR (any must match):**
```json
{
  "or": [
    { "match": { ... } },
    { "match": { ... } }
  ]
}
```

**NOT (must not match):**
```json
{
  "not": {
    "match": { ... }
  }
}
```

### Complete Trigger Example

```json
{
  "trigger-rule": {
    "and": [
      {
        "match": {
          "type": "payload-hmac-sha256",
          "secret": "WEBHOOK_SECRET",
          "parameter": {
            "source": "header",
            "name": "X-Hub-Signature-256"
          }
        }
      },
      {
        "match": {
          "type": "value",
          "value": "refs/heads/main",
          "parameter": {
            "source": "payload",
            "name": "ref"
          }
        }
      },
      {
        "match": {
          "type": "value",
          "value": "push",
          "parameter": {
            "source": "header",
            "name": "X-GitHub-Event"
          }
        }
      }
    ]
  }
}
```

---

## Webhook Container Configuration

### Docker Compose Entry

```yaml
webhook:
  image: almir/webhook:latest
  container_name: webhook
  restart: unless-stopped
  environment:
    - WEBHOOK_SECRET=${WEBHOOK_SECRET}
  volumes:
    - ./config/hooks.json:/etc/webhook/hooks.json:ro
    - ./scripts:/scripts:ro
    - /home/dawiddutoit/projects:/projects
    - /var/run/docker.sock:/var/run/docker.sock
  command: ["-verbose", "-hooks=/etc/webhook/hooks.json", "-hotreload"]
  networks:
    - default
```

### Volume Mounts

| Mount | Purpose |
|-------|---------|
| `/etc/webhook/hooks.json` | Hook configuration |
| `/scripts` | Deploy scripts |
| `/projects` | Project directories |
| `/var/run/docker.sock` | Docker access for deployments |

### Command Flags

| Flag | Description |
|------|-------------|
| `-verbose` | Enable detailed logging |
| `-hooks=PATH` | Path to hooks.json |
| `-hotreload` | Reload hooks.json on change |
| `-port=9000` | Listen port (default 9000) |
| `-ip=""` | Bind address (default all) |

---

## GitHub Webhook Events

### Push Event Payload (Key Fields)

```json
{
  "ref": "refs/heads/main",
  "before": "abc123...",
  "after": "def456...",
  "repository": {
    "id": 12345,
    "name": "repo-name",
    "full_name": "owner/repo-name",
    "private": true,
    "clone_url": "https://github.com/owner/repo-name.git"
  },
  "pusher": {
    "name": "username",
    "email": "user@example.com"
  },
  "sender": {
    "login": "username",
    "id": 67890
  },
  "commits": [
    {
      "id": "def456...",
      "message": "Commit message",
      "author": {
        "name": "Name",
        "email": "email@example.com"
      }
    }
  ],
  "head_commit": {
    "id": "def456...",
    "message": "Latest commit message"
  }
}
```

### Useful Payload Fields for Arguments

| Field Path | Description |
|------------|-------------|
| `ref` | Branch reference (e.g., refs/heads/main) |
| `repository.name` | Repository name |
| `repository.full_name` | owner/repo-name format |
| `repository.clone_url` | Git clone URL |
| `pusher.name` | Username who pushed |
| `head_commit.message` | Latest commit message |
| `commits[0].id` | First commit SHA |

---

## Security Considerations

### Secret Management

**Environment Variable Reference:**
```json
"secret": "WEBHOOK_SECRET"
```
This references the environment variable, NOT a literal secret value. Never put actual secrets in hooks.json.

**Secret Strength:**
```bash
# Generate strong secret (32 bytes = 64 hex chars)
openssl rand -hex 32
```

**Secret Rotation:**
1. Generate new secret: `openssl rand -hex 32`
2. Update GitHub webhook with new secret
3. Update .env with new WEBHOOK_SECRET
4. Restart webhook container: `docker compose restart webhook`
5. Test with a push event

### Network Security

**Cloudflare Access Bypass:**
- webhook.temet.ai has bypass policy (no authentication)
- This is required for GitHub to deliver webhooks
- Security relies on HMAC signature verification

**IP Allowlisting (Optional):**
GitHub webhook IPs can be retrieved from: https://api.github.com/meta
Look for the `hooks` array.

### Audit Trail

All webhook deliveries are logged:
- GitHub: Settings -> Webhooks -> Recent Deliveries
- Server: `docker logs webhook`
- Deployments: `/tmp/deploy-*.log`

---

## Troubleshooting Guide

### Error: 404 Not Found

**Symptoms:**
- GitHub shows 404 for webhook delivery
- curl to endpoint returns 404

**Causes and Fixes:**

| Cause | Fix |
|-------|-----|
| Hook ID not in hooks.json | Add hook entry with correct ID |
| hooks.json syntax error | Validate JSON: `cat hooks.json \| jq .` |
| Webhook container not running | `docker compose up -d webhook` |
| Wrong URL path | Check URL is `/hooks/<id>` not `/<id>` |

### Error: 401/403 Unauthorized

**Symptoms:**
- GitHub shows 401 or 403
- "signature does not match" in webhook logs

**Causes and Fixes:**

| Cause | Fix |
|-------|-----|
| Secret mismatch | Ensure GitHub secret matches .env WEBHOOK_SECRET |
| Environment variable not set | Check: `docker exec webhook env \| grep WEBHOOK` |
| Container not restarted | `docker compose restart webhook` |
| Whitespace in secret | Re-copy secret without trailing spaces |

### Error: Webhook Triggered but Deployment Fails

**Symptoms:**
- GitHub shows 200 OK
- webhook logs show "got matched"
- But code not updated

**Diagnostic Steps:**

```bash
# 1. Check webhook received and matched
docker logs webhook --tail 30

# 2. Check deployment script executed
ls -la /tmp/deploy-*.log | tail -3
cat $(ls -t /tmp/deploy-*.log | head -1)

# 3. Check working directory exists
ls -la /projects/<repo-name>

# 4. Check git can pull
cd /projects/<repo-name> && git status

# 5. Check docker permissions
docker ps
```

**Common Causes:**

| Issue | Fix |
|-------|-----|
| Directory doesn't exist | Clone repo to /projects/<repo-name> |
| Git authentication | Configure SSH key or credential helper |
| Docker permission denied | Add docker.sock mount to webhook container |
| Script not executable | `chmod +x scripts/deploy.sh` |

### Error: Timeout

**Symptoms:**
- GitHub shows timeout error
- Deployment takes too long

**Fixes:**
1. Make deploy.sh faster (use `--quiet` flags)
2. Increase timeout in GitHub webhook settings
3. Run long tasks asynchronously (background job)

### Verification Commands

```bash
# Check webhook container is running
docker ps | grep webhook

# View webhook container logs
docker logs webhook --tail 50

# Test health endpoint
curl -v https://webhook.temet.ai/hooks/health

# Validate hooks.json syntax
cat /home/dawiddutoit/projects/network/config/hooks.json | jq .

# Check environment variable is set
docker exec webhook env | grep WEBHOOK_SECRET

# List configured hooks
cat /home/dawiddutoit/projects/network/config/hooks.json | jq '.[].id'

# Simulate webhook delivery (for testing)
curl -X POST https://webhook.temet.ai/hooks/<hook-id> \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -H "X-Hub-Signature-256: sha256=<computed-signature>" \
  -d '{"ref": "refs/heads/main", "repository": {"full_name": "test/repo"}}'
```

### Computing Test Signature

```bash
SECRET="your-webhook-secret"
PAYLOAD='{"ref":"refs/heads/main","repository":{"full_name":"test/repo"}}'
echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET"
```

Use the output prefixed with `sha256=` in the X-Hub-Signature-256 header.
