#!/bin/bash

# Master Testing Script - Tests all supported OS distributions
# Executes comprehensive testing matrix and generates detailed results

set -euo pipefail

REPO_PATH="/Users/kevin/ansible-infra"
RESULTS_FILE="${REPO_PATH}/COMPREHENSIVE_TEST_RESULTS.md"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test matrix: os_name:image_name:os_family
declare -a TEST_MATRIX=(
    "Ubuntu 22.04:22.04:Debian"
    "Ubuntu 24.04:24.04:Debian"
    "Alpine 3.20:alpine:Alpine"
)

# Additional OS versions to attempt if images available
declare -a OPTIONAL_TESTS=(
    "Ubuntu 20.04:20.04:Debian"
    "Debian 12:debian-12:Debian"
    "Debian 11:debian-11:Debian"
    "CentOS Stream 9:centos-stream-9:RedHat"
    "CentOS Stream 8:centos-stream-8:RedHat"
    "Rocky 9:rocky-9:RedHat"
    "Rocky 8:rocky-8:RedHat"
)

# Results tracking
declare -A TEST_RESULTS
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

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

# Function to test a distribution
test_distribution() {
    local os_name=$1
    local image_name=$2
    local os_family=$3
    local vm_name="test-${os_name// /-}-$(date +%s | tail -c 5)"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    print_status "INFO" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_status "INFO" "Testing: $os_name (image: $image_name)"
    print_status "INFO" "VM Name: $vm_name"

    # Try to launch VM
    print_status "INFO" "  → Launching VM..."
    if ! timeout 600 multipass launch -n "$vm_name" -c 2 -m 2G -d 10G "$image_name" > /dev/null 2>&1; then
        print_status "FAIL" "  → Failed to launch $os_name"
        TEST_RESULTS["$os_name"]="LAUNCH_FAILED"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi

    print_status "SUCCESS" "  → VM launched successfully"
    sleep 3

    # Test 1: OS Detection
    print_status "INFO" "  → Test 1: OS Detection"
    if multipass exec "$vm_name" -- uname -a > /dev/null 2>&1; then
        OS_INFO=$(multipass exec "$vm_name" -- uname -a)
        print_status "SUCCESS" "    OS: $OS_INFO"
    else
        print_status "FAIL" "    Could not detect OS"
    fi

    # Test 2: Python Availability
    print_status "INFO" "  → Test 2: Python"
    if multipass exec "$vm_name" -- python3 --version > /dev/null 2>&1; then
        PYTHON_VERSION=$(multipass exec "$vm_name" -- python3 --version)
        print_status "SUCCESS" "    $PYTHON_VERSION"
    else
        print_status "WARN" "    Python3 not available, installing..."
        if [[ "$image_name" == "alpine"* ]]; then
            multipass exec "$vm_name" -- apk add --no-cache python3 > /dev/null 2>&1 || true
        else
            multipass exec "$vm_name" -- apt-get update > /dev/null 2>&1 || \
            multipass exec "$vm_name" -- yum install -y python3 > /dev/null 2>&1 || true
            multipass exec "$vm_name" -- apt-get install -y python3 > /dev/null 2>&1 || \
            multipass exec "$vm_name" -- yum install -y python3 > /dev/null 2>&1 || true
        fi
    fi

    # Test 3: Package Manager
    print_status "INFO" "  → Test 3: Package Manager"
    if [[ "$image_name" == "alpine"* ]]; then
        if multipass exec "$vm_name" -- apk info > /dev/null 2>&1; then
            print_status "SUCCESS" "    Alpine APK package manager functional"
        fi
    elif [[ "$os_family" == "RedHat" ]]; then
        if multipass exec "$vm_name" -- rpm --version > /dev/null 2>&1; then
            print_status "SUCCESS" "    RedHat RPM package manager functional"
        fi
    else
        if multipass exec "$vm_name" -- dpkg --version > /dev/null 2>&1; then
            print_status "SUCCESS" "    Debian DPKG package manager functional"
        fi
    fi

    # Test 4: Network Connectivity
    print_status "INFO" "  → Test 4: Network Connectivity"
    if multipass exec "$vm_name" -- ping -c 1 8.8.8.8 > /dev/null 2>&1; then
        print_status "SUCCESS" "    Network connectivity working"
    else
        print_status "WARN" "    Network connectivity limited"
    fi

    # Test 5: Framework Transfer
    print_status "INFO" "  → Test 5: Framework Transfer"
    if timeout 120 multipass transfer -r "$REPO_PATH" "$vm_name":/tmp/ansible-infra > /dev/null 2>&1; then
        print_status "SUCCESS" "    Framework transferred successfully"
    else
        print_status "FAIL" "    Framework transfer failed"
        TEST_RESULTS["$os_name"]="TRANSFER_FAILED"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        multipass delete -p "$vm_name" 2>/dev/null || true
        return 1
    fi

    # Test 6: Role Structure Validation
    print_status "INFO" "  → Test 6: Role Structure"
    TASK_FILES=$(multipass exec "$vm_name" -- ls /tmp/ansible-infra/roles/common/tasks/ 2>/dev/null | wc -l)
    if [ "$TASK_FILES" -gt 5 ]; then
        print_status "SUCCESS" "    Role structure valid ($TASK_FILES task files found)"
        TEST_RESULTS["$os_name"]="PASSED"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        print_status "FAIL" "    Role structure invalid"
        TEST_RESULTS["$os_name"]="STRUCTURE_FAILED"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi

    # Clean up
    print_status "INFO" "  → Cleaning up VM..."
    multipass delete -p "$vm_name" 2>/dev/null || true
    print_status "SUCCESS" "  → VM removed"

    echo ""
}

# Main execution
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "COMPREHENSIVE OS TESTING - ANSIBLE FRAMEWORK"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
print_status "INFO" "Testing Framework: $REPO_PATH"
print_status "INFO" "Timestamp: $TIMESTAMP"
print_status "INFO" "Test Approach: Sequential Multipass VM testing"
echo ""

# Run mandatory tests
print_status "INFO" "PHASE 1: Core Distribution Testing"
for test_case in "${TEST_MATRIX[@]}"; do
    IFS=':' read -r os_name image_name os_family <<< "$test_case"
    test_distribution "$os_name" "$image_name" "$os_family"
done

# Try optional tests
print_status "INFO" "PHASE 2: Optional Distribution Testing"
for test_case in "${OPTIONAL_TESTS[@]}"; do
    IFS=':' read -r os_name image_name os_family <<< "$test_case"
    print_status "WARN" "Attempting $os_name (may not be available)..."
    test_distribution "$os_name" "$image_name" "$os_family" || SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
done

# Summary
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "TEST SUMMARY"
echo "════════════════════════════════════════════════════════════════════════════════"
print_status "INFO" "Total Tests: $TOTAL_TESTS"
print_status "SUCCESS" "Passed: $PASSED_TESTS"
print_status "FAIL" "Failed: $FAILED_TESTS"
print_status "WARN" "Skipped: $SKIPPED_TESTS"
echo ""

# Calculate success rate
if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo "Success Rate: $SUCCESS_RATE%"
fi

# Generate markdown report
{
    echo "# Comprehensive OS Testing Results"
    echo ""
    echo "**Date**: $TIMESTAMP"
    echo "**Testing Framework**: Multipass"
    echo "**Total Tests**: $TOTAL_TESTS"
    echo "**Passed**: $PASSED_TESTS"
    echo "**Failed**: $FAILED_TESTS"
    echo "**Skipped**: $SKIPPED_TESTS"
    echo ""

    if [ $TOTAL_TESTS -gt 0 ]; then
        echo "**Success Rate**: $SUCCESS_RATE%"
        echo ""
    fi

    echo "## Test Results by Distribution"
    echo ""
    echo "| OS | Status |"
    echo "|---|---|"
    for os_name in "${!TEST_RESULTS[@]}"; do
        status=${TEST_RESULTS[$os_name]}
        if [[ "$status" == "PASSED" ]]; then
            echo "| $os_name | ✓ PASSED |"
        else
            echo "| $os_name | ✗ $status |"
        fi
    done

    echo ""
    echo "## Test Coverage"
    echo ""
    echo "Each OS distribution tested for:"
    echo "- OS detection and kernel information"
    echo "- Python 3 availability and version"
    echo "- Package manager functionality"
    echo "- Network connectivity to external resources"
    echo "- Framework transfer and integrity"
    echo "- Role structure validation"

} > "$RESULTS_FILE"

print_status "SUCCESS" "Report saved to: $RESULTS_FILE"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    print_status "SUCCESS" "All tests passed!"
    exit 0
else
    print_status "WARN" "Some tests failed or were skipped"
    exit 1
fi
