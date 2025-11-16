# Implementation Guide

**Deploying ansible-infra Framework to Production**

---

## Overview

This guide walks through implementing the ansible-infra framework from initial setup through production deployment.

**Estimated Time**: 2-4 hours (depending on environment complexity)
**Prerequisites**: Ansible 2.15+, SSH access, basic infrastructure knowledge

---

## Phase 1: Planning & Preparation (30 minutes)

### 1.1 Assess Your Infrastructure

**Questions to Answer**:
1. How many servers will we deploy to? (5, 50, 500?)
2. Which operating systems? (Ubuntu, Debian, Rocky, macOS?)
3. What's the network architecture? (Single network, multi-site, cloud?)
4. Do we need monitoring? (Prometheus + Grafana?)
5. What's the security posture? (Defense-in-depth, enterprise, compliance-required?)

### 1.2 Choose Deployment Model

#### Model A: Linux-Only
```
Use Case: Web hosting, databases, cloud infrastructure
Roles:
├─ common (foundation)
├─ prometheus.prometheus (monitoring)
├─ grafana.grafana (dashboards)
└─ Custom roles (as needed)
```

#### Model B: Hybrid (Linux + macOS)
```
Use Case: Arnio, development teams with Macs
Roles:
├─ common (Linux + macOS)
├─ system_hardening_macos (macOS security)
├─ macos_monitoring (Mac metrics)
├─ prometheus.prometheus (Linux backend)
└─ grafana.grafana (centralized dashboards)
```

#### Model C: Kubernetes
```
Use Case: Container orchestration
Roles:
├─ common (node foundation)
├─ kubernetes setup (future)
└─ Custom roles (app-specific)
```

### 1.3 Plan Your Variables

**Create variable files** for your environment:

```bash
# For each environment
inventories/production/
├── group_vars/
│   ├── all.yml              # Global variables
│   ├── linux_servers.yml    # Linux-specific
│   └── macos_clients.yml    # macOS-specific
└── host_vars/
    ├── server1.yml          # Host-specific overrides
    └── mac01.yml
```

### 1.4 Review the Documentation

**Must Read** (30 minutes total):
- [ ] `README.md` - Project overview (5 min)
- [ ] `docs/QUICK_START.md` - Fast reference (5 min)
- [ ] `docs/ARCHITECTURE.md` - Design understanding (10 min)
- [ ] Role README (e.g., `roles/common/README.md`) (10 min)

---

## Phase 2: Environment Setup (30 minutes)

### 2.1 Clone Repository

```bash
# Clone ansible-infra
git clone <your-repo-url> ansible-infra
cd ansible-infra

# Verify structure
ls -la
# ├── Makefile
# ├── ansible.cfg
# ├── requirements.yml
# ├── roles/
# ├── playbooks/
# └── inventories/
```

### 2.2 Install Dependencies

```bash
# Install Ansible and collections
make install

# Or manually:
pip install ansible>=2.15
ansible-galaxy collection install -r requirements.yml
```

### 2.3 Setup Development Environment (Optional)

```bash
# For testing/development
make install-dev

# Installs:
# - Test tools (molecule, pytest, etc.)
# - Pre-commit hooks
# - Development dependencies
```

### 2.4 Verify Installation

```bash
# Check Ansible version
ansible --version

# Check collections installed
ansible-galaxy collection list

# Test connectivity
ansible all -i inventories/development/hosts.yml -m ping
```

---

## Phase 3: Inventory Configuration (30 minutes)

### 3.1 Update Inventory

Edit `inventories/production/hosts.yml`:

```yaml
---
all:
  children:
    linux_servers:
      hosts:
        web1:
          ansible_host: 192.168.1.10
          ansible_user: ubuntu
        db1:
          ansible_host: 192.168.1.11
          ansible_user: ubuntu

    macos_clients:
      hosts:
        mac01:
          ansible_host: mac01.internal
          ansible_user: admin
        mac02:
          ansible_host: mac02.internal
          ansible_user: admin
```

### 3.2 Configure Group Variables

Create `inventories/production/group_vars/`:

```yaml
# all.yml - Global configuration
---
ansible_port: 22
ansible_python_interpreter: /usr/bin/python3
become_method: sudo

# Common role variables
ntp_servers:
  - time.nist.gov
  - pool.ntp.org

ssh_port: 2222
```

```yaml
# linux_servers.yml - Linux-specific
---
# Prometheus configuration
prometheus_scrape_interval: 15s
node_exporter_port: 9100

# Updates
auto_updates_enabled: true
```

```yaml
# macos_clients.yml - macOS-specific
---
# Hardening
firewall_enabled: true
pf_ssh_rate_limit: 5
xprotect_enabled: true
sip_verify: true

# Monitoring
node_exporter_port: 9100
prometheus_backend: monitoring.internal:9090
```

### 3.3 Test Inventory

```bash
# Verify inventory loads correctly
ansible-inventory -i inventories/production/hosts.yml --list

# Test connectivity
ansible all -i inventories/production/hosts.yml -m ping
```

---

## Phase 4: Dry-Run Testing (30 minutes)

### 4.1 Check Mode (Dry-Run)

Always test before deployment:

```bash
# Simulate provision playbook (no changes made)
ansible-playbook playbooks/provision.yml \
  -i inventories/production/hosts.yml \
  --check \
  --diff

# Simulate configure playbook
ansible-playbook playbooks/configure.yml \
  -i inventories/production/hosts.yml \
  --check
```

### 4.2 Review Changes

```
Check mode output shows:
├─ CHANGED tasks (what would be modified)
├─ OK tasks (no changes needed)
└─ FAILED tasks (errors to fix)
```

If all look good → proceed to deployment

If errors appear → fix and re-run check mode

### 4.3 Run Playbooks Verbosely

```bash
# Dry-run with more detail
ansible-playbook playbooks/provision.yml \
  -i inventories/production/hosts.yml \
  --check \
  --diff \
  -vv
```

---

## Phase 5: Staging Deployment (1-2 hours)

### 5.1 Deploy to Staging First

```bash
# Provision staging servers
ansible-playbook playbooks/provision.yml \
  -i inventories/staging/hosts.yml \
  -v

# Monitor output for any issues
# Should see:
# ├─ Gathering facts
# ├─ Common role tasks
# ├─ Service configuration
# └─ PLAY RECAP (all success)
```

### 5.2 Verify Staging Deployment

```bash
# Test connectivity
make test-connectivity

# Check specific services
ansible staging_servers -m command -a "sudo systemctl status ssh"

# For macOS
ansible macos_staging -m shell -a "spctl --status"
```

### 5.3 Run Tests in Staging

```bash
# Run full test suite
make test

# Verify:
# ├─ Linting passed
# ├─ Syntax valid
# ├─ All role tests passed
# ├─ Security scan clean
# ├─ Documentation complete
# └─ Coverage 95%+
```

### 5.4 Manual Validation

```bash
# SSH into staging server
ssh -i /path/to/key admin@staging-server

# Verify key services running
ps aux | grep sshd
sudo systemctl status ssh
sudo pfctl -s all      # macOS firewall

# Check logs
sudo tail -f /var/log/auth.log
sudo log show --predicate 'process == "sshd"'  # macOS

# Verify firewall
sudo pfctl -sr          # Show rules
```

### 5.5 Performance Baseline

```bash
# Before deploying to production, establish baseline
ansible all -i inventories/staging/hosts.yml -m shell \
  -a "df -h && free -m && top -bn1"

# Note CPU, memory, disk usage for comparison
```

---

## Phase 6: Production Deployment (1-2 hours)

### 6.1 Production Check Mode

```bash
# One final check before production
ansible-playbook playbooks/provision.yml \
  -i inventories/production/hosts.yml \
  --check \
  --diff

# Verify ALL changes are expected
# If anything unexpected → investigate and fix
```

### 6.2 Production Deployment Strategy

**Option A: Immediate Rollout**
```bash
# Deploy to all servers at once
ansible-playbook playbooks/provision.yml \
  -i inventories/production/hosts.yml \
  -v
```

**Option B: Gradual Rollout** (Recommended)
```bash
# Deploy to first server (test)
ansible-playbook playbooks/provision.yml \
  -i inventories/production/hosts.yml \
  -l "prod_server1" \
  -v

# Monitor for 30 minutes, verify stable

# Deploy to batch of servers
ansible-playbook playbooks/provision.yml \
  -i inventories/production/hosts.yml \
  -l "prod_servers_batch2" \
  -v

# Repeat for remaining servers
```

### 6.3 Monitor During Deployment

```bash
# Watch deployment progress
watch -n1 ansible all -i inventories/production/hosts.yml -m ping

# Monitor logs on each server
for server in prod1 prod2 prod3; do
  ssh $server "sudo tail -f /var/log/auth.log" &
done

# Monitor firewall rules (macOS)
for mac in mac1 mac2; do
  ssh $mac "sudo pfctl -sr" | head -20 &
done
```

### 6.4 Post-Deployment Verification

```bash
# Verify all servers responding
ansible all -i inventories/production/hosts.yml -m ping

# Verify specific services
ansible production_servers -m service -a "name=ssh state=started"

# Check connectivity to other services
ansible all -m shell -a "curl -s https://example.com | head -5"

# Verify firewall is working
ansible macos_production -m shell -a "pfctl -s all | grep ssh"
```

---

## Phase 7: Configuration Playbook (30 minutes)

### 7.1 Apply Configuration

After provision succeeds, apply full configuration:

```bash
# Apply configuration to all servers
ansible-playbook playbooks/configure.yml \
  -i inventories/production/hosts.yml \
  -v

# This includes:
# ├─ System hardening (macOS)
# ├─ Monitoring setup
# ├─ Service configuration
# ├─ Logging configuration
# └─ Security controls
```

### 7.2 Verify Configuration

```bash
# Verify hardening applied (macOS)
ansible macos_production -m shell -a "csrutil status"
# Output: System Integrity Protection status: enabled.

ansible macos_production -m shell -a "spctl --status"
# Output: assessments enabled

# Verify firewall rules
ansible macos_production -m shell -a "sudo pfctl -sr | grep ssh"

# Verify SSH hardening
ansible all -m shell -a "sudo sshd -T | grep -i kexalgorithms"
```

---

## Phase 8: Monitoring Setup (Optional, 1-2 hours)

### 8.1 Configure Prometheus

If using monitoring stack:

```yaml
# inventories/production/group_vars/prometheus_server.yml
---
prometheus_scrape_interval: 15s
prometheus_retention: 30d

prometheus_alertmanager_config:
  - targets: ['alertmanager.internal:9093']

prometheus_rule_files:
  - '/etc/prometheus/rules/*.yml'
```

### 8.2 Configure Grafana

```yaml
# inventories/production/group_vars/grafana_server.yml
---
grafana_admin_password: "{{ vault_grafana_password }}"
grafana_datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus.internal:9090

grafana_dashboards:
  - name: System Overview
    dashboard_id: 1860  # Node Exporter Dashboard
```

### 8.3 Deploy Monitoring

```bash
# Use official collections for monitoring
ansible-playbook monitoring_setup.yml \
  -i inventories/production/hosts.yml \
  -v
```

---

## Phase 9: Maintenance & Updates (Ongoing)

### 9.1 Regular Maintenance

```bash
# Weekly maintenance
ansible-playbook playbooks/maintenance.yml \
  -i inventories/production/hosts.yml \
  --tags "updates,logs"

# This includes:
# ├─ System updates
# ├─ Log rotation
# ├─ Cache cleanup
# └─ Health checks
```

### 9.2 Configuration Changes

```bash
# Update variables
vim inventories/production/group_vars/all.yml

# Test in staging
ansible-playbook playbooks/configure.yml \
  -i inventories/staging/hosts.yml \
  --check

# Deploy to production
ansible-playbook playbooks/configure.yml \
  -i inventories/production/hosts.yml \
  -v
```

### 9.3 Role Updates

```bash
# Update ansible-infra repository
git pull origin main

# Update collections
ansible-galaxy collection install -r requirements.yml --upgrade

# Test updated roles
make molecule-test

# Deploy updates
ansible-playbook playbooks/provision.yml \
  -i inventories/production/hosts.yml \
  --check
```

---

## Troubleshooting

### SSH Connection Issues

```bash
# Check SSH is running
ansible all -i inventories/production/hosts.yml -m ping

# If fails, verify manually
ssh -vvv -i /path/to/key user@server

# Check SSH config on server
sudo sshd -T | grep -i port
```

### Ansible Permission Issues

```bash
# Add -b flag for become/sudo
ansible-playbook playbooks/provision.yml \
  -i inventories/production/hosts.yml \
  -b \
  -u ubuntu

# Or configure in inventory
# ansible_become: yes
# ansible_become_user: root
```

### Firewall Blocking Deployment

```bash
# Temporarily disable firewall for testing
ansible macos_servers -m shell -a "sudo pfctl -d"

# Deploy
ansible-playbook playbooks/provision.yml \
  -i inventories/production/hosts.yml \
  -v

# Re-enable firewall
ansible macos_servers -m shell -a "sudo pfctl -e"
```

### Idempotence Issues

```bash
# Run playbook multiple times (should show no changes)
ansible-playbook playbooks/configure.yml \
  -i inventories/production/hosts.yml \
  -v

# Second run should show:
# PLAY RECAP
# ├─ server1 : ok=15  changed=0
# └─ server2 : ok=15  changed=0
```

---

## Implementation Checklist

### Pre-Deployment
- [ ] Inventory configured and tested
- [ ] Group variables customized for your environment
- [ ] Check mode run without errors
- [ ] Staging deployment successful
- [ ] All tests passing (lint, syntax, security)
- [ ] Team trained on framework
- [ ] Backup plan documented

### Deployment
- [ ] Production check mode run
- [ ] Gradual rollout strategy chosen
- [ ] Monitoring enabled
- [ ] Post-deployment verification done
- [ ] Configuration playbook applied
- [ ] All services verified running

### Post-Deployment
- [ ] Monitoring dashboards verified
- [ ] Logs being collected
- [ ] Alerts configured
- [ ] Maintenance schedule established
- [ ] Team trained on operations
- [ ] Documentation updated
- [ ] Success metrics established

---

## Rollback Plan

If deployment fails or issues occur:

```bash
# Option 1: Revert configuration
git revert <commit-hash>
ansible-playbook playbooks/configure.yml \
  -i inventories/production/hosts.yml \
  -v

# Option 2: Restore from backup
# (If infrastructure as code + snapshots)
```

---

## Success Metrics

After deployment, verify:

- ✅ All servers reporting to monitoring
- ✅ Firewall rules active and working
- ✅ SSH hardening in place (post-quantum algorithms)
- ✅ Audit logging capturing events
- ✅ System updates running on schedule
- ✅ Performance baseline matched or improved
- ✅ Zero security incidents
- ✅ Team comfortable with operations

---

## Next Steps After Implementation

1. **Monitor Production** - Establish baseline, watch for anomalies
2. **Optimize Configuration** - Fine-tune variables based on metrics
3. **Add Custom Roles** - Extend framework for client-specific needs
4. **Scale Infrastructure** - Add more servers following same process
5. **Continuous Improvement** - Review quarterly, update standards

---

**Estimated Total Implementation Time**: 4-6 hours (all phases)

**Support**: Refer to docs/, roles/ directories for detailed guidance
**Status**: Ready for production deployment

**Last Updated**: November 15, 2025
