# Firewall Configuration Guide

Complete firewall setup for Debian/Ubuntu (UFW) and RedHat/Rocky/Alma (firewalld).

---

## Table of Contents

1. [Basic Configuration](#basic-configuration)
2. [Debian/Ubuntu (UFW)](#debianubuntu-ufw-configuration)
3. [RedHat/Rocky/Alma (firewalld)](#redhatrockyalma-firewalld-configuration)
4. [Complete Examples](#complete-examples)
5. [Verification](#verification)
6. [Upstream Modules & Alternatives](#upstream-modules--alternatives)

---

## Basic Configuration

### Default Configuration

By default, only SSH and ICMP are allowed:
- **SSH**: Port 22 (configurable)
- **ICMP**: Ping (rate-limited to 10/minute)
- **Default Policy**: DROP incoming, ACCEPT outgoing

### Quick Start

Enable firewall with custom rules:

```yaml
# group_vars/all.yml or inventory/hosts.yml
firewall_enabled: true
firewall_ssh_port: 22
firewall_allow_icmp: true
```

---

## Debian/Ubuntu (UFW) Configuration

### Basic Custom Rules

Add ports and IP-based rules using `firewall_custom_rules`:

```yaml
# group_vars/all.yml or inventory/hosts.yml
firewall_enabled: true
firewall_ssh_port: 22
firewall_allow_icmp: true

firewall_custom_rules:
  # Allow HTTP from anywhere
  - rule: allow
    port: 80
    proto: tcp
    comment: "Allow HTTP"

  # Allow HTTPS from anywhere
  - rule: allow
    port: 443
    proto: tcp
    comment: "Allow HTTPS"

  # Allow SSH only from internal network
  - rule: allow
    port: 22
    proto: tcp
    from_ip: 192.168.1.0/24
    comment: "Allow SSH from internal"

  # Block SSH from specific IP
  - rule: deny
    port: 22
    proto: tcp
    from_ip: 10.0.0.5
    comment: "Block SSH from suspicious IP"

  # Allow MySQL only from app servers
  - rule: allow
    port: 3306
    proto: tcp
    from_ip: 10.0.1.0/24
    comment: "Allow MySQL from app tier"

  # Allow PostgreSQL from specific IPs
  - rule: allow
    port: 5432
    proto: tcp
    from_ip: 10.0.1.0/24
    comment: "Allow PostgreSQL from app tier"

  # Allow DNS from internal network
  - rule: allow
    port: 53
    proto: udp
    from_ip: 192.168.1.0/24
    comment: "Allow DNS from internal"
```

### UFW Rule Parameters

```yaml
- rule: allow|deny|reject        # Action to take
  port: 80                        # Port number (optional)
  proto: tcp|udp|icmp             # Protocol (default: tcp)
  from_ip: 192.168.1.0/24         # Source IP/CIDR (optional)
  to_ip: 10.0.0.0/8               # Destination IP/CIDR (optional)
  direction: in|out               # Direction (default: in)
  comment: "Description"          # Comment for the rule
```

---

## RedHat/Rocky/Alma (firewalld) Configuration

### Simple Port Rules

Use `firewall_services` for predefined services and `firewall_ports` for custom ports:

```yaml
# group_vars/all.yml or inventory/hosts.yml
firewall_enabled: true
firewall_zone: public
firewall_allow_icmp: true

# Allow predefined services
firewall_services:
  - service: http
    state: enabled
  - service: https
    state: enabled

# Allow custom ports
firewall_ports:
  - port: 3306
    proto: tcp
    state: enabled
  - port: 5432
    proto: tcp
    state: enabled
  - port: 53
    proto: udp
    state: enabled
```

### IP-Based Rules (Rich Rules)

For complex filtering with specific IP addresses, use `firewall_rich_rules`:

```yaml
firewall_rich_rules:
  # Allow SSH only from internal network
  - rule: 'rule family="ipv4" source address="192.168.1.0/24" port protocol="tcp" port="22" accept'

  # Block SSH from specific IP
  - rule: 'rule family="ipv4" source address="10.0.0.5" port protocol="tcp" port="22" reject'

  # Allow HTTP from anywhere
  - rule: 'rule family="ipv4" port protocol="tcp" port="80" accept'

  # Allow HTTPS from anywhere
  - rule: 'rule family="ipv4" port protocol="tcp" port="443" accept'

  # Allow MySQL only from app tier
  - rule: 'rule family="ipv4" source address="10.0.1.0/24" port protocol="tcp" port="3306" accept'

  # Allow PostgreSQL from app tier
  - rule: 'rule family="ipv4" source address="10.0.1.0/24" port protocol="tcp" port="5432" accept'

  # Allow DNS from internal network
  - rule: 'rule family="ipv4" source address="192.168.1.0/24" port protocol="udp" port="53" accept'

  # Reject everything else
  - rule: 'rule family="ipv4" reject'
```

### firewalld Rich Rule Syntax

```
rule [family="ipv4|ipv6"] [source address="IP/CIDR"] [destination address="IP"]
  [port protocol="tcp|udp" port="NUMBER"]
  [accept|reject|drop]
```

---

## Complete Examples

### Example 1: Simple Web Server (Debian)

```yaml
# group_vars/web_servers.yml
firewall_enabled: true

firewall_custom_rules:
  - rule: allow
    port: 80
    proto: tcp
    comment: "HTTP"
  - rule: allow
    port: 443
    proto: tcp
    comment: "HTTPS"
```

### Example 2: Multi-Tier Architecture (Debian)

```yaml
# group_vars/web_servers.yml
firewall_custom_rules:
  - rule: allow
    port: 80
    proto: tcp
    comment: "HTTP from anywhere"
  - rule: allow
    port: 443
    proto: tcp
    comment: "HTTPS from anywhere"
  - rule: allow
    port: 22
    proto: tcp
    from_ip: 10.0.0.0/8
    comment: "SSH from internal only"

# group_vars/app_servers.yml
firewall_custom_rules:
  - rule: allow
    port: 8080
    proto: tcp
    from_ip: 10.0.1.0/24
    comment: "App from web tier"
  - rule: allow
    port: 22
    proto: tcp
    from_ip: 10.0.0.0/8
    comment: "SSH from internal only"

# group_vars/db_servers.yml
firewall_custom_rules:
  - rule: allow
    port: 3306
    proto: tcp
    from_ip: 10.0.1.0/24
    comment: "MySQL from app tier"
  - rule: allow
    port: 22
    proto: tcp
    from_ip: 10.0.0.0/8
    comment: "SSH from internal only"
```

### Example 3: Multi-Tier Architecture (RedHat)

```yaml
# group_vars/web_servers.yml
firewall_services:
  - service: http
    state: enabled
  - service: https
    state: enabled

firewall_rich_rules:
  - rule: 'rule family="ipv4" source address="10.0.0.0/8" port protocol="tcp" port="22" accept'
  - rule: 'rule family="ipv4" reject'

# group_vars/app_servers.yml
firewall_ports:
  - port: 8080
    proto: tcp
    state: enabled

firewall_rich_rules:
  - rule: 'rule family="ipv4" source address="10.0.1.0/24" port protocol="tcp" port="8080" accept'
  - rule: 'rule family="ipv4" source address="10.0.0.0/8" port protocol="tcp" port="22" accept'
  - rule: 'rule family="ipv4" reject'

# group_vars/db_servers.yml
firewall_ports:
  - port: 3306
    proto: tcp
    state: enabled

firewall_rich_rules:
  - rule: 'rule family="ipv4" source address="10.0.1.0/24" port protocol="tcp" port="3306" accept'
  - rule: 'rule family="ipv4" source address="10.0.0.0/8" port protocol="tcp" port="22" accept'
  - rule: 'rule family="ipv4" reject'
```

### Example 4: Production Cluster (Mixed OS)

```yaml
# group_vars/production.yml

# For Debian/Ubuntu systems
firewall_custom_rules:
  - rule: allow
    port: 80
    proto: tcp
    from_ip: 0.0.0.0/0
    comment: "HTTP from anywhere"
  - rule: allow
    port: 443
    proto: tcp
    from_ip: 0.0.0.0/0
    comment: "HTTPS from anywhere"
  - rule: allow
    port: 3306
    proto: tcp
    from_ip: 10.0.1.0/24
    comment: "MySQL from app tier"
  - rule: allow
    port: 5432
    proto: tcp
    from_ip: 10.0.1.0/24
    comment: "PostgreSQL from app tier"
  - rule: allow
    port: 6379
    proto: tcp
    from_ip: 10.0.1.0/24
    comment: "Redis from app tier"
  - rule: allow
    port: 22
    proto: tcp
    from_ip: 10.0.0.0/8
    comment: "SSH from internal only"
  - rule: deny
    port: 22
    proto: tcp
    from_ip: 0.0.0.0/0
    comment: "Block SSH from internet"

# For RedHat/Rocky/Alma systems
firewall_services:
  - service: http
    state: enabled
  - service: https
    state: enabled

firewall_rich_rules:
  - rule: 'rule family="ipv4" source address="10.0.1.0/24" port protocol="tcp" port="3306" accept'
  - rule: 'rule family="ipv4" source address="10.0.1.0/24" port protocol="tcp" port="5432" accept'
  - rule: 'rule family="ipv4" source address="10.0.1.0/24" port protocol="tcp" port="6379" accept'
  - rule: 'rule family="ipv4" source address="10.0.0.0/8" port protocol="tcp" port="22" accept'
  - rule: 'rule family="ipv4" source address="0.0.0.0/0" port protocol="tcp" port="22" reject'
  - rule: 'rule family="ipv4" reject'
```

---

## Verification

### Check firewall status

**Debian/Ubuntu**:
```bash
ufw status verbose
ufw show added
```

**RedHat/Rocky/Alma**:
```bash
firewall-cmd --list-all
firewall-cmd --list-rich-rules
```

### Test connectivity

```bash
# Test SSH
ssh -p 22 user@hostname

# Test HTTP
curl -I http://hostname

# Test custom port
nc -zv hostname 3306
```

---

## Common Troubleshooting

| Issue | Debian/Ubuntu | RedHat |
|-------|---------------|--------|
| Rule not applied | `ufw reload` | `firewall-cmd --reload` |
| Verify rules | `ufw show added` | `firewall-cmd --list-all` |
| Check logs | `/var/log/ufw.log` | `journalctl -u firewalld` |
| Reset firewall | `ufw reset` | `firewalld stop && rm -rf /etc/firewalld/zones/public.xml` |

---

## Best Practices

1. **Always allow SSH first** - Don't lock yourself out
2. **Use CIDR notation** - `192.168.1.0/24` instead of individual IPs
3. **Add comments** - Describe each rule's purpose
4. **Test before production** - Verify connectivity after changes
5. **Deny by default** - Only allow what's needed
6. **Rate limit ICMP** - Prevent DoS attacks (automatic in this role)
7. **Log denied connections** - Helps troubleshooting and security

---

## Upstream Modules & Alternatives

This document outlines upstream Ansible modules and community roles for firewall management.

### Current Implementation

The `firewall.yml` task uses **official upstream Ansible modules**:

| Platform | Module | Collection | Status |
|----------|--------|-----------|--------|
| Debian/Ubuntu | `community.general.ufw` | community.general | Maintained |
| RedHat/Rocky/Alma | `ansible.posix.firewalld` | ansible.posix | Maintained |

These are the official Ansible modules for firewall management, actively maintained by Red Hat and the community.

---

### Upstream Modules (Recommended)

#### 1. community.general.ufw

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

#### 2. ansible.posix.firewalld

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

### Community Roles (Alternative)

#### 1. geerlingguy.firewall

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

#### 2. fngry.ufw

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

#### 3. stackhpc.firewall-config

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

### Comparison Matrix

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

### Recommendation

#### Current Implementation (This Project)

**Why we use raw modules**:
- Direct control over configuration
- No abstraction layer overhead
- Clearer implementation logic
- Works across Debian AND RedHat in one task file
- Maximum flexibility for custom rules

#### If Simplification Needed

**Use `geerlingguy.firewall`** if you want:
- Pre-built role with less configuration
- Jeff Geerling's community reputation
- Simpler variable structure
- Less custom rule management

#### If Advanced Features Needed

**Use `stackhpc.firewall-config`** if you want:
- Template-based rule generation
- nftables optimization
- Complex rule orchestration
- Enterprise-grade features

---

### Module Reference Quick Lookup

#### UFW Module Parameters

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

#### firewalld Module Parameters

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

### Migration Path

If you want to migrate from raw modules to a community role:

#### Option 1: geerlingguy.firewall

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

### Summary

| Approach | Pros | Cons |
|----------|------|------|
| **Raw modules** (current) | Full control, flexible, lightweight | More code, custom maintenance |
| **geerlingguy role** | Simple, well-tested, excellent docs | Less flexible, learning role parameters |
| **stackhpc role** | Advanced features, enterprise-ready | More complex, steeper learning curve |

**Current recommendation**: Keep raw modules for maximum control and cross-platform support in this project.

---

**Last Updated**: November 2025
**Version**: 2.0 (Consolidated)
