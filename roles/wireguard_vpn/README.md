# Wireguard VPN Role

Manages Wireguard VPN configuration with support for multiple topologies: full mesh, hub-and-spoke (HA), and site-to-site.

## Overview

This role provides:
- Wireguard installation and configuration
- Automatic key generation and distribution
- Multiple topology modes (full mesh, HA/hub-and-spoke, site-to-site)
- Peer management with flexible configuration
- DNS and routing configuration
- IPv4 and IPv6 support
- Firewall integration
- MTU and keepalive settings

## Requirements

- Proxmox VMs or physical servers with supported OS (Ubuntu 20.04+, Debian 10+, Fedora, CentOS 8+)
- Kernel 5.6+ (Wireguard in-kernel)
- Python 3.6+ on control node

Install Python dependencies:
```bash
pip install netaddr
```

## Role Variables

### Core Configuration

```yaml
# Wireguard enabled/disabled
wireguard_enabled: true

# VPN network settings
wireguard_vpn_network: "10.0.0.0/24"      # VPN subnet
wireguard_vpn_mtu: 1420                   # MTU for VPN tunnel
wireguard_persistent_keepalive: 25        # Keepalive interval (0 = disabled)
wireguard_port: 51820                     # Wireguard listen port

# DNS configuration
wireguard_dns_servers:
  - 1.1.1.1
  - 1.0.0.1
```

### Topology Selection

```yaml
# Choose ONE of the three topologies:
wireguard_topology: "full_mesh"           # Options: full_mesh, hub_spoke, site_to_site
```

### Full Mesh Topology (All nodes peer to all nodes)

```yaml
# Requires: wireguard_topology: "full_mesh"

# Define all nodes in the mesh
wireguard_full_mesh_nodes:
  node1:
    vpn_ip: "10.0.0.1"
    public_endpoint: "node1.example.com:51820"
    public_key: "{{ vault_node1_pubkey }}"  # Auto-generated if omitted

  node2:
    vpn_ip: "10.0.0.2"
    public_endpoint: "node2.example.com:51820"
    public_key: "{{ vault_node2_pubkey }}"
```

**How it works:**
- Every node connects to every other node
- Each node has a unique VPN IP
- Bi-directional peering
- Best for 2-50 nodes with good inter-node connectivity

**Example Inventory:**
```yaml
wireguard_nodes:
  hosts:
    vpn-node-01:
      wireguard_topology: full_mesh
      wireguard_vpn_ip: 10.0.0.1
    vpn-node-02:
      wireguard_vpn_ip: 10.0.0.2
    vpn-node-03:
      wireguard_vpn_ip: 10.0.0.3
```

### Hub-and-Spoke (High Availability)

```yaml
# Requires: wireguard_topology: "hub_spoke"

# Hub configuration (firewall/router)
wireguard_ha_mode: true                  # Enable HA mode
wireguard_hub_node: "fw-primary"         # Primary hub

# Hub peers (secondary gateways for failover)
wireguard_hub_peers:
  - name: "fw-secondary"
    vpn_ip: "10.0.0.254"
    public_endpoint: "fw-secondary.example.com:51820"
    role: backup                         # backup or standby

# Spoke nodes
wireguard_spoke_nodes:
  spoke1:
    vpn_ip: "10.0.0.10"
    networks: ["192.168.1.0/24"]         # Networks behind this spoke
    public_endpoint: "spoke1.example.com:51820"

  spoke2:
    vpn_ip: "10.0.0.20"
    networks: ["192.168.2.0/24"]
    public_endpoint: "spoke2.example.com:51820"
```

**How it works:**
- Hub (firewall) is central gateway
- Spokes only peer with hub(s)
- Hub routes traffic between spokes
- Secondary hub provides failover
- Best for centralized security/routing

**Example Inventory:**
```yaml
firewalls:
  hosts:
    fw-primary:
      wireguard_role: hub
      wireguard_vpn_ip: 10.0.0.1
      wireguard_topology: hub_spoke
      wireguard_ha_mode: true
    fw-secondary:
      wireguard_role: hub
      wireguard_vpn_ip: 10.0.0.254
      wireguard_backup: true

spoke_nodes:
  hosts:
    app-server-01:
      wireguard_role: spoke
      wireguard_vpn_ip: 10.0.0.10
      wireguard_networks: ["192.168.1.0/24"]
    db-server-01:
      wireguard_role: spoke
      wireguard_vpn_ip: 10.0.0.20
      wireguard_networks: ["192.168.2.0/24"]
```

### Site-to-Site Topology

```yaml
# Requires: wireguard_topology: "site_to_site"

# Define sites/locations
wireguard_sites:
  site_a:
    location: "New York"
    gateway: "gw-nyc"
    networks: ["192.168.1.0/24", "192.168.2.0/24"]
    vpn_network: "10.0.1.0/24"

  site_b:
    location: "London"
    gateway: "gw-lon"
    networks: ["192.168.10.0/24", "192.168.11.0/24"]
    vpn_network: "10.0.2.0/24"

  site_c:
    location: "Tokyo"
    gateway: "gw-tyo"
    networks: ["192.168.20.0/24"]
    vpn_network: "10.0.3.0/24"

# Inter-site routing
wireguard_site_routes:
  - from: site_a
    to: site_b
    via: gw-nyc
  - from: site_b
    to: site_c
    via: gw-lon
  - from: site_c
    to: site_a
    via: gw-tyo
```

**How it works:**
- Each site has its own VPN subnet
- Gateways route between sites
- Supports partial mesh (not all sites peer)
- Best for multi-location companies

### Optional: IP Forwarding & Firewall Integration

```yaml
# Enable IP forwarding (required for hub/spoke and site-to-site)
wireguard_enable_ip_forward: true

# Configure UFW for Wireguard traffic
wireguard_configure_firewall: true
wireguard_firewall_rules:
  - direction: in
    protocol: udp
    port: "{{ wireguard_port }}"
    rule: allow

# Configure VPN network routing
wireguard_setup_routes: true
wireguard_routes:
  - destination: "10.0.0.0/24"
    via: "{{ wireguard_vpn_ip }}"
```

## Usage

### Deploy Full Mesh Wireguard Network

```bash
# Deploy full mesh VPN across all nodes
uv run ansible-playbook playbooks/deploy-wireguard.yml \
  -i inventories/production/hosts/wireguard.yml \
  -e "wireguard_topology=full_mesh"
```

### Deploy HA Hub-and-Spoke with Failover

```bash
# Deploy firewall HA with spoke nodes
uv run ansible-playbook playbooks/deploy-wireguard.yml \
  -i inventories/production/hosts/wireguard-ha.yml \
  -e "wireguard_topology=hub_spoke" \
  -e "wireguard_ha_mode=true"
```

### Deploy Site-to-Site VPN

```bash
# Deploy multi-location site-to-site VPN
uv run ansible-playbook playbooks/deploy-wireguard.yml \
  -i inventories/production/hosts/wireguard-sites.yml \
  -e "wireguard_topology=site_to_site"
```

### Verify VPN Status

```bash
# Check VPN connectivity
uv run ansible-playbook playbooks/verify-wireguard.yml \
  -i inventories/production/hosts/wireguard.yml
```

## Task Organization

- `install.yml` - Install Wireguard and dependencies
- `keys.yml` - Generate and distribute keys
- `configure.yml` - Configure Wireguard interface
- `topology-full-mesh.yml` - Configure full mesh peers
- `topology-hub-spoke.yml` - Configure hub-and-spoke
- `topology-site-to-site.yml` - Configure site-to-site
- `routing.yml` - Configure IP forwarding and routes
- `firewall.yml` - Configure UFW/firewall rules
- `verify.yml` - Verify VPN connectivity

## Key Generation and Storage

Keys are auto-generated if not provided:

```bash
# Keys stored in group_vars (encrypted with Ansible Vault)
ansible-vault encrypt inventories/production/group_vars/wireguard.yml

# Example:
vault_node1_private_key: |
  {{ generated private key }}
vault_node1_public_key: |
  {{ generated public key }}
```

## High Availability Features

### Hub-and-Spoke with Failover

1. **Primary Hub**: Active firewall handling all traffic
2. **Secondary Hub**: Backup firewall with same VPN IP range
3. **Spokes**: Routes via primary, falls back to secondary
4. **VRRP Integration**: Optional keepalived for automatic failover

### Full Mesh HA Pattern

For full mesh with HA, recommend:
- Deploy Wireguard on separate "gateway" nodes
- Use LVS or HAProxy for failover
- Each gateway runs full mesh
- Applications connect via gateway VIP

## Topology Decision Matrix

| Topology | Nodes | Complexity | Security | Latency | HA Support |
|----------|-------|-----------|----------|---------|-----------|
| Full Mesh | 2-50 | Low | Best | Best | Poor |
| Hub-Spoke | 50+ | Medium | Medium | Good | Excellent |
| Site-to-Site | 3+ sites | High | Best | Good | Excellent |

## Security Considerations

1. **Key Management**: Store all keys in Ansible Vault
2. **Public Key Distribution**: Use secure channels
3. **Firewall Rules**: Restrict Wireguard port by source IP
4. **Pre-shared Keys**: Optional per-peer pre-shared keys
5. **Network Isolation**: Use different VPN subnets per use case

## Integration with Common Role

This role works alongside the `common` role:
- `common` provides base OS configuration
- `wireguard_vpn` configures VPN connectivity
- `common` role firewall rules + `wireguard_configure_firewall` = complete security

## Troubleshooting

### Check Wireguard Status

```bash
# On each VPN node
wg show
wg show wg0 peers
ip addr show wg0
```

### Verify Peer Connectivity

```bash
# Test ping across VPN
ping -I 10.0.0.1 10.0.0.2

# Check MTU
ping -M do -s 1372 10.0.0.2
```

### View Logs

```bash
journalctl -u wg-quick@wg0 -f
journalctl -k | grep wireguard
```

## References

- [Wireguard Official Site](https://www.wireguard.com/)
- [githubixx Wireguard Role](https://github.com/githubixx/ansible-role-wireguard)
- [ansibleguy Wireguard Role](https://github.com/ansibleguy/infra_wireguard)
- [Wireguard Installation Guide](https://www.wireguard.com/install/)
