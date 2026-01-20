# GitHub Webhook Setup - Examples

Common webhook configurations for different repository types and deployment scenarios.

## Table of Contents

1. [Basic Repository Setup](#basic-repository-setup)
2. [Docker Compose Project](#docker-compose-project)
3. [Static Website](#static-website)
4. [Multi-Branch Deployment](#multi-branch-deployment)
5. [Monorepo Configuration](#monorepo-configuration)
6. [Custom Deploy Scripts](#custom-deploy-scripts)

---

## Basic Repository Setup

### Minimal Hook Configuration

For a simple repository with standard deployment:

```json
{
  "id": "my-project",
  "execute-command": "/scripts/deploy.sh",
  "command-working-directory": "/projects/my-project",
  "pass-arguments-to-command": [
    {
      "source": "payload",
      "name": "repository.full_name"
    }
  ],
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
      }
    ]
  },
  "response-message": "Deployment triggered for my-project"
}
```

### GitHub Configuration

```
Payload URL: https://webhook.temet.ai/hooks/my-project
Content type: application/json
Secret: <WEBHOOK_SECRET from .env>
Events: Just the push event
Active: Checked
```

---

## Docker Compose Project

### Hook for Docker-Based Service

```json
{
  "id": "web-app",
  "execute-command": "/scripts/deploy.sh",
  "command-working-directory": "/projects/web-app",
  "pass-arguments-to-command": [
    {
      "source": "payload",
      "name": "repository.full_name"
    }
  ],
  "pass-environment-to-command": [
    {
      "source": "payload",
      "envname": "COMMIT_SHA",
      "name": "after"
    },
    {
      "source": "payload",
      "envname": "PUSHER",
      "name": "pusher.name"
    }
  ],
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
      }
    ]
  },
  "response-message": "Docker deployment triggered"
}
```

### Enhanced Deploy Script

Create `/projects/web-app/scripts/post-deploy.sh`:

```bash
#!/bin/bash
set -e

echo "Running database migrations..."
docker compose exec -T app python manage.py migrate

echo "Clearing cache..."
docker compose exec -T app python manage.py clearcache

echo "Post-deploy complete"
```

---

## Static Website

### Hook for Static Site Generator

```json
{
  "id": "docs-site",
  "execute-command": "/scripts/deploy-static.sh",
  "command-working-directory": "/projects/docs-site",
  "pass-arguments-to-command": [
    {
      "source": "payload",
      "name": "repository.name"
    }
  ],
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
      }
    ]
  },
  "response-message": "Static site build triggered"
}
```

### Static Site Deploy Script

Create `/home/dawiddutoit/projects/network/scripts/deploy-static.sh`:

```bash
#!/bin/bash
set -e

REPO_NAME="${1:-unknown}"
DEPLOY_LOG="/tmp/deploy-$(date +%Y%m%d-%H%M%S).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$DEPLOY_LOG"
}

log "=== Static site deployment for: $REPO_NAME ==="
log "Working directory: $(pwd)"

# Pull latest changes
log "Pulling latest changes..."
git fetch origin main
git reset --hard origin/main

# Build static site
if [ -f "package.json" ]; then
    log "Building site..."
    npm install --silent
    npm run build
fi

# Copy to web root (adjust path as needed)
if [ -d "dist" ]; then
    log "Deploying to web root..."
    cp -r dist/* /var/www/html/
fi

log "=== Static site deployment complete ==="
```

---

## Multi-Branch Deployment

### Staging and Production Branches

```json
{
  "id": "app-staging",
  "execute-command": "/scripts/deploy-staging.sh",
  "command-working-directory": "/projects/app-staging",
  "pass-arguments-to-command": [
    {
      "source": "payload",
      "name": "repository.full_name"
    }
  ],
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
          "value": "refs/heads/develop",
          "parameter": {
            "source": "payload",
            "name": "ref"
          }
        }
      }
    ]
  },
  "response-message": "Staging deployment triggered"
}
```

```json
{
  "id": "app-production",
  "execute-command": "/scripts/deploy-production.sh",
  "command-working-directory": "/projects/app-production",
  "pass-arguments-to-command": [
    {
      "source": "payload",
      "name": "repository.full_name"
    }
  ],
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
      }
    ]
  },
  "response-message": "Production deployment triggered"
}
```

### GitHub Configuration for Multi-Branch

**Staging webhook:**
```
Payload URL: https://webhook.temet.ai/hooks/app-staging
Events: Push (triggers on all branches, hook filters by ref)
```

**Production webhook:**
```
Payload URL: https://webhook.temet.ai/hooks/app-production
Events: Push
```

---

## Monorepo Configuration

### Separate Hooks per Service

For a monorepo with `/frontend` and `/backend` directories:

```json
{
  "id": "monorepo-frontend",
  "execute-command": "/scripts/deploy-frontend.sh",
  "command-working-directory": "/projects/monorepo/frontend",
  "pass-arguments-to-command": [
    {
      "source": "payload",
      "name": "repository.full_name"
    }
  ],
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
      }
    ]
  },
  "response-message": "Frontend deployment triggered"
}
```

### Smart Deploy Script for Monorepo

Create `/scripts/deploy-monorepo.sh`:

```bash
#!/bin/bash
set -e

REPO_NAME="${1:-unknown}"
CHANGED_FILES="${2:-}"
DEPLOY_LOG="/tmp/deploy-$(date +%Y%m%d-%H%M%S).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$DEPLOY_LOG"
}

log "=== Monorepo deployment for: $REPO_NAME ==="

# Pull latest
git fetch origin main
git reset --hard origin/main

# Get changed files in this push
CHANGED=$(git diff --name-only HEAD~1 HEAD 2>/dev/null || echo "")

# Deploy frontend if changed
if echo "$CHANGED" | grep -q "^frontend/"; then
    log "Frontend changes detected, deploying..."
    cd frontend && npm install && npm run build
    cd ..
fi

# Deploy backend if changed
if echo "$CHANGED" | grep -q "^backend/"; then
    log "Backend changes detected, deploying..."
    cd backend && docker compose up -d --build
    cd ..
fi

log "=== Monorepo deployment complete ==="
```

---

## Custom Deploy Scripts

### Notification on Deploy

```bash
#!/bin/bash
set -e

REPO_NAME="${1:-unknown}"
SLACK_WEBHOOK="https://hooks.slack.com/services/xxx/yyy/zzz"

notify_slack() {
    local message="$1"
    curl -s -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"$message\"}" \
        "$SLACK_WEBHOOK"
}

# Notify start
notify_slack ":rocket: Deploying $REPO_NAME..."

# Standard deployment
git fetch origin main
git reset --hard origin/main

if [ -f "docker-compose.yml" ]; then
    docker compose pull --quiet
    docker compose up -d --remove-orphans
fi

# Notify success
notify_slack ":white_check_mark: $REPO_NAME deployed successfully!"
```

### Deploy with Health Check

```bash
#!/bin/bash
set -e

REPO_NAME="${1:-unknown}"
HEALTH_URL="https://my-service.temet.ai/health"
MAX_RETRIES=10

# Standard deployment
git fetch origin main
git reset --hard origin/main

docker compose pull --quiet
docker compose up -d --remove-orphans

# Wait for health check
echo "Waiting for service to be healthy..."
for i in $(seq 1 $MAX_RETRIES); do
    if curl -sf "$HEALTH_URL" > /dev/null 2>&1; then
        echo "Service is healthy!"
        exit 0
    fi
    echo "Attempt $i/$MAX_RETRIES - waiting..."
    sleep 5
done

echo "ERROR: Service failed health check!"
exit 1
```

### Rollback on Failure

```bash
#!/bin/bash
set -e

REPO_NAME="${1:-unknown}"
PREVIOUS_SHA=$(git rev-parse HEAD)

deploy() {
    git fetch origin main
    git reset --hard origin/main
    docker compose up -d --remove-orphans
}

rollback() {
    echo "Deployment failed, rolling back to $PREVIOUS_SHA..."
    git reset --hard "$PREVIOUS_SHA"
    docker compose up -d --remove-orphans
}

# Attempt deployment
if ! deploy; then
    rollback
    exit 1
fi

# Health check
sleep 10
if ! curl -sf "https://my-service.temet.ai/health" > /dev/null 2>&1; then
    rollback
    exit 1
fi

echo "Deployment successful!"
```

---

## Full hooks.json Example

Complete hooks.json with multiple services:

```json
[
  {
    "id": "health",
    "execute-command": "/bin/echo",
    "command-working-directory": "/",
    "response-message": "OK"
  },
  {
    "id": "local-infra",
    "execute-command": "/scripts/deploy.sh",
    "command-working-directory": "/projects/local-infra",
    "pass-arguments-to-command": [
      {
        "source": "payload",
        "name": "repository.full_name"
      }
    ],
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
        }
      ]
    },
    "response-message": "Deployment triggered for local-infra"
  },
  {
    "id": "network",
    "execute-command": "/scripts/deploy.sh",
    "command-working-directory": "/projects/network",
    "pass-arguments-to-command": [
      {
        "source": "payload",
        "name": "repository.full_name"
      }
    ],
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
        }
      ]
    },
    "response-message": "Deployment triggered for network"
  }
]
```
