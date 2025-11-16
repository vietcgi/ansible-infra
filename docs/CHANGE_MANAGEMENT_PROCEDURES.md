# Change Management Procedures

## Overview

This document defines the change management process for ansible-infra infrastructure. The procedures ensure controlled, auditable, and safe infrastructure modifications with minimal disruption.

---

## Change Categories

### Category 1: Emergency Changes (Fast-Track)
- **Trigger**: Active security incident, critical outage
- **Approval**: Verbal approval from duty manager sufficient
- **Testing**: Minimal (smoke tests only)
- **Notification**: After deployment
- **Example**: Security patch for active vulnerability

**Procedure**:
```
Incident Occurs
  ↓
Fix developed (< 15 min)
  ↓
Verbal approval from on-call lead
  ↓
Deploy to production
  ↓
Notify team post-deployment
  ↓
Full testing/review within 24 hours
```

### Category 2: Critical Changes (Standard Process)
- **Trigger**: Security updates, critical bug fixes, major features
- **Approval**: Manager approval required
- **Testing**: Full Molecule test suite, staging validation
- **Notification**: 24 hours advance notice to team
- **Change window**: Scheduled maintenance window
- **Example**: SSH hardening update, critical patch rollout

**Procedure**:
```
Change requested (ticket created)
  ↓ (4 hours)
Code review & testing completed
  ↓ (4 hours)
Manager approval obtained
  ↓ (24 hours advance)
Communicate change window to users
  ↓ (during window)
Deploy to staging
  ↓ (1 hour)
Validation in staging
  ↓ (approval)
Deploy to production
  ↓ (post-deployment)
Verify and document
```

### Category 3: Standard Changes (Routine)
- **Trigger**: Regular updates, minor improvements, configuration tweaks
- **Approval**: Team lead approval
- **Testing**: Molecule tests, peer review
- **Notification**: Posted in change log
- **Example**: Package updates, configuration optimizations

**Procedure**:
```
Change request submitted
  ↓
Peer code review
  ↓
Molecule test suite passes
  ↓
Team lead approval
  ↓
Merge to main branch
  ↓
Automated deployment (if configured)
  ↓
Post-deployment smoke tests
```

### Category 4: Minor Changes (Pre-Approved)
- **Trigger**: Documentation, comments, minor refactoring
- **Approval**: Self-approved with peer review
- **Testing**: Ansible-lint only
- **Notification**: Commit message with context
- **Example**: README updates, code cleanup, variable renaming

**Procedure**:
```
Change developed
  ↓
Self-reviewed
  ↓
Ansible-lint passes
  ↓
Pull request to main
  ↓
At least 1 peer review/approval
  ↓
Merge to main
```

---

## Change Request Process

### Step 1: Submit Change Request

Create GitHub issue or use change tracking system:

```markdown
## Change Request: [Title]

### Category
[ ] Emergency (fast-track)
[x] Critical (full process)
[ ] Standard (routine)
[ ] Minor (pre-approved)

### Description
Brief description of what is changing and why.

### Impact Assessment
- **Services affected**: [List]
- **Users impacted**: [Estimated count]
- **Risk level**: [Low/Medium/High]
- **Rollback difficulty**: [Easy/Moderate/Difficult]

### Implementation Plan
1. Step 1: [Action]
2. Step 2: [Action]
3. Verification: [How will we verify success?]

### Testing Completed
- [x] Molecule tests passed
- [x] Staging environment validated
- [ ] Performance testing
- [ ] Security review

### Rollback Plan
If deployment fails:
1. Step 1: [Rollback action]
2. Step 2: [Verification]

### Estimated Duration
- Deployment time: [X minutes]
- Expected downtime: [Y minutes or "None"]
- Monitoring period: [Z minutes post-deployment]

### Risk Assessment
- **Risk**: [Low/Medium/High]
- **Mitigation**: [How will we handle failures?]
- **Blast radius**: [How many systems affected if it fails?]
```

### Step 2: Triage & Categorization

Team lead reviews and categorizes within 4 hours:

- [ ] Category assigned
- [ ] Risk assessment approved
- [ ] Timeline scheduled (if needed)
- [ ] Assigned to implementer
- [ ] Dependencies identified

### Step 3: Code Review

For all changes:

```
Requirements for approval:
☑ At least 2 peer reviews
☑ All Molecule tests pass
☑ Ansible-lint passes
☑ No breaking changes (or documented)
☑ Documentation updated
☑ Change rollback procedure documented
```

**Code Review Checklist**:
- [ ] Code follows style guidelines
- [ ] Changes are minimal and focused
- [ ] No hardcoded values or secrets
- [ ] Error handling appropriate
- [ ] Comments explain non-obvious logic
- [ ] Tests added for new functionality
- [ ] Documentation updated

### Step 4: Testing

**Molecule Tests** (all must pass):
```bash
cd roles/common
molecule test

# Results must show:
- ✓ Lint passed
- ✓ Create successful (4 platforms)
- ✓ Prepare successful
- ✓ Converge successful (no errors)
- ✓ Idempotence passed
- ✓ Verify assertions passed
```

**Staging Validation**:
```bash
# Deploy to staging environment
ansible-playbook playbooks/configure.yml \
  -i inventories/staging/hosts.yml

# Run smoke tests
curl http://staging-host/health
ansible staging -m ping

# Manual verification
ssh user@staging-host
systemctl status service
```

**Security Review** (for security-related changes):
- [ ] No credentials in code
- [ ] Encryption used appropriately
- [ ] Access control validated
- [ ] Compliance mappings updated
- [ ] Security impacts documented

### Step 5: Approval

**For Critical Changes**:
Manager or director approval required.

```
Approval by: [Name] [Date/Time]
Manager email: [confirmation]
Approval expires in: 7 days
```

**For Standard/Minor Changes**:
Team lead approval via PR comments.

```
@team-lead please review
Approved by: @team-lead [Date]
```

### Step 6: Scheduling

**For Emergency Changes**:
Deploy immediately after approval.

**For Critical Changes**:
Schedule during approved maintenance window.

```
Change window:
Start: 2025-11-20 02:00 UTC
Duration: 1 hour
Maintenance window: 2025-11-20 02:00-03:00 UTC
Rollback window: 2025-11-20 03:00-03:30 UTC

Notification sent to:
- All team members
- Slack #announcements
- Status page
```

**For Standard/Minor Changes**:
Deploy during business hours (7 AM - 6 PM in primary timezone).

### Step 7: Deployment

**Pre-Deployment Checklist**:
- [ ] Backup created
- [ ] Rollback plan verified
- [ ] Team notified
- [ ] Monitoring configured
- [ ] War room established (if critical)
- [ ] On-call engineer standing by
- [ ] Status page updated to "Maintenance"

**Deployment Steps**:

1. **Verify environment** (5 min)
   ```bash
   git status  # Clean working directory
   git pull origin main  # Latest code
   ansible all -i inventories/production -m ping  # All hosts reachable
   ```

2. **Run deployment** (5-30 min)
   ```bash
   # Dry-run first
   ansible-playbook playbooks/configure.yml \
     -i inventories/production \
     --check --diff

   # If dry-run successful, proceed
   ansible-playbook playbooks/configure.yml \
     -i inventories/production
   ```

3. **Monitor execution** (during deployment)
   ```bash
   # Watch progress
   tail -f /var/log/ansible-infra/ansible.log

   # Monitor system metrics
   watch -n 5 'top -b -n1 | head -20'
   ```

### Step 8: Verification

**Post-Deployment Checks** (15 min):

```bash
#!/bin/bash
# post-deployment-verification.sh

echo "=== POST-DEPLOYMENT VERIFICATION ==="
echo "Time: $(date)"

# 1. Service health
echo ""
echo "1. Service Status:"
systemctl status ansible-infra || echo "FAILED"

# 2. Configuration validity
echo ""
echo "2. Configuration Validation:"
ansible all -i inventories/production -m ping

# 3. Smoke tests
echo ""
echo "3. Running Smoke Tests:"
molecule verify || echo "Tests failed"

# 4. Error rate
echo ""
echo "4. Error Monitoring:"
curl -s http://prometheus:9090/api/v1/query?query='rate(errors_total[5m])' | jq .

# 5. Performance
echo ""
echo "5. Performance Check:"
curl -w "Response time: %{time_total}s\n" http://localhost:8000/health

echo ""
echo "=== VERIFICATION COMPLETE ==="
```

**Rollback if Issues Found**:
```bash
# Identify issue
tail -f /var/log/ansible-infra/ansible.log

# Revert to previous state
git reset --hard HEAD~1
ansible-playbook playbooks/configure.yml \
  -i inventories/production

# Verify rollback successful
ansible all -i inventories/production -m ping
```

### Step 9: Documentation

**Create post-deployment summary**:

```markdown
# Change Deployment Summary

**Date**: 2025-11-15
**Change**: Update SSH to post-quantum algorithms
**Duration**: 23 minutes
**Status**: Successful

## What Changed
- Added sntrup761x25519-sha512 key exchange
- Updated sshd_config template
- Rolled out to all production hosts

## Testing Results
- Molecule tests: ✓ Passed
- Staging validation: ✓ Passed
- Smoke tests: ✓ Passed
- No errors detected

## Metrics Pre/Post
- SSH auth success rate: 99.95% → 99.98%
- Connection time: 2.3ms → 2.1ms
- Error rate: 0.05% → 0.02%

## Issues Encountered
None

## Verification
- All hosts confirmed
- Services operational
- Monitoring alerts cleared
- Users report normal service

## Next Steps
- Monitor for 24 hours
- Review metrics tomorrow
- Document lessons learned
```

### Step 10: Closure

**Final Steps**:
- [ ] Status page updated to "Operational"
- [ ] Change ticket marked "Closed"
- [ ] Post-deployment metrics recorded
- [ ] Team notified of completion
- [ ] Documentation updated
- [ ] Next change scheduled (if applicable)

---

## Change Management Tools & Templates

### Change Request Template

```
Title: [Clear, specific description]
Category: [Emergency/Critical/Standard/Minor]
Requester: [Name]
Assigned To: [Implementer]
Priority: [Critical/High/Medium/Low]
Target Date: [YYYY-MM-DD]

Description:
[Detailed explanation of change]

Justification:
[Why is this change needed?]

Impact:
- Services affected: [List]
- Data affected: [Yes/No, what data]
- User facing: [Yes/No]
- Performance impact: [None/Positive/Negative]
- Security impact: [None/Positive/Negative]

Testing:
- Unit tests: [Pass/Fail]
- Integration tests: [Pass/Fail]
- Staging validation: [Pass/Fail]
- Rollback tested: [Yes/No]

Risks:
- Technical risks: [List]
- Mitigations: [List]
- Rollback plan: [Described]

Approvals:
- Code review: [Date, Reviewer name]
- Manager approval: [Date, Name]
```

### Change Log Format

```
## [2025-11-15] - SSH Post-Quantum Cryptography Update

### Added
- sntrup761x25519-sha512 key exchange algorithm
- Post-quantum algorithm documentation

### Changed
- SSH key exchange preference order
- sshd_config template for modern algorithms

### Security
- Future-proof against quantum computing threats
- Maintains backward compatibility

### Testing
- Molecule tests on 4 platforms
- Staging environment validation
- SSH authentication verification

### Deployment
- Duration: 23 minutes
- Downtime: None
- Rollback tested: Yes
```

---

## Change Management Metrics

Track these metrics to measure process effectiveness:

```
Metrics to monitor:
- Change success rate (% of changes without rollback)
- Change deployment time (planned vs actual)
- Change testing coverage (% of changes tested)
- Change approval time (submission to approval)
- Post-change issues (bugs from recent changes)
- Change cycle time (idea to production)
```

**Monthly Review**:
```
Summary for November 2025:
- Changes processed: 47
- Success rate: 98.9%
- Average deployment time: 18 minutes (target: 20)
- Zero production incidents from changes
- Approval time: avg 4.2 hours (target: 4 hours)
- Testing coverage: 100%

Status: ✓ Within targets
```

---

## Maintenance Windows

### Scheduling

**Standard windows** (same time every week):
- Tuesday 02:00-04:00 UTC
- Thursday 02:00-04:00 UTC

**Special maintenance** (as needed):
- Published 72 hours in advance
- Scheduled outside peak usage times
- Limited to 2-hour windows maximum

### Window Management

```bash
#!/bin/bash
# Announce maintenance window

MESSAGE="Scheduled maintenance: Tuesday 2025-11-21 02:00 UTC
Duration: 1 hour
Changes: SSH configuration update
Impact: Brief connectivity interruption (< 5 min)

We will send status updates every 15 minutes.
Thank you for your patience."

# Post to status page
curl -X POST https://status.example.com/api/incidents \
  -d "status_page_id=$ID" \
  -d "message=$MESSAGE"

# Notify via Slack
curl -X POST https://hooks.slack.com/services/xxx \
  -d "payload={\"text\":\"$MESSAGE\"}"

# Email notification
echo "$MESSAGE" | mail -s "Maintenance Window Scheduled" ops@example.com
```

---

## Emergency Change Procedure

For immediate fixes during active incidents:

1. **Declare emergency** (< 2 min)
   - Severity 1 (Critical) incident active
   - Standard approval process would cause unacceptable delay

2. **Verbal approval** (< 5 min)
   - Duty manager or on-call lead approves verbally
   - Record approval in incident ticket

3. **Rapid implementation** (< 15 min)
   - Minimal testing (no time for full suite)
   - Deploy with high confidence fix

4. **Post-deployment review** (within 24 hours)
   - Full testing conducted
   - Peer review completed
   - Formal approval obtained
   - If issues found, rollback and replan

Example emergency change:
```
14:23 - Alert: Security vulnerability in dependency
14:24 - Investigation: Confirmed active exploit
14:25 - Fix developed: Patch identified, tested locally
14:26 - Emergency approval: Duty manager @jane_smith approves
14:31 - Deployed: Patch applied to all hosts
14:45 - Verified: No new exploits detected
15:00 - Post-incident: Full review and approval documented
```

---

## Documentation

**Last Updated**: November 15, 2025
**Version**: 1.0.0
**Status**: Production-Ready
**Next Review**: February 15, 2026

This process ensures safe, controlled infrastructure changes with full audit trail.
