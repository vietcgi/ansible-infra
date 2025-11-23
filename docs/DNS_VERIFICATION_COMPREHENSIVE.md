# Comprehensive DNS Verification Guide

## Overview

Complete DNS verification system for all email authentication records (DMARC, DKIM, SPF) with automatic duplicate detection, cleanup, and post-deployment validation.

## Architecture

### Three-Layer Verification System

```
┌─────────────────────────────────────────────────────────────┐
│                   CONFIGURATION LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  • DKIM Setup (dkim-setup.yml)                              │
│  • SPF Setup (spf-setup.yml)                                │
│  • DMARC Setup with Built-in Cleanup (dmarc-setup.yml)      │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                  VERIFICATION LAYER                          │
├─────────────────────────────────────────────────────────────┤
│  • DKIM Verification (dkim-verification.yml)                │
│  • SPF Verification (spf-verification.yml)                  │
│  • DMARC Verification (dmarc-verification.yml)              │
│  → Post-deployment record validation                        │
│  → Format and structure checking                            │
│  → Count verification (exactly 1 record)                    │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                   SUMMARY LAYER                              │
├─────────────────────────────────────────────────────────────┤
│  • DNS Verification Summary (dns-verification-summary.yml)  │
│  → Unified report of all records                            │
│  → Status overview                                          │
│  → Next steps and testing commands                          │
└─────────────────────────────────────────────────────────────┘
```

## DNS Records Overview

| Record | Location | Count | Criticality | Verification |
|--------|----------|-------|-------------|--------------|
| **DKIM** | `selector._domainkey.domain` | 1 per selector | HIGH | ✓ Enforced |
| **DMARC** | `_dmarc.domain` | Exactly 1 | CRITICAL | ✓ Enforced + Cleanup |
| **SPF** | `domain` (root) | Exactly 1 | HIGH | ✓ Verified |

## File Structure

```
roles/email-delivery/tasks/
├── main.yml                        # Main task orchestration
├── dkim-setup.yml                  # DKIM key generation
├── dkim-verification.yml           # NEW: DKIM verification
├── spf-setup.yml                   # SPF record creation
├── spf-verification.yml            # NEW: SPF verification
├── dmarc-setup.yml                 # DMARC with cleanup logic
├── dmarc-verification.yml          # DMARC verification
└── dns-verification-summary.yml    # NEW: Unified summary
```

## DMARC Setup with Built-in Cleanup

**File**: `dmarc-setup.yml`

### Features

1. **Duplicate Detection**
   - Queries Cloudflare for existing `_dmarc.*` records
   - Counts total records
   - Reports findings

2. **Intelligent Cleanup** (if > 1 record found)
   - Identifies most complete record
   - Selects based on presence of: `sp=`, `pct=`, `rua=`, `ruf=`
   - Deletes all other records
   - Keeps the most complete one

3. **Conditional Creation**
   - Only creates/updates if 0 or 1 records exist after cleanup
   - Idempotent - safe to run multiple times

### Workflow

```
Query existing DMARC records
    ├─ 0 records found → Create new record
    ├─ 1 record found → Verify format, optionally update
    └─ >1 records found
       ├─ Identify most complete
       ├─ Delete duplicates
       └─ Create/update if needed
```

### Example Output

```
Found 3 existing DMARC record(s) for _dmarc.example.com
Record IDs: id1, id2, id3

Identifying most complete record...
Keeping record with sp=, pct=, rua=, ruf= fields
Deleting 2 duplicate records

✓ DMARC Record Status
Policy: none
Report Email: dmarc-reports@example.com
Forensics Email: dmarc-forensics@example.com
Record(s) after setup: 1 (created or verified)
```

## DKIM Verification

**File**: `dkim-verification.yml`

### Verification Steps

1. Fetch DKIM records from Cloudflare
2. Count records for selector
3. Validate format: `v=DKIM1; k=rsa; p=<key>`
4. Display record details
5. Assert exactly 1 record exists

### Output Example

```
════════════════════════════════════════════════════════
DKIM Record Verification
════════════════════════════════════════════════════════
Total DKIM records found: 1
Selector: default
✓ SUCCESS: Exactly one DKIM record exists

Record 1:
Name: default._domainkey.example.com
Type: TXT
Content (truncated): v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BA...
TTL: 3600
ID: abc123def456

════════════════════════════════════════════════════════
✓ DKIM Configuration Verified
════════════════════════════════════════════════════════
```

## SPF Verification

**File**: `spf-verification.yml`

### Verification Steps

1. Fetch all TXT records for domain
2. Filter for SPF records (starting with `v=spf1`)
3. Count SPF records (should be exactly 1 per RFC 7208)
4. Validate format
5. Display full SPF record

### Output Example

```
════════════════════════════════════════════════════════
SPF Record Verification
════════════════════════════════════════════════════════
Total SPF records found: 1
Domain: example.com
✓ SUCCESS: Exactly one SPF record exists

Record 1:
Name: example.com
Type: TXT
Content: v=spf1 mx include:sendgrid.net -all
TTL: 3600
ID: xyz789abc123

════════════════════════════════════════════════════════
✓ SPF Configuration Verified
════════════════════════════════════════════════════════
```

## DMARC Verification

**File**: `dmarc-verification.yml`

### Verification Steps

1. Fetch `_dmarc.*` records from Cloudflare
2. Count records
3. Assert exactly 1 exists
4. Validate format: starts with `v=DMARC1`
5. Display record content and ID

### Output Example

```
════════════════════════════════════════════════════════
DMARC Record Verification
════════════════════════════════════════════════════════
Total DMARC records found: 1
✓ SUCCESS: Exactly one DMARC record exists

Record Details:
  Name: _dmarc.example.com
  Type: TXT
  Content: v=DMARC1; p=none; sp=quarantine; pct=100; ...
  TTL: 3600
  ID: 49cf509cb55f92ab2b39ee0483b46d00

✓ Record format is valid

════════════════════════════════════════════════════════
✓ DMARC configuration is correct and ready
════════════════════════════════════════════════════════
```

## Unified Summary

**File**: `dns-verification-summary.yml`

Displays comprehensive report of all DNS records after setup and verification.

### Output Example

```
═══════════════════════════════════════════════════════════════════════════
📋 EMAIL AUTHENTICATION DNS RECORDS VERIFICATION SUMMARY
═══════════════════════════════════════════════════════════════════════════

Domain: example.com
DKIM Selector: default

───────────────────────────────────────────────────────────────────────────
Record Type       │ Expected    │ Actual      │ Status
───────────────────────────────────────────────────────────────────────────
DKIM              │ 1 record    │ Verified    │ ✓
DMARC             │ 1 record    │ Verified    │ ✓
SPF               │ 1 record    │ Verified    │ ✓
───────────────────────────────────────────────────────────────────────────

📌 DNS Record Details:

1. DKIM Record:
   Name: default._domainkey.example.com
   Type: TXT
   Status: ✓ Created and verified
   Format: v=DKIM1; k=rsa; p=<public_key>

2. DMARC Record:
   Name: _dmarc.example.com
   Type: TXT
   Status: ✓ Created and verified
   Policy: p=none; sp=quarantine
   Reporting: rua=mailto:dmarc-reports@example.com
              ruf=mailto:dmarc-forensics@example.com

3. SPF Record:
   Name: example.com (root)
   Type: TXT
   Status: ✓ Created and verified
   Format: v=spf1 mx -all

✓ ALL EMAIL AUTHENTICATION RECORDS VERIFIED AND READY
═══════════════════════════════════════════════════════════════════════════
```

## Execution Flow

### During Playbook Run

```
email-delivery role starts
    │
    ├─→ Configure Cloudflare DNS (if enabled)
    ├─→ Configure DKIM Keys and DNS Records
    ├─→ Configure SPF Records
    ├─→ Configure DMARC Records
    │   └─→ [Built-in: Check for duplicates → Clean up if needed]
    │
    ├─→ VERIFY DMARC Record Configuration
    │   └─→ [Assert exactly 1 record exists]
    │
    ├─→ VERIFY DKIM Record Configuration
    │   └─→ [Assert format and count]
    │
    ├─→ VERIFY SPF Record Configuration
    │   └─→ [Assert format and count]
    │
    ├─→ Display DNS Verification Summary
    │   └─→ [Show unified report]
    │
    ├─→ Configure TLS Certificates
    ├─→ Configure KumoMTA for Delivery
    └─→ ... (other tasks)
```

## Tag Usage

All verification tasks support Ansible tags for selective execution:

```bash
# Run full setup with verification
ansible-playbook email-delivery-setup.yml

# Run only verification tasks
ansible-playbook email-delivery-setup.yml --tags verify

# Verify only DMARC
ansible-playbook email-delivery-setup.yml --tags verify,dmarc

# Verify DKIM and SPF only
ansible-playbook email-delivery-setup.yml --tags verify,dkim,spf

# Skip verification entirely
ansible-playbook email-delivery-setup.yml --skip-tags verify
```

## Failure Scenarios & Recovery

### Scenario 1: Multiple DMARC Records
**Detection**: `dmarc-setup.yml` finds > 1 record
**Action**: Automatically identifies most complete, deletes others
**Result**: Verification passes after cleanup

### Scenario 2: Invalid DKIM Format
**Detection**: `dkim-verification.yml` fails format check
**Action**: Task fails with clear error message
**Recovery**: Manually recreate DKIM key and record

### Scenario 3: Missing SPF Record
**Detection**: `spf-verification.yml` finds 0 records
**Action**: Task fails with warning
**Recovery**: Check if SPF was created, recreate if needed

### Scenario 4: API Connection Error
**Detection**: URI calls to Cloudflare fail
**Action**: Task logs error and continues
**Recovery**: Check API token, zone ID, and network connectivity

## Testing & Validation

### Test 1: First-time Deployment
```bash
ansible-playbook playbooks/email-delivery-setup.yml \
  -e "email_domain=example.com" \
  -e "email_server_ip=192.0.2.1" \
  -e "cloudflare_api_token=..." \
  -e "cloudflare_zone_id=..."
```

**Expected**: All records created and verified

### Test 2: Idempotency (Run Twice)
```bash
# First run
ansible-playbook playbooks/email-delivery-setup.yml -e "..."

# Second run (should be idempotent)
ansible-playbook playbooks/email-delivery-setup.yml -e "..."
```

**Expected**: No changes on second run

### Test 3: Duplicate Cleanup
1. Manually create duplicate DMARC record in Cloudflare
2. Run playbook
3. Observe automatic duplicate removal

**Expected**: Playbook removes duplicates and verifies 1 record

### Test 4: Verify-Only Mode
```bash
# Skip setup, run only verification
ansible-playbook playbooks/email-delivery-setup.yml \
  -e "..." \
  --tags verify
```

**Expected**: Validates existing DNS records without changes

## Monitoring After Deployment

### Check DNS Propagation

```bash
# Check all email auth records
nslookup -type=TXT example.com
nslookup -type=TXT _dmarc.example.com
nslookup -type=TXT default._domainkey.example.com
```

### Verify Email Authentication

1. Send test email
2. Check email headers in Gmail
3. Look for:
   - `DKIM: PASS`
   - `SPF: PASS`
   - `DMARC: PASS`

### Monitor DMARC Reports

- Check mailbox: `dmarc-reports@example.com`
- Reports arrive daily at midnight UTC
- Analyze for authentication failures

## Related Documentation

- [DMARC Verification Logic](DMARC_VERIFICATION_LOGIC.md)
- [Email Delivery Setup](../playbooks/email-delivery-setup.yml)
- [Cloudflare Integration](../roles/cloudflare_integration)
- [KumoMTA Configuration](../roles/kumomta)

## Commits

- **7f07542** - feat: add DMARC verification logic to ensure single record exists
  - Created: `dmarc-verification.yml`
  - Updated: `dmarc-setup.yml` with cleanup logic
  - Updated: `main.yml`

- **017eefe** - feat: add comprehensive DNS verification for DKIM, DMARC, and SPF records
  - Created: `dkim-verification.yml`
  - Created: `spf-verification.yml`
  - Created: `dns-verification-summary.yml`
  - Updated: `main.yml` with all verification tasks

## Changelog

### v2.0 (2025-11-22)
- Added comprehensive DNS verification for all email auth records
- Created DKIM verification task
- Created SPF verification task
- Created unified DNS verification summary
- Updated main playbook to include all verification tasks
- Added tag support for selective verification runs

### v1.0 (2025-11-22)
- Initial DMARC verification implementation
- Built-in duplicate detection and cleanup
- DMARC-specific post-deployment verification
