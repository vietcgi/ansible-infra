# ansible-infra - Enterprise Infrastructure Automation Framework

A production-grade, reusable infrastructure automation framework for multi-platform deployments (Linux + macOS) with enterprise-grade testing, security, and monitoring.

**Status**: ✅ Production-Ready | 📚 Fully Documented | 🔒 Security-Hardened | 🧪 Enterprise-Tested

## Overview

**ansible-infra** is an enterprise-class infrastructure-as-code framework designed for managing Linux and macOS servers at scale. It uses official Ansible collections for Linux infrastructure and custom roles for macOS-specific requirements, following industry best practices.

### Key Features

- **Multi-Platform Support**: Ubuntu, Debian, Rocky, AlmaLinux (Linux) + macOS
- **Hybrid Deployment Model**: Official collections (Linux) + custom roles (macOS)
- **macOS Security Hardening**: 31 security controls with NIST + CIS compliance
- **Enterprise Testing**: Molecule framework with 4 test scenarios
- **Production-Ready**: Pre-commit hooks, GitHub Actions CI/CD, automated testing
- **Security First**: Secret detection, vulnerability scanning, compliance alignment
- **Modular Architecture**: Reusable roles and playbooks
- **Idempotent Design**: Safe to run repeatedly - no configuration drift

## Documentation Roadmap

**Choose your path based on your role:**

### 🚀 Getting Started (5-15 minutes)
- **[Quick Start](docs/QUICK_START.md)** - Choose your deployment path (Arnio, Linux-only, or hardening)
- **[README](README.md)** (this file) - Project overview

### 🏗️ Understanding the Design (15-30 minutes)
- **[Architecture Guide](docs/ARCHITECTURE.md)** - Hybrid deployment model, role strategy, data flow
- **[Roadmap & Vision](docs/ROADMAP.md)** - Long-term strategy, phases, scaling

### 🔐 Security & Compliance (20-40 minutes)
- **[Security Hardening](docs/SECURITY_HARDENING.md)** - 31+ controls, firewall, SSH, audit logging
- **[Standards & Compliance](docs/STANDARDS.md)** - NIST SP 800-219, CIS Benchmarks, Apple guidelines
- **[macOS Role Details](roles/system_hardening_macos/README.md)** - Complete role reference

### 🧪 Quality & Testing (20-30 minutes)
- **[Quality Assurance](docs/QUALITY_ASSURANCE.md)** - Testing framework, CI/CD, Molecule, pre-commit hooks

### 📦 Implementation (2-4 hours)
- **[Implementation Guide](docs/IMPLEMENTATION.md)** - Step-by-step deployment to production
- **[Monitoring Setup](docs/PROMETHEUS_INTEGRATION.md)** - Prometheus + Grafana integration

### 📚 Reference Documentation
- **[Collections Reference](docs/COLLECTIONS_REFERENCE.md)** - Comprehensive Ansible collection inventory with role specifications and dependencies

## Quick Start

### Prerequisites

- Ansible 2.15+
- SSH access to target servers
- Python 3.8+ on control node
- Sudo access on target servers (optional but recommended)

### Installation

```bash
# Clone repository
git clone <your-repo-url> ansible-infra
cd ansible-infra

# Install dependencies
ansible-galaxy collection install -r requirements.yml

# Verify installation
ansible-inventory -i inventories/production/hosts.yml --list
```

## Architecture

### Directory Structure

```
ansible-infra/
├── ansible.cfg                 # Ansible configuration
├── requirements.yml            # Collection dependencies
├── roles/
│   ├── common/                # OS-agnostic foundation role
│   └── system_hardening_macos/ # macOS security hardening role
├── playbooks/
│   ├── provision.yml          # Initial server provisioning
│   ├── configure.yml          # Full configuration stack
│   └── maintenance.yml        # Updates, patches, cleanup
├── inventories/
│   ├── production/            # Production servers
│   ├── staging/               # Staging environment
│   └── development/           # Development servers
├── docs/                      # Comprehensive documentation
└── .gitignore
```

### Execution Flow

```
Provision Playbook
  ↓
Common Role (Foundation)
  - OS validation
  - System updates
  - Core packages
  - SSH hardening
  - NTP sync
  - Sysctl tuning
  - Audit logging

Configure Playbook
  ↓
Common Role + Grafana Collection
  - Foundation setup
  - Grafana Agent (metrics collection)
  - Prometheus (time-series DB)
  - Loki (log aggregation)
  - Node Exporter (system metrics)

Maintenance Playbook
  ↓
Rolling Updates
  - Package updates
  - Log rotation
  - Cache cleanup
  - Service validation
```

## Usage

### Provision New Servers

```bash
# Provision production servers
ansible-playbook playbooks/provision.yml -i inventories/production/hosts.yml -v

# Provision specific host
ansible-playbook playbooks/provision.yml -i inventories/production/hosts.yml -l web01.sentinel.local

# Dry-run (check mode)
ansible-playbook playbooks/provision.yml -i inventories/production/hosts.yml -C
```

### Full Configuration Setup

```bash
# Configure production environment
ansible-playbook playbooks/configure.yml -i inventories/production/hosts.yml

# Apply only Grafana components
ansible-playbook playbooks/configure.yml -i inventories/production/hosts.yml --tags grafana

# Skip monitoring (if not needed)
ansible-playbook playbooks/configure.yml -i inventories/production/hosts.yml --skip-tags monitoring
```

### Maintenance & Updates

```bash
# Rolling updates (one server at a time)
ansible-playbook playbooks/maintenance.yml -i inventories/production/hosts.yml --tags updates

# Log cleanup and rotation
ansible-playbook playbooks/maintenance.yml -i inventories/production/hosts.yml --tags logs

# Full maintenance cycle
ansible-playbook playbooks/maintenance.yml -i inventories/production/hosts.yml
```

## Configuration

### Inventory Management

Edit `inventories/production/hosts.yml` to define your servers:

```yaml
all:
  vars:
    ansible_user: ubuntu
    common_hostname_environment: production
    monitoring_grafana_enabled: true

  children:
    webservers:
      hosts:
        web01.sentinel.local:
          ansible_host: 10.0.1.10
```

### Environment Variables

Define environment-specific variables in:
- `inventories/production/group_vars/all.yml`
- `inventories/staging/group_vars/all.yml`
- `inventories/development/group_vars/all.yml`

### Secrets Management

Use Ansible Vault for sensitive data:

```bash
# Create vault password file
echo "your-secure-password" > ~/.vault_password

# Encrypt sensitive variables
ansible-vault encrypt inventories/production/group_vars/all/vault.yml

# Run playbooks with vault
ansible-playbook configure.yml --vault-password-file ~/.vault_password
```

## Monitoring & Observability

### Grafana Agent

The Grafana Agent is automatically installed on all servers and configured to:
- Collect system metrics (CPU, memory, disk, network)
- Ship logs to Loki
- Send traces to Tempo (optional)
- Send metrics to Prometheus

### Accessing Grafana

```
URL: http://<grafana-server>:3000
Default Credentials: admin / admin (change immediately!)
```

### Default Dashboards

- Node Exporter overview
- System metrics
- Log streams
- Alert status

## Security

### Hardening Applied

✓ SSH key-based authentication only
✓ Firewall configuration
✓ Audit logging enabled
✓ Sysctl kernel hardening
✓ Regular security updates
✓ File descriptor limits

### Compliance

- CIS Benchmarks baseline
- NIST controls
- PCI DSS ready
- SOC 2 compliant practices

## Troubleshooting

### SSH Connection Issues

```bash
# Test SSH connectivity
ansible all -i inventories/production/hosts.yml -m ping

# Check SSH keys
ssh-keyscan -H <host> >> ~/.ssh/known_hosts
```

### Playbook Failures

```bash
# Run in verbose mode
ansible-playbook configure.yml -vvv

# Check specific host
ansible-playbook configure.yml -l hostname -vv

# Validate syntax
ansible-playbook configure.yml --syntax-check
```

### Service Status

```bash
# Check Grafana Agent
systemctl status grafana-agent

# Check Node Exporter
systemctl status node_exporter

# View service logs
journalctl -u grafana-agent -f
journalctl -u node_exporter -f
```

## Best Practices

### 1. Version Control

Always commit changes:
```bash
git add .
git commit -m "feat: update monitoring configuration"
git push origin main
```

### 2. Testing

Test playbooks before production:
```bash
# Dry-run on staging
ansible-playbook configure.yml -i inventories/staging/hosts.yml -C

# Then on staging with changes
ansible-playbook configure.yml -i inventories/staging/hosts.yml

# Monitor and validate
# Then promote to production
```

### 3. Rollback Procedures

Keep backups of critical configurations:
```bash
# Backup before changes
ansible-playbook backup.yml -i inventories/production/hosts.yml

# Restore if needed
ansible-playbook restore.yml -i inventories/production/hosts.yml -e "backup_date=2025-11-15"
```

### 4. Documentation

Document changes in git commit messages:
- **feat**: New feature added
- **fix**: Bug fix applied
- **docs**: Documentation updated
- **chore**: Maintenance task

## Development

### Running Tests

```bash
# Syntax validation
ansible-playbook playbooks/provision.yml --syntax-check

# Lint checking
ansible-lint playbooks/

# Dry-run (check mode)
ansible-playbook playbooks/provision.yml -C
```

### Contributing

1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes and test
3. Commit with descriptive message
4. Push to remote: `git push origin feature/new-feature`
5. Create pull request

## Support & Resources

### Documentation

- [Ansible Documentation](https://docs.ansible.com)
- [Grafana Documentation](https://grafana.com/docs)
- [Grafana Ansible Collection](https://galaxy.ansible.com/grafana/grafana)

### Troubleshooting

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues.

### Architecture Details

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for design decisions.

## License

GPL-3.0-or-later

## Contributing

Contributions welcome! Please ensure:
- All playbooks pass ansible-lint
- Documentation is updated
- Changes are tested in staging first

---

**Last Updated**: November 15, 2025
**Maintainer**: Infrastructure Team
