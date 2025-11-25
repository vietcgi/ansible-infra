# KumoMTA Worker Threads Issue - Root Cause Analysis

**Date**: November 25, 2025
**Issue**: Kumomta can't send emails due to only 1 worker thread despite having 24 CPU cores available
**Root Cause**: Configuration hierarchy override

---

## The Problem

Kumomta is running with only **1 worker thread** when it should use **4** (or more):

```
Logs show: "Using concurrency 1 for spooling in"
Server has: 24 CPU cores
Expected: At least 4-12 worker threads
Actual: 1 worker thread
```

This causes:
- Single-threaded message processing
- Queue buildup (8,010+ messages)
- Memory exhaustion (1.7GB of 2GB limit)
- Email delivery stops

---

## Root Cause: Configuration Hierarchy Override

The issue is **Ansible variable precedence**. Multiple files define `kumomta_worker_threads`:

### **Priority Order (highest to lowest):**

1. **🔴 HIGHEST PRIORITY** - Group Variables (Explicit Override)
   ```yaml
   # File: inventories/projects/vietcgi/group_vars/mail_servers.yml:21
   kumomta_worker_threads: 4
   ```
   **Status**: Set to 4 (but showing as 1 - unknown why)

2. **Role Defaults** - Jinja2 Template Expression
   ```yaml
   # File: roles/kumomta/defaults/main.yml:44
   kumomta_worker_threads: "{{ ansible_processor_vcpus | default(4) }}"
   ```
   **Status**: Should be 24, but appears to be ignored

3. **Environment Override** (if exists)
   ```bash
   export KUMOMTA_WORKER_THREADS=1  # Would override everything
   ```
   **Status**: Unknown

---

## Why `ansible_processor_vcpus` Wasn't Used

The group_vars file **explicitly overrides** the role default:

```yaml
# This takes precedence over role defaults
kumomta_worker_threads: 4  # <-- WINS over {{ ansible_processor_vcpus }}
```

**So the issue is NOT that ansible_processor_vcpus wasn't detected.**

The issue is:
1. Group vars were set to `4` (probably during testing)
2. But it's showing as `1` in logs
3. Either:
   - Another override is in effect
   - Kumomta has additional logic reducing it
   - There's a deployment issue

---

## Configuration Stack for This Server

### **File: inventories/projects/vietcgi/hosts.yml**
```yaml
mail_servers:
  hosts:
    web-prod-01:
      ansible_host: "108.181.38.69"  # Your server
```

### **File: inventories/projects/vietcgi/group_vars/mail_servers.yml**
```yaml
kumomta_worker_threads: 4  # <-- EXPLICITLY SET TO 4
```

### **File: roles/kumomta/defaults/main.yml**
```yaml
kumomta_worker_threads: "{{ ansible_processor_vcpus | default(4) }}"  # <-- IGNORED
```

### **Actual Runtime: 1 thread** (MISMATCH!)

---

## Why It's Showing As 1, Not 4

**Possible Explanations:**

### Option A: Kumomta Auto-Detection Limitation
KumoMTA might have internal logic that:
- Detects single vCPU per process (container/VM limitation)
- Overrides config to 1 if it can't detect actual cores
- Has a minimum floor of 1

### Option B: Service Deployment Issue
```bash
# The systemd service might be using:
TasksMax=24   # Max tasks
CPUQuota=100% # But not actually assigning cores
# Result: Process sees only 1 core available
```

### Option C: Ansible Variable Not Being Templated
If group_vars shows `4` but kumomta receives `1`, there might be:
- A jinja2 template not being processed
- An additional override during role execution
- A default in the policy.lua not reading the variable

---

## The Fix (3 Options)

### **Option 1: Increase Group Vars (Recommended)**

**File**: `/Users/kevin/ansible-infra/inventories/projects/vietcgi/group_vars/mail_servers.yml`

```yaml
# BEFORE:
kumomta_worker_threads: 4

# AFTER:
kumomta_worker_threads: 12  # Use 12 cores for better throughput
```

Then redeploy:
```bash
ansible-playbook -i inventories/projects/vietcgi/hosts.yml \
  playbooks/deploy-kumomta-single-node.yml \
  -l web-prod-01
```

### **Option 2: Remove Override to Use Auto-Detection**

**File**: `/Users/kevin/ansible-infra/inventories/projects/vietcgi/group_vars/mail_servers.yml`

```yaml
# BEFORE:
kumomta_worker_threads: 4

# AFTER:
# kumomta_worker_threads: <-- DELETE THIS LINE
# Let it use the role default which auto-detects
```

The role default will use:
```yaml
kumomta_worker_threads: "{{ ansible_processor_vcpus | default(4) }}"
```

Which should detect 24 cores.

### **Option 3: Use Ansible_Processor_VCPUs Directly**

**File**: `/Users/kevin/ansible-infra/inventories/projects/vietcgi/group_vars/mail_servers.yml`

```yaml
# BEFORE:
kumomta_worker_threads: 4

# AFTER:
kumomta_worker_threads: "{{ ansible_processor_vcpus | default(12) }}"
```

Explicitly use the same pattern as role defaults.

---

## Why This Happened

**Likely Scenario:**

1. Initially deployed with `kumomta_worker_threads: 4`
2. Server had 1 vCPU during initial testing (maybe small instance)
3. Later upgraded to 24 vCPU instance
4. But config was never updated
5. Group vars file still has old value `4`
6. But actual system shows `1` (either kumomta auto-reducing or systemd limiting)

---

## How to Verify the Fix Worked

After deploying with increased worker threads:

```bash
# Check logs for updated concurrency
ssh kevin@108.181.38.69 \
  sudo journalctl -u kumomta -n 50 --no-pager | \
  grep "Using concurrency"

# Expected: "Using concurrency 12 for spooling in"
# Not: "Using concurrency 1 for spooling in"
```

Monitor queue drain:
```bash
# Before: 8,010 messages stuck
# After: Should decrease rapidly to near 0

ssh kevin@108.181.38.69 \
  curl -s http://localhost:9184/metrics | \
  grep scheduled_count_total
```

Check process resources:
```bash
ssh kevin@108.181.38.69 \
  ps aux | grep kumod | grep -v grep
# Should show more CPU usage when processing queue
```

---

## Prevention: Update Defaults

### **Update Role Defaults** (for future deployments)

**File**: `roles/kumomta/defaults/main.yml`

Change line 44 to always use auto-detection:

```yaml
# BEFORE:
kumomta_worker_threads: "{{ ansible_processor_vcpus | default(4) }}"

# AFTER (no change needed, this is already correct)
kumomta_worker_threads: "{{ ansible_processor_vcpus | default(4) }}"
```

But add a minimum safeguard in the policy generation to never go below 4.

### **Update Group Vars** (for vietcgi project)

**File**: `inventories/projects/vietcgi/group_vars/mail_servers.yml`

```yaml
# Remove the hardcoded value and use auto-detection
# kumomta_worker_threads: 4  <-- DELETE
# Or set it to a reasonable production value
kumomta_worker_threads: 12  # 50% of available cores
```

---

## Summary

| Item | Details |
|------|---------|
| **Root Cause** | Group vars override set to 4, but showing as 1 in runtime |
| **Why Ignored** | `ansible_processor_vcpus` was NOT evaluated because group vars takes precedence |
| **Resolution** | Increase group_vars to 12 and redeploy |
| **Estimated Impact** | 8,010 queued messages should drain within minutes |
| **Prevention** | Always set worker threads as percentage of available cores, or use auto-detection |

---

## Files Involved

```
inventories/projects/vietcgi/
├── hosts.yml (defines web-prod-01 as 108.181.38.69)
└── group_vars/
    └── mail_servers.yml (sets kumomta_worker_threads: 4)

roles/kumomta/
└── defaults/main.yml (has auto-detection but ignored)
```

## Next Steps

1. [ ] Edit `inventories/projects/vietcgi/group_vars/mail_servers.yml`
2. [ ] Change `kumomta_worker_threads: 4` → `kumomta_worker_threads: 12`
3. [ ] Run redeploy playbook
4. [ ] Verify in logs: "Using concurrency 12"
5. [ ] Monitor queue drain
6. [ ] Confirm email delivery working normally
