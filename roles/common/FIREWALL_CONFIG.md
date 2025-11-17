# Firewall Configuration Guide

Complete firewall setup for Debian/Ubuntu (UFW) and RedHat/Rocky/Alma (firewalld).

---

## Default Configuration

By default, only SSH and ICMP are allowed:
- **SSH**: Port 22 (configurable)
- **ICMP**: Ping (rate-limited to 10/minute)
- **Default Policy**: DROP incoming, ACCEPT outgoing

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

## Verification Commands

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

**Last Updated**: November 17, 2025
