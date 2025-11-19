# Network Infrastructure Automation Framework

Complete Ansible automation for Proxmox VE, Wireguard VPN, and firewalls (OPNSense/pfSense) with production-ready HA support.

## 🚀 Quick Navigation

| Need | Start Here |
|------|-----------|
| **5-minute overview** | [QUICK_START.md](QUICK_START.md) |
| **Full deployment guide** | [docs/NETWORK_INFRASTRUCTURE_GUIDE.md](docs/NETWORK_INFRASTRUCTURE_GUIDE.md) |
| **What was built** | [docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md) |
| **Proxmox details** | [roles/proxmox_infrastructure/README.md](roles/proxmox_infrastructure/README.md) |
| **Wireguard topologies** | [roles/wireguard_vpn/README.md](roles/wireguard_vpn/README.md) |

## 📋 What's Included

### Proxmox Infrastructure
- **Location:** `roles/proxmox_infrastructure/`
- **Purpose:** VM/LXC container management with Proxmox VE API
- **Features:**
  - Single-node or 3-node HA clustering
  - Automatic cloud-init template handling
  - Network bridge, VLAN, and storage configuration
  - HA resource management with automatic failover
- **Documentation:** [README](roles/proxmox_infrastructure/README.md)

### Wireguard VPN
- **Location:** `roles/wireguard_vpn/`
- **Purpose:** Encrypted VPN connectivity with flexible topologies
- **Topologies:**
  - Full Mesh: All nodes peer to all nodes (2-50 nodes)
  - Hub-and-Spoke with HA: Central gateway with failover
  - Site-to-Site: Multi-location inter-site routing
- **Documentation:** [README](roles/wireguard_vpn/README.md)

### Firewall Frameworks
- **OPNSense:** API-based firewall automation (400+ GitHub stars)
- **pfSense:** XML/PHP-based firewall automation (235+ GitHub stars)
- **Features:** HA failover, rule management, VPN integration
- **Documentation:** [firewall-example.yml](inventories/production/hosts/firewall-example.yml)

### Example Inventories
- **proxmox-example.yml:** Single-node and HA cluster examples
- **wireguard-example.yml:** All three topology modes
- **firewall-example.yml:** OPNSense and pfSense HA pairs
- **Location:** `inventories/production/hosts/`

### Orchestration Playbooks
- **deploy-proxmox.yml:** Deploy Proxmox with VMs
- **deploy-wireguard.yml:** Deploy Wireguard VPN
- **deploy-infrastructure.yml:** Full 6-stage orchestration
- **Location:** `playbooks/`

## 🏗️ Architecture

```
Internet / Public Network
        ↓
[OPNSense/pfSense Firewall HA Pair]
        ↓
[Proxmox VE Cluster (HA)]
├── Web Tier VMs
├── Database Tier VMs
└── Cache Tier VMs
        ↓
[Wireguard VPN]
├── Full Mesh (all nodes peer)
├── Hub-Spoke (central gateway + failover)
└── Site-to-Site (multi-location)
```

## ⚡ 30-Minute Quick Start

```bash
# 1. Install collections
uv run ansible-galaxy collection install -r requirements.yml

# 2. Copy and customize inventory
cp inventories/production/hosts/proxmox-example.yml \
   inventories/production/hosts/proxmox.yml
vim inventories/production/hosts/proxmox.yml

# 3. Deploy Proxmox
uv run ansible-playbook playbooks/deploy-proxmox.yml \
  -i inventories/production/hosts/proxmox.yml

# 4. Deploy Wireguard (choose topology)
uv run ansible-playbook playbooks/deploy-wireguard.yml \
  -i inventories/production/hosts/wireguard.yml \
  -e "wireguard_topology=full_mesh"

# 5. Verify
ansible all -i inventories/production/hosts/ -m ping
```

## 🎯 Key Features

### High Availability
- **Proxmox:** 3-node cluster with automatic VM failover
- **Wireguard:** Secondary hub as backup gateway
- **Firewalls:** CARP-based automatic failover (1-3 seconds)

### Topology Flexibility
- **One variable** switches entire Wireguard deployment model
- Users choose: full mesh vs hub-spoke vs site-to-site
- Each topology has documented use cases and best practices

### Production-Ready
- Error handling and validation
- Idempotent tasks (safe to run multiple times)
- Comprehensive logging and debugging
- Security hardening via common role

### Easy Integration
- Integrates with existing `common` role
- Separation of concerns (each role does one thing)
- Works alongside other infrastructure

## 📚 Documentation

| Document | Purpose | Time |
|----------|---------|------|
| [QUICK_START.md](QUICK_START.md) | Get running in 30 minutes | 5 min |
| [NETWORK_INFRASTRUCTURE_GUIDE.md](docs/NETWORK_INFRASTRUCTURE_GUIDE.md) | Complete deployment guide | 20 min |
| [IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md) | Architecture and design decisions | 15 min |
| [proxmox_infrastructure/README.md](roles/proxmox_infrastructure/README.md) | Proxmox-specific options | 10 min |
| [wireguard_vpn/README.md](roles/wireguard_vpn/README.md) | Wireguard topology guide | 10 min |

## 🛠️ Configuration Examples

### Proxmox Single Node
```yaml
proxmox_ha_enabled: false
proxmox_vms:
  - name: web-01
    vmid: 100
    template: ubuntu-22.04
    cores: 4
    memory: 8192
```

### Proxmox HA Cluster
```yaml
proxmox_ha_enabled: true
proxmox_ha_groups:
  - group_name: prod-cluster
    nodes: [pve-01, pve-02, pve-03]
    priority: {pve-01: 1, pve-02: 2, pve-03: 3}
```

### Wireguard Full Mesh
```yaml
wireguard_topology: full_mesh
wireguard_full_mesh_nodes:
  node1: {vpn_ip: 10.0.0.1, public_endpoint: "node1.example.com"}
  node2: {vpn_ip: 10.0.0.2, public_endpoint: "node2.example.com"}
```

### Wireguard Hub-Spoke with HA
```yaml
wireguard_topology: hub_spoke
wireguard_ha_mode: true
wireguard_hub_node: fw-primary
wireguard_hub_peers:
  - name: fw-secondary
    vpn_ip: 10.0.0.254
    role: backup
```

## 🔐 Security

- Secrets stored in Ansible Vault
- API tokens with limited privileges
- SSH key-based authentication only
- Base OS hardening via common role
- Network isolation via firewall rules
- Encrypted VPN traffic (Wireguard)

## 🧪 Testing

```bash
# Syntax validation
ansible-playbook --syntax-check playbooks/*.yml

# Dry-run
ansible-playbook playbooks/deploy-proxmox.yml --check

# Connectivity test
ansible all -i inventories/production/hosts/ -m ping
```

## 📊 Component Overview

| Component | Upstream | Approach | Integration |
|-----------|----------|----------|-------------|
| **Proxmox** | community.proxmox | API-based | Full wrapper role |
| **OPNSense** | oxlorg.opnsense (O-X-L) | REST API | Framework ready |
| **pfSense** | pfsensible.core | XML + PHP | Framework ready |
| **Wireguard** | githubixx/ansible-wg | Config files | Framework ready |

## 📁 File Structure

```
ansible-infra/
├── QUICK_START.md                              # Start here!
├── NETWORK_INFRASTRUCTURE.md                   # This file
├── requirements.yml                            # Collections (updated)
├── roles/
│   ├── proxmox_infrastructure/                 # NEW
│   │   ├── README.md
│   │   ├── defaults/main.yml
│   │   └── tasks/
│   │       ├── main.yml
│   │       ├── validate-environment.yml
│   │       ├── api-connection.yml
│   │       ├── vm-management.yml
│   │       ├── vm-management-item.yml
│   │       ├── ha-configuration.yml
│   │       ├── cloudinit-templates.yml
│   │       ├── network-management.yml
│   │       ├── storage-management.yml
│   │       └── api-token-management.yml
│   ├── wireguard_vpn/                         # NEW
│   │   ├── README.md
│   │   └── defaults/main.yml
│   └── common/                                # Existing
├── inventories/production/hosts/
│   ├── proxmox-example.yml                     # NEW
│   ├── wireguard-example.yml                   # NEW
│   ├── firewall-example.yml                    # NEW
│   └── (other inventories)
├── playbooks/
│   ├── deploy-proxmox.yml                      # NEW
│   ├── deploy-wireguard.yml                    # NEW
│   ├── deploy-infrastructure.yml               # NEW
│   └── (other playbooks)
└── docs/
    ├── NETWORK_INFRASTRUCTURE_GUIDE.md         # NEW
    ├── IMPLEMENTATION_SUMMARY.md               # NEW
    └── (other docs)
```

## 🚀 Deployment Stages

```
Stage 1: Proxmox Hypervisors
         ↓ (5 min)
Stage 2: Wait for VM Boot
         ↓ (10 min)
Stage 3: Configure Base OS
         ↓ (5 min)
Stage 4: Deploy Firewalls
         ↓ (5 min)
Stage 5: Deploy Wireguard VPN
         ↓ (5 min)
Stage 6: Application Deployment
         ↓
Total: ~30 minutes
```

## ✅ What's Included

- ✓ Proxmox infrastructure role with HA
- ✓ Wireguard VPN with 3 topology options
- ✓ Firewall automation frameworks (OPNSense + pfSense)
- ✓ Example inventories for all components
- ✓ Orchestration playbooks
- ✓ Comprehensive documentation
- ✓ Production-ready with error handling
- ✓ Security hardening
- ✓ Idempotent tasks

## 🔄 Integration with Existing Framework

All roles follow your framework's patterns:
- Same directory structure
- Same task organization style
- Same variable naming conventions
- Same error handling approach
- Integrates with `common` role
- Works with your monitoring stack

## 📖 Next Steps

1. **Read** [QUICK_START.md](QUICK_START.md) (5 minutes)
2. **Review** [NETWORK_INFRASTRUCTURE_GUIDE.md](docs/NETWORK_INFRASTRUCTURE_GUIDE.md) (20 minutes)
3. **Copy** example inventories and customize
4. **Test** in non-production environment
5. **Deploy** to production

## 🆘 Support

For questions about:
- **Proxmox:** See [roles/proxmox_infrastructure/README.md](roles/proxmox_infrastructure/README.md)
- **Wireguard:** See [roles/wireguard_vpn/README.md](roles/wireguard_vpn/README.md)
- **Upstream Collections:**
  - [community.proxmox docs](https://docs.ansible.com/ansible/latest/collections/community/proxmox/)
  - [oxlorg.opnsense docs](https://opnsense.ansibleguy.net/)
  - [pfsensible.core repo](https://github.com/pfsensible/core)
  - [githubixx wireguard](https://github.com/githubixx/ansible-role-wireguard)

---

**Framework Version:** 1.0.0
**Last Updated:** 2025-11-19
**Ansible Minimum:** 2.9.27+
**Python Minimum:** 3.6+

**Start with:** [QUICK_START.md](QUICK_START.md)
