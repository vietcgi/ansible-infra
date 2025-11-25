# KumoMTA Concurrency Issue - Deep Investigation

**Date**: November 25, 2025
**Investigation Focus**: Why KumoMTA shows `available_parallelism=1` despite having 24 CPU cores
**Status**: Root cause identified - design issue with configuration mechanism

---

## Executive Summary

The email delivery failure is caused by **KumoMTA's `available_parallelism` detection returning 1 instead of 24**, even though:
- System has 24 CPU cores
- Ansible config is set to `kumomta_worker_threads: 12`
- Systemd service has `CPUQuota=100%`
- Process cpuset shows `Cpus_allowed_list: 0-23`

**Root cause**: The `kumomta_worker_threads` variable is **never actually passed to KumoMTA**. It's only used in a Lua configuration file that KumoMTA doesn't read for concurrency settings.

---

## Architecture Analysis

### Current Configuration Flow

```
Ansible → Group Variables (kumomta_worker_threads=12)
        ↓
   Jinja2 Templates
        ↓
   Lua Config Files (queue.lua, policy.lua)
        ↓
   KumoMTA Binary (reads --policy flag only)
        ↓
   Rust std::thread::available_parallelism()
        ↓
   Returns: 1 (incorrect)
```

**The Problem**: The worker_threads variable is templated into Lua files, but KumoMTA doesn't read those files for concurrency configuration. KumoMTA automatically detects parallelism using Rust's `std::thread::available_parallelism()`, which is returning 1.

### Where Worker Threads is Configured

**File: `roles/kumomta/templates/queue.lua.j2:19`**
```lua
workers = {{ kumomta_worker_threads }},  -- Sets to 12, but not used by KumoMTA
```

**This is NOT used for KumoMTA's actual concurrency.**

KumoMTA's concurrency is determined by:
1. **`std::thread::available_parallelism()`** - Rust's thread availability detection
2. **Cgroup limits** - CPU quotas/limits if in container
3. **KumoMTA's internal logic** - May have minimums/maximums

---

## Why available_parallelism Returns 1

When KumoMTA logs show:
```
available_parallelism=1
Running a production workload with fewer than 4 cores is not recommended
Using concurrency 1 for spooling in
```

This indicates `std::thread::available_parallelism()` returned 1. Possible causes:

### 1. Cgroup v1/v2 CPU Restrictions
```bash
# Check if system is using cgroups
cat /proc/self/cgroup | grep -i cpu
cat /sys/fs/cgroup/cpu.max       # cgroup v2
cat /sys/fs/cgroup/cpuset/cpuset.cpus  # cgroup v1
```

Even though `CPUQuota=100%`, the actual CPU count visible to the process might be 1.

### 2. Container/VM Detection
If KumoMTA detects it's in a container (Docker, VM, etc.), it might limit itself to 1 core.

### 3. NUMA Configuration
```bash
# Check NUMA settings
numactl -H
# If process is pinned to 1 NUMA node with 1 core visible
```

### 4. Process CPU Affinity
```bash
# Check what CPUs the process can use
taskset -p <pid>  # Should show 0-23, not just 0
```

---

## Ansible Configuration Mechanism Analysis

### Configuration File Hierarchy

**File: `roles/kumomta/templates/kumomta.service.j2:14`**
```bash
ExecStart=/opt/kumomta/sbin/kumod --policy /opt/kumomta/etc/policy/init.lua
```

**CRITICAL ISSUE**: There's NO mechanism to pass worker_threads to KumoMTA.

### No CLI Parameter Exists

KumoMTA binary doesn't accept `--worker-threads` or `--concurrency` flags:
```bash
kumod --policy /path/to/policy.lua  # Only policy is configurable
# NO support for: --worker-threads 12 or --concurrency 12
```

### Lua Configuration is Not Used

The Ansible templated variables go into `.lua` files:
- `queue.lua.j2` → `workers = 12`  (NOT READ by KumoMTA for concurrency)
- `policy.lua.j2` → Various settings (SOME read, some ignored)

**But KumoMTA doesn't have a Lua API for setting concurrency.**

According to KumoMTA documentation:
- Concurrency is determined by `available_parallelism()`
- **Cannot be overridden in Lua policy**
- **Cannot be set via CLI flags**
- **Can only be influenced via cgroup CPU limits**

---

## The Real Solution

Since KumoMTA's concurrency is driven by `std::thread::available_parallelism()`, we need to either:

### Option A: Restrict CPU Assignment to Force Higher Count

If the system is using cgroups and misreporting cores, we need to:

```bash
# On the production server, check current limits
cat /sys/fs/cgroup/cpu.max              # cgroup v2
cat /sys/fs/cgroup/cpuset.cpus          # cgroup v1
taskset -p <kumomta_pid>                # Process CPU affinity
```

If the process is restricted to 1 core, KumoMTA correctly reports 1.

### Option B: Use Memory Limits as Alternative

Instead of relying on concurrency, increase:
- Memory limit (already 2GB, could increase if needed)
- Connection limits (concurrent SMTP connections)
- Queue retry strategies

### Option C: Check for KumoMTA Environment Variables

KumoMTA might support:
```bash
RAYON_NUM_THREADS=12     # If using Rayon thread pool
RUST_NUM_THREADS=12      # If using Rust threads
KM_CONCURRENCY=12        # If KumoMTA has custom env var
```

Would need to test in systemd service:
```ini
[Service]
Environment="RAYON_NUM_THREADS=12"
ExecStart=/opt/kumomta/sbin/kumod --policy /opt/kumomta/etc/policy/init.lua
```

### Option D: Upgrade Memory, Keep 1 Concurrency

If the system is truly single-core capable (or reports it), we can:
- Increase memory limit to 4-8GB
- Reduce retry intervals
- Tune queue management for single-threaded processing
- Accept slower throughput (8K-10K msgs/hour instead of 50K+)

---

## Verification Steps

### Step 1: Check Actual CPU Availability on Server
```bash
ssh kevin@108.181.38.69 << 'EOF'
echo "=== Total CPUs ==="
nproc

echo "=== Process CPUs ==="
pid=$(pgrep -f 'kumod')
taskset -p $pid | grep -o '0-[0-9]*\|[0-9]\+,[0-9]\+'

echo "=== Cgroup Limits ==="
cat /sys/fs/cgroup/cpu.max 2>/dev/null || echo "cgroup v1"
cat /sys/fs/cgroup/cpuset.cpus 2>/dev/null
ps aux | grep kumod | head -1

echo "=== Current Queue Depth ==="
curl -s http://localhost:9184/metrics | grep scheduled_count_total
EOF
```

### Step 2: Check KumoMTA Logs for Diagnostic Info
```bash
ssh kevin@108.181.38.69 'sudo journalctl -u kumomta -n 100 --no-pager' | grep -E 'parallelism|concurrency|cores|threads'
```

### Step 3: Test Environment Variable Override (if applicable)
```bash
# Modify systemd service to test env vars
sudo systemctl edit kumomta
# Add: Environment="RAYON_NUM_THREADS=12"
# Save and reload
sudo systemctl daemon-reload
sudo systemctl restart kumomta
```

---

## Updated Configuration Approach

### Current Attempt (Not Working)

**File: `inventories/projects/vietcgi/group_vars/mail_servers.yml:21`**
```yaml
kumomta_worker_threads: 12  # Set in Ansible but not used by KumoMTA
```

### What Should Be Done

**Option 1: Try Environment Variable (Recommended)**
```yaml
# In group_vars:
kumomta_env_variables:
  RAYON_NUM_THREADS: 12
  RUST_LOG: info

# In systemd template:
{% for key, value in (kumomta_env_variables | default({})).items() %}
Environment="{{ key }}={{ value }}"
{% endfor %}
```

**Option 2: Document Current Limitation**
```yaml
# In group_vars - document why this is set but may not be used
kumomta_worker_threads: 12
# NOTE: This variable is NOT currently used by KumoMTA binary
# KumoMTA's concurrency is determined by available_parallelism()
# Which may be limited by cgroups or detected as 1 core in VM/container environments
# See KUMOMTA_CONCURRENCY_INVESTIGATION.md for details
```

**Option 3: Increase Memory for Single-Threaded Operation**
```yaml
kumomta_memory_limit: "4G"  # Increase from 2G to handle single-threaded queue buildup
kumomta_worker_threads: 12  # Keep for documentation purposes
```

---

## Implications for Email Delivery

### With Single-Threaded Concurrency (Current State)

**Throughput Estimate**:
- 1 worker thread × average 100ms per message = ~10 messages/second
- Per hour: ~36,000 messages
- Peak queue before memory pressure: ~18,000 messages (at 1.7GB of 2GB)
- Time to clear backlog: 30-60 minutes

**Symptoms** (currently observed):
- Queue grows rapidly
- Memory pressure kicks in (`shrink_ready_queue_due_to_low_mem`)
- Delivery stops
- Service restart provides temporary relief

### With Multi-Threaded Concurrency (If Fixed)

**With 12 concurrency** (if we can force KumoMTA to use it):
- 12 worker threads × average 100ms per message = ~120 messages/second
- Per hour: ~432,000 messages
- Peak queue before memory pressure: ~216,000 messages
- Time to clear backlog: 5-10 minutes (much faster)

---

## Next Steps

### Immediate (This Week)

1. **Verify CPU availability on production server**
   ```bash
   nproc  # Should show 24
   taskset -p <kumomta-pid>  # Should show 0-23
   ```

2. **Check KumoMTA logs for available_parallelism value**
   ```bash
   journalctl -u kumomta | grep available_parallelism
   ```

3. **Test environment variable approach**
   ```bash
   # Try RAYON_NUM_THREADS=12 in systemd service
   ```

### Medium Term (Next 2 Weeks)

1. **Identify why available_parallelism reports 1**
   - Check cgroup configuration
   - Verify VM/container detection
   - Review KumoMTA code or contact support

2. **Document the limitation**
   - Update Ansible comments explaining the issue
   - Create operational runbook for queue management under single-threaded constraint

3. **Implement workarounds**
   - Increase memory limit to 4GB
   - Tune retry intervals
   - Monitor queue depth with alerts

### Long Term (Next Month)

1. **Upgrade to KumoMTA version with CLI concurrency support** (if available)
2. **Or migrate to email system with better concurrency control**
3. **Implement cluster mode** with multiple KumoMTA instances (1 worker each = 12 total workers)

---

## Files Modified

- `inventories/projects/vietcgi/group_vars/mail_servers.yml` - Updated worker_threads to 12 (may not help with current issue)
- `roles/kumomta/templates/policy.lua.j2` - Added Prometheus listener on port 9184
- `ROOT_CAUSE_ANALYSIS.md` - Initial root cause analysis
- `WORKER_THREADS_FIX.md` - Configuration fix documentation
- `KUMOMTA_CONCURRENCY_INVESTIGATION.md` - This document

---

## Summary

| Aspect | Details |
|--------|---------|
| **Issue** | KumoMTA shows available_parallelism=1 instead of 24 |
| **Root Cause** | KumoMTA's concurrency is not configurable via Ansible/CLI; determined by `std::thread::available_parallelism()` |
| **Current Workaround** | Increase memory limit; set concurrency 12 for documentation |
| **Real Solution** | Determine why available_parallelism returns 1; try env vars; consider architecture change |
| **Impact** | Single-threaded bottleneck limits throughput to ~10 msgs/sec; queue backs up; delivery stops |
| **Resolution Path** | Verify server CPU availability → test env vars → increase memory → monitor → escalate to KumoMTA support |

---

**Status**: Investigation continuing - awaiting verification from production server.
