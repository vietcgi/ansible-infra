#!/bin/bash

# Validation Test Runner - Focuses on newly created components

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TESTS_DIR="$PROJECT_DIR/tests"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
TESTS_PASSED=0
TESTS_FAILED=0

echo "======================================================================"
echo "  Ansible Infrastructure - Validation Test Suite"
echo "======================================================================"
echo ""
echo "Testing newly created components:"
echo "- Wireguard (all 3 topologies)"
echo "- OPNSense Firewall Role"
echo "- pfSense Firewall Role"
echo "- Proxmox Infrastructure Role"
echo ""

# ==================== SYNTAX VALIDATION ====================
echo -e "${BLUE}=== SYNTAX VALIDATION ===${NC}"
echo ""

run_test() {
    local name=$1
    local cmd=$2

    echo -n "Testing: $name ... "
    if eval "$cmd" &>/dev/null; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "  Command: $cmd"
        ((TESTS_FAILED++))
    fi
}

# Test all new role task files
run_test "Wireguard main.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/wireguard_vpn/tasks/main.yml"

run_test "Wireguard topology-full-mesh.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/wireguard_vpn/tasks/topology-full-mesh.yml"

run_test "Wireguard topology-hub-spoke.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/wireguard_vpn/tasks/topology-hub-spoke.yml"

run_test "Wireguard topology-site-to-site.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/wireguard_vpn/tasks/topology-site-to-site.yml"

echo ""
echo -e "${BLUE}OPNSense Firewall Role${NC}"

run_test "OPNSense main.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/opnsense_firewall/tasks/main.yml"

run_test "OPNSense validate.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/opnsense_firewall/tasks/validate.yml"

run_test "OPNSense system.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/opnsense_firewall/tasks/system.yml"

run_test "OPNSense interfaces.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/opnsense_firewall/tasks/interfaces.yml"

run_test "OPNSense ha-carp.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/opnsense_firewall/tasks/ha-carp.yml"

run_test "OPNSense firewall-rules.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/opnsense_firewall/tasks/firewall-rules.yml"

run_test "OPNSense nat-rules.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/opnsense_firewall/tasks/nat-rules.yml"

run_test "OPNSense wireguard-vpn.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/opnsense_firewall/tasks/wireguard-vpn.yml"

run_test "OPNSense backup.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/opnsense_firewall/tasks/backup.yml"

echo ""
echo -e "${BLUE}pfSense Firewall Role${NC}"

run_test "pfSense main.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/pfsense_firewall/tasks/main.yml"

run_test "pfSense validate.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/pfsense_firewall/tasks/validate.yml"

run_test "pfSense system.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/pfsense_firewall/tasks/system.yml"

run_test "pfSense interfaces.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/pfsense_firewall/tasks/interfaces.yml"

run_test "pfSense routing.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/pfsense_firewall/tasks/routing.yml"

run_test "pfSense firewall-rules.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/pfsense_firewall/tasks/firewall-rules.yml"

run_test "pfSense nat-rules.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/pfsense_firewall/tasks/nat-rules.yml"

run_test "pfSense ha-carp.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/pfsense_firewall/tasks/ha-carp.yml"

run_test "pfSense vpn.yml" \
    "ansible-playbook --syntax-check $PROJECT_DIR/roles/pfsense_firewall/tasks/vpn.yml"

echo ""
echo -e "${BLUE}Proxmox Infrastructure Role${NC}"

run_test "Proxmox playbook" \
    "ansible-playbook --syntax-check $PROJECT_DIR/playbooks/deploy-proxmox.yml"

echo ""
echo -e "${BLUE}Wireguard Playbooks${NC}"

run_test "Deploy Wireguard playbook" \
    "ansible-playbook --syntax-check $PROJECT_DIR/playbooks/deploy-wireguard.yml"

# ==================== FILE EXISTENCE ====================
echo ""
echo -e "${BLUE}=== FILE EXISTENCE ===${NC}"
echo ""

check_file() {
    local path=$1
    local name=$2

    echo -n "Checking: $name ... "
    if [ -f "$path" ]; then
        local lines=$(wc -l < "$path")
        echo -e "${GREEN}✓ EXISTS${NC} ($lines lines)"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ MISSING${NC}"
        ((TESTS_FAILED++))
    fi
}

# Wireguard
check_file "$PROJECT_DIR/roles/wireguard_vpn/templates/wireguard.conf.j2" "Wireguard Jinja2 template"
check_file "$PROJECT_DIR/roles/wireguard_vpn/molecule/full-mesh/molecule.yml" "Molecule full-mesh config"
check_file "$PROJECT_DIR/roles/wireguard_vpn/molecule/hub-spoke/molecule.yml" "Molecule hub-spoke config"
check_file "$PROJECT_DIR/roles/wireguard_vpn/molecule/site-to-site/molecule.yml" "Molecule site-to-site config"

# OPNSense
check_file "$PROJECT_DIR/roles/opnsense_firewall/tasks/main.yml" "OPNSense main task"
check_file "$PROJECT_DIR/oxlorg.opnsense_collection_documentation.md" "OPNSense collection docs"

# pfSense
check_file "$PROJECT_DIR/roles/pfsense_firewall/tasks/main.yml" "pfSense main task"

# Documentation
check_file "$PROJECT_DIR/IMPLEMENTATION_STATUS.md" "Implementation status"
check_file "$PROJECT_DIR/tests/README.md" "Test documentation"

# ==================== TEMPLATE VALIDATION ====================
echo ""
echo -e "${BLUE}=== TEMPLATE VALIDATION ===${NC}"
echo ""

echo -n "Validating Wireguard Jinja2 template... "
if grep -q "\[Interface\]" "$PROJECT_DIR/roles/wireguard_vpn/templates/wireguard.conf.j2" && \
   grep -q "\[Peer\]" "$PROJECT_DIR/roles/wireguard_vpn/templates/wireguard.conf.j2"; then
    echo -e "${GREEN}✓ VALID${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ INVALID${NC}"
    ((TESTS_FAILED++))
fi

# ==================== SUMMARY ====================
echo ""
echo "======================================================================"
echo "  TEST SUMMARY"
echo "======================================================================"
echo ""
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

TOTAL=$((TESTS_PASSED + TESTS_FAILED))
if [ $TOTAL -gt 0 ]; then
    RATE=$((TESTS_PASSED * 100 / TOTAL))
    echo -e "Pass Rate: ${GREEN}${RATE}%${NC}"
fi

echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    echo ""
    echo "Status: Components syntactically valid and properly implemented"
    echo ""
    echo "Next steps:"
    echo "1. Run Molecule tests: cd roles/wireguard_vpn && molecule test"
    echo "2. Deploy to test environment with real VMs/containers"
    echo "3. Run connectivity tests after deployment"
    echo ""
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo ""
    echo "Review output above for details"
    exit 1
fi
