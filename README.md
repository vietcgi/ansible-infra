# Sentinel Infrastructure - Enterprise Ansible Automation

A production-grade, cross-platform infrastructure automation framework using Ansible with integrated Grafana monitoring.

## Overview

**Sentinel Infrastructure** is an enterprise-class Ansible-based infrastructure-as-code (IaC) solution designed for managing Linux and macOS servers at scale. It leverages industry-standard collections and battle-tested practices.

### Key Features

- **Multi-Platform Support**: Ubuntu, Debian, CentOS, RHEL, Rocky, AlmaLinux, macOS
- **Grafana Integration**: Unified observability with Grafana Agent, Prometheus, and Loki
- **Production-Ready**: Security hardening, audit logging, and compliance baseline
- **Modular Architecture**: Reusable roles and playbooks following Ansible best practices
- **Enterprise Standards**: Version control, CI/CD ready, comprehensive documentation
- **Idempotent Design**: Safe to run repeatedly - no configuration drift
- **GitOps Ready**: Infrastructure as Code with git-based workflows

## Quick Start

### Prerequisites

- Ansible 2.15+
- SSH access to target servers
- Python 3.8+ on control node
- Sudo access on target servers (optional but recommended)

### Installation

```bash
# Clone repository
git clone <your-repo-url> sentinel-infra
cd sentinel-infra

# Install dependencies
ansible-galaxy collection install -r requirements.yml

# Verify installation
ansible-inventory -i inventories/production/hosts.yml --list
```

## Architecture

### Directory Structure

```
sentinel-infra/
├── ansible.cfg                 # Ansible configuration
├── requirements.yml            # Collection dependencies
├── roles/
│   └── common/                # Foundation role (OS-agnostic setup)
├── playbooks/
│   ├── provision.yml          # Initial server provisioning
│   ├── configure.yml          # Full configuration stack
│   └── maintenance.yml        # Updates, patches, cleanup
├── inventories/
│   ├── production/            # Production servers
│   ├── staging/               # Staging environment
│   └── development/           # Development servers
├── tests/                     # Testing and validation
├── docs/                      # Documentation
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
