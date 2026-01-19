#!/bin/bash
#
# bootstrap.sh - Deploy Vast.ai GPU Host with One Command
#
# Usage:
#   ./bootstrap.sh <target-ip> [username]
#   ./bootstrap.sh 192.168.1.100
#   ./bootstrap.sh 192.168.1.100 ubuntu
#
# Requirements:
#   - SSH key-based access to target
#   - Target: Ubuntu 22.04 with NVIDIA GPUs
#

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANSIBLE_DIR="${SCRIPT_DIR}"
PLAYBOOK="playbooks/deploy-vastai-host.yml"
TEMP_INVENTORY="/tmp/vastai-bootstrap-inventory-$$.yml"
LOG_FILE="/tmp/vastai-bootstrap-$(date +%Y%m%d-%H%M%S).log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ============================================================================
# FUNCTIONS
# ============================================================================
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_step() {
    echo -e "${CYAN}> $1${NC}"
}

print_success() {
    echo -e "${GREEN}[OK] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[WARN] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

show_usage() {
    cat << EOF
${BLUE}Vast.ai GPU Host Bootstrap${NC}

${YELLOW}Usage:${NC}
  ./bootstrap.sh <target-ip> [username]

${YELLOW}Arguments:${NC}
  <target-ip>    IP address of the target server
  [username]     SSH username (default: current user or 'ubuntu')

${YELLOW}Examples:${NC}
  ./bootstrap.sh 192.168.1.100              # Uses default username
  ./bootstrap.sh 192.168.1.100 ubuntu       # Explicit username
  ./bootstrap.sh 10.0.0.50 admin            # Custom admin user

${YELLOW}Prerequisites:${NC}
  - SSH key-based access to target server
  - Target running Ubuntu 22.04 LTS
  - NVIDIA GPUs installed (RTX 4090 recommended)
  - Vast.ai API key (will be prompted)

${YELLOW}What This Does:${NC}
  1. Installs Ansible locally (if needed)
  2. Installs Ansible collections
  3. Deploys NVIDIA drivers + container toolkit
  4. Installs and configures Vast.ai daemon
  5. Configures GPU marketplace listing
  6. Sets up security hardening
  7. Enables GPU monitoring

${YELLOW}Environment Variables:${NC}
  VASTAI_API_KEY    - Vast.ai API key (or will be prompted)
  SSH_KEY_PATH      - Path to SSH private key (default: ~/.ssh/id_rsa)
  ANSIBLE_VERBOSITY - Ansible verbosity level (0-4, default: 1)

EOF
}

check_dependencies() {
    print_step "Checking local dependencies..."

    local missing=()

    if ! command -v python3 &> /dev/null; then
        missing+=("python3")
    fi

    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        missing+=("pip")
    fi

    if ! command -v ssh &> /dev/null; then
        missing+=("ssh")
    fi

    if [[ ${#missing[@]} -gt 0 ]]; then
        print_error "Missing dependencies: ${missing[*]}"
        echo "Please install them first:"
        echo "  Ubuntu/Debian: sudo apt install python3 python3-pip openssh-client"
        echo "  macOS: brew install python3"
        exit 1
    fi

    print_success "All dependencies present"
}

install_ansible() {
    print_step "Checking Ansible installation..."

    if command -v ansible-playbook &> /dev/null; then
        local version
        version=$(ansible --version | head -1)
        print_success "Ansible already installed: $version"
        return 0
    fi

    print_step "Installing Ansible..."

    if command -v pipx &> /dev/null; then
        pipx install ansible-core
        pipx inject ansible-core jmespath
    else
        pip3 install --user ansible-core jmespath

        local user_bin="${HOME}/.local/bin"
        if [[ ":$PATH:" != *":$user_bin:"* ]]; then
            export PATH="$user_bin:$PATH"
            print_warning "Added $user_bin to PATH for this session"
        fi
    fi

    if command -v ansible-playbook &> /dev/null; then
        print_success "Ansible installed successfully"
    else
        print_error "Ansible installation failed"
        exit 1
    fi
}

install_collections() {
    print_step "Installing Ansible collections..."

    cd "${ANSIBLE_DIR}"

    if [[ -f "requirements.yml" ]]; then
        ansible-galaxy collection install -r requirements.yml --force 2>&1 | tee -a "$LOG_FILE"
        print_success "Collections installed"
    else
        print_warning "No requirements.yml found, installing core collections..."
        ansible-galaxy collection install community.docker community.general ansible.posix --force
    fi
}

test_ssh_connectivity() {
    local target="$1"
    local user="$2"
    local key="${SSH_KEY_PATH:-$HOME/.ssh/id_rsa}"

    print_step "Testing SSH connectivity to ${user}@${target}..."

    if [[ ! -f "$key" ]]; then
        key="$HOME/.ssh/id_ed25519"
    fi

    if ssh -o BatchMode=yes -o ConnectTimeout=10 -i "$key" "${user}@${target}" "echo 'SSH OK'" &> /dev/null; then
        print_success "SSH connection successful"
        export SSH_KEY_PATH="$key"
        return 0
    else
        print_error "Cannot connect via SSH to ${user}@${target}"
        echo ""
        echo "Troubleshooting:"
        echo "  1. Verify SSH key is added: ssh-add ${key}"
        echo "  2. Test manually: ssh ${user}@${target}"
        echo "  3. Check firewall allows port 22"
        exit 1
    fi
}

prompt_vastai_key() {
    if [[ -n "${VASTAI_API_KEY:-}" ]]; then
        print_success "Using VASTAI_API_KEY from environment"
        return 0
    fi

    echo ""
    print_warning "Vast.ai API key not found in environment"
    echo "Get your API key from: https://cloud.vast.ai/account/"
    echo ""
    read -rsp "Enter your Vast.ai API key: " VASTAI_API_KEY
    echo ""

    if [[ -z "$VASTAI_API_KEY" ]]; then
        print_error "API key is required"
        exit 1
    fi

    export VASTAI_API_KEY
    print_success "API key received"
}

create_temp_inventory() {
    local target="$1"
    local user="$2"
    local key="${SSH_KEY_PATH:-$HOME/.ssh/id_rsa}"

    print_step "Creating temporary inventory..."

    cat > "$TEMP_INVENTORY" << EOF
---
all:
  hosts:
    vastai_host:
      ansible_host: ${target}
      ansible_user: ${user}
      ansible_ssh_private_key_file: ${key}
      ansible_python_interpreter: /usr/bin/python3

  vars:
    # Vast.ai Configuration
    vastai_api_key: "${VASTAI_API_KEY}"
    vastai_enabled: true
    vastai_min_gpu: 1
    vastai_port_range_start: 40000
    vastai_port_range_end: 40019

    # GPU Configuration
    gpu_nvidia_enabled: true
    gpu_nvidia_driver_version: "550"
    gpu_container_toolkit_enabled: true
    gpu_monitoring_enabled: true

    # Enable Docker (required for Vast.ai)
    container_docker_enabled: true
    container_docker_compose_enabled: true

    # Security (recommended defaults)
    fail2ban_enabled: true
    firewall_enabled: true

    # Common role settings
    common_update_packages: true
    common_upgrade_packages: true
EOF

    print_success "Inventory created at $TEMP_INVENTORY"
}

run_playbook() {
    local verbosity="${ANSIBLE_VERBOSITY:-1}"
    local verbosity_flag=""

    for ((i=0; i<verbosity; i++)); do
        verbosity_flag="${verbosity_flag}v"
    done

    if [[ -n "$verbosity_flag" ]]; then
        verbosity_flag="-${verbosity_flag}"
    fi

    print_step "Running Vast.ai deployment playbook..."
    echo "Logging to: $LOG_FILE"
    echo ""

    cd "${ANSIBLE_DIR}"

    set +e
    ansible-playbook "$PLAYBOOK" \
        -i "$TEMP_INVENTORY" \
        $verbosity_flag \
        --diff \
        2>&1 | tee -a "$LOG_FILE"

    local exit_code=${PIPESTATUS[0]}
    set -e

    if [[ $exit_code -eq 0 ]]; then
        print_success "Deployment completed successfully!"
    else
        print_error "Deployment failed with exit code $exit_code"
        echo "Check log file: $LOG_FILE"
        return $exit_code
    fi
}

cleanup() {
    print_step "Cleaning up..."

    if [[ -f "$TEMP_INVENTORY" ]]; then
        rm -f "$TEMP_INVENTORY"
        print_success "Temporary inventory removed"
    fi
}

show_next_steps() {
    local target="$1"

    print_header "Deployment Complete - Next Steps"

    cat << EOF
${GREEN}Your Vast.ai GPU host is configured!${NC}

${YELLOW}1. Configure Port Forwarding on Your Router:${NC}
   Forward TCP ports 40000-40019 to ${target}

${YELLOW}2. Verify Vast.ai Registration:${NC}
   SSH into the server and check:
   ${CYAN}cat /var/lib/vastai_kaalia/machine_id${NC}

${YELLOW}3. Check GPU Status:${NC}
   ${CYAN}nvidia-smi${NC}
   ${CYAN}docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi${NC}

${YELLOW}4. Monitor Vast.ai Dashboard:${NC}
   https://cloud.vast.ai/host/machines

${YELLOW}5. Set Pricing (via CLI):${NC}
   ${CYAN}vastai list machine <MACHINE_ID> --price_gpu 0.50 --min_chunk 1${NC}

${YELLOW}6. Run Self-Test:${NC}
   ${CYAN}vastai self-test machine <MACHINE_ID>${NC}

${YELLOW}Log File:${NC} ${LOG_FILE}

${YELLOW}Troubleshooting:${NC}
   - Check daemon: ${CYAN}sudo systemctl status vastai${NC}
   - View logs: ${CYAN}sudo journalctl -u vastai -f${NC}
   - Restart: ${CYAN}sudo systemctl restart vastai${NC}

EOF
}

# ============================================================================
# MAIN
# ============================================================================
main() {
    if [[ $# -lt 1 ]] || [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
        show_usage
        exit 0
    fi

    local TARGET_IP="$1"
    local TARGET_USER="${2:-${USER:-ubuntu}}"

    if ! [[ "$TARGET_IP" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        print_error "Invalid IP address format: $TARGET_IP"
        exit 1
    fi

    print_header "Vast.ai GPU Host Bootstrap"
    echo "Target:   ${TARGET_USER}@${TARGET_IP}"
    echo "Playbook: ${PLAYBOOK}"
    echo ""

    trap cleanup EXIT

    check_dependencies
    install_ansible
    install_collections
    test_ssh_connectivity "$TARGET_IP" "$TARGET_USER"
    prompt_vastai_key
    create_temp_inventory "$TARGET_IP" "$TARGET_USER"
    run_playbook

    show_next_steps "$TARGET_IP"
}

main "$@"
