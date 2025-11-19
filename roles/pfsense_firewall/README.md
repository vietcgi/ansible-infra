# pfSense Firewall Role

Manages pfSense firewall configuration via SSH and XML manipulation.

## Status

**Framework Role** - Ready for extension with upstream `pfsensible.core` collection.

## Overview

This role provides a wrapper around pfSense XML configuration for managing:
- Firewall rules and aliases
- Interface configuration
- NAT rules
- IPsec VPN tunnels
- High Availability (CARP failover)

## Requirements

- pfSense 2.4.5+ with SSH access enabled
- SSH public key authentication configured
- `pfsensible.core` collection installed
- Sudo access on pfSense system

## Role Variables

```yaml
# pfSense SSH Configuration
ansible_user: root
ansible_ssh_private_key_file: ~/.ssh/pfsense_key

# HA Configuration
pfsense_ha_enabled: false
pfsense_ha_mode: "carp"
pfsense_ha_vhid: 1
pfsense_ha_virtual_ip: "192.168.1.254"

# Interface Configuration
pfsense_interfaces: []

# Firewall Rules
pfsense_firewall_rules: []

# NAT Rules
pfsense_nat_rules: []

# IPsec Configuration
pfsense_ipsec_enabled: false
pfsense_ipsec_tunnels: []
```

## Usage

```bash
# Deploy pfSense firewall
uv run ansible-playbook playbooks/deploy-pfsense.yml \
  -i inventories/production/hosts/pfsense.yml
```

## Setup Requirements

Before using this role:

1. Enable SSH on pfSense:
   System → Advanced → Admin Access → Secure Shell

2. Create ansible user:
   System → User Manager

3. Add SSH public key to user

4. Add user to admin group

## Documentation

See `docs/NETWORK_INFRASTRUCTURE_GUIDE.md` for complete configuration examples.

## Integration

This role integrates with:
- `common` role for base OS hardening
- `wireguard_vpn` role for VPN integration
- Upstream `pfsensible.core` collection for XML operations

## Next Steps

1. Implement task files to wrap `pfsensible.core` collection
2. Add interface management via XML
3. Add firewall rule management
4. Add NAT rule management
5. Add IPsec VPN configuration
6. Add HA/CARP configuration
