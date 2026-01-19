# pfSense WireGuard Testing Environment

Local testing environment for the `pfsense_wireguard` Ansible role.

## Prerequisites

- VirtualBox 7.x
- Vagrant 2.x
- pfSense CE ISO ([download](https://www.pfsense.org/download/))
- Ansible with pfsensible.core collection

## Quick Start

### 1. Set Up Network

```bash
make setup-network
```

This creates a VirtualBox host-only network at `192.168.56.0/24`.

### 2. Create pfSense VM

```bash
# Set path to your pfSense ISO
export PFSENSE_ISO=~/Downloads/pfSense-CE-2.7.2-RELEASE-amd64.iso

make create-vm
```

### 3. Install pfSense

Start the VM and complete installation:

```bash
VBoxManage startvm pfsense-test
```

During installation:
1. Accept defaults for most options
2. **WAN Interface**: `em0` (NAT)
3. **LAN Interface**: `em1` (host-only)
4. After install, configure LAN IP: `192.168.56.10/24`

### 4. Enable SSH

In pfSense web UI (`https://192.168.56.10`):
1. System > Advanced > Admin Access
2. Enable SSH
3. Set SSH port to 22

### 5. Test SSH

```bash
make ssh-pfsense
# Password: pfsense (default)
```

### 6. Start Test Client

```bash
vagrant up client
```

### 7. Run Ansible Playbook

First, configure your WireGuard provider credentials:

```bash
# Edit the test vars file
vim ../../inventories/pfsense/group_vars/pfsense/wireguard.yml
```

Then run:

```bash
make ansible-test
```

## Network Topology

```
┌─────────────────────────────────────────────────────────────┐
│  Host Machine                                               │
│  192.168.56.1 (vboxnet0)                                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
         ┌────────┴────────┐
         │  Host-Only Net  │
         │  192.168.56.0/24│
         └────────┬────────┘
                  │
     ┌────────────┴────────────┐
     │                         │
┌────┴─────┐             ┌─────┴────┐
│ pfSense  │             │  Client  │
│ LAN:     │             │          │
│ .56.10   │─────────────│  .0.100  │
│          │  10.0.0.0/24│          │
│ WAN: NAT │             │          │
└──────────┘             └──────────┘
     │
     │ NAT (VirtualBox)
     ▼
   Internet
```

## Test Commands

```bash
# Check connectivity
make test

# SSH to pfSense
make ssh-pfsense

# SSH to test client
make ssh-client

# Run Ansible (dry-run)
make ansible-check

# Run Ansible (apply)
make ansible-test
```

## Verify WireGuard

After running the playbook:

### On pfSense

```bash
# Check WireGuard status
/usr/local/bin/wg show

# Check tunnel interface
ifconfig tun_wg0
```

### On Test Client

```bash
# Check public IP (should be VPN IP)
curl https://api.ipify.org

# Check routing
ip route
```

## Troubleshooting

### SSH Connection Refused
- Ensure SSH is enabled in pfSense
- Check firewall rules allow SSH on LAN

### No Handshake
- Verify endpoint is reachable: `ping <vpn-server>`
- Check keys are correct
- Verify WAN can reach UDP/51820

### Can't Route Traffic
- Check NAT rules are created
- Verify gateway is assigned
- Check interface is enabled

### Slow Performance
- Adjust MTU (try 1380, 1400, 1420)
- Check for packet fragmentation

## Cleanup

```bash
# Stop VMs
make stop

# Destroy everything
make destroy
```
