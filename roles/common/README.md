# Common Role - Foundation Infrastructure Configuration

**Enterprise-grade OS-agnostic foundation for Linux and macOS servers**

---

## Overview

The `common` role establishes a consistent, hardened foundation across heterogeneous infrastructure (Ubuntu, Debian, Rocky, AlmaLinux, and macOS). It provides essential system configuration, security controls, and operational best practices—regardless of operating system family.

**Design Philosophy**: Single idempotent role. Apply once or repeatedly; convergent to desired state with zero drift.

---

## Role Purpose

### What This Role Does

Executes 11 sequential configuration tasks to deliver a production-ready server:

1. **OS Validation** - Verify supported distribution and system architecture
2. **System Updates** - Apply security patches and package upgrades
3. **Core Packages** - Install essential utilities (curl, git, vim, jq, tmux, etc.)
4. **Python Runtime** - Configure Python 3 with pip and development headers
5. **NTP Synchronization** - Configure time service for distributed systems
6. **SSH Hardening** - Apply cryptographic and policy-based security controls
7. **Kernel Tuning** (sysctl) - Optimize networking and security parameters
8. **Audit Logging** - Enable system event auditing for compliance/forensics
9. **File Limits** - Configure ulimits for process resource management
10. **DNS Configuration** - Set resolvers for name resolution reliability
11. **Logging Infrastructure** - Configure centralized logging and retention policies

### What This Role Does NOT Do

- **Platform-specific hardening**: Use `system_hardening_macos` for macOS security controls
- **Application configuration**: Application-specific roles extend this foundation
- **Container orchestration**: Kubernetes setup requires additional roles
- **Monitoring agent setup**: Covered by separate monitoring roles (Grafana collection, Prometheus)

---

## Prerequisites

### System Requirements

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **OS** | Ubuntu 20.04+, Debian 11+, CentOS/RHEL 8+, Rocky 8+, macOS 12+ | Version constraints enforced |
| **Ansible** | 2.15+ | Uses modern syntax and modules |
| **SSH Access** | Key-based authentication | Playbook requires remote execution |
| **Privileges** | sudo/become required | All tasks require elevated permissions |
| **Python 3** | 3.8+ on control node | Ansible dependency |

### Network Requirements

- SSH access to target servers (default port 22, configurable)
- Outbound HTTPS (443) for package downloads
- NTP access to time servers (UDP 123)
- DNS resolution access (UDP 53)

### Dependency Roles

None. The `common` role has **zero role dependencies**—it operates independently.

---

## Role Tasks

### Task 1: Validate OS (validate_os.yml)

**Purpose**: Verify server meets minimum OS requirements before configuration

**What It Does**:
- Asserts `ansible_os_family` is in supported distributions list
- Displays system information (distro, kernel, architecture, Python version)
- Fails gracefully with clear error message if OS unsupported

**Output Example**:
```
✓ OS family supported: Debian
System Information:
 Distribution: Ubuntu 22.04 LTS
 OS Family: Debian
 Kernel: 5.15.0-xx-generic
 Architecture: x86_64
 Python: 3.10.12
```

### Task 2: System Update (system_update.yml)

**Purpose**: Apply security patches and dependency updates

**What It Does**:
- Detects package manager (apt, yum, brew)
- Updates package cache/metadata
- Upgrades all packages to latest versions
- Handles platform differences (Debian uses `apt`, RedHat uses `yum`, macOS uses `brew`)

**Variables**:
```yaml
common_update_packages: true # Update package list
common_upgrade_packages: true # Upgrade all packages
```

### Task 3: Install Core Packages (core_packages.yml)

**Purpose**: Provide essential CLI utilities for operations and debugging

**Default Packages** (12 total):
- `curl`, `wget` - HTTP/file download tools
- `git` - Version control
- `vim` - Text editor
- `htop` - Process monitoring (interactive)
- `tree` - Directory structure visualization
- `jq` - JSON processing
- `tmux` - Terminal multiplexing
- `unzip` - Archive extraction
- `net-tools` - Network diagnostics

**Customization**:
```yaml
common_core_packages:
 - curl
 - wget
 - git
 # Add custom packages here
 - your-package-name
```

### Task 4: Configure Python (python.yml)

**Purpose**: Ensure Python 3 runtime is available with development dependencies

**What It Does**:
- Installs Python 3 (already present on most modern systems)
- Installs pip (Python package manager)
- Installs development headers (`python3-dev`)
- Creates virtual environments capability (`python3-venv`)

**Installed Packages**:
```yaml
common_python_packages:
 - python3-pip # Package manager
 - python3-dev # Compile extensions
 - python3-venv # Virtual environment support
```

### Task 5: Configure NTP (ntp.yml)

**Purpose**: Synchronize system time across distributed infrastructure

**What It Does**:
- Detects OS and installs appropriate NTP service (`ntp` on Debian/RedHat, uses `timed` on macOS)
- Renders configuration from `ntp.conf.j2` template
- Enables and starts NTP service
- Optionally synchronizes time on first boot

**Variables**:
```yaml
common_timezone: "UTC"
common_ntp_enabled: true
common_ntp_servers:
 - 0.pool.ntp.org
 - 1.pool.ntp.org
 - 2.pool.ntp.org
 - 3.pool.ntp.org
common_ntp_synchronize_on_boot: true
```

**Why This Matters**: Distributed systems require synchronized time for:
- Log correlation across servers
- Authentication certificate validation
- Distributed tracing and metrics correlation

### Task 6: SSH Hardening (ssh_hardening.yml)

**Purpose**: Apply cryptographic and policy-based security controls to SSH daemon

**What It Does**:
- Renders `/etc/ssh/sshd_config` from `sshd_config.j2` template
- Validates configuration syntax before applying (prevents lockout)
- Sets correct permissions (0600)
- Restarts SSH service to apply changes
- Handles platform differences (Linux systemd vs macOS launchctl)

**Key Configuration Options** (via template):
```yaml
common_ssh_port: 22 # SSH listen port
common_ssh_permit_root_login: "no" # Disable root SSH
common_ssh_password_authentication: "no" # Key-based only
common_ssh_key_bits: 4096 # SSH key strength
```

**Security Controls Applied** (template-based):
- Disable root login
- Disable password authentication (keys only)
- Disable port forwarding (adjustable)
- Set secure key exchange algorithms
- Enable protocol 2 only
- Restrict ciphers to modern algorithms

### Task 7: Kernel Tuning (sysctl.yml)

**Purpose**: Optimize OS kernel parameters for security and performance

**What It Does**:
- Renders `/etc/sysctl.d/99-sentinel.conf`
- Applies sysctl parameters without reboot
- Validates kernel parameter compatibility

**Network Performance Tuning**:
```yaml
net.core.somaxconn: 1024 # TCP accept queue size
net.ipv4.tcp_max_syn_backlog: 2048 # SYN cookie threshold
net.ipv4.tcp_tw_reuse: 1 # Reuse TIME_WAIT sockets
net.ipv4.tcp_fin_timeout: 30 # FIN_WAIT timeout (seconds)
```

**Security Hardening**:
```yaml
net.ipv4.conf.all.send_redirects: 0 # Disable ICMP redirects
net.ipv4.conf.default.send_redirects: 0
net.ipv4.conf.all.accept_source_route: 0 # Reject source routing
net.ipv4.conf.default.accept_source_route: 0
net.ipv4.icmp_echo_ignore_broadcasts: 1 # Ignore broadcast pings
net.ipv4.icmp_ignore_bogus_error_responses: 1
```

### Task 8: Audit Logging (audit.yml)

**Purpose**: Enable system event auditing for security compliance and forensics

**What It Does**:
- Installs audit daemon (auditd)
- Renders audit rules from `audit.rules.j2` template
- Enables and starts auditd service
- Configures audit event retention

**Variables**:
```yaml
common_enable_audit: true
common_log_retention_days: 30
```

**Audit Rules** (template-based):
- Track authentication events (login, sudo)
- Monitor configuration changes
- Log executable modifications
- Track privilege escalation attempts

### Task 9: File Limits (limits.yml)

**Purpose**: Configure process resource limits (ulimits) for stability

**What It Does**:
- Renders `/etc/security/limits.d/99-sentinel.conf`
- Sets soft and hard limits for open file descriptors
- Prevents resource exhaustion attacks
- Enables high-throughput applications

**Variables**:
```yaml
common_file_limits:
 soft: 65536 # Per-process open files (soft limit)
 hard: 65536 # Per-process open files (hard limit)
```

**Why**: Default limits (1024) insufficient for:
- High-throughput web servers
- Distributed database nodes
- Message brokers and event systems

### Task 10: DNS Configuration (dns.yml)

**Purpose**: Configure reliable DNS resolution

**What It Does**:
- Detects OS family
- Renders `/etc/resolv.conf` (Debian) or Netplan config (Ubuntu 18.04+)
- Sets primary and fallback resolvers
- Prevents DNS resolution failures

**Variables**:
```yaml
common_dns_servers:
 - 8.8.8.8 # Google DNS primary
 - 8.8.4.4 # Google DNS secondary
 - 1.1.1.1 # Cloudflare DNS
```

**Why Multiple Servers**: Fault tolerance—if primary is unavailable, system falls back to secondary resolvers.

### Task 11: Logging (logging.yml)

**Purpose**: Configure centralized logging infrastructure

**What It Does**:
- Configures log rotation and retention
- Ensures logging service is running
- Sets up log aggregation endpoints (if configured)
- Prevents log files from consuming disk space

**Variables**:
```yaml
common_log_retention_days: 30
```

---

## Role Variables

### OS-Agnostic Variables (Safely Override These)

All variables include sensible production defaults and can be customized via group_vars or host_vars.

#### System Updates
```yaml
common_update_packages: true # Run apt/yum update
common_upgrade_packages: true # Upgrade all packages
```

#### Packages
```yaml
common_core_packages: # Customize core utilities
 - curl
 - wget
 - git
 - vim
 - htop
 - tree
 - jq
 - tmux
 - unzip
 - net-tools

common_python_packages: # Customize Python stack
 - python3-pip
 - python3-dev
 - python3-venv
```

#### Time Management
```yaml
common_timezone: "UTC" # System timezone
common_ntp_enabled: true # Enable NTP service
common_ntp_servers: # NTP servers to sync against
 - 0.pool.ntp.org
 - 1.pool.ntp.org
 - 2.pool.ntp.org
 - 3.pool.ntp.org
common_ntp_synchronize_on_boot: true # Sync time at startup
```

#### SSH Hardening
```yaml
common_ssh_port: 22 # SSH listen port
common_ssh_permit_root_login: "no" # Disable root login
common_ssh_password_authentication: "no" # Require keys
common_ssh_key_bits: 4096 # Key strength
```

**Security Features Enabled:**
- Post-quantum key exchange: `sntrup761x25519-sha512@openssh.com`
- Modern elliptic curves: `curve25519-sha256`
- Strong ciphers: `chacha20-poly1305@openssh.com`, `aes256-gcm@openssh.com`
- Encrypted MACs: `hmac-sha2-512-etm@openssh.com`
- Key-based authentication only
- Root login disabled
- Proper configuration validation before apply

#### Kernel Tuning
```yaml
common_sysctl_config: # Network & security parameters
 # Network performance
 net.core.somaxconn: 1024
 net.ipv4.tcp_max_syn_backlog: 2048
 net.ipv4.tcp_tw_reuse: 1
 net.ipv4.tcp_fin_timeout: 30

 # Security
 net.ipv4.conf.all.send_redirects: 0
 net.ipv4.conf.default.send_redirects: 0
 net.ipv4.conf.all.accept_source_route: 0
 net.ipv4.conf.default.accept_source_route: 0

 # ICMP
 net.ipv4.icmp_echo_ignore_broadcasts: 1
 net.ipv4.icmp_ignore_bogus_error_responses: 1
```

#### File Limits
```yaml
common_file_limits:
 soft: 65536 # Soft limit per process
 hard: 65536 # Hard limit per process
```

#### Logging
```yaml
common_enable_audit: true # Enable auditd
common_log_retention_days: 30 # Delete logs after N days
```

#### DNS
```yaml
common_dns_servers:
 - 8.8.8.8 # Google Primary
 - 8.8.4.4 # Google Secondary
 - 1.1.1.1 # Cloudflare
```

#### Environment
```yaml
common_hostname_environment: production # Environment tag
common_disable_swap: false # Keep swap enabled by default
```

### Internal Variables (Do NOT Override)

These variables are auto-detected and should never be manually set:

```yaml
# Package manager auto-detection
common_package_manager_map:
 Debian: { manager: apt, update_cache: true, update_cmd: "apt-get update" }
 RedHat: { manager: yum, update_cache: false, update_cmd: "yum check-update" }
 Darwin: { manager: brew, update_cache: false, update_cmd: "brew update" }

# Service name mapping by OS family
common_services_map:
 ntp:
 Debian: ntp
 RedHat: ntpd
 Darwin: null # macOS uses timed
 ssh:
 Debian: ssh
 RedHat: sshd
 Darwin: com.openssh.sshd

# Path mapping
common_paths:
 ssh_config: /etc/ssh/sshd_config
 sysctl_config: /etc/sysctl.d/99-sentinel.conf
 audit_config: /etc/audit/rules.d/sentinel.rules

# Supported distributions (validation only)
common_supported_distributions:
 - ubuntu
 - debian
 - centos
 - rhel
 - rocky
 - almalinux
 - macos

# Minimum version constraints
common_min_versions:
 ubuntu: "20.04"
 debian: "11"
 centos: "8"
 rhel: "8"
 macos: "12"
```

---

## Usage Examples

### Basic Deployment (All Defaults)

```yaml
---
- name: Deploy common foundation role
 hosts: all
 roles:
 - common
```

**Result**: Every server gets standard foundation with production defaults.

### Linux-Only Deployment (Custom Variables)

```yaml
---
- name: Linux infrastructure foundation
 hosts: linux_servers
 vars:
 common_timezone: "America/New_York"
 common_ntp_servers:
 - time.nist.gov
 - time-a.nist.gov
 roles:
 - common
```

### Hybrid Deployment (Linux + macOS)

```yaml
---
- name: Foundation on all platforms
 hosts: all
 vars:
 common_timezone: "UTC"
 common_ssh_port: 2222 # Non-standard port for security
 common_ssh_password_authentication: "no"
 roles:
 - common

# Then apply platform-specific hardening
- name: macOS security hardening
 hosts: macos_servers
 roles:
 - system_hardening_macos
```

### Group Variables Configuration

**inventories/production/group_vars/all.yml**:
```yaml
---
# Global defaults for all servers
common_update_packages: true
common_upgrade_packages: true
common_timezone: "UTC"
common_ntp_enabled: true
```

**inventories/production/group_vars/linux_servers.yml**:
```yaml
---
# Linux-specific customization
common_ssh_port: 2222
common_file_limits:
 soft: 131072 # Higher for database servers
 hard: 131072
```

**inventories/production/group_vars/macos_servers.yml**:
```yaml
---
# macOS-specific customization
common_hostname_environment: workstation
common_ntp_synchronize_on_boot: true
```

### Idempotence Demonstration

Run the role multiple times—should always reach the same state:

```bash
# First run - applies configuration
ansible-playbook playbooks/provision.yml -i inventories/production/hosts.yml

# Output: changed=12, unchanged=0

# Second run - no changes needed (idempotent)
ansible-playbook playbooks/provision.yml -i inventories/production/hosts.yml

# Output: changed=0, unchanged=12 ← All tasks already at desired state
```

---

## Integration with Framework

### In ansible-infra Playbooks

**provision.yml** - Initial server setup:
```yaml
- common # Foundation (this role)
- (optional additional roles)
```

**configure.yml** - Full configuration:
```yaml
- common # Foundation first
- system_hardening_macos # Then platform-specific (macOS only)
- monitoring_roles # Then monitoring setup
```

**maintenance.yml** - Ongoing updates:
```yaml
- common # Keep foundation updated
```

### Dependency Chain

```
provision.yml
└── common (foundation)
 ├── OS validation
 ├── System updates (security patches)
 ├── Core packages
 ├── Python runtime
 ├── SSH hardening
 ├── Kernel tuning
 ├── Audit logging
 └── [Ready for platform-specific roles]

configure.yml
└── common (maintenance)
 └── system_hardening_macos (conditional - macOS only)
```

---

## Supported Platforms

| OS | Minimum Version | Package Manager | Status | Notes |
|----|-----------------|-----------------|--------|-------|
| **Ubuntu** | 20.04 LTS | apt | Tested | Primary platform |
| **Debian** | 11 | apt | Tested | Stable releases only |
| **Rocky** | 8 | yum | Tested | CentOS alternative |
| **AlmaLinux** | 8 | yum | Tested | CentOS alternative |
| **CentOS** | 8 | yum | Tested | End-of-life soon |
| **RHEL** | 8 | yum | Tested | Enterprise Linux |
| **macOS** | 12 | brew | Tested | Monterey+ |

---

## Handlers

The role defines handlers for service restart events:

```yaml
# restart sshd (Linux)
# Triggered when: SSH configuration changes

# restart sshd macos
# Triggered when: SSH configuration changes on macOS

# restart ntp
# Triggered when: NTP configuration changes (Debian)

# restart ntpd
# Triggered when: NTP configuration changes (RedHat)

# restart auditd
# Triggered when: Audit rules change
```

Handlers execute **only if their triggering tasks made changes**, respecting idempotence.

---

## Templates

The role uses Jinja2 templates for platform-agnostic configuration:

| Template | Target | Purpose |
|----------|--------|---------|
| `sshd_config.j2` | `/etc/ssh/sshd_config` | SSH daemon security configuration |
| `ntp.conf.j2` | `/etc/ntp.conf` | NTP client/server configuration |
| `audit.rules.j2` | `/etc/audit/rules.d/sentinel.rules` | Audit daemon rules |
| `limits.conf.j2` | `/etc/security/limits.d/99-sentinel.conf` | File descriptor limits |
| `resolv.conf.j2` | `/etc/resolv.conf` | DNS resolver configuration (Debian) |
| `dns_netplan.yaml.j2` | `/etc/netplan/99-sentinel.yaml` | DNS configuration (Ubuntu 18.04+) |

---

## Troubleshooting

### SSH Locked After Deployment

**Symptom**: Cannot SSH into server after running role

**Cause**: SSH configuration error or firewall blocking

**Recovery**:
```bash
# Check SSH syntax before applying
ssh -t user@host sudo sshd -t

# Revert SSH configuration
ssh -t user@host sudo cp /etc/ssh/sshd_config.bak /etc/ssh/sshd_config

# Restart SSH
ssh -t user@host sudo systemctl restart sshd

# OR: Use console/IPMI to recover manually
```

### NTP Not Synchronizing

**Symptom**: Time drifts on servers despite NTP enabled

**Check**:
```bash
# Verify NTP service status
ansible all -m shell -a "systemctl status ntp"

# Check time skew
ansible all -m shell -a "timedatectl"

# View NTP peers
ansible all -m shell -a "ntpq -p"
```

**Fix**:
```bash
# Force time resync
ansible all -m shell -a "sudo ntpd -gq && sudo systemctl restart ntp"
```

### High Open File Limits Not Applied

**Symptom**: Processes still hit file descriptor limit despite setting `common_file_limits`

**Check**:
```bash
# Verify limits applied
ansible all -m shell -a "cat /etc/security/limits.d/99-sentinel.conf"

# Check process-specific limits
ansible all -m shell -a "cat /proc/$(pgrep nginx)/limits"
```

**Fix**: May require process restart or user session logout/login for new limits to apply.

### Audit Daemon Consuming Disk Space

**Symptom**: `/var/log/audit/` growing rapidly

**Check**:
```bash
ansible all -m shell -a "du -sh /var/log/audit/"
```

**Fix**: Reduce audit rules scope or increase `common_log_retention_days`:
```yaml
common_log_retention_days: 14 # Reduce retention
```

---

## Security Considerations

### SSH Hardening

- **Root login disabled** - Prevents direct root SSH access
- **Password authentication disabled** - Requires SSH keys only
- **Modern key exchange** - Post-quantum resistant algorithms
- **Restrictive ciphers** - Only modern, tested algorithms

### Kernel Hardening

- **Network redirects disabled** - Prevents ICMP redirect attacks
- **Source routing disabled** - Prevents IP spoofing
- **Bogus error responses ignored** - Reduces noise from attackers
- **TCP fairness** - Prevents SYN flood exhaustion

### Audit Logging

- **Authentication events logged** - Compliance requirement (NIST, CIS)
- **Privilege escalation tracked** - Who ran what with sudo
- **Configuration change detection** - Audit trail for compliance

### DNS Security

- **Multiple resolvers** - Fault tolerance against poisoning
- **Cloudflare + Google** - Reputable providers with filtering

---

## Performance Impact

- **First run**: 2-5 minutes (package updates + installations)
- **Subsequent runs**: 30 seconds (idempotent, minimal changes)
- **Network impact**: ~50-200 MB download (OS updates)
- **Disk usage**: ~500 MB - 2 GB (depends on OS version)

---

## Compliance Mappings

### NIST Controls

- **SI-2**: Information System Security Updates (system updates)
- **CM-5**: Access Restrictions for Change (audit logging)
- **AU-2**: Audit Events (audit rules)
- **SC-7**: Boundary Protection (firewall, SSH hardening)

### CIS Benchmarks

- **1.1.1**: Disable uncommon filesystems
- **5.2.x**: SSH Configuration
- **6.2.x**: User and Group Settings
- **4.1.1**: Audit Rules

---

## Maintenance

### Monthly Review

```bash
# Check for failed tasks
ansible all -m command -a "grep -i fail /var/log/ansible.log" -i production/hosts.yml

# Verify all services running
ansible all -m service -a "name={{ item }} state=started" -e "item=sshd" -i production/hosts.yml
```

### Quarterly Updates

```bash
# Update role variables if needed
git pull origin main

# Re-run provision.yml to apply any configuration changes
ansible-playbook playbooks/provision.yml -i inventories/production/hosts.yml
```

---

## Related Documentation

- **[ARCHITECTURE.md](../docs/ARCHITECTURE.md)** - Framework design and role composition
- **[IMPLEMENTATION.md](../docs/IMPLEMENTATION.md)** - Step-by-step production deployment
- **[SECURITY_HARDENING.md](../docs/SECURITY_HARDENING.md)** - Detailed security controls
- **[system_hardening_macos README](../system_hardening_macos/README.md)** - macOS-specific hardening

---

## Contributing

To extend the common role:

1. **Add new task file** in `tasks/` directory
2. **Import in tasks/main.yml** in appropriate order
3. **Add variables** in `defaults/main.yml` with sensible defaults
4. **Document** new variables and task purpose in this README
5. **Test across platforms** (Ubuntu, Debian, Rocky, macOS)
6. **Ensure idempotence** - running twice produces no changes

---

**Status**: Production-Ready | **Last Updated**: November 15, 2025
