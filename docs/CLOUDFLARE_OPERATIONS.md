# Cloudflare Integration - Operations and Change Management Guide

**Date**: November 17, 2025
**Purpose**: Safe operational procedures for common Cloudflare changes
**Audience**: Infrastructure operators, DevOps engineers

---

## Safe Change Workflow

All Cloudflare configuration changes should follow this workflow:

```
┌─────────────────────────────────────────────────────────┐
│ 1. Backup Current State                                  │
│    ansible-playbook examples/cloudflare_backup.yml       │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Update Variables/Code                                 │
│    - Modify roles/cloudflare_integration/defaults/       │
│    - Update examples/cloudflare_deployment.yml          │
│    - Update git and commit                              │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Dry-Run (Check Mode)                                  │
│    ansible-playbook ... --check --ask-vault-pass        │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ 4. Review Changes                                        │
│    - Read Ansible output carefully                      │
│    - Verify "changed" count is expected                 │
│    - Check for any errors/warnings                      │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ 5. Get Approval                                          │
│    - Show team the planned changes                      │
│    - Verify impact is acceptable                        │
│    - Get sign-off                                       │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ 6. Deploy (Remove --check)                              │
│    ansible-playbook ... --ask-vault-pass               │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ 7. Verify in Dashboard                                  │
│    - Log into Cloudflare dashboard                      │
│    - Verify changes applied correctly                   │
│    - Check for any warnings/alerts                      │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ 8. Run Health Check                                      │
│    /usr/local/bin/cloudflare-health-check              │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ 9. Monitor Results                                       │
│    - Watch logs for 24 hours                            │
│    - Monitor WAF/DDoS metrics                           │
│    - Verify no false positives                         │
└─────────────────────────────────────────────────────────┘
```

---

## Common Operations

### Operation 1: Add New DNS Record

**Scenario**: You need to add a new subdomain and enable Cloudflare proxy

**Steps**:

1. **Backup first**
   ```bash
   ansible-playbook examples/cloudflare_backup.yml --ask-vault-pass
   ```

2. **Update variables**
   ```yaml
   # roles/cloudflare_integration/defaults/main.yml
   # or examples/cloudflare_deployment.yml

   cloudflare_dns_records:
     # ... existing records ...
     - zone: "example.com"
       record: "api"              # New: api.example.com
       type: "A"
       value: "192.0.2.10"
       ttl: 300
       proxied: true
       state: "present"
   ```

3. **Dry-run**
   ```bash
   ansible-playbook examples/cloudflare_deployment.yml \
     --check --ask-vault-pass
   ```

   Expected output:
   ```
   TASK [cloudflare_integration : Create DNS records from configuration]
   ...
   changed: [localhost] => (item=api.example.com)
   ```

4. **Review the change**
   - Check it only adds the new record (not modifying others)
   - Verify TTL and proxy settings

5. **Deploy**
   ```bash
   ansible-playbook examples/cloudflare_deployment.yml --ask-vault-pass
   ```

6. **Verify**
   - Check Cloudflare dashboard: DNS → Verify new record exists
   - Test DNS: `dig api.example.com` or `nslookup api.example.com`
   - Verify proxy enabled (orange cloud in dashboard)

---

### Operation 2: Update WAF Sensitivity Level

**Scenario**: WAF is too strict, blocking legitimate traffic

**Steps**:

1. **Backup current state**
   ```bash
   ansible-playbook examples/cloudflare_backup.yml --ask-vault-pass
   ```

2. **Update WAF sensitivity**
   ```yaml
   # examples/cloudflare_deployment.yml
   cloudflare_waf_enabled: true
   cloudflare_waf_sensitivity_level: "medium"  # Changed from "high"
   ```

3. **Dry-run to verify**
   ```bash
   ansible-playbook examples/cloudflare_deployment.yml \
     --check --ask-vault-pass --tags cloudflare_waf
   ```

4. **Deploy**
   ```bash
   ansible-playbook examples/cloudflare_deployment.yml \
     --ask-vault-pass --tags cloudflare_waf
   ```

5. **Verify in dashboard**
   - WAF & DDoS → WAF Rules → Check "Sensitivity Level"
   - Should show "Medium"

6. **Monitor**
   - Watch WAF logs for false positives: Security → WAF
   - Monitor blocked requests
   - If still too strict, repeat with "low"

---

### Operation 3: Enable/Disable DDoS Protection

**Scenario**: Testing DDoS during maintenance window

**Steps**:

1. **Backup**
   ```bash
   ansible-playbook examples/cloudflare_backup.yml --ask-vault-pass
   ```

2. **Update DDoS setting**
   ```yaml
   # examples/cloudflare_deployment.yml
   cloudflare_ddos_protection_enabled: false  # Disable for testing
   ```

3. **Dry-run**
   ```bash
   ansible-playbook examples/cloudflare_deployment.yml \
     --check --ask-vault-pass --tags cloudflare_ddos
   ```

4. **Deploy during maintenance window**
   ```bash
   # Announce maintenance
   # Deploy change
   ansible-playbook examples/cloudflare_deployment.yml \
     --ask-vault-pass --tags cloudflare_ddos

   # Verify
   # Re-enable
   ```

5. **Re-enable after maintenance**
   ```yaml
   cloudflare_ddos_protection_enabled: true
   ```

6. **Deploy**
   ```bash
   ansible-playbook examples/cloudflare_deployment.yml \
     --ask-vault-pass --tags cloudflare_ddos
   ```

---

### Operation 4: Change SSL/TLS Mode

**Scenario**: Need strict SSL/TLS for production

**Important**: Only change if you have valid certificates on origin!

**Steps**:

1. **Verify origin has valid certificate**
   ```bash
   openssl s_client -connect origin.example.com:443 -showcerts
   ```

2. **Backup**
   ```bash
   ansible-playbook examples/cloudflare_backup.yml --ask-vault-pass
   ```

3. **Update SSL mode**
   ```yaml
   # examples/cloudflare_deployment.yml

   # Current: flexible (no cert required on origin)
   # New: full_strict (requires valid cert matching domain)
   cloudflare_ssl_tls_mode: "full_strict"
   cloudflare_ssl_tls_minimum_version: "1.3"
   ```

4. **Dry-run**
   ```bash
   ansible-playbook examples/cloudflare_deployment.yml \
     --check --ask-vault-pass --tags cloudflare_ssl
   ```

5. **IMPORTANT: Test on staging first!**
   ```bash
   # Don't deploy to production without testing
   # Use staging domain to verify:
   # 1. Origin certificate is valid
   # 2. Version is supported (TLS 1.3)
   # 3. No connection errors
   ```

6. **Deploy to production**
   ```bash
   ansible-playbook examples/cloudflare_deployment.yml \
     --ask-vault-pass --tags cloudflare_ssl
   ```

7. **Verify immediately**
   ```bash
   # Check no SSL errors
   curl -I https://www.example.com

   # Should show 200 OK, not SSL error
   ```

---

### Operation 5: Adjust Cache TTL

**Scenario**: Reduce cache time for frequently updated content

**Steps**:

1. **Backup**
   ```bash
   ansible-playbook examples/cloudflare_backup.yml --ask-vault-pass
   ```

2. **Update cache settings**
   ```yaml
   # examples/cloudflare_deployment.yml
   cloudflare_edge_cache_enabled: true
   cloudflare_cache_browser_ttl: 15  # Changed from 30 minutes
   ```

3. **Dry-run**
   ```bash
   ansible-playbook examples/cloudflare_deployment.yml \
     --check --ask-vault-pass --tags cloudflare_cache
   ```

4. **Deploy**
   ```bash
   ansible-playbook examples/cloudflare_deployment.yml \
     --ask-vault-pass --tags cloudflare_cache
   ```

5. **Monitor impact**
   - Analytics → Caching → Cache hit ratio
   - Monitor origin server load
   - Check if performance acceptable

6. **Adjust if needed**
   - If cache miss too high, increase TTL
   - If origin overloaded, increase TTL
   - Balance performance vs freshness

---

## Emergency Procedures

### Emergency 1: WAF Blocking All Traffic

**Symptom**: Website suddenly inaccessible, all requests blocked

**Immediate Fix**:

```bash
# Disable WAF immediately
curl -X PATCH \
    -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
    -H "Content-Type: application/json" \
    https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/waf \
    -d '{"value":"off"}'

echo "WAF disabled - website should be accessible"
```

**Then investigate**:
```bash
# Check what rules were blocking
# WAF & DDoS → WAF Rules → Check logs
# See what patterns matched

# Identify false positive rule
# Update rule exceptions or change settings
# Test in check mode before redeploying
```

### Emergency 2: SSL Certificate Error

**Symptom**: Visitors see SSL certificate error

**Immediate Fix**:

```bash
# Downgrade SSL mode temporarily
curl -X PATCH \
    -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
    -H "Content-Type: application/json" \
    https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/ssl \
    -d '{"value":"flexible"}'

echo "SSL mode set to flexible - website should be accessible"
```

**Then investigate**:
```bash
# Check origin certificate
openssl s_client -connect origin.example.com:443

# Is it valid?
# Does it match your domain?
# Has it expired?

# Fix on origin, then set SSL to full_strict
```

### Emergency 3: DDoS Attack Overwhelming Site

**Immediate**:
```bash
# Increase DDoS sensitivity
curl -X PATCH \
    -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
    -H "Content-Type: application/json" \
    https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/ddos_sensitivity \
    -d '{"value":"high"}'

# Enable rate limiting
curl -X PATCH \
    -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
    -H "Content-Type: application/json" \
    https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/waf \
    -d '{"value":"on"}'
```

**Then**:
- Monitor attack in Real-Time Logs
- Check attack source geography
- Consider blocking countries if all attack from one region
- Contact Cloudflare support if attack overwhelming edge

---

## Monitoring During Changes

### What to Monitor

1. **Immediately after deployment**:
   ```bash
   # Check health
   /usr/local/bin/cloudflare-health-check

   # Watch real-time logs
   tail -f /var/log/cloudflare/health-check.log
   ```

2. **First hour**:
   - Watch Analytics dashboard
   - Monitor Error rates
   - Check Real-Time Logs for blocks/issues
   - Verify DNS resolution working

3. **First 24 hours**:
   - Monitor WAF block rates
   - Check for false positives
   - Monitor origin server load
   - Watch error logs

### Dashboards to Check

| Dashboard | What to Check | Location |
|-----------|---------------|----------|
| Analytics | Traffic, errors, cache | Cloudflare → Your domain → Analytics |
| Real-Time Logs | Individual requests | Security → Real-Time Logs |
| WAF | Blocked requests | Security → WAF |
| DDoS | Attack traffic | Security → DDoS |
| SSL/TLS | Certificate status | SSL/TLS → Overview |
| Health Check | System status | Cloudflare dashboard |

---

## Rollback Procedures

### Quick Rollback (Last 5 minutes)

```bash
# If you just deployed and something broke immediately
git log --oneline | head -3
git checkout HEAD~1 -- roles/cloudflare_integration/
ansible-playbook examples/cloudflare_deployment.yml --ask-vault-pass
```

### Standard Rollback (Recent changes)

```bash
# Identify good commit
git log --oneline | grep "cloudflare"

# Review what changed
git show COMMIT_HASH

# Revert
git revert COMMIT_HASH

# Deploy reverted version
ansible-playbook examples/cloudflare_deployment.yml --ask-vault-pass
```

### Full Restore from Backup

```bash
# If code rollback not enough, restore from API backup
BACKUP="backups/cloudflare/example.com/dns_20251117.json"

# Restore DNS records from backup
cat "$BACKUP" | jq -r '.[] | @json' | while read record; do
    curl -X POST \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
        -d "$record"
done
```

---

## Change Log Template

Document all changes for audit trail:

```markdown
# Cloudflare Change Log

## [2025-01-15] - WAF Sensitivity Update
- **Changed**: WAF sensitivity level high → medium
- **Reason**: False positives blocking legitimate traffic
- **Requester**: Team Lead Name
- **Approval**: Manager approval obtained
- **Backup**: backups/cloudflare/example.com/settings_20250115.json
- **Result**: Successful, monitored 24 hours, no issues
- **Rollback Plan**: Revert to "high" if false negatives increase

## [2025-01-10] - Add API Subdomain
- **Changed**: Added api.example.com DNS record
- **Reason**: New API service deployment
- **Requester**: Developer Name
- **Backup**: backups/cloudflare/example.com/dns_20250110.json
- **Result**: Successful
- **Verified**: DNS resolution working, Cloudflare proxying
```

---

## Maintenance Windows

### Scheduling Maintenance

1. **Announce in advance**
   ```
   To: infrastructure-team
   Subject: Cloudflare Maintenance - 2025-01-20 22:00-23:00 UTC

   We will be updating Cloudflare security rules.
   Expected impact: None (tested in check mode)
   Rollback: Available within 5 minutes if issues

   Please avoid deployments during this window.
   ```

2. **Execute change during window**
   - Follow normal workflow (backup, check, deploy, verify)
   - Have team on standby
   - Monitor closely

3. **Post-maintenance notification**
   ```
   Maintenance complete. All systems normal.
   Changes deployed successfully.
   No issues detected.
   ```

---

## Change Approval Checklist

- [ ] **Planning**
  - [ ] Change request documented
  - [ ] Business justification provided
  - [ ] Risk assessment completed
  - [ ] Rollback plan defined

- [ ] **Implementation**
  - [ ] Backup created and verified
  - [ ] Code changes peer reviewed
  - [ ] Changes committed to git
  - [ ] Check mode ran successfully

- [ ] **Deployment**
  - [ ] Approval obtained (manager/lead)
  - [ ] Maintenance window scheduled
  - [ ] Team notified
  - [ ] Deploy executed

- [ ] **Verification**
  - [ ] Health check passed
  - [ ] Dashboard verified
  - [ ] No errors in logs
  - [ ] User-facing impact verified

- [ ] **Post-Deployment**
  - [ ] Monitored for 24 hours
  - [ ] No false positives observed
  - [ ] Documentation updated
  - [ ] Change log entry created

---

**Last Updated**: November 17, 2025
**Status**: Production-Ready
**Review Schedule**: Quarterly
