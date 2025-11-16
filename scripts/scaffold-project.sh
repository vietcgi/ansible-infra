#!/bin/bash
#
# scaffold-project.sh - Create a new project from template
#
# Usage: ./scripts/scaffold-project.sh <project-name>
# Example: ./scripts/scaffold-project.sh my-infrastructure
#
# This script:
# 1. Creates project directory structure
# 2. Copies templates from _templates/
# 3. Initializes Vault encrypted secrets file
# 4. Provides next-step instructions
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECTS_DIR="${SCRIPT_DIR}/inventories/projects"
TEMPLATES_DIR="${PROJECTS_DIR}/_templates"

# Functions
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

show_usage() {
    cat << EOF
${BLUE}Ansible Infrastructure - Project Scaffolding${NC}

${YELLOW}Usage:${NC}
  ./scripts/scaffold-project.sh <project-name> [options]

${YELLOW}Arguments:${NC}
  <project-name>     Name of your project (e.g., my-infrastructure, customer-prod)

${YELLOW}Options:${NC}
  --help             Show this help message
  --force            Overwrite existing project
  --no-vault         Skip Vault initialization
  --quick            Skip verbose output

${YELLOW}Examples:${NC}
  ./scripts/scaffold-project.sh my-infrastructure
  ./scripts/scaffold-project.sh customer-prod --no-vault
  ./scripts/scaffold-project.sh staging --force

${YELLOW}Result:${NC}
  Creates: inventories/projects/<project-name>/
  - inventory.yml (server definitions)
  - group_vars/all.yml (project defaults)
  - group_vars/all_vault.yml (encrypted secrets)
  - host_vars/ (host-specific overrides)

${YELLOW}Next Steps:${NC}
  1. Edit inventories/projects/<project-name>/inventory.yml
  2. Edit inventories/projects/<project-name>/group_vars/all.yml
  3. Set secrets: ansible-vault edit inventories/projects/<project-name>/group_vars/all_vault.yml
  4. Test: ansible all -i inventories/projects/<project-name> -m ping
  5. Deploy: ansible-playbook playbooks/provision.yml -i inventories/projects/<project-name>

EOF
}

# Parse arguments
PROJECT_NAME="${1:-}"
FORCE=false
NO_VAULT=false
QUIET=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            show_usage
            exit 0
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --no-vault)
            NO_VAULT=true
            shift
            ;;
        --quick)
            QUIET=true
            shift
            ;;
        *)
            PROJECT_NAME="$1"
            shift
            ;;
    esac
done

# Validation
if [[ -z "$PROJECT_NAME" ]]; then
    print_error "Project name required"
    echo ""
    show_usage
    exit 1
fi

# Validate project name format
if ! [[ "$PROJECT_NAME" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    print_error "Invalid project name: '$PROJECT_NAME'"
    print_info "Project names must contain only letters, numbers, hyphens, and underscores"
    exit 1
fi

PROJECT_PATH="${PROJECTS_DIR}/${PROJECT_NAME}"

# Check if project already exists
if [[ -d "$PROJECT_PATH" ]]; then
    if [[ "$FORCE" == false ]]; then
        print_error "Project '$PROJECT_NAME' already exists at: $PROJECT_PATH"
        print_info "Use --force to overwrite"
        exit 1
    else
        print_warning "Overwriting existing project: $PROJECT_NAME"
        rm -rf "$PROJECT_PATH"
    fi
fi

# Check templates exist
if [[ ! -d "$TEMPLATES_DIR" ]]; then
    print_error "Templates directory not found: $TEMPLATES_DIR"
    print_info "Make sure you're running from the ansible-infra root directory"
    exit 1
fi

# Create project structure
[[ "$QUIET" == false ]] && print_header "Creating Project: $PROJECT_NAME"

mkdir -p "${PROJECT_PATH}/group_vars"
mkdir -p "${PROJECT_PATH}/host_vars"
print_success "Created project directories"

# Copy inventory template
if [[ -f "${TEMPLATES_DIR}/inventory.yml.jinja2" ]]; then
    cp "${TEMPLATES_DIR}/inventory.yml.jinja2" "${PROJECT_PATH}/inventory.yml"
    print_success "Created inventory.yml"
else
    # Fallback: create basic inventory
    cat > "${PROJECT_PATH}/inventory.yml" << 'EOF'
all:
  children:
    webservers:
      hosts:
        web01:
          ansible_host: 10.0.1.10
    databases:
      hosts:
        db01:
          ansible_host: 10.0.2.10
  vars:
    ansible_user: ubuntu
    ansible_port: 22
    ansible_python_interpreter: /usr/bin/python3
EOF
    print_success "Created inventory.yml (basic)"
fi

# Copy group variables
for template_file in "${TEMPLATES_DIR}"/group_vars/*.yml; do
    if [[ -f "$template_file" ]]; then
        filename=$(basename "$template_file")
        cp "$template_file" "${PROJECT_PATH}/group_vars/${filename%%.jinja2}"
    fi
done 2>/dev/null

# Special handling for all.yml
if [[ ! -f "${PROJECT_PATH}/group_vars/all.yml" ]]; then
    cat > "${PROJECT_PATH}/group_vars/all.yml" << EOF
---
# Project Identification
project_name: ${PROJECT_NAME}
project_env: production
project_owner: your-team
project_description: "${PROJECT_NAME} Infrastructure"

# Common Configuration
common_hostname_prefix: ${PROJECT_NAME%%[-_]*}
common_ntp_servers:
  - 0.pool.ntp.org
  - 1.pool.ntp.org
common_ssh_port: 22

# Monitoring Configuration
monitoring_enabled: true
monitoring_grafana_enabled: true
monitoring_prometheus_enabled: true
monitoring_loki_enabled: false

# Security Configuration
security_hardening_level: production
ssh_hardening_enabled: true
firewall_enabled: true
EOF
    print_success "Created group_vars/all.yml"
fi

# Create Vault secrets file
if [[ "$NO_VAULT" == false ]]; then
    VAULT_FILE="${PROJECT_PATH}/group_vars/all_vault.yml"

    if [[ ! -f "$VAULT_FILE" ]]; then
        # Create unencrypted template first
        cat > "${VAULT_FILE}.tmp" << EOF
---
# Encrypted Secrets for ${PROJECT_NAME}
# Edit with: ansible-vault edit ${VAULT_FILE}

vault_grafana_admin_password: "change-me-to-secure-password"
vault_prometheus_scrape_token: "change-me-to-token"
vault_database_root_password: "change-me-to-password"
vault_ssh_key_private: |
  -----BEGIN OPENSSH PRIVATE KEY-----
  Add your SSH private key here
  -----END OPENSSH PRIVATE KEY-----
EOF

        # Try to encrypt with ansible-vault
        if command -v ansible-vault &> /dev/null; then
            if ansible-vault encrypt "${VAULT_FILE}.tmp" --vault-password-file /dev/stdin <<< "" 2>/dev/null || \
               ansible-vault encrypt "${VAULT_FILE}.tmp" 2>/dev/null; then
                mv "${VAULT_FILE}.tmp" "${VAULT_FILE}"
                print_success "Created group_vars/all_vault.yml (encrypted)"
            else
                # If encryption fails, keep as template
                rm -f "${VAULT_FILE}.tmp"
                cat > "${VAULT_FILE}" << EOF
---
# TODO: Encrypt this file with: ansible-vault encrypt ${VAULT_FILE}
vault_grafana_admin_password: "change-me"
vault_prometheus_scrape_token: "change-me"
vault_database_root_password: "change-me"
EOF
                print_warning "Vault file created (not encrypted yet - see notes below)"
            fi
        else
            rm -f "${VAULT_FILE}.tmp"
            print_warning "ansible-vault not found - creating plaintext template"
            print_info "Encrypt with: ansible-vault encrypt ${VAULT_FILE}"
        fi
    fi
fi

# Create .gitkeep for host_vars
touch "${PROJECT_PATH}/host_vars/.gitkeep"
print_success "Created host_vars/ directory"

# Create README for project
cat > "${PROJECT_PATH}/README.md" << EOF
# Project: ${PROJECT_NAME}

Infrastructure as Code for ${PROJECT_NAME} using Ansible.

## Quick Start

1. **Define your servers**
   \`\`\`bash
   edit inventory.yml
   \`\`\`

2. **Configure defaults**
   \`\`\`bash
   edit group_vars/all.yml
   \`\`\`

3. **Set secrets**
   \`\`\`bash
   ansible-vault edit group_vars/all_vault.yml
   \`\`\`

4. **Test connectivity**
   \`\`\`bash
   ansible all -i . -m ping
   \`\`\`

5. **Deploy**
   \`\`\`bash
   ansible-playbook ../../../playbooks/provision.yml -i .
   \`\`\`

## Files

- **inventory.yml** - Server definitions
- **group_vars/all.yml** - Project-wide configuration
- **group_vars/<group>.yml** - Group-specific configuration
- **group_vars/all_vault.yml** - Encrypted secrets
- **host_vars/** - Host-specific configuration

## Documentation

- See [\`../../README.md\`](../../README.md) for framework overview
- See [\`../../../docs/NEW_PROJECT_QUICKSTART.md\`](../../../docs/NEW_PROJECT_QUICKSTART.md) for detailed guide
- See [\`../../../docs/ARCHITECTURE.md\`](../../../docs/ARCHITECTURE.md) for technical details

## Variables

All available variables are documented in the role defaults:

- \`../../common/defaults/main.yml\`
- \`../../system_hardening_macos/defaults/main.yml\`

Override any variable in:
- \`group_vars/all.yml\` (project-wide)
- \`group_vars/<group>.yml\` (group-specific)
- \`host_vars/<host>.yml\` (host-specific)

## Support

- Questions? See the main [README](../../README.md)
- Issues? Check [TROUBLESHOOTING.md](../../../docs/TROUBLESHOOTING.md)
EOF
print_success "Created README.md"

# Summary
[[ "$QUIET" == false ]] && print_header "Project Created Successfully!"

cat << EOF
${GREEN}✓${NC} Project: ${GREEN}${PROJECT_NAME}${NC}
${GREEN}✓${NC} Location: ${GREEN}${PROJECT_PATH}${NC}

${BLUE}Files Created:${NC}
  - inventory.yml                    (Server definitions)
  - group_vars/all.yml              (Project defaults)
  - group_vars/all_vault.yml        (Encrypted secrets)
  - host_vars/                      (Host-specific config)
  - README.md                       (Project documentation)

${BLUE}Next Steps:${NC}

1. ${YELLOW}Define your servers${NC}
   \$ edit ${PROJECT_PATH}/inventory.yml

2. ${YELLOW}Configure project defaults${NC}
   \$ edit ${PROJECT_PATH}/group_vars/all.yml

3. ${YELLOW}Set encrypted secrets${NC}
   \$ ansible-vault edit ${PROJECT_PATH}/group_vars/all_vault.yml

4. ${YELLOW}Test connectivity${NC}
   \$ ansible all -i ${PROJECT_PATH} -m ping

5. ${YELLOW}Deploy to your servers${NC}
   \$ ansible-playbook playbooks/provision.yml -i ${PROJECT_PATH}

${BLUE}Tips:${NC}
  - See: docs/NEW_PROJECT_QUICKSTART.md (15-minute guide)
  - See: docs/ARCHITECTURE.md (technical deep-dive)
  - See: docs/PROJECT_REUSABILITY_GUIDE.md (advanced patterns)

${BLUE}Vault Password:${NC}
  Store your Vault password in: ~/.vault_password
  Then use: --vault-password-file ~/.vault_password

EOF
