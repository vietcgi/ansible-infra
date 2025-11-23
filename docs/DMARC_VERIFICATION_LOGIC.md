# DMARC Verification Logic Documentation

## Overview

The DMARC verification logic ensures that exactly **one** DMARC record exists in Cloudflare DNS, preventing duplicate records that cause email authentication validation failures.

## Problem Statement

When multiple DMARC records exist for the same domain (e.g., `_dmarc.vietcgi.nguoivietcali.com`), email authentication systems like Gmail will reject the DMARC policy as invalid, causing:
- DMARC validation: **FAIL** in email headers
- Email deliverability issues
- Inconsistent authentication results

## Solution Architecture

The verification logic is implemented in two Ansible task files:

### 1. **dmarc-setup.yml** - Creation with Built-in Verification

Located: `roles/email-delivery/tasks/dmarc-setup.yml`

**Workflow:**
```
1. Check for existing DMARC records
   └─ Query Cloudflare API for _dmarc.<domain> TXT records

2. If multiple records found (count > 1)
   ├─ Fetch details of all existing records
   ├─ Identify the most complete record (has sp=, pct=, rua=, ruf=)
   └─ Delete all other records, keeping only the most complete one

3. Create or update DMARC record
   └─ Only if 0 or 1 records exist after cleanup

4. Display status
   └─ Shows final record count and configuration
```

**Key Features:**
- Idempotent: Safe to run multiple times
- Automatic cleanup: Removes duplicates if found
- Intelligent selection: Keeps the most complete/correct record
- API-based: Uses Cloudflare REST API for direct control

### 2. **dmarc-verification.yml** - Post-Deployment Verification

Located: `roles/email-delivery/tasks/dmarc-verification.yml`

**Workflow:**
```
1. Fetch all DMARC records for the domain
2. Count total records
3. Validate record format (must start with v=DMARC1)
4. Assert exactly 1 record exists
   ├─ If 1: SUCCESS ✓
   ├─ If 0: FAIL - record not created
   └─ If >1: FAIL - duplicates found
5. Display detailed record information
```

**Output Example:**
```
════════════════════════════════════════════════════════
DMARC Record Verification
════════════════════════════════════════════════════════
Total DMARC records found: 1
✓ SUCCESS: Exactly one DMARC record exists

Record Details:
  Name: _dmarc.vietcgi.nguoivietcali.com
  Type: TXT
  Content: v=DMARC1; p=none; sp=quarantine; pct=100; rua=mailto:...
  TTL: 3600
  ID: 49cf509cb55f92ab2b39ee0483b46d00

✓ Record format is valid

════════════════════════════════════════════════════════
✓ DMARC configuration is correct and ready
════════════════════════════════════════════════════════
```

## Integration in Main Playbook

The verification is called in: `roles/email-delivery/tasks/main.yml`

```yaml
- name: Configure DMARC Records
  ansible.builtin.include_tasks: dmarc-setup.yml

- name: Verify DMARC Record Configuration
  ansible.builtin.include_tasks: dmarc-verification.yml
  when: cloudflare_api_token is defined and cloudflare_api_token != ""
```

**Execution Order:**
1. DKIM setup
2. SPF setup
3. **DMARC setup** (with built-in verification)
4. **DMARC verification** (post-deployment check)
5. TLS certificates
6. KumoMTA delivery configuration

## How It Works: Technical Details

### Step 1: Check Existing Records

```yaml
- name: Check for existing DMARC records
  ansible.builtin.uri:
    url: "https://api.cloudflare.com/client/v4/zones/{{ cloudflare_zone_id }}/dns_records?type=TXT&name=_dmarc.{{ email_domain }}"
    method: GET
    headers:
      Authorization: "Bearer {{ cloudflare_api_token }}"
```

Uses Cloudflare API to query DNS records. Filter parameters:
- `type=TXT` - Only TXT records
- `name=_dmarc.{{ email_domain }}` - Exact domain match

### Step 2: Intelligent Duplicate Cleanup

If multiple records exist:
1. Fetch details of each record
2. Identify complete records using Jinja2 filters:
   ```yaml
   records_with_all_fields: "{{ dmarc_record_details.results
     | map(attribute='json.result')
     | select('defined')
     | select('search', 'sp=')
     | select('search', 'pct=')
     | select('search', 'rua=')
     | select('search', 'ruf=')
     | list }}"
   ```
3. Keep the most complete record
4. Delete all others via API

### Step 3: Create/Update Record

Only executes if record count is 0 or 1:

```yaml
- name: Create DMARC TXT Record
  community.general.cloudflare_dns:
    zone: "{{ email_domain }}"
    record: "_dmarc"
    type: "TXT"
    value: "v=DMARC1; p={{ dmarc_policy }}; sp={{ dmarc_subdomain_policy }}; ..."
    ttl: 3600
```

### Step 4: Verification

Post-deployment verification ensures configuration is correct:

```yaml
- name: Verify DMARC record count
  assert:
    that:
      - dmarc_record_count | int == 1
    fail_msg: |
      DMARC validation failed:
      - Expected: 1 DMARC record
      - Found: {{ dmarc_record_count | int }}
```

## Variables Used

| Variable | Default | Description |
|----------|---------|-------------|
| `email_domain` | - | Domain for DMARC record (e.g., `vietcgi.nguoivietcali.com`) |
| `cloudflare_zone_id` | - | Cloudflare zone ID (from API token) |
| `cloudflare_api_token` | - | Bearer token for Cloudflare API |
| `dmarc_policy` | `none` | DMARC policy (none, quarantine, reject) |
| `dmarc_subdomain_policy` | `quarantine` | Subdomain policy |
| `dmarc_percent` | `100` | Percentage of messages to filter |
| `dmarc_report_email` | `dmarc-reports@{{ email_domain }}` | Aggregate report recipient |
| `dmarc_forensics_email` | `dmarc-forensics@{{ email_domain }}` | Forensics report recipient |

## Failure Scenarios & Recovery

### Scenario 1: Multiple DMARC Records Found
**Symptom:** Playbook shows "Found 3 existing DMARC record(s)"

**Automatic Recovery:**
1. `dmarc-setup.yml` identifies the most complete record
2. Deletes all other records
3. Keeps the correct one
4. `dmarc-verification.yml` confirms exactly 1 record remains

### Scenario 2: No DMARC Record Found
**Symptom:** "DMARC record not created"

**Recovery:**
1. Check Cloudflare API credentials
2. Verify `cloudflare_api_token` and `cloudflare_zone_id` are correct
3. Ensure domain exists in Cloudflare zone
4. Rerun playbook

### Scenario 3: Verification Fails After Cleanup
**Symptom:** Assert error after duplicate deletion

**Manual Steps:**
1. Login to Cloudflare dashboard
2. Navigate to DNS records
3. Find `_dmarc.{{ email_domain }}` TXT record
4. Verify exactly 1 record exists
5. Ensure record format: `v=DMARC1; p=none; sp=quarantine; ...`
6. Rerun playbook

## Testing the Logic

### Test 1: First-time Deployment
```bash
ansible-playbook playbooks/email-delivery-setup.yml \
  -e "email_domain=example.com" \
  -e "email_server_ip=192.0.2.1" \
  -e "cloudflare_api_token=..." \
  -e "cloudflare_zone_id=..."
```

**Expected Result:** Single DMARC record created and verified

### Test 2: Idempotency (Run Twice)
```bash
# First run
ansible-playbook playbooks/email-delivery-setup.yml -e "..."

# Second run (should be idempotent)
ansible-playbook playbooks/email-delivery-setup.yml -e "..."
```

**Expected Result:** No changes made (already configured)

### Test 3: Duplicate Cleanup
1. Manually create a duplicate DMARC record in Cloudflare
2. Run playbook
3. Observe automatic duplicate removal and cleanup

## Monitoring

To verify DMARC status after deployment:

```bash
# Check DNS record
nslookup -type=TXT _dmarc.example.com

# Should return exactly 1 record:
# _dmarc.example.com text = "v=DMARC1; p=none; sp=quarantine; ..."
```

## Related Documentation

- [Email Delivery Setup](email-delivery-setup.yml) - Main playbook
- [Cloudflare Integration](cloudflare_integration.md) - DNS provider config
- [DKIM Configuration](DKIM_SETUP.md) - DKIM signing setup
- [SPF Configuration](SPF_SETUP.md) - SPF record configuration

## Commits

- **7f07542** - "feat: add DMARC verification logic to ensure single record exists"
  - New: `roles/email-delivery/tasks/dmarc-verification.yml`
  - Updated: `roles/email-delivery/tasks/dmarc-setup.yml`
  - Updated: `roles/email-delivery/tasks/main.yml`

## Changelog

### v1.0 (2025-11-22)
- Initial implementation of DMARC verification logic
- Built-in duplicate detection and cleanup in setup task
- Post-deployment verification task
- Automatic intelligent record selection (keeps most complete)
- Comprehensive error handling and reporting
