# Operational Runbooks

## Overview

This document provides step-by-step procedures for common operational tasks in ansible-infra infrastructure. These runbooks enable rapid, consistent incident response and routine maintenance.

---

## Runbook: Host Recovery

### When to Use
- Host becomes unreachable
- Service not responding
- Manual restart needed

### Prerequisites
- SSH access to hosts
- Ansible configured
- Backups current

### Procedure

**1. Verify failure** (2 min)
```bash
ansible target_host -m ping
# UNREACHABLE or FAILED indicates problem
```

**2. Assess impact** (2 min)
```bash
# Check if service still available
curl http://target_host:8000/health  # Timeout confirms down

# Check other hosts
ansible all -m ping | grep FAILED
```

**3. Option A: Restart service** (5 min)
```bash
# Reboot host (if access to console)
ansible target_host -m reboot

# Or restart service
ansible target_host -m systemd \
  -a "name=ansible-infra state=restarted"
```

**4. Option B: Rebuild host** (10 min)
```bash
# Complete reprovisioning
ansible-playbook playbooks/provision.yml \
  -i inventories/production \
  -e "target_host=target_host"
```

**5. Verification** (3 min)
```bash
ansible target_host -m ping
# Should return PING: pong

# Check service
ansible target_host -m systemd \
  -a "name=ansible-infra"
# Should show: active (running)

# Run health check
ansible target_host -m uri \
  -a "url=http://localhost:8000/health"
```

**Estimated Duration**: 5-15 minutes

---

## Runbook: Configuration Drift Recovery

### When to Use
- Configuration doesn't match expected state
- Manual changes made to hosts
- Need to restore to known good state

### Procedure

**1. Detect drift** (2 min)
```bash
# Dry-run shows what changed
ansible-playbook playbooks/configure.yml \
  --check --diff \
  -i inventories/production

# Review proposed changes
```

**2. Assess impact** (3 min)
```bash
# Check what will change
# Look for unexpected changes
# If dangerous, skip to manual investigation
```

**3. Apply fix** (5 min)
```bash
# Apply configuration (for real)
ansible-playbook playbooks/configure.yml \
  -i inventories/production

# Or specific role
ansible-playbook playbooks/configure.yml \
  -i inventories/production \
  --tags "ssh_hardening"
```

**4. Verify** (3 min)
```bash
# Check no new errors
ansible all -m shell \
  -a "systemctl status ansible" | grep active

# Verify configuration
sshd -T | grep -i "KexAlgorithms"
```

**Estimated Duration**: 10-15 minutes

---

## Runbook: Package Update & Patch

### When to Use
- Security patch available
- Package update recommended
- Scheduled maintenance window

### Procedure

**1. Pre-update backup** (5 min)
```bash
# Create backup
bash /usr/local/bin/full-system-backup.sh

# Verify
ls -lh /backups/full/latest/
```

**2. Test updates** (10 min)
```bash
# Check for available updates
ansible staging -m apt -a "update_cache=yes"
ansible staging -m apt -a "list=upgradeable"

# Dry-run upgrade
ansible staging -m apt \
  -a "upgrade=full state=present" \
  --check
```

**3. Apply updates** (15 min)
```bash
# Upgrade production (during maintenance window)
ansible production -m apt \
  -a "upgrade=full state=present"

# Watch progress
tail -f /var/log/ansible-infra/ansible.log
```

**4. Verify** (5 min)
```bash
# Check services running
ansible all -m systemd \
  -a "name=ansible-infra state=started"

# Reboot if kernel updated
ansible all -m reboot --async 600

# Verify after reboot
ansible all -m command -a "uname -r"
```

**5. Smoke tests** (5 min)
```bash
# Run health checks
molecule verify

# Check error rate
curl http://prometheus:9090/api/v1/query?query=rate(errors_total[5m])
```

**Estimated Duration**: 40-60 minutes

---

## Runbook: SSH Access Troubleshooting

### When to Use
- Cannot SSH to host
- Authentication failing
- Permission denied errors

### Procedure

**1. Check connectivity** (2 min)
```bash
# Verify host reachable
ping -c 3 target_host

# Check SSH port open
nc -zv target_host 22

# Test SSH verbosely
ssh -vvv user@target_host exit
```

**2. Check SSH configuration** (3 min)
```bash
# On host, verify SSH running
systemctl status ssh

# Check sshd config
sshd -T | head -20

# Look for syntax errors
sshd -T  # Should output without errors
```

**3. Check authentication** (3 min)
```bash
# Verify key exists locally
ls -la ~/.ssh/id_ed25519

# Check permissions
stat ~/.ssh/id_ed25519  # Should be 600

# Check on host
ansible target_host -m shell \
  -a "ls -la /home/user/.ssh/authorized_keys"
```

**4. Fix issues** (5-15 min)
```bash
# Issue: Key permissions wrong
chmod 0600 ~/.ssh/id_ed25519
chmod 0700 ~/.ssh/

# Issue: Key not in authorized_keys
ansible-playbook playbooks/configure-ssh.yml

# Issue: SSH not starting
ansible target_host -m systemd \
  -a "name=ssh state=started"

# Issue: Firewall blocking
ansible target_host -m firewalld \
  -a "port=22/tcp permanent=yes state=enabled"
```

**5. Verify** (2 min)
```bash
# Test SSH works
ssh user@target_host echo "Connected"
```

**Estimated Duration**: 10-25 minutes

---

## Runbook: Vault Access Recovery

### When to Use
- Cannot decrypt vault files
- Vault password lost
- Forgot vault password

### Procedure

**1. Check vault file** (1 min)
```bash
# Verify file encrypted
file inventories/production/vault/main.yml
# Should show: encrypted data

# Try to view
ansible-vault view inventories/production/vault/main.yml
# Should prompt for password
```

**2. Recover password** (5 min)
```bash
# If password stored in 1Password/LastPass
# Retrieve from password manager

# If password file stored
export ANSIBLE_VAULT_PASSWORD_FILE=/path/to/password/file

# If multiple environment variables
echo $VAULT_PASSWORD_PROD
```

**3. Access vault files** (2 min)
```bash
# View vault file
ansible-vault view inventories/production/vault/main.yml
# Should display content

# Edit vault file
ansible-vault edit inventories/production/vault/main.yml
```

**4. If password truly lost** (30 min)
```bash
# Requirement: You must have backup password
# From: separate secure storage

# 1. Get backup password from secure location
# 2. Decrypt files
ansible-vault decrypt --vault-id old@/path/to/backup/password \
  inventories/production/vault/main.yml

# 3. Review content
cat inventories/production/vault/main.yml

# 4. Generate new password
openssl rand -base64 32 > /new/vault/password

# 5. Re-encrypt with new password
ansible-vault encrypt --vault-id new@/new/vault/password \
  inventories/production/vault/main.yml

# 6. Store new password securely
# - Save to password manager
# - Update CI/CD secrets
# - Save backup copy in secure location

# 7. Verify
ansible-vault view inventories/production/vault/main.yml
```

**Estimated Duration**: 2-35 minutes depending on scenario

---

## Runbook: Database Failover

### When to Use
- Primary database down
- Database corruption detected
- Need to switch to replica

### Procedure

**1. Assess situation** (3 min)
```bash
# Check primary database
psql -h primary-db -U admin -c "SELECT version();"
# Should fail

# Check replica status
psql -h replica-db -U admin -c "SELECT * FROM pg_stat_replication;"
# Should show replication lag
```

**2. Verify replica is ready** (2 min)
```bash
# Check replica can accept connections
psql -h replica-db -U admin -c "SELECT 1;"

# Check replica data integrity
psql -h replica-db -U admin -c "SELECT COUNT(*) FROM important_table;"
# Compare with known count
```

**3. Promote replica** (5 min)
```bash
# SSH to replica
ssh user@replica-db

# Promote to primary
pg_ctl promote -D /var/lib/postgresql/data

# Verify promotion
psql -c "SELECT pg_is_in_recovery();"
# Should return 'f' (false) = not in recovery = is primary
```

**4. Update connection strings** (5 min)
```bash
# Update Ansible inventory
ansible-playbook playbooks/update-db-host.yml \
  -e "db_host=replica-db.example.com"

# Update application configs
ansible all -m template \
  -a "src=database.conf.j2 dest=/etc/database.conf"
```

**5. Verify applications working** (5 min)
```bash
# Test database queries
ansible all -m command \
  -a "psql -U app_user -c 'SELECT 1;'"

# Check application health
curl http://app:8000/health

# Monitor error rates
# Should show no connection errors
```

**6. Recover primary** (ongoing)
```bash
# Investigate why primary failed
# Restore data
# Rebuild and rejoin as replica

# Do NOT use old primary immediately
# Must rebuild and verify data integrity
```

**Estimated Duration**: 15-30 minutes

---

## Runbook: Disk Space Recovery

### When to Use
- Disk space alert triggered
- Disk > 85% full
- Applications failing due to space

### Procedure

**1. Identify issue** (5 min)
```bash
# Check disk usage
df -h

# Find largest directories
du -sh /* | sort -h

# Check log files
ls -lh /var/log/ansible-infra/

# Check temp files
ls -lh /tmp/
```

**2. Clean up logs** (5 min)
```bash
# Rotate logs
logrotate -f /etc/logrotate.d/ansible-infra

# Remove old compressed logs
find /var/log -name "*.gz" -mtime +30 -delete

# Clean temp files
rm -rf /tmp/ansible-*
rm -rf /tmp/*.tmp
```

**3. Archive backups** (10 min)
```bash
# Move old backups to archive
mv /backups/full/backup-*.tar.gz /backups/archive/

# Compress retained backups
gzip /backups/configs/*.tar

# Verify disk recovered
df -h
```

**4. Verify services** (3 min)
```bash
# Check applications still running
ansible all -m systemd \
  -a "name=ansible-infra"

# Test functionality
curl http://localhost:8000/health
```

**5. Monitor** (ongoing)
```bash
# Watch for disk growth
watch -n 60 'df -h | grep root'

# Set up alert if > 80%
# Configure log rotation if growing
```

**Estimated Duration**: 20-40 minutes

---

## Runbook: Service Restart

### When to Use
- Service hung or unresponsive
- Configuration changed
- Memory leak suspected

### Procedure

**1. Check service status** (1 min)
```bash
systemctl status ansible-infra
# Should show if running or failed
```

**2. Stop service** (2 min)
```bash
systemctl stop ansible-infra

# Wait for graceful shutdown
sleep 5

# Verify stopped
systemctl status ansible-infra | grep "inactive"
```

**3. Clear state** (2 min)
```bash
# Remove pid files
rm -f /var/run/ansible-infra.pid

# Clear temp files
rm -rf /tmp/ansible-infra-*

# Clear cache if applicable
redis-cli FLUSHDB  # if using Redis
```

**4. Start service** (2 min)
```bash
systemctl start ansible-infra

# Monitor startup
journalctl -f -u ansible-infra
```

**5. Verify running** (2 min)
```bash
# Check status
systemctl status ansible-infra
# Should show active (running)

# Test functionality
curl http://localhost:8000/health
# Should return 200 OK
```

**Estimated Duration**: 10-15 minutes

---

## Runbook Index

| Runbook | Duration | Complexity | When to Use |
|---------|----------|-----------|------------|
| Host Recovery | 5-15 min | Low | Host down |
| Config Drift | 10-15 min | Low | Config wrong |
| Package Update | 40-60 min | Medium | Patch Tuesday |
| SSH Troubleshooting | 10-25 min | Medium | SSH failing |
| Vault Recovery | 2-35 min | High | Password lost |
| Database Failover | 15-30 min | High | DB down |
| Disk Space | 20-40 min | Medium | Disk full |
| Service Restart | 10-15 min | Low | Service hung |

---

## Emergency Contacts

For issues not covered by runbooks:
- On-call: @on-call
- Team Lead: @team-lead
- Director: @director
- Status page: https://status.example.com

---

## Documentation

**Last Updated**: November 15, 2025
**Version**: 1.0.0
**Status**: Production-Ready
**Next Review**: February 15, 2026

Runbooks updated quarterly based on incidents.
