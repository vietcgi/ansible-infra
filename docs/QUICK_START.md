# Quick Start Guide

**ansible-infra** - Enterprise Infrastructure Automation Framework

---

## Deployment Scenarios

### Hybrid Deployment (macOS + Linux Backend)

**Recommended for**: Multi-platform infrastructures requiring coordinated resource management

1. **Review architecture** (10 min)
   ```
   Read: docs/ARCHITECTURE.md
   Focus: Hybrid deployment patterns, role composition, data flow
   ```

2. **Review security controls** (15 min)
   ```
   Read: docs/SECURITY_HARDENING.md
   Focus: macOS hardening with 31+ controls, NIST/CIS compliance
   ```

3. **Install framework** (5 min)
   ```bash
   make install-dev
   make setup-hooks
   ```

4. **Validate deployment** (10 min)
   ```bash
   make test-fast              # Lint + syntax check
   make test                   # Full test suite
   ```

5. **Deploy to staging**
   ```bash
   vim inventories/staging/hosts.yml
   make provision-staging
   make configure-staging
   ```

---

### Linux-Only Deployment

**Recommended for**: Pure Linux infrastructure using official Ansible collections

1. **Initialize environment** (5 min)
   ```bash
   make install
   make install-dev
   ```

2. **Configure inventory** (10 min)
   ```bash
   vim inventories/production/hosts.yml
   ```

3. **Deploy infrastructure**
   ```bash
   # Dry-run first (recommended)
   ansible-playbook playbooks/provision.yml -i inventories/production/hosts.yml --check

   # Deploy provisioning
   make provision-prod

   # Apply full configuration
   make configure-prod
   ```

4. **Verify deployment** (5 min)
   ```bash
   make test-connectivity
   ```

---

### macOS Security Hardening

**Recommended for**: Systems requiring NIST SP 800-219 and CIS-compliant configuration

1. **Review hardening controls** (15 min)
   ```
   Read: roles/system_hardening_macos/README.md
   Review: 31+ security controls, compliance mappings
   ```

2. **Local validation** (10 min)
   ```bash
   cd roles/system_hardening_macos
   molecule test
   ```

3. **Production deployment** (5 min)
   ```bash
   ansible-playbook playbooks/configure.yml -i inventories/production/hosts.yml
   ```

---

## Essential Commands

### Installation & Setup
```bash
make install                  # Install Ansible collections
make install-dev              # Install dev tools (test, lint, etc.)
make setup-hooks              # Install git pre-commit hooks
```

### Validation & Testing
```bash
make test-fast               # Quick validation (2 min)
make test                    # Complete test suite (15 min)
make molecule-test           # Molecule tests only
make lint                    # Code quality analysis
make security                # Security scanning
```

### Deployment
```bash
# Staging
make provision-staging       # Initial deployment
make configure-staging       # Full configuration
make maintain-staging        # Updates/maintenance

# Production
make provision-prod          # Initial deployment
make configure-prod          # Full configuration
make maintain-prod           # Updates/maintenance
```

### Utilities
```bash
make help                    # Command reference
make version                 # Tool versions
make clean                   # Cleanup temporary files
```

---

## Documentation Hierarchy

| Document | Purpose | Duration |
|----------|---------|----------|
| **README.md** | Project overview, feature summary | 10 min |
| **docs/ARCHITECTURE.md** | System design, component relationships, data flow | 30 min |
| **docs/QUICK_START.md** | This file - fast deployment paths | 15 min |
| **docs/SECURITY_HARDENING.md** | macOS security controls, firewall, SSH hardening | 40 min |
| **docs/STANDARDS.md** | Compliance mapping (NIST, CIS, Apple) | 30 min |
| **docs/QUALITY_ASSURANCE.md** | Testing framework, CI/CD, Molecule, pre-commit | 30 min |
| **docs/IMPLEMENTATION.md** | 9-phase production deployment guide | 2-4 hours |
| **docs/PROMETHEUS_INTEGRATION.md** | Monitoring setup, metrics collection | 20 min |
| **docs/COLLECTIONS_REFERENCE.md** | Ansible collection inventory | 15 min |

---

## Repository Structure

```
ansible-infra/
├── Makefile                              # 25+ automation commands
├── ansible.cfg                           # Ansible configuration
├── requirements.yml                      # Collection dependencies
│
├── roles/
│   ├── common/                           # Foundation role
│   └── system_hardening_macos/          # macOS hardening
│
├── playbooks/
│   ├── provision.yml                     # Initial deployment
│   ├── configure.yml                     # Full configuration
│   └── maintenance.yml                   # Updates/maintenance
│
├── inventories/
│   ├── production/hosts.yml
│   ├── staging/hosts.yml
│   └── development/hosts.yml
│
└── docs/
    ├── QUICK_START.md                    # This guide
    ├── ARCHITECTURE.md                   # System design
    ├── ROADMAP.md                        # Vision & strategy
    ├── SECURITY_HARDENING.md             # Security controls
    ├── STANDARDS.md                      # Compliance
    ├── QUALITY_ASSURANCE.md              # Testing
    ├── IMPLEMENTATION.md                 # Deployment
    ├── PROMETHEUS_INTEGRATION.md         # Monitoring
    └── COLLECTIONS_REFERENCE.md          # References
```

---

## Troubleshooting

### "make: command not found"
Ensure you are in the ansible-infra directory:
```bash
cd /path/to/ansible-infra
```

### "ansible-playbook: command not found"
Install Ansible:
```bash
make install
# Or: pip install 'ansible>=2.15'
```

### Failed tests during local validation
Enable debug mode for detailed output:
```bash
make molecule-debug
# Keeps instance running for manual inspection
```

### Playbook execution issues
Run with verbose output for diagnosis:
```bash
ansible-playbook playbooks/configure.yml \
  -i inventories/staging/hosts.yml \
  -vvv
```

---

## Recommended Next Steps

1. Review repository structure and documentation
2. Install dependencies: `make install-dev`
3. Validate setup: `make test-fast`
4. Read `docs/ARCHITECTURE.md` for design overview
5. Configure `inventories/` for your environment
6. Run staged deployment: `make provision-staging`
7. Monitor metrics via `docs/PROMETHEUS_INTEGRATION.md`

---

**Status**: Production-ready infrastructure automation framework
**Last Updated**: November 15, 2025
