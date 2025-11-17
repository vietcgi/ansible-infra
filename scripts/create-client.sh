#!/bin/bash
#
# Create new client infrastructure configuration
# Automates project scaffolding with templates
#
# Usage:
#   ./scripts/create-client.sh acme-corp
#   ./scripts/create-client.sh my-project --domain example.com --env staging
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Default values
CLIENT_NAME="${1:?}"
CLIENT_DOMAIN="${CLIENT_NAME}.example.com"
CLIENT_ENV="production"

# Parse additional arguments
while [[ $# -gt 1 ]]; do
    case "$2" in
        --domain)
            CLIENT_DOMAIN="$3"
            shift 2
            ;;
        --env)
            CLIENT_ENV="$3"
            shift 2
            ;;
        *)
            echo "Unknown option: $2"
            exit 1
            ;;
    esac
done

# Validate client name
if ! [[ "$CLIENT_NAME" =~ ^[a-z0-9_-]+$ ]]; then
    echo -e "${RED}ERROR: Invalid client name.${NC}"
    echo "Use lowercase letters, numbers, hyphens, and underscores only."
    exit 1
fi

# Client directory
CLIENT_DIR="${REPO_ROOT}/inventories/projects/${CLIENT_NAME}"

# Check if client already exists
if [ -d "$CLIENT_DIR" ]; then
    echo -e "${RED}ERROR: Client directory already exists: $CLIENT_DIR${NC}"
    exit 1
fi

# Create directories
echo -e "${BLUE}Creating client directory structure...${NC}"
mkdir -p "${CLIENT_DIR}/group_vars" "${CLIENT_DIR}/host_vars"
echo -e "${GREEN}✓ Created: $CLIENT_DIR${NC}"

# Copy client template
echo -e "${BLUE}Copying configuration template...${NC}"
cp "${REPO_ROOT}/inventories/projects/_templates/client_template.yml" \
   "${CLIENT_DIR}/group_vars/all.yml"
echo -e "${GREEN}✓ Created: ${CLIENT_DIR}/group_vars/all.yml${NC}"

# Update placeholders in configuration
sed -i.bak "s/acme-corp/${CLIENT_NAME}/g" "${CLIENT_DIR}/group_vars/all.yml"
sed -i.bak "s/acme.example.com/${CLIENT_DOMAIN}/g" "${CLIENT_DIR}/group_vars/all.yml"
sed -i.bak "s/production/${CLIENT_ENV}/g" "${CLIENT_DIR}/group_vars/all.yml"
rm -f "${CLIENT_DIR}/group_vars/all.yml.bak"
echo -e "${GREEN}✓ Updated placeholders in configuration${NC}"

# Create hosts.yml template
echo -e "${BLUE}Creating inventory file...${NC}"
cat > "${CLIENT_DIR}/hosts.yml" << 'HOSTS_EOF'
---
# Inventory for client infrastructure
#
# Edit this file with your server information:
# - Replace IP_ADDRESS with actual server IPs
# - Add additional servers as needed
# - Set ansible_user to your SSH user (ubuntu, ec2-user, etc.)
#
# Variables:
#   ansible_host: IP address or hostname of server
#   ansible_user: SSH username for remote access
#   ansible_port: SSH port (default: 22)
#   app_framework: Application framework (nodejs, python, django, go, java)
#   app_name: Application name for deployment
#
# Run with:
#   ansible-playbook playbooks/client_onboarding.yml \
#     -i inventories/projects/CLIENT_NAME/hosts.yml \
#     --ask-vault-pass

all:
  vars:
    # Default connection settings (can be overridden per-host)
    ansible_user: "ubuntu"                          # Change to your SSH user
    ansible_ssh_private_key_file: "~/.ssh/id_rsa"  # Path to SSH private key
    ansible_python_interpreter: "/usr/bin/python3"
    ansible_ssh_common_args: ""                     # Add -o ProxyCommand=... if needed

  children:
    app_servers:
      hosts:
        # Example server 1
        server1:
          ansible_host: "203.0.113.10"              # Replace with actual IP
          app_framework: "nodejs"
          app_name: "api-gateway"

        # Example server 2 (uncomment and configure)
        # server2:
        #   ansible_host: "203.0.113.11"
        #   app_framework: "nodejs"
        #   app_name: "web-app"

    database_servers:
      hosts:
        # Example database server (uncomment if needed)
        # db1:
        #   ansible_host: "203.0.113.20"

# Host variables can also be defined in host_vars/ directory:
# - host_vars/server1.yml
# - host_vars/server2.yml
# See examples in host_vars/ directory

HOSTS_EOF
echo -e "${GREEN}✓ Created: ${CLIENT_DIR}/hosts.yml${NC}"

# Create example host_vars
echo -e "${BLUE}Creating example host variables...${NC}"
cat > "${CLIENT_DIR}/host_vars/server1.yml.example" << 'HOSTVAR_EOF'
---
# Host-specific variables for server1
# This is an example - uncomment and customize as needed

# Connection settings (per-host overrides)
# ansible_host: "203.0.113.10"
# ansible_user: "ubuntu"
# ansible_port: 22

# Application configuration
# app_framework: "nodejs"
# app_name: "api-gateway"
# app_root_path: "/opt/api-gateway"

# Environment variables (application-specific)
# app_env_vars:
#   API_PORT: "3000"
#   LOG_LEVEL: "info"
#   DATABASE_URL: "postgresql://user:pass@db.example.com/database"
#   REDIS_URL: "redis://cache.example.com:6379"

HOSTVAR_EOF
echo -e "${GREEN}✓ Created: ${CLIENT_DIR}/host_vars/server1.yml.example${NC}"

# Create vault template
echo -e "${BLUE}Creating vault template...${NC}"
cat > "${CLIENT_DIR}/auth0_vault.yml" << 'VAULT_EOF'
---
# Auth0 Credentials - ENCRYPTED VAULT FILE
#
# IMPORTANT: This file contains sensitive credentials
# - NEVER commit to git (already in .gitignore)
# - NEVER share vault password via email
# - Store vault password in secure password manager
# - Rotate credentials every 90 days
#
# Edit this file with: ansible-vault edit auth0_vault.yml
# The vault password prompt will appear when needed
#
# Get these values from:
# 1. Auth0 Dashboard → Settings → Domain
#    → vault_auth0_domain: "your-domain.auth0.com"
#
# 2. Auth0 Dashboard → Applications → Machine-to-Machine Apps
#    → vault_auth0_client_id: "YOUR_M2M_CLIENT_ID"
#    → vault_auth0_client_secret: "YOUR_M2M_CLIENT_SECRET"
#
# 3. (Optional) Google Console → OAuth credentials
#    → vault_google_oauth_client_id: "YOUR_GOOGLE_CLIENT_ID"
#    → vault_google_oauth_secret: "YOUR_GOOGLE_SECRET"
#
# 4. Initial admin user password for Auth0
#    → vault_initial_admin_password: "strong_password"
#

# Replace these with your actual credentials
vault_auth0_domain: "your-domain.auth0.com"
vault_auth0_client_id: "your_m2m_client_id_here"
vault_auth0_client_secret: "your_m2m_client_secret_here"

# Optional: Social login providers
vault_google_oauth_client_id: ""
vault_google_oauth_secret: ""

# Initial admin user password
vault_initial_admin_password: "ChangeMe123!"

VAULT_EOF
echo -e "${GREEN}✓ Created: ${CLIENT_DIR}/auth0_vault.yml${NC}"

# Create .gitignore for this client
echo -e "${BLUE}Creating .gitignore...${NC}"
cat > "${CLIENT_DIR}/.gitignore" << 'GITIGNORE_EOF'
# Client-specific secrets - NEVER commit to git
auth0_vault.yml
*_vault.yml
*.key
*.pem
.env*
secrets/

# Local files
*.swp
*.swo
*~
.DS_Store

GITIGNORE_EOF
echo -e "${GREEN}✓ Created: ${CLIENT_DIR}/.gitignore${NC}"

# Create README for this client
echo -e "${BLUE}Creating client README...${NC}"
cat > "${CLIENT_DIR}/README.md" << 'README_EOF'
# Client Infrastructure Configuration

This directory contains all infrastructure configuration for this client.

## Files

- **hosts.yml** - Server inventory (edit with your servers)
- **group_vars/all.yml** - Client configuration (customize as needed)
- **host_vars/** - Per-server configuration (optional)
- **auth0_vault.yml** - Auth0 credentials (keep secure!)

## Quick Start

### Step 1: Configure Servers
Edit `hosts.yml` and add your server IP addresses:

```yaml
app_servers:
  hosts:
    server1:
      ansible_host: "YOUR_SERVER_IP"
      ansible_user: "ubuntu"
```

### Step 2: Create Vault
Create and encrypt the Auth0 credentials vault:

```bash
ansible-vault create auth0_vault.yml
# Enter a strong vault password (24+ characters)
# Then add your Auth0 credentials:
# vault_auth0_domain: "your-domain.auth0.com"
# vault_auth0_client_id: "your_client_id"
# vault_auth0_client_secret: "your_secret"
```

### Step 3: Configure Client
Edit `group_vars/all.yml` and customize:
- Client domain
- Applications (Node.js, Python, etc.)
- Environment variables
- Social login providers (optional)

### Step 4: Verify Connectivity
Test SSH access to all servers:

```bash
ansible all -i hosts.yml -m ping --ask-vault-pass
```

### Step 5: Deploy
Run the client onboarding playbook:

```bash
ansible-playbook ../../playbooks/client_onboarding.yml \
  -i hosts.yml \
  --ask-vault-pass \
  -v
```

## Documentation

- [Client Onboarding Guide](../../docs/CLIENT_ONBOARDING.md)
- [Auth0 Integration Guide](../../docs/AUTH0_INTEGRATION.md)
- [Vault Management](../../docs/VAULT_MANAGEMENT.md)
- [Security Audit](../../docs/SECURITY_AUDIT.md)

## Next Steps

1. Fill in server IPs in `hosts.yml`
2. Create encrypted vault with Auth0 credentials
3. Customize configuration in `group_vars/all.yml`
4. Test connectivity with ping
5. Deploy with playbook
6. Verify in Auth0 dashboard
7. Deploy applications

## Security

- **NEVER commit vault files to git** ✅ .gitignore configured
- **NEVER share vault password via email**
- **Store vault password in password manager**
- **Rotate Auth0 secrets every 90 days**

---

Created: NOW_TIMESTAMP

README_EOF

# Replace NOW_TIMESTAMP with actual date
sed -i.bak "s/NOW_TIMESTAMP/$(date +'%Y-%m-%d %H:%M:%S')/g" "${CLIENT_DIR}/README.md"
rm -f "${CLIENT_DIR}/README.md.bak"
echo -e "${GREEN}✓ Created: ${CLIENT_DIR}/README.md${NC}"

# Print summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Client Created Successfully${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Client Directory:${NC} ${CLIENT_DIR}/"
echo ""
echo "📁 Files Created:"
echo "  ✓ group_vars/all.yml      - Client configuration"
echo "  ✓ hosts.yml              - Server inventory"
echo "  ✓ host_vars/server1.yml.example - Per-host config example"
echo "  ✓ auth0_vault.yml        - Auth0 credentials (encrypted)"
echo "  ✓ .gitignore             - Git exclusions"
echo "  ✓ README.md              - Client documentation"
echo ""
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo ""
echo "1️⃣  Edit configuration:"
echo "   ${BLUE}vim ${CLIENT_DIR}/group_vars/all.yml${NC}"
echo ""
echo "2️⃣  Add your servers to inventory:"
echo "   ${BLUE}vim ${CLIENT_DIR}/hosts.yml${NC}"
echo ""
echo "3️⃣  Create encrypted vault for Auth0 credentials:"
echo "   ${BLUE}ansible-vault create ${CLIENT_DIR}/auth0_vault.yml${NC}"
echo ""
echo "   When prompted, enter your Auth0 credentials:"
echo "   - vault_auth0_domain: your-domain.auth0.com"
echo "   - vault_auth0_client_id: YOUR_CLIENT_ID"
echo "   - vault_auth0_client_secret: YOUR_CLIENT_SECRET"
echo ""
echo "4️⃣  Test SSH connectivity:"
echo "   ${BLUE}ansible all -i ${CLIENT_DIR}/hosts.yml -m ping --ask-vault-pass${NC}"
echo ""
echo "5️⃣  Deploy infrastructure:"
echo "   ${BLUE}ansible-playbook playbooks/client_onboarding.yml \${NC}"
echo "   ${BLUE}  -i ${CLIENT_DIR}/hosts.yml \${NC}"
echo "   ${BLUE}  --ask-vault-pass${NC}"
echo ""
echo -e "${YELLOW}SECURITY REMINDERS:${NC}"
echo "  ⚠️  Vault files are in .gitignore - they won't be committed"
echo "  ⚠️  Store vault password in password manager (not email!)"
echo "  ⚠️  Rotate Auth0 secrets every 90 days"
echo "  ⚠️  Keep .env files private on deployed servers"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "  📖 See ${CLIENT_DIR}/README.md for more details"
echo "  📖 See docs/CLIENT_ONBOARDING.md for complete guide"
echo ""

exit 0
