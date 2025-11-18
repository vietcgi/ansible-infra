# Common Role Enhancements - High-Priority Gap Implementation

**Date**: November 17, 2025
**Version**: 1.0
**Status**: Production Ready

---

## Overview

This document describes the four high-priority enhancements added to the `common` role to address critical infrastructure gaps identified in the comprehensive role analysis.

### What Was Added

1. **Hostname and Domain Configuration** (`hostname_domain.yml`)
2. **Swap Management** (`swap_management.yml`)
3. **Encryption at Rest** (`encryption_at_rest.yml`)
4. **Change Tracking and Baseline Snapshots** (`change_tracking.yml`)

---

## 1. Hostname and Domain Configuration

### Purpose

Sets system hostname and domain name, which is fundamental for:
- DNS resolution and service discovery
- Distributed systems coordination
- Logging and monitoring (appears in system logs)
- SSL/TLS certificate generation
- Multi-system deployments

### Configuration

```yaml
# roles/common/defaults/main.yml
common_hostname: "{{ inventory_hostname }}"  # Defaults to Ansible inventory name
common_domain: ""                             # Optional: domain name (e.g., "example.com")
common_configure_hosts_file: true             # Update /etc/hosts automatically
```

### Usage Example

```yaml
# In your inventory or host_vars
---
myserver-1:
  ansible_host: 192.168.1.10
  common_hostname: "myserver-1"
  common_domain: "example.com"

# Results in:
# - Hostname: myserver-1
# - FQDN: myserver-1.example.com
# - /etc/hosts entry: 127.0.0.1 myserver-1 localhost
```

### What It Does

- Sets system hostname via `hostnamectl` (Linux) or `scutil` (macOS)
- Updates `/etc/hostname` (persistent on reboot)
- Configures `/etc/hosts` for local resolution
- Configures systemd-resolved domain settings (if systemd-resolved is in use)
- Validates hostname resolution after configuration

### Verification

```bash
# Check hostname configuration
hostname
hostname -f      # Full FQDN
hostname -s      # Short name

# Check /etc/hosts
cat /etc/hosts | grep 127.0.0.1

# Check DNS resolution
getent hosts $(hostname)
```

---

## 2. Swap Management

### Purpose

Manages swap space for systems requiring:
- Handling temporary memory spikes
- Graceful degradation under load
- Performance tuning for specific workloads
- Optional encryption for sensitive data

### Configuration

```yaml
# roles/common/defaults/main.yml

# Create swap space
common_swap_size: 4                          # Size in GB (0 = disabled)
common_disable_swap: false                   # Set true to remove all swap

# Performance tuning
common_swap_swappiness: 30                   # 0-100: balance between RAM and swap
common_swap_vfs_cache_pressure: 50           # Memory pressure on cache

# Encryption (optional)
common_encrypt_swap: false                   # Enable LUKS encryption
common_swap_device: ""                       # Device for encrypted swap
```

### Usage Scenarios

**Scenario 1: High-Performance Server (SSD-based)**
```yaml
common_swap_size: 0                          # Disable swap
common_swap_swappiness: 0                    # Never use swap
```

**Scenario 2: Standard Server**
```yaml
common_swap_size: 4                          # 4GB swap
common_swap_swappiness: 30                   # Balanced (default)
```

**Scenario 3: Memory-Constrained System**
```yaml
common_swap_size: 16                         # Large swap pool
common_swap_swappiness: 60                   # Prefer swap
```

**Scenario 4: Security-Sensitive (Encrypted)**
```yaml
common_swap_size: 4
common_encrypt_swap: true                    # Encrypt swap with LUKS
common_swap_device: "/dev/sdb1"              # Use dedicated device
```

### What It Does

- Creates swap file using `fallocate` (fast) or `dd` (compatible)
- Enables swap space
- Configures `/etc/fstab` for persistent swap
- Tunes kernel parameters (`vm.swappiness`, `vm.vfs_cache_pressure`)
- Optionally encrypts swap with LUKS2
- Disables all swap if `common_disable_swap: true`

### Swappiness Values Guide

| Value | Behavior | Use Case |
|-------|----------|----------|
| 0-10 | Minimize swap, prefer RAM | SSD-based, high-performance systems |
| 30 | Balanced | General-purpose servers (recommended) |
| 60-100 | Prefer swap | Memory-constrained, HDD-based systems |

### Verification

```bash
# Check swap status
swapon --show

# Check swappiness
cat /proc/sys/vm/swappiness

# Monitor swap usage
free -h
vmstat 1 5    # Watch swap in/out rates

# Verify swap in fstab
grep swap /etc/fstab
```

---

## 3. Encryption at Rest

### Purpose

Provides data protection at rest for:
- Sensitive logs and audit trails
- User home directories
- Temporary swap space
- Full-disk encryption (macOS FileVault)

### Configuration

```yaml
# roles/common/defaults/main.yml

# Master encryption enable
common_encryption_enabled: false             # Enable encryption features

# Directory encryption
common_encrypt_home: false                   # Encrypt /home
common_encrypt_logs: false                   # Encrypt /var/log
common_encrypt_swap: false                   # Encrypt swap space

# Size configuration
common_encryption_home_size: 20              # Size for /home (GB)
common_encryption_log_size: 5                # Size for /var/log (GB)

# Key management
common_encryption_key_storage: "/etc/crypt_keys"  # Secure key location
common_encryption_log_retention: 90          # Keep logs for N days
```

### Implementation Status

⚠️ **IMPORTANT**: The current implementation is a **template/reference**. Production encryption requires:

1. **Planning Phase**
   - Identify volumes to encrypt
   - Plan partition layout
   - Document key management
   - Design recovery procedures

2. **Pre-Deployment**
   - Full system backup
   - Boot media preparation
   - Recovery key generation

3. **Execution**
   - Create LVM logical volumes
   - Format with LUKS2
   - Mount encrypted volumes
   - Restore data (if upgrading existing system)

4. **Post-Deployment**
   - Document encryption setup
   - Test recovery procedures
   - Train operations team
   - Secure key storage

### Encryption Methods

**Option 1: LUKS Full-Disk Encryption**
```bash
# Requires: Initial OS installation with encryption option
# Encrypts: All data on boot device
# Supported: Ubuntu, Debian, CentOS, RHEL (with full-disk setup)
```

**Option 2: LUKS Partition Encryption**
```bash
# Encrypts specific partitions (/home, /var/log, etc.)
# Advantages: Flexible, per-partition keys
# Disadvantages: More complex to manage
```

**Option 3: FileVault (macOS)**
```yaml
common_encryption_enabled: true              # Enables check
# Actual activation: System Preferences → Security & Privacy → FileVault
```

### Verification

```bash
# Check encrypted volumes
cryptsetup status /dev/mapper/crypt_*

# Check mount options
mount | grep /dev/mapper

# Verify LUKS headers
cryptsetup luksDump /dev/sdaX

# Test recovery
cryptsetup luksOpen /dev/sdaX test_recovery
mount /dev/mapper/test_recovery /mnt/test
```

### Security Considerations

⚠️ **Key Management**
- Store encryption keys securely (not on encrypted volume!)
- Consider key escrow for disaster recovery
- Rotate keys annually
- Document recovery procedures

⚠️ **Performance Impact**
- LUKS adds minimal CPU overhead (hardware AES available)
- Minimal disk I/O impact
- Memory overhead: ~1-2 MB per encrypted volume

⚠️ **Recovery Risk**
- Lost keys = lost data
- Test recovery before production deployment
- Keep recovery media accessible

---

## 4. Change Tracking and Baseline Snapshots

### Purpose

Provides configuration drift detection and change audit trail for:
- Compliance (SOC2, PCI DSS, HIPAA)
- Security incident investigation
- Configuration validation
- Unauthorized change detection

### Configuration

```yaml
# roles/common/defaults/main.yml

# Enable/disable change tracking
common_enable_change_tracking: true          # Master enable flag

# Tracking options
common_track_package_changes: true           # Monitor installed packages
common_track_configuration_changes: true     # Monitor config files
common_track_security_changes: true          # Monitor security settings
common_track_service_changes: true           # Monitor service status

# Automation
common_change_tracking_schedule: "daily"     # Frequency: daily, weekly, monthly
common_change_detection_interval_hours: 24   # Hours between scans

# Storage
common_baseline_location: "/var/lib/ansible-baseline"
common_change_log_location: "/var/log/ansible-changes"
common_change_tracking_retention_days: 90    # Keep reports for N days
```

### What Gets Captured

#### Baseline Snapshot (created once)

1. **OS Information**
   - Hostname, OS family, kernel version
   - Architecture, CPU count, memory

2. **Installed Packages**
   - Complete list (dpkg, rpm, brew)
   - Package versions
   - Installation date

3. **Configuration Files**
   - SHA256 checksums of `/etc/*.conf` files
   - Allows detection of manual edits

4. **Service Status**
   - List of systemd services
   - Running status, enabled/disabled

5. **Security Configuration**
   - SSH settings (port, auth methods)
   - Firewall rules
   - SELinux/AppArmor status

#### Change Detection (daily)

- Compares current state to baseline
- Identifies new/removed packages
- Detects configuration file modifications
- Reports security setting changes
- Verifies baseline integrity

### Usage

**View Latest Baseline**
```bash
# List baseline files
ls -lh /var/lib/ansible-baseline/

# Check baseline status
cat /var/lib/ansible-baseline/os_baseline.txt
cat /var/lib/ansible-baseline/configs/checksums.sha256
```

**Run Change Detection**
```bash
# Manual check
/var/lib/ansible-baseline/check_changes.sh

# View latest report
cat /var/log/ansible-changes/change_report_*.txt

# View change log
cat /var/log/ansible-changes/CHANGELOG.md
```

**Automated Detection**
```bash
# Check systemd timer status
systemctl list-timers | grep ansible-change-check

# View timer logs
journalctl -u ansible-change-check.service -n 50

# Manually trigger timer
systemctl start ansible-change-check.service
```

### Change Log Format

```markdown
# Configuration Change Log

| Date | Component | Change | Reason | Status |
|------|-----------|--------|--------|--------|
| 2025-01-15 | SSH | Port changed 22→2222 | Security hardening | ✓ Approved |
| 2025-01-14 | Packages | nginx upgraded 1.24→1.25 | Security patch | ✓ Auto |
| 2025-01-13 | Firewall | Port 443 allowed | New service | ⚠ Pending review |
```

### Drift Detection Workflow

```
1. Baseline Created
   └─ Snapshot taken
      └─ Stored in /var/lib/ansible-baseline/

2. Configuration Changes Made
   └─ Manual edits, package updates, etc.

3. Change Detection Runs (daily)
   └─ Compares current state to baseline
      └─ Generates change report

4. Review Report
   └─ Identify unexpected changes
      └─ Investigate deviations

5. Approve or Remediate
   └─ Update baseline if changes approved
   └─ Revert if changes unauthorized

6. Document
   └─ Record in CHANGELOG.md
      └─ Maintain audit trail
```

### Verification

```bash
# Verify change tracking is active
systemctl is-active ansible-change-check.timer

# Check when last scan ran
ls -lh /var/log/ansible-changes/change_report_*.txt

# View current baseline hash
cat /var/lib/ansible-baseline/baseline_hash.txt

# Run manual check
/var/lib/ansible-baseline/check_changes.sh
```

---

## Integration with Existing Framework

### Task Execution Order

The new tasks are executed in this order (before PHASE 1):

```
Core Foundation (original)
├─ OS validation
├─ System updates
├─ Core packages
├─ Python runtime
├─ User management
├─ Chrony/NTP
├─ SSH hardening
├─ Sysctl tuning
├─ Audit logging
├─ File limits
├─ DNS configuration
└─ Logging

NEW: Core Foundation Additions
├─ Hostname & Domain Configuration
├─ Swap Management
├─ Encryption at Rest
└─ Change Tracking & Baseline Snapshots

PHASE 1: Security, Monitoring, and Backup
├─ Firewall
├─ Fail2ban
├─ ... (rest of PHASE 1)
```

### How to Enable/Disable

**Example 1: Enable only change tracking**
```yaml
# roles/common/defaults/main.yml or group_vars/all
common_enable_change_tracking: true
common_swap_size: 0                    # Disable swap management
common_encryption_enabled: false       # Disable encryption
```

**Example 2: Enable encryption only**
```yaml
common_encryption_enabled: true
common_encrypt_home: true
common_encrypt_logs: true
common_enable_change_tracking: false   # Disable tracking
```

**Example 3: Selective hostnames**
```yaml
# group_vars/webservers
common_hostname: "web-{{ inventory_hostname_short }}"
common_domain: "example.com"

# group_vars/databases
common_hostname: "db-{{ inventory_hostname_short }}"
common_domain: "example.com"
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Review configuration defaults
- [ ] Customize for your environment
- [ ] Test in non-production first
- [ ] Create full system backups (encryption)
- [ ] Document any deviations from defaults
- [ ] Plan key management (encryption)

### Deployment

- [ ] Run in `--check` mode first: `ansible-playbook -i inventory playbook.yml --check`
- [ ] Review proposed changes
- [ ] Deploy to test systems
- [ ] Monitor first deployment closely
- [ ] Deploy to production

### Post-Deployment

- [ ] Verify hostname configuration: `hostname -f`
- [ ] Verify swap: `swapon --show` and `free -h`
- [ ] Verify change tracking: `/var/lib/ansible-baseline/check_changes.sh`
- [ ] Document baseline state
- [ ] Update runbooks with new procedures
- [ ] Train operations team

---

## Troubleshooting

### Hostname Issues

```bash
# Problem: Hostname not set
# Solution: Check ansible_hostname variable
ansible all -i inventory -m debug -a "var=ansible_hostname"

# Manually set hostname
sudo hostnamectl set-hostname myserver-1
sudo hostnamectl set-hostname myserver-1.example.com --transient
```

### Swap Issues

```bash
# Problem: Swap not created
# Solution: Check disk space
df -h

# Create swap manually
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Verify
swapon --show
```

### Encryption Issues

```bash
# Problem: LUKS device not found
# Solution: Verify cryptsetup
cryptsetup --version

# List encrypted devices
cryptsetup status /dev/mapper/*

# Manual unlock
cryptsetup luksOpen /dev/sdaX crypt_device --key-file /etc/crypt_key.file
```

### Change Tracking Issues

```bash
# Problem: Change detection not running
# Solution: Check timer
systemctl list-timers ansible-change-check.timer

# Check service logs
journalctl -u ansible-change-check.service -n 100

# Run manually
sudo /var/lib/ansible-baseline/check_changes.sh

# Verify permissions
ls -la /var/lib/ansible-baseline/
ls -la /var/log/ansible-changes/
```

---

## Performance Impact

### CPU

| Feature | Impact |
|---------|--------|
| Hostname | Negligible |
| Swap Management | Negligible |
| Encryption | <5% (LUKS with AES-NI) |
| Change Tracking | <1% (daily task) |

### Disk

| Feature | Usage |
|---------|-------|
| Baseline Snapshot | ~50-100 MB |
| Change Reports (90 days) | ~100-200 MB |
| Encryption Keys | <1 MB |

### Memory

| Feature | Usage |
|---------|-------|
| Swap Space | Varies (0-common_swap_size GB) |
| Change Detection | ~20 MB (temporary) |
| LUKS Overhead | ~1-2 MB per volume |

---

## Security Considerations

### Hostname
- ✅ Public information (appears in logs, DNS)
- ✅ Can contain environment info (dev, staging, prod)
- ⚠️ Don't expose sensitive information in hostname

### Swap
- ✅ Encryption available via LUKS
- ⚠️ Unencrypted swap = readable memory dumps
- ✅ Swappiness tuning improves performance

### Encryption at Rest
- ✅ Protects data from physical access
- ⚠️ Does NOT protect data in memory
- ⚠️ Key management is critical
- ✅ LUKS2 is cryptographically sound

### Change Tracking
- ✅ Detects unauthorized modifications
- ✅ Creates audit trail for compliance
- ⚠️ Requires secure storage of baseline/reports
- ✅ Validates configuration integrity

---

## References

- [Hostname Configuration (Linux)](https://man.archlinux.org/man/hostnamectl.1)
- [systemd-resolved](https://man.archlinux.org/man/resolved.conf.5)
- [Swap Management](https://wiki.archlinux.org/title/Swap)
- [LUKS Encryption](https://wiki.archlinux.org/title/Dm-crypt/Encrypting_an_entire_system)
- [Change Auditing](https://linux-audit.com/)

---

**Last Updated**: November 17, 2025
**Maintained By**: Infrastructure Team
**Status**: Production Ready
