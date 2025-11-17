# Common Role: 100% Completion Roadmap

**Status**: 35-40% Complete (979 LOC) → Target: 100% Complete (8,289-10,219 LOC)
**Timeline**: 11-15 weeks
**Total Work**: 7,310-10,240 LOC across 80+ components

---

## Executive Summary

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| **Implementation** | 35-40% | 100% | 7,310-10,240 LOC |
| **Code Quality** | Excellent | Excellent | Maintain |
| **Security** | Good | Critical | Add 8+ security components |
| **Monitoring** | None | Enterprise | Add observability stack |
| **Compliance** | Basic audit | Full CIS/STIG | Add compliance automation |
| **HA/DR** | None | Active | Add clustering & backup |

---

## PHASE 1: CRITICAL FOUNDATION (Weeks 1-3, 2,100-2,850 LOC)

**Goal**: Production-ready infrastructure with security, monitoring, backup

### 1.1 Firewall Management (100-120 LOC) - WEEK 1
**File**: `roles/common/tasks/firewall.yml`

**Components**:
- UFW for Ubuntu/Debian (stateless)
- firewalld for RHEL/CentOS (stateful)
- Dynamic port management
- Service-based rule templating
- DDoS protection rules (SYN flood limits)

**Variables to add** (defaults/main.yml):
```yaml
firewall_enabled: true
firewall_allow_ssh: true
firewall_ssh_port: 22
firewall_allow_icmp: true
firewall_rate_limit_icmp: 10/sec
firewall_custom_rules: []
firewall_default_policy: deny_incoming
```

**Status**: Pending

---

### 1.2 fail2ban Setup (100-150 LOC) - WEEK 1
**File**: `roles/common/tasks/fail2ban.yml`

**Components**:
- fail2ban installation & config
- Jails for: sshd, postfix, nginx, apache
- Ban thresholds: 5 attempts in 10 minutes
- Ban duration: 3600 seconds
- Email notifications on ban
- Recidivism tracking

**Templates**:
- `jail.local.j2` - Jail configurations
- `filter.d/custom.conf.j2` - Custom filters

**Status**: Pending

---

### 1.3 Metrics Collection - node_exporter (120-180 LOC) - WEEK 1
**File**: `roles/common/tasks/metrics.yml`

**Components**:
- node_exporter 1.8.0+ installation
- Prometheus textfile collector setup
- Custom metric definitions
- Service enablement & startup
- Port 9100 exposure configuration
- TLS certificate support

**Metrics to expose**:
- System: CPU, memory, disk, network
- Process: file descriptors, context switches
- Custom: application-specific metrics

**Status**: Pending

---

### 1.4 Log Shipping - filebeat/rsyslog (100-150 LOC) - WEEK 2
**File**: `roles/common/tasks/log_shipping.yml`

**Components**:
- filebeat 8.x installation (primary)
- rsyslog fallback for older systems
- Elasticsearch endpoint configuration
- Log parsing & enrichment
- TLS certificate management
- Buffer & retry configuration

**Log inputs**:
- System logs (syslog)
- SSH logs (/var/log/auth.log)
- Audit logs (/var/log/audit)
- Application logs (configurable)

**Status**: Pending

---

### 1.5 Secrets Management - Vault (120-180 LOC) - WEEK 2
**File**: `roles/common/tasks/vault.yml`

**Components**:
- HashiCorp Vault agent installation
- Auto-unseal configuration (KMS/HSM)
- Credential injection for system services
- SSH public key generation
- TLS certificate management
- Service account setup

**Features**:
- Dynamic secrets for databases
- SSH OTP generation
- Encryption-as-a-service
- Audit logging integration

**Status**: Pending

---

### 1.6 Sudo Hardening (50-80 LOC) - WEEK 2
**File**: `roles/common/tasks/sudo_hardening.yml`

**Components**:
- Sudoers configuration hardening
- Disable NOPASSWD by default
- Log all sudo commands
- TTY requirement enforcement
- Use_pty requirement
- Logging to syslog + file
- Timeout configuration (15 min auth, 5 min idle)

**Security additions**:
- Require matching user for file access
- Disable shell execution in sudoers rules
- Require explicit command paths
- Use allowed_users and allowed_groups

**Status**: Pending

---

### 1.7 Backup Agent - Bacula/Veeam (120-180 LOC) - WEEK 3
**File**: `roles/common/tasks/backup.yml`

**Components**:
- Backup client installation (Bacula/Veeam/Commvault)
- Backup schedule configuration
- Incremental backup setup
- Retention policy: 7-day, 4-week, yearly
- Backup encryption (AES-256)
- Recovery test automation (monthly)
- Backup verification hooks

**Features**:
- Automated backup scheduling
- Pre/post-backup hooks
- Backup notification emails
- Recovery time objective (RTO) setup
- Backup media management

**Status**: Pending

---

### 1.8 SELinux/AppArmor Hardening (80-100 LOC) - WEEK 3
**File**: `roles/common/tasks/apparmor.yml` + `roles/common/tasks/selinux.yml`

**Components**:

**SELinux (RHEL/CentOS)**:
- Policy installation (targeted)
- Context labeling for critical services
- Transition rules configuration
- Enforcing mode setup (with audit first)
- Custom policy compilation

**AppArmor (Ubuntu/Debian)**:
- Profile installation
- Enforce mode for critical services
- Custom profile development
- Complain mode testing

**Status**: Pending

---

**PHASE 1 Subtotal**: 2,100-2,850 LOC
**Target Completion**: 50-55%

---

## PHASE 2: COMPLIANCE & ADVANCED MONITORING (Weeks 4-7, 2,200-3,100 LOC)

### 2.1 CIS Benchmarks (200-300 LOC) - WEEKS 4-5
**File**: `roles/common/tasks/cis_benchmarks.yml`

**Coverage**:
- CIS Ubuntu Linux 20.04 v1.1.0
- CIS Debian Linux 11 v1.0.0
- CIS RHEL 8 v1.0.0
- CIS CentOS 8 v1.0.0

**Implementation**:
- Scored items (70+ controls)
- Unscored items (10+)
- Exception handling framework
- Benchmark scoring calculation
- Compliance report generation

**Status**: Pending

---

### 2.2 STIG Hardening (200-300 LOC) - WEEKS 5-6
**File**: `roles/common/tasks/stig.yml`

**Coverage**:
- DISA RHEL 8 STIG (255 rules)
- Ubuntu 20.04 hardening
- Access controls, cryptography, logging
- System updates and patches
- Account management & authentication

**Implementation**:
- STIG ID mapping
- Rule prioritization
- Exception framework
- Compliance matrix generation

**Status**: Pending

---

### 2.3 NIST 800-53 Mapping (150-250 LOC) - WEEK 6
**File**: `roles/common/tasks/nist_controls.yml`

**Coverage**:
- AC (Access Control) - 22 controls
- AT (Awareness & Training) - 3 controls
- AU (Audit & Accountability) - 12 controls
- CA (Security Assessment & Authorization) - 6 controls
- CM (Configuration Management) - 9 controls
- CP (Contingency Planning) - 13 controls
- IA (Identification & Authentication) - 9 controls
- IR (Incident Response) - 8 controls
- MA (Maintenance) - 3 controls
- MP (Media Protection) - 3 controls
- PE (Physical & Environmental) - 18 controls
- PL (Planning) - 8 controls
- PS (Personnel Security) - 7 controls
- RA (Risk Assessment) - 3 controls
- SA (System & Services Acquisition) - 16 controls
- SC (System & Communications Protection) - 43 controls
- SI (System & Information Integrity) - 12 controls

**Implementation**:
- Control mapping to tasks
- Evidence collection automation
- Assessment support tools

**Status**: Pending

---

### 2.4 Advanced Audit Rules (100-150 LOC) - WEEK 6
**File**: `roles/common/tasks/audit_rules_advanced.yml`

**Enhanced Rules**:
- File access tracking (system binaries, config files)
- Network monitoring (iptables/nftables changes)
- Privilege escalation attempts
- Cryptographic operations
- SELinux/AppArmor events
- Cryptographic key material
- Unauthorized access attempts

**Status**: Pending

---

### 2.5 Rootkit Detection (80-100 LOC) - WEEK 4
**File**: `roles/common/tasks/rootkit_detection.yml`

**Components**:
- rkhunter 1.4.6+ installation
- chkrootkit 0.55+ installation
- Scheduled scans (daily)
- Email notifications on detection
- Quarantine procedures
- False positive handling

**Status**: Pending

---

### 2.6 Intrusion Detection - AIDE (100-150 LOC) - WEEK 7
**File**: `roles/common/tasks/intrusion_detection.yml`

**Components**:
- AIDE (Advanced Intrusion Detection Environment)
- File integrity monitoring
- Daily baseline checks
- Change detection & alerts
- Baseline update procedures
- Integration with syslog

**Monitored paths**:
- /boot, /lib, /lib64, /usr
- /sbin, /bin, /usr/bin, /usr/sbin
- /etc (critical configs)

**Status**: Pending

---

### 2.7 Credential Rotation (100-160 LOC) - WEEK 7
**File**: `roles/common/tasks/credential_rotation.yml`

**Components**:
- SSH key rotation (quarterly)
- API token rotation (monthly)
- Database password rotation
- Vault secrets rotation
- TLS certificate renewal
- Automated rotation hooks

**Status**: Pending

---

### 2.8 Log Centralization Enhancement (100-150 LOC) - WEEK 7
**File**: `roles/common/tasks/log_centralization.yml`

**Components**:
- Logstash integration
- Log parsing pipelines
- Elasticsearch index rotation
- Kibana dashboard setup
- Log retention policies
- Log archival to S3/Azure

**Status**: Pending

---

**PHASE 2 Subtotal**: 2,200-3,100 LOC
**Target Completion**: 75-80%

---

## PHASE 3: ADVANCED CAPABILITIES (Weeks 8-12, 2,300-3,200 LOC)

### 3.1 High Availability - Pacemaker (150-250 LOC) - WEEKS 8-9
**File**: `roles/common/tasks/ha_clustering.yml`

**Components**:
- Pacemaker installation
- Corosync cluster formation
- STONITH fencing configuration
- Resource management
- Failover automation
- Health check integration
- Split-brain prevention

**Status**: Pending

---

### 3.2 Docker Setup & Hardening (100-150 LOC) - WEEK 9
**File**: `roles/common/tasks/docker.yml`

**Components**:
- Docker Engine installation
- Daemon security hardening
- Storage driver selection
- Network configuration
- TLS support
- Registry authentication
- User namespace remapping

**Security hardening**:
- Seccomp profiles
- AppArmor/SELinux policies
- Resource limits
- Logging configuration

**Status**: Pending

---

### 3.3 Container Image Scanning (100-150 LOC) - WEEK 10
**File**: `roles/common/tasks/container_scanning.yml`

**Components**:
- Trivy scanner installation
- Image vulnerability scanning
- Anchore integration
- Scan scheduling (nightly)
- Vulnerability report generation
- Policy enforcement (block critical)

**Status**: Pending

---

### 3.4 Volume Management - LVM (120-180 LOC) - WEEK 10
**File**: `roles/common/tasks/volume_management.yml`

**Components**:
- LVM setup & configuration
- Physical volume creation
- Volume group management
- Logical volume creation
- Filesystem creation & mounting
- Snapshot management
- Resize automation

**Features**:
- Automated LVM expansion
- Snapshot scheduling
- Thin provisioning support
- Performance monitoring

**Status**: Pending

---

### 3.5 Disk Encryption - LUKS (100-150 LOC) - WEEK 11
**File**: `roles/common/tasks/disk_encryption.yml`

**Components**:
- LUKS encryption setup
- Encrypted LVM volumes
- Key material management
- Crypttab configuration
- Unlock automation on boot
- Encrypted swap
- Encryption key backup

**Security**:
- AES-256 encryption
- Key escrow for recovery
- Secure key storage

**Status**: Pending

---

### 3.6 Backup Verification (80-120 LOC) - WEEK 11
**File**: `roles/common/tasks/backup_verification.yml`

**Components**:
- Automated recovery testing
- Backup integrity verification
- Test restore procedures
- Report generation
- Failure alerting
- Recovery time testing

**Verification types**:
- Full restore tests (quarterly)
- Partial restore tests (monthly)
- Integrity checks (weekly)
- Offsite copy verification (monthly)

**Status**: Pending

---

### 3.7 Disaster Recovery (100-150 LOC) - WEEK 12
**File**: `roles/common/tasks/disaster_recovery.yml`

**Components**:
- DR plan automation
- Failover procedures
- Recovery point objective (RPO)
- Recovery time objective (RTO)
- DR testing schedules
- Runbook generation

**Automation**:
- Automated failover detection
- Failback procedures
- Data consistency checks

**Status**: Pending

---

### 3.8 Performance Tuning Suite (150-250 LOC) - WEEK 12
**File**: `roles/common/tasks/performance_tuning.yml`

**Components**:
- CPU affinity & pinning
- Memory tuning (swap, cache, hugepages)
- Disk I/O optimization
- Network performance tuning
- CPU power states
- Thermal management

**Tuning parameters**:
- TCP buffer optimization
- Queue depth tuning
- I/O scheduler selection
- CPU governors

**Status**: Pending

---

### 3.9 Configuration Drift Detection (80-130 LOC) - WEEK 8
**File**: `roles/common/tasks/drift_detection.yml`

**Components**:
- Configuration baseline creation
- Scheduled drift detection
- Compliance scanning
- Change notification
- Automated remediation (optional)
- Drift reporting

**Detection methods**:
- File checksum validation
- Package version tracking
- Configuration file comparison

**Status**: Pending

---

**PHASE 3 Subtotal**: 2,300-3,200 LOC
**Target Completion**: 95%

---

## PHASE 4: POLISH & ECOSYSTEM (Weeks 13-15, 500-900 LOC)

### 4.1 Network Bonding & VLAN (100-150 LOC)
**File**: `roles/common/tasks/network_bonding.yml`

**Components**:
- Network interface bonding (LACP/active-backup)
- VLAN configuration
- Bonding failover
- VLAN prioritization
- Dynamic VLAN assignment

**Status**: Pending

---

### 4.2 Development Tools (80-150 LOC)
**File**: `roles/common/tasks/dev_tools.yml`

**Components**:
- Git installation & config
- Build tools (gcc, make, cmake)
- Language runtimes (Node.js, Go, Rust)
- Package managers (npm, cargo)
- Development libraries

**Status**: Pending

---

### 4.3 Advanced Container Runtime (120-180 LOC)
**File**: `roles/common/tasks/container_runtime.yml`

**Components**:
- containerd installation
- CRI-O installation (RHEL/CentOS)
- Kubernetes CRI support
- Pod infrastructure images
- Container networking

**Status**: Pending

---

### 4.4 Compliance Reporting (120-200 LOC)
**File**: `roles/common/tasks/compliance_reporting.yml`

**Components**:
- Compliance report generation
- Audit log aggregation
- Evidence collection
- SOC 2 Type II reporting
- Executive summaries
- Dashboard integration

**Status**: Pending

---

### 4.5 Integration Testing (50-100 LOC)
**Molecule/tests**: Complete test coverage

**Tests to implement**:
- Cross-platform validation (8 OS variants)
- Security hardening verification
- Compliance control testing
- High availability failover
- Backup/recovery procedures
- Performance baseline establishment

**Status**: Pending

---

### 4.6 Documentation (30-120 LOC)
**Files**:
- Complete TROUBLESHOOTING.md
- ARCHITECTURE.md
- COMPLIANCE_MATRIX.md
- DISASTER_RECOVERY_PLAN.md
- PERFORMANCE_TUNING_GUIDE.md

**Status**: Pending

---

**PHASE 4 Subtotal**: 500-900 LOC
**Target Completion**: 100%

---

## Implementation Statistics

### By Phase
| Phase | Weeks | LOC Range | Cumulative % | Key Focus |
|-------|-------|-----------|-------------|-----------|
| 1 | 2-3 | 2,100-2,850 | 50-55% | Security foundation |
| 2 | 3-4 | 2,200-3,100 | 75-80% | Compliance & monitoring |
| 3 | 4-5 | 2,300-3,200 | 95% | HA, DR, containers |
| 4 | 2-3 | 500-900 | 100% | Polish & docs |
| **Total** | **11-15** | **7,310-10,240** | **100%** | Enterprise-grade |

### By Complexity
| Complexity | Items | Est. LOC | % |
|-----------|-------|----------|---|
| Simple | 22 | 2,200-2,500 | 30% |
| Medium | 45 | 3,500-4,200 | 50% |
| Complex | 13 | 1,800-2,500 | 20% |

### By Category
| Category | Items | Est. LOC | Priority |
|----------|-------|----------|----------|
| Security | 12 | 2,100-2,850 | P1 |
| Monitoring | 8 | 670-1,020 | P1 |
| Compliance | 7 | 950-1,520 | P1 |
| Backup/DR | 8 | 710-1,070 | P1 |
| Containers | 8 | 720-1,090 | P1 |
| Performance | 6 | 450-720 | P2 |
| HA/Clustering | 6 | 630-970 | P1 |
| Configuration | 6 | 520-830 | P2 |
| Secrets | 5 | 450-710 | P1 |
| Networking | 6 | 520-800 | P2 |
| Storage | 5 | 460-700 | P1 |
| Development | 5 | 310-640 | P3 |

---

## Critical Path & Dependencies

```
├─ PHASE 1 (Foundation)
│ ├─ Firewall (required for all)
│ ├─ Metrics (required for monitoring)
│ ├─ Backup (required for DR)
│ ├─ Secrets (required for compliance)
│ └─ Sudo Hardening (required for security)
│
├─ PHASE 2 (Compliance)
│ ├─ CIS/STIG (depends on Phase 1)
│ ├─ Audit Rules (depends on Firewall)
│ └─ Log Shipping (depends on Metrics)
│
├─ PHASE 3 (Advanced)
│ ├─ HA Clustering (depends on Phase 1)
│ ├─ Docker (depends on Firewall)
│ ├─ LVM (depends on Phase 1)
│ └─ Encryption (depends on Storage)
│
└─ PHASE 4 (Polish)
 ├─ Compliance Reporting (depends on Phase 2)
 ├─ Testing (depends on all phases)
 └─ Documentation (depends on all phases)
```

---

## Success Metrics

### Code Quality
- [ ] All tasks idempotent (2+ runs)
- [ ] Cross-platform tested (8 OS variants)
- [ ] Ansible-lint passing (0 errors)
- [ ] 95%+ code coverage in tests

### Functionality
- [ ] All 80+ components implemented
- [ ] 100% of NIST 800-53 controls mapped
- [ ] CIS/STIG compliance automated
- [ ] HA failover tested & working

### Performance
- [ ] Baseline metrics established
- [ ] <5min deployment time per component
- [ ] <2% CPU overhead from monitoring
- [ ] <500MB disk footprint

### Security
- [ ] All secrets encrypted at rest
- [ ] Encryption in transit enabled
- [ ] Audit trails complete
- [ ] No hardcoded credentials

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Cross-platform failures | Medium | High | Molecule tests on all 8 OS |
| Breaking changes | Medium | Critical | Blue-green testing, rollback plans |
| Performance regression | Low | Medium | Baseline benchmarking |
| Compliance gaps | Low | Critical | Compliance validation in CI/CD |
| HA split-brain | Low | Critical | Quorum + STONITH testing |

---

## Next Steps

1. **Week 1**: Begin PHASE 1 implementation (firewall, fail2ban, metrics)
2. **Week 2**: Continue PHASE 1 (backup, secrets, sudo hardening)
3. **Week 3**: Complete PHASE 1, begin testing
4. **Weeks 4-7**: PHASE 2 (compliance automation)
5. **Weeks 8-12**: PHASE 3 (HA, DR, advanced features)
6. **Weeks 13-15**: PHASE 4 (polish, documentation, final testing)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-16
**Status**: APPROVED FOR IMPLEMENTATION
