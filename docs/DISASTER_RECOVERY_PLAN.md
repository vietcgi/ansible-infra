# Disaster Recovery Plan

## Overview

This document outlines the comprehensive disaster recovery (DR) strategy for ansible-infra infrastructure. It provides procedures for rapid recovery from various failure scenarios, with defined Recovery Time Objectives (RTO) and Recovery Point Objectives (RPO).

---

## Recovery Objectives

### Recovery Time Objective (RTO)

Time to restore full service capability after a disaster:

| Scenario | RTO | Justification |
|----------|-----|---------------|
| **Single host failure** | 15 minutes | Quick provisioning via Ansible |
| **Single role failure** | 5 minutes | Configuration reapplication |
| **Network segment failure** | 30 minutes | Failover to backup network |
| **Complete data center failure** | 2 hours | Full infrastructure rebuild |
| **Partial infrastructure loss** | 30 minutes | Partial rebuild + existing hosts |
| **Configuration corruption** | 5 minutes | Git repository rollback |
| **Secrets compromise** | 1 hour | Vault password rotation + redeployment |

### Recovery Point Objective (RPO)

Maximum acceptable data loss:

| Data Type | RPO | Strategy |
|-----------|-----|----------|
| **Infrastructure code** | 0 minutes | Git continuous push |
| **Configuration** | 4 hours | Hourly automated backups |
| **Secrets (Vault)** | On-demand | Encrypted version control |
| **Application data** | 24 hours | Daily automated snapshots |
| **Logs** | 24 hours | Centralized log aggregation |
| **Metrics** | 24 hours | Prometheus time-series storage |

### Mean Time to Recovery (MTTR)

Average time to recover from failure:

| Issue Type | Current MTTR | Target MTTR |
|-----------|-------------|-------------|
| **SSH key issues** | 30 min | 5 min |
| **Configuration drift** | 45 min | 15 min |
| **Package dependency issues** | 60 min | 30 min |
| **Network connectivity** | 90 min | 30 min |
| **System corruption** | 120 min | 60 min |

---

## Disaster Classification

### Level 1: Minimal Impact
- **Scope**: Single role or component
- **Examples**: SSH config issue, package not installed, service stopped
- **RTO**: 5-15 minutes
- **Action**: Local remediation via Ansible
- **On-call**: Not required for all incidents

### Level 2: Moderate Impact
- **Scope**: Multiple components or single host completely offline
- **Examples**: System corruption, host failure, network interface down
- **RTO**: 15-30 minutes
- **Action**: Host replacement or rebuild from backup
- **On-call**: Required, single person sufficient

### Level 3: Significant Impact
- **Scope**: Multiple hosts or core infrastructure affected
- **Examples**: Database server down, multiple hosts failed, network segment isolated
- **RTO**: 30-60 minutes
- **Action**: Failover to secondary, rebuild primary
- **On-call**: Required, escalation to team lead

### Level 4: Critical/Catastrophic
- **Scope**: Complete infrastructure failure or data loss imminent
- **Examples**: Data center failure, ransomware attack, widespread corruption
- **RTO**: 1-2 hours
- **Action**: Complete rebuild from offsite backups
- **On-call**: All-hands incident, executive notification

---

## Disaster Scenarios & Recovery Procedures

### Scenario 1: Single Host Failure

**Trigger**: Host becomes unreachable, services unavailable

**Detection**:
```bash
# Monitoring alert triggers
ansible all -i inventories/production -m ping | grep "FAILED"

# Manual check
ssh user@host "echo test"  # Connection timeout
```

**Recovery Procedure** (5-15 minutes):

1. **Verify failure** (2 min)
   ```bash
   ansible failed_host -m ping
   ssh -v failed_host "exit"  # Verbose SSH to verify
   ```

2. **Assess damage** (2 min)
   - Is data loss possible?
   - Are other hosts affected?
   - Can service continue without this host?

3. **Option A: Quick Reboot** (5 min)
   ```bash
   # If host is in rescue mode or can be rebooted
   ansible-playbook -i inventories/production \
     playbooks/restart.yml -e "target_host=failed_host"
   ```

4. **Option B: Rebuild Host** (10 min)
   ```bash
   # Re-provision the host completely
   ansible-playbook -i inventories/production \
     playbooks/provision.yml -e "target_host=failed_host"

   # Reapply configuration
   ansible-playbook -i inventories/production \
     playbooks/configure.yml -e "target_host=failed_host"
   ```

5. **Verification** (3 min)
   ```bash
   # Health checks
   ansible failed_host -m ping
   ansible failed_host -m command -a "systemctl status"

   # Run smoke tests
   molecule verify
   ```

6. **Post-Recovery**
   - Document incident in incident report
   - Check logs for root cause
   - Update monitoring if needed

---

### Scenario 2: Network Connectivity Loss

**Trigger**: Host loses network, cannot reach network segment

**Detection**:
```bash
# Icinga/Prometheus alerts
# Unreachable hosts exceed threshold
# DNS lookups timing out
```

**Recovery Procedure** (15-30 minutes):

1. **Identify failure scope** (3 min)
   ```bash
   # Check which hosts are affected
   ansible all -i inventories/production -m ping

   # Test network connectivity
   for host in $(cat inventories/production/hosts.yml); do
     mtr -c 1 $host
   done
   ```

2. **Assess network** (5 min)
   ```bash
   # Check routing
   ip route
   ip -4 addr show

   # Check interfaces
   ip link show
   ethtool eth0 | grep "Link detected"
   ```

3. **Failover to secondary** (10 min)
   - If secondary network exists, switch DNS
   - Update load balancer
   - Verify traffic routing

   ```bash
   # Update DNS or load balancer
   ansible-playbook playbooks/failover-network.yml
   ```

4. **Fix primary network** (ongoing)
   ```bash
   # Restore primary network
   ansible-playbook playbooks/restore-network.yml \
     -e "network_interface=eth0"
   ```

5. **Verification** (5 min)
   ```bash
   # Test connectivity
   ansible all -i inventories/production -m ping
   ```

---

### Scenario 3: Configuration Corruption

**Trigger**: Configuration file modified incorrectly, system unstable

**Detection**:
```bash
# Services failing to start
systemctl status service_name  # Failed

# Ansible linting errors
ansible-lint playbooks/

# Health check failures
curl http://localhost:8000/health  # 500 error
```

**Recovery Procedure** (2-5 minutes):

1. **Identify corruption** (1 min)
   ```bash
   # Check Git status
   git status
   git diff

   # Find changed files
   find /etc -newer /tmp/baseline -type f
   ```

2. **Rollback to last known good** (2 min)
   ```bash
   # Find last successful commit
   git log --oneline | head -5

   # Revert corrupt file
   git checkout HEAD~1 -- roles/common/templates/sshd_config.j2

   # Or full reset if necessary
   git reset --hard HEAD~1
   ```

3. **Reapply configuration** (2 min)
   ```bash
   # Reapply roles
   ansible-playbook -i inventories/production \
     playbooks/configure.yml \
     -e "target_role=common"
   ```

4. **Verify restoration** (1 min)
   ```bash
   # Check service status
   systemctl status service_name

   # Validate configuration
   ansible-lint playbooks/
   ```

---

### Scenario 4: Secrets Compromise

**Trigger**: Vault password exposed, secrets potentially leaked

**Detection**:
- Unauthorized Vault access detected in logs
- Credentials found in git history
- Unusual login attempts with exposed credentials

**Recovery Procedure** (30-60 minutes):

1. **Immediate containment** (5 min)
   ```bash
   # Revoke all potentially compromised secrets
   # Kill all active sessions
   pkill -u vulnerable_user

   # Disable affected accounts
   passwd -l vulnerable_user
   ```

2. **Change Vault password** (10 min)
   ```bash
   # Generate new password
   openssl rand -base64 32 > /tmp/new-vault-pass

   # Reencrypt with new password
   ansible-vault rekey \
     --vault-id old@/tmp/old-vault-pass \
     --vault-id new@/tmp/new-vault-pass \
     inventories/production/vault/main.yml

   # Update CI/CD with new password
   # Update all ~/.ansible/ vault password files
   ```

3. **Rotate all exposed secrets** (20 min)
   ```bash
   # Regenerate SSH keys
   for host in $(ansible all -i inventories/production --list-hosts); do
     ansible-playbook playbooks/rotate-ssh-keys.yml \
       -e "target_host=$host"
   done

   # Update database passwords
   # Reset API tokens
   # Regenerate certificates
   ```

4. **Audit secret usage** (15 min)
   ```bash
   # Check what was accessed
   grep vault /var/log/ansible-infra/*.log | grep access

   # Scan git history for secrets
   git log -p | grep -i "password\|secret\|token"
   ```

5. **Communication** (10 min)
   - Notify security team
   - Inform affected users
   - Create security incident ticket
   - Update security policy if needed

---

### Scenario 5: Database Failure

**Trigger**: Database service down, cannot connect, data potentially lost

**Detection**:
```bash
# Service status
systemctl status postgresql  # Failed

# Connection test
psql -h localhost -U user dbname  # Connection refused

# Application errors
tail -f /var/log/application.log  # Database connection errors
```

**Recovery Procedure** (15-30 minutes):

1. **Assess situation** (3 min)
   ```bash
   # Check if disk space issue
   df -h /var/lib/postgresql/

   # Check logs
   tail -50 /var/log/postgresql/postgresql.log

   # Check memory/CPU
   top -b -n 1 | head -20
   ```

2. **Option A: Restart service** (2 min)
   ```bash
   systemctl restart postgresql

   # Monitor startup
   journalctl -f -u postgresql
   ```

3. **Option B: Recover from backup** (15 min)
   ```bash
   # Stop database service
   systemctl stop postgresql

   # Restore from latest backup
   bash /usr/local/bin/restore-database.sh /backups/databases/latest/

   # Start service
   systemctl start postgresql

   # Verify data integrity
   psql -U user dbname -c "SELECT COUNT(*) FROM table;"
   ```

4. **Option C: Promote replica** (10 min)
   ```bash
   # If replication configured
   # SSH to replica
   ssh replica-host

   # Promote to primary
   pg_ctl promote -D /var/lib/postgresql/data

   # Update connection strings
   ansible-playbook playbooks/update-db-config.yml \
     -e "db_host=replica-host"
   ```

5. **Verification** (3 min)
   ```bash
   # Test connectivity
   psql -h localhost -U user dbname -c "SELECT 1;"

   # Check replication status (if applicable)
   psql -U user dbname -c "SELECT * FROM pg_stat_replication;"
   ```

---

### Scenario 6: Complete Data Center Failure

**Trigger**: Entire site offline, multiple infrastructure failures

**Detection**:
- All hosts unreachable
- DNS queries fail
- Network segment completely down
- Physical datacenter issues (power, cooling)

**Recovery Procedure** (60-120 minutes):

1. **Declare disaster** (5 min)
   - Activate incident response team
   - Notify executive stakeholders
   - Open war room/communication channel
   - Activate offsite recovery location

2. **Verify unrecoverable** (10 min)
   ```bash
   # Confirm primary site truly offline
   ansible all -i inventories/production -m ping
   # All FAILED/UNREACHABLE

   # Check with network/infrastructure team
   # Verify no recovery ETA
   ```

3. **Recover infrastructure from backups** (45 min)
   ```bash
   # Access offsite backup storage
   aws s3 ls s3://ansible-infra-backups/

   # Download full system backup
   aws s3 cp s3://ansible-infra-backups/full-backup.tar.gz \
     /backups/disaster-recovery/

   # Verify integrity
   sha256sum -c /backups/disaster-recovery/full-backup.sha256

   # Extract backup
   tar -xzf /backups/disaster-recovery/full-backup.tar.gz \
     -C /tmp/restore/
   ```

4. **Restore from Git bundle** (15 min)
   ```bash
   # Restore Git repository
   git bundle verify /tmp/restore/repo.bundle
   git fetch /tmp/restore/repo.bundle '*:*'

   # Verify all branches/tags restored
   git branch -a
   git tag | grep backup
   ```

5. **Restore configurations and secrets** (20 min)
   ```bash
   # Extract configurations
   tar -xzf /tmp/restore/inventory.tar.gz
   tar -xzf /tmp/restore/configs.tar.gz

   # Extract encrypted secrets
   mkdir -p inventories/production/vault
   tar -xzf /tmp/restore/vault.tar.gz

   # Decrypt secrets for use
   ansible-vault decrypt inventories/production/vault/main.yml
   ```

6. **Provision new infrastructure** (30 min)
   ```bash
   # Create VMs/instances in failover site
   terraform apply -var="location=failover-site"

   # Run provisioning playbook
   ansible-playbook playbooks/provision.yml \
     -i inventories/failover-site/hosts.yml

   # Apply configuration
   ansible-playbook playbooks/configure.yml \
     -i inventories/failover-site/hosts.yml
   ```

7. **Verify recovery** (10 min)
   ```bash
   # Health checks
   ansible all -i inventories/failover-site/hosts.yml \
     -m command -a "systemctl status"

   # Run smoke tests
   molecule verify

   # Validate data restore
   psql -U user dbname -c "SELECT COUNT(*) FROM critical_table;"
   ```

8. **Communication and post-incident**
   - Update stakeholders on recovery status
   - Document incident details
   - Plan recovery of primary site
   - Schedule post-mortem meeting

---

## Disaster Recovery Runbooks

### Quick Runbook: Single Host Recovery

```bash
#!/bin/bash
# quick-recovery-single-host.sh

HOST=$1

if [ -z "$HOST" ]; then
  echo "Usage: $0 <hostname>"
  exit 1
fi

echo "=== SINGLE HOST RECOVERY ==="
echo "Target: $HOST"
echo "Time: $(date)"

# 1. Verify failure
echo "1. Verifying host failure..."
ansible "$HOST" -m ping || {
  echo "✓ Host confirmed unreachable"
}

# 2. Check backups
echo "2. Checking available backups..."
ls -lh /backups/full/ | tail -3

# 3. Rebuild host
echo "3. Provisioning new host..."
ansible-playbook -i inventories/production playbooks/provision.yml \
  -e "target_host=$HOST" || {
  echo "ERROR: Provisioning failed"
  exit 1
}

# 4. Apply configuration
echo "4. Applying configuration..."
ansible-playbook -i inventories/production playbooks/configure.yml \
  -e "target_host=$HOST" || {
  echo "ERROR: Configuration failed"
  exit 1
}

# 5. Verify
echo "5. Verifying recovery..."
ansible "$HOST" -m command -a "systemctl status" || {
  echo "ERROR: Services not running"
  exit 1
}

echo ""
echo "✓ Recovery complete!"
```

### Quick Runbook: Configuration Rollback

```bash
#!/bin/bash
# quick-recovery-config-rollback.sh

ROLE=$1
COMMITS_BACK=${2:-1}

if [ -z "$ROLE" ]; then
  echo "Usage: $0 <role-name> [commits-back]"
  exit 1
fi

echo "=== CONFIGURATION ROLLBACK ==="
echo "Role: $ROLE"
echo "Rolling back $COMMITS_BACK commit(s)"

# 1. Show recent commits
echo "Recent commits:"
git log --oneline roles/"$ROLE" | head -5

# 2. Rollback
echo "Rolling back..."
git reset --hard HEAD~"$COMMITS_BACK"

# 3. Reapply configuration
echo "Reapplying configuration..."
ansible-playbook -i inventories/production playbooks/configure.yml \
  -e "target_role=$ROLE"

# 4. Verify
echo "Verifying..."
ansible-lint playbooks/

echo "✓ Rollback complete!"
```

---

## Disaster Recovery Testing

### Quarterly DR Drills

Schedule and execute quarterly disaster recovery drills:

```bash
#!/bin/bash
# dr-drill.sh - Quarterly disaster recovery test

echo "=== DISASTER RECOVERY DRILL ==="
echo "Date: $(date)"
echo "Objective: Test recovery procedures"

# 1. Select random scenario
SCENARIOS=(
  "single-host-failure"
  "configuration-corruption"
  "network-failure"
  "database-failure"
)

SCENARIO="${SCENARIOS[$((RANDOM % ${#SCENARIOS[@]}))]}"

echo "Selected scenario: $SCENARIO"

# 2. Execute scenario
case $SCENARIO in
  single-host-failure)
    HOST=$(ansible all -i inventories/staging --list-hosts | shuf -n 1)
    echo "Simulating failure of $HOST..."
    # Stop services but preserve OS
    ansible "$HOST" -m systemd -a "name=ansible state=stopped"
    ;;

  configuration-corruption)
    echo "Simulating configuration corruption..."
    # Corrupt a file temporarily
    ROLE=$(ls roles/ | shuf -n 1)
    ansible-playbook playbooks/test-corruption.yml \
      -e "target_role=$ROLE"
    ;;

  network-failure)
    echo "Simulating network isolation..."
    # Isolate host from network
    HOST=$(ansible all -i inventories/staging --list-hosts | shuf -n 1)
    ansible "$HOST" -m command -a "ifconfig eth0 down"
    ;;

  database-failure)
    echo "Simulating database failure..."
    # Stop database service
    ansible all -i inventories/staging -m systemd \
      -a "name=postgresql state=stopped"
    ;;
esac

# 3. Measure recovery time
echo "Recording recovery attempt..."
START_TIME=$(date +%s)

# Recovery steps performed here
# ... (execute appropriate recovery for scenario)

END_TIME=$(date +%s)
RECOVERY_TIME=$((END_TIME - START_TIME))

# 4. Verify recovery
echo "Verifying recovery..."
ansible all -i inventories/staging -m ping

# 5. Report
cat > /tmp/dr-drill-report-$(date +%Y%m%d).txt <<EOF
DR Drill Report
===============
Date: $(date)
Scenario: $SCENARIO
Recovery Time: ${RECOVERY_TIME} seconds
Status: $([ $RECOVERY_TIME -lt 600 ] && echo "PASS" || echo "FAIL")

Issues encountered:
- [List any issues]

Recommendations:
- [List recommendations]
EOF

echo "✓ Drill complete. Report saved."
```

---

## Disaster Communication Plan

### Escalation Path

```
Incident Detected (ANY TEAM MEMBER)
  ↓ (notify within 5 min)
On-Call Engineer
  ↓ (assess severity, notify if Level 2+)
Team Lead / Incident Commander
  ↓ (if Level 3-4)
Director of Operations
  ↓ (if Level 4)
Executive Management / CEO
```

### Notification Templates

**Level 1-2 Incident**
```
Subject: Incident Notice - Level [#]
To: ops-team@example.com

Issue: [Brief description]
Impact: [Services affected]
Status: [Investigating/Resolving]
ETA: [Estimated resolution time]
Next Update: [Time]
```

**Level 3-4 Incident**
```
Subject: CRITICAL INCIDENT - Immediate Attention Required
To: leadership@example.com, ops-team@example.com

SUMMARY
======
Critical infrastructure failure requiring executive notification.

DETAILS
=======
Issue: [Description]
Impact: [Business impact]
Affected Services: [List]
Customer Impact: [Description]
Financial Impact: [Estimated]

RESPONSE
========
Status: [Investigating/Mitigating/Recovering]
Team Activated: [Names]
Recovery Estimate: [ETA]

NEXT STEPS
==========
- [Action 1]
- [Action 2]

Next Update: [Time]
```

---

## Disaster Recovery Checklist

### Before Each Major Change

- [ ] Full system backup created
- [ ] Backup verified and tested
- [ ] Offsite copy initiated
- [ ] Rollback plan documented
- [ ] Team notified of change window
- [ ] Backup contact information current
- [ ] Emergency procedures reviewed

### Monthly

- [ ] Verify backup integrity
- [ ] Test restore procedure
- [ ] Check offsite replication status
- [ ] Review incident logs for lessons learned
- [ ] Update runbooks with new procedures

### Quarterly

- [ ] Execute full DR drill
- [ ] Document results
- [ ] Update recovery procedures based on findings
- [ ] Review RTO/RPO targets
- [ ] Audit compliance with plan

---

## Contact Information

**Maintain current and secured:**
- On-call engineer phone/email
- Team lead contact information
- Executive escalation contacts
- Backup storage access credentials
- DR site access procedures
- Third-party vendor contacts

---

## Documentation

**Last Updated**: November 15, 2025
**Version**: 1.0.0
**Status**: Production-Ready
**Next Review**: February 15, 2026

This plan is reviewed annually and updated as infrastructure changes.
