# Staging & Production Rollout Plan

**Date**: November 17, 2025
**Status**: Ready for Execution
**Duration**: 4 weeks total (1 week staging + 3 weeks phased production)

---

## Executive Summary

This document outlines the proven approach for safely deploying the 100% enterprise-grade common role across your infrastructure. The strategy uses a phased approach with 24-hour validation periods to minimize risk.

**Risk Level**: LOW
**Estimated Downtime**: 0 minutes (no restarts required)
**Rollback Time**: < 5 minutes (idempotent - re-run previous version)

---

## Phase 0: Pre-Deployment Preparation (Days 1-3)

### Day 1: Environment Setup

**Morning (2 hours)**
1. Review all configuration guides
2. Prepare Ansible Vault with secrets:
   ```bash
   # Create vault file with sensitive data
   ansible-vault create group_vars/all.yml
   ```
   Add these secrets:
   ```yaml
   ---
   vault_smtp_password: "your-smtp-password"
   vault_slack_webhook: "https://hooks.slack.com/services/..."
   vault_pagerduty_token: "your-pagerduty-token"
   vault_pagerduty_service_key: "your-service-key"
   ```

3. Create staging environment inventory:
   ```yaml
   # inventory/staging.yml
   [staging]
   staging-web-01 ansible_host=10.0.1.10
   staging-web-02 ansible_host=10.0.1.11
   staging-db-01 ansible_host=10.0.2.10

   [staging:vars]
   environment=staging
   ```

4. Create staging group_vars:
   ```yaml
   # group_vars/staging.yml
   alert_cpu_high: 90
   alert_memory_high: 90
   monitoring_slack_enabled: true
   compliance_remediation_enabled: true  # Test auto-fix in staging
   ```

**Afternoon (2 hours)**
5. Create production environment inventory (but don't deploy yet)
6. Create production group_vars (conservative thresholds)
7. Prepare rollback procedures documentation
8. Set up monitoring dashboard for alert verification

### Day 2: Testing in Development

**Full Day (8 hours)**
1. Deploy to development environment for 24-hour validation
2. Verify all tasks execute without errors
3. Check compliance scanning works
4. Validate alert thresholds appropriate
5. Test notification channels
6. Document any adjustments needed

### Day 3: Preparations Complete

1. Review all documentation
2. Get approval from stakeholders
3. Schedule maintenance windows (if needed)
4. Brief operations team on new features
5. Set up post-deployment monitoring dashboard

---

## Phase 1: Staging Deployment (Days 4-11)

### Week 1: Full 24-Hour Validation

**Monday (Day 4): Initial Deployment**

```bash
# Deploy to staging environment
cd /path/to/ansible-infra

# Run against staging hosts
ansible-playbook site.yml \
  -i inventory/staging.yml \
  --vault-password-file ~/.vault_pass \
  -e environment=staging

# Verify deployment succeeded
ansible staging -i inventory/staging.yml -m ping
```

**Expected Results**:
- All tasks complete without errors
- 0 failed tasks
- Kernel hardening applied
- Password policy enforced
- Storage mounts configured
- Alerts created and routed

**Verification Tasks** (Run these post-deployment):

```bash
# 1. Verify kernel hardening
ssh staging-web-01 "sysctl kernel.kptr_restrict"
# Expected: kernel.kptr_restrict = 2

# 2. Check password policy
ssh staging-web-01 "grep -A5 'minlen' /etc/security/pwquality.conf"
# Expected: minlen = 14

# 3. Verify storage mounts
ssh staging-web-01 "mount | grep -E 'tmp|var|home'"
# Expected: noexec,nosuid,nodev flags present

# 4. Check compliance scanning
ssh staging-web-01 "ls -la /opt/compliance-frameworks/"
# Expected: All compliance checker scripts present

# 5. Verify alerts configured
ssh staging-web-01 "ls -la /etc/monitoring/alerts/"
# Expected: All alert configuration files present
```

**Tuesday-Thursday (Days 5-7): 72-Hour Validation**

Monitor continuously:

```bash
# Check alert generation (should see test alerts)
ssh staging-web-01 "tail -20 /var/log/alert*.log"

# Verify compliance scans running
ssh staging-web-01 "crontab -l | grep compliance"

# Monitor system performance
ansible staging -i inventory/staging.yml -a "vmstat 1 3"

# Check disk usage
ansible staging -i inventory/staging.yml -a "df -h"

# Verify no errors in logs
ssh staging-web-01 "grep ERROR /var/log/syslog | tail -5"
```

**Friday-Weekend (Days 8-11): Collect Baseline Data**

```bash
# Collect 48-hour performance baseline
ansible staging -i inventory/staging.yml -a "cat /proc/loadavg"

# Review compliance reports
ssh staging-web-01 "cat /var/log/compliance/fedramp-check-$(date +%Y%m%d).log"

# Verify alerts tested and working
# (Should have received email/Slack alerts during 4-day period)

# Get approval to proceed to production
# - Alert team lead if any issues detected
# - Document any threshold adjustments needed
```

### Success Criteria for Staging

All items must be **PASSED** before proceeding to production:

- [ ] Kernel hardening: No errors
- [ ] Password policy: Enforced
- [ ] Storage mounts: Correct flags
- [ ] Alerts: Functioning (test alerts received)
- [ ] Compliance: Scans completed
- [ ] Performance: No degradation
- [ ] Stability: System stable for 72 hours
- [ ] Monitoring: Alert delivery working

---

## Phase 2: Production Rollout (Days 12-33)

### Phase 2a: Non-Critical Systems (Days 12-14)

**Target**: 2-3 non-production systems
**Duration**: 3 days
**Risk**: Minimal

```bash
# Create production-non-critical inventory
cat > inventory/production-non-critical.yml <<EOF
[production-non-critical]
backup-01 ansible_host=10.1.10.10
monitoring-01 ansible_host=10.1.10.20
logging-01 ansible_host=10.1.10.30

[production-non-critical:vars]
environment=production
EOF

# Deploy
ansible-playbook site.yml \
  -i inventory/production-non-critical.yml \
  --vault-password-file ~/.vault_pass \
  -e environment=production
```

**Monitoring During Rollout**:
```bash
# Watch system during deployment
watch -n 5 'ssh backup-01 uptime'

# Monitor for errors in real-time
ssh backup-01 "tail -f /var/log/syslog | grep -E ERROR"

# Verify post-deployment
ansible production-non-critical \
  -i inventory/production-non-critical.yml \
  -m shell -a 'sysctl kernel.kptr_restrict'
```

**Success**: Systems operating normally after 48 hours

### Phase 2b: Development Environment (Days 15-18)

**Target**: All development servers
**Duration**: 4 days
**Risk**: Low (non-critical)

```bash
# Create development inventory
cat > inventory/development.yml <<EOF
[development]
dev-web-01 ansible_host=10.2.1.10
dev-web-02 ansible_host=10.2.1.11
dev-db-01 ansible_host=10.2.2.10
dev-db-02 ansible_host=10.2.2.11

[development:vars]
environment=development
EOF

# Deploy in batches to minimize impact
ansible-playbook site.yml \
  -i inventory/development.yml \
  --vault-password-file ~/.vault_pass \
  -e environment=development \
  -e "ansible_serial=2"  # Run 2 hosts in parallel
```

**Validation**:
- Gather feedback from dev team
- Adjust thresholds if needed
- Document any dev-specific settings

**Success**: Dev team confirms normal operations

### Phase 2c: Production Web Tier (Days 19-25)

**Target**: Production web servers (25% → 50% → 100%)
**Duration**: 7 days
**Risk**: Medium (mitigated by phased approach)

#### Week 1: 25% Rollout (Days 19-21)

```bash
# Create web tier inventory
cat > inventory/production-web.yml <<EOF
# First 25% of web servers
[production-web-phase-1]
web-prod-01 ansible_host=10.1.1.10
web-prod-02 ansible_host=10.1.1.11

[production-web-phase-1:vars]
environment=production

# Remaining 75% (deploy later)
[production-web-phase-2]
web-prod-03 ansible_host=10.1.1.12
web-prod-04 ansible_host=10.1.1.13
web-prod-05 ansible_host=10.1.1.14
web-prod-06 ansible_host=10.1.1.15

[production-web-phase-2:vars]
environment=production
EOF

# Phase 2c-1: Deploy to 25%
ansible-playbook site.yml \
  -i inventory/production-web.yml \
  --vault-password-file ~/.vault_pass \
  -e environment=production \
  -e "ansible_limit=production-web-phase-1"

# Monitor for 48 hours
for i in {1..4}; do
  echo "=== Monitoring Check $i (6 hours later) ==="
  ansible production-web-phase-1 -i inventory/production-web.yml -m ping
  ansible production-web-phase-1 -i inventory/production-web.yml -a "uptime"
  sleep 6h
done
```

**Monitoring Dashboard**:
- Track request latency
- Monitor error rates
- Check alert firing rates
- Verify no performance degradation

**Success Criteria**:
- Error rates within normal range
- Request latency unchanged
- No alert storms
- Rollback not needed

#### Week 2: 50% Rollout (Days 22-24)

```bash
# Phase 2c-2: Deploy to next 25% (now 50% total)
ansible-playbook site.yml \
  -i inventory/production-web.yml \
  --vault-password-file ~/.vault_pass \
  -e environment=production \
  -e "ansible_limit=production-web-phase-2[0:2]"  # First 3 of remaining

# Monitor for 48 hours
```

#### Week 3: 100% Rollout (Days 25+)

```bash
# Phase 2c-3: Deploy to remaining hosts
ansible-playbook site.yml \
  -i inventory/production-web.yml \
  --vault-password-file ~/.vault_pass \
  -e environment=production
```

### Phase 2d: Production Database Tier (Days 26-28)

**Target**: Production databases
**Duration**: 3 days
**Risk**: Medium-High (critical systems)

```bash
# Create database inventory
cat > inventory/production-db.yml <<EOF
[production-db-primary]
db-prod-01 ansible_host=10.1.2.10

[production-db-replica]
db-prod-02 ansible_host=10.1.2.11
db-prod-03 ansible_host=10.1.2.12

[production-db-primary:vars]
environment=production

[production-db-replica:vars]
environment=production
EOF

# Deploy replicas first, then primary
# This ensures ongoing availability

# 1. Deploy to replicas
ansible-playbook site.yml \
  -i inventory/production-db.yml \
  --vault-password-file ~/.vault_pass \
  -e environment=production \
  -e "ansible_limit=production-db-replica"

# Monitor replication for 24 hours
# Verify no replication lag

# 2. Deploy to primary (during maintenance window)
ansible-playbook site.yml \
  -i inventory/production-db.yml \
  --vault-password-file ~/.vault_pass \
  -e environment=production \
  -e "ansible_limit=production-db-primary"
```

### Phase 2e: Production Remaining Systems (Days 29-33)

Deploy to remaining production systems:
- Cache systems
- Load balancers
- Supporting services
- Management systems

```bash
# Final comprehensive rollout
ansible-playbook site.yml \
  -i inventory/production.yml \
  --vault-password-file ~/.vault_pass \
  -e environment=production
```

---

## Phase 3: Post-Deployment Validation (Days 34+)

### Week 1 After Deployment: Active Monitoring

**Daily**:
1. Review alert logs
2. Check compliance reports
3. Monitor application performance
4. Verify no unexpected errors

**Weekly**:
1. Analyze alert patterns
2. Review compliance scanning results
3. Adjust thresholds if needed
4. Conduct security audit

### Threshold Adjustment Strategy

```bash
# If alerts firing too frequently (> 10/hour):
# Increase threshold by 10%
ansible-playbook site.yml \
  -i inventory/production.yml \
  -e "alert_cpu_high=88" \
  -t monitoring_tuning

# If no alerts firing when expected:
# Decrease threshold by 10%
ansible-playbook site.yml \
  -i inventory/production.yml \
  -e "alert_cpu_high=82" \
  -t monitoring_tuning
```

### Monthly Review

- Review all compliance reports
- Analyze performance metrics
- Plan optimization opportunities
- Document lessons learned
- Update runbooks based on real incidents

---

## Rollback Procedures

If issues are discovered:

```bash
# Quick Rollback (restore previous version)
# Re-run playbook with previous version of role:

cd /path/to/ansible-infra
git checkout HEAD~1  # Go back one commit

# Run playbook again (idempotent, will revert changes)
ansible-playbook site.yml \
  -i inventory/staging.yml \
  --vault-password-file ~/.vault_pass

# Verify rollback
ssh staging-web-01 "sysctl kernel.kptr_restrict"
```

**Estimated Rollback Time**: < 5 minutes

---

## Communication Plan

### Pre-Deployment

- **1 Week Before**: Announce deployment plan to all teams
- **3 Days Before**: Detailed briefing for ops team
- **1 Day Before**: Final checklist review

### During Deployment

- **Per Phase**: Email update on completion status
- **Issues**: Immediate Slack notification to on-call team
- **Completion**: Email notification to all stakeholders

### Post-Deployment

- **Day 3**: Status report with monitoring data
- **Week 1**: Summary and lessons learned
- **Month 1**: Comprehensive review with recommendations

---

## Success Metrics

**Technical**:
- ✓ All deployments complete without errors
- ✓ No performance degradation
- ✓ All alerts functioning
- ✓ Compliance scanning active
- ✓ Zero unplanned rollbacks

**Operational**:
- ✓ All teams trained on new features
- ✓ Documentation complete and accurate
- ✓ Runbooks updated
- ✓ Monitoring dashboards active

**Business**:
- ✓ System availability maintained at 99.9%+
- ✓ No revenue impact
- ✓ Security posture improved
- ✓ Compliance requirements met

---

## Timeline Summary

```
Phase 0: Preparation        Days 1-3    (3 days)
Phase 1: Staging           Days 4-11    (8 days)
Phase 2a: Non-Critical     Days 12-14   (3 days)
Phase 2b: Development      Days 15-18   (4 days)
Phase 2c: Web Tier         Days 19-25   (7 days)
Phase 2d: Database Tier    Days 26-28   (3 days)
Phase 2e: Remaining        Days 29-33   (5 days)
Phase 3: Validation        Day 34+      (Ongoing)

Total: 4-5 weeks from start to 100% completion
```

---

**Ready to proceed with staging deployment!**

Contact your infrastructure team to begin Phase 0 preparation.

