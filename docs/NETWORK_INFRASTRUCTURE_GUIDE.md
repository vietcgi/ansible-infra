# Network Infrastructure Automation Guide

Complete guide for deploying and managing Proxmox, Firewalls (OPNSense/pfSense), and Wireguard VPN using Ansible.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Quick Start](#quick-start)
3. [Proxmox VM Deployment](#proxmox-vm-deployment)
4. [Wireguard VPN Deployment](#wireguard-vpn-deployment)
5. [Firewall Configuration](#firewall-configuration)
6. [High Availability Patterns](#high-availability-patterns)
7. [Integration Patterns](#integration-patterns)
8. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### Reference Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet / Public Network                  │
└────────────────────────────┬────────────────────────────────┘
                             │
                      ┌──────┴──────┐
                      │ OPNSense/   │
                      │ pfSense FW  │ (HA Pair)
                      │ 192.168.1.1 │
                      └──────┬──────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │Proxmox 1 │          │Proxmox 2 │          │Proxmox 3 │
   │ (HA)     │          │ (HA)     │          │ (HA)     │
   └────┬────┘          └────┬────┘          └────┬────┘
        │                    │                    │
   ┌────┴─────┐          ┌────┴─────┐          ┌────┴─────┐
   │ VM Cluster           │ VM Cluster           │ VM Cluster│
   │ (Web,DB, │          │ (Web,DB, │          │ (Web,DB, │
   │  Cache)  │          │  Cache)  │          │  Cache)  │
   └────┬─────┘          └────┬─────┘          └────┬─────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                  ┌──────────▼──────────┐
                  │  Wireguard VPN      │
                  │  10.0.0.0/24        │
                  │  Full Mesh Topology │
                  └─────────────────────┘
```

### Component Overview

| Component | Role | Purpose |
|-----------|------|---------|
| **Proxmox** | Hypervisor | VM/LXC container management with HA clustering |
| **OPNSense** | Firewall | Advanced firewall rules, VPN gateways, load balancing |
| **pfSense** | Firewall | Alternative firewall with same capabilities |
| **Wireguard** | VPN | Encrypted inter-host and site-to-site connectivity |
| **Common Role** | Base OS | SSH hardening, firewall, monitoring, logging |

---

## Quick Start

### Prerequisites

```bash
# Install Ansible collections
cd ansible-infra
uv run ansible-galaxy collection install -r requirements.yml

# Set up inventory
cp inventories/production/hosts/proxmox-example.yml inventories/production/hosts/proxmox.yml
cp inventories/production/hosts/wireguard-example.yml inventories/production/hosts/wireguard.yml
cp inventories/production/hosts/firewall-example.yml inventories/production/hosts/firewall.yml

# Update hostnames and IPs in each file
# Add vault password file
echo 'your-vault-password' > ~/.ansible-vault-pass
```

### 5-Minute Deployment

```bash
# 1. Deploy Proxmox infrastructure with HA
cd ansible-infra
uv run ansible-playbook playbooks/deploy-proxmox.yml \
  -i inventories/production/hosts/proxmox.yml \
  --vault-password-file ~/.ansible-vault-pass

# 2. Configure VMs with base OS
uv run ansible-playbook playbooks/deploy-infrastructure.yml \
  -i inventories/production/hosts/proxmox.yml \
  -e deploy_stage=vm_base_config

# 3. Deploy firewall (OPNSense HA example)
uv run ansible-playbook playbooks/deploy-firewalls.yml \
  -i inventories/production/hosts/firewall.yml

# 4. Deploy Wireguard VPN (full mesh)
uv run ansible-playbook playbooks/deploy-wireguard.yml \
  -i inventories/production/hosts/wireguard.yml \
  -e "wireguard_topology=full_mesh"

# 5. Verify all systems online
ansible all -i inventories/production/hosts/ -m ping
```

---

## Proxmox VM Deployment

### Single Node (Minimal)

```yaml
# inventories/production/hosts/proxmox.yml
proxmox_hypervisors:
  hosts:
    pve-node-01:
      ansible_host: 192.168.1.10
  vars:
    proxmox_api_host: 192.168.1.10
    proxmox_api_user: root@pam
    proxmox_api_password: "{{ vault_proxmox_password }}"

    proxmox_vms:
      - name: web-01
        vmid: 100
        template: ubuntu-22.04
        cores: 4
        memory: 8192
        disk: 50
```

**Deploy:**
```bash
uv run ansible-playbook playbooks/deploy-proxmox.yml \
  -i inventories/production/hosts/proxmox.yml
```

### HA Cluster (3+ Nodes)

**Key Features:**
- Automatic VM relocation on node failure
- Max 3 restarts before failover
- Priority-based node preferences

```yaml
# inventories/production/hosts/proxmox.yml
proxmox_hypervisors:
  hosts:
    pve-node-01: {ansible_host: 192.168.1.10}
    pve-node-02: {ansible_host: 192.168.1.11}
    pve-node-03: {ansible_host: 192.168.1.12}
  vars:
    proxmox_api_host: 192.168.1.10
    proxmox_ha_enabled: true

    proxmox_ha_groups:
      - group_name: web-cluster
        nodes: [pve-node-01, pve-node-02, pve-node-03]
        priority: {pve-node-01: 1, pve-node-02: 2, pve-node-03: 3}

    proxmox_ha_resources:
      - vmid: 100
        group: web-cluster
        max_restart: 3
        max_relocate: 1
```

**Deploy:**
```bash
uv run ansible-playbook playbooks/deploy-proxmox.yml \
  -i inventories/production/hosts/proxmox.yml
```

### Template Management

```yaml
proxmox_cloudinit_enabled: true
proxmox_cloudinit_templates:
  - name: ubuntu-22.04
    image_url: https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img
    vmid: 9000
    storage: local-lvm
```

**Import manually if API doesn't support:**
```bash
# On Proxmox node
wget https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img
qm create 9000 --name ubuntu-22.04 --memory 2048 --cores 2
qm importdisk 9000 jammy-server-cloudimg-amd64.img local-lvm
qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9000-disk-0
qm set 9000 --ide2 local-lvm:cloudinit --boot c --bootdisk scsi0
qm template 9000
```

---

## Wireguard VPN Deployment

### Topology Selection

#### Full Mesh (All nodes peer to all nodes)

**When to use:** 2-50 nodes with good inter-connectivity, no central gateway needed

```yaml
# inventories/production/hosts/wireguard.yml
wireguard_nodes:
  hosts:
    vpn-node-01: {ansible_host: 192.168.1.100, wireguard_vpn_ip: 10.0.0.1}
    vpn-node-02: {ansible_host: 192.168.1.101, wireguard_vpn_ip: 10.0.0.2}
    vpn-node-03: {ansible_host: 192.168.1.102, wireguard_vpn_ip: 10.0.0.3}
  vars:
    wireguard_topology: full_mesh
    wireguard_vpn_network: 10.0.0.0/24

    wireguard_full_mesh_nodes:
      node1: {vpn_ip: 10.0.0.1, public_endpoint: "vpn-01.example.com:51820"}
      node2: {vpn_ip: 10.0.0.2, public_endpoint: "vpn-02.example.com:51820"}
      node3: {vpn_ip: 10.0.0.3, public_endpoint: "vpn-03.example.com:51820"}
```

**Deploy:**
```bash
uv run ansible-playbook playbooks/deploy-wireguard.yml \
  -i inventories/production/hosts/wireguard.yml \
  -e "wireguard_topology=full_mesh"
```

#### Hub-and-Spoke with HA (Recommended)

**When to use:** Centralized security gateway with failover

**Features:**
- Primary hub handles all traffic
- Secondary hub provides automatic failover
- Spokes route through hubs
- HA mode with VRRP (virtual IP)

```yaml
# inventories/production/hosts/wireguard-ha.yml
firewalls:
  hosts:
    fw-primary:
      ansible_host: 192.168.1.250
      wireguard_vpn_ip: 10.0.0.1
      wireguard_role: hub

    fw-secondary:
      ansible_host: 192.168.1.251
      wireguard_vpn_ip: 10.0.0.254
      wireguard_backup: true

  vars:
    wireguard_topology: hub_spoke
    wireguard_ha_mode: true
    wireguard_hub_node: fw-primary

    wireguard_hub_peers:
      - name: fw-secondary
        vpn_ip: 10.0.0.254
        role: backup

    wireguard_enable_ip_forward: true

spoke_nodes:
  hosts:
    app-01: {ansible_host: 192.168.2.10, wireguard_vpn_ip: 10.0.0.10}
    db-01: {ansible_host: 192.168.3.10, wireguard_vpn_ip: 10.0.0.20}

  vars:
    wireguard_topology: hub_spoke

    wireguard_spoke_nodes:
      app-01: {vpn_ip: 10.0.0.10, networks: ["192.168.2.0/24"]}
      db-01: {vpn_ip: 10.0.0.20, networks: ["192.168.3.0/24"]}
```

**Deploy:**
```bash
uv run ansible-playbook playbooks/deploy-wireguard.yml \
  -i inventories/production/hosts/wireguard-ha.yml \
  -e "wireguard_topology=hub_spoke"
```

#### Site-to-Site Multi-Location VPN

**When to use:** Connect offices/datacenters with site-specific subnets

```yaml
# inventories/production/hosts/wireguard-sites.yml
site_nyc:
  hosts:
    gw-nyc: {ansible_host: 203.0.113.1, wireguard_vpn_ip: 10.0.1.1}
    app-nyc-01: {ansible_host: 192.168.1.10, wireguard_vpn_ip: 10.0.1.10}

site_london:
  hosts:
    gw-lon: {ansible_host: 203.0.113.2, wireguard_vpn_ip: 10.0.2.1}
    app-lon-01: {ansible_host: 192.168.10.10, wireguard_vpn_ip: 10.0.2.10}

all:
  vars:
    wireguard_topology: site_to_site
    wireguard_enable_ip_forward: true

    wireguard_sites:
      site_a: {gateway: gw-nyc, networks: ["192.168.1.0/24"], vpn_network: "10.0.1.0/24"}
      site_b: {gateway: gw-lon, networks: ["192.168.10.0/24"], vpn_network: "10.0.2.0/24"}
```

**Deploy:**
```bash
uv run ansible-playbook playbooks/deploy-wireguard.yml \
  -i inventories/production/hosts/wireguard-sites.yml \
  -e "wireguard_topology=site_to_site"
```

### Verify VPN Status

```bash
# Check on any VPN node
wg show
wg show wg0 peers
ip addr show wg0

# Test connectivity
ping -I 10.0.0.1 10.0.0.2
ping -M do -s 1372 10.0.0.2  # Check MTU (should not fragment)

# View logs
journalctl -u wg-quick@wg0 -f
```

---

## Firewall Configuration

### OPNSense (API-Based)

**Advantages:** Modern REST API, web UI integration, easy automation

```yaml
# inventories/production/hosts/opnsense.yml
opnsense_firewalls:
  hosts:
    opnsense-primary:
      ansible_host: 192.168.1.1
      firewall_role: primary

    opnsense-secondary:
      ansible_host: 192.168.1.2
      firewall_role: secondary
      firewall_backup: true

  vars:
    opnsense_api_host: "{{ inventory_hostname }}"
    opnsense_api_key: "{{ vault_opnsense_api_key }}"
    opnsense_api_secret: "{{ vault_opnsense_api_secret }}"

    opnsense_ha_enabled: true
    opnsense_ha_vhid: 1
    opnsense_ha_virtual_ip: 192.168.1.254

    opnsense_interfaces:
      - name: em0
        ipaddr: "{{ opnsense_wan_ip }}"
        subnet: 24
        description: WAN

      - name: em1
        ipaddr: "{{ opnsense_lan_ip }}"
        subnet: 24
        description: LAN
```

**Deploy:**
```bash
uv run ansible-playbook playbooks/deploy-firewalls.yml \
  -i inventories/production/hosts/opnsense.yml
```

### pfSense (SSH-Based XML)

**Advantages:** Mature collection, SSH-based (no API version issues), XML flexibility

```yaml
# inventories/production/hosts/pfsense.yml
pfsense_firewalls:
  hosts:
    pfsense-primary:
      ansible_host: 192.168.2.1

    pfsense-secondary:
      ansible_host: 192.168.2.2

  vars:
    pfsensible_setup: true
    pfsense_ha_enabled: true
    pfsense_ha_vhid: 2
    pfsense_ha_virtual_ip: 192.168.2.254

    pfsense_firewall_rules:
      - name: "Allow SSH"
        action: pass
        interface: wan
        protocol: tcp
        destination_port: 22
```

**Deploy:**
```bash
uv run ansible-playbook playbooks/deploy-firewalls.yml \
  -i inventories/production/hosts/pfsense.yml
```

---

## High Availability Patterns

### Proxmox HA Cluster

**Three-node configuration (minimum for production):**

```yaml
proxmox_ha_enabled: true
proxmox_ha_groups:
  - group_name: "prod-cluster"
    nodes: [pve-node-01, pve-node-02, pve-node-03]
    priority: {pve-node-01: 1, pve-node-02: 2, pve-node-03: 3}

proxmox_ha_resources:
  - vmid: 100
    group: prod-cluster
    max_restart: 3        # Restart VM up to 3 times
    max_relocate: 1       # Relocate to different node after 3 failures
```

**Behavior:**
1. Node failure detected (fence timeout ~15s)
2. VM stopped on failed node
3. VM restarted on next preferred node
4. After 3 restarts, VM stays stopped (manual intervention)
5. After max_relocate moves, VM stays on current node

### Wireguard HA (Hub-and-Spoke)

**Primary + Secondary hubs with VIP:**

```yaml
wireguard_ha_mode: true
wireguard_hub_node: fw-primary

wireguard_hub_peers:
  - name: fw-secondary
    vpn_ip: 10.0.0.254
    role: backup
```

**Failover:**
- All traffic through primary hub
- Spokes monitor primary (via keepalive)
- Secondary hub active as backup
- Manual or VRRP-based failover

### Firewall HA (CARP)

**OPNSense or pfSense CARP setup:**

```yaml
opnsense_ha_enabled: true
opnsense_ha_mode: carp
opnsense_ha_vhid: 1
opnsense_ha_virtual_ip: 192.168.1.254
opnsense_ha_advskew_primary: 10
opnsense_ha_advskew_secondary: 200
```

**Automatic Failover:**
- Primary firewall owns VIP
- Secondary monitors via CARP heartbeat
- On primary failure, secondary takes VIP (1-3 seconds)
- All client connections failover automatically

---

## Integration Patterns

### Complete Infrastructure Deployment

```bash
# Deploy in stages
uv run ansible-playbook playbooks/deploy-infrastructure.yml \
  -i inventories/production/hosts/ \
  -e deploy_stage=all
```

**Deployment order:**
1. Proxmox hypervisors (HA cluster)
2. VMs boot and get network
3. Base OS configuration (common role)
4. Firewall deployment (OPNSense/pfSense HA)
5. Wireguard VPN (full mesh or hub-spoke)
6. Application deployment

### Monitoring Integration

All components report to centralized monitoring:

```yaml
# In common role (applied to all VMs)
common_monitoring_enabled: true
prometheus_scrape_configs:
  - job_name: proxmox
    static_configs:
      - targets: ['192.168.1.10:9090']

  - job_name: wireguard
    static_configs:
      - targets: ['10.0.0.1:9586']

  - job_name: firewall
    static_configs:
      - targets: ['192.168.1.1:9101']
```

### Backup Strategy

```yaml
# Proxmox backup
proxmox_backup_enabled: true
proxmox_backup_schedule:
  - vmid: 100
    schedule: "0 2 * * *"        # Daily at 2 AM
    retention_days: 7
    storage: local-lvm

# Firewall backup
firewall_backup_enabled: true
firewall_backup_schedule: "0 3 * * *"  # Daily at 3 AM

# VM snapshots
vm_snapshot_schedule: "0 1 * * *"  # Daily at 1 AM
```

---

## Troubleshooting

### Proxmox Issues

**VM won't start:**
```bash
# Check logs on Proxmox node
journalctl -u pvedaemon -f
qm status 100              # Check VM 100 status
qm start 100 --skiplock    # Force start if locked
```

**HA not working:**
```bash
# Check cluster status
pvecm status
ha-manager status          # View HA resources
ha-manager add vm:100      # Add VM to HA
```

### Wireguard Issues

**Connectivity problems:**
```bash
# Check VPN interface status
ip link show wg0
wg show wg0
ip addr show wg0

# Test reachability
ping -I 10.0.0.1 10.0.0.2
traceroute -i wg0 10.0.0.2

# Check MTU (should be ~1372 bytes less than physical MTU)
ping -M do -s 1372 10.0.0.2  # Should not fragment
```

**Key issues:**
```bash
# Verify key consistency
wg show wg0 public-key      # My public key
wg show wg0 peers           # Peer keys

# Regenerate keys if needed
wg genkey | tee /tmp/private.key | wg pubkey > /tmp/public.key
```

### Firewall Issues

**OPNSense API errors:**
```bash
# Test API connectivity
curl -k -u 'user:pass' https://opnsense-ip/api/core/system/status

# Check API token
ssh root@opnsense-ip
ocspctl system status
```

**pfSense SSH access:**
```bash
# Verify SSH is enabled and user exists
ssh -i ~/.ssh/firewall_key root@pfsense-ip
sudo grep -A5 "pfSense" /etc/motd  # Check version
```

### Ansible Debugging

```bash
# Verbose output
-v or -vv or -vvv (increase verbosity)

# Dry run (check mode)
--check

# Show diffs
--diff

# List tasks
--list-tasks

# Start at specific task
--start-at-task "Task name"
```

---

## Next Steps

1. **Customize Inventories:** Update IP addresses and hostnames
2. **Store Secrets:** Use Ansible Vault for passwords and API keys
3. **Set Up Monitoring:** Deploy Prometheus/Grafana for visibility
4. **Configure Backup:** Set up automated backups
5. **Document Access:** Create runbooks for common operations
6. **Test Failover:** Practice recovery procedures

For detailed role documentation, see:
- `roles/proxmox_infrastructure/README.md`
- `roles/wireguard_vpn/README.md`
- `roles/opnsense_firewall/README.md` (when created)
- `roles/pfsense_firewall/README.md` (when created)
