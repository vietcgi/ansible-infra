# Common Role 100% Completion Roadmap

**Date**: November 17, 2025
**Status**: 4 of 15 items complete (27%)
**Progress**: CRITICAL PHASE COMPLETE → CONTINUING HIGH/MEDIUM

---

## Implementation Progress

### Completed (4 items)
- ✅ **kernel_hardening.yml** - Advanced kernel security parameters (ASLR, ptrace, module restrictions)
- ✅ **password_policy.yml** - PAM + login.defs hardening (14+ char, complexity, account lockout)
- ✅ **backup_recovery_testing.yml** - Automated restore validation with weekly testing
- ✅ **compliance_scanning.yml** - CIS/NIST validation (lynis, AIDE, OpenSCAP, samhain)
- ✅ **pam-pwquality.j2** - PAM password quality configuration template
- ✅ **kernel-blacklist.j2** - Kernel module blacklist template

### In Progress (0 items)

### Remaining (11 items - 73%)

---

## Detailed Implementation Plan

### PHASE 1: Critical Security (2 of 5 complete - 40%)

#### Item 1: storage_hardening.yml (2 hours) ⏳
**Status**: PENDING
**Purpose**: Mount options, disk encryption, quotas

**Includes**:
- `/tmp` hardening (tmpfs with noexec, nosuid, nodev)
- `/var` noexec mounting (prevent executable uploads)
- Swap encryption with `cryptsetup`
- Disk usage monitoring and alerts (85%, 95%, 99%)
- Filesystem integrity checks
- Disk quota enforcement
- LVM configuration and monitoring

**Templates needed**:
- `mount-hardening.j2` - Fstab entries
- `disk-monitoring.j2` - Monitoring rules

**Dependencies**: None
**Estimated effort**: 2 hours

---

### PHASE 2: Enhanced Configuration (0 of 5 complete - 0%)

#### Item 2: Enhance firewall.yml (2 hours) ⏳
**Current state**: Ingress rules + DDoS protection
**Enhancements needed**:
- Add egress filtering rules
- IPv6 hardening (separate from IPv4)
- Connection rate limiting
- Packet logging to syslog
- UFW logging integration
- Connection state tracking (SYN cookies)

**Changes**:
```yaml
# Add to firewall.yml
- name: Enable firewall packet logging
- name: Configure egress rules
- name: Add IPv6 hardening rules
- name: Enable connection rate limiting
```

**Estimated effort**: 2 hours

---

#### Item 3: Enhance logging.yml (2 hours) ⏳
**Current state**: Basic rsyslog
**Enhancements needed**:
- Remote syslog server configuration with TLS
- Log encryption (TLS certificates)
- Centralized log aggregation validation
- Log rotation policy enforcement
- Tamper protection for audit logs
- Log integrity verification

**New tasks**:
```yaml
- name: Configure remote syslog with TLS
- name: Enforce log rotation policies
- name: Setup log integrity monitoring
- name: Validate central logging connection
```

**Estimated effort**: 2 hours

---

#### Item 4: Enhance vault_secrets_rotation_wrapper.yml (1 hour) ⏳
**Current state**: Vault installation + PKI
**Enhancements needed**:
- Automated rotation verification after rotation
- Failed rotation alerting
- Secrets access audit trail
- Automatic credential revocation on compromise
- Test rotated secrets functionality

**Additions**:
```yaml
- name: Verify secrets after rotation
- name: Alert on rotation failures
- name: Query vault audit logs
```

**Estimated effort**: 1 hour

---

#### Item 5: Enhance docker_security_wrapper.yml (2 hours) ⏳
**Current state**: Docker basic hardening
**Enhancements needed**:
- Image vulnerability scanning (Trivy)
- Container runtime security (Falco)
- Image signing/verification (Notary)
- Registry authentication validation
- Supply chain security (SBOM)
- Secrets scanning in images

**Additions**:
```yaml
- name: Install Trivy image scanner
- name: Scan Docker images on build
- name: Deploy Falco runtime security
- name: Generate SBOM for images
```

**Estimated effort**: 2 hours

---

### PHASE 3: Operational Excellence (0 of 5 complete - 0%)

#### Item 6: performance_tuning.yml (3 hours) ⏳
**Purpose**: System-wide performance optimization

**Includes**:
- CPU scheduler optimization (cgroup v2)
- Memory management (`vm.swappiness`, `vm.dirty_ratio`)
- I/O scheduler tuning (deadline, noop)
- Network buffer optimization
- Database-specific tuning (PostgreSQL/MySQL)
- Cache optimization
- THP (Transparent Huge Pages) configuration
- CPU governor configuration

**Templates needed**:
- `cpu-tuning.j2` - CPU scheduler settings
- `memory-tuning.j2` - Memory parameters
- `io-tuning.j2` - I/O optimization
- `db-tuning.j2` - Database parameters

**Estimated effort**: 3 hours

---

#### Item 7: monitoring_tuning.yml (3 hours) ⏳
**Purpose**: Alert configuration and optimization

**Includes**:
- Alert severity levels and routing
- Runbook integration with alerts
- Alert deduplication/silencing rules
- On-call rotation configuration
- Escalation policies
- Synthetic monitoring (uptime checks)
- Performance baseline establishment
- Predictive alerting (anomaly detection)

**Templates needed**:
- `alert-routing.j2` - Alert rules
- `thresholds.j2` - Alert thresholds
- `runbook-mapping.j2` - Alert-to-runbook mapping

**Estimated effort**: 3 hours

---

#### Item 8: compliance_automation.yml (4 hours) ⏳
**Purpose**: Continuous compliance checking

**Includes**:
- FedRAMP compliance validation
- HIPAA compliance checks
- SOC 2 compliance automation
- PCI-DSS scanning
- Audit log tamper detection
- Compliance exception tracking
- Audit trail correlation
- Automated remediation for violations

**Templates needed**:
- `fedora-compliance.j2` - FedRAMP rules
- `hipaa-compliance.j2` - HIPAA checks
- `pci-compliance.j2` - PCI-DSS validation

**Estimated effort**: 4 hours

---

### PHASE 4: Integration & Testing (0 of 2 complete - 0%)

#### Item 9: Update main.yml (1 hour) ⏳
**Purpose**: Include all new task files

**Changes**:
```yaml
# In roles/common/tasks/main.yml
- ansible.builtin.include_tasks: kernel_hardening.yml
  when: common_kernel_hardening_enabled | default(true)

- ansible.builtin.include_tasks: password_policy.yml
  when: common_password_policy_enabled | default(true)

- ansible.builtin.include_tasks: backup_recovery_testing.yml
  when: backup_enabled | default(false)

- ansible.builtin.include_tasks: compliance_scanning.yml
  when: common_compliance_scanning_enabled | default(true)

- ansible.builtin.include_tasks: storage_hardening.yml
  when: common_storage_hardening_enabled | default(true)

# ... and 5 more enhancements
```

**Estimated effort**: 1 hour

---

#### Item 10: Update defaults/main.yml (1 hour) ⏳
**Purpose**: Add all new variables

**New variables**:
```yaml
# Kernel hardening
common_kernel_hardening_enabled: true
kernel_modules_to_blacklist:
  - usb_storage
  - bluetooth
  - dccp

# Password policy
common_password_policy_enabled: true
password_min_length: 14
password_max_age: 90

# Storage hardening
common_storage_hardening_enabled: true
storage_tmpfs_options: "noexec,nosuid,nodev"
disk_usage_alert_threshold: 85

# Compliance
common_compliance_scanning_enabled: true
compliance_scan_schedule: "0 1 * * 0"  # Weekly

# ... and 50+ more variables
```

**Estimated effort**: 1 hour

---

### PHASE 5: Validation (0 of 1 complete - 0%)

#### Item 11: Run comprehensive tests (4 hours) ⏳
**Purpose**: Ensure all changes work correctly

**Tests**:
1. Syntax validation (`ansible-lint`)
2. Role execution on all OS variants (10 scenarios)
3. Idempotency testing (run twice, verify no changes)
4. Template rendering validation
5. Handler execution verification
6. Variable precedence checking
7. Integration testing with other roles
8. Compliance validation (lynis, OpenSCAP)

**Process**:
```bash
# Syntax check
ansible-lint roles/common/

# Molecule testing
cd roles/common
molecule test

# Idempotency check
ansible-playbook playbooks/test.yml --check
ansible-playbook playbooks/test.yml
ansible-playbook playbooks/test.yml
# Both runs should show 0 changed
```

**Estimated effort**: 4 hours

---

## Timeline & Resource Allocation

### Week 1 (This Week)
- **Mon-Tue**: PHASE 1 - Storage hardening + Phase 2 Part 1 (firewall, logging)
- **Wed-Thu**: PHASE 2 Part 2 (vault, docker) + PHASE 3 Part 1 (performance)
- **Fri**: PHASE 3 Part 2 (monitoring, compliance) + Integration

### Week 2
- **Mon-Tue**: Full validation & testing
- **Wed**: Documentation & runbooks
- **Thu-Fri**: Buffer for fixes & refinements

**Total estimated effort**: 30 hours
**Parallel opportunity**: Many items can be implemented in parallel

---

## Critical Path (Fastest Route)

If focusing on maximum impact with minimum time:

1. **Day 1**: Storage hardening + Firewall enhancement (4 hours)
2. **Day 2**: Compliance automation + Performance tuning (7 hours)
3. **Day 3**: Integration + Initial testing (4 hours)
4. **Day 4**: Full testing + Fixes (4 hours)

**Minimum viable 100%**: 19 hours

---

## Quality Assurance Checklist

Before marking 100% complete:

- [ ] All 11 remaining task files created with proper Ansible best practices
- [ ] All 15+ supporting templates created
- [ ] All variables added to defaults/main.yml
- [ ] All tasks included in main.yml with proper conditions
- [ ] ansible-lint passes with no errors or warnings
- [ ] Molecule tests pass on all 10 OS scenarios
- [ ] Idempotency verified (run 3 times, 3rd shows 0 changed)
- [ ] Handler execution verified
- [ ] Integration tests pass with other roles
- [ ] CIS benchmark compliance validated (lynis)
- [ ] NIST compliance verified (OpenSCAP)
- [ ] No regressions in existing functionality
- [ ] All handlers defined and tested
- [ ] Proper use of `changed_when` and `failed_when`
- [ ] All sensitive tasks tagged with `no_log` where appropriate
- [ ] Documentation updated (README, variable reference)
- [ ] Git history clean with proper commit messages
- [ ] All quality gates pass (pre-commit hooks)
- [ ] Code review completed (if applicable)

---

## Dependencies Between Items

```
Item 1: Kernel Hardening
  └─ No dependencies

Item 2: Password Policy
  └─ Depends on: PAM libraries (auto-installed)

Item 3: Backup Testing
  └─ Depends on: Backup client (Item 19)

Item 4: Compliance Scanning
  └─ Depends on: None

Item 5: Storage Hardening
  └─ No dependencies (but requires careful testing)

Item 6: Firewall Enhancement
  └─ Depends on: firewall.yml (existing)

Item 7: Logging Enhancement
  └─ Depends on: logging.yml (existing)

Item 8: Vault Enhancement
  └─ Depends on: vault_secrets_rotation_wrapper.yml (existing)

Item 9: Docker Enhancement
  └─ Depends on: docker_security_wrapper.yml (existing)

Item 10: Performance Tuning
  └─ No dependencies

Item 11: Monitoring Tuning
  └─ Depends on: Prometheus/Grafana stack

Item 12: Compliance Automation
  └─ Depends on: compliance_scanning.yml

Item 13: Update main.yml
  └─ Depends on: All above items completed

Item 14: Update defaults/main.yml
  └─ Depends on: All task items completed

Item 15: Testing & Validation
  └─ Depends on: Items 13-14 completed
```

**Optimal implementation order**: 1, 2, 4, 5, 10, 6, 7, 8, 9, 11, 12, 13, 14, 15

---

## Parallel Implementation Groups

**Group A** (Can start immediately):
- Kernel hardening
- Password policy
- Compliance scanning
- Storage hardening
- Performance tuning

**Group B** (Can start after Group A begins):
- Firewall enhancement
- Logging enhancement
- Vault enhancement
- Docker enhancement
- Monitoring tuning

**Group C** (Must wait for Groups A & B):
- Compliance automation
- Update main.yml
- Update defaults/main.yml
- Testing & validation

---

## Risk Mitigation

### High Risk Items
- **Storage hardening**: Mount changes could break system
  - Mitigation: Test in VM first, careful fstab editing, validation before reboot

- **Kernel hardening**: Some parameters might break specific workloads
  - Mitigation: Flag for testing, document per-workload overrides

### Medium Risk Items
- **Firewall enhancement**: Could block legitimate traffic
  - Mitigation: Test carefully, document allowed rules, enable logging

- **Password policy**: Might lock out users
  - Mitigation: Test on subset first, clear runbook for unlock

### Low Risk Items
- **Performance tuning**: Suboptimal performance vs. crashes
  - Mitigation: Monitor after changes, revert if needed

- **Compliance scanning**: Safe, read-only operations
  - Mitigation: No risk, benefits only

---

## Success Metrics

When 100% complete:
- ✓ All critical security gaps closed
- ✓ All compliance frameworks validated
- ✓ All operational gaps addressed
- ✓ Zero configuration drift
- ✓ 0 critical findings on CIS benchmark
- ✓ Full NIST compliance validated
- ✓ 100% uptime for critical services
- ✓ <5 minute RTO for disaster recovery
- ✓ All audit requirements satisfied

---

**Current Status**: Starting implementation of remaining 11 items
**Next Milestone**: Complete PHASE 1 & 2 (storage + enhancements) by EOD
**Final Completion Target**: 100% within 30 hours of work

Ready to continue? Current progress: **27% complete**
