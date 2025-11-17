# New Project Quick Start

**Get a new infrastructure project running in 15 minutes**

---

## Prerequisites

```bash
# Check you have these installed
ansible --version # 2.10+
python --version # 3.8+
git --version # Any recent version
ansible-galaxy --version # Should come with ansible
```

If anything is missing, see [Installation Guide](INSTALLATION.md).

---

## Step 1: Clone This Repository (2 minutes)

```bash
# Option A: Clone as base for new project
git clone <this-repo-url> my-infrastructure
cd my-infrastructure

# Option B: Use as GitHub template
# Click "Use this template" on GitHub (recommended)
```

---

## Step 2: Create Your Project Structure (1 minute)

```bash
# Method 1: Automatic (recommended)
./scripts/scaffold-project.sh my-project

# Method 2: Manual
mkdir -p inventories/projects/my-project/{group_vars,host_vars}
cp -r inventories/projects/_templates/* inventories/projects/my-project/
```

Output:
```
inventories/projects/my-project/
├── inventory.yml
├── group_vars/
│ ├── all.yml
│ ├── webservers.yml
│ ├── databases.yml
│ ├── monitoring_disabled.yml
│ └── all_vault.yml (encrypted)
└── host_vars/
```

---

## Step 3: Define Your Servers (3 minutes)

Edit `inventories/projects/my-project/inventory.yml`:

```yaml
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

 monitoring_servers:
 hosts:
 prometheus01:
 ansible_host: 10.0.3.10
 grafana01:
 ansible_host: 10.0.3.20

 vars:
 ansible_user: ubuntu # SSH user
 ansible_port: 22 # SSH port
 ansible_python_interpreter: /usr/bin/python3
```

**Tips**:
- Use hostnames or IPs in `ansible_host:`
- Group related servers together
- Keep `vars:` for common settings

---

## Step 4: Configure Project Defaults (3 minutes)

Edit `inventories/projects/my-project/group_vars/all.yml`:

```yaml
---
# Project Identity
project_name: my-project
project_env: production
project_owner: your-team
project_description: "My first infrastructure project"

# Server Configuration
common_hostname_prefix: myproj
common_ntp_servers:
 - 0.ubuntu.pool.ntp.org
 - 1.ubuntu.pool.ntp.org
common_ssh_port: 2222

# Monitoring (optional)
monitoring_enabled: true
monitoring_grafana_enabled: true
monitoring_prometheus_enabled: true
monitoring_loki_enabled: false

# Security
security_hardening_level: production
ssh_hardening_enabled: true
firewall_enabled: true
```

**Available Variables**: See [docs/ARCHITECTURE.md](ARCHITECTURE.md#variable-reference) for complete list.

---

## Step 5: Set Up Secrets (Vault) (2 minutes)

```bash
# Create encrypted secrets file
ansible-vault create inventories/projects/my-project/group_vars/all_vault.yml

# This opens an editor. Add your secrets:
vault_grafana_admin_password: "SecurePassword123!"
vault_prometheus_scrape_token: "your-token-here"
vault_database_root_password: "DBPassword456!"
vault_ssh_key_private: |
 -----BEGIN OPENSSH PRIVATE KEY-----
 ...your-key-content...
 -----END OPENSSH PRIVATE KEY-----

# Save and close the editor
```

**Security Tips**:
- Never commit unencrypted secrets
- Use strong passwords (20+ characters)
- Store vault password in `~/.vault_password` (not in git)

---

## Step 6: Test Connectivity (2 minutes)

```bash
# Install dependencies
ansible-galaxy collection install -r requirements.yml

# Test SSH connectivity
ansible all -i inventories/projects/my-project -m ping

# Expected output:
# web01 | SUCCESS => {
# "ansible_facts": {
# "discovered_interpreter_python": "/usr/bin/python3"
# },
# "changed": false,
# "ping": "pong"
# }
```

**If this fails**:
- Check `ansible_host` values are correct
- Verify SSH keys are configured
- Check firewall allows SSH (port 22 or custom port)
- Run with `-vvv` for debugging: `ansible all -i inventories/projects/my-project -m ping -vvv`

---

## Step 7: Deploy to Your Servers (2 minutes)

```bash
# Option 1: Dry-run first (safe, no changes)
ansible-playbook playbooks/provision.yml \
 -i inventories/projects/my-project \
 --check

# Option 2: Actually deploy
ansible-playbook playbooks/provision.yml \
 -i inventories/projects/my-project \
 --vault-password-file ~/.vault_password

# Option 3: Deploy specific servers
ansible-playbook playbooks/provision.yml \
 -i inventories/projects/my-project \
 -l webservers \
 --vault-password-file ~/.vault_password
```

---

## Step 8: Configure Services (Variable)

After provisioning, configure services:

```bash
# Full configuration
ansible-playbook playbooks/configure.yml \
 -i inventories/projects/my-project \
 --vault-password-file ~/.vault_password

# Specific roles only
ansible-playbook playbooks/configure.yml \
 -i inventories/projects/my-project \
 --tags "grafana,prometheus" \
 --vault-password-file ~/.vault_password

# Skip monitoring
ansible-playbook playbooks/configure.yml \
 -i inventories/projects/my-project \
 --skip-tags "monitoring" \
 --vault-password-file ~/.vault_password
```

---

## What Gets Deployed

### By Default (provision.yml)

- OS updates and patches
- Core packages (git, curl, wget, etc.)
- NTP synchronization
- SSH hardening
- Sysctl tuning
- Audit logging
- Firewall configuration
- User management

### With configure.yml

- Grafana Agent (monitoring)
- Prometheus (metrics)
- Loki (logs)
- Node Exporter (system metrics)
- Custom service configuration

---

## Common Tasks

### Add a New Server

```bash
# 1. Add to inventory
# inventories/projects/my-project/inventory.yml
databases:
 hosts:
 db02: # NEW
 ansible_host: 10.0.2.11

# 2. Create host-specific config (optional)
# inventories/projects/my-project/host_vars/db02.yml
ansible_host: 10.0.2.11
hostname: db02-prod
disk_capacity_gb: 1000

# 3. Deploy to new server
ansible-playbook playbooks/provision.yml \
 -i inventories/projects/my-project \
 -l db02
```

### Update Configuration

```bash
# 1. Edit group_vars or host_vars
edit inventories/projects/my-project/group_vars/all.yml

# 2. Test changes
ansible-playbook playbooks/configure.yml \
 -i inventories/projects/my-project \
 --check

# 3. Apply changes
ansible-playbook playbooks/configure.yml \
 -i inventories/projects/my-project
```

### Disable Monitoring

```bash
# Edit group_vars/all.yml
monitoring_enabled: false

# Or skip during playbook
ansible-playbook playbooks/configure.yml \
 -i inventories/projects/my-project \
 --skip-tags "monitoring"
```

### Access Grafana

```bash
# After deploy, Grafana is at:
http://<grafana-server>:3000

# Default credentials:
# Username: admin
# Password: (from vault_grafana_admin_password)
```

---

## Customization

### Change SSH Port

```yaml
# inventories/projects/my-project/group_vars/all.yml
common_ssh_port: 2222
```

### Change NTP Servers

```yaml
# inventories/projects/my-project/group_vars/all.yml
common_ntp_servers:
 - 10.0.1.5 # Your internal NTP
 - 8.8.8.8 # Google DNS
```

### Disable Specific Features

```yaml
# inventories/projects/my-project/group_vars/all.yml
ssh_hardening_enabled: false
firewall_enabled: false
security_hardening_level: minimal # or 'production'
```

### Group-Specific Settings

```yaml
# inventories/projects/my-project/group_vars/webservers.yml
common_ssh_port: 2223 # Different port for web servers
enable_caching: true # Enable caching for web servers
max_connections: 5000 # Higher limit for web servers
```

### Host-Specific Settings

```yaml
# inventories/projects/my-project/host_vars/web01.yml
ansible_host: 10.0.1.10
hostname: web01-prod
enable_monitoring: false # Special case for this host
disk_capacity_gb: 500 # More disk for this server
```

---

## Troubleshooting

### SSH Connection Refused

```bash
# Check host is reachable
ping 10.0.1.10

# Check SSH is listening
ssh -v ubuntu@10.0.1.10

# Check known_hosts
ssh-keyscan -H 10.0.1.10 >> ~/.ssh/known_hosts

# Try with verbose ansible
ansible all -i inventories/projects/my-project -m ping -vvv
```

### Vault Password Issues

```bash
# Store password in file
echo "your-vault-password" > ~/.vault_password
chmod 600 ~/.vault_password

# Use password file
ansible-playbook playbooks/provision.yml \
 -i inventories/projects/my-project \
 --vault-password-file ~/.vault_password

# Or enter interactively
ansible-playbook playbooks/provision.yml \
 -i inventories/projects/my-project \
 --ask-vault-pass
```

### Playbook Hangs or Times Out

```bash
# Increase timeout
ansible-playbook playbooks/provision.yml \
 -i inventories/projects/my-project \
 --timeout=60

# Run with verbose output
ansible-playbook playbooks/provision.yml \
 -i inventories/projects/my-project \
 -vvv

# Check server logs
ssh ubuntu@10.0.1.10 'tail -f /var/log/syslog'
```

### Check Mode Shows Too Many Changes

```bash
# Run in check mode
ansible-playbook playbooks/provision.yml \
 -i inventories/projects/my-project \
 --check

# See what would change (verbose)
ansible-playbook playbooks/provision.yml \
 -i inventories/projects/my-project \
 --check -vvv

# Review the diffs carefully before deploying
```

---

## Next Steps

### 1. Understand the Architecture
- Read [docs/ARCHITECTURE.md](ARCHITECTURE.md)
- Understand variable hierarchy
- Learn about roles

### 2. Customize for Your Needs
- Create additional roles
- Override variables per project
- Add custom playbooks

### 3. Set Up for Multiple Projects
- Follow [docs/PROJECT_REUSABILITY_GUIDE.md](PROJECT_REUSABILITY_GUIDE.md)
- Create project templates
- Document your patterns

### 4. Production Deployment
- Test in staging first
- Document your runbooks
- Set up monitoring
- Plan for disaster recovery

---

## Quick Command Reference

```bash
# List all hosts in project
ansible all -i inventories/projects/my-project --list-hosts

# Get facts from specific host
ansible web01 -i inventories/projects/my-project -m setup

# Run ad-hoc command
ansible webservers -i inventories/projects/my-project -m shell -a "uptime"

# Dry-run (check mode)
ansible-playbook playbooks/provision.yml -i inventories/projects/my-project --check

# Deploy with specific tags
ansible-playbook playbooks/configure.yml -i inventories/projects/my-project --tags "ssh,firewall"

# Skip specific tags
ansible-playbook playbooks/configure.yml -i inventories/projects/my-project --skip-tags "monitoring"

# Target specific hosts
ansible-playbook playbooks/provision.yml -i inventories/projects/my-project -l web01

# Verbose output
ansible-playbook playbooks/provision.yml -i inventories/projects/my-project -vvv

# With vault password
ansible-playbook playbooks/provision.yml -i inventories/projects/my-project --vault-password-file ~/.vault_password
```

---

## Support

**Questions?**
- See [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Read [docs/PROJECT_REUSABILITY_GUIDE.md](PROJECT_REUSABILITY_GUIDE.md)
- Check [Ansible Documentation](https://docs.ansible.com)

**Found an issue?**
- Create an issue in GitHub
- Include playbook output with `-vvv`
- Include your inventory (redact secrets)

---

**Last Updated**: 2025-11-16
**Time to Complete**: 15 minutes
**Difficulty**: Beginner-friendly
