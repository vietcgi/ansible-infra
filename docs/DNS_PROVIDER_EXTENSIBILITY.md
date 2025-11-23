# DNS Provider Extensibility Guide

## Overview

The email delivery setup playbook is designed to support multiple DNS providers. Currently, Cloudflare is implemented. This guide shows how to extend support to other DNS providers like AWS Route53, Google Cloud DNS, Azure DNS, etc.

## Architecture

The playbook uses a provider-based routing pattern:

```
email-delivery-setup.yml
├── Pre-tasks (generate DKIM, build DNS records)
├── KumoMTA role (email server + DKIM key generation)
├── Tasks (add DKIM DNS record to array)
├── Provider-specific DNS role
│   ├── cloudflare_integration (current)
│   ├── route53_integration (example - to be implemented)
│   ├── google_dns_integration (to be implemented)
│   └── azure_dns_integration (to be implemented)
└── Post-tasks (health check, summary)
```

## Generic DNS Record Format

All DNS records use a standardized format in the playbook:

```yaml
dns_records:
  - zone: "example.com"              # Base domain/zone
    record: "mail"                   # Subdomain (or @ for root)
    type: "A"                        # Record type (A, MX, TXT, etc.)
    value: "192.0.2.1"              # Record value
    ttl: 3600                        # Time to live
    proxied: false                   # Proxy through provider (Cloudflare)
    state: "present"                 # present/absent
```

This format is provider-agnostic and defined in `playbooks/email-delivery-setup.yml` lines 117-158.

## Implementation Pattern

### For Cloudflare (Current Implementation)

**Role**: `roles/cloudflare_integration/`

**Key Task** (`roles/cloudflare_integration/tasks/main.yml` lines 64-78):
```yaml
- name: Create DNS records from configuration
  community.general.cloudflare_dns:
    zone: "{{ item.zone }}"
    record: "{{ item.record | default('@') }}"
    type: "{{ item.type }}"
    value: "{{ item.value }}"
    ttl: "{{ item.ttl | default(3600) }}"
    proxied: "{{ item.proxied | default(false) }}"
    api_token: "{{ cloudflare_api_token }}"
    state: "{{ item.state | default('present') }}"
  loop: "{{ cloudflare_dns_records | default([]) }}"
```

**Translates**:
- Generic `zone` → Cloudflare `zone`
- Generic `record` → Cloudflare `record`
- Uses Cloudflare-specific `api_token` and `proxied` parameters

### For AWS Route53 (Example Template)

**Role to Create**: `roles/route53_integration/`

**Structure**:
```
roles/route53_integration/
├── tasks/
│   └── main.yml (converts generic dns_records to Route53 format)
├── defaults/
│   └── main.yml (Route53 configuration)
└── README.md (documentation)
```

**Expected Implementation** (`roles/route53_integration/tasks/main.yml`):
```yaml
---
- name: Configure Route53 DNS Management
  when: route53_enabled | default(false) and route53_dns_enabled | default(false)
  block:
    - name: Create Route53 Hosted Zone records
      amazon.aws.route53:
        zone: "{{ item.zone }}"
        record: "{{ item.record }}.{{ item.zone if item.record != '@' else '' }}"
        type: "{{ item.type }}"
        value: "{{ item.value }}"
        ttl: "{{ item.ttl | default(3600) }}"
        state: "{{ item.state | default('present') }}"
      loop: "{{ route53_dns_records | default([]) }}"
      register: route53_results
```

## Step-by-Step: Adding a New DNS Provider

### 1. Create the Provider Role Directory

```bash
mkdir -p roles/route53_integration/tasks
mkdir -p roles/route53_integration/defaults
touch roles/route53_integration/tasks/main.yml
touch roles/route53_integration/defaults/main.yml
touch roles/route53_integration/README.md
```

### 2. Define Provider Variables (`defaults/main.yml`)

```yaml
---
# Route53 Integration Configuration
route53_enabled: false
route53_dns_enabled: false
route53_region: "us-east-1"
route53_access_key: ""
route53_secret_key: ""
# Map generic dns_records to route53_dns_records
route53_dns_records: "{{ dns_records | default([]) }}"
```

### 3. Implement DNS Record Creation (`tasks/main.yml`)

```yaml
---
- name: Configure Route53 DNS Management
  when: route53_enabled and route53_dns_enabled
  block:
    # Install required collection if needed
    - name: Install amazon.aws collection
      ansible.builtin.command:
        cmd: "ansible-galaxy collection install --force amazon.aws"
      changed_when: false
      delegate_to: localhost
      run_once: true

    # Create records
    - name: Create Route53 DNS records
      amazon.aws.route53:
        zone: "{{ item.zone }}"
        record: "{{ [item.record, item.zone] | select('defined') | join('.') if item.record != '@' else item.zone }}"
        type: "{{ item.type }}"
        value: "{{ item.value }}"
        ttl: "{{ item.ttl | default(3600) }}"
        aws_access_key: "{{ route53_access_key }}"
        aws_secret_key: "{{ route53_secret_key }}"
        region: "{{ route53_region }}"
        state: "{{ item.state | default('present') }}"
      loop: "{{ route53_dns_records | default([]) }}"
      when:
        - route53_dns_records is defined
        - item.value != ""
```

### 4. Update the Playbook to Support the New Provider

**File**: `playbooks/email-delivery-setup.yml`

**Variables Section** (add to lines 54-58):
```yaml
# DNS Provider Selection
dns_provider: "cloudflare"  # Options: cloudflare, route53, google_dns, azure_dns, manual
route53_enabled: "{{ dns_provider == 'route53' }}"
route53_access_key: ""
route53_secret_key: ""
```

**Include Role** (add after cloudflare_integration role):
```yaml
    - name: Include Route53 integration role
      include_role:
        name: route53_integration
      when: dns_provider == 'route53'
      tags: [route53, dns]
```

### 5. Update Usage Documentation

**Usage** (in playbooks/email-delivery-setup.yml comment block):
```yaml
# For Cloudflare:
ansible-playbook playbooks/email-delivery-setup.yml \
  -e "dns_provider=cloudflare" \
  -e "cloudflare_api_token=your_token" \
  -e "cloudflare_zone_id=your_zone_id"

# For Route53:
ansible-playbook playbooks/email-delivery-setup.yml \
  -e "dns_provider=route53" \
  -e "route53_access_key=YOUR_KEY" \
  -e "route53_secret_key=YOUR_SECRET" \
  -e "route53_region=us-east-1"
```

## Provider Implementation Checklist

For each new DNS provider, ensure:

- [ ] Role directory created: `roles/<provider>_integration/`
- [ ] Default variables defined in `defaults/main.yml`
- [ ] Provider-specific tasks in `tasks/main.yml`
- [ ] API authentication method documented
- [ ] DNS record format translation implemented
- [ ] Error handling for API failures
- [ ] Support for all record types (A, MX, TXT, CNAME, etc.)
- [ ] TTL and proxy settings handled (if applicable)
- [ ] Documentation in role README.md
- [ ] Playbook updated to conditionally include role
- [ ] Variables documented in main playbook
- [ ] Test with sample domain

## Supported DNS Providers

### Current
- **Cloudflare**: Fully implemented (lines 161-170 in playbooks/email-delivery-setup.yml)

### To Implement
- **AWS Route53**: See template above
- **Google Cloud DNS**: Uses `gcp_dns_managed_zone` module
- **Azure DNS**: Uses `azure_rm_dnsrecordset` module
- **Manual/Generic**: For providers without Ansible module support

## Testing a New Provider

```bash
# Dry-run test
ansible-playbook playbooks/email-delivery-setup.yml \
  -e "email_domain=test.example.com" \
  -e "email_server_ip=192.0.2.1" \
  -e "dns_provider=route53" \
  -e "route53_access_key=test" \
  -e "route53_secret_key=test" \
  --check \
  -v

# Actual deployment
ansible-playbook playbooks/email-delivery-setup.yml \
  -e "email_domain=test.example.com" \
  -e "email_server_ip=192.0.2.1" \
  -e "dns_provider=route53"
```

## Best Practices

1. **Keep generic format separate from provider-specific format**
   - Build `dns_records` in generic format in pre_tasks
   - Each provider role maps to its own format internally

2. **Support multiple instances of same record type**
   - Use `loop` to iterate through records
   - Support lists of values for MX records with priorities

3. **Handle API errors gracefully**
   - Set `ignore_errors` for non-critical failures
   - Provide clear error messages
   - Suggest corrective actions

4. **Document authentication requirements**
   - Clearly state what credentials are needed
   - Show how to obtain them
   - Provide examples in role README

5. **Test edge cases**
   - Subdomain vs root domain records
   - Records with special characters
   - Duplicate record creation
   - Record deletion/updates

## Example: Adding Google Cloud DNS

**Would require**:
1. Create `roles/google_dns_integration/`
2. Implement using `google.cloud.gcp_dns_managed_zone` or `google.cloud.gcp_dns_resource_record_set`
3. Add variables for GCP project, credentials
4. Handle zone creation if needed
5. Update playbook to include role conditionally

See `roles/route53_integration/` template as starting point.

## Future Enhancements

- [ ] DNS record caching/validation
- [ ] Multi-provider failover support
- [ ] DNS record health checks
- [ ] Automatic TTL reduction during setup
- [ ] DNS propagation monitoring
- [ ] Provider-specific optimizations (e.g., Cloudflare's HTTP API)
