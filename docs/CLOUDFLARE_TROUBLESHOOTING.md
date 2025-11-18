# Cloudflare Integration - Troubleshooting Guide

**Date**: November 17, 2025
**Role**: cloudflare_integration
**Documentation**: API responses, error scenarios, and debugging techniques

---

## Quick Diagnosis

### Check Current Status

```bash
# View integration status
ansible-playbook examples/cloudflare_preflight.yml --ask-vault-pass

# Run health check
/usr/local/bin/cloudflare-health-check

# View logs
tail -f /var/log/cloudflare/health-check.log
```

---

## API Response Structure Reference

### Success Response Format

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

### Error Response Format

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

**Key Fields**:
- `success`: false
- `errors`: Array of error objects with `code` and `message`
- `result`: null or partial data

---

## Common Errors and Solutions

### 1. Authentication Failed (Status 401/403)

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

### 2. Zone Not Found (HTTP 404 or "not found in result")

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

### 3. Permission Denied (HTTP 403 for specific features)

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

### 4. Invalid Request Body (HTTP 400)

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

# ✅ CORRECT
body:
  value: "high"
```

---

### 5. Rate Limit Exceeded (HTTP 429)

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

### 6. Invalid TTL Value

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
    ttl: 3600  # ✅ Valid
    proxied: true  # If true, must use specific values (60, 120, 300, 1800, 3600)
```

---

## Log File Locations and Analysis

### Health Check Logs

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

### Ansible Playbook Execution

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

### Manual API Testing

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

## Debugging Checklist

### Pre-Deployment

- [ ] Run pre-flight validation: `ansible-playbook examples/cloudflare_preflight.yml`
- [ ] Verify API token in vault: `ansible-vault view inventories/.../cloudflare_vault.yml`
- [ ] Check domain is in Cloudflare: Dashboard → Sites → Your Domain
- [ ] Verify DNS delegation: Check registrar uses Cloudflare nameservers
- [ ] Test API token manually: `curl -H "Authorization: Bearer TOKEN" https://api.cloudflare.com/client/v4/user`

### During Deployment

- [ ] Use `--check` mode first: `ansible-playbook ... --check`
- [ ] Review planned changes carefully
- [ ] Use `-vvv` flag for verbose output
- [ ] Check for warnings or errors in output

### After Deployment

- [ ] Verify in Cloudflare dashboard: Check DNS, WAF, SSL/TLS settings
- [ ] Run health check: `/usr/local/bin/cloudflare-health-check`
- [ ] Check logs: `tail -f /var/log/cloudflare/health-check.log`
- [ ] Test DNS resolution: `dig www.example.com` or `nslookup`

---

## Advanced Debugging

### Test Individual API Endpoints

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

### Extract Zone ID for Manual Testing

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

### Monitor API Rate Limits

```bash
# Check remaining rate limit in response headers
curl -i \
  -H "Authorization: Bearer TOKEN" \
  https://api.cloudflare.com/client/v4/user | head -20

# Look for: X-RateLimit-Remaining header
# Typically: 1200 requests per 5 minutes
```

---

## Plan-Specific Limitations

### Free Plan

- No WAF rules (enterprise feature)
- Limited DDoS protection
- No advanced SSL/TLS
- No custom page rules

**Error**: "This feature requires a higher plan"

**Fix**: Upgrade to Pro or Business plan

### Pro/Business Plans

- WAF available
- Advanced DDoS
- Custom SSL/TLS rules
- Full API access

### Enterprise Plan

- All features available
- API rate limit: 1200 req/5 min
- Custom rate limits possible
- Dedicated support

---

## Rollback Procedures

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

✅ **Deployment is successful when**:

1. Pre-flight validation passes all checks
2. Playbook runs without errors
3. Cloudflare dashboard shows expected configuration
4. Health check script completes successfully
5. DNS queries resolve correctly
6. WAF logs show traffic processing
7. SSL/TLS certificate is valid

---

**Last Updated**: November 17, 2025
**Maintainer**: Sentinel Infrastructure
**Next Review**: 6 months or upon major Cloudflare API changes
