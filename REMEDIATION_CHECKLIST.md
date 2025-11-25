# KumoMTA Remediation Checklist

Quick-reference prioritized checklist for addressing audit findings.

## 🔴 CRITICAL - Must Fix Immediately

### SMTP Authentication (Security)
- [ ] Implement SASL PLAIN/LOGIN mechanism
- [ ] Create credential database file/system
- [ ] Add password hashing (bcrypt)
- [ ] Implement authentication logging
- [ ] Test SMTP AUTH with client credentials

**Files to Create/Modify**:
- [ ] `roles/kumomta/tasks/security-auth.yml` (NEW)
- [ ] `roles/kumomta/templates/auth.lua.j2` (NEW)
- [ ] `roles/kumomta/defaults/main.yml` (update variables)

**Estimated Effort**: 8 hours

---

### Backup Encryption
- [ ] Install GPG/age encryption tools
- [ ] Generate backup encryption key
- [ ] Modify backup script to encrypt
- [ ] Test encrypted backup restore
- [ ] Document key management/rotation

**Files to Modify**:
- [ ] `roles/kumomta/templates/kumomta-backup.sh.j2`
- [ ] `roles/kumomta/templates/kumomta-restore.sh.j2`
- [ ] `roles/kumomta/tasks/backup.yml`

**Estimated Effort**: 6 hours

---

### TLS Hardening (Security)
- [ ] Set minimum TLS 1.2
- [ ] Configure strong cipher suites only
- [ ] Enable OCSP stapling
- [ ] Add certificate validation for outbound
- [ ] Test with SSL Labs

**Files to Create/Modify**:
- [ ] `roles/kumomta/templates/tls-config.lua.j2` (NEW)
- [ ] `roles/kumomta/templates/policy.lua.j2` (update)
- [ ] `roles/kumomta/defaults/main.yml`

**Estimated Effort**: 10 hours

---

### SPF/DMARC Enforcement (Email Security)
- [ ] Add SPF validation in policy
- [ ] Add DMARC policy checking
- [ ] Implement DKIM signature validation
- [ ] Add alignment checks
- [ ] Log policy violations
- [ ] Configure quarantine/reject actions

**Files to Create/Modify**:
- [ ] `roles/kumomta/templates/spf-dmarc-policy.lua.j2` (NEW)
- [ ] `roles/kumomta/templates/policy.lua.j2` (integrate)
- [ ] `roles/kumomta/defaults/main.yml`

**Estimated Effort**: 12 hours

---

### Fail2ban Integration (Brute Force)
- [ ] Install fail2ban package
- [ ] Create kumomta jail configuration
- [ ] Define fail patterns (auth, SMTP spam)
- [ ] Set ban times and retry limits
- [ ] Test ban trigger and unban

**Files to Create/Modify**:
- [ ] `roles/kumomta/tasks/security-hardening.yml` (NEW)
- [ ] `roles/kumomta/files/fail2ban-kumomta.conf` (NEW)

**Estimated Effort**: 4 hours

---

### Metrics Validation
- [ ] Query actual metrics from running instance
- [ ] Document all exported metrics
- [ ] Update alert rules to match actual metrics
- [ ] Create metric validation test
- [ ] Add metrics audit to CI/CD

**Files to Create/Modify**:
- [ ] `roles/kumomta/templates/kumomta-alerts.yml.j2`
- [ ] `tests/test_kumomta_metrics.yml` (NEW)
- [ ] Documentation

**Estimated Effort**: 5 hours

---

### Disable Non-Functional Features
- [ ] Set `kumomta_webhook_enabled: false` if not implementing
- [ ] Document which features are disabled
- [ ] Remove misleading documentation

**Estimated Effort**: 1 hour

**Total Phase 1 Effort**: 46 hours (1.5 weeks)

---

## 🟡 HIGH PRIORITY - Complete Before Production

### Load Testing
- [ ] Create load test playbook with Apache JMeter
- [ ] Test incremental loads (10K, 100K, 1M messages)
- [ ] Measure:
  - [ ] Queue processing latency (p50, p95, p99)
  - [ ] CPU/Memory/Disk utilization
  - [ ] Connection limits
  - [ ] Delivery throughput
- [ ] Document capacity limits
- [ ] Create scaling guidelines

**Files to Create**:
- [ ] `playbooks/load-test.yml` (NEW)
- [ ] `roles/kumomta/files/load-test-config.jmx` (NEW)
- [ ] `docs/CAPACITY_PLANNING.md` (NEW)

**Estimated Effort**: 20 hours

---

### Backup Restore Testing
- [ ] Automate monthly restore tests
- [ ] Create restore procedure runbook
- [ ] Test restore to isolated environment
- [ ] Measure RTO (Recovery Time Objective)
- [ ] Verify message integrity post-restore
- [ ] Document recovery procedures

**Files to Create/Modify**:
- [ ] `playbooks/test-restore.yml` (NEW)
- [ ] `docs/DISASTER_RECOVERY_RUNBOOK.md` (NEW)
- [ ] `roles/kumomta/tasks/backup.yml`

**Estimated Effort**: 12 hours

---

### IPv6 Support
- [ ] Enable IPv6 in policy configuration
- [ ] Update SMTP listeners for dual-stack
- [ ] Test IPv6 inbound delivery
- [ ] Create AAAA DNS records
- [ ] Update documentation

**Files to Modify**:
- [ ] `roles/kumomta/templates/policy.lua.j2`
- [ ] `roles/kumomta/defaults/main.yml`

**Estimated Effort**: 8 hours

---

### Content Filtering Integration
- [ ] Select filter (SpamAssassin or rspamd)
- [ ] Install and configure spam filter
- [ ] Create antivirus integration (ClamAV)
- [ ] Add attachment filtering
- [ ] Implement size limits
- [ ] Create whitelist/blacklist

**Files to Create**:
- [ ] `roles/kumomta/tasks/content-filtering.yml` (NEW)
- [ ] `roles/kumomta/templates/filter-policy.lua.j2` (NEW)

**Estimated Effort**: 16 hours

---

### CI/CD Pipeline
- [ ] Create GitHub Actions workflow for testing
- [ ] Add ansible-lint checks
- [ ] Add security scanning (trivy, snyk)
- [ ] Create deployment workflow
- [ ] Implement blue-green deployment
- [ ] Add rollback procedures

**Files to Create**:
- [ ] `.github/workflows/test.yml` (NEW)
- [ ] `.github/workflows/deploy.yml` (NEW)
- [ ] `.github/workflows/security-scan.yml` (NEW)

**Estimated Effort**: 12 hours

---

### Disaster Recovery Planning
- [ ] Create RTO/RPO definitions
- [ ] Document recovery for each failure scenario
- [ ] Create incident response runbooks
- [ ] Test failover procedures
- [ ] Setup communication plan
- [ ] Create post-incident templates

**Files to Create**:
- [ ] `docs/DISASTER_RECOVERY_PLAN.md` (NEW)
- [ ] `docs/INCIDENT_RESPONSE_RUNBOOK.md` (NEW)
- [ ] `playbooks/failover-procedures.yml` (NEW)

**Estimated Effort**: 10 hours

---

### Supply Chain Security
- [ ] Add GPG signature verification
- [ ] Create mirror/caching strategy
- [ ] Document binary signing
- [ ] Setup checksum verification
- [ ] Consider source compilation option

**Files to Modify**:
- [ ] `roles/kumomta/tasks/install.yml`

**Estimated Effort**: 6 hours

**Total Phase 2 Effort**: 84 hours (2-3 weeks)

---

## 🟢 MEDIUM PRIORITY - Should Complete

### Distributed Tracing
- [ ] Add message correlation IDs
- [ ] Implement trace logging
- [ ] Setup OpenTelemetry (optional)
- [ ] Create trace analysis tools

**Estimated Effort**: 12 hours

---

### List Management Features
- [ ] Implement RFC 2369 headers
- [ ] Add List-Unsubscribe support
- [ ] Create one-click unsubscribe
- [ ] Add List-Post and List-Help headers

**Estimated Effort**: 10 hours

---

### API Endpoints
- [ ] Create queue inspection API
- [ ] Implement message requeue endpoint
- [ ] Add config reload endpoint
- [ ] Create health check endpoint
- [ ] Add API authentication

**Estimated Effort**: 16 hours

---

### Third-Party Integrations
- [ ] Add SendGrid/AWS SES fallback
- [ ] Setup Kafka event streaming
- [ ] Integrate ELK/Loki logging
- [ ] Add Vault secrets management

**Estimated Effort**: 20 hours (per integration)

**Total Phase 3 Effort**: 58+ hours (1-2 weeks)

---

## Implementation Priority by Component

### Week 1 (Critical Security - 40 hours)
- [ ] SMTP AUTH + fail2ban (12 hours)
- [ ] Backup encryption (6 hours)
- [ ] TLS hardening (10 hours)
- [ ] Metrics validation (5 hours)
- [ ] Infrastructure review (7 hours)

### Week 2 (Security & Validation - 40 hours)
- [ ] SPF/DMARC enforcement (12 hours)
- [ ] Backup restore testing (12 hours)
- [ ] Supply chain security (6 hours)
- [ ] Documentation updates (10 hours)

### Week 3-4 (Testing & Operations - 50+ hours)
- [ ] Load testing (20 hours)
- [ ] IPv6 support (8 hours)
- [ ] CI/CD pipeline (12 hours)
- [ ] Disaster recovery planning (10 hours)

### Beyond (Nice-to-have - 100+ hours)
- [ ] Content filtering (16 hours)
- [ ] Distributed tracing (12 hours)
- [ ] List management (10 hours)
- [ ] API endpoints (16 hours)
- [ ] Third-party integrations (50+ hours)

---

## Quick Implementation Guide

### Start with Phase 1, Sprint 1 (Week 1):

```bash
# 1. Create SMTP AUTH task
mkdir -p roles/kumomta/tasks/
touch roles/kumomta/tasks/security-auth.yml

# 2. Create TLS hardening task
touch roles/kumomta/tasks/security-tls.yml

# 3. Add fail2ban integration
touch roles/kumomta/tasks/security-hardening.yml

# 4. Update policy template for SPF/DMARC
# Edit: roles/kumomta/templates/policy.lua.j2

# 5. Validate metrics
./scripts/validate-metrics.sh

# 6. Update defaults
# Edit: roles/kumomta/defaults/main.yml
```

### Testing Checklist Before Production Deployment:

- [ ] SMTP AUTH: Test with multiple credentials
- [ ] TLS: Verify cipher suites with nmap/sslscan
- [ ] SPF/DMARC: Test with alignment issues
- [ ] Backup: Complete encrypt→backup→restore cycle
- [ ] Metrics: All alerts reference valid metrics
- [ ] Load: Handle at least 2x expected volume
- [ ] HA/Failover: Manual switchover works
- [ ] Recovery: Timed restore from backup

---

## Tracking Template

Use this to track remediation progress:

```markdown
## Phase 1 Progress

- [x] Security audit completed
- [ ] SMTP AUTH implemented (ETA: Nov 30)
- [ ] TLS hardening (ETA: Nov 28)
- [ ] SPF/DMARC validation (ETA: Dec 1)
- [ ] Backup encryption (ETA: Nov 27)
- [ ] Fail2ban integration (ETA: Nov 29)
- [ ] Metrics validation (ETA: Nov 26)

Status: 1/7 complete (14%)
Timeline: On track for Nov 30 completion
```

---

## Success Criteria

### Phase 1 Complete When:
- ✅ SMTP AUTH tested with valid/invalid credentials
- ✅ All backups encrypted and restore tested
- ✅ TLS 1.2+ enforced with strong ciphers
- ✅ SPF/DMARC validation working
- ✅ All Prometheus alerts reference real metrics
- ✅ Fail2ban preventing brute force attempts

### Phase 2 Complete When:
- ✅ Load tested to 2x expected volume
- ✅ Backup restore completes in <30 minutes
- ✅ IPv6 delivery confirmed working
- ✅ CI/CD pipeline running on PRs
- ✅ Disaster recovery runbooks created and tested

### Phase 3 Complete When:
- ✅ SLOs defined with monitoring
- ✅ On-call rotation established
- ✅ Monthly restore drill completed
- ✅ Capacity limits documented
- ✅ Team training completed

---

## Support & References

- [KumoMTA Documentation](https://docs.kumomta.com)
- [RFC 7231 - SPF](https://tools.ietf.org/html/rfc7231)
- [RFC 7489 - DMARC](https://tools.ietf.org/html/rfc7489)
- [RFC 7672 - DANE](https://tools.ietf.org/html/rfc7672)
- [MTA-STS Spec](https://tools.ietf.org/html/rfc8461)
