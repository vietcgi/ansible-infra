# Ansible Infrastructure - Project Reusability Guide

**For**: Future projects, teams, and deployments
**Version**: 1.0
**Last Updated**: 2025-11-16

---

## Table of Contents

1. [Overview](#overview)
2. [What Makes This Reusable](#what-makes-this-reusable)
3. [For New Projects](#for-new-projects)
4. [For New Team Members](#for-new-team-members)
5. [Customization Patterns](#customization-patterns)
6. [FAQ & Troubleshooting](#faq--troubleshooting)

---

## Overview

This repository is designed as a **reusable infrastructure-as-code framework** that can be adapted for multiple projects, teams, and deployment scenarios. Instead of starting from scratch, future projects can:

- ✅ Clone and customize this framework
- ✅ Reuse proven roles and playbooks
- ✅ Leverage tested patterns and best practices
- ✅ Maintain consistency across projects
- ✅ Reduce deployment time from weeks to hours

### Core Philosophy

**Don't copy-paste code. Clone frameworks and customize them.**

This repository provides:
- **Proven architecture** tested in production
- **Enterprise patterns** for security, monitoring, and compliance
- **Reusable roles** that work across Linux and macOS
- **Clear documentation** for rapid onboarding
- **Flexible configuration** via variables and Vault

---

## What Makes This Reusable

### 1. Modular Role Design

**Roles are self-contained, independently deployable units:**

```
roles/
├── common/                    # OS-independent foundation
│   ├── defaults/main.yml     # Sensible defaults for all projects
│   ├── tasks/                # Parameterized tasks
│   └── templates/            # Generic templates
└── system_hardening_macos/   # macOS-specific hardening
    ├── defaults/main.yml
    ├── tasks/
    └── README.md
```

**Key Principle**: Each role has `defaults/main.yml` with sensible defaults that can be overridden per project without modifying the role itself.

**Example**:
```yaml
# roles/common/defaults/main.yml
common_ntp_servers:
  - 0.pool.ntp.org
  - 1.pool.ntp.org
common_ssh_port: 22

# Your project overrides this in group_vars:
# inventories/projects/my-project/group_vars/all.yml
common_ntp_servers:
  - 10.0.1.5           # Your internal NTP
  - 8.8.8.8
common_ssh_port: 2222   # Your custom port
```

### 2. Flexible Inventory Structure

```
inventories/
├── projects/                 # Multi-project support
│   ├── _templates/          # Templates for new projects
│   ├── project-alpha/       # Your first project
│   ├── project-beta/        # Your second project
│   └── project-gamma/       # And so on...
├── shared/                  # Cross-project defaults
└── legacy/                  # Old structures (for migration)
```

**Benefit**: New projects follow a consistent pattern. Old inventories still work during migration.

### 3. Variable Hierarchy (Easy Customization)

```
Least Specific (Defaults)
↓
1. roles/<role>/defaults/main.yml          [Framework defaults]
2. inventories/shared/global_vars.yml      [Cross-project overrides]
3. inventories/projects/<project>/group_vars/all.yml        [Project defaults]
4. inventories/projects/<project>/group_vars/<group>.yml    [Group overrides]
5. inventories/projects/<project>/host_vars/<host>.yml      [Host-specific]
6. inventories/projects/<project>/group_vars/all_vault.yml  [Encrypted secrets]
7. playbook -e "var=value"                 [Runtime overrides]
↑
Most Specific (Highest Priority)
```

**Usage**: Override only what you need. Keep defaults as fallbacks.

### 4. Proven Playbooks

Three core playbooks handle all scenarios:

```yaml
# provision.yml    - Initial server setup
# configure.yml    - Full configuration stack
# maintenance.yml  - Updates, patches, cleanup
```

Each is **project-aware** and can target specific projects:

```bash
# Deploy to specific project
ansible-playbook playbooks/provision.yml \
  -i inventories/projects/my-project

# Or all projects
ansible-playbook playbooks/provision.yml \
  -i inventories/projects/
```

### 5. Secrets Management with Ansible Vault

```yaml
# Encrypted file (git-safe)
inventories/projects/my-project/group_vars/all_vault.yml

# Contains:
vault_grafana_admin_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256;...
vault_database_root_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256;...
```

**Benefit**: Secrets encrypted at rest, never exposed in git or logs.

### 6. Pre-Commit Hooks & Testing

```yaml
# .pre-commit-config.yaml automatically:
# - Validates YAML syntax
# - Runs ansible-lint
# - Prevents secrets in commits
# - Validates inventory structure
```

**Benefit**: Consistent code quality across all projects.

---

## For New Projects

### Quick Start (5 minutes)

#### Option 1: Clone & Customize (Recommended)

```bash
# Clone this repository
git clone <this-repo> my-infrastructure
cd my-infrastructure

# Create your first project from template
./scripts/scaffold-project.sh my-project

# Customize your inventory
edit inventories/projects/my-project/inventory.yml

# Test connectivity
ansible all -i inventories/projects/my-project -m ping

# Deploy!
ansible-playbook playbooks/provision.yml \
  -i inventories/projects/my-project
```

#### Option 2: Use as Remote Template

```bash
# Create new repo from this as template
# (GitHub: Use "Use this template" button)

# OR manually
git clone <this-repo> --single-branch new-project
cd new-project
rm -rf .git
git init
git add .
git commit -m "Initial commit: Infrastructure framework"
git remote add origin <your-new-repo>
git push -u origin main
```

### Project Structure

Once created, your project looks like:

```
my-infrastructure/
├── inventories/
│   └── projects/
│       └── my-project/
│           ├── inventory.yml              # Your servers
│           ├── group_vars/
│           │   ├── all.yml               # Project defaults
│           │   ├── webservers.yml        # Web server config
│           │   ├── databases.yml         # Database config
│           │   └── all_vault.yml         # Encrypted secrets
│           └── host_vars/
│               ├── web01.yml
│               ├── web02.yml
│               └── db01.yml
├── playbooks/
│   ├── provision.yml
│   ├── configure.yml
│   └── maintenance.yml
├── roles/
│   ├── common/
│   └── system_hardening_macos/
├── ansible.cfg
├── requirements.yml
└── Makefile
```

### Configuration Steps

#### Step 1: Define Your Servers

```yaml
# inventories/projects/my-project/inventory.yml
all:
  children:
    webservers:
      hosts:
        web01:
          ansible_host: 10.0.1.10
        web02:
          ansible_host: 10.0.1.11
    databases:
      hosts:
        db01:
          ansible_host: 10.0.2.10
  vars:
    ansible_user: ubuntu
    ansible_port: 22
```

#### Step 2: Set Project Defaults

```yaml
# inventories/projects/my-project/group_vars/all.yml
---
# Project Identification
project_name: my-project
project_env: production
project_owner: your-team

# Common Configuration
common_ntp_servers:
  - 10.0.1.5
  - 8.8.8.8
common_ssh_port: 2222

# Monitoring
monitoring_enabled: true
monitoring_grafana_enabled: true

# Security
security_hardening_level: production
ssh_hardening_enabled: true
```

#### Step 3: Set Secrets (Encrypted)

```bash
# Create and encrypt secrets
ansible-vault create inventories/projects/my-project/group_vars/all_vault.yml

# Add content:
vault_grafana_admin_password: "your-secure-password"
vault_prometheus_scrape_token: "your-token"
vault_database_root_password: "your-db-password"

# Save and close (Ctrl-D if using stdin)
```

#### Step 4: Deploy

```bash
# Provision servers
ansible-playbook playbooks/provision.yml \
  -i inventories/projects/my-project \
  --vault-password-file ~/.vault_password

# Configure services
ansible-playbook playbooks/configure.yml \
  -i inventories/projects/my-project \
  --vault-password-file ~/.vault_password
```

---

## For New Team Members

### Onboarding (1 hour)

#### 1. Clone and Setup (10 minutes)

```bash
git clone <repo> ansible-infra
cd ansible-infra

# Install dependencies
ansible-galaxy collection install -r requirements.yml

# Verify installation
ansible-inventory -i inventories/projects --list
```

#### 2. Understand the Structure (15 minutes)

Read these in order:
1. **README.md** - Project overview
2. **docs/ARCHITECTURE.md** - Design decisions
3. **docs/QUICK_START.md** - Basic operations

#### 3. Explore Existing Projects (15 minutes)

```bash
# List all projects
ls -la inventories/projects/

# Explore project structure
tree inventories/projects/project-alpha/

# View project config
cat inventories/projects/project-alpha/inventory.yml
cat inventories/projects/project-alpha/group_vars/all.yml
```

#### 4. Practice (20 minutes)

```bash
# Test connectivity to a project
ansible all -i inventories/projects/project-alpha -m ping

# Run a playbook in check mode (no changes)
ansible-playbook playbooks/provision.yml \
  -i inventories/projects/project-alpha \
  -C

# Look at facts for a specific host
ansible web01 -i inventories/projects/project-alpha -m setup
```

### Key Concepts to Understand

#### 1. Variable Precedence

Variables are applied in this order (later ones override earlier):

1. **Role defaults** - Built into roles
2. **Global defaults** - `inventories/shared/global_vars.yml`
3. **Project defaults** - `inventories/projects/<project>/group_vars/all.yml`
4. **Group overrides** - `inventories/projects/<project>/group_vars/<group>.yml`
5. **Host overrides** - `inventories/projects/<project>/host_vars/<host>.yml`
6. **Vault secrets** - `inventories/projects/<project>/group_vars/all_vault.yml`
7. **Runtime** - `ansible-playbook -e "var=value"`

**Example**: SSH port
```yaml
# Role default: 22
# Project override: 2222
# Host override: 2223
# Result: Host uses 2223, others use 2222
```

#### 2. Idempotency

All playbooks are **idempotent** - safe to run multiple times:

```bash
# First run
ansible-playbook playbooks/provision.yml -i inventories/projects/my-project

# Second run (same result, no changes if config unchanged)
ansible-playbook playbooks/provision.yml -i inventories/projects/my-project
```

#### 3. Secrets Management

Never commit unencrypted secrets. Always use Vault:

```bash
# Good: Encrypted in git
inventories/projects/my-project/group_vars/all_vault.yml
$ANSIBLE_VAULT;1.1;AES256;...

# Bad: Plaintext in git (will be caught by pre-commit hooks)
password: my-secret-password
```

---

## Customization Patterns

### Pattern 1: Add a New Role

```bash
# Create role structure
mkdir -p roles/my-feature/{tasks,defaults,templates,vars}

# Add tasks
cat > roles/my-feature/tasks/main.yml << 'EOF'
---
- name: Configure my feature
  debug:
    msg: "Configuring {{ my_feature_name }}"
EOF

# Add defaults
cat > roles/my-feature/defaults/main.yml << 'EOF'
---
my_feature_name: "default-value"
my_feature_enabled: true
EOF

# Include in playbook
# Add to playbooks/configure.yml:
#   roles:
#     - my-feature
```

### Pattern 2: Override Role Defaults Per Project

```yaml
# inventories/projects/my-project/group_vars/all.yml
---
# Override role defaults
common_ssh_port: 2222
common_ntp_servers:
  - 10.0.1.5

# Add new variables for custom roles
my_feature_name: "custom-value"
my_feature_enabled: false
```

### Pattern 3: Create Project-Specific Variables

```yaml
# inventories/projects/my-project/group_vars/all.yml
---
# Standard variables from roles
common_hostname_prefix: myproject

# Your custom variables
my_app_version: "2.1.0"
my_app_port: 8080
my_app_replicas: 3
```

### Pattern 4: Override by Group or Host

```yaml
# inventories/projects/my-project/group_vars/webservers.yml
---
# Only webservers get these settings
common_ssh_port: 2222
enable_caching: true
max_connections: 1000

# inventories/projects/my-project/host_vars/web01.yml
---
# Only this host gets this setting
enable_monitoring: false  # Special case
```

---

## FAQ & Troubleshooting

### Q: How do I use this for a completely different type of infrastructure?

**A**: Clone and customize:

1. Keep `roles/common` (universal foundation)
2. Replace `roles/system_hardening_macos` with your needs
3. Add new roles as needed
4. Keep the same playbook and inventory structure
5. Update documentation

**Example**: For Kubernetes infrastructure, replace system roles with Kubernetes-specific roles.

### Q: Can I use this with existing servers (non-greenfield)?

**A**: Yes! Use these approaches:

```bash
# Option 1: Idempotent playbooks (safe for existing servers)
ansible-playbook playbooks/provision.yml -i inventories/projects/my-project -C

# Option 2: Selective role application
ansible-playbook playbooks/provision.yml \
  -i inventories/projects/my-project \
  --tags "ntp,ssh" \
  -C

# Option 3: Run in check mode first
ansible-playbook playbooks/provision.yml \
  -i inventories/projects/my-project \
  --check
```

### Q: How do I handle secrets for different environments?

**A**: Create separate Vault files:

```bash
# Production secrets
ansible-vault create inventories/projects/my-project-prod/group_vars/all_vault.yml

# Staging secrets
ansible-vault create inventories/projects/my-project-staging/group_vars/all_vault.yml

# Different passwords per environment
# Store in: ~/.vault_passwords/my-project-prod
# Store in: ~/.vault_passwords/my-project-staging
```

### Q: How do I test changes before deploying to production?

**A**: Use staging environment:

```bash
# 1. Test in check mode
ansible-playbook playbooks/configure.yml \
  -i inventories/projects/staging \
  --check

# 2. Test in staging environment
ansible-playbook playbooks/configure.yml \
  -i inventories/projects/staging

# 3. Verify results
ansible all -i inventories/projects/staging -m ping

# 4. Deploy to production
ansible-playbook playbooks/configure.yml \
  -i inventories/projects/production
```

### Q: How do I add hosts to an existing project?

**A**: Add to inventory and variables:

```yaml
# inventories/projects/my-project/inventory.yml
all:
  children:
    webservers:
      hosts:
        web01:
          ansible_host: 10.0.1.10
        web02:  # NEW
          ansible_host: 10.0.1.11
        web03:  # NEW
          ansible_host: 10.0.1.12

# inventories/projects/my-project/host_vars/web02.yml
---
ansible_host: 10.0.1.11
hostname: web02-prod

# inventories/projects/my-project/host_vars/web03.yml
---
ansible_host: 10.0.1.12
hostname: web03-prod
```

### Q: How do I migrate from this framework to a different tool later?

**A**: All your configuration is in YAML files. You can:

1. Export inventory to JSON/YAML
2. Export variables to a structured format
3. Write conversion tools
4. Export playbooks to Terraform, CloudFormation, etc.

**No vendor lock-in** - everything is standard Ansible and YAML.

### Q: What if I need to customize roles for my project?

**A**: **Don't modify roles directly!** Instead:

```bash
# Option 1: Use variable overrides (preferred)
# inventories/projects/my-project/group_vars/all.yml
my_custom_setting: true

# Option 2: Create project-specific role
mkdir -p roles/my-project-customization
# Add your customization tasks
# Include in playbook after the base role

# Option 3: Create role variant
mkdir -p roles/common-my-project
# Copy from common/ and customize
# Include in playbook instead of common
```

---

## Next Steps

### For Your First Project

1. ✅ Clone this repository
2. ✅ Run `./scripts/scaffold-project.sh my-first-project`
3. ✅ Edit `inventories/projects/my-first-project/inventory.yml`
4. ✅ Edit `inventories/projects/my-first-project/group_vars/all.yml`
5. ✅ Create Vault secrets: `ansible-vault create ...`
6. ✅ Test: `ansible all -i inventories/projects/my-first-project -m ping`
7. ✅ Deploy: `ansible-playbook playbooks/provision.yml -i inventories/projects/my-first-project`

### For Future Teams

Provide them with:
- [ ] This guide (PROJECT_REUSABILITY_GUIDE.md)
- [ ] QUICK_START.md for immediate productivity
- [ ] ARCHITECTURE.md for deep understanding
- [ ] Example projects in `inventories/projects/`
- [ ] Video tutorials (optional but helpful)

---

## Support & Learning

- **Ansible Documentation**: https://docs.ansible.com
- **Best Practices**: https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html
- **Inventory Guide**: https://docs.ansible.com/ansible/latest/user_guide/inventory.html
- **Vault Documentation**: https://docs.ansible.com/ansible/latest/user_guide/vault.html

---

**Last Updated**: 2025-11-16
**For Questions**: See TROUBLESHOOTING.md
