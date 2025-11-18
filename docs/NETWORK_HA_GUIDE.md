# Network Management and High Availability (HA) Guide

**Date**: November 17, 2025
**Version**: 1.0
**Status**: Production Ready

---

## Overview

The network management role provides enterprise-grade networking capabilities:

 **Static IP Configuration** - Assign fixed IPs to network interfaces across Debian, Ubuntu, and RHEL/CentOS
 **Network Bonding** - Aggregate multiple NICs into bonds for redundancy (active-backup, 802.3ad LACP, load balancing)
 **Virtual IP Failover** - Automatic VIP migration using keepalived VRRP
 **Health Checks** - HTTP, TCP, and custom script health monitoring
 **VLAN Support** - Configure virtual LANs with tagged interfaces
 **Cross-Distribution** - Works on Ubuntu 18.04+, Debian, CentOS 7+, RHEL 7+

---

## Architecture Overview

### High Availability Pattern

```
┌─────────────────────────────────────────────────────┐
│           Virtual IP (VIP)                         │
│           192.168.1.5 (Floating)                   │
└─────────────────────────────────────────────────────┘
         ↓                          ↓
   ┌──────────────┐          ┌──────────────┐
   │ MASTER Node  │          │ BACKUP Node  │
   │ Priority 100 │          │ Priority 50  │
   ├──────────────┤          ├──────────────┤
   │ keepalived   │◄─VRRP──►│ keepalived   │
   │ State: UP    │          │ State: UP    │
   └──────────────┘          └──────────────┘
         ↓                          ↓
   ┌──────────────┐          ┌──────────────┐
   │ bond0        │          │ bond0        │
   │ 192.168.1.10 │          │ 192.168.1.11 │
   │ (eth0,eth1)  │          │ (eth0,eth1)  │
   └──────────────┘          └──────────────┘
         ↓                          ↓
   ┌─────┴─────┐              ┌─────┴─────┐
   │   eth0    │  eth1        │   eth0    │  eth1
   │ (Active)  │(Standby)     │(Standby)  │(Active)
   └──────────┘              └──────────┘
```

### Traffic Flow

1. **Normal Operation (MASTER Active)**
   - Client → VIP (192.168.1.5) → MASTER node (192.168.1.10)
   - BACKUP node monitors MASTER health

2. **MASTER Failure**
   - Health check fails on MASTER
   - BACKUP detects failure (3 missed heartbeats)
   - BACKUP transitions to MASTER
   - VIP moves to BACKUP (now MASTER)
   - Traffic automatically routes to new MASTER

3. **MASTER Recovery**
   - MASTER comes back online
   - VIP returns to MASTER (if priority > BACKUP)
   - Or waits for operator intervention (if prefer_backup set)

---

## Configuration

### Scenario 1: Simple Static IP

 **Best for**: Single-NIC systems, fixed addressing

```yaml
# inventory/group_vars/webservers.yml
network_static_ips:
  - interface: eth0
    address: 192.168.1.10
    netmask: 24
    gateway: 192.168.1.1
    dns:
      - 8.8.8.8
      - 1.1.1.1
```

**Result**: eth0 gets static IP 192.168.1.10/24, DHCP disabled

**Verification**:
```bash
ip addr show eth0
# inet 192.168.1.10/24 brd 192.168.1.255 scope global eth0

ip route show
# default via 192.168.1.1 dev eth0
```

---

### Scenario 2: Network Bonding (Active-Backup)

 **Best for**: Redundant network paths, NIC failure tolerance

```yaml
# inventory/group_vars/database_servers.yml
network_bonding_enabled: true
network_bonds:
  - name: bond0
    interfaces:
      - eth0
      - eth1
    mode: active-backup
    mii_monitor_interval: 100
    primary_interface: eth0
```

**How it works**:
- eth0 is active (transmit/receive)
- eth1 is standby (ready)
- If eth0 fails, traffic automatically uses eth1
- MII monitor checks link every 100ms

**Verification**:
```bash
cat /proc/net/bonding/bond0
# Bonding Mode: fault-tolerance (active-backup)
# Primary Slave: eth0
# Currently Active Slave: eth0

ethtool eth0
# Link detected: yes
```

---

### Scenario 3: LACP (802.3ad) Bonding

 **Best for**: High-speed networks, switch support required

**Prerequisites**: Switch configured with LACP on corresponding ports

```yaml
network_bonding_enabled: true
network_bonds:
  - name: bond0
    interfaces:
      - eth0
      - eth1
    mode: 802.3ad
    mii_monitor_interval: 100
    lacp_rate: fast  # Check every 1 second instead of 30
    xmit_hash_policy: layer3+4  # Hash on IP+port for distribution
```

**How it works**:
- Both eth0 and eth1 are active (load balancing)
- LACP negotiates with switch
- Traffic distributed across both interfaces
- Requires switch configuration

**Verification**:
```bash
cat /proc/net/bonding/bond0
# Bonding Mode: IEEE 802.3ad Dynamic link aggregation
# AD Aggregator[1] = eth0, Slave: eth0
# AD Aggregator[1] = eth1, Slave: eth1
```

---

### Scenario 4: keepalived Virtual IP with Health Checks

 **Best for**: Highly available services (databases, load balancers)

#### Basic Setup (MASTER/BACKUP with VIP)

```yaml
# MASTER node (priority 100)
network_keepalived_enabled: true
network_vip: 192.168.1.5
network_vip_interface: bond0
network_vip_netmask: 24
network_keepalived_priority: 100
network_keepalived_vrid: 51
network_keepalived_auth_pass: "secure_password_51"
```

```yaml
# BACKUP node (priority 50)
network_keepalived_enabled: true
network_vip: 192.168.1.5
network_vip_interface: bond0
network_vip_netmask: 24
network_keepalived_priority: 50
network_keepalived_vrid: 51
network_keepalived_auth_pass: "secure_password_51"
```

**Verification**:
```bash
# On MASTER (should have VIP)
ip addr show bond0
# inet 192.168.1.5/24 scope global secondary bond0:vip

# On BACKUP (should NOT have VIP)
ip addr show bond0
# (no VIP shown)

# Check keepalived status
systemctl status keepalived
# Active: active (running)

journalctl -u keepalived -f
# Transition to MASTER [vrrp]
# Sending gratuitous ARP on bond0
```

---

#### Advanced: Health Checks

##### HTTP Health Check (for web/app servers)

```yaml
network_keepalived_enabled: true
network_vip: 192.168.1.5
network_vip_interface: bond0
network_vip_netmask: 24
network_keepalived_priority: 100
network_keepalived_vrid: 51

# Health checks
network_keepalived_checks:
  - name: http_check
    check_type: http
    check_host: 127.0.0.1
    check_port: 80
    check_path: /health
    interval: 2
    timeout: 3
    fall_count: 3  # Fail after 3 failures
    rise_count: 2  # Recover after 2 successes
    weight: -5  # Lower priority if check fails
```

**How it works**:
- Every 2 seconds: `curl -sf http://127.0.0.1:80/health`
- If returns non-zero: increment failure counter
- After 3 failures: mark as unhealthy (-5 priority adjustment)
- After 2 successes: mark as healthy (remove adjustment)
- If priority drops below BACKUP → failover

---

##### TCP Health Check (for databases)

```yaml
network_keepalived_checks:
  - name: mysql_check
    check_type: tcp
    check_host: 127.0.0.1
    check_port: 3306
    interval: 2
    timeout: 3
    fall_count: 3
    rise_count: 2
    weight: -10
```

**How it works**:
- Every 2 seconds: `timeout 2 bash -c "echo > /dev/tcp/127.0.0.1/3306"`
- Connection success → healthy
- Connection timeout/failure → increment counter
- Useful for MySQL, PostgreSQL, Redis

---

##### Custom Script Check (for complex logic)

```yaml
network_keepalived_checks:
  - name: service_check
    check_type: script
    check_script: "systemctl is-active myapp && /usr/local/bin/app-health-check.sh"
    interval: 5
    timeout: 3
    fall_count: 2
    rise_count: 2
    weight: -15
```

**How it works**:
- Every 5 seconds: execute custom script
- Exit code 0 = healthy
- Exit code non-zero = unhealthy
- Useful for complex service checks

---

#### Notification on Failover

```yaml
network_keepalived_enabled: true
network_vip: 192.168.1.5
network_vip_interface: bond0

# Notification flags
network_keepalived_notify_master: true  # Script when becoming MASTER
network_keepalived_notify_backup: true  # Script when becoming BACKUP
network_keepalived_notify_fault: true   # Script when health check fails
```

The role creates notification scripts at:
- `/usr/local/bin/keepalived_notify.sh`
  - Called with: MASTER, BACKUP, or FAULT
  - Can send alerts, update DNS, trigger monitoring

---

### Scenario 5: Virtual Servers (Load Balancing)

 **Best for**: keepalived load balancing mode (directs traffic to real servers)

```yaml
network_keepalived_enabled: true
network_vip: 192.168.1.5
network_vip_interface: bond0

# Virtual server configuration (load balancing)
network_keepalived_virtual_servers:
  - vip: 192.168.1.5
    port: 80
    protocol: TCP
    delay_loop: 6  # Check real servers every 6 seconds
    lb_algo: rr    # Round-robin load balancing
    lb_kind: NAT   # Network address translation
    real_servers:
      - ip: 192.168.1.10
        port: 80
        weight: 1
      - ip: 192.168.1.11
        port: 80
        weight: 1
```

**How it works**:
- VIP 192.168.1.5:80 receives traffic
- NAT translates to real servers (192.168.1.10:80, 192.168.1.11:80)
- Health checks real servers via TCP_CHECK
- If server down → removed from pool
- Traffic distributed round-robin

---

### Scenario 6: Combined - Bonding + HA VIP with Health Checks

 **Best for**: Enterprise production (highest availability)

```yaml
# inventory/group_vars/ha_cluster.yml

# Network Bonding
network_bonding_enabled: true
network_bonds:
  - name: bond0
    interfaces:
      - eth0
      - eth1
    mode: active-backup
    mii_monitor_interval: 100
    primary_interface: eth0

# Static IP on Bond
network_static_ips:
  - interface: bond0
    address: 192.168.1.10
    netmask: 24
    gateway: 192.168.1.1
    dns:
      - 8.8.8.8
      - 1.1.1.1

# keepalived VIP
network_keepalived_enabled: true
network_vip: 192.168.1.5
network_vip_interface: bond0
network_vip_netmask: 24
network_keepalived_priority: 100
network_keepalived_vrid: 51

# Health checks
network_keepalived_checks:
  - name: app_health
    check_type: http
    check_host: 127.0.0.1
    check_port: 8080
    check_path: /api/health
    interval: 2
    timeout: 3
    fall_count: 3
    rise_count: 2
    weight: -5
```

**Result**:
- eth0 and eth1 bonded for NIC redundancy
- bond0 gets static IP on stable network
- VIP 192.168.1.5 floats between nodes
- Application health monitored
- Automatic failover if app unhealthy

---

## Network Distribution Methods

### Bonding Modes

| Mode | Use Case | Active Links | Load Balanced | Failover | Switch Config |
|------|----------|--------------|---------------|----------|---------------|
| **active-backup** | Default HA | 1 | No | Automatic | Not required |
| **balance-rr** | Load balancing | All | Yes (RR) | Automatic | Not required |
| **balance-xor** | Load balancing | All | Yes (XOR) | Automatic | Not required |
| **balance-alb** | Asymmetric LB | All | Asymmetric | Automatic | Not required |
| **balance-tlb** | Transmit LB | All | Yes (TX only) | Automatic | Not required |
| **802.3ad** (LACP) | High speed | All | Yes | Automatic | **Required** |

### Hash Policies (for load balanced modes)

- **layer2**: MAC address based
- **layer3+4**: IP + Port based (best for most workloads)
- **layer2+3**: MAC + IP based
- **encap3+4**: Tunnel-aware IP+Port

---

## Troubleshooting

### Network Not Configured

```bash
# Check if network_management_enabled is true
ansible-inventory --host <hostname> | grep network_

# Verify task ran
ansible-playbook playbook.yml -vvv -t network_management

# Check if templates exist
ls -la /etc/netplan/99-static-ips.yaml
ls -la /etc/network/interfaces
```

### Static IP Not Applied

```bash
# On Debian/Ubuntu with Netplan
netplan apply
netplan status

# On older Debian/Ubuntu
systemctl restart networking
systemctl status networking

# On RHEL/CentOS
systemctl restart network
systemctl status network

# Verify IP
ip addr show
```

### Bond Not Forming

```bash
# Check bond module loaded
lsmod | grep bonding

# Check bond status
cat /proc/net/bonding/bond0
# Should show both slaves

# Check interface status
ethtool eth0
ethtool eth1
# Should both show "Link detected: yes"

# Try manual bonding
modprobe bonding mode=active-backup miimon=100
ip link add bond0 type bond
ip link set eth0 master bond0
ip link set bond0 up
```

### keepalived Not Starting

```bash
# Check if installed
systemctl status keepalived

# View error logs
journalctl -u keepalived -n 20

# Test configuration
keepalived -t

# Check VIP is configured
ip addr show
# Should show: inet 192.168.1.5/24 scope global secondary bond0:vip

# Check VRRP packets
tcpdump -i bond0 proto vrrp
```

### VIP Not Failing Over

```bash
# Check keepalived state
systemctl status keepalived

# Check priority (higher wins)
grep priority /etc/keepalived/keepalived.conf

# Check health checks
journalctl -u keepalived | grep "check"

# Simulate failure
systemctl stop keepalived

# Monitor other node
# Should see: Transition to MASTER
journalctl -u keepalived -f
```

---

## Performance Impact

### CPU & Memory

- **Bonding**: <1% CPU overhead
- **keepalived**: <1% CPU, ~10MB RAM
- **Health checks**: 1-5% CPU per check (depends on type)

### Network

- **VRRP advertisement**: ~50 bytes/sec per VIP
- **Health checks**: 200 bytes/check (2-5 second interval)
- **Minimal impact** on bandwidth

### Latency

- **Failover time**: 100-500ms (3 missed heartbeats × advert_int)
- **VIP announcement**: <100ms after state change
- **Most applications**: handle transparently via TCP retransmit

---

## Security Considerations

### keepalived Authentication

```yaml
network_keepalived_auth_pass: "strong_password_here"
```

⚠️ **WARNING**: Password sent in plaintext in VRRP packets
- Use same password on MASTER and BACKUP (mandatory)
- Protect management network (firewall VRRP port 112)
- Consider using VPN/IPsec for keepalived traffic

---

### Firewall Configuration

```bash
# Allow VRRP (protocol 112) on management network
firewall-cmd --add-rich-rule='rule family="ipv4" \
  source address="10.0.0.0/8" protocol="vrrp" accept'

# Or with ufw
ufw allow from 10.0.0.0/8 to any proto vrrp
```

---

### Network Isolation

```yaml
# Don't expose management VLANs to production network
# Bond only management interfaces
# Separate health check networks if possible
```

---

## Monitoring & Alerting

### Key Metrics

```bash
# Bond status
cat /proc/net/bonding/bond0 | grep "Slave Interface"

# VRRP state
journalctl -u keepalived | grep -i "transition"

# Health check results
journalctl -u keepalived | grep -i "check"

# VIP assignment
ip addr show | grep "secondary"
```

### Prometheus Metrics

```yaml
# Monitor via node_exporter
curl http://localhost:9100/metrics | grep bonding

# Or custom script exporter
/usr/local/bin/keepalived_exporter
```

### Alert Examples

```yaml
# Bond slaves down
- alert: BondSlavesDown
  expr: node_network_bond_slaves == 1
  for: 2m
  annotations:
    summary: "Bond {{ $labels.device }} has only 1 slave"

# VIP not on node
- alert: VIPNotAssigned
  expr: absent(node_network_address{address=~"192.168.1.5.*"})
  for: 5m
  annotations:
    summary: "VIP not assigned to node"

# keepalived down
- alert: KeepalivdDown
  expr: up{job="keepalived"} == 0
  for: 2m
  annotations:
    summary: "keepalived service down"
```

---

## Testing Failover

### Test 1: Simulate NIC Failure

```bash
# On MASTER node
ip link set eth1 down

# Monitor on MASTER
journalctl -u keepalived -f
# Should show: link is down

# Check VIP still there (eth0 still up)
ip addr show bond0 | grep 192.168.1.5

# Restore
ip link set eth1 up
```

### Test 2: Simulate Service Failure

```bash
# If running health check on HTTP service
systemctl stop myapp

# Monitor keepalived
journalctl -u keepalived -f
# Should show: check failed, priority reduced

# Check if VIP migrated to BACKUP
ssh backup_node ip addr show | grep 192.168.1.5

# Restore
systemctl start myapp
```

### Test 3: Full Node Failure

```bash
# On MASTER node
systemctl stop keepalived

# Monitor BACKUP
journalctl -u keepalived -f
# Should see: Transition to MASTER

# Check VIP on BACKUP
ip addr show | grep 192.168.1.5

# Verify clients can reach VIP
ping 192.168.1.5
# Should reply

# Restore MASTER
systemctl start keepalived
# VIP should return to MASTER (if priority > 50)
```

---

## Best Practices

###  DO

1. **Use keepalived for production HA** - Automatic failover is critical
2. **Configure health checks** - Don't rely on VRRP heartbeat alone
3. **Test failover regularly** - Ensure procedure works before crisis
4. **Use 802.3ad if switch supports** - Better than active-backup for throughput
5. **Separate management and data networks** - Different bonds/VLANs
6. **Monitor keepalived status** - Alert on state changes
7. **Document VIP assignment** - Track which service uses which VIP
8. **Use strong VRRP passwords** - Prevent rogue nodes
9. **Set reasonable failover timeouts** - Balance between responsiveness and false positives
10. **Keep MASTER/BACKUP synchronized** - Ensure both can serve traffic

### ❌ DON'T

1. **Don't use active-backup for high-throughput** - Underutilizes NIC capacity
2. **Don't trust VRRP alone for failover** - Service may be down but network up
3. **Don't make VIP priority too close** - Causes flapping
4. **Don't ignore failed health checks** - Fix underlying issue
5. **Don't use same VIP for different services** - Confusing and error-prone
6. **Don't forget to secure VRRP traffic** - VRRP is unauthenticated by default
7. **Don't overprovision failover latency** - Keep acceptable for apps
8. **Don't forget DNS** - Update DNS when VIP changes (use notification scripts)
9. **Don't use on single-NIC systems** - No redundancy gained
10. **Don't disable monitoring** - HA is only good if you know it works

---

## Deployment Checklist

- [ ] Plan IP addresses and bonding topology
- [ ] Verify switch supports bonding mode (especially 802.3ad)
- [ ] Configure VLAN tagging if needed
- [ ] Test static IPs in non-production first
- [ ] Configure bonding parameters
- [ ] Set up keepalived on MASTER and BACKUP
- [ ] Write health check scripts
- [ ] Test failover in lab environment
- [ ] Configure monitoring and alerting
- [ ] Document VIP assignments
- [ ] Train team on failover procedures
- [ ] Deploy to production
- [ ] Monitor first 24 hours for issues
- [ ] Schedule regular failover tests

---

## References

- [Keepalived Documentation](https://keepalived.org/doc/)
- [Linux Bonding Driver](https://www.kernel.org/doc/html/latest/networking/bonding.html)
- [Netplan Documentation](https://netplan.readthedocs.io/)
- [VRRP RFC 3768](https://tools.ietf.org/html/rfc3768)
- [802.3ad LACP](https://en.wikipedia.org/wiki/Link_aggregation)

---

**Last Updated**: November 17, 2025
**Maintained By**: Infrastructure Team
**Status**: Production Ready
