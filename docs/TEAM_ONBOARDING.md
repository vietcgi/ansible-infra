# Team Onboarding Guide

**Get new team members productive with this Ansible framework in 1 hour**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Onboarding (30 minutes)](#quick-onboarding-30-minutes)
3. [Deep Dive (30 minutes)](#deep-dive-30-minutes)
4. [Hands-On Practice](#hands-on-practice)
5. [Knowledge Check](#knowledge-check)
6. [Support & Next Steps](#support--next-steps)

---

## Prerequisites

### System Requirements

Before starting, ensure you have:

```bash
# Required
git --version # Any recent version
ansible --version # 2.10 or later
python3 --version # 3.8 or later
ssh -V # OpenSSH (usually pre-installed)

# Nice to have
vim --version # Or your favorite editor
jq --version # For JSON processing
```

### Installation (if needed)

```bash
# macOS
brew install ansible git python3

# Ubuntu/Debian
sudo apt update
sudo apt install ansible git python3-pip

# Check installation
ansible --version # Should show 2.10+
```

### Access & Permissions

Before starting, you'll need:

- [ ] Git access to the repository
- [ ] SSH access to at least one test server (or use local testing)
- [ ] Vault password for secrets (ask team lead)
- [ ] Read access to this documentation

---

## Quick Onboarding (30 minutes)

### Step 1: Clone the Repository (5 minutes)

```bash
# Clone the repository
git clone <repository-url> ansible-infra
cd ansible-infra

# Verify structure
ls -la

# You should see:
# - roles/ (reusable Ansible roles)
# - playbooks/ (main playbooks)
# - inventories/ (server definitions)
# - docs/ (documentation)
# - ansible.cfg (Ansible configuration)
# - requirements.yml (dependencies)
```

### Step 2: Install Dependencies (5 minutes)

```bash
# Install Ansible collections
ansible-galaxy collection install -r requirements.yml

# Expected output:
# Starting galaxy collection install process
# process_dependency grafana.grafana...
# Installing 'grafana.grafana:6.0.6' to...
# ...
# Collection installed successfully
```

### Step 3: Understand the Structure (10 minutes)

Read these files in this order:

```bash
# 1. Overview (2 minutes)
cat README.md

# 2. Architecture (5 minutes)
cat docs/ARCHITECTURE.md | head -100

# 3. Quick start (3 minutes)
cat docs/NEW_PROJECT_QUICKSTART.md | head -50
```

### Step 4: Explore an Example Project (10 minutes)

```bash
# List available projects
ls -la inventories/projects/

# Explore the example project
cd inventories/projects/example-project/

# View server definitions
cat inventory.yml

# View project configuration
cat group_vars/all.yml

# View group-specific settings
cat group_vars/webservers.yml

# Go back to root
cd /path/to/ansible-infra
```

---

## Deep Dive (30 minutes)

### Understanding the Framework

#### 1. Projects vs Roles (5 minutes)

**Projects**: Individual infrastructure deployments

```
inventories/projects/
├── example-project/ ← Your first project
├── customer-alpha/ ← Another project
└── staging/ ← Another project
```

**Roles**: Reusable components used by projects

```
roles/
├── common/ ← Foundation setup
├── system_hardening_macos/ ← macOS-specific
└── (add your own)
```

**Key Principle**: Roles define WHAT, projects define WHERE

#### 2. Variable Hierarchy (10 minutes)

Variables are applied in this order (later ones override earlier):

```
1. roles/<role>/defaults/main.yml [Framework defaults]
 ↓ (override with)
2. inventories/shared/global_vars.yml [Cross-project]
 ↓ (override with)
3. group_vars/all.yml [Project-wide]
 ↓ (override with)
4. group_vars/<group>.yml [Group-specific]
 ↓ (override with)
5. host_vars/<host>.yml [Host-specific]
 ↓ (override with)
6. group_vars/all_vault.yml [Encrypted secrets]
 ↓ (override with)
7. ansible-playbook -e "var=value" [Runtime]
```

**Example**: SSH port configuration

```yaml
# Role default (roles/common/defaults/main.yml)
common_ssh_port: 22

# Project override (group_vars/all.yml)
common_ssh_port: 2222 # All servers in project use 2222

# Group override (group_vars/webservers.yml)
common_ssh_port: 2223 # Web servers use 2223

# Host override (host_vars/web01.yml)
common_ssh_port: 2224 # Only web01 uses 2224

# Result:
# web01: 2224 (host override)
# web02: 2223 (group override)
# db01: 2222 (project override)
```

#### 3. The Three Main Playbooks (10 minutes)

**provision.yml** - Initial server setup

```bash
ansible-playbook playbooks/provision.yml -i inventories/projects/my-project
# Runs: OS updates, core packages, NTP, SSH hardening, sysctl tuning
```

**configure.yml** - Service configuration

```bash
ansible-playbook playbooks/configure.yml -i inventories/projects/my-project
# Runs: Monitoring setup, Grafana, Prometheus, Loki, Node Exporter
```

**maintenance.yml** - Ongoing maintenance

```bash
ansible-playbook playbooks/maintenance.yml -i inventories/projects/my-project
# Runs: Package updates, log rotation, cache cleanup, validation
```

#### 4. Secrets Management with Vault (5 minutes)

**Never commit unencrypted secrets!**

```bash
# Create encrypted secrets file
ansible-vault create inventories/projects/my-project/group_vars/all_vault.yml

# Edit encrypted file
ansible-vault edit inventories/projects/my-project/group_vars/all_vault.yml

# Use in playbooks
vault_grafana_admin_password: "secret123"

# Access in playbook
- name: Set Grafana password
 grafana_user:
 password: "{{ vault_grafana_admin_password }}"
 no_log: true # Important: never log passwords
```

---

## Hands-On Practice

### Exercise 1: Create Your First Project (15 minutes)

```bash
# 1. Create project from template
./scripts/scaffold-project.sh my-first-project

# 2. View the created structure
ls -la inventories/projects/my-first-project/

# 3. Edit the inventory
edit inventories/projects/my-first-project/inventory.yml

# Add a sample server:
all:
 children:
 webservers:
 hosts:
 web01:
 ansible_host: localhost # For testing locally

# 4. Edit project defaults
edit inventories/projects/my-first-project/group_vars/all.yml

# Change:
project_name: my-first-project
project_owner: your-name

# 5. Test your inventory
ansible all -i inventories/projects/my-first-project --list-hosts

# Expected: Should list web01
```

### Exercise 2: Understand Variable Overrides (10 minutes)

```bash
# 1. Check default SSH port (from role)
grep "common_ssh_port" roles/common/defaults/main.yml

# Expected: common_ssh_port: 22

# 2. Override in project
edit inventories/projects/my-first-project/group_vars/all.yml

# Add:
common_ssh_port: 2222

# 3. Verify with ansible
ansible all -i inventories/projects/my-first-project -m debug \
 -a "var=common_ssh_port"

# Expected: web01 should show 2222
```

### Exercise 3: Test Playbook (Check Mode) (10 minutes)

```bash
# 1. Run provision playbook in check mode (no changes)
ansible-playbook playbooks/provision.yml \
 -i inventories/projects/my-first-project \
 --check \
 --diff

# 2. Review what WOULD change
# (Don't worry if some tasks are skipped)

# 3. Run specific task
ansible-playbook playbooks/provision.yml \
 -i inventories/projects/my-first-project \
 --tags "ntp" \
 --check

# Expected: Should show NTP configuration changes
```

### Exercise 4: Create Host-Specific Config (10 minutes)

```bash
# 1. Copy host template
cp inventories/projects/my-first-project/host_vars/EXAMPLE_HOST.yml \
 inventories/projects/my-first-project/host_vars/web01.yml

# 2. Edit host config
edit inventories/projects/my-first-project/host_vars/web01.yml

# Change:
ansible_host: 10.0.1.10
hostname: web01-prod
disk_capacity_gb: 500

# 3. Verify with ansible
ansible web01 -i inventories/projects/my-first-project -m debug \
 -a "var=hostname"

# Expected: Should show "web01-prod"
```

---

## Knowledge Check

### Quiz Yourself

**Q1: Where do role defaults live?**
<details>
<summary>Answer</summary>
`roles/<role>/defaults/main.yml`
</details>

**Q2: What overrides role defaults?**
<details>
<summary>Answer</summary>
Anything in: global_vars.yml, group_vars/all.yml, group_vars/<group>.yml, host_vars/<host>.yml, all_vault.yml, or -e flags
</details>

**Q3: Which file should secrets go in?**
<details>
<summary>Answer</summary>
`group_vars/all_vault.yml` (encrypted with ansible-vault)
</details>

**Q4: What's the difference between provision.yml and configure.yml?**
<details>
<summary>Answer</summary>
- provision.yml: OS-level setup (updates, packages, NTP, SSH hardening)
- configure.yml: Service setup (Grafana, Prometheus, monitoring)
</details>

**Q5: How do you run a playbook in check mode?**
<details>
<summary>Answer</summary>
`ansible-playbook playbooks/provision.yml -i inventories/projects/my-project --check`
</details>

---

## Common Tasks

### Create a New Project

```bash
./scripts/scaffold-project.sh my-new-project
edit inventories/projects/my-new-project/inventory.yml
edit inventories/projects/my-new-project/group_vars/all.yml
ansible-playbook playbooks/provision.yml -i inventories/projects/my-new-project
```

### Deploy to Existing Project

```bash
# Provision (OS-level setup)
ansible-playbook playbooks/provision.yml \
 -i inventories/projects/my-project \
 --vault-password-file ~/.vault_password

# Configure (services)
ansible-playbook playbooks/configure.yml \
 -i inventories/projects/my-project \
 --vault-password-file ~/.vault_password
```

### Test Without Making Changes

```bash
ansible-playbook playbooks/provision.yml \
 -i inventories/projects/my-project \
 --check \
 --diff
```

### Run Specific Roles/Tags

```bash
# Only NTP
ansible-playbook playbooks/provision.yml \
 -i inventories/projects/my-project \
 --tags "ntp"

# Skip monitoring
ansible-playbook playbooks/configure.yml \
 -i inventories/projects/my-project \
 --skip-tags "monitoring"
```

### Get Host Information

```bash
# List all hosts in project
ansible all -i inventories/projects/my-project --list-hosts

# Get specific variable
ansible web01 -i inventories/projects/my-project -m debug -a "var=common_ssh_port"

# Get all facts
ansible web01 -i inventories/projects/my-project -m setup
```

---

## Troubleshooting

### "SSH connection refused"

```bash
# 1. Verify host is reachable
ping 10.0.1.10

# 2. Check SSH is listening
ssh -v ubuntu@10.0.1.10

# 3. Add host to known_hosts
ssh-keyscan -H 10.0.1.10 >> ~/.ssh/known_hosts

# 4. Verify ansible inventory
ansible all -i inventories/projects/my-project -m ping
```

### "Ansible module not found"

```bash
# Reinstall collections
ansible-galaxy collection install -r requirements.yml

# Verify installation
ansible-galaxy collection list | grep grafana
```

### "Vault password error"

```bash
# Create vault password file
echo "your-vault-password" > ~/.vault_password
chmod 600 ~/.vault_password

# Use in playbook
ansible-playbook playbooks/provision.yml \
 -i inventories/projects/my-project \
 --vault-password-file ~/.vault_password
```

### "Playbook hangs or times out"

```bash
# Run with verbose output to see where it's hanging
ansible-playbook playbooks/provision.yml \
 -i inventories/projects/my-project \
 -vvv

# Increase timeout
ansible-playbook playbooks/provision.yml \
 -i inventories/projects/my-project \
 --timeout=60
```

---

## Support & Next Steps

### When You're Stuck

1. **Check the docs**
 - README.md - Overview
 - docs/ARCHITECTURE.md - Design decisions
 - docs/NEW_PROJECT_QUICKSTART.md - Step-by-step guide
 - docs/TROUBLESHOOTING.md - Common issues

2. **Run in verbose mode**
 ```bash
 ansible-playbook playbooks/provision.yml \
 -i inventories/projects/my-project \
 -vvv
 ```

3. **Check server logs**
 ```bash
 ssh ubuntu@10.0.1.10
 tail -f /var/log/syslog
 journalctl -u grafana-agent -f
 ```

4. **Ask for help**
 - Create a GitHub issue with full output
 - Include playbook output (redact secrets)
 - Include your inventory (redact IPs/credentials)

### Learning Path

**Day 1: Basics**
- [ ] Complete "Quick Onboarding" section
- [ ] Do Exercise 1: Create first project
- [ ] Read README.md
- [ ] Take knowledge check quiz

**Day 2: Deep Dive**
- [ ] Complete "Deep Dive" section
- [ ] Do Exercises 2-4
- [ ] Read docs/ARCHITECTURE.md
- [ ] Explore roles/common/

**Day 3: Real Projects**
- [ ] Create your first production project
- [ ] Test with check mode
- [ ] Deploy to staging
- [ ] Monitor results

**Day 4+: Mastery**
- [ ] Customize roles for your needs
- [ ] Create new roles
- [ ] Help onboard other team members
- [ ] Document your patterns

### Next Steps

1. **Complete the exercises above**
2. **Create a real project** following NEW_PROJECT_QUICKSTART.md
3. **Read** docs/ARCHITECTURE.md for deeper understanding
4. **Explore** docs/PROJECT_REUSABILITY_GUIDE.md for advanced patterns
5. **Join** team discussions about infrastructure changes

### Resources

- **Ansible Documentation**: https://docs.ansible.com
- **Ansible Best Practices**: https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html
- **Variable Precedence**: https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#variable-precedence-where-should-i-put-a-variable
- **Vault Documentation**: https://docs.ansible.com/ansible/latest/user_guide/vault.html

---

## Welcome to the Team!

You're now part of the infrastructure team. This framework is designed to make your job easier while keeping things safe and consistent.

**Remember**:
- Test in staging first
- Use check mode to preview changes
- Never commit unencrypted secrets
- Ask questions - that's how we all learn

Happy deploying! 

---

**Questions?** Open an issue or reach out to your team lead.

**Last Updated**: 2025-11-16
**Version**: 1.0
**Time to Complete**: 1 hour
