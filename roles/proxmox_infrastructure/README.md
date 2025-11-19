# Proxmox Infrastructure Role

Manages Proxmox VE cluster configuration and VM/container lifecycle using the `community.proxmox` collection.

## Overview

This role provides:
- Proxmox cluster initialization and configuration
- VM/LXC container creation and management
- Cloud-init template handling
- High Availability (HA) group configuration (optional)
- API token management
- Network interface configuration
- Storage and disk management

## Requirements

- Proxmox VE 6.0+ installed and accessible
- `community.proxmox` collection (>=1.4.0)
- `proxmoxer` Python library on control node
- SSH key-based access to Proxmox hosts

Install Python dependencies:
```bash
pip install proxmoxer requests
```

## Role Variables

### Required Variables

```yaml
# Proxmox API connection
proxmox_api_host: "192.168.1.10"           # Proxmox host IP
proxmox_api_user: "root@pam"               # API user
proxmox_api_password: "{{ vault_proxmox_password }}"
proxmox_node: "pve-node-01"                # Node name for VM creation

# VM Configuration (per host)
proxmox_vms:
  - name: "web-01"
    template: "ubuntu-22.04"               # Template to clone from
    vmid: 100
    cores: 4
    memory: 8192
    disk: 50                               # GB
    storage: "local-lvm"
    net0: "virtio,bridge=vmbr0"
    state: present                         # present or absent
```

### Optional Variables - High Availability (HA)

```yaml
# Enable HA management
proxmox_ha_enabled: false                  # Enable HA configuration

# HA Group configuration (when enabled)
proxmox_ha_groups:
  - group_name: "web-cluster"
    nodes:
      - "pve-node-01"
      - "pve-node-02"
      - "pve-node-03"
    priority:
      pve-node-01: 1
      pve-node-02: 2
      pve-node-03: 3

# HA Resource (VM) configuration
proxmox_ha_resources:
  - vmid: 100
    state: started
    group: "web-cluster"
    max_relocate: 1
    max_restart: 3
```

### Optional Variables - Cloud-Init Templates

```yaml
# Cloud-init template management
proxmox_cloudinit_enabled: true            # Enable cloud-init handling

# Cloud-init template creation (import from URL)
proxmox_cloudinit_templates:
  - name: "ubuntu-22.04"
    image_url: "https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img"
    storage: "local"
    vmid: 9000

# Default cloud-init config
proxmox_cloudinit_config:
  hostname: "{{ inventory_hostname }}"
  user: "ubuntu"
  ssh_keys:
    - "{{ lookup('file', '~/.ssh/id_ed25519.pub') }}"
  packages:
    - qemu-guest-agent
    - curl
    - git
```

### Optional Variables - API Token Management

```yaml
# Create Proxmox API tokens for automation
proxmox_api_tokens:
  - name: "ansible-automation"
    user: "ansible@pam"
    privileges: "Datastore.AllocateSpace,Pool.Allocate,Sys.Audit,VM.Allocate,VM.Clone,VM.Console,VM.Migrate,VM.Monitor,VM.PowerMgmt"
```

### Optional Variables - Network Configuration

```yaml
# Network bridges and VLANs
proxmox_network_bridges:
  - name: "vmbr1"
    ports: ["eno2"]
    vlan_aware: true
    stp: false

# VLAN configuration
proxmox_vlans:
  - iface: "vmbr1"
    vlan: 100
    name: "vlan100"
```

### Optional Variables - Storage Configuration

```yaml
# Storage backend configuration
proxmox_storage:
  - storage: "ceph-pool"
    type: "rbd"
    content: "images,rootdir"
    pool: "rbd"
    nodes:
      - "pve-node-01"
      - "pve-node-02"
      - "pve-node-03"

# LVM volume group creation
proxmox_lvm_vg:
  - name: "pve-local"
    pvs: ["/dev/sdb"]
```

## Example Inventory - Single Node

```yaml
# inventories/production/hosts/proxmox.yml
proxmox_hypervisors:
  hosts:
    pve-node-01:
      ansible_host: 192.168.1.10
      proxmox_node: pve-node-01

  vars:
    proxmox_api_host: 192.168.1.10
    proxmox_api_user: root@pam
    proxmox_api_password: "{{ vault_proxmox_password }}"

    # VMs to manage
    proxmox_vms:
      - name: web-01
        vmid: 100
        template: ubuntu-22.04
        cores: 4
        memory: 8192
        disk: 50
        net0: "virtio,bridge=vmbr0"

vm_cluster:
  hosts:
    web-01:
      ansible_host: "192.168.1.100"
      depends_on: pve-node-01
```

## Example Inventory - HA Cluster

```yaml
# inventories/production/hosts/proxmox-ha.yml
proxmox_hypervisors:
  hosts:
    pve-node-01:
      ansible_host: 192.168.1.10
    pve-node-02:
      ansible_host: 192.168.1.11
    pve-node-03:
      ansible_host: 192.168.1.12

  vars:
    proxmox_api_host: 192.168.1.10
    proxmox_api_user: root@pam
    proxmox_api_password: "{{ vault_proxmox_password }}"

    # Enable HA
    proxmox_ha_enabled: true

    proxmox_ha_groups:
      - group_name: "web-cluster"
        nodes: [pve-node-01, pve-node-02, pve-node-03]
        priority:
          pve-node-01: 1
          pve-node-02: 2
          pve-node-03: 3

    proxmox_ha_resources:
      - vmid: 100
        group: web-cluster
        max_restart: 3
        max_relocate: 1
      - vmid: 101
        group: web-cluster
        max_restart: 3
        max_relocate: 1

    # VMs
    proxmox_vms:
      - name: web-01
        vmid: 100
        template: ubuntu-22.04
        cores: 4
        memory: 8192
      - name: web-02
        vmid: 101
        template: ubuntu-22.04
        cores: 4
        memory: 8192

vm_cluster:
  hosts:
    web-01: {ansible_host: 192.168.1.100}
    web-02: {ansible_host: 192.168.1.101}
```

## Usage

### Deploy to Single Proxmox Node

```bash
# Create VMs on single node
uv run ansible-playbook playbooks/deploy-proxmox.yml \
  -i inventories/production/hosts/proxmox.yml
```

### Deploy HA Proxmox Cluster

```bash
# Initialize cluster with HA
uv run ansible-playbook playbooks/deploy-proxmox-ha.yml \
  -i inventories/production/hosts/proxmox-ha.yml
```

### Add/Update VMs (Idempotent)

```bash
# Update configuration on existing VMs
uv run ansible-playbook playbooks/deploy-proxmox.yml \
  -i inventories/production/hosts/proxmox.yml \
  -e "proxmox_state=present"
```

### Remove VMs

```bash
# Delete VMs (use with caution!)
uv run ansible-playbook playbooks/deploy-proxmox.yml \
  -i inventories/production/hosts/proxmox.yml \
  -e "proxmox_state=absent"
```

## Task Organization

- `validate-environment.yml` - Check Proxmox prerequisites
- `api-connection.yml` - Configure API authentication
- `cluster-setup.yml` - Initialize Proxmox cluster (if needed)
- `vm-management.yml` - Create/update/delete VMs
- `cloudinit-templates.yml` - Manage cloud-init templates
- `ha-configuration.yml` - Configure HA groups and resources
- `network-management.yml` - Configure bridges, VLANs, bonds
- `storage-management.yml` - Configure storage backends
- `api-token-management.yml` - Create API tokens for automation

## Limitations & Known Issues

1. **Cloud-init Template Import**: Requires manual image download or custom shell execution (not available in community.proxmox)
2. **Template Cloning**: Must use existing templates; creating from scratch requires additional steps
3. **Storage Types**: Advanced storage (Ceph, ZFS) require additional nodes and setup
4. **Network Configuration**: Some advanced networking features may require manual qm commands

## Handler Patterns

```yaml
# Restart Proxmox services
- name: Reload Proxmox configuration
  handlers:
    - name: restart-pve-services
    - name: reload-network-config
```

## Security Notes

- Store `proxmox_api_password` in Ansible Vault
- Use limited-privilege API tokens when possible
- Restrict SSH access to Proxmox nodes
- Enable 2FA on Proxmox web interface

## Integration with Common Role

This role works alongside the `common` role:
- `common` configures base Linux for VMs
- `proxmox_infrastructure` manages VM lifecycle
- Run `common` role on each created VM after provisioning

## Testing

Test role locally:
```bash
# Validate syntax
ansible-playbook --syntax-check playbooks/deploy-proxmox.yml

# Dry-run (check mode)
uv run ansible-playbook playbooks/deploy-proxmox.yml \
  --check -i inventories/production/hosts/proxmox.yml
```

## References

- [Proxmox VE API Documentation](https://pve.proxmox.com/pve-docs/api-viewer/)
- [community.proxmox Collection Docs](https://docs.ansible.com/ansible/latest/collections/community/proxmox/index.html)
- [proxmoxer Python Library](https://github.com/proxmox/proxmoxer)
