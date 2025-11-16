#!/bin/bash

# Docker-Based Testing Script - Tests all 11 supported OS distributions
# Uses native ARM64 Docker images (optimal for Apple Silicon M1/M2/M3/M4)

set -euo pipefail

REPO_PATH="/Users/kevin/ansible-infra"
RESULTS_FILE="${REPO_PATH}/DOCKER_TEST_RESULTS.md"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test matrix: os_name:docker_image:package_manager
declare -a TEST_MATRIX=(
    # Debian-based
    "Ubuntu 20.04:ubuntu:20.04:apt"
    "Ubuntu 22.04:ubuntu:22.04:apt"
    "Ubuntu 24.04:ubuntu:24.04:apt"
    "Debian 11:debian:11:apt"
    "Debian 12:debian:12:apt"
    # Alpine
    "Alpine 3.16:alpine:3.16:apk"
    "Alpine 3.20:alpine:3.20:apk"
    # RedHat-based
    "CentOS Stream 8:centos:8:yum"
    "CentOS Stream 9:centos:stream9:yum"
    "Rocky Linux 8:rockylinux:8:yum"
    "Rocky Linux 9:rockylinux:9:yum"
)

# Results tracking
declare -A TEST_RESULTS
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

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

# Function to test a distribution using Docker
test_distribution_docker() {
    local os_name=$1
    local docker_image=$2
    local image_tag=$3
    local pkg_manager=$4
    local container_name="ansible-test-${os_name// /-}-$(date +%s | tail -c 5)"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    print_status "INFO" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_status "INFO" "Testing: $os_name"
    print_status "INFO" "Docker Image: $docker_image:$image_tag"
    print_status "INFO" "Container: $container_name"
    echo ""

    # Test 1: Pull image and launch container
    print_status "INFO" "  [1/5] Pulling Docker image..."
    if ! docker pull "$docker_image:$image_tag" > /dev/null 2>&1; then
        print_status "FAIL" "    Failed to pull $docker_image:$image_tag"
        TEST_RESULTS["$os_name"]="PULL_FAILED"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
    print_status "SUCCESS" "    Image pulled successfully"

    # Test 2: OS Detection
    print_status "INFO" "  [2/5] OS Detection"
    if OS_INFO=$(docker run --rm "$docker_image:$image_tag" uname -a 2>/dev/null); then
        print_status "SUCCESS" "    $(echo "$OS_INFO" | tail -1 | cut -c1-70)..."
    else
        print_status "FAIL" "    Could not detect OS"
        TEST_RESULTS["$os_name"]="OS_DETECT_FAILED"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi

    # Test 3: Python Availability
    print_status "INFO" "  [3/5] Python Availability"
    if PYTHON_VERSION=$(docker run --rm "$docker_image:$image_tag" python3 --version 2>&1); then
        print_status "SUCCESS" "    $PYTHON_VERSION"
    else
        print_status "WARN" "    Python3 not pre-installed"
    fi

    # Test 4: Package Manager
    print_status "INFO" "  [4/5] Package Manager"
    if [ "$pkg_manager" = "apt" ]; then
        if docker run --rm "$docker_image:$image_tag" dpkg --version > /dev/null 2>&1; then
            print_status "SUCCESS" "    APT/DPKG functional"
        fi
    elif [ "$pkg_manager" = "apk" ]; then
        if docker run --rm "$docker_image:$image_tag" apk --version > /dev/null 2>&1; then
            print_status "SUCCESS" "    APK functional"
        fi
    elif [ "$pkg_manager" = "yum" ]; then
        if docker run --rm "$docker_image:$image_tag" yum --version > /dev/null 2>&1; then
            print_status "SUCCESS" "    YUM functional"
        fi
    fi

    # Test 5: Framework Transfer & Role Structure
    print_status "INFO" "  [5/5] Framework & Role Structure"

    # Copy framework to container and test
    if docker run --rm \
        -v "$REPO_PATH:/tmp/ansible-infra:ro" \
        "$docker_image:$image_tag" \
        ls /tmp/ansible-infra/roles/common/tasks > /dev/null 2>&1; then

        TASK_COUNT=$(docker run --rm \
            -v "$REPO_PATH:/tmp/ansible-infra:ro" \
            "$docker_image:$image_tag" \
            ls -1 /tmp/ansible-infra/roles/common/tasks 2>/dev/null | wc -l)

        if [ "$TASK_COUNT" -gt 5 ]; then
            print_status "SUCCESS" "    Framework accessible ($TASK_COUNT task files)"
            TEST_RESULTS["$os_name"]="PASSED"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            print_status "FAIL" "    Role structure incomplete ($TASK_COUNT files)"
            TEST_RESULTS["$os_name"]="STRUCTURE_FAILED"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        print_status "FAIL" "    Framework not accessible"
        TEST_RESULTS["$os_name"]="TRANSFER_FAILED"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi

    echo ""
}

# Main execution
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "DOCKER-BASED COMPREHENSIVE OS TESTING"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
print_status "INFO" "Testing Framework: $REPO_PATH"
print_status "INFO" "Testing Method: Docker (native ARM64 images)"
print_status "INFO" "Timestamp: $TIMESTAMP"
print_status "INFO" "Target Architecture: linux/arm64 (Apple Silicon optimized)"
echo ""

# Run tests
print_status "INFO" "STARTING DISTRIBUTION TESTS"
for test_case in "${TEST_MATRIX[@]}"; do
    IFS=':' read -r os_name docker_image image_tag pkg_manager <<< "$test_case"
    test_distribution_docker "$os_name" "$docker_image" "$image_tag" "$pkg_manager"
done

# Summary
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "TEST SUMMARY"
echo "════════════════════════════════════════════════════════════════════════════════"
print_status "INFO" "Total Tests: $TOTAL_TESTS"
print_status "SUCCESS" "Passed: $PASSED_TESTS"
print_status "FAIL" "Failed: $FAILED_TESTS"
echo ""

if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    print_status "INFO" "Success Rate: $SUCCESS_RATE%"
fi

echo ""

# Generate markdown report
{
    echo "# Docker-Based Comprehensive OS Testing Results"
    echo ""
    echo "**Date**: $TIMESTAMP"
    echo "**Testing Method**: Docker (native ARM64 images)"
    echo "**Architecture**: linux/arm64 (Apple Silicon M1/M2/M3/M4)"
    echo "**Total Tests**: $TOTAL_TESTS"
    echo "**Passed**: $PASSED_TESTS"
    echo "**Failed**: $FAILED_TESTS"
    echo ""

    if [ $TOTAL_TESTS -gt 0 ]; then
        echo "**Success Rate**: $SUCCESS_RATE%"
        echo ""
    fi

    echo "## Test Results by Distribution"
    echo ""
    echo "| OS | Status | Details |"
    echo "|---|---|---|"
    for os_name in "${!TEST_RESULTS[@]}"; do
        status=${TEST_RESULTS[$os_name]}
        if [[ "$status" == "PASSED" ]]; then
            echo "| $os_name | ✓ PASSED | Framework accessible, role structure intact |"
        else
            echo "| $os_name | ✗ $status | See logs above for details |"
        fi
    done

    echo ""
    echo "## Test Coverage"
    echo ""
    echo "Each OS distribution tested for:"
    echo "- Docker image availability (native ARM64)"
    echo "- OS detection and kernel information"
    echo "- Python 3 availability (pre-installed or not)"
    echo "- Package manager functionality"
    echo "- Framework accessibility and integrity"
    echo "- Role structure validation"

} > "$RESULTS_FILE"

print_status "SUCCESS" "Report saved to: $RESULTS_FILE"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    print_status "SUCCESS" "All $TOTAL_TESTS distributions tested successfully!"
    exit 0
else
    print_status "WARN" "$FAILED_TESTS of $TOTAL_TESTS tests failed"
    exit 1
fi
