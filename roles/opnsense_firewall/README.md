# OPNSense Firewall Role

Manages OPNSense firewall configuration via REST API.

## Status

**Framework Role** - Ready for extension with upstream `oxlorg.opnsense` collection.

## Overview

This role provides a wrapper around the OPNSense API for managing:
- Firewall rules and aliases
- Interface configuration
- NAT rules
- VPN integration
- High Availability (CARP failover)

## Requirements

- OPNSense 20.7+ with API support enabled
- SSH access for configuration
- API credentials (username and API key/secret)
- `oxlorg.opnsense` collection installed

## Role Variables

```yaml
# OPNSense API Configuration
opnsense_api_host: "192.168.1.1"
opnsense_api_user: "root"
opnsense_api_key: "{{ vault_opnsense_api_key }}"
opnsense_api_secret: "{{ vault_opnsense_api_secret }}"

# HA Configuration
opnsense_ha_enabled: false
opnsense_ha_mode: "carp"
opnsense_ha_vhid: 1
opnsense_ha_virtual_ip: "192.168.1.254"

# Interface Configuration
opnsense_interfaces: []

# Firewall Rules
opnsense_firewall_rules: []

# NAT Rules
opnsense_nat_rules: []
```

## Usage

```bash
# Deploy OPNSense firewall
uv run ansible-playbook playbooks/deploy-opnsense.yml \
  -i inventories/production/hosts/opnsense.yml
```

## Documentation

See `docs/NETWORK_INFRASTRUCTURE_GUIDE.md` for complete configuration examples.

## Integration

This role integrates with:
- `common` role for base OS hardening
- `wireguard_vpn` role for VPN integration
- Upstream `oxlorg.opnsense` collection for API operations

## Next Steps

1. Implement task files to wrap `oxlorg.opnsense` collection
2. Add interface management via API
3. Add firewall rule management
4. Add NAT rule management
5. Add HA/CARP configuration
