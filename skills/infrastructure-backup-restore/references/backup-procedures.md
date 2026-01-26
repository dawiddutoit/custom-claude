# Infrastructure Backup and Restore Procedures

Comprehensive backup and restoration procedures for network infrastructure.

## Table of Contents

1. [Backup Procedures](#backup-procedures)
2. [Restore Procedures](#restore-procedures)
3. [Disaster Recovery](#disaster-recovery)
4. [Backup Management](#backup-management)
5. [Security and Encryption](#security-and-encryption)

## Backup Procedures

### Full Infrastructure Backup with Manifest

```bash
# Set backup directory
backup_dir="/home/dawiddutoit/projects/network/backups/full-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup_dir"

echo "Creating full infrastructure backup..."
echo "Backup location: $backup_dir"

# Backup Pi-hole data
echo "Backing up Pi-hole data..."
tar -czf "$backup_dir/pihole_data.tar.gz" \
  -C /var/lib/docker/volumes/network_pihole_data/_data .

# Backup Caddy data (certificates)
echo "Backing up Caddy certificates..."
tar -czf "$backup_dir/caddy_data.tar.gz" \
  -C /var/lib/docker/volumes/network_caddy_data/_data .

# Backup configuration files
echo "Backing up configuration files..."
cp /home/dawiddutoit/projects/network/docker-compose.yml "$backup_dir/"
cp /home/dawiddutoit/projects/network/domains.toml "$backup_dir/"
cp -r /home/dawiddutoit/projects/network/caddy "$backup_dir/"
cp -r /home/dawiddutoit/projects/network/config "$backup_dir/"
cp -r /home/dawiddutoit/projects/network/scripts "$backup_dir/"

# Backup .env (SENSITIVE - secure this!)
echo "Backing up .env secrets..."
cp /home/dawiddutoit/projects/network/.env "$backup_dir/.env"

# Backup systemd services
echo "Backing up systemd services..."
mkdir -p "$backup_dir/systemd"
cp /etc/systemd/system/infrastructure-monitor.* "$backup_dir/systemd/" 2>/dev/null || true

# Create backup manifest
cat > "$backup_dir/MANIFEST.txt" << EOF
Infrastructure Backup Manifest
Created: $(date)
Hostname: $(hostname)
User: $(whoami)

Contents:
- pihole_data.tar.gz (Pi-hole configuration and data)
- caddy_data.tar.gz (Caddy certificates and data)
- docker-compose.yml (Service definitions)
- domains.toml (Domain configuration)
- caddy/ (Caddyfile and Dockerfile)
- config/ (Webhook and Caddy configs)
- scripts/ (Management scripts)
- .env (SENSITIVE - all secrets and tokens)
- systemd/ (Monitoring service files)

⚠️  SECURITY WARNING:
This backup contains sensitive data:
- API tokens (Cloudflare, Google OAuth)
- Passwords (Pi-hole)
- Webhook secrets
- Access tokens

Store securely and encrypt for off-site storage.
EOF

# Show backup summary
echo ""
echo "✅ Backup completed successfully!"
echo "Location: $backup_dir"
echo ""
echo "Backup contents:"
ls -lh "$backup_dir"
echo ""
echo "Total size: $(du -sh "$backup_dir" | cut -f1)"
```

### Backup Individual Docker Volumes

```bash
backup_dir="/home/dawiddutoit/projects/network/backups"
mkdir -p "$backup_dir"

# Backup Pi-hole data
echo "Backing up Pi-hole data..."
tar -czf "$backup_dir/pihole-backup-$(date +%Y%m%d).tar.gz" \
  -C /var/lib/docker/volumes/network_pihole_data/_data .

# Backup Caddy certificates
echo "Backing up Caddy certificates..."
tar -czf "$backup_dir/caddy-backup-$(date +%Y%m%d).tar.gz" \
  -C /var/lib/docker/volumes/network_caddy_data/_data .

echo "Volume backups completed"
ls -lh "$backup_dir"/*-backup-$(date +%Y%m%d).tar.gz
```

**Note on Caddy certificates:**
- Certificates can be re-obtained automatically via DNS-01 challenge
- Backup not strictly necessary if Cloudflare API token is valid
- Useful for immediate restoration without waiting for ACME

### Backup Configuration Files Only

```bash
backup_dir="/home/dawiddutoit/projects/network/backups/config-$(date +%Y%m%d)"
mkdir -p "$backup_dir"

# Backup configuration
tar -czf "$backup_dir/network-config.tar.gz" \
  -C /home/dawiddutoit/projects/network \
  docker-compose.yml domains.toml caddy/ config/ scripts/ .env

echo "Configuration backup completed: $backup_dir/network-config.tar.gz"
```

## Restore Procedures

### Restore Specific Components

**Restore only Pi-hole data:**

```bash
backup_file="/home/dawiddutoit/projects/network/backups/pihole-backup-20260120.tar.gz"

# Stop Pi-hole
docker compose -f /home/dawiddutoit/projects/network/docker-compose.yml down pihole

# Restore volume
docker volume rm network_pihole_data
docker volume create network_pihole_data
tar -xzf "$backup_file" \
  -C /var/lib/docker/volumes/network_pihole_data/_data

# Start Pi-hole
docker compose -f /home/dawiddutoit/projects/network/docker-compose.yml up -d pihole

echo "Pi-hole data restored"
```

**Restore only Caddy certificates:**

```bash
backup_file="/home/dawiddutoit/projects/network/backups/caddy-backup-20260120.tar.gz"

# Stop Caddy
docker compose -f /home/dawiddutoit/projects/network/docker-compose.yml down caddy

# Restore volume
docker volume rm network_caddy_data
docker volume create network_caddy_data
tar -xzf "$backup_file" \
  -C /var/lib/docker/volumes/network_caddy_data/_data

# Start Caddy
docker compose -f /home/dawiddutoit/projects/network/docker-compose.yml up -d caddy

echo "Caddy certificates restored"
```

**Restore only configuration:**

```bash
backup_file="/home/dawiddutoit/projects/network/backups/config-20260120/network-config.tar.gz"

# Extract to project directory
tar -xzf "$backup_file" \
  -C /home/dawiddutoit/projects/network

# Restart services to pick up changes
docker compose -f /home/dawiddutoit/projects/network/docker-compose.yml restart

echo "Configuration restored"
```

## Disaster Recovery

### Complete Rebuild from Scratch

**Scenario:** New server, fresh OS, need to restore infrastructure

**Step 1: Install Docker**

```bash
# Install Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin -y
```

**Step 2: Restore Project Directory**

```bash
# Create project directory
mkdir -p /home/dawiddutoit/projects/network
cd /home/dawiddutoit/projects/network

# Extract backup
backup_dir="/path/to/backup/full-backup-20260120-143000"
cp -r "$backup_dir"/* .
```

**Step 3: Restore Docker Volumes**

```bash
# Create volumes
docker volume create network_pihole_data
docker volume create network_caddy_data

# Restore Pi-hole data
tar -xzf pihole_data.tar.gz \
  -C /var/lib/docker/volumes/network_pihole_data/_data

# Restore Caddy certificates
tar -xzf caddy_data.tar.gz \
  -C /var/lib/docker/volumes/network_caddy_data/_data
```

**Step 4: Restore Systemd Services**

```bash
# Copy systemd service files
sudo cp systemd/infrastructure-monitor.* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now infrastructure-monitor.timer
```

**Step 5: Start Services**

```bash
# Start all services
docker compose up -d

# Monitor startup
docker compose logs -f
```

**Step 6: Verify Recovery**

```bash
# Check all services running
docker compose ps

# Test DNS
dig @192.168.68.136 pihole.temet.ai

# Test HTTPS
curl -I https://pihole.temet.ai

# Test tunnel
docker logs cloudflared | grep "Registered tunnel"

# Run health check
./scripts/health-check.sh
```

**Recovery time:** 15-30 minutes depending on internet speed

## Backup Management

### Retention Policy

```bash
backup_base="/home/dawiddutoit/projects/network/backups"

# Keep last 7 daily backups
find "$backup_base" -name "full-backup-*" -mtime +7 -delete

# Keep last 3 monthly backups (first of month)
# Manual: Review and delete old monthly backups

# Always keep latest full backup
```

### Automated Backup Script

```bash
#!/bin/bash
# /home/dawiddutoit/projects/network/scripts/backup-infrastructure.sh

backup_dir="/home/dawiddutoit/projects/network/backups/auto-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup_dir"

# Backup volumes
tar -czf "$backup_dir/pihole_data.tar.gz" \
  -C /var/lib/docker/volumes/network_pihole_data/_data .
tar -czf "$backup_dir/caddy_data.tar.gz" \
  -C /var/lib/docker/volumes/network_caddy_data/_data .

# Backup configuration
cp /home/dawiddutoit/projects/network/.env "$backup_dir/.env"
cp /home/dawiddutoit/projects/network/docker-compose.yml "$backup_dir/"
cp /home/dawiddutoit/projects/network/domains.toml "$backup_dir/"

# Delete backups older than 7 days
find /home/dawiddutoit/projects/network/backups -name "auto-*" -mtime +7 -delete

echo "Backup completed: $backup_dir"
```

### Schedule with Cron

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /home/dawiddutoit/projects/network/scripts/backup-infrastructure.sh >> /var/log/infrastructure-backup.log 2>&1
```

## Security and Encryption

### Encrypt Backup for Off-Site Storage

```bash
# Encrypt backup for off-site storage
backup_file="/home/dawiddutoit/projects/network/backups/full-backup-20260120.tar.gz"

tar -czf - /path/to/backup | \
  gpg --symmetric --cipher-algo AES256 > backup-encrypted.tar.gz.gpg

# Upload to cloud storage (example)
# rclone copy backup-encrypted.tar.gz.gpg remote:backups/
```

### Security Considerations

**What's sensitive in backups:**
- .env file (API tokens, passwords, secrets)
- Pi-hole configuration (may contain internal hostnames)
- Caddy certificates (private keys)

**Protection measures:**
- Never commit backups to git
- Use encryption for off-site storage
- Restrict file permissions (600 for .env)
- Store encrypted backups in separate location
- Rotate off-site backups regularly

### Backup Verification

```bash
# Verify backup integrity
backup_dir="/home/dawiddutoit/projects/network/backups/full-backup-20260120"

# Check all expected files exist
expected_files=(
  "pihole_data.tar.gz"
  "caddy_data.tar.gz"
  "docker-compose.yml"
  ".env"
  "MANIFEST.txt"
)

for file in "${expected_files[@]}"; do
  if [ -f "$backup_dir/$file" ]; then
    echo "✅ $file"
  else
    echo "❌ Missing: $file"
  fi
done

# Verify tar archives are not corrupted
tar -tzf "$backup_dir/pihole_data.tar.gz" > /dev/null && echo "✅ pihole_data.tar.gz OK"
tar -tzf "$backup_dir/caddy_data.tar.gz" > /dev/null && echo "✅ caddy_data.tar.gz OK"
```
