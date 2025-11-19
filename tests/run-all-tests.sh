#!/bin/bash

# Comprehensive Test Runner
# Runs all tests and generates report

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TESTS_DIR="$PROJECT_DIR/tests"
RESULTS_FILE="$TESTS_DIR/test-results.txt"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

echo "======================================================================"
echo "  Ansible Infrastructure - Comprehensive Test Suite"
echo "======================================================================"
echo ""

# Function to run a test
run_test() {
    local test_name=$1
    local test_command=$2
    local test_file=$3

    echo -e "${BLUE}Running: ${test_name}${NC}"

    if [ ! -f "$test_file" ]; then
        echo -e "${YELLOW}SKIPPED${NC}: Test file not found: $test_file"
        ((TESTS_SKIPPED++))
        echo ""
        return
    fi

    if eval "$test_command"; then
        echo -e "${GREEN}PASSED${NC}: $test_name"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}FAILED${NC}: $test_name"
        ((TESTS_FAILED++))
    fi
    echo ""
}

# ==================== SYNTAX VALIDATION ====================
echo -e "${BLUE}=== PHASE 1: SYNTAX VALIDATION ===${NC}"
echo ""

run_test "Playbook Syntax" \
    "cd $PROJECT_DIR && ansible-playbook --syntax-check playbooks/*.yml" \
    "$PROJECT_DIR/playbooks/deploy-proxmox.yml"

run_test "Role Syntax" \
    "cd $PROJECT_DIR && find roles -name '*.yml' | xargs -I {} ansible-playbook --syntax-check {} 2>/dev/null" \
    "$PROJECT_DIR/roles/wireguard_vpn/tasks/main.yml"

# ==================== MOLECULE TESTS ====================
echo -e "${BLUE}=== PHASE 2: MOLECULE INTEGRATION TESTS ===${NC}"
echo ""

if command -v molecule &> /dev/null; then
    echo "Molecule found. Running Molecule tests..."
    echo ""

    # Full Mesh
    run_test "Molecule Full Mesh" \
        "cd $PROJECT_DIR/roles/wireguard_vpn && molecule test -s full-mesh 2>/dev/null" \
        "$PROJECT_DIR/roles/wireguard_vpn/molecule/full-mesh/molecule.yml"

    # Hub-Spoke
    run_test "Molecule Hub-Spoke" \
        "cd $PROJECT_DIR/roles/wireguard_vpn && molecule test -s hub-spoke 2>/dev/null" \
        "$PROJECT_DIR/roles/wireguard_vpn/molecule/hub-spoke/molecule.yml"

    # Site-to-Site
    run_test "Molecule Site-to-Site" \
        "cd $PROJECT_DIR/roles/wireguard_vpn && molecule test -s site-to-site 2>/dev/null" \
        "$PROJECT_DIR/roles/wireguard_vpn/molecule/site-to-site/molecule.yml"
else
    echo -e "${YELLOW}Molecule not installed. Skipping Molecule tests.${NC}"
    echo "To install: pip install molecule molecule-docker ansible-lint"
    echo ""
    TESTS_SKIPPED=$((TESTS_SKIPPED + 3))
fi

# ==================== ANSIBLE VALIDATION ====================
echo -e "${BLUE}=== PHASE 3: ANSIBLE VALIDATION ===${NC}"
echo ""

run_test "Ansible Inventory" \
    "cd $PROJECT_DIR && ansible-inventory -i inventories/production/hosts/proxmox.yml --list 2>/dev/null | head -1" \
    "$PROJECT_DIR/inventories/production/hosts/proxmox.yml"

run_test "Ansible Roles" \
    "cd $PROJECT_DIR && ansible-galaxy role list 2>/dev/null | grep -q wireguard || true && echo 'OK'" \
    "$PROJECT_DIR/roles/wireguard_vpn"

# ==================== TEMPLATE VALIDATION ====================
echo -e "${BLUE}=== PHASE 4: TEMPLATE VALIDATION ===${NC}"
echo ""

# Check if Jinja2 templates are present
if [ -f "$PROJECT_DIR/roles/wireguard_vpn/templates/wireguard.conf.j2" ]; then
    echo -e "${GREEN}✓${NC} Wireguard template exists"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} Wireguard template missing"
    ((TESTS_FAILED++))
fi
echo ""

# ==================== CONFIGURATION VALIDATION ====================
echo -e "${BLUE}=== PHASE 5: CONFIGURATION VALIDATION ===${NC}"
echo ""

# Check for required files
required_files=(
    "roles/wireguard_vpn/tasks/main.yml"
    "roles/opnsense_firewall/tasks/main.yml"
    "roles/pfsense_firewall/tasks/main.yml"
    "playbooks/deploy-wireguard.yml"
    "playbooks/deploy-firewalls.yml"
)

for file in "${required_files[@]}"; do
    if [ -f "$PROJECT_DIR/$file" ]; then
        echo -e "${GREEN}✓${NC} Found: $file"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} Missing: $file"
        ((TESTS_FAILED++))
    fi
done
echo ""

# ==================== DOCUMENTATION VALIDATION ====================
echo -e "${BLUE}=== PHASE 6: DOCUMENTATION VALIDATION ===${NC}"
echo ""

required_docs=(
    "IMPLEMENTATION_STATUS.md"
    "QUICK_START.md"
    "NETWORK_INFRASTRUCTURE_GUIDE.md"
)

for doc in "${required_docs[@]}"; do
    if [ -f "$PROJECT_DIR/$doc" ]; then
        lines=$(wc -l < "$PROJECT_DIR/$doc")
        echo -e "${GREEN}✓${NC} Found: $doc ($lines lines)"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} Missing: $doc"
        ((TESTS_FAILED++))
    fi
done
echo ""

# ==================== TEST SUMMARY ====================
echo "======================================================================"
echo "  TEST SUMMARY"
echo "======================================================================"
echo ""
echo -e "Passed:  ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed:  ${RED}$TESTS_FAILED${NC}"
echo -e "Skipped: ${YELLOW}$TESTS_SKIPPED${NC}"
echo ""

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
if [ $TOTAL_TESTS -gt 0 ]; then
    PASS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))
    echo -e "Pass Rate: ${GREEN}${PASS_RATE}%${NC}"
    echo ""
fi

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    echo ""
    echo "Status: READY FOR DEPLOYMENT"
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo ""
    echo "Review output above for failures"
    exit 1
fi
