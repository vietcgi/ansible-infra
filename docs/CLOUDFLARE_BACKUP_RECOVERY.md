# Cloudflare Integration - Backup and Recovery Procedures

**Date**: November 17, 2025
**Purpose**: Comprehensive guide for backing up and recovering Cloudflare configuration
**Critical**: Always backup before deploying automation

---

## Quick Reference

### Before First Deployment
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

## Pre-Deployment Backup Strategy

### Why Backup?

1. **Disaster Recovery** - Restore if automation breaks something
2. **Change Audit Trail** - Compare before/after configurations
3. **Rollback Point** - Known-good state to revert to
4. **Compliance** - Document configuration history
5. **Team Safety** - Prevent accidental data loss

### When to Backup

✅ **MUST DO** before:
- First Cloudflare automation deployment
- Major version upgrades of the framework
- Large configuration changes (WAF rule overhaul, SSL/TLS mode change)
- DNS migration to new registrar

✅ **SHOULD DO** before:
- Regular deployments (monthly is reasonable)
- Significant updates to vars
- Team changes (new ops person taking over)

---

## Automated Backup Playbook

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

## Manual Backup Script

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

## Recovery Procedures

### Restore DNS Records

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

### Rollback WAF Configuration

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

## Backup Storage Best Practices

### 1. Git Repository (with masking)

```bash
mkdir -p backups/cloudflare/example.com/
git add backups/cloudflare/example.com/
git commit -m "chore: backup Cloudflare configuration"
```

### 2. Cloud Storage (Encrypted)

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

## Disaster Recovery Checklist

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

**Last Updated**: November 17, 2025
**Status**: Production-Ready
