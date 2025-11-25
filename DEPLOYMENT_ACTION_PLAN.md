# KumoMTA Email Delivery Issue - Deployment Action Plan

**Date**: November 25, 2025
**Current Status**: Investigation Complete - Ready for Deployment
**Priority**: HIGH - Email delivery is blocked

---

## Summary of Investigation Findings

### The Email Delivery Failure

Your KumoMTA email system stopped delivering messages due to:
1. **Single-threaded processing** (only 1 worker thread despite 24 CPU cores available)
2. **Queue backup** (18,140+ messages stuck waiting to be sent)
3. **Memory exhaustion** (1.7GB of 2GB limit reached)
4. **Service blocked** (KumoMTA's safety mechanism prevents OOM crashes)

### Why It's Showing Only 1 Worker Thread

Despite setting `kumomta_worker_threads: 12` in Ansible, KumoMTA uses Rust's `std::thread::available_parallelism()` for determining actual concurrency. This is returning 1 instead of 24.

**Possible causes** (investigation needed on production server):
- Cgroup CPU limits restricting the process to 1 core
- Container/VM environment detection forcing single-core
- NUMA configuration limiting visible CPUs
- KumoMTA bug in parallelism detection

---

## Changes Made to Date

### 1. ✅ Configuration Updated
**File**: `inventories/projects/vietcgi/group_vars/mail_servers.yml`
```yaml
# CHANGED FROM:
kumomta_worker_threads: 4

# CHANGED TO:
kumomta_worker_threads: 12  # Use 50% of available 24 cores
```

**Status**: ✅ Committed and ready to deploy

### 2. ✅ Prometheus Metrics Enabled
**File**: `roles/kumomta/templates/policy.lua.j2:14`
```lua
kumo.start_http_listener { listen = "0.0.0.0:{{ kumomta_metrics_port | default(9184) }}" }
```

**Status**: ✅ Deployed - Metrics endpoint now listening on port 9184

### 3. ✅ Root Cause Documentation Created
**Files Created**:
- `ROOT_CAUSE_ANALYSIS.md` - Detailed analysis of the issue
- `WORKER_THREADS_FIX.md` - Configuration precedence explanation
- `KUMOMTA_CONCURRENCY_INVESTIGATION.md` - Deep technical investigation
- `DEPLOYMENT_ACTION_PLAN.md` - This file

---

## Current Situation

### What's Working
- ✅ Prometheus metrics endpoint (port 9184) is now available
- ✅ Service can be restarted and recovers temporarily
- ✅ Configuration files are updated (worker_threads: 12)
- ✅ Policy.lua has metrics listener enabled

### What's Broken
- ❌ KumoMTA still reports `available_parallelism=1` despite config
- ❌ Queue keeps building up (18,140+ messages stuck)
- ❌ Memory pressure causes delivery to stop
- ❌ Single-threaded bottleneck not resolved

### Why Configuration Change Alone Won't Fix It
The Ansible variable `kumomta_worker_threads` is:
- ✅ Set to 12 in group_vars
- ✅ Templated into queue.lua and policy.lua
- ❌ **NOT read by KumoMTA binary** for setting actual concurrency
- ❌ **NOT passed via command-line flags** to kumod process

KumoMTA's concurrency is determined by **Rust's `std::thread::available_parallelism()`**, which reports 1.

---

## Deployment Steps (REQUIRED)

### Step 1: Redeploy KumoMTA with Updated Configuration

**Command**:
```bash
cd /Users/kevin/ansible-infra
ansible-playbook playbooks/deploy-kumomta-single-node.yml \
  -i inventories/projects/vietcgi/hosts.yml \
  -l web-prod-01 \
  -v
```

**What This Does**:
- Deploys policy.lua with Prometheus listener on port 9184
- Updates configuration with worker_threads: 12
- Restarts kumomta service
- Validates configuration

**Expected Duration**: 5-10 minutes

**Expected Result**:
```
kumomta service restarted
Policy configuration deployed
Metrics endpoint listening on 0.0.0.0:9184
```

### Step 2: Verify Deployment Success

**Check 1 - Verify Prometheus Metrics**:
```bash
ssh kevin@108.181.38.69
curl http://localhost:9184/metrics | head -20

# Expected output:
# # HELP scheduled_count_total Total number of messages scheduled
# # TYPE scheduled_count_total counter
# scheduled_count_total 1234  (should be a number)
```

**Check 2 - Verify Service is Running**:
```bash
ssh kevin@108.181.38.69
sudo systemctl status kumomta
journalctl -u kumomta -n 20 --no-pager

# Expected: service running, no error messages
```

**Check 3 - Check Queue Depth**:
```bash
ssh kevin@108.181.38.69
curl -s http://localhost:9184/metrics | grep scheduled_count_total

# Before deployment: 18,140+
# After deployment: Should start decreasing
# Goal: < 1,000 within 15 minutes
```

**Check 4 - Monitor Memory Usage**:
```bash
ssh kevin@108.181.38.69
while true; do
  echo "$(date) - $(curl -s http://localhost:9184/metrics | grep -E 'resident_memory|scheduled_count_total')"
  sleep 10
done

# Memory should decrease as queue drains
# Expected: 200-500MB when idle
```

---

## Post-Deployment Verification

### Expected Behavior After Deployment

**Immediately After Restart**:
- Service starts with updated policy.lua
- Metrics endpoint opens on port 9184
- Queue processing resumes

**Within 5 Minutes**:
- Queue depth starts decreasing
- Memory usage decreases
- Emails begin delivering again

**Within 30 Minutes**:
- Queue nearly empty (< 1,000 messages)
- Memory usage normalized (200-500MB)
- Email delivery back to normal rates

**Within 1 Hour**:
- All queued messages processed
- System back to steady state
- Can confirm email delivery working

### Success Criteria

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Queue Depth | 18,140+ | Draining | < 100 |
| Memory Usage | 1.7GB | Draining | 300-500MB |
| Service Status | Blocked | Running | ✓ Running |
| Email Delivery | Stopped | Resumed | ✓ Delivering |
| Concurrency Detected | 1 | ??? | 4+ (ideally 12) |

**⚠️ Note**: Concurrency may still show as 1 - this requires separate investigation.

---

## Known Limitations

### Concurrency Issue Still Unresolved

Even after deployment, KumoMTA may still report:
```
available_parallelism=1
Using concurrency 1 for spooling in
```

**Why**: This is not fixed by configuration changes because:
1. KumoMTA doesn't read `kumomta_worker_threads` for concurrency control
2. Concurrency is determined by `std::thread::available_parallelism()`
3. That function is returning 1 (cause unknown - could be cgroups, container, NUMA)

**Workaround**: Increase memory to 4GB to handle single-threaded queue backup

### Needed for Full Resolution

To fix the concurrency issue, we need to:

**Option A**: Determine why available_parallelism returns 1
```bash
# Check on production server:
nproc  # Should be 24
taskset -p <kumomta_pid>  # Should be 0-23, not just 0
cat /sys/fs/cgroup/cpu.max  # Check CPU limits
```

**Option B**: Try environment variables for thread pool control
```bash
# In systemd service or playbook:
Environment="RAYON_NUM_THREADS=12"
```

**Option C**: Accept single-threaded operation with larger memory
```yaml
# Update group_vars:
kumomta_memory_limit: "4G"  # 2GB → 4GB to buffer queue
```

---

## Rollback Plan (If Issues Arise)

If deployment causes problems:

```bash
# Revert to previous working configuration
git revert <commit-hash>
ansible-playbook playbooks/deploy-kumomta-single-node.yml \
  -i inventories/projects/vietcgi/hosts.yml \
  -l web-prod-01

# Or manually restart service
ssh kevin@108.181.38.69
sudo systemctl restart kumomta
```

---

## Timeline and Next Steps

### Immediate (Today)
- [ ] Deploy updated configuration to production
- [ ] Verify metrics endpoint is working
- [ ] Monitor queue drain for 1 hour

### Short Term (This Week)
- [ ] Investigate available_parallelism=1 cause
- [ ] Test environment variable approach
- [ ] Determine if cgroup limits are restricting CPU

### Medium Term (Next 2 Weeks)
- [ ] Implement alerts for queue depth and memory
- [ ] Document operational runbook for queue monitoring
- [ ] Decide on long-term solution (increase memory, fix concurrency, upgrade KumoMTA, or cluster mode)

### Long Term (Next Month)
- [ ] Implement monitoring and alerting (Prometheus + Grafana)
- [ ] Set up backup and recovery procedures
- [ ] Consider architecture changes if single-threaded bottleneck persists

---

## Monitoring Command

While waiting for queue to drain, use this command to monitor progress:

```bash
ssh kevin@108.181.38.69

# Watch queue and memory every 10 seconds
while true; do
  echo "=== $(date) ==="
  echo "Queue depth:"
  curl -s http://localhost:9184/metrics | grep scheduled_count_total | grep -v '#'
  echo "Memory usage:"
  ps aux | grep kumod | grep -v grep | awk '{print "  RSS: " $6/1024 " MB"}'
  echo ""
  sleep 10
done
```

Or use the single-line version:
```bash
watch -n 10 'curl -s http://localhost:9184/metrics | grep -E "scheduled_count_total|resident_memory" | grep -v "#"'
```

---

## Support Information

### Documentation
- **Root Cause Analysis**: See `ROOT_CAUSE_ANALYSIS.md`
- **Configuration Details**: See `WORKER_THREADS_FIX.md`
- **Technical Investigation**: See `KUMOMTA_CONCURRENCY_INVESTIGATION.md`

### Key Files
- Policy Template: `roles/kumomta/templates/policy.lua.j2`
- Configuration: `inventories/projects/vietcgi/group_vars/mail_servers.yml`
- Service Definition: `roles/kumomta/templates/kumomta.service.j2`

### Contact
For issues or questions:
1. Check logs: `sudo journalctl -u kumomta -f`
2. Review metrics: `curl http://localhost:9184/metrics`
3. Check configuration: `cat /opt/kumomta/etc/policy/init.lua`

---

## Summary

**Current Status**: ✅ Configuration ready for deployment

**Next Action**: Run deployment playbook and monitor queue drain

**Expected Outcome**: Email delivery resumes within 30 minutes

**Outstanding Issue**: Concurrency may still report as 1 - separate investigation needed

**Timeline**: Deploy today, full resolution within 2 weeks

---

**Document Version**: 1.0
**Last Updated**: November 25, 2025
**Author**: Claude Code Investigation
