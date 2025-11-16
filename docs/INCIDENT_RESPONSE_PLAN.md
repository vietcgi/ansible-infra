# Incident Response Plan

## Overview

This document outlines procedures for rapid detection, response, and resolution of incidents affecting ansible-infra infrastructure. The plan minimizes Mean Time to Recovery (MTTR) and ensures coordinated incident management.

---

## Incident Classification

### Critical (Severity 1)
- **Impact**: Complete service outage or imminent data loss
- **Users affected**: All or majority
- **Response time**: Immediate (< 5 minutes)
- **Escalation**: Full team + management
- **Examples**: Complete infrastructure failure, active security breach

### High (Severity 2)
- **Impact**: Partial service unavailability
- **Users affected**: Multiple users or critical features
- **Response time**: Urgent (< 30 minutes)
- **Escalation**: On-call + team lead
- **Examples**: Database down, single host failure, key feature broken

### Medium (Severity 3)
- **Impact**: Service degradation
- **Users affected**: Some users, non-critical features
- **Response time**: Standard (< 2 hours)
- **Escalation**: On-call engineer
- **Examples**: Slow performance, minor feature bug, configuration issue

### Low (Severity 4)
- **Impact**: Minimal impact
- **Users affected**: Few or no active users
- **Response time**: Normal (< 24 hours)
- **Escalation**: None required
- **Examples**: Documentation errors, minor UI issues, feature requests

---

## Incident Detection

### Automated Monitoring

**1. Prometheus Alerts**
```yaml
groups:
  - name: critical
    interval: 30s
    rules:
      - alert: HostDown
        expr: up{job="ansible"} == 0
        for: 1m
        severity: critical

      - alert: AnsiblePlaybookFailure
        expr: rate(ansible_plays_failed[5m]) > 0
        severity: high

      - alert: HighCPUUsage
        expr: node_cpu{mode="idle"} < 0.2
        severity: medium

      - alert: DiskSpacelow
        expr: node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.1
        severity: medium
```

**2. Log-Based Alerts**
```bash
# Monitor for critical errors in logs
grep -E "ERROR|CRITICAL|FAILED" /var/log/ansible-infra/*.log

# Count errors and alert if threshold exceeded
ERROR_COUNT=$(grep -c "ERROR" /var/log/ansible-infra/ansible.log)
if [ "$ERROR_COUNT" -gt 10 ]; then
  send_alert "ERROR_THRESHOLD_EXCEEDED"
fi
```

**3. Health Checks**
```bash
#!/bin/bash
# Health check script run every 5 minutes

# Check SSH availability
timeout 5 ssh -o ConnectTimeout=2 user@host echo "OK" || \
  ALERT "SSH_UNREACHABLE"

# Check Vault availability
curl -s -f http://localhost:8200/v1/sys/health || \
  ALERT "VAULT_UNREACHABLE"

# Check Prometheus
curl -s -f http://localhost:9090/-/healthy || \
  ALERT "PROMETHEUS_DOWN"
```

### Manual Detection

- Team member reports issue
- Customer reports service degradation
- Slack/email alert notification

---

## Incident Response Workflow

### Phase 1: Detection & Triage (0-5 minutes)

**Immediate Actions:**

1. **Alert received** (< 1 min)
   - Check if false alarm
   - Acknowledge alert in monitoring system
   - Notify on-call engineer

2. **Initial assessment** (1-3 min)
   ```bash
   # Quick checks
   ansible all -i inventories/production -m ping
   systemctl status [service_name]
   curl http://localhost:8000/health
   tail -f /var/log/ansible-infra/ansible.log
   ```

3. **Severity classification** (2-5 min)
   - Determine which severity level
   - Is immediate escalation needed?
   - Start war room if Severity 1-2

4. **Communication**
   - Notify Slack channel: `#incidents`
   - Page on-call engineer if not already notified
   - Set status page to "Investigating"

**Triage Checklist:**
- [ ] Alert confirmed (not false positive)
- [ ] Service actually affected verified
- [ ] Severity level assigned
- [ ] On-call engineer notified
- [ ] War room established (if needed)
- [ ] Incident ticket created

---

### Phase 2: Investigation (5-30 minutes)

**Incident Commander Actions:**

1. **Establish command structure**
   - Designate Incident Commander
   - Assign Investigation Lead
   - Assign Communication Lead
   - Assign Remediation Lead

2. **Gather information** (5-15 min)
   ```bash
   # System information
   uname -a
   uptime
   free -h
   df -h

   # Service status
   systemctl status ansible-infra
   systemctl status ssh
   systemctl status postgresql

   # Network connectivity
   ip link show
   ip route show
   netstat -an | grep LISTEN

   # Recent changes
   git log --oneline -10
   systemctl list-units --failed
   journalctl -xe --lines=50

   # Monitoring data
   # Check Prometheus for anomalies
   # Check Grafana dashboards
   # Review alert history
   ```

3. **Identify root cause** (10-20 min)
   - Is it infrastructure? (networking, hardware, resources)
   - Is it application? (configuration, deployment, code)
   - Is it external? (dependency, API, third-party)
   - Is it human? (accidental misconfiguration, deployment error)

4. **Document findings**
   ```
   Timeline of events:
   - 14:23: CPU alert triggered
   - 14:24: Alert acknowledged
   - 14:25: Verified high CPU on web-server-01
   - 14:26: Identified Ansible playbook running (PROVISION)
   - 14:27: Checked git log - recent change to role

   Root cause hypothesis:
   - New role configuration causing resource leak
   - Playbook consuming excessive CPU
   ```

**Investigation Checklist:**
- [ ] War room established
- [ ] Incident ticket created with details
- [ ] Root cause hypothesis identified
- [ ] Affected systems documented
- [ ] Timeline of events recorded
- [ ] Customer impact quantified

---

### Phase 3: Remediation (15-60+ minutes)

**Choose remediation strategy based on root cause:**

#### Strategy 1: Service Restart
If service has become unstable but code is correct:
```bash
# 1. Stop service
systemctl stop ansible-infra

# 2. Clear any bad state
rm -rf /tmp/ansible-*
redis-cli FLUSHDB

# 3. Start service
systemctl start ansible-infra

# 4. Verify
systemctl status ansible-infra
curl http://localhost:8000/health
```

#### Strategy 2: Configuration Rollback
If recent configuration change caused issue:
```bash
# 1. Identify bad commit
git log --oneline roles/common/tasks/

# 2. Rollback
git revert HEAD --no-edit
# or
git reset --hard HEAD~1

# 3. Re-apply configuration
ansible-playbook playbooks/configure.yml

# 4. Verify
ansible all -m ping
```

#### Strategy 3: Failover/Fallback
If primary component failed, switch to secondary:
```bash
# 1. Verify secondary ready
ansible secondary -m ping

# 2. Update DNS/load balancer
ansible-playbook playbooks/failover.yml

# 3. Monitor new configuration
watch -n 5 'curl http://localhost:8000/health'
```

#### Strategy 4: Emergency Fix
If code bug requires quick patch:
```bash
# 1. Create hotfix branch
git checkout -b hotfix/critical-bug

# 2. Make minimal fix
# Edit one file only
git add [file]

# 3. Deploy
ansible-playbook playbooks/deploy-hotfix.yml

# 4. Monitor
tail -f /var/log/ansible-infra/ansible.log
```

#### Strategy 5: Degraded Mode
If service cannot be fully restored, operate in reduced capacity:
```bash
# 1. Disable non-essential features
ansible-playbook playbooks/degraded-mode.yml

# 2. Inform customers
send_status_page_update "Operating in degraded mode"

# 3. Work on full restoration
# While service continues with limited functionality
```

**Remediation Checklist:**
- [ ] Remediation strategy chosen
- [ ] Risks assessed
- [ ] Approval obtained (if required)
- [ ] Rollback plan prepared
- [ ] Fix applied
- [ ] Verification shows improvement
- [ ] Customer notified

---

### Phase 4: Verification & Recovery (5-15 minutes)

**Confirm incident is resolved:**

```bash
#!/bin/bash
# Comprehensive verification script

echo "=== INCIDENT RECOVERY VERIFICATION ==="
echo "Time: $(date)"

# 1. Service health checks
echo ""
echo "1. Service Status:"
systemctl status ansible-infra || echo "FAILED"

# 2. API responsiveness
echo ""
echo "2. API Health:"
curl -s http://localhost:8000/health | jq .
RESPONSE_TIME=$(curl -w "%{time_total}" -o /dev/null -s http://localhost:8000/health)
echo "Response time: ${RESPONSE_TIME}s"

# 3. Database connectivity
echo ""
echo "3. Database Status:"
ansible all -i inventories/production -m command \
  -a "systemctl is-active postgresql"

# 4. Smoke tests
echo ""
echo "4. Running Smoke Tests:"
molecule verify || echo "Tests failed"

# 5. Monitoring data
echo ""
echo "5. Monitoring Dashboards:"
# Check Grafana dashboard for green status
# Check Prometheus for normal metrics

# 6. Error rates
echo ""
echo "6. Error Rates:"
curl -s 'http://prometheus:9090/api/v1/query?query=rate(requests_failed_total[5m])' | jq .

# Summary
echo ""
echo "=== VERIFICATION SUMMARY ==="
if [ $? -eq 0 ]; then
  echo "✓ All systems operational"
  echo "✓ Ready to close incident"
else
  echo "✗ Issues remain, continue remediation"
fi
```

**Verification Checklist:**
- [ ] Service responding normally
- [ ] Smoke tests passing
- [ ] No elevated error rates
- [ ] Performance normal
- [ ] Monitoring alerts cleared
- [ ] Logs show normal operation

---

### Phase 5: Communication (Ongoing)

**During Incident:**

**Update 1 (at discovery)**
```
#incidents: 🔴 INVESTIGATING - High CPU on database server
- Impact: Database queries slow
- Status: Investigating root cause
- ETA: 15 minutes
```

**Update 2 (root cause found)**
```
#incidents: 🟡 WORKING - Found root cause
- Issue: New Ansible role causing resource leak
- Impact: Database performance degraded ~40%
- Action: Rolling back configuration
- ETA: 5 minutes
```

**Update 3 (fix deployed)**
```
#incidents: 🟢 RECOVERING - Fix deployed
- Action taken: Rolled back to previous configuration
- Status: Monitoring for stability
- ETA: Full recovery 5 minutes
```

**Update 4 (resolved)**
```
#incidents: ✅ RESOLVED
- Duration: 23 minutes
- Root cause: Resource leak in new role
- Fix: Reverted configuration
- Post-incident: Will schedule analysis meeting
```

**To All Users:**
```
Service Status Update
====================
Issue: Database performance degradation
Status: RESOLVED
Duration: 23 minutes (14:23-14:46 UTC)
Impact: Queries were slow
Root Cause: Configuration change
Fix: Reverted to stable version

We apologize for the disruption. A detailed analysis will be published in our status page.
```

---

### Phase 6: Closure (< 30 minutes after resolution)

**Post-Incident Actions:**

1. **Update status page**
   - Mark incident as resolved
   - Post final status update
   - Include brief summary

2. **Close ticket**
   ```
   Incident closed at: [time]
   Duration: [total time]
   Root cause: [brief description]
   Resolution: [what was done]
   Temporary fix: [if applicable]
   Permanent fix needed: [if applicable]
   ```

3. **Notify stakeholders**
   - Email incident summary
   - Update management
   - Document financial impact

4. **Schedule post-mortem**
   - Within 24 hours of incident
   - Entire team attends
   - Focus on learning, not blame

**Closure Checklist:**
- [ ] Incident marked resolved in system
- [ ] Status page updated
- [ ] All notifications sent
- [ ] Post-mortem scheduled
- [ ] Ticket archived
- [ ] Metrics recorded

---

## Post-Mortem Process

### Scheduling

Post-mortem held within 24 hours of incident resolution:

```
Critical (P1): Same day or next morning
High (P2): Within 48 hours
Medium (P3): Within 1 week
Low (P4): As needed
```

### Agenda (60-90 minutes)

1. **Timeline Review** (15 min)
   - When was incident detected?
   - How long to identify root cause?
   - When was fix deployed?
   - When was service fully restored?

2. **Root Cause Analysis** (20 min)
   - What was the root cause?
   - Why did our controls not prevent this?
   - Could this happen again?

3. **Impact Assessment** (10 min)
   - How many users affected?
   - How long was service degraded?
   - Financial impact?

4. **What Went Well** (10 min)
   - Quick detection?
   - Effective communication?
   - Smooth remediation?

5. **What Could Be Better** (15 min)
   - Preventive measures?
   - Faster detection?
   - Faster resolution?

6. **Action Items** (10 min)
   - Assign owners
   - Set deadlines
   - Track in issue tracker

### Post-Mortem Report Template

```markdown
# Post-Mortem Report: [Incident Title]

## Summary
- **Severity**: [P1/P2/P3/P4]
- **Duration**: [Start time] - [End time] ([Total minutes])
- **Root Cause**: [One sentence description]
- **Affected Services**: [List services]
- **Users Impacted**: [Count/description]

## Timeline
| Time | Event |
|------|-------|
| 14:23 | Alert fired for high CPU |
| 14:24 | On-call notified and acknowledged |
| 14:26 | Root cause identified: new Ansible role |
| 14:31 | Configuration rollback deployed |
| 14:35 | Service recovered, verification passed |
| 14:46 | Post-mortem scheduled |

## Root Cause Analysis

The new common role update introduced a loop that continuously queried system resources,
causing CPU to spike to 95%+.

### Why it wasn't prevented:
- Pre-commit hooks didn't catch the issue
- Staging tests ran on smaller dataset (no resource pressure)
- Code review focused on syntax, not performance

## What Went Well
- ✓ Fast alert response (1 minute)
- ✓ Quick root cause identification (3 minutes)
- ✓ Smooth rollback procedure (5 minutes)
- ✓ Clear communication throughout

## What Could Be Better
- ✗ Load testing in staging didn't catch resource issue
- ✗ No resource limit checks in pre-deployment
- ✗ Role not reviewed by performance specialist

## Action Items
1. Add performance baseline tests to CI (Owner: @alice, Due: Nov 20)
2. Implement resource limit checks in Molecule tests (Owner: @bob, Due: Nov 22)
3. Require performance review for resource-heavy roles (Owner: @charlie, Due: Nov 25)
4. Create runbook for diagnosing CPU spikes (Owner: @alice, Due: Nov 18)

## Financial Impact
- Downtime: 23 minutes
- Users affected: ~500
- Estimated cost: $2,300 (SLA credits, lost productivity)
```

---

## Incident Management Tools

### Slack Integration

```yaml
# Configure incident alerts to Slack
alertmanager:
  receivers:
    - name: 'slack-critical'
      slack_configs:
        - channel: '#incidents'
          title: '{{ .GroupLabels.severity }}: {{ .CommonAnnotations.summary }}'
          text: |
            {{ range .Alerts }}
            {{ .Annotations.description }}
            {{ end }}
          actions:
            - type: button
              text: 'View Grafana'
              url: 'https://grafana.example.com/d/xyz'
            - type: button
              text: 'View Logs'
              url: 'https://logs.example.com/?q=error'
```

### Incident Ticket Template

```
[INCIDENT] Service Degradation - Database High CPU

Priority: P2 (High)
Severity: High
Status: Open

Affected Service(s):
- Database server
- API endpoints
- Web UI

Symptoms:
- Slow database queries
- API timeouts
- User reports slow interface

Current Status:
- Root cause identified: Query optimization missing
- Estimated resolution: 2 hours

Assigned To: @on-call-engineer
Created: 2025-11-15 14:23 UTC
Last Updated: 2025-11-15 14:31 UTC
```

---

## On-Call Responsibilities

### During Incident

1. **Acknowledge within 5 minutes**
2. **Assess severity within 10 minutes**
3. **Update status within 15 minutes**
4. **Begin remediation within 30 minutes**
5. **Escalate if needed** (no progress after 1 hour)

### Communication Responsibilities

- Slack updates every 15 minutes during active incident
- Email updates for resolved incidents
- Status page updates for customer-facing issues

### After-Hours Incidents

- Page on-call engineer immediately
- Conference call for P1/P2
- Email summary for P3/P4

---

## Escalation Matrix

```
Incident Level 1 (Critical)
├─ On-call Engineer
├─ Team Lead (page immediately)
├─ Director of Operations (page after 15 min if not improving)
└─ VP Engineering (notify after 30 min)

Incident Level 2 (High)
├─ On-call Engineer
├─ Team Lead (if not resolved in 30 min)
└─ Director (if not resolved in 1 hour)

Incident Level 3 (Medium)
└─ On-call Engineer (notify Team Lead next business day)

Incident Level 4 (Low)
└─ Normal issue tracking (no on-call escalation)
```

---

## Preventing Incidents

### Alerting Best Practices

```yaml
# Set appropriate alert thresholds
rules:
  # Too sensitive (causes alert fatigue)
  - alert: CPUHigh
    expr: cpu_usage > 50  # ❌ Bad

  # Appropriate threshold
  - alert: CPUHigh
    expr: cpu_usage > 80  # ✓ Good

  # Contextual threshold
  - alert: HighCPU
    expr: rate(cpu_seconds_total[5m]) > 0.8  # ✓ Better
```

### Testing Readiness

```bash
#!/bin/bash
# Pre-deployment incident readiness check

echo "=== INCIDENT READINESS CHECK ==="

# 1. Monitoring configured
[ -f /etc/prometheus/rules.yml ] && echo "✓ Prometheus rules configured" || echo "✗ Missing rules"

# 2. Alerting channels working
curl -s http://localhost:9093/ > /dev/null && echo "✓ Alertmanager running" || echo "✗ Alertmanager down"

# 3. Runbooks available
[ -d /runbooks ] && echo "✓ Runbooks available" || echo "✗ Runbooks missing"

# 4. On-call schedule
pagerduty list-oncalls | grep -q "on call" && echo "✓ On-call schedule active" || echo "✗ On-call schedule issue"

# 5. Incident templates
[ -f /templates/incident-report.md ] && echo "✓ Templates available" || echo "✗ Templates missing"

echo ""
echo "✓ Readiness check complete"
```

---

## Emergency Contacts

Maintain and update quarterly:

```
🚨 CRITICAL CONTACTS
====================

On-Call Engineer: [Name] +1-[Phone] [Slack: @oncall]
Team Lead: [Name] +1-[Phone] [Email]
Director: [Name] +1-[Phone] [Email]
VP Engineering: [Name] +1-[Phone] [Email]

Other Important:
- Security Team: [Contact]
- Infrastructure Team: [Contact]
- Database Admin: [Contact]
- Network Team: [Contact]

Status Page: [URL]
War Room: [Zoom/Teams link]
Incident Channel: #incidents (Slack)
```

---

## Documentation

**Last Updated**: November 15, 2025
**Version**: 1.0.0
**Status**: Production-Ready
**Next Review**: February 15, 2026

This plan is tested quarterly through incident response drills.
