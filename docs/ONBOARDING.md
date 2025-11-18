# Onboarding Guide

Complete guide for onboarding team members and clients to the Ansible infrastructure framework.

---

## Table of Contents

1. [Team Member Onboarding](#team-member-onboarding)
2. [Client Onboarding](#client-onboarding)
3. [Shared Procedures](#shared-procedures)
4. [Access Provisioning](#access-provisioning)

---

## Team Member Onboarding

**Get new team members productive with this Ansible framework in 1 hour**

### Prerequisites

#### System Requirements

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

#### Installation (if needed)

```bash
# macOS
brew install ansible git python3

# Ubuntu/Debian
sudo apt update
sudo apt install ansible git python3-pip

# Check installation
ansible --version # Should show 2.10+
```

#### Access & Permissions

Before starting, you'll need:

- [ ] Git access to the repository
- [ ] SSH access to at least one test server (or use local testing)
- [ ] Vault password for secrets (ask team lead)
- [ ] Read access to this documentation

---

### Quick Onboarding (30 minutes)

#### Step 1: Clone the Repository (5 minutes)

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

#### Step 2: Install Dependencies (5 minutes)

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

#### Step 3: Understand the Structure (10 minutes)

Read these files in this order:

```bash
# 1. Overview (2 minutes)
cat README.md

# 2. Architecture (5 minutes)
cat docs/ARCHITECTURE.md | head -100

# 3. Quick start (3 minutes)
cat START_HERE.md | head -50
```

#### Step 4: Explore an Example Project (10 minutes)

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

### Deep Dive (30 minutes)

#### Understanding the Framework

**1. Projects vs Roles (5 minutes)**

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

**2. Variable Hierarchy (10 minutes)**

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

**3. The Three Main Playbooks (10 minutes)**

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

**4. Secrets Management with Vault (5 minutes)**

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

### Hands-On Practice

#### Exercise 1: Create Your First Project (15 minutes)

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

#### Exercise 2: Understand Variable Overrides (10 minutes)

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

#### Exercise 3: Test Playbook (Check Mode) (10 minutes)

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

#### Exercise 4: Create Host-Specific Config (10 minutes)

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

### Knowledge Check

#### Quiz Yourself

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

### Common Tasks for Team Members

#### Create a New Project

```bash
./scripts/scaffold-project.sh my-new-project
edit inventories/projects/my-new-project/inventory.yml
edit inventories/projects/my-new-project/group_vars/all.yml
ansible-playbook playbooks/provision.yml -i inventories/projects/my-new-project
```

#### Deploy to Existing Project

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

#### Test Without Making Changes

```bash
ansible-playbook playbooks/provision.yml \
  -i inventories/projects/my-project \
  --check \
  --diff
```

#### Run Specific Roles/Tags

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

#### Get Host Information

```bash
# List all hosts in project
ansible all -i inventories/projects/my-project --list-hosts

# Get specific variable
ansible web01 -i inventories/projects/my-project -m debug -a "var=common_ssh_port"

# Get all facts
ansible web01 -i inventories/projects/my-project -m setup
```

---

## Client Onboarding

**Step-by-step instructions for onboarding new clients with automated infrastructure setup**

### Quick Start for Client Onboarding

For an experienced operator, basic client onboarding takes ~15 minutes:

```bash
# 1. Create client configuration
mkdir -p inventories/projects/acme_corp
cp inventories/projects/_templates/client_template.yml \
  inventories/projects/acme_corp/group_vars/all.yml

# 2. Configure Auth0 credentials
ansible-vault create inventories/projects/acme_corp/auth0_vault.yml

# 3. Create inventory
cat > inventories/projects/acme_corp/hosts.yml << 'EOF'
all:
  children:
    app_servers:
      hosts:
        server1:
          ansible_host: IP_ADDRESS
          ansible_user: ubuntu
EOF

# 4. Run onboarding
ansible-playbook playbooks/client_onboarding.yml \
  -i inventories/projects/acme_corp/hosts.yml \
  --ask-vault-pass

# 5. Verify and deploy applications
```

### Pre-Onboarding Checklist

#### Information Gathering

- [ ] **Client Name**: Short name for identification (e.g., `acme-corp`)
- [ ] **Domain**: Primary domain for client (e.g., `acme.example.com`)
- [ ] **Environment**: Deployment environment (`development`, `staging`, `production`)
- [ ] **Team Size**: Number of users needing access
- [ ] **Application Type**: Framework(s) used (Node.js, Python, Go, Java, etc.)
- [ ] **Deployment Servers**: IP addresses or hostnames of target servers
- [ ] **SSH Credentials**: SSH key or password for server access

#### Auth0 Account Setup

- [ ] Create Auth0 account (free tier)
- [ ] Verify email address
- [ ] Create Machine-to-Machine application
- [ ] Grant Auth0 Management API access to M2M app
- [ ] Copy M2M credentials (Domain, Client ID, Client Secret)

#### Infrastructure Preparation

- [ ] Target servers deployed and accessible via SSH
- [ ] Ubuntu/Debian OS installed (other distributions also supported)
- [ ] SSH key-based authentication configured
- [ ] Basic firewall rules allowing SSH (port 22)
- [ ] At least 2GB RAM, 10GB disk space per server

#### Optional: Social Login Setup

- [ ] Google OAuth credentials (for social login)
- [ ] Microsoft/Office365 credentials (optional)
- [ ] GitHub OAuth credentials (optional)

### Step-by-Step Client Onboarding

#### Step 1: Create Client Directory Structure

```bash
# Create project directory
mkdir -p inventories/projects/acme_corp/{group_vars,host_vars}

# Navigate to project
cd inventories/projects/acme_corp
```

#### Step 2: Configure Client Settings

Copy the template and customize:

```bash
cp ../../_templates/client_template.yml group_vars/all.yml
```

Edit the configuration:

```bash
vim group_vars/all.yml
```

**Key customizations**:
```yaml
client_name: "acme-corp" # Your client name
client_domain: "acme.example.com" # Your domain
client_env: "production" # Your environment

# For Node.js application
app_framework: "nodejs"
app_name: "api-gateway"
app_root_path: "/opt/api-gateway"

# Add more applications as needed
```

#### Step 3: Create Vault File for Secrets

Create encrypted vault for sensitive credentials:

```bash
ansible-vault create auth0_vault.yml
```

You'll be prompted for a vault password. Enter a strong password (24+ characters).

Inside the vault file, add:

```yaml
---
# Auth0 Credentials (from your Auth0 account)
vault_auth0_domain: "your-domain.auth0.com"
vault_auth0_client_id: "YOUR_M2M_CLIENT_ID"
vault_auth0_client_secret: "YOUR_M2M_CLIENT_SECRET"

# Optional: Social Login Providers
vault_google_oauth_client_id: "YOUR_GOOGLE_ID"
vault_google_oauth_secret: "YOUR_GOOGLE_SECRET"

# Initial admin user password (will be sent to admin@your-domain)
vault_initial_admin_password: "InitialP@ssw0rd123!"
```

**IMPORTANT**:
- This file should NEVER be committed to git
- Store vault password securely (password manager, not in code)
- Rotate client secrets every 90 days

#### Step 4: Create Server Inventory

Create `hosts.yml` with your target servers:

```bash
cat > hosts.yml << 'EOF'
---
all:
  vars:
    # Default connection settings
    ansible_user: "ubuntu"
    ansible_ssh_private_key_file: "~/.ssh/id_rsa"
    ansible_python_interpreter: "/usr/bin/python3"

  children:
    app_servers:
      hosts:
        acme-prod-01:
          ansible_host: "203.0.113.10"
          app_framework: "nodejs"
          app_name: "api-gateway"

        acme-prod-02:
          ansible_host: "203.0.113.11"
          app_framework: "nodejs"
          app_name: "web-app"

    database_servers:
      hosts:
        acme-db-01:
          ansible_host: "203.0.113.20"
EOF
```

#### Step 5: Verify Connectivity

Before running the full playbook, verify Ansible can reach all servers:

```bash
# Test connectivity to all hosts
ansible all -i hosts.yml -m ping

# Expected output:
# acme-prod-01 | SUCCESS => {
#     "ping": "pong"
# }
```

If any hosts fail, troubleshoot SSH connectivity:

```bash
# Debug SSH connection
ssh -i ~/.ssh/id_rsa ubuntu@203.0.113.10

# Check SSH key permissions
chmod 600 ~/.ssh/id_rsa
chmod 700 ~/.ssh
```

#### Step 6: Run Onboarding Playbook (Dry Run)

First, do a dry run to preview changes without applying them:

```bash
ansible-playbook ../../playbooks/client_onboarding.yml \
  -i hosts.yml \
  --ask-vault-pass \
  --check \
  --diff
```

You'll be prompted to enter the vault password. Review the output for:
- All hosts are reachable
- OS baseline tasks will be applied
- Auth0 configurations will be created
- No unexpected changes

#### Step 7: Run Onboarding Playbook (Apply)

Once verified, apply the actual configuration:

```bash
ansible-playbook ../../playbooks/client_onboarding.yml \
  -i hosts.yml \
  --ask-vault-pass \
  -v
```

Monitor the output for:
- Common role: OS baseline applied
- Auth0 role: Applications and users created
- App Integration: .env files and configs generated

The playbook will take approximately 3-5 minutes per server.

#### Step 8: Retrieve Generated Artifacts

After successful onboarding, retrieve the generated files:

```bash
# From the playbook run, you should see files in playbook directory:
ls -la /path/to/playbooks/*_auth0_credentials.txt
ls -la /path/to/playbooks/*_auth0_configs/

# Copy to secure location
mkdir -p ~/client_credentials/acme_corp
cp /path/to/playbooks/acme_corp_auth0_credentials.txt ~/client_credentials/acme_corp/
cp -r /path/to/playbooks/acme_corp_auth0_configs/ ~/client_credentials/acme_corp/
```

### Client Verification

#### 1. SSH and Login

Verify you can SSH into the provisioned servers:

```bash
ssh -i ~/.ssh/id_rsa ubuntu@203.0.113.10
```

Check the OS baseline was applied:

```bash
# Verify firewall is active
sudo ufw status

# Check security updates
sudo apt list --upgradable

# Verify hostname
hostname

# Check timezone
timedatectl
```

#### 2. Check Auth0 Dashboard

Log in to your Auth0 tenant and verify:

1. **Applications Created**:
   - Navigate to Applications → Applications
   - Should see your client applications listed
   - Verify client IDs match generated credentials

2. **Users Created** (if configured):
   - Navigate to User Management → Users
   - Verify admin user and other users are present

3. **Roles Configured** (if configured):
   - Navigate to User Management → Roles
   - Verify roles and permissions are defined

4. **Social Login** (if configured):
   - Navigate to Connections
   - Verify Google, Microsoft, or other providers enabled

#### 3. Verify Application Configuration

SSH into application server and check:

```bash
# Check .env file exists and has correct permissions
ls -la /opt/acme-corp-app/.env

# Verify .env file content (don't print secrets!)
grep AUTH0 /opt/acme-corp-app/.env | cut -d= -f1
# Should output:
# AUTH0_DOMAIN
# AUTH0_CLIENT_ID
# AUTH0_CLIENT_SECRET
# AUTH0_AUDIENCE

# Check framework-specific configs
ls -la /opt/acme-corp-app/auth0.config.js # Node.js
ls -la /opt/acme-corp-app/auth0_config.py # Python
ls -la /opt/acme-corp-app/config/auth0.go # Go
```

#### 4. Test Auth0 Connectivity

From application server, test Auth0 API:

```bash
# Using curl to test Auth0 API
curl -X POST https://YOUR_DOMAIN/oauth/token \
  -H "Content-Type: application/json" \
  -d "{
    \"client_id\": \"YOUR_CLIENT_ID\",
    \"client_secret\": \"YOUR_CLIENT_SECRET\",
    \"audience\": \"https://YOUR_DOMAIN/api/v2/\",
    \"grant_type\": \"client_credentials\"
  }"

# Should return an access token (no errors)
```

### Common Client Scenarios

#### Scenario 1: Node.js Application

**Customize group_vars/all.yml**:
```yaml
app_framework: "nodejs"
app_name: "api-gateway"
app_root_path: "/opt/api-gateway"
app_env_vars:
  API_PORT: "3000"
  LOG_LEVEL: "info"
```

**After onboarding**, deploy Node.js app:
```bash
cd /opt/api-gateway
npm install
npm start
```

#### Scenario 2: Django Application

**Customize group_vars/all.yml**:
```yaml
app_framework: "django"
app_name: "web-portal"
app_root_path: "/opt/web-portal"
app_env_vars:
  DATABASE_URL: "postgresql://user:pass@db.example.com/web_portal"
  REDIS_URL: "redis://cache.example.com:6379"
```

**After onboarding**, deploy Django:
```bash
cd /opt/web-portal
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### Scenario 3: Multiple Applications on Same Server

Run onboarding multiple times with different `app_*` variables:

```bash
# First application
ansible-playbook playbooks/client_onboarding.yml \
  -i inventories/projects/acme_corp/hosts.yml \
  --ask-vault-pass \
  -e "app_name=api-gateway app_framework=nodejs"

# Second application
ansible-playbook playbooks/client_onboarding.yml \
  -i inventories/projects/acme_corp/hosts.yml \
  --ask-vault-pass \
  -e "app_name=web-app app_framework=nodejs"
```

#### Scenario 4: Staging and Production

Create separate inventory directories:

```bash
inventories/projects/acme_corp/
├── staging/
│   ├── hosts.yml
│   ├── group_vars/all.yml
│   └── auth0_vault.yml
└── prod/
    ├── hosts.yml
    ├── group_vars/all.yml
    └── auth0_vault.yml
```

Deploy to each environment separately:

```bash
# Deploy to staging
ansible-playbook playbooks/client_onboarding.yml \
  -i inventories/projects/acme_corp/staging/hosts.yml \
  --ask-vault-pass

# Deploy to production
ansible-playbook playbooks/client_onboarding.yml \
  -i inventories/projects/acme_corp/prod/hosts.yml \
  --ask-vault-pass
```

### Post-Client-Onboarding

#### 1. Store Credentials Securely

```bash
# Move credentials to secure storage
mkdir -p ~/client_data/acme_corp
cp -r /path/to/acme_corp_auth0_configs ~/client_data/acme_corp/
cp /path/to/acme_corp_auth0_credentials.txt ~/client_data/acme_corp/

# Remove from playbook directory
rm -f /path/to/acme_corp_auth0_*

# Verify backup worked
ls -la ~/client_data/acme_corp/
```

#### 2. Document Client Information

Create a client record:

```markdown
# Client: Acme Corporation

**Onboarded**: 2025-11-16
**Environment**: Production
**Servers**: acme-prod-01 (203.0.113.10), acme-prod-02 (203.0.113.11)

## Auth0 Tenant
- Domain: acme-corp.auth0.com
- Applications: acme-webapp, acme-api
- Users: admin@acme.example.com

## Deployed Applications
1. API Gateway (Node.js) - 203.0.113.10:3000
2. Web Application (Node.js) - 203.0.113.11:3000

## Contacts
- Primary Contact: John Doe (john@acme.example.com)
- Technical Contact: Jane Smith (jane@acme.example.com)
- Support: support@acme.example.com

## Credentials Location
- Server: vault.internal
- Path: /secure/client_data/acme_corp/
```

#### 3. Configure Monitoring

Set up monitoring for the client infrastructure:

```bash
# Deploy monitoring agent
ansible-playbook playbooks/setup_monitoring.yml \
  -i inventories/projects/acme_corp/hosts.yml

# Configure alerts
ansible-playbook playbooks/configure_alerts.yml \
  -i inventories/projects/acme_corp/hosts.yml
```

#### 4. Schedule Review

- **1 Week**: Verify applications are running smoothly
- **1 Month**: Review Auth0 logs for any issues
- **Quarterly**: Rotate client secrets
- **Semi-Annual**: Audit permissions and access

---

## Shared Procedures

### Troubleshooting (Applies to Both)

#### "SSH connection refused"

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

#### "Ansible module not found"

```bash
# Reinstall collections
ansible-galaxy collection install -r requirements.yml

# Verify installation
ansible-galaxy collection list | grep grafana
```

#### "Vault password error"

```bash
# Create vault password file
echo "your-vault-password" > ~/.vault_password
chmod 600 ~/.vault_password

# Use in playbook
ansible-playbook playbooks/provision.yml \
  -i inventories/projects/my-project \
  --vault-password-file ~/.vault_password
```

#### "Playbook hangs or times out"

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

## Access Provisioning

### For Team Members

Team members need access to:

1. **Git Repository**: Read/write access for infrastructure changes
2. **Vault Passwords**: Access to decrypt secrets
3. **SSH Keys**: Ability to SSH into managed servers
4. **Documentation**: This guide and related docs

**Provisioning steps**:
```bash
# 1. Add to git repository with appropriate permissions
# 2. Share vault password securely (password manager)
# 3. Add SSH public key to authorized_keys on servers
# 4. Provide links to documentation
```

### For Clients

Clients need access to:

1. **Auth0 Dashboard**: Manage users and applications
2. **Application URLs**: Access deployed applications
3. **Support Contacts**: Who to reach for help
4. **Documentation**: How to use their applications

**Provisioning steps**:
```bash
# 1. Grant Auth0 dashboard access (admin role)
# 2. Provide application URLs and credentials
# 3. Share support contact information
# 4. Provide user guides and documentation
```

---

## Learning Path

### Day 1: Basics (Team Members)
- [ ] Complete "Quick Onboarding" section
- [ ] Do Exercise 1: Create first project
- [ ] Read README.md
- [ ] Take knowledge check quiz

### Day 2: Deep Dive (Team Members)
- [ ] Complete "Deep Dive" section
- [ ] Do Exercises 2-4
- [ ] Read docs/ARCHITECTURE.md
- [ ] Explore roles/common/

### Day 3: Real Projects (Team Members)
- [ ] Create your first production project
- [ ] Test with check mode
- [ ] Deploy to staging
- [ ] Monitor results

### Day 4+: Mastery (Team Members)
- [ ] Customize roles for your needs
- [ ] Create new roles
- [ ] Help onboard other team members
- [ ] Document your patterns

---

## Resources

- **Ansible Documentation**: https://docs.ansible.com
- **Ansible Best Practices**: https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html
- **Variable Precedence**: https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#variable-precedence-where-should-i-put-a-variable
- **Vault Documentation**: https://docs.ansible.com/ansible/latest/user_guide/vault.html

---

## Welcome!

You're now part of the infrastructure team (or our client family). This framework is designed to make your job easier while keeping things safe and consistent.

**Remember**:
- Test in staging first
- Use check mode to preview changes
- Never commit unencrypted secrets
- Ask questions - that's how we all learn

Happy deploying!

---

**Last Updated**: November 2025
**Version**: 2.0 (Consolidated)
**Time to Complete**: 1 hour (team) / 15-30 minutes (client)
