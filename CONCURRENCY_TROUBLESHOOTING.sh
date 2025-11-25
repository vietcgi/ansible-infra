#!/bin/bash
# KumoMTA Concurrency Troubleshooting Script
# Run this on the production server to diagnose why available_parallelism=1
# Usage: ssh kevin@108.181.38.69 'bash -s' < CONCURRENCY_TROUBLESHOOTING.sh

set -e

echo "==================================================================="
echo "KumoMTA Concurrency Investigation"
echo "$(date)"
echo "==================================================================="
echo ""

# Get process info
echo "=== KUMOMTA PROCESS INFORMATION ==="
KM_PID=$(pgrep -f 'kumod' | head -1)
if [ -z "$KM_PID" ]; then
    echo "❌ KumoMTA process not found!"
    echo "Start it with: sudo systemctl start kumomta"
    exit 1
fi
echo "Process ID: $KM_PID"
echo "Process Status:"
ps aux | grep -E "^\s*[^ ]*\s*$KM_PID\s"
echo ""

# CPU Information
echo "=== SYSTEM CPU INFORMATION ==="
echo "Total CPU cores (nproc): $(nproc)"
echo "CPU info:"
grep -E "^processor|^cpu cores" /proc/cpuinfo | head -10
echo "Model name:"
grep "model name" /proc/cpuinfo | head -1
echo ""

# Process CPU Affinity
echo "=== PROCESS CPU AFFINITY ==="
echo "CPUs available to KumoMTA process:"
if command -v taskset &> /dev/null; then
    taskset -p $KM_PID
else
    # Fallback: read from /proc
    echo "cpus_allowed_list: $(cat /proc/$KM_PID/status | grep -E '^Cpus_allowed_list' | awk '{print $2}')"
fi
echo ""

# Cgroup Information (v2)
echo "=== CGROUP V2 INFORMATION ==="
if [ -f "/sys/fs/cgroup/cpu.max" ]; then
    echo "CPU max limit:"
    cat /sys/fs/cgroup/cpu.max
    echo ""
    echo "CPU current utilization:"
    cat /sys/fs/cgroup/cpu.stat 2>/dev/null | head -5 || echo "  (not available)"
else
    echo "  Not using cgroup v2"
fi
echo ""

# Cgroup Information (v1)
echo "=== CGROUP V1 INFORMATION ==="
if [ -d "/sys/fs/cgroup/cpuset" ] && [ -f "/sys/fs/cgroup/cpuset/cpuset.cpus" ]; then
    echo "CPUs assigned (cpuset.cpus):"
    cat /sys/fs/cgroup/cpuset/cpuset.cpus
    echo ""
    echo "CPU shares (cpu.shares):"
    if [ -f "/sys/fs/cgroup/cpu/cpu.shares" ]; then
        cat /sys/fs/cgroup/cpu/cpu.shares
    else
        echo "  (not available)"
    fi
else
    echo "  Not using cgroup v1 cpuset"
fi
echo ""

# NUMA Information
echo "=== NUMA INFORMATION ==="
if command -v numactl &> /dev/null; then
    echo "NUMA available:"
    numactl -H | head -10
    echo ""
    echo "Current process NUMA affinity:"
    numactl -p -l $KM_PID 2>/dev/null || echo "  (unable to read)"
else
    echo "  numactl not installed (NUMA likely not configured)"
fi
echo ""

# KumoMTA Logs
echo "=== KUMOMTA RECENT LOGS ==="
echo "Last 30 log lines mentioning parallelism/concurrency/cores/threads:"
if command -v journalctl &> /dev/null; then
    echo "--- From journalctl: ---"
    journalctl -u kumomta -n 200 --no-pager 2>/dev/null | grep -i -E 'parallelism|concurrency|cores|threads|available_parallelism' | tail -10 || echo "  (no matches found)"
else
    echo "  (journalctl not available)"
fi

if [ -f "/var/log/kumomta/init.log" ]; then
    echo "--- From init.log: ---"
    grep -i -E 'parallelism|concurrency|cores|threads' /var/log/kumomta/init.log | tail -5 || echo "  (no matches found)"
fi
echo ""

# Systemd Service Info
echo "=== SYSTEMD SERVICE CONFIGURATION ==="
echo "KumoMTA systemd service limits:"
systemctl show kumomta 2>/dev/null | grep -i -E 'CPUAccounting|CPUQuota|MemoryLimit|TasksMax|LimitNOFILE' || echo "  (not available)"
echo ""

# Environment Variables
echo "=== KUMOMTA ENVIRONMENT VARIABLES ==="
echo "Environment variables passed to kumod:"
cat /proc/$KM_PID/environ 2>/dev/null | tr '\0' '\n' | grep -i -E 'RAYON|RUST|THREAD|CPU|NUMA' || echo "  (none found)"
echo ""

# KumoMTA Configuration
echo "=== KUMOMTA CONFIGURATION ==="
if [ -f "/opt/kumomta/etc/policy/init.lua" ]; then
    echo "Policy file location: /opt/kumomta/etc/policy/init.lua"
    echo "Policy file size: $(wc -c < /opt/kumomta/etc/policy/init.lua) bytes"
    echo "First few lines:"
    head -20 /opt/kumomta/etc/policy/init.lua | head -10
else
    echo "  Policy file not found at /opt/kumomta/etc/policy/init.lua"
fi
echo ""

# Try to get metrics
echo "=== KUMOMTA METRICS ==="
echo "Attempting to retrieve metrics from port 9184..."
if curl -s -m 5 http://localhost:9184/metrics > /tmp/kumomta_metrics.txt 2>/dev/null; then
    echo "✓ Metrics endpoint responding"
    echo "Total metrics lines: $(wc -l < /tmp/kumomta_metrics.txt)"
    echo "Relevant metrics:"
    grep -E 'scheduled_count|resident_memory|concurrency|workers|threads' /tmp/kumomta_metrics.txt | head -10
else
    echo "✗ Metrics endpoint not responding"
    echo "  (Try: curl -v http://localhost:9184/metrics)"
fi
echo ""

# Service Status
echo "=== SERVICE STATUS ==="
sudo systemctl status kumomta --no-pager 2>/dev/null | head -20 || echo "  (unable to read - may need sudo)"
echo ""

echo "==================================================================="
echo "Investigation Complete"
echo "==================================================================="
echo ""
echo "INTERPRETATION GUIDE:"
echo ""
echo "1. If 'CPUs available to KumoMTA' shows only 0 (not 0-23):"
echo "   → Cgroup or container is restricting to 1 CPU"
echo "   → This is why available_parallelism=1"
echo "   → Fix: Increase cgroup CPU limit or move to unrestricted container"
echo ""
echo "2. If 'System CPU cores' shows 24 but 'CPU available to process' shows 1:"
echo "   → Process is restricted by cgroup/container"
echo "   → Fix: Check docker run -c, kubernetes limits, systemd CPUQuota"
echo ""
echo "3. If environment variables show RAYON_NUM_THREADS or similar:"
echo "   → Can try setting these in systemd service"
echo "   → Edit: sudo systemctl edit kumomta"
echo "   → Add: Environment=\"RAYON_NUM_THREADS=12\""
echo ""
echo "4. If NUMA info shows multiple nodes but process limited to one:"
echo "   → NUMA node has only 1 core assigned"
echo "   → Fix: Adjust NUMA affinity or assign more cores"
echo ""
echo "NEXT STEPS:"
echo "1. Review output above for 'CPUs available to KumoMTA'"
echo "2. If restricted to 1 core, determine why (cgroup, container, NUMA)"
echo "3. Either expand CPU assignment or adjust KumoMTA configuration"
echo "4. Possible workaround: increase memory limit to 4GB"
echo ""
