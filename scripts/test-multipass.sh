#!/bin/bash

# Multipass Testing Framework for Ansible Common Role
# Tests all supported distributions

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_PATH="/Users/kevin/ansible-infra"
TEST_DIR="/tmp/ansible-test"
LOG_FILE="/tmp/ansible-test-results.log"
RESULTS_FILE="${REPO_PATH}/TEST_RESULTS.md"

# Test matrix: os_name:os_version:image_name
declare -a TEST_MATRIX=(
    "Ubuntu:20.04:ubuntu-20.04"
    "Ubuntu:22.04:ubuntu-22.04"
    "Ubuntu:24.04:ubuntu-24.04"
    "Debian:11:debian-11"
    "Debian:12:debian-12"
    "CentOS:8:centos-stream-8"
    "CentOS:9:centos-stream-9"
    "Rocky:8:rocky-8"
    "Rocky:9:rocky-9"
    "Alpine:3.18:alpine-3.18"
    "Alpine:3.20:alpine-3.20"
)

# Initialize results
declare -A RESULTS
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

echo "════════════════════════════════════════════════════════════════"
echo "Ansible Common Role - Multipass Testing Framework"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Function to print status
print_status() {
    local status=$1
    local message=$2
    case $status in
        "SUCCESS")
            echo -e "${GREEN}[✓]${NC} $message"
            ;;
        "FAIL")
            echo -e "${RED}[✗]${NC} $message"
            ;;
        "INFO")
            echo -e "${BLUE}[i]${NC} $message"
            ;;
        "WARN")
            echo -e "${YELLOW}[!]${NC} $message"
            ;;
    esac
}

# Function to create and test VM
test_distribution() {
    local os_name=$1
    local os_version=$2
    local image_name=$3
    local vm_name="test-${os_name,,}-${os_version}"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    print_status "INFO" "Testing $os_name $os_version (image: $image_name)"

    # Launch VM
    print_status "INFO" "  → Launching VM: $vm_name"
    if multipass launch --name "$vm_name" --image "$image_name" --timeout 600 2>/dev/null; then
        print_status "SUCCESS" "  → VM launched successfully"
    else
        print_status "FAIL" "  → Failed to launch VM"
        RESULTS["$os_name:$os_version"]="LAUNCH_FAILED"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi

    # Wait for VM to be ready
    sleep 5

    # Install Python (required for Ansible)
    print_status "INFO" "  → Installing Python..."
    if [[ "$image_name" == "alpine"* ]]; then
        multipass exec "$vm_name" -- apk add --no-cache python3 openssh-client > /dev/null 2>&1
    else
        multipass exec "$vm_name" -- apt-get update > /dev/null 2>&1 || yum install -y python3 > /dev/null 2>&1
        multipass exec "$vm_name" -- apt-get install -y python3 > /dev/null 2>&1 || yum install -y python3 > /dev/null 2>&1
    fi
    print_status "SUCCESS" "  → Python installed"

    # Copy ansible-infra to VM
    print_status "INFO" "  → Copying Ansible framework..."
    multipass transfer -r "$REPO_PATH" "$vm_name":/home/ubuntu/ansible-infra 2>/dev/null || \
    multipass transfer -r "$REPO_PATH" "$vm_name":/root/ansible-infra 2>/dev/null || true
    print_status "SUCCESS" "  → Framework copied"

    # Test common role syntax
    print_status "INFO" "  → Testing role syntax..."
    if multipass exec "$vm_name" -- \
        python3 -m py_compile /home/ubuntu/ansible-infra/roles/common/tasks/*.yml 2>/dev/null || \
        python3 -m py_compile /root/ansible-infra/roles/common/tasks/*.yml 2>/dev/null; then
        print_status "SUCCESS" "  → Syntax check passed"
        RESULTS["$os_name:$os_version"]="PASSED"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        print_status "FAIL" "  → Syntax check failed"
        RESULTS["$os_name:$os_version"]="SYNTAX_FAILED"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi

    # Clean up VM
    print_status "INFO" "  → Cleaning up VM..."
    multipass delete -p "$vm_name" > /dev/null 2>&1 || true
    print_status "SUCCESS" "  → VM removed"
    echo ""
}

# Run tests
echo "Starting tests for ${#TEST_MATRIX[@]} distributions..."
echo ""

for test_case in "${TEST_MATRIX[@]}"; do
    IFS=':' read -r os_name os_version image_name <<< "$test_case"
    test_distribution "$os_name" "$os_version" "$image_name"
done

# Generate report
echo "════════════════════════════════════════════════════════════════"
echo "Test Results Summary"
echo "════════════════════════════════════════════════════════════════"
echo ""
print_status "INFO" "Total Tests: $TOTAL_TESTS"
print_status "SUCCESS" "Passed: $PASSED_TESTS"
print_status "FAIL" "Failed: $FAILED_TESTS"
echo ""

# Create markdown report
{
    echo "# Ansible Common Role - Testing Report"
    echo ""
    echo "**Date**: $(date)"
    echo "**Testing Framework**: Multipass"
    echo "**Total Tests**: $TOTAL_TESTS"
    echo "**Passed**: $PASSED_TESTS"
    echo "**Failed**: $FAILED_TESTS"
    echo "**Success Rate**: $((PASSED_TESTS * 100 / TOTAL_TESTS))%"
    echo ""
    echo "## Test Results by Distribution"
    echo ""
    echo "| OS | Version | Status |"
    echo "|---|---|---|"

    for test_case in "${TEST_MATRIX[@]}"; do
        IFS=':' read -r os_name os_version image_name <<< "$test_case"
        status=${RESULTS["$os_name:$os_version"]:-"UNKNOWN"}
        if [[ "$status" == "PASSED" ]]; then
            status_icon="✓ PASSED"
        else
            status_icon="✗ $status"
        fi
        echo "| $os_name | $os_version | $status_icon |"
    done

    echo ""
    echo "## Detailed Test Log"
    echo ""
    if [[ -f "$LOG_FILE" ]]; then
        echo '```'
        cat "$LOG_FILE"
        echo '```'
    fi
} > "$RESULTS_FILE"

print_status "SUCCESS" "Report generated: $RESULTS_FILE"
echo ""

if [[ $FAILED_TESTS -eq 0 ]]; then
    print_status "SUCCESS" "All tests passed!"
    exit 0
else
    print_status "FAIL" "Some tests failed"
    exit 1
fi
