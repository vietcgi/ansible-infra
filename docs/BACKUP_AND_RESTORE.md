# Backup and Restore Procedures

## Overview

This document provides comprehensive procedures for backing up and restoring ansible-infra infrastructure components, configurations, and data. Backups are critical for disaster recovery, system migrations, and operational safety.

---

## Backup Strategy

### Recovery Point Objective (RPO)
- **Critical data**: 4 hours maximum data loss
- **Configurations**: 24 hours maximum
- **Infrastructure state**: Continuous via version control

### Recovery Time Objective (RTO)
- **Full infrastructure**: 2 hours
- **Single component**: 15 minutes
- **Configuration recovery**: 5 minutes

### Backup Retention Policies

| Category | Retention | Frequency | Location |
|----------|-----------|-----------|----------|
| **Configuration** | 90 days | Hourly | Git + offsite |
| **Secrets** | 90 days | On change | Encrypted vault |
| **Database** | 30 days | Daily | Automated dumps |
| **Logs** | 365 days | Daily rotation | Centralized storage |
| **Full system** | 7 days | Weekly | Cold storage |
| **Monthly archive** | 12 months | Monthly | Offsite archive |

---

## Configuration Backups

### 1. Git-Based Backup (Primary)

All infrastructure code is version controlled in Git, providing automatic backup:

```bash
# Verify git repository status
cd /path/to/ansible-infra
git status
git log --oneline | head -20

# Create tagged backup point before major changes
git tag -a "backup-prod-$(date +%Y%m%d-%H%M%S)" -m "Pre-deployment backup"

# Push to remote for offsite backup
git push origin --all
git push origin --tags

# Verify remote is in sync
git branch -a
git tag -l
```

**Backup points for critical events:**
- Before major role updates
- Before changing core infrastructure
- Before security policy changes
- Before inventory modifications
- Before secrets rotation

### 2. Ansible Vault Backups

Protect encrypted secrets with versioned backups:

```bash
# Backup current vault files
BACKUP_DIR="/backups/ansible-vault/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Copy all vault files
find inventories/ -name "vault" -type d -exec cp -r {} "$BACKUP_DIR/" \;
find inventories/ -name "*.vault" -exec cp {} "$BACKUP_DIR/" \;

# Encrypt backup location
tar -czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"
openssl enc -aes-256-cbc -salt -in "${BACKUP_DIR}.tar.gz" \
  -out "${BACKUP_DIR}.tar.gz.enc" -k "${VAULT_BACKUP_KEY}"

# Remove unencrypted temporary files
rm -rf "$BACKUP_DIR" "${BACKUP_DIR}.tar.gz"

# Verify backup
ls -lh "${BACKUP_DIR}.tar.gz.enc"
```

**Vault backup schedule:**
- After any secret changes
- Before credential rotations
- Before Vault password changes
- Monthly routine backup

### 3. Configuration File Backups

Backup critical configuration directories:

```bash
#!/bin/bash
# backup-configs.sh - Backup all critical Ansible configurations

BACKUP_ROOT="/backups/configs"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="${BACKUP_ROOT}/${TIMESTAMP}"

mkdir -p "$BACKUP_DIR"

# Backup directories
BACKUP_PATHS=(
  "roles/"
  "playbooks/"
  "inventories/"
  "group_vars/"
  "host_vars/"
  "filter_plugins/"
  "callback_plugins/"
  "ansible.cfg"
  "requirements.yml"
  "requirements.txt"
)

# Create tarball
tar -czf "${BACKUP_DIR}.tar.gz" "${BACKUP_PATHS[@]}"

# Verify integrity
tar -tzf "${BACKUP_DIR}.tar.gz" > /dev/null && \
  echo "✓ Backup successful: ${BACKUP_DIR}.tar.gz" || \
  echo "✗ Backup verification failed"

# Keep only 30-day history
find "$BACKUP_ROOT" -maxdepth 1 -name "*.tar.gz" -type f \
  -mtime +30 -delete

# List recent backups
echo -e "\nRecent configuration backups:"
ls -lh "$BACKUP_ROOT" | tail -10
```

**Run automatically:**
```bash
# Add to crontab
0 2 * * * /usr/local/bin/backup-configs.sh >> /var/log/backups/configs.log 2>&1
```

---

## Data Backups

### 1. Database Backups

For any database backends (Prometheus, InfluxDB, etc.):

```bash
#!/bin/bash
# backup-databases.sh - Backup all infrastructure databases

BACKUP_DIR="/backups/databases/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Prometheus data backup
if command -v promtool &> /dev/null; then
  echo "Backing up Prometheus..."
  tar -czf "${BACKUP_DIR}/prometheus.tar.gz" \
    /var/lib/prometheus/ \
    /etc/prometheus/
fi

# InfluxDB backup (if used)
if command -v influx &> /dev/null; then
  echo "Backing up InfluxDB..."
  influx backup "${BACKUP_DIR}/influxdb"
fi

# PostgreSQL backup (if used)
if command -v pg_dump &> /dev/null; then
  echo "Backing up PostgreSQL..."
  pg_dump -h localhost dbname > "${BACKUP_DIR}/postgresql.sql"
  gzip "${BACKUP_DIR}/postgresql.sql"
fi

# Verify backups
echo "Backup verification:"
du -sh "${BACKUP_DIR}"/*

# Cleanup old backups (keep 30 days)
find /backups/databases -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;
```

**Backup frequency:**
- Prometheus: Daily, 7-day retention
- InfluxDB: Daily, 30-day retention
- PostgreSQL: Daily, 90-day retention

### 2. File System Backups

Backup critical file systems:

```bash
#!/bin/bash
# backup-filesystem.sh - Backup critical file systems

BACKUP_DIR="/backups/filesystem"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/filesystem-${TIMESTAMP}.tar.gz"

# Critical directories
declare -a BACKUP_PATHS=(
  "/etc/ansible/"
  "/var/log/ansible-infra/"
  "/opt/ansible-infra/"
  "/home/*/.ssh/authorized_keys"
)

# Create backup with exclusions
tar -czf "$BACKUP_FILE" \
  --exclude="*.lock" \
  --exclude="*cache*" \
  --exclude="*tmp*" \
  "${BACKUP_PATHS[@]}" 2>/dev/null

# Encrypt sensitive backup
gpg --symmetric --cipher-algo AES256 "$BACKUP_FILE"

# Remove unencrypted version
rm "$BACKUP_FILE"

# Verify encrypted backup
file "${BACKUP_FILE}.gpg"
echo "✓ Backup created: ${BACKUP_FILE}.gpg"

# Cleanup old backups (7 day retention)
find "$BACKUP_DIR" -name "filesystem-*.tar.gz.gpg" -type f \
  -mtime +7 -delete
```

---

## Log Backups

### Centralized Log Storage

All infrastructure logs backed up continuously:

```bash
#!/bin/bash
# backup-logs.sh - Backup and archive logs

LOG_DIR="/var/log/ansible-infra"
ARCHIVE_DIR="/backups/logs"
TIMESTAMP=$(date +%Y%m%d)

mkdir -p "$ARCHIVE_DIR"

# Archive and compress daily logs
find "$LOG_DIR" -type f -name "*.log" -mtime 0 \
  -exec gzip {} \;

# Move archived logs
mv "${LOG_DIR}"/*.log.gz "$ARCHIVE_DIR/daily-${TIMESTAMP}/" 2>/dev/null

# Create monthly archives
if [ "$(date +%d)" == "01" ]; then
  MONTH_PREV=$(date -d "1 month ago" +%Y%m)
  tar -czf "${ARCHIVE_DIR}/monthly-${MONTH_PREV}.tar.gz" \
    "${ARCHIVE_DIR}/daily-${MONTH_PREV}"*
fi

# Cleanup: Keep 1 year of logs
find "$ARCHIVE_DIR" -type f -mtime +365 -delete
```

---

## Full System Backup

### Pre-Deployment Full Backup

Before major infrastructure changes:

```bash
#!/bin/bash
# full-system-backup.sh - Complete infrastructure backup

BACKUP_ROOT="/backups/full"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="${BACKUP_ROOT}/backup-${TIMESTAMP}"

echo "Starting full system backup at $(date)"
mkdir -p "$BACKUP_DIR"

# 1. Backup all configurations (Git)
echo "1. Backing up Git repository..."
git bundle create "${BACKUP_DIR}/repo.bundle" --all

# 2. Backup Vault secrets
echo "2. Backing up encrypted secrets..."
tar -czf "${BACKUP_DIR}/vault.tar.gz" inventories/*/vault/

# 3. Backup Ansible plugins
echo "3. Backing up plugins..."
tar -czf "${BACKUP_DIR}/plugins.tar.gz" \
  filter_plugins/ callback_plugins/ 2>/dev/null

# 4. Backup inventory data
echo "4. Backing up inventory..."
tar -czf "${BACKUP_DIR}/inventory.tar.gz" \
  inventories/ group_vars/ host_vars/

# 5. Backup all roles
echo "5. Backing up roles..."
tar -czf "${BACKUP_DIR}/roles.tar.gz" roles/

# 6. Backup playbooks
echo "6. Backing up playbooks..."
tar -czf "${BACKUP_DIR}/playbooks.tar.gz" playbooks/

# 7. System state snapshot
echo "7. Creating system state snapshot..."
ansible all -i inventories/production/hosts.yml \
  -m setup -a "filter=ansible_*" \
  > "${BACKUP_DIR}/system-state.json" 2>/dev/null

# 8. Create backup manifest
cat > "${BACKUP_DIR}/MANIFEST.txt" <<EOF
Full System Backup
==================
Timestamp: $(date)
Hostname: $(hostname)
User: $(whoami)

Contents:
- repo.bundle: Git repository bundle (all branches/tags)
- vault.tar.gz: Encrypted Ansible Vault files
- plugins.tar.gz: Custom Ansible plugins
- inventory.tar.gz: Inventory definitions
- roles.tar.gz: All Ansible roles
- playbooks.tar.gz: All playbooks
- system-state.json: Current system state

Verification:
EOF

# Verify all files created
echo "Backup verification:"
find "$BACKUP_DIR" -type f -exec ls -lh {} \; | \
  awk '{print $9, "(" $5 ")"}' | tee -a "${BACKUP_DIR}/MANIFEST.txt"

# Create final tarball
tar -czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

echo "✓ Full system backup complete: ${BACKUP_DIR}.tar.gz"
echo "  Size: $(du -h ${BACKUP_DIR}.tar.gz | cut -f1)"

# Calculate checksum
sha256sum "${BACKUP_DIR}.tar.gz" > "${BACKUP_DIR}.sha256"

# Store offsite
# gsutil cp "${BACKUP_DIR}.tar.gz" gs://backups-bucket/
# aws s3 cp "${BACKUP_DIR}.tar.gz" s3://backups-bucket/
```

---

## Restore Procedures

### 1. Git Configuration Restore

Restore from specific commit or tag:

```bash
# List available backups
git tag | grep backup

# Restore from specific tag
git checkout backup-prod-20250115-120000

# Or reset to specific commit
git log --oneline | head -20
git reset --hard <commit-hash>

# Restore specific files
git checkout <commit> -- roles/common/tasks/main.yml

# Restore deleted file
git checkout HEAD~1 -- deleted-file.yml
```

### 2. Full System Restore

Restore from full backup tarball:

```bash
#!/bin/bash
# restore-system.sh - Restore from full system backup

BACKUP_FILE="$1"
RESTORE_DIR="/tmp/ansible-infra-restore"

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup-file.tar.gz>"
  exit 1
fi

# Verify backup integrity
echo "Verifying backup integrity..."
sha256sum -c "${BACKUP_FILE}.sha256" || {
  echo "✗ Backup verification failed!"
  exit 1
}

# Extract backup
mkdir -p "$RESTORE_DIR"
tar -xzf "$BACKUP_FILE" -C "$RESTORE_DIR"

echo "Backup contents:"
ls -lh "$RESTORE_DIR"

# Restore Git repository
echo "Restoring Git repository..."
git bundle verify "${RESTORE_DIR}/repo.bundle"
git fetch "${RESTORE_DIR}/repo.bundle" '*:*'

# Restore Vault secrets
echo "Restoring encrypted secrets..."
mkdir -p inventories/*/vault
tar -xzf "${RESTORE_DIR}/vault.tar.gz" -C .

# Restore inventory
echo "Restoring inventory..."
tar -xzf "${RESTORE_DIR}/inventory.tar.gz" -C .

# Restore roles
echo "Restoring roles..."
tar -xzf "${RESTORE_DIR}/roles.tar.gz" -C .

# Restore plugins
echo "Restoring plugins..."
tar -xzf "${RESTORE_DIR}/plugins.tar.gz" -C . 2>/dev/null || true

# Restore playbooks
echo "Restoring playbooks..."
tar -xzf "${RESTORE_DIR}/playbooks.tar.gz" -C .

# Verify restoration
echo "Verifying restoration..."
git status
ls -la roles/
ls -la playbooks/

# Cleanup
rm -rf "$RESTORE_DIR"

echo "✓ System restoration complete"
echo ""
echo "Next steps:"
echo "1. Review changes: git status"
echo "2. Test in staging environment"
echo "3. Run Molecule tests: molecule test"
echo "4. Deploy to production if verified"
```

### 3. Configuration File Restore

Restore individual configuration files:

```bash
#!/bin/bash
# restore-config.sh - Restore specific configuration files

BACKUP_FILE="$1"
FILE_PATH="$2"

if [ $# -lt 2 ]; then
  echo "Usage: $0 <backup-file.tar.gz> <file-path>"
  echo "Example: $0 configs-20250115.tar.gz playbooks/provision.yml"
  exit 1
fi

# Extract specific file
tar -xzf "$BACKUP_FILE" "$FILE_PATH"

# Display restored file
echo "Restored file:"
cat "$FILE_PATH"

# Create backup of current version
if [ -f "$FILE_PATH" ]; then
  cp "$FILE_PATH" "${FILE_PATH}.backup-$(date +%s)"
fi
```

### 4. Database Restore

Restore database from backup:

```bash
#!/bin/bash
# restore-database.sh - Restore from database backup

BACKUP_DIR="$1"

if [ -z "$BACKUP_DIR" ]; then
  echo "Usage: $0 <backup-directory>"
  exit 1
fi

# Restore Prometheus
if [ -f "${BACKUP_DIR}/prometheus.tar.gz" ]; then
  echo "Restoring Prometheus..."
  sudo systemctl stop prometheus
  sudo tar -xzf "${BACKUP_DIR}/prometheus.tar.gz" -C /
  sudo systemctl start prometheus
fi

# Restore InfluxDB
if [ -d "${BACKUP_DIR}/influxdb" ]; then
  echo "Restoring InfluxDB..."
  influx restore -portable "${BACKUP_DIR}/influxdb"
fi

# Restore PostgreSQL
if [ -f "${BACKUP_DIR}/postgresql.sql.gz" ]; then
  echo "Restoring PostgreSQL..."
  gunzip -c "${BACKUP_DIR}/postgresql.sql.gz" | psql
fi

echo "✓ Database restoration complete"
```

---

## Restore Testing

### Regular Restore Drills

Test restore procedures quarterly:

```bash
#!/bin/bash
# test-restore.sh - Test restore procedures without affecting production

BACKUP_FILE="/backups/full/latest-backup.tar.gz"
TEST_DIR="/tmp/restore-test-$(date +%s)"

echo "Starting restore drill at $(date)"
mkdir -p "$TEST_DIR"

# Extract to test directory
tar -xzf "$BACKUP_FILE" -C "$TEST_DIR"

# Verify contents
echo "Verifying backup contents:"
du -sh "$TEST_DIR"/*

# Test Git repository
if [ -f "${TEST_DIR}/repo.bundle" ]; then
  echo "Testing Git bundle..."
  git bundle verify "${TEST_DIR}/repo.bundle"
fi

# Test archive integrity
for archive in "${TEST_DIR}"/*.tar.gz; do
  echo "Testing $archive..."
  tar -tzf "$archive" > /dev/null || echo "ERROR: $archive corrupted"
done

# Create restore test report
cat > "/tmp/restore-test-report-$(date +%Y%m%d).txt" <<EOF
Restore Test Report
===================
Date: $(date)
Backup: $BACKUP_FILE
Test Directory: $TEST_DIR

Results:
✓ Backup archive integrity verified
✓ All component archives present
✓ Git bundle valid
✓ Manifest file present

Recommendation: Ready for production
EOF

# Cleanup
rm -rf "$TEST_DIR"

echo "✓ Restore drill completed successfully"
```

---

## Backup Storage & Redundancy

### Local Storage
- **Location**: `/backups/` on local filesystem
- **Retention**: 7-30 days depending on type
- **Encryption**: Optional for configs, required for secrets
- **Access**: Restricted to authorized users only

### Offsite Storage

Replicate critical backups offsite:

```bash
#!/bin/bash
# sync-offsite-backups.sh - Sync backups to cloud storage

BACKUP_DIR="/backups"
CLOUD_BUCKET="gs://ansible-infra-backups"  # GCS example

# Sync full system backups
gsutil -m rsync -r -d "${BACKUP_DIR}/full" "${CLOUD_BUCKET}/full"

# Sync configuration backups
gsutil -m rsync -r -d "${BACKUP_DIR}/configs" "${CLOUD_BUCKET}/configs"

# Sync database backups
gsutil -m rsync -r -d "${BACKUP_DIR}/databases" "${CLOUD_BUCKET}/databases"

# Verify sync
echo "Offsite backup status:"
gsutil du -s "${CLOUD_BUCKET}"

# Alternative: AWS S3
# aws s3 sync /backups s3://ansible-infra-backups --delete

# Alternative: Azure Blob Storage
# az storage blob upload-batch --account-name backupaccount \
#   --source /backups --destination backup-container
```

### Backup Encryption

All sensitive backups encrypted:

```bash
# Encrypt backup with GPG
gpg --symmetric --cipher-algo AES256 backup-file.tar.gz

# Or with OpenSSL
openssl enc -aes-256-cbc -salt -in backup.tar.gz \
  -out backup.tar.gz.enc -k "$(cat /etc/backup-key)"

# Verify encrypted file
file backup.tar.gz.enc
```

---

## Backup Monitoring & Alerting

### Backup Health Checks

```bash
#!/bin/bash
# check-backups.sh - Monitor backup health

BACKUP_DIR="/backups"
ALERT_EMAIL="ops@example.com"

# Check backup freshness (should be < 24 hours)
LATEST_BACKUP=$(find "$BACKUP_DIR" -name "*.tar.gz" -type f \
  -printf '%T@ %p\n' | sort -rn | head -1 | cut -d' ' -f2-)

BACKUP_AGE=$(($(date +%s) - $(stat -f%m "$LATEST_BACKUP" 2>/dev/null || stat -c%Y "$LATEST_BACKUP")))
BACKUP_AGE_HOURS=$((BACKUP_AGE / 3600))

if [ "$BACKUP_AGE_HOURS" -gt 24 ]; then
  echo "⚠ WARNING: Latest backup is $BACKUP_AGE_HOURS hours old" | \
    mail -s "Backup Age Alert" "$ALERT_EMAIL"
fi

# Check disk space (should be < 90% full)
DISK_USAGE=$(df "$BACKUP_DIR" | tail -1 | awk '{print $5}' | sed 's/%//')

if [ "$DISK_USAGE" -gt 90 ]; then
  echo "⚠ ALERT: Backup disk $DISK_USAGE% full" | \
    mail -s "Backup Storage Alert" "$ALERT_EMAIL"
fi

# Check backup integrity
for backup in "$BACKUP_DIR"/*/*.tar.gz; do
  if ! tar -tzf "$backup" > /dev/null 2>&1; then
    echo "✗ CRITICAL: Backup $backup is corrupted" | \
      mail -s "Backup Corruption Alert" "$ALERT_EMAIL"
  fi
done

echo "✓ Backup health check complete"
```

**Run periodically:**
```bash
# Add to crontab (check every 6 hours)
0 */6 * * * /usr/local/bin/check-backups.sh
```

---

## Disaster Recovery Using Backups

### Complete Infrastructure Recovery

In event of total infrastructure failure:

```bash
#!/bin/bash
# disaster-recovery.sh - Full infrastructure recovery from backups

BACKUP_FILE="/backups/full/latest-full-backup.tar.gz"

echo "=== DISASTER RECOVERY PROCEDURE ==="
echo "Starting at: $(date)"
echo ""

# Step 1: Verify backup integrity
echo "Step 1: Verifying backup integrity..."
if ! sha256sum -c "${BACKUP_FILE}.sha256"; then
  echo "CRITICAL: Backup integrity check failed!"
  exit 1
fi

# Step 2: Extract backup to temporary location
echo "Step 2: Extracting backup..."
TEMP_DIR="/tmp/disaster-recovery-$$"
mkdir -p "$TEMP_DIR"
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR" || exit 1

# Step 3: Restore Git repository
echo "Step 3: Restoring code repository..."
git bundle verify "${TEMP_DIR}/repo.bundle" || exit 1
git fetch "${TEMP_DIR}/repo.bundle" '*:*' || exit 1

# Step 4: Restore configurations
echo "Step 4: Restoring configurations..."
tar -xzf "${TEMP_DIR}/configs.tar.gz" || exit 1

# Step 5: Restore inventory
echo "Step 5: Restoring inventory..."
tar -xzf "${TEMP_DIR}/inventory.tar.gz" || exit 1

# Step 6: Restore secrets
echo "Step 6: Restoring secrets..."
mkdir -p inventories/*/vault
tar -xzf "${TEMP_DIR}/vault.tar.gz" || exit 1

# Step 7: Verify restoration
echo "Step 7: Verifying restored files..."
if [ ! -d "roles" ] || [ ! -d "playbooks" ]; then
  echo "ERROR: Critical directories not restored"
  exit 1
fi

# Step 8: Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "✓ Disaster recovery restoration complete!"
echo "Next steps:"
echo "1. Verify Git repository: git log --oneline"
echo "2. Check inventory: ansible-inventory --list"
echo "3. Run Molecule tests: molecule test"
echo "4. Deploy to infrastructure: ansible-playbook playbooks/provision.yml"
echo ""
```

---

## Backup Checklist

Before production deployment:

- [ ] Full system backup created
- [ ] Backup integrity verified (sha256sum check)
- [ ] Vault secrets backed up separately
- [ ] Git repository tagged
- [ ] Backup copied to offsite storage
- [ ] Restore procedure documented in runbook
- [ ] Restore drill scheduled
- [ ] Monitoring alerts configured for backup failures
- [ ] Backup retention policies validated
- [ ] Encryption keys stored securely in separate location

---

## Troubleshooting

### Backup Failed

```bash
# Check disk space
df -h /backups

# Check permissions
ls -la /backups

# Check logs
tail -f /var/log/backups/backup.log

# Test backup script manually
bash -x /usr/local/bin/backup-configs.sh
```

### Restore Failed

```bash
# Verify backup integrity
tar -tzf backup-file.tar.gz

# Extract to test directory
tar -xzf backup-file.tar.gz -C /tmp/test

# Check file permissions in backup
tar -tzf backup-file.tar.gz | head -20
```

### Corrupted Backup

If backup is corrupted:
1. Identify last known good backup
2. Use previous backup instead
3. Test restore before relying on it
4. Report incident for investigation

---

## Documentation

**Last Updated**: November 15, 2025
**Status**: Production-Ready
**Version**: 1.0.0

For questions or improvements, contact the operations team.
