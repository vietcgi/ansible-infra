# oxlorg.opnsense Ansible Collection - Complete Documentation

## Overview

The **oxlorg.opnsense** is a comprehensive Ansible collection for managing OPNsense firewalls via their API. The collection provides 100+ modules covering all aspects of firewall configuration and management.

**Repository**: https://github.com/O-X-L/ansible-opnsense
**Documentation**: https://ansible-opnsense.oxl.app/
**Ansible Galaxy**: https://galaxy.ansible.com/ui/repo/published/oxlorg/opnsense

---

## Installation

### Prerequisites

The collection requires the **httpx** Python module for API communications:

```bash
python3 -m pip install --upgrade httpx
```

### Install Collection

```bash
# Latest version from GitHub
ansible-galaxy collection install git+https://github.com/O-X-L/ansible-opnsense.git

# Stable/tested version (25.7.7)
ansible-galaxy collection install git+https://github.com/O-X-L/ansible-opnsense.git,25.7.7

# From Ansible Galaxy
ansible-galaxy collection install oxlorg.opnsense
```

---

## Authentication

### API Credential Setup

1. Create API credentials in OPNsense:
   - Navigate to: **System → Access → Users**
   - Edit admin user (or create dedicated API user)
   - Click **Add API Key**
   - Download credentials (only available once)

### Authentication Methods

#### Method 1: Direct Parameters
```yaml
- name: Example task
  oxlorg.opnsense.alias:
    firewall_url: "https://opnsense.example.com"
    api_key: "your_api_key"
    api_secret: "your_api_secret"
    ssl_verify: true
    name: "example_alias"
    content: "192.168.1.0/24"
```

#### Method 2: Credential File
```yaml
- name: Example task with credential file
  oxlorg.opnsense.alias:
    firewall_url: "https://opnsense.example.com"
    api_credential_file: "/home/user/.secret/opn.key"
    ssl_verify: true
    name: "example_alias"
    content: "192.168.1.0/24"
```

**Credential file format** (INI):
```ini
[opnsense]
api_key=your_api_key_here
api_secret=your_api_secret_here
url=https://opnsense.example.com/api
ssl_verify=true
timeout=30
```

#### Method 3: Module Defaults (Recommended)
```yaml
- name: Configure OPNsense
  hosts: opnsense_firewalls

  module_defaults:
    group/oxlorg.opnsense.all:
      firewall_url: "https://{{ ansible_host }}"
      api_credential_file: "/home/user/.secret/opn.key"
      ssl_verify: true

  tasks:
    - name: Create alias
      oxlorg.opnsense.alias:
        name: "web_servers"
        content: "10.0.1.10"

    - name: Create firewall rule
      oxlorg.opnsense.rule:
        description: "Allow HTTP to web servers"
        source_net: "any"
        destination_net: "web_servers"
        destination_port: "80"
        protocol: "tcp"
        action: "pass"
```

### Security Best Practices

- **Always use SSL verification** for production environments
- Use **ansible-vault** to encrypt api_secret values
- Create **dedicated API users** with minimum required privileges
- Use **credential files** instead of hardcoded values
- Restrict API access to specific IP addresses in OPNsense

---

## Module Naming Convention

All modules follow the pattern: `oxlorg.opnsense.<module_name>`

- **oxlorg**: Organization/vendor identifier (O-X-L)
- **opnsense**: Platform name
- **module_name**: Specific resource/functionality

Examples:
- `oxlorg.opnsense.alias` - Manage firewall aliases
- `oxlorg.opnsense.interface_vlan` - Manage VLAN interfaces
- `oxlorg.opnsense.rule` - Manage firewall rules

---

## Available Modules by Category

### Base Operations
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.list` | List existing entries | stable |
| `oxlorg.opnsense.reload` | Reload configuration | stable |
| `oxlorg.opnsense.raw` | Raw API calls | unstable |
| `oxlorg.opnsense.service` | Manage services | stable |

### Aliases
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.alias` | Manage aliases | stable |
| `oxlorg.opnsense.alias_multi` | Bulk alias management | stable |
| `oxlorg.opnsense.alias_purge` | Remove all aliases | unstable |

### Firewall Rules
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.rule` | Manage firewall rules | stable |
| `oxlorg.opnsense.rule_multi` | Bulk rule management | stable |
| `oxlorg.opnsense.rule_purge` | Remove all rules | unstable |
| `oxlorg.opnsense.rule_interface_group` | Manage interface groups | stable |

### Interfaces
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.interface_vlan` | Manage VLANs | stable |
| `oxlorg.opnsense.interface_vxlan` | Manage VXLANs | stable |
| `oxlorg.opnsense.interface_vip` | Manage Virtual IPs (CARP) | stable |
| `oxlorg.opnsense.interface_lagg` | Manage LAGG (Link Aggregation) | stable |
| `oxlorg.opnsense.interface_loopback` | Manage loopback interfaces | stable |
| `oxlorg.opnsense.interface_gre` | Manage GRE tunnels | stable |
| `oxlorg.opnsense.interface_bridge` | Manage bridges | unstable |
| `oxlorg.opnsense.interface_gif` | Manage GIF tunnels | unstable |

### Routing
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.route` | Manage static routes | stable |
| `oxlorg.opnsense.gateway` | Manage gateways | stable |

### NAT
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.nat_source` | Manage source NAT | stable |
| `oxlorg.opnsense.nat_one_to_one` | Manage 1:1 NAT | stable |

### High Availability (HA/CARP)
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.hasync_general` | Configure HA synchronization | stable |
| `oxlorg.opnsense.hasync_service` | Trigger service sync/restart | stable |

### System Settings
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.system` | Manage system settings | stable |
| `oxlorg.opnsense.cron` | Manage cron jobs | stable |
| `oxlorg.opnsense.syslog` | Configure syslog | stable |
| `oxlorg.opnsense.snapshot` | Manage configuration snapshots | stable |
| `oxlorg.opnsense.savepoint` | Manage savepoints | stable |
| `oxlorg.opnsense.package` | Manage packages | stable |

### DNS - Unbound
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.unbound_general` | General Unbound settings | stable |
| `oxlorg.opnsense.unbound_acl` | Manage ACLs | stable |
| `oxlorg.opnsense.unbound_forward` | Configure forwarding | stable |
| `oxlorg.opnsense.unbound_dot` | DNS over TLS settings | stable |
| `oxlorg.opnsense.unbound_host` | Manage host overrides | stable |
| `oxlorg.opnsense.unbound_host_alias` | Manage host aliases | stable |
| `oxlorg.opnsense.unbound_dnsbl` | DNS blocklists | stable |

### DNS - BIND
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.bind_general` | General BIND settings | stable |
| `oxlorg.opnsense.bind_blocklist` | Manage blocklists | stable |
| `oxlorg.opnsense.bind_acl` | Manage ACLs | stable |
| `oxlorg.opnsense.bind_domain` | Manage domains | stable |
| `oxlorg.opnsense.bind_record` | Manage DNS records | stable |
| `oxlorg.opnsense.bind_record_multi` | Bulk record management | stable |

### DNS - Dnsmasq
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.dnsmasq_general` | General settings | unstable |
| `oxlorg.opnsense.dnsmasq_domain` | Manage domains | unstable |
| `oxlorg.opnsense.dnsmasq_host` | Manage hosts | unstable |
| `oxlorg.opnsense.dnsmasq_range` | DHCP ranges | unstable |
| `oxlorg.opnsense.dnsmasq_option` | DHCP options | unstable |
| `oxlorg.opnsense.dnsmasq_boot` | PXE boot settings | unstable |
| `oxlorg.opnsense.dnsmasq_tag` | Manage tags | unstable |

### VPN - WireGuard
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.wireguard_general` | General settings | stable |
| `oxlorg.opnsense.wireguard_server` | Manage servers | stable |
| `oxlorg.opnsense.wireguard_peer` | Manage peers | stable |
| `oxlorg.opnsense.wireguard_show` | Show status | stable |

### VPN - OpenVPN
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.openvpn_client` | Manage clients | stable |
| `oxlorg.opnsense.openvpn_server` | Manage servers | stable |
| `oxlorg.opnsense.openvpn_static_key` | Manage static keys | stable |
| `oxlorg.opnsense.openvpn_status` | Check status | stable |
| `oxlorg.opnsense.openvpn_client_override` | Client overrides | stable |

### VPN - IPSec
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.ipsec_general` | General settings | unstable |
| `oxlorg.opnsense.ipsec_connection` | Manage connections | stable |
| `oxlorg.opnsense.ipsec_tunnel` | Manage tunnels | stable |
| `oxlorg.opnsense.ipsec_pool` | IP pools | stable |
| `oxlorg.opnsense.ipsec_network` | Networks | stable |
| `oxlorg.opnsense.ipsec_auth_local` | Local authentication | stable |
| `oxlorg.opnsense.ipsec_auth_remote` | Remote authentication | stable |
| `oxlorg.opnsense.ipsec_child` | Child SAs | stable |
| `oxlorg.opnsense.ipsec_vti` | Virtual tunnel interfaces | stable |
| `oxlorg.opnsense.ipsec_cert` | Certificates | stable |
| `oxlorg.opnsense.ipsec_psk` | Pre-shared keys | stable |
| `oxlorg.opnsense.ipsec_manual_spd` | Manual SPD entries | stable |

### DHCP
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.dhcp_general` | General settings | stable |
| `oxlorg.opnsense.dhcp_subnet` | Manage subnets | stable |
| `oxlorg.opnsense.dhcp_reservation` | Manage reservations | stable |
| `oxlorg.opnsense.dhcp_controlagent` | Control agent settings | stable |

### DHCP Relay
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.dhcrelay_relay` | Configure relay | stable |
| `oxlorg.opnsense.dhcrelay_destination` | Relay destinations | stable |

### Dynamic Routing - FRR
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.frr_general` | General FRR settings | stable |
| `oxlorg.opnsense.frr_diagnostic` | Diagnostics | stable |
| `oxlorg.opnsense.frr_rip` | RIP configuration | stable |

### Dynamic Routing - BFD
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.frr_bfd_general` | BFD settings | stable |
| `oxlorg.opnsense.frr_bfd_neighbor` | BFD neighbors | stable |

### Dynamic Routing - BGP
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.frr_bgp_general` | General BGP settings | stable |
| `oxlorg.opnsense.frr_bgp_neighbor` | BGP neighbors | stable |
| `oxlorg.opnsense.frr_bgp_peer_group` | Peer groups | stable |
| `oxlorg.opnsense.frr_bgp_prefix_list` | Prefix lists | stable |
| `oxlorg.opnsense.frr_bgp_route_map` | Route maps | stable |
| `oxlorg.opnsense.frr_bgp_community_list` | Community lists | stable |
| `oxlorg.opnsense.frr_bgp_as_path` | AS path lists | stable |
| `oxlorg.opnsense.frr_bgp_redistribution` | Redistribution | stable |

### Dynamic Routing - OSPF
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.frr_ospf_general` | OSPFv2 settings | stable |
| `oxlorg.opnsense.frr_ospf_interface` | OSPF interfaces | stable |
| `oxlorg.opnsense.frr_ospf_network` | OSPF networks | stable |
| `oxlorg.opnsense.frr_ospf_prefix_list` | Prefix lists | stable |
| `oxlorg.opnsense.frr_ospf_route_map` | Route maps | stable |
| `oxlorg.opnsense.frr_ospf_redistribution` | Redistribution | stable |

### Dynamic Routing - OSPFv3
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.frr_ospf3_general` | OSPFv3 settings | stable |
| `oxlorg.opnsense.frr_ospf3_interface` | OSPFv3 interfaces | stable |
| `oxlorg.opnsense.frr_ospf3_network` | OSPFv3 networks | stable |
| `oxlorg.opnsense.frr_ospf3_prefix_list` | Prefix lists | stable |
| `oxlorg.opnsense.frr_ospf3_route_map` | Route maps | stable |
| `oxlorg.opnsense.frr_ospf3_redistribution` | Redistribution | stable |

### Traffic Shaping
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.shaper_pipe` | Manage pipes | stable |
| `oxlorg.opnsense.shaper_queue` | Manage queues | stable |
| `oxlorg.opnsense.shaper_rule` | Shaping rules | stable |

### IDS/IPS
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.ids_general` | General IDS settings | stable |
| `oxlorg.opnsense.ids_action` | IDS actions | stable |
| `oxlorg.opnsense.ids_ruleset` | Manage rulesets | stable |
| `oxlorg.opnsense.ids_rule` | Manage rules | stable |
| `oxlorg.opnsense.ids_user_rule` | User-defined rules | stable |
| `oxlorg.opnsense.ids_policy` | Policies | stable |
| `oxlorg.opnsense.ids_policy_rule` | Policy rules | stable |

### Web Proxy
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.webproxy_general` | General settings | stable |
| `oxlorg.opnsense.webproxy_cache` | Cache settings | stable |
| `oxlorg.opnsense.webproxy_parent` | Parent proxy | stable |
| `oxlorg.opnsense.webproxy_traffic` | Traffic settings | stable |
| `oxlorg.opnsense.webproxy_forward` | Forward proxy | stable |
| `oxlorg.opnsense.webproxy_acl` | Access control | stable |
| `oxlorg.opnsense.webproxy_icap` | ICAP settings | stable |
| `oxlorg.opnsense.webproxy_auth` | Authentication | stable |
| `oxlorg.opnsense.webproxy_remote_acl` | Remote ACLs | stable |
| `oxlorg.opnsense.webproxy_pac_proxy` | PAC proxy | stable |
| `oxlorg.opnsense.webproxy_pac_match` | PAC matches | stable |
| `oxlorg.opnsense.webproxy_pac_rule` | PAC rules | stable |

### Monitoring - Monit
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.monit_service` | Manage services | stable |
| `oxlorg.opnsense.monit_alert` | Alert settings | stable |
| `oxlorg.opnsense.monit_test` | Test configurations | stable |

### Nginx
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.nginx_general` | General settings | stable |
| `oxlorg.opnsense.nginx_upstream_server` | Upstream servers | stable |

### Postfix
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.postfix_general` | General settings | stable |
| `oxlorg.opnsense.postfix_domain` | Manage domains | stable |
| `oxlorg.opnsense.postfix_recipient` | Recipients | stable |
| `oxlorg.opnsense.postfix_recipientbcc` | Recipient BCC | stable |
| `oxlorg.opnsense.postfix_sender` | Senders | stable |
| `oxlorg.opnsense.postfix_senderbcc` | Sender BCC | stable |
| `oxlorg.opnsense.postfix_sendercanonical` | Sender canonical | stable |
| `oxlorg.opnsense.postfix_headercheck` | Header checks | stable |
| `oxlorg.opnsense.postfix_address` | Addresses | stable |

### ACME (Certificates)
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.acme_general` | General settings | stable |
| `oxlorg.opnsense.acme_account` | Manage accounts | stable |
| `oxlorg.opnsense.acme_validation` | Validation methods | stable |
| `oxlorg.opnsense.acme_certificate` | Manage certificates | stable |
| `oxlorg.opnsense.acme_action` | ACME actions | stable |

### User Management
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.user` | Manage users | unstable |
| `oxlorg.opnsense.group` | Manage groups | unstable |
| `oxlorg.opnsense.privilege` | Manage privileges | unstable |

### Other
| Module | Purpose | State |
|--------|---------|-------|
| `oxlorg.opnsense.neighbor` | Neighbor discovery | unstable |

---

## Practical Examples by Use Case

### 1. Interface Configuration

#### Create VLAN Interface
```yaml
- name: Create VLAN 100 on vtnet0
  oxlorg.opnsense.interface_vlan:
    description: "Management VLAN"
    interface: "vtnet0"
    vlan: 100
    priority: 0
    state: present
    reload: true
```

#### Create LAGG Interface
```yaml
- name: Create LAGG interface
  oxlorg.opnsense.interface_lagg:
    description: "Bond0"
    members:
      - "vtnet1"
      - "vtnet2"
    protocol: "lacp"
    state: present
```

#### Create Virtual IP (CARP)
```yaml
- name: Create CARP VIP for HA
  oxlorg.opnsense.interface_vip:
    interface: "lan"
    mode: "carp"
    vhid: 1
    advskew: 0
    advbase: 1
    password: "{{ carp_password }}"
    address: "192.168.1.1"
    subnet: 24
    description: "LAN CARP VIP"
    state: present
```

### 2. Firewall Rules

#### Basic Firewall Rule
```yaml
- name: Allow HTTP traffic
  oxlorg.opnsense.rule:
    description: "Allow HTTP from LAN to DMZ"
    interface: "lan"
    direction: "in"
    action: "pass"
    protocol: "tcp"
    source_net: "192.168.1.0/24"
    destination_net: "10.0.1.0/24"
    destination_port: "80"
    quick: true
    state: present
```

#### Rule with Alias
```yaml
- name: Create alias for web servers
  oxlorg.opnsense.alias:
    name: "web_servers"
    type: "host"
    content:
      - "10.0.1.10"
      - "10.0.1.11"
    description: "Web server pool"
    state: present

- name: Allow traffic to web servers
  oxlorg.opnsense.rule:
    description: "Allow HTTPS to web servers"
    source_net: "any"
    destination_net: "web_servers"
    destination_port: "443"
    protocol: "tcp"
    action: "pass"
    state: present
```

#### Block Rule
```yaml
- name: Block outbound telnet
  oxlorg.opnsense.rule:
    description: "Block telnet outbound"
    interface: "lan"
    action: "block"
    protocol: "tcp"
    source_net: "any"
    destination_net: "any"
    destination_port: "23"
    state: present
```

### 3. HA/CARP Configuration

#### Configure HA Synchronization
```yaml
- name: Configure HA sync settings
  oxlorg.opnsense.hasync_general:
    # pfSync configuration
    pfsync_interface: "sync0"
    pfsync_peer_ip: "192.168.254.2"
    pfsync_version: "1400"

    # Config sync settings
    synchronize_to_ip: "192.168.254.2"
    synchronize_username: "root"
    synchronize_password: "{{ ha_sync_password }}"

    # What to synchronize
    synchronize_aliases: true
    synchronize_rules: true
    synchronize_nat: true
    synchronize_ipsec: true
    synchronize_openvpn: true
    synchronize_users: true
    synchronize_certs: true
    synchronize_dhcp: true

    state: present
```

#### Trigger Service Sync
```yaml
- name: Sync and restart unbound DNS
  oxlorg.opnsense.hasync_service:
    action: "restart"
    services:
      - "unbound"
```

### 4. System Settings

#### Configure System Settings
```yaml
- name: Set hostname and domain
  oxlorg.opnsense.system:
    hostname: "fw01"
    domain: "example.com"
    timezone: "America/New_York"
    language: "en_US"
    dns_servers:
      - "8.8.8.8"
      - "8.8.4.4"
    state: present
```

#### Create Cron Job
```yaml
- name: Schedule configuration backup
  oxlorg.opnsense.cron:
    description: "Daily config backup"
    command: "/usr/local/opnsense/scripts/backup.sh"
    minutes: "0"
    hours: "2"
    days: "*"
    months: "*"
    weekdays: "*"
    enabled: true
    state: present
```

### 5. Routing

#### Static Route
```yaml
- name: Add static route
  oxlorg.opnsense.route:
    description: "Route to remote site"
    network: "10.10.0.0/16"
    gateway: "WAN_GW"
    enabled: true
    state: present
```

#### Gateway
```yaml
- name: Create gateway
  oxlorg.opnsense.gateway:
    name: "VPN_GW"
    interface: "opt1"
    gateway: "192.168.100.1"
    priority: 255
    weight: 1
    description: "VPN gateway"
    disabled: false
    state: present
```

### 6. DNS Configuration

#### Unbound DNS
```yaml
- name: Configure Unbound general settings
  oxlorg.opnsense.unbound_general:
    enabled: true
    port: 53
    dnssec: true
    forwarding: false
    regdhcp: true
    state: present

- name: Add DNS host override
  oxlorg.opnsense.unbound_host:
    hostname: "server1"
    domain: "local.lan"
    server: "192.168.1.100"
    description: "Internal server"
    state: present
```

#### BIND DNS
```yaml
- name: Configure BIND domain
  oxlorg.opnsense.bind_domain:
    name: "example.com"
    mode: "master"
    server: "192.168.1.1"
    state: present

- name: Add DNS A record
  oxlorg.opnsense.bind_record:
    domain: "example.com"
    name: "www"
    type: "A"
    value: "192.168.1.10"
    state: present
```

### 7. VPN Configuration

#### WireGuard Server
```yaml
- name: Create WireGuard server
  oxlorg.opnsense.wireguard_server:
    name: "wg0"
    port: 51820
    privkey: "{{ wireguard_private_key }}"
    pubkey: "{{ wireguard_public_key }}"
    addresses: "10.200.0.1/24"
    state: present

- name: Add WireGuard peer
  oxlorg.opnsense.wireguard_peer:
    server: "wg0"
    name: "client1"
    pubkey: "{{ client_public_key }}"
    allowed_ips: "10.200.0.2/32"
    state: present
```

#### IPSec Tunnel
```yaml
- name: Create IPSec connection
  oxlorg.opnsense.ipsec_connection:
    description: "Site-to-Site VPN"
    remote_addrs: "203.0.113.10"
    local_addrs: "198.51.100.10"
    version: 2
    proposal: "aes256-sha256-modp2048"
    state: present
```

### 8. NAT Configuration

#### Source NAT (Outbound)
```yaml
- name: Configure source NAT
  oxlorg.opnsense.nat_source:
    interface: "wan"
    source_net: "192.168.1.0/24"
    destination_net: "any"
    target_address: "WAN address"
    description: "LAN to WAN NAT"
    state: present
```

#### 1:1 NAT
```yaml
- name: Create 1:1 NAT
  oxlorg.opnsense.nat_one_to_one:
    interface: "wan"
    external: "203.0.113.50"
    internal: "192.168.1.100"
    description: "Web server NAT"
    state: present
```

### 9. DHCP Configuration

```yaml
- name: Configure DHCP subnet
  oxlorg.opnsense.dhcp_subnet:
    interface: "lan"
    subnet: "192.168.1.0/24"
    range_from: "192.168.1.100"
    range_to: "192.168.1.200"
    gateway: "192.168.1.1"
    dns_servers:
      - "192.168.1.1"
    domain: "local.lan"
    state: present

- name: Add DHCP reservation
  oxlorg.opnsense.dhcp_reservation:
    interface: "lan"
    mac: "00:11:22:33:44:55"
    ip: "192.168.1.50"
    hostname: "printer1"
    description: "Office printer"
    state: present
```

### 10. Package Management

```yaml
- name: Install package
  oxlorg.opnsense.package:
    name: "os-acme-client"
    action: "install"

- name: Remove package
  oxlorg.opnsense.package:
    name: "os-theme-rebellion"
    action: "remove"
```

### 11. Configuration Management

#### List Existing Items
```yaml
- name: List all aliases
  oxlorg.opnsense.list:
    target: "alias"
  register: aliases_result

- name: Show aliases
  debug:
    var: aliases_result
```

#### Reload Configuration
```yaml
- name: Reload firewall rules
  oxlorg.opnsense.reload:
    target: "filter"

- name: Reload aliases
  oxlorg.opnsense.reload:
    target: "alias"
```

#### Create Configuration Snapshot
```yaml
- name: Create backup snapshot
  oxlorg.opnsense.snapshot:
    description: "Pre-upgrade backup"
    action: "create"
```

### 12. Bulk Operations

#### Disable Auto-Reload for Performance
```yaml
- name: Bulk create aliases without reload
  oxlorg.opnsense.alias:
    name: "{{ item.name }}"
    content: "{{ item.content }}"
    reload: false  # Don't reload after each change
    state: present
  loop:
    - { name: "servers1", content: "10.0.1.0/24" }
    - { name: "servers2", content: "10.0.2.0/24" }
    - { name: "servers3", content: "10.0.3.0/24" }

- name: Reload aliases once after all changes
  oxlorg.opnsense.reload:
    target: "alias"
```

---

## Common Parameters

Most modules support these common parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `firewall_url` | string | URL to OPNsense firewall (https://hostname) |
| `api_key` | string | API key for authentication |
| `api_secret` | string | API secret for authentication |
| `api_credential_file` | string | Path to credential file |
| `ssl_verify` | bool | Verify SSL certificate (default: true) |
| `state` | string | Desired state: present/absent/enabled/disabled |
| `reload` | bool | Auto-reload config after change (default: true) |
| `debug` | bool | Enable debug output (default: false) |

---

## Configuration Reload Behavior

### Automatic Reload
By default, most modules **automatically reload** the relevant configuration when changes are made:

```yaml
- name: This will auto-reload after creation
  oxlorg.opnsense.alias:
    name: "web_servers"
    content: "10.0.1.10"
    # reload: true (default)
```

### Manual Reload (Performance Optimization)
For bulk operations, disable auto-reload and trigger manually:

```yaml
- name: Create multiple items without reload
  oxlorg.opnsense.rule:
    description: "Rule {{ item }}"
    reload: false
    # ... other parameters
  loop: "{{ rules_list }}"

- name: Reload once after all changes
  oxlorg.opnsense.reload:
    target: "filter"  # or "alias", "nat", etc.
```

### Reload Targets
Common reload targets:
- `filter` - Firewall rules
- `alias` - Aliases
- `nat` - NAT rules
- `route` - Routes
- `unbound` - DNS service
- `dhcp` - DHCP service

---

## Important Notes

### Rule Management Caveat
**IMPORTANT**: The ruleset managed by `oxlorg.opnsense.rule` is **SEPARATE** from the default Web UI rules (Firewall → Rules). Use the automation ruleset or web UI, but mixing both can cause confusion.

### Interface Names
Use **technical interface names** (e.g., 'opt1', 'vtnet0') instead of friendly names (e.g., 'DMZ'). Check interface names in: **Interfaces → Assignments**

### Version Compatibility
The collection aims to support the **latest version of OPNsense**. API changes in older firmware versions may cause module failures. Always test in a non-production environment first.

### Development States
- **stable**: Production-ready, thoroughly tested
- **unstable**: Functional but undergoing practical testing
- **development**: Under active development
- **testing**: In automated testing phase

---

## Troubleshooting

### Enable Debug Output
```yaml
- name: Debug API calls
  oxlorg.opnsense.alias:
    name: "test"
    content: "192.168.1.1"
    debug: true
```

### Common Issues

1. **SSL Certificate Errors**
   - Use `ssl_verify: false` for testing (not recommended for production)
   - Add CA certificate to system trust store

2. **Authentication Failures**
   - Verify API key/secret are correct
   - Check user has necessary privileges
   - Ensure API access is enabled

3. **Module Not Found**
   - Verify collection is installed: `ansible-galaxy collection list`
   - Use fully qualified module name: `oxlorg.opnsense.module_name`

4. **Changes Not Applied**
   - Check if reload occurred (or force with `reload: true`)
   - Manually reload from Web UI: **Power → Apply Settings**

---

## Resources

- **Official Documentation**: https://ansible-opnsense.oxl.app/
- **GitHub Repository**: https://github.com/O-X-L/ansible-opnsense
- **Issues/Feature Requests**: https://github.com/O-X-L/ansible-opnsense/issues
- **Discussions**: https://github.com/O-X-L/ansible-opnsense/discussions
- **OPNsense API Docs**: https://docs.opnsense.org/development/api.html

---

## License

This collection is maintained by O-X-L and is available as open source software.

---

**Last Updated**: 2025-11-19
**Collection Version**: 25.7.7 (stable)
**Supported OPNsense**: Latest version
