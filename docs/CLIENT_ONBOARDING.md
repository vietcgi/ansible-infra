# Client Onboarding Guide

Step-by-step instructions for onboarding new clients with automated infrastructure setup.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Pre-Onboarding Checklist](#pre-onboarding-checklist)
3. [Step-by-Step Onboarding](#step-by-step-onboarding)
4. [Verification](#verification)
5. [Common Scenarios](#common-scenarios)
6. [Post-Onboarding](#post-onboarding)

## Quick Start

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

## Pre-Onboarding Checklist

### Information Gathering

- [ ] **Client Name**: Short name for identification (e.g., `acme-corp`)
- [ ] **Domain**: Primary domain for client (e.g., `acme.example.com`)
- [ ] **Environment**: Deployment environment (`development`, `staging`, `production`)
- [ ] **Team Size**: Number of users needing access
- [ ] **Application Type**: Framework(s) used (Node.js, Python, Go, Java, etc.)
- [ ] **Deployment Servers**: IP addresses or hostnames of target servers
- [ ] **SSH Credentials**: SSH key or password for server access

### Auth0 Account Setup

- [ ] Create Auth0 account (free tier)
- [ ] Verify email address
- [ ] Create Machine-to-Machine application
- [ ] Grant Auth0 Management API access to M2M app
- [ ] Copy M2M credentials (Domain, Client ID, Client Secret)

### Infrastructure Preparation

- [ ] Target servers deployed and accessible via SSH
- [ ] Ubuntu/Debian OS installed (other distributions also supported)
- [ ] SSH key-based authentication configured
- [ ] Basic firewall rules allowing SSH (port 22)
- [ ] At least 2GB RAM, 10GB disk space per server

### Optional: Social Login Setup

- [ ] Google OAuth credentials (for social login)
- [ ] Microsoft/Office365 credentials (optional)
- [ ] GitHub OAuth credentials (optional)

## Step-by-Step Onboarding

### Step 1: Create Client Directory Structure

```bash
# Create project directory
mkdir -p inventories/projects/acme_corp/{group_vars,host_vars}

# Navigate to project
cd inventories/projects/acme_corp
```

### Step 2: Configure Client Settings

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

### Step 3: Create Vault File for Secrets

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

⚠️ **IMPORTANT**:
- This file should NEVER be committed to git
- Store vault password securely (password manager, not in code)
- Rotate client secrets every 90 days

### Step 4: Create Server Inventory

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

### Step 5: Verify Connectivity

Before running the full playbook, verify Ansible can reach all servers:

```bash
# Test connectivity to all hosts
ansible all -i hosts.yml -m ping

# Expected output:
# acme-prod-01 | SUCCESS => {
# "ping": "pong"
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

### Step 6: Run Onboarding Playbook (Dry Run)

First, do a dry run to preview changes without applying them:

```bash
ansible-playbook ../../playbooks/client_onboarding.yml \
 -i hosts.yml \
 --ask-vault-pass \
 --check \
 --diff
```

You'll be prompted to enter the vault password. Review the output for:
- ✓ All hosts are reachable
- ✓ OS baseline tasks will be applied
- ✓ Auth0 configurations will be created
- ✓ No unexpected changes

### Step 7: Run Onboarding Playbook (Apply)

Once verified, apply the actual configuration:

```bash
ansible-playbook ../../playbooks/client_onboarding.yml \
 -i hosts.yml \
 --ask-vault-pass \
 -v
```

Monitor the output for:
- ✓ Common role: OS baseline applied
- ✓ Auth0 role: Applications and users created
- ✓ App Integration: .env files and configs generated

The playbook will take approximately 3-5 minutes per server.

### Step 8: Retrieve Generated Artifacts

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

## Verification

### 1. SSH and Login

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

### 2. Check Auth0 Dashboard

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

### 3. Verify Application Configuration

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

### 4. Test Auth0 Connectivity

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

## Common Scenarios

### Scenario 1: Node.js Application

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

### Scenario 2: Django Application

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

### Scenario 3: Multiple Applications on Same Server

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

### Scenario 4: Staging and Production

Create separate inventory directories:

```bash
inventories/projects/acme_corp/
├── staging/
│ ├── hosts.yml
│ ├── group_vars/all.yml
│ └── auth0_vault.yml
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

## Post-Onboarding

### 1. Store Credentials Securely

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

### 2. Document Client Information

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

### 3. Deploy Applications

Follow the guides in [docs/AUTH0_INTEGRATION.md](AUTH0_INTEGRATION.md) for framework-specific deployment instructions.

### 4. Configure Monitoring

Set up monitoring for the client infrastructure:

```bash
# Deploy monitoring agent
ansible-playbook playbooks/setup_monitoring.yml \
 -i inventories/projects/acme_corp/hosts.yml

# Configure alerts
ansible-playbook playbooks/configure_alerts.yml \
 -i inventories/projects/acme_corp/hosts.yml
```

### 5. Establish Support Process

1. **Client Communication**: Email confirmation of successful onboarding
2. **Access Instructions**: How to manage Auth0 users and applications
3. **Support Contacts**: Who to reach for issues
4. **Documentation**: Links to relevant guides

### 6. Schedule Review

- **1 Week**: Verify applications are running smoothly
- **1 Month**: Review Auth0 logs for any issues
- **Quarterly**: Rotate client secrets
- **Semi-Annual**: Audit permissions and access

## Cleanup/Offboarding

To remove client infrastructure:

```bash
# Dry run to preview removal
ansible-playbook playbooks/client_onboarding.yml \
 -i inventories/projects/acme_corp/hosts.yml \
 --ask-vault-pass \
 -e "onboarding_state=absent" \
 --check \
 --diff

# Apply removal
ansible-playbook playbooks/client_onboarding.yml \
 -i inventories/projects/acme_corp/hosts.yml \
 --ask-vault-pass \
 -e "onboarding_state=absent"
```

This will:
- Delete Auth0 applications
- Remove users and roles
- Remove application configurations
- Keep OS baseline (can be removed manually if needed)

---

**Last Updated**: November 2025
**Version**: 1.0
**Estimated Onboarding Time**: 15-30 minutes
