# Firewall Configuration: Upstream Modules & Alternatives

This document outlines upstream Ansible modules and community roles for firewall management.

---

## Current Implementation

The `firewall.yml` task uses **official upstream Ansible modules**:

| Platform | Module | Collection | Status |
|----------|--------|-----------|--------|
| Debian/Ubuntu | `community.general.ufw` | community.general | Maintained |
| RedHat/Rocky/Alma | `ansible.posix.firewalld` | ansible.posix | Maintained |

These are the official Ansible modules for firewall management, actively maintained by Red Hat and the community.

---

## Upstream Modules (Recommended)

### 1. community.general.ufw

**For**: Debian, Ubuntu, Linux Mint

**Features**:
- Simple, intuitive syntax
- Supports IPv4 and IPv6
- Source/destination IP filtering
- Rate limiting support
- Direction control (in/out/incoming/outgoing)

**Installation**:
```bash
ansible-galaxy collection install community.general
```

**Basic Usage**:
```yaml
- name: Allow SSH
  community.general.ufw:
    rule: allow
    port: 22
    proto: tcp
    from_ip: 192.168.1.0/24
```

**Module Documentation**:
```
https://docs.ansible.com/ansible/latest/collections/community/general/ufw_module.html
```

---

### 2. ansible.posix.firewalld

**For**: RHEL, CentOS, Rocky, Alma Linux, Fedora

**Features**:
- Zone-based firewall management
- Service and port management
- Rich rule support (complex filtering)
- Masquerading and port forwarding
- Timeout support for temporary rules

**Installation**:
```bash
ansible-galaxy collection install ansible.posix
```

**Basic Usage**:
```yaml
- name: Allow HTTP
  ansible.posix.firewalld:
    service: http
    state: enabled
    permanent: yes

- name: IP-based rule
  ansible.posix.firewalld:
    rich_rule: 'rule family="ipv4" source address="192.168.1.0/24" port protocol="tcp" port="22" accept'
    permanent: yes
    state: enabled
```

**Module Documentation**:
```
https://docs.ansible.com/ansible/latest/collections/ansible/posix/firewalld_module.html
```

---

## Community Roles (Alternative)

### 1. geerlingguy.firewall

**Author**: Jeff Geerling (Red Hat/Ansible expert)

**Features**:
- Supports both UFW and firewalld
- Simple variable-based configuration
- Well-tested across multiple OS versions
- Excellent documentation

**Installation**:
```bash
ansible-galaxy install geerlingguy.firewall
```

**Usage**:
```yaml
---
- hosts: all
  roles:
    - geerlingguy.firewall

  vars:
    firewall_allowed_tcp_ports:
      - 22
      - 80
      - 443
    firewall_allowed_udp_ports:
      - 53
```

**Galaxy Link**: https://galaxy.ansible.com/geerlingguy/firewall

**GitHub**: https://github.com/geerlingguy/ansible-role-firewall

---

### 2. fngry.ufw

**Author**: Fungry

**Features**:
- UFW-specific optimization
- Granular control over UFW configuration
- Support for application profiles

**Installation**:
```bash
ansible-galaxy install fngry.ufw
```

**Usage**:
```yaml
---
- hosts: debian_systems
  roles:
    - fngry.ufw

  vars:
    ufw_enabled: yes
    ufw_packages:
      - ufw
    ufw_defaults:
      - { direction: 'incoming', policy: 'deny' }
      - { direction: 'outgoing', policy: 'allow' }
    ufw_rules:
      - rule: allow
        port: 22
        proto: tcp
```

**Galaxy Link**: https://galaxy.ansible.com/fngry/ufw

---

### 3. stackhpc.firewall-config

**Author**: StackHPC Team

**Features**:
- Advanced filtering capabilities
- Supports nftables and iptables
- Template-based rule generation
- Production-ready

**Installation**:
```bash
ansible-galaxy install stackhpc.firewall-config
```

**Usage**:
```yaml
---
- hosts: all
  roles:
    - stackhpc.firewall-config

  vars:
    firewall_config_enabled: yes
    firewall_rules:
      - name: allow_ssh
        protocol: tcp
        destination_port: 22
        source_ip: 192.168.1.0/24
```

**Galaxy Link**: https://galaxy.ansible.com/stackhpc/firewall-config

---

## Comparison Matrix

| Feature | UFW Module | firewalld Module | geerlingguy | fngry | stackhpc |
|---------|-----------|-----------------|------------|-------|----------|
| **Debian Support** | ✓ | ✗ | ✓ | ✓ | ✓ |
| **RedHat Support** | ✗ | ✓ | ✓ | ✗ | ✓ |
| **Source IP filtering** | ✓ | ✓ (rich rules) | Limited | ✓ | ✓ |
| **Maintenance** | Active | Active | Well-maintained | Moderate | Active |
| **Documentation** | Official | Official | Excellent | Good | Comprehensive |
| **Community Users** | Large | Large | Very large | Medium | Medium |
| **Learning curve** | Easy | Moderate | Easy | Easy | Moderate |

---

## Recommendation

### Current Implementation (This Project)

**Why we use raw modules**:
- Direct control over configuration
- No abstraction layer overhead
- Clearer implementation logic
- Works across Debian AND RedHat in one task file
- Maximum flexibility for custom rules

### If Simplification Needed

**Use `geerlingguy.firewall`** if you want:
- Pre-built role with less configuration
- Jeff Geerling's community reputation
- Simpler variable structure
- Less custom rule management

### If Advanced Features Needed

**Use `stackhpc.firewall-config`** if you want:
- Template-based rule generation
- nftables optimization
- Complex rule orchestration
- Enterprise-grade features

---

## Module Reference Quick Lookup

### UFW Module Parameters

```yaml
community.general.ufw:
  rule: allow|deny|reject
  port: <number>
  proto: tcp|udp|icmp|esp|ah
  from_ip: <IP/CIDR>
  to_ip: <IP/CIDR>
  from_port: <number>
  to_port: <number>
  direction: in|out|incoming|outgoing
  interface: <interface_name>
  state: enabled|disabled|reset
  comment: <string>
```

### firewalld Module Parameters

```yaml
ansible.posix.firewalld:
  service: <service_name>
  port: <port/protocol>
  rich_rule: <rule_string>
  zone: public|internal|external|dmz|trusted|home|work|block|drop
  state: enabled|disabled
  permanent: yes|no
  immediate: yes|no
  masquerade: yes|no
  timeout: <seconds>
```

---

## Migration Path

If you want to migrate from raw modules to a community role:

### Option 1: geerlingguy.firewall

**Step 1**: Map current variables
```yaml
# Current (raw modules)
firewall_custom_rules:
  - rule: allow
    port: 80

# geerlingguy equivalent
firewall_allowed_tcp_ports:
  - 80
```

**Step 2**: Install role
```bash
ansible-galaxy install geerlingguy.firewall
```

**Step 3**: Replace task with role
```yaml
# Remove: roles/common/tasks/firewall.yml
# Add to playbook:
- role: geerlingguy.firewall
```

---

## Summary

| Approach | Pros | Cons |
|----------|------|------|
| **Raw modules** (current) | Full control, flexible, lightweight | More code, custom maintenance |
| **geerlingguy role** | Simple, well-tested, excellent docs | Less flexible, learning role parameters |
| **stackhpc role** | Advanced features, enterprise-ready | More complex, steeper learning curve |

**Current recommendation**: Keep raw modules for maximum control and cross-platform support in this project.

---

**Last Updated**: November 17, 2025
