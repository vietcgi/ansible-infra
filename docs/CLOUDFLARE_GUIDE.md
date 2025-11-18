# Cloudflare Integration - Comprehensive Operations Guide

**Date**: November 17, 2025
**Purpose**: Complete operational manual for Cloudflare configuration management
**Audience**: Infrastructure operators, DevOps engineers

---

## Table of Contents

1. [Safe Change Workflow](#safe-change-workflow)
2. [Common Operations](#common-operations)
3. [Emergency Procedures](#emergency-procedures)
4. [Troubleshooting Guide](#troubleshooting-guide)
5. [Backup & Recovery](#backup--recovery)
6. [Rollback Procedures](#rollback-procedures)
7. [Change Log Template](#change-log-template)
8. [Maintenance Windows](#maintenance-windows)

---

## Safe Change Workflow

All Cloudflare configuration changes should follow this 9-step workflow:

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

## Troubleshooting Guide

### Quick Diagnosis

```bash
# View integration status
ansible-playbook examples/cloudflare_preflight.yml --ask-vault-pass

# Run health check
/usr/local/bin/cloudflare-health-check

# View logs
tail -f /var/log/cloudflare/health-check.log
```

---

### API Response Structure Reference

#### Success Response Format

All successful Cloudflare API responses follow this structure:

```json
{
  "success": true,
  "errors": [],
  "messages": [],
  "result": {
    // Actual response data
  }
}
```

**Key Fields**:
- `success`: Boolean - Always check this for API calls
- `result`: Object/Array - Actual data returned by the API
- `errors`: Array - Empty if successful
- `messages`: Array - Informational messages (can be present in successful responses)

#### Error Response Format

When an API call fails:

```json
{
  "success": false,
  "errors": [
    {
      "code": 1004,
      "message": "Invalid request headers"
    }
  ],
  "messages": [],
  "result": null
}
```

---

### Common Errors and Solutions

#### 1. Authentication Failed (Status 401/403)

**Symptom**: `FAILED ✗` in pre-flight validation or role execution

**Error Response**:
```json
{
  "success": false,
  "errors": [
    {
      "code": 9103,
      "message": "Authentication error"
    }
  ]
}
```

**Causes and Fixes**:

| Cause | Fix |
|-------|-----|
| API token invalid/expired | Generate new token in Cloudflare dashboard |
| Token doesn't have required scopes | Create token with Zone:DNS:Edit, Zone:WAF:Edit, Zone:Settings:Edit scopes |
| Whitelist IP restriction | Check token IP whitelist allows your Ansible controller IP |
| Token revoked | Create new API token in Cloudflare dashboard |

**Debug**:
```bash
# Test token validity
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.cloudflare.com/client/v4/user

# Should return user information if valid
```

---

#### 2. Zone Not Found (HTTP 404 or "not found in result")

**Symptom**: "Zone 'example.com' not found in Cloudflare account"

**Error Response**:
```json
{
  "success": true,
  "result": []  // Empty array when zone not found
}
```

**Causes and Fixes**:

| Cause | Fix |
|-------|-----|
| Domain not added to Cloudflare | Add domain to Cloudflare account dashboard |
| DNS not delegated to Cloudflare | Update registrar nameservers to Cloudflare NS |
| Wrong domain name in variable | Verify `cloudflare_domain` matches Cloudflare configuration |
| Typo in domain name | Check for typos (example.com vs example.co) |

**Debug**:
```bash
# List all zones in account
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.cloudflare.com/client/v4/zones?per_page=50

# Look for your domain in the results array
```

---

#### 3. Permission Denied (HTTP 403 for specific features)

**Symptom**: WAF/DDoS/SSL deployment fails, but DNS works

**Error Response**:
```json
{
  "success": false,
  "errors": [
    {
      "code": 1003,
      "message": "Invalid request - missing required parameters"
    }
  ]
}
```

**Actual Issue**: Token lacks permissions for that specific feature

**Causes and Fixes**:

| Feature | Required Scope | Fix |
|---------|----------------|-----|
| DNS records | `Zone:DNS:Edit` | Token has this scope |
| WAF rules | `Zone:WAF:Edit` | Add this scope to token |
| SSL/TLS settings | `Zone:Settings:Edit` | Add this scope to token |
| Monitoring | `Account:Audit Log:Read` | Add this scope to token |

**Debug**:
```bash
# Test specific feature permission
curl -X PATCH \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.cloudflare.com/client/v4/zones/ZONE_ID/settings/waf \
  -d '{"value":"on"}'

# If 403: You don't have WAF:Edit permission
```

---

#### 4. Invalid Request Body (HTTP 400)

**Symptom**: "Invalid request" error during WAF/DDoS/SSL configuration

**Error Response**:
```json
{
  "success": false,
  "errors": [
    {
      "code": 1004,
      "message": "Invalid request - body does not match schema"
    }
  ]
}
```

**Causes and Fixes**:

| Cause | Fix |
|-------|-----|
| Wrong value format for setting | Check expected format (enum vs string vs number) |
| Unsupported value for setting | Verify setting is available on your Cloudflare plan |
| Missing required field | Check API documentation for required fields |
| JSON parsing error | Validate JSON in request body is well-formed |

**Example**: WAF Sensitivity Invalid
```yaml
# ❌ WRONG - Should be string
body:
  value: high  # String, not number

#  CORRECT
body:
  value: "high"
```

---

#### 5. Rate Limit Exceeded (HTTP 429)

**Symptom**: Deployment fails partway through with "rate limit" message

**Error Response**:
```json
{
  "success": false,
  "errors": [
    {
      "code": 1012,
      "message": "Request rate limit exceeded"
    }
  ]
}
```

**Causes and Fixes**:

| Cause | Fix |
|-------|-----|
| Too many API calls in short time | Add delays between requests |
| Multiple deployments running simultaneously | Run sequentially instead |
| Large number of DNS records | Split into smaller batches |

**Prevent**:
```yaml
# Add delay between API calls
- name: Configure setting with rate limit safety
  ansible.builtin.uri:
    url: "..."
    ...
  register: result

- name: Wait before next API call
  ansible.builtin.pause:
    seconds: 1
```

---

#### 6. Invalid TTL Value

**Symptom**: DNS record creation fails with invalid TTL

**Error Response**:
```json
{
  "success": false,
  "errors": [
    {
      "code": 1004,
      "message": "TTL out of valid range"
    }
  ]
}
```

**Valid TTL Ranges**:
- Proxied records (orange cloud): 60, 120, 300, 1800, 3600
- DNS only (gray cloud): 60 to 86400 seconds (or 1 for auto)

**Fix**:
```yaml
cloudflare_dns_records:
  - zone: "example.com"
    record: "www"
    type: "A"
    value: "192.0.2.1"
    ttl: 3600  #  Valid
    proxied: true  # If true, must use specific values (60, 120, 300, 1800, 3600)
```

---

### Log File Locations and Analysis

#### Health Check Logs

```bash
# View health check output
tail -f /var/log/cloudflare/health-check.log

# Sample output
API authentication: PASSED
Zone found: example.com (zone_id=abc123...)
DNS records: 5 configured
WAF status: ENABLED
DDoS status: ENABLED
SSL/TLS: ENABLED
```

#### Ansible Playbook Execution

```bash
# Run with verbose output for debugging
ansible-playbook examples/cloudflare_deployment.yml \
  --ask-vault-pass \
  -vvv  # Triple verbose for maximum detail

# Check specific task
ansible-playbook examples/cloudflare_deployment.yml \
  --ask-vault-pass \
  -vvv \
  --tags cloudflare_waf  # Only run WAF tasks
```

#### Manual API Testing

```bash
# Test DNS record creation
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.cloudflare.com/client/v4/zones/ZONE_ID/dns_records \
  -d '{
    "type": "A",
    "name": "test.example.com",
    "content": "192.0.2.1",
    "ttl": 3600,
    "proxied": false
  }'

# Parse response
curl ... | jq '.result'  # Extract result field
curl ... | jq '.errors'  # Show errors if any
```

---

### Debugging Checklist

#### Pre-Deployment

- [ ] Run pre-flight validation: `ansible-playbook examples/cloudflare_preflight.yml`
- [ ] Verify API token in vault: `ansible-vault view inventories/.../cloudflare_vault.yml`
- [ ] Check domain is in Cloudflare: Dashboard → Sites → Your Domain
- [ ] Verify DNS delegation: Check registrar uses Cloudflare nameservers
- [ ] Test API token manually: `curl -H "Authorization: Bearer TOKEN" https://api.cloudflare.com/client/v4/user`

#### During Deployment

- [ ] Use `--check` mode first: `ansible-playbook ... --check`
- [ ] Review planned changes carefully
- [ ] Use `-vvv` flag for verbose output
- [ ] Check for warnings or errors in output

#### After Deployment

- [ ] Verify in Cloudflare dashboard: Check DNS, WAF, SSL/TLS settings
- [ ] Run health check: `/usr/local/bin/cloudflare-health-check`
- [ ] Check logs: `tail -f /var/log/cloudflare/health-check.log`
- [ ] Test DNS resolution: `dig www.example.com` or `nslookup`

---

### Advanced Debugging

#### Test Individual API Endpoints

```bash
# Get zone ID
ZONE_ID=$(curl -s \
  -H "Authorization: Bearer TOKEN" \
  https://api.cloudflare.com/client/v4/zones?name=example.com | \
  jq -r '.result[0].id')

# Test WAF endpoint
curl -X PATCH \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/security_level \
  -d '{"value":"high"}' | jq '.'

# Test DDoS endpoint
curl -X PATCH \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/advanced_ddos \
  -d '{"value":"on"}' | jq '.'
```

#### Extract Zone ID for Manual Testing

```bash
# From Ansible facts
ansible localhost -m debug -a "var=cloudflare_zone_id" \
  -e @inventories/production/group_vars/all/cloudflare_vault.yml \
  --ask-vault-pass

# Or from API directly
ZONE_ID=$(curl -s \
  -H "Authorization: Bearer $TOKEN" \
  https://api.cloudflare.com/client/v4/zones?name=example.com | \
  jq -r '.result[0].id')

echo "Zone ID: $ZONE_ID"
```

#### Monitor API Rate Limits

```bash
# Check remaining rate limit in response headers
curl -i \
  -H "Authorization: Bearer TOKEN" \
  https://api.cloudflare.com/client/v4/user | head -20

# Look for: X-RateLimit-Remaining header
# Typically: 1200 requests per 5 minutes
```

---

### Plan-Specific Limitations

#### Free Plan

- No WAF rules (enterprise feature)
- Limited DDoS protection
- No advanced SSL/TLS
- No custom page rules

**Error**: "This feature requires a higher plan"

**Fix**: Upgrade to Pro or Business plan

#### Pro/Business Plans

- WAF available
- Advanced DDoS
- Custom SSL/TLS rules
- Full API access

#### Enterprise Plan

- All features available
- API rate limit: 1200 req/5 min
- Custom rate limits possible
- Dedicated support

---

## Backup & Recovery

### Quick Reference - Before First Deployment

```bash
# Export all DNS records
curl -H "Authorization: Bearer TOKEN" \
  https://api.cloudflare.com/client/v4/zones/ZONE_ID/dns_records | \
  jq '.result' > cloudflare_dns_backup_$(date +%Y%m%d).json

# Export WAF rules
curl -H "Authorization: Bearer TOKEN" \
  https://api.cloudflare.com/client/v4/zones/ZONE_ID/firewall/rules | \
  jq '.result' > cloudflare_waf_backup_$(date +%Y%m%d).json

# Export all settings
curl -H "Authorization: Bearer TOKEN" \
  https://api.cloudflare.com/client/v4/zones/ZONE_ID/settings | \
  jq '.result' > cloudflare_settings_backup_$(date +%Y%m%d).json
```

---

### Pre-Deployment Backup Strategy

#### Why Backup?

1. **Disaster Recovery** - Restore if automation breaks something
2. **Change Audit Trail** - Compare before/after configurations
3. **Rollback Point** - Known-good state to revert to
4. **Compliance** - Document configuration history
5. **Team Safety** - Prevent accidental data loss

#### When to Backup

 **MUST DO** before:
- First Cloudflare automation deployment
- Major version upgrades of the framework
- Large configuration changes (WAF rule overhaul, SSL/TLS mode change)
- DNS migration to new registrar

 **SHOULD DO** before:
- Regular deployments (monthly is reasonable)
- Significant updates to vars
- Team changes (new ops person taking over)

---

### Automated Backup Playbook

Save as `examples/cloudflare_backup.yml`:

```yaml
---
- name: Backup Cloudflare Configuration
  hosts: localhost
  gather_facts: false

  vars:
    cloudflare_api_token: "{{ vault_cloudflare_api_token }}"
    cloudflare_domain: "{{ vault_cloudflare_domain }}"
    backup_dir: "backups/cloudflare/{{ cloudflare_domain }}"

  tasks:
    - name: Create backup directory
      ansible.builtin.file:
        path: "{{ backup_dir }}"
        state: directory
        mode: '0700'

    - name: Get zone ID
      ansible.builtin.uri:
        url: "https://api.cloudflare.com/client/v4/zones?name={{ cloudflare_domain }}"
        method: GET
        headers:
          Authorization: "Bearer {{ cloudflare_api_token }}"
      register: zone_lookup
      changed_when: false
      no_log: true

    - name: Set zone ID fact
      ansible.builtin.set_fact:
        zone_id: "{{ zone_lookup.json.result[0].id }}"

    - name: Backup DNS records
      ansible.builtin.uri:
        url: "https://api.cloudflare.com/client/v4/zones/{{ zone_id }}/dns_records?per_page=500"
        method: GET
        headers:
          Authorization: "Bearer {{ cloudflare_api_token }}"
      register: dns_records
      changed_when: false
      no_log: true

    - name: Save DNS records to file
      ansible.builtin.copy:
        content: "{{ dns_records.json.result | to_nice_json }}"
        dest: "{{ backup_dir }}/dns_records_{{ ansible_date_time.iso8601_basic }}.json"
        mode: '0600'

    - name: Backup WAF rules
      ansible.builtin.uri:
        url: "https://api.cloudflare.com/client/v4/zones/{{ zone_id }}/firewall/rules?per_page=500"
        method: GET
        headers:
          Authorization: "Bearer {{ cloudflare_api_token }}"
      register: waf_rules
      changed_when: false
      no_log: true

    - name: Save WAF rules to file
      ansible.builtin.copy:
        content: "{{ waf_rules.json.result | to_nice_json }}"
        dest: "{{ backup_dir }}/waf_rules_{{ ansible_date_time.iso8601_basic }}.json"
        mode: '0600'

    - name: Backup all zone settings
      ansible.builtin.uri:
        url: "https://api.cloudflare.com/client/v4/zones/{{ zone_id }}/settings"
        method: GET
        headers:
          Authorization: "Bearer {{ cloudflare_api_token }}"
      register: all_settings
      changed_when: false
      no_log: true

    - name: Save settings to file
      ansible.builtin.copy:
        content: "{{ all_settings.json.result | to_nice_json }}"
        dest: "{{ backup_dir }}/settings_{{ ansible_date_time.iso8601_basic }}.json"
        mode: '0600'

  post_tasks:
    - name: Display backup summary
      ansible.builtin.debug:
        msg: |
          Cloudflare Backup Complete ✓
          ============================
          Domain: {{ cloudflare_domain }}
          Zone ID: {{ zone_id }}
          Location: {{ backup_dir }}/

          Backed Up:
          - DNS records: {{ dns_records.json.result | length }} records
          - WAF rules: {{ waf_rules.json.result | length }} rules
          - Settings: {{ all_settings.json.result | length }} settings
```

Usage:
```bash
ansible-playbook examples/cloudflare_backup.yml --ask-vault-pass
```

---

### Manual Backup Script

Create `scripts/backup_cloudflare.sh`:

```bash
#!/bin/bash
set -e

DOMAIN="${1:-example.com}"
API_TOKEN="${CLOUDFLARE_API_TOKEN}"
BACKUP_DIR="backups/cloudflare/${DOMAIN}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

if [ -z "$API_TOKEN" ]; then
    echo "ERROR: CLOUDFLARE_API_TOKEN not set"
    exit 1
fi

mkdir -p "$BACKUP_DIR"

echo "Backing up Cloudflare configuration for $DOMAIN..."

# Get Zone ID
ZONE_ID=$(curl -s \
    -H "Authorization: Bearer $API_TOKEN" \
    https://api.cloudflare.com/client/v4/zones?name=$DOMAIN | \
    jq -r '.result[0].id')

if [ -z "$ZONE_ID" ]; then
    echo "ERROR: Zone not found"
    exit 1
fi

echo "Zone ID: $ZONE_ID"

# Backup DNS records
echo "Backing up DNS records..."
curl -s \
    -H "Authorization: Bearer $API_TOKEN" \
    "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?per_page=500" | \
    jq '.result' > "$BACKUP_DIR/dns_${TIMESTAMP}.json"

# Backup WAF rules
echo "Backing up WAF rules..."
curl -s \
    -H "Authorization: Bearer $API_TOKEN" \
    "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/firewall/rules?per_page=500" | \
    jq '.result' > "$BACKUP_DIR/waf_${TIMESTAMP}.json"

# Backup settings
echo "Backing up zone settings..."
curl -s \
    -H "Authorization: Bearer $API_TOKEN" \
    "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings" | \
    jq '.result' > "$BACKUP_DIR/settings_${TIMESTAMP}.json"

echo "Backup complete!"
ls -lh "$BACKUP_DIR"/*.json
```

Usage:
```bash
export CLOUDFLARE_API_TOKEN="your-token"
bash scripts/backup_cloudflare.sh example.com
```

---

### Recovery Procedures

#### Restore DNS Records

```bash
# List available backups
ls -lh backups/cloudflare/example.com/dns_*.json

# Restore specific backup
BACKUP="backups/cloudflare/example.com/dns_20251117_120000.json"
ZONE_ID="abc123"
TOKEN="your-token"

# Recreate DNS records from backup
cat "$BACKUP" | jq -r '.[] | @json' | while read record; do
    echo "Restoring: $(echo $record | jq -r '.name')"
    curl -X POST \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
        -d "$record"
done
```

#### Rollback WAF Configuration

```bash
# Disable WAF temporarily
curl -X PATCH \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/waf \
    -d '{"value":"off"}'

# Revert code changes
git log --oneline | head -5
git checkout COMMIT_HASH -- roles/cloudflare_integration/

# Redeploy
ansible-playbook examples/cloudflare_deployment.yml --ask-vault-pass
```

---

### Backup Storage Best Practices

#### 1. Git Repository (with masking)

```bash
mkdir -p backups/cloudflare/example.com/
git add backups/cloudflare/example.com/
git commit -m "chore: backup Cloudflare configuration"
```

#### 2. Cloud Storage (Encrypted)

```bash
# AWS S3
aws s3 cp backups/cloudflare/ \
    s3://my-backup-bucket/cloudflare/ \
    --sse AES256 --recursive

# Azure Blob Storage
az storage blob upload-batch \
    -d backups -s backups/cloudflare/ \
    --account-name myaccount
```

---

### Disaster Recovery Checklist

- [ ] **Before First Deployment**
  - [ ] Export DNS records from Cloudflare dashboard
  - [ ] Export all zone settings via API
  - [ ] Test restore procedure on test domain
  - [ ] Store backups in 2+ locations

- [ ] **Monthly**
  - [ ] Run automated backup playbook
  - [ ] Verify backup files are valid JSON
  - [ ] Test restore procedure

- [ ] **Before Major Changes**
  - [ ] Create fresh backup
  - [ ] Get team approval
  - [ ] Have restore procedure ready

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

### Manual Rollback

If deployment breaks DNS or causes issues:

```bash
# Export current Cloudflare DNS records
curl -s \
  -H "Authorization: Bearer TOKEN" \
  https://api.cloudflare.com/client/v4/zones/ZONE_ID/dns_records \
  -H "Content-Type: application/json" | \
  jq '.result[]' > dns_backup.json

# Keep this backup before any future deployments!
```

### Revert Playbook Changes

```bash
# Revert to previous known-good configuration
git revert COMMIT_HASH

# Re-run deployment with reverted config
ansible-playbook examples/cloudflare_deployment.yml \
  --ask-vault-pass \
  --check
```

### Manual Cloudflare Dashboard Fix

1. Log into Cloudflare dashboard
2. Navigate to affected domain
3. DNS → Edit records directly
4. WAF → Adjust rules as needed
5. SSL/TLS → Change mode if needed

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

### Monitoring During Changes

#### What to Monitor

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

#### Dashboards to Check

| Dashboard | What to Check | Location |
|-----------|---------------|----------|
| Analytics | Traffic, errors, cache | Cloudflare → Your domain → Analytics |
| Real-Time Logs | Individual requests | Security → Real-Time Logs |
| WAF | Blocked requests | Security → WAF |
| DDoS | Attack traffic | Security → DDoS |
| SSL/TLS | Certificate status | SSL/TLS → Overview |
| Health Check | System status | Cloudflare dashboard |

---

### Change Approval Checklist

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

## Contact and Support

### Self-Help Resources

- Cloudflare API Docs: https://developers.cloudflare.com/api/
- Ansible Docs: https://docs.ansible.com/
- This framework: `docs/CLOUDFLARE_*.md`

### Debugging Information to Gather

When reporting issues, include:

```bash
# System info
ansible --version
python --version

# Vault variables (safely)
ansible-vault view inventories/.../cloudflare_vault.yml

# Pre-flight results
ansible-playbook examples/cloudflare_preflight.yml --ask-vault-pass 2>&1

# Logs
tail -100 /var/log/cloudflare/health-check.log

# Git status
cd /path/to/ansible-infra
git log --oneline -10
git status
```

---

## Success Indicators

 **Deployment is successful when**:

1. Pre-flight validation passes all checks
2. Playbook runs without errors
3. Cloudflare dashboard shows expected configuration
4. Health check script completes successfully
5. DNS queries resolve correctly
6. WAF logs show traffic processing
7. SSL/TLS certificate is valid

---

**Last Updated**: November 17, 2025
**Status**: Production-Ready
**Review Schedule**: Quarterly
