# Cloudflare Integration Role

Enterprise-grade Cloudflare edge security and CDN platform integration for ansible-infra.

## Overview

This role provides complete Cloudflare integration by managing DNS records, WAF rules, DDoS protection, SSL/TLS certificates, and edge caching through a combination of the official `community.general.cloudflare_dns` module and direct Cloudflare API calls for advanced features.

**Implementation Approach**:
- DNS records: Official `community.general.cloudflare_dns` module
- Advanced features (WAF, DDoS, SSL/TLS, caching): Direct API calls via `ansible.builtin.uri`
- No external/unmaintained collections
- Idempotent operations with proper error handling

## Quick Start

```yaml
- name: Configure Cloudflare
  hosts: localhost
  roles:
    - cloudflare_integration
  vars:
    cloudflare_enabled: true
    cloudflare_api_token: "{{ vault_cloudflare_api_token }}"
    cloudflare_domain: "example.com"
    cloudflare_dns_enabled: true
    cloudflare_waf_enabled: true
```

## Documentation

For comprehensive documentation, see:

**[docs/CLOUDFLARE_GUIDE.md](../../docs/CLOUDFLARE_GUIDE.md)** - Complete operations manual including:
- Safe change workflow (9-step process)
- Common operations (DNS, WAF, DDoS, SSL/TLS, cache)
- Emergency procedures
- Troubleshooting guide
- Backup & recovery procedures
- Rollback procedures
- Change log templates
- Maintenance windows checklist

**Additional Documentation**:
- [CLOUDFLARE_CICD_INTEGRATION.md](../../docs/CLOUDFLARE_CICD_INTEGRATION.md) - CI/CD integration patterns
- [CLOUDFLARE_AUDIT.md](../../docs/CLOUDFLARE_AUDIT.md) - Historical decision record

---

**Status**: Production-Ready | **Last Updated**: November 17, 2025
