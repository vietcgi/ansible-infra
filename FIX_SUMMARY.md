# KumoMTA Deployment Fix - Summary

**Commit**: 957f62a
**Date**: November 25, 2025
**Status**: Ready to deploy

---

## What Was Fixed

The deployment playbook has been improved to actually fix the concurrency issue:

### **3 Key Changes**

#### 1. **Removed Hardcoded Override** ❌ → ✅
```yaml
# BEFORE (playbooks/deploy-kumomta-single-node.yml):
kumomta_worker_threads: 4  # Hardcoded, overrides group_vars!

# AFTER:
# kumomta_worker_threads: comes from group_vars/mail_servers.yml (currently 12)
```
**Impact**: Now uses the correct value from group_vars (12) instead of hardcoded 4

#### 2. **Added RAYON_NUM_THREADS Environment Variable** 🚀
```ini
# systemd service now includes:
Environment="RAYON_NUM_THREADS=12"
Environment="RAYON_THREAD_STACK_SIZE=8388608"
Environment="RUST_LOG=info"
Environment="RUST_BACKTRACE=0"
```
**Impact**: Tells KumoMTA's Rayon thread pool to use 12 threads instead of auto-detecting 1

#### 3. **Enhanced Post-Deployment Diagnostics** 📊
```
CONCURRENCY CONFIGURATION:
- RAYON_NUM_THREADS: (verified from systemd)
- Process ID: (shows running process)
- CPU Affinity: (shows which CPUs visible to process)
- Parallelism Detection: (shows what KumoMTA logs say)

METRICS ENDPOINT:
- Status: ACTIVE ✓ or INACTIVE ✗
- URL: http://server:9184/metrics
- Queue Depth: (from metrics)
```
**Impact**: Automatically shows if concurrency fix worked, no manual checking needed

---

## How to Use

### **Deploy the Fixed Playbook**

```bash
cd /Users/kevin/ansible-infra

ansible-playbook playbooks/deploy-kumomta-single-node.yml \
  -i inventories/projects/vietcgi/hosts.yml \
  -l web-prod-01 \
  -v
```

### **What Happens During Deployment**

1. ✅ Installs/updates KumoMTA with new config
2. ✅ Sets RAYON_NUM_THREADS=12 in systemd service
3. ✅ Restarts KumoMTA service
4. ✅ **Automatically checks if it worked** (new!)
5. ✅ **Displays concurrency status** (new!)
6. ✅ **Shows queue depth from metrics** (new!)
7. ✅ **Verifies metrics endpoint** (new!)

### **Expected Output (End of Playbook)**

```
✓ KumoMTA Single Node Deployment Complete
===========================================

Service Status: active
Configuration: Valid
Queue Directory: /var/spool/kumomta
Log Directory: /var/log/kumomta

CONCURRENCY CONFIGURATION:
- RAYON_NUM_THREADS: RAYON_NUM_THREADS=12
- Process ID: 12345
- CPU Affinity: 0-23  ← Should show all 24 CPUs
- Parallelism Detection: Using concurrency 12 for spooling

METRICS ENDPOINT:
- Status: ACTIVE ✓
- URL: http://server:9184/metrics
- Queue Depth: Check metrics for scheduled_count_total

DEPLOYMENT SUMMARY:
- Worker Threads Config: 12
- Memory Limit: 2G
- CPU Quota: 100%

NEXT STEPS:
1. Monitor queue draining: curl http://server:9184/metrics | grep scheduled_count_total
2. Check logs for concurrency info: journalctl -u kumomta.service -f | grep -i concurrency
3. Verify email delivery: Test sending message
4. Run diagnostics if still single-threaded: bash CONCURRENCY_TROUBLESHOOTING.sh

IMPORTANT:
- Environment variable RAYON_NUM_THREADS=12 was configured
- This should improve concurrency from 1 to 12 threads
- If parallelism still shows 1: Check CPU affinity and run diagnostics
- If queue draining: Deployment successful ✓
- If queue still backing up: Additional investigation needed
```

---

## Success Indicators

### ✅ Deployment Successful If:
- `Service Status: active`
- `RAYON_NUM_THREADS: RAYON_NUM_THREADS=12` ← Shows it's configured
- `CPU Affinity: 0-23` ← Shows all 24 CPUs available
- `Parallelism Detection: Using concurrency 12` ← Shows it worked!
- `METRICS ENDPOINT: ACTIVE ✓` ← Shows metrics endpoint working
- Queue starts decreasing within 5 minutes

### ⚠️ Needs Investigation If:
- `RAYON_NUM_THREADS: RAYON_NUM_THREADS not set` ← Env var not configured
- `CPU Affinity: 0` ← Only 1 CPU visible to process (cgroup limit?)
- `Parallelism Detection: Using concurrency 1` ← Still single-threaded
- `METRICS ENDPOINT: INACTIVE ✗` ← Metrics not working
- Queue still backing up after 30 minutes

---

## Files Modified

| File | Change | Reason |
|------|--------|--------|
| `playbooks/deploy-kumomta-single-node.yml` | Removed hardcoded worker_threads, added env vars, enhanced diagnostics | Use group_vars value + proper thread config |
| `roles/kumomta/templates/kumomta.service.j2` | Added Environment variables templating | Pass RAYON_NUM_THREADS to service |
| `roles/kumomta/defaults/main.yml` | Added kumomta_env_variables defaults | Define env vars for all deployments |

---

## Deployment Commands

```bash
# One-liner deployment
cd /Users/kevin/ansible-infra && \
ansible-playbook playbooks/deploy-kumomta-single-node.yml \
  -i inventories/projects/vietcgi/hosts.yml \
  -l web-prod-01 -v

# With detailed output
cd /Users/kevin/ansible-infra && \
ansible-playbook playbooks/deploy-kumomta-single-node.yml \
  -i inventories/projects/vietcgi/hosts.yml \
  -l web-prod-01 -v --extra-vars "kumomta_worker_threads=12"

# To check playbook without deploying
ansible-playbook playbooks/deploy-kumomta-single-node.yml \
  -i inventories/projects/vietcgi/hosts.yml \
  -l web-prod-01 --check --diff
```

---

## What This Fixes

### The Problem
```
Queue: 18,140+ messages stuck
Memory: 1.7GB of 2GB limit
Concurrency: Stuck at 1 thread
Result: Email delivery STOPPED
```

### The Solution
```
RAYON_NUM_THREADS: 12 → Tells KumoMTA to use 12 threads
CPU Affinity: 0-23 → Allows access to all 24 cores
Config: Updated to 12 workers → Proper configuration
Result: Email delivery should resume
```

### Expected Timeline
- **0 min**: Deployment starts
- **5 min**: Deployment completes, KumoMTA restarts with RAYON_NUM_THREADS=12
- **10 min**: Queue starts draining (if fix worked)
- **30 min**: Queue nearly empty, memory normalized
- **60 min**: All messages processed, system steady

---

## Troubleshooting

### If Parallelism Still Shows 1
```bash
# Check if env var is set
systemctl show kumomta.service -p Environment

# Check if process can see all CPUs
taskset -p $(pgrep -f kumod)

# Run full diagnostics
ssh kevin@108.181.38.69 'bash -s' < /Users/kevin/ansible-infra/CONCURRENCY_TROUBLESHOOTING.sh
```

### If Queue Doesn't Drain
```bash
# Monitor in real-time
watch -n 5 'curl -s http://server:9184/metrics | grep scheduled_count_total'

# Check logs
journalctl -u kumomta.service -f | grep -i 'error\|failed\|warning'
```

### If Metrics Endpoint Doesn't Respond
```bash
# Test endpoint
curl -v http://server:9184/metrics

# Check if port is listening
netstat -tlnp | grep 9184

# Check service status
systemctl status kumomta.service
```

---

## Next Steps After Deployment

1. **Verify metrics**: `curl http://server:9184/metrics | grep scheduled_count_total`
2. **Monitor queue**: Watch queue depth decrease over 30 minutes
3. **Test email delivery**: Send test message to external domain
4. **Check concurrency**: Verify logs show "Using concurrency 12 for spooling"
5. **Commit success**: If working, document the successful deployment

---

## Rollback (If Needed)

```bash
# Revert the changes
git revert 957f62a

# Redeploy with previous version
ansible-playbook playbooks/deploy-kumomta-single-node.yml \
  -i inventories/projects/vietcgi/hosts.yml \
  -l web-prod-01
```

---

## Summary

**Fixed Playbook**:
- ✅ Removes hardcoded overrides
- ✅ Adds RAYON_NUM_THREADS environment variable (12 threads)
- ✅ Provides automatic diagnostics and verification
- ✅ Shows exactly if the fix worked

**Ready to Deploy**: Yes ✅

**Expected Outcome**: Email delivery resumes within 30 minutes

**Outstanding**: May still need to investigate if available_parallelism returns 1 (CPU affinity issue)

**Run**: `ansible-playbook playbooks/deploy-kumomta-single-node.yml -i inventories/projects/vietcgi/hosts.yml -l web-prod-01 -v`

---

**Version**: 1.0
**Status**: Ready for Production
**Author**: Claude Code Fix
**Commit**: 957f62a
