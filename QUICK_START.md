# Quick Start - Network Infrastructure Automation

Get Proxmox + Wireguard + Firewall running in 30 minutes.

## 1. Install Collections (2 min)

```bash
cd ansible-infra
uv run ansible-galaxy collection install -r requirements.yml
```

## 2. Copy & Customize Inventory (5 min)

```bash
# Copy examples
cp inventories/production/hosts/proxmox-example.yml inventories/production/hosts/proxmox.yml
cp inventories/production/hosts/wireguard-example.yml inventories/production/hosts/wireguard.yml

# Edit with your IPs and hostnames
vim inventories/production/hosts/proxmox.yml
vim inventories/production/hosts/wireguard.yml

# Create vault for secrets
echo 'your-vault-password' > ~/.ansible-vault-pass
```

## 3. Deploy Proxmox (10 min)

```bash
# Single node (minimal)
uv run ansible-playbook playbooks/deploy-proxmox.yml \
  -i inventories/production/hosts/proxmox.yml

# Or: 3-node HA cluster (uncomment HA vars in inventory)
# Deployment takes 5-10 minutes
```

## 4. Deploy Wireguard VPN (5 min)

Choose your topology:

**Full Mesh (all peer to all):**
```bash
uv run ansible-playbook playbooks/deploy-wireguard.yml \
  -i inventories/production/hosts/wireguard.yml \
  -e "wireguard_topology=full_mesh"
```

**Hub-and-Spoke with HA (recommended):**
```bash
uv run ansible-playbook playbooks/deploy-wireguard.yml \
  -i inventories/production/hosts/wireguard.yml \
  -e "wireguard_topology=hub_spoke"
```

**Site-to-Site Multi-Location:**
```bash
uv run ansible-playbook playbooks/deploy-wireguard.yml \
  -i inventories/production/hosts/wireguard.yml \
  -e "wireguard_topology=site_to_site"
```

## 5. Verify Everything Works (3 min)

```bash
# Test connectivity to all hosts
ansible all -i inventories/production/hosts/ -m ping

# Check Proxmox VMs
ansible proxmox_hypervisors -m shell -a "qm list"

# Check Wireguard status
ansible wireguard_nodes -m shell -a "wg show" 2>/dev/null || echo "VPN not deployed"
```

## Configuration Matrix

| Want | Command |
|------|---------|
| **Single Proxmox node** | Uncomment basic vars in inventory |
| **3-node Proxmox HA** | Uncomment `proxmox_ha_enabled: true` and HA vars |
| **Wireguard full mesh** | `-e "wireguard_topology=full_mesh"` |
| **Wireguard with failover** | `-e "wireguard_topology=hub_spoke" -e "wireguard_ha_mode=true"` |
| **OPNSense firewall** | Add to inventory (framework ready) |
| **pfSense firewall** | Add to inventory (framework ready) |

## Example Commands

### Deploy everything (production)
```bash
uv run ansible-playbook playbooks/deploy-infrastructure.yml \
  -i inventories/production/hosts/ \
  -e deploy_stage=all \
  --vault-password-file ~/.ansible-vault-pass
```

### Deploy just VMs
```bash
uv run ansible-playbook playbooks/deploy-proxmox.yml \
  -i inventories/production/hosts/proxmox.yml
```

### Check before deploying
```bash
ansible-playbook playbooks/deploy-proxmox.yml \
  -i inventories/production/hosts/proxmox.yml \
  --check --diff
```

### View what will happen
```bash
ansible-playbook playbooks/deploy-proxmox.yml \
  -i inventories/production/hosts/proxmox.yml \
  --list-tasks
```

## Troubleshooting

**Ansible not found?**
```bash
pip install ansible-core>=2.12 proxmoxer requests
```

**API connection error?**
```bash
# Test manually
python3 -c "from proxmoxer import ProxmoxAPI; print('OK')"

# Check credentials in inventory
grep -A3 proxmox_api inventories/production/hosts/proxmox.yml
```

**Wireguard not applying?**
```bash
# Check if nodes are in inventory
grep -A5 "wireguard_nodes:" inventories/production/hosts/wireguard.yml

# Test SSH to nodes
ansible wireguard_nodes -m ping -i inventories/production/hosts/
```

**Keys permission error?**
```bash
chmod 600 ~/.ssh/proxmox_key ~/.ssh/wireguard_key
ssh-keygen -y -f ~/.ssh/proxmox_key > ~/.ssh/proxmox_key.pub
```

## Next: Read Full Documentation

- `docs/NETWORK_INFRASTRUCTURE_GUIDE.md` - Complete guide
- `docs/IMPLEMENTATION_SUMMARY.md` - What was built
- `roles/proxmox_infrastructure/README.md` - Proxmox details
- `roles/wireguard_vpn/README.md` - Wireguard details

## Architecture Recap

```
Internet
   ↓
[OPNSense/pfSense Firewall HA]
   ↓
[Proxmox Cluster (HA)]
   ├─ Web VMs
   ├─ DB VMs
   └─ Cache VMs
   ↓
[Wireguard VPN]
   ├─ Full Mesh (simple, all peer to all)
   ├─ Hub-Spoke (recommended, HA failover)
   └─ Site-to-Site (multi-location)
```

## Typical Deployment Timeline

| Stage | Time | Action |
|-------|------|--------|
| 1 | 5 min | Proxmox deploys hypervisors |
| 2 | 10 min | VMs boot and get network |
| 3 | 5 min | Firewalls initialize |
| 4 | 5 min | Wireguard VPN connects all |
| 5 | 5 min | Applications start |
| **Total** | **30 min** | **Full infrastructure online** |

## Common Customizations

**Add more VMs:**
```yaml
# inventories/production/hosts/proxmox.yml
proxmox_vms:
  - name: web-01
    vmid: 100
  - name: web-02          # Add this
    vmid: 101
  - name: db-01
    vmid: 200
```

**Change VPN network:**
```yaml
# inventories/production/hosts/wireguard.yml
wireguard_vpn_network: "10.20.0.0/24"  # Change from 10.0.0.0/24
```

**Enable Proxmox HA:**
```yaml
# inventories/production/hosts/proxmox.yml
proxmox_ha_enabled: true
proxmox_ha_groups:
  - group_name: prod
    nodes: [pve-01, pve-02, pve-03]
```

## Getting Help

1. Check role README.md files
2. Review `docs/NETWORK_INFRASTRUCTURE_GUIDE.md`
3. Search upstream role documentation:
   - https://docs.ansible.com/ansible/latest/collections/community/proxmox/
   - https://opnsense.ansibleguy.net/
   - https://github.com/pfsensible/core

---

**You're ready! Start with Step 1 above.**
