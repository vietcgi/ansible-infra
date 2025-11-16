# system_hardening_macos - Quick Start Guide

**Status**: Production-ready macOS security hardening role

---

## What This Does (60 Second Summary)

Hardens macOS systems to 2025 best practices:
- ✅ Firewall: Application Firewall + Packet Filter with SSH rate limiting
- ✅ SSH: Post-quantum algorithms + strong ciphers + key-based auth only
- ✅ System Integrity: Verifies SIP, Gatekeeper, XProtect are enabled
- ✅ Access Control: Hardened sudo, no auto-login, hidden user list
- ✅ Network: Disables unnecessary services, configures secure DNS
- ✅ Logging: OpenBSM audit logging + unified logging
- ✅ Updates: Automatic security and OS updates

---

## Basic Usage

### 1. Apply to All macOS Servers
```yaml
---
- name: Harden macOS systems
  hosts: macos_servers
  become: yes
  roles:
    - role: common                      # Apply foundation first
    - role: system_hardening_macos      # Then apply hardening
```

### 2. Apply with Custom Settings
```yaml
---
- name: Harden macOS with custom DNS
  hosts: macos_servers
  become: yes
  roles:
    - role: common
    - role: system_hardening_macos
      vars:
        macos_firewall_enabled: true
        macos_firewall_stealth_mode: true
        macos_dns_servers:
          - 8.8.8.8              # Google DNS example
          - 8.8.4.4
        macos_sshd_password_authentication: "no"
        macos_disable_airdrop: true
```

---

## Configuration Options

### Most Important Settings

```yaml
# Firewall (required for security)
macos_firewall_enabled: true              # Enable Application Firewall
macos_pf_enabled: true                    # Enable Packet Filter
macos_pf_rate_limit_ssh: true             # SSH anti-bruteforce

# SSH (key-based auth only)
macos_ssh_hardening_enabled: true         # Apply hardening
macos_sshd_password_authentication: "no"  # Disable password auth
macos_sshd_permit_root_login: "no"        # Disable root login

# System Integrity (non-negotiable)
macos_sip_required: true                  # MUST be true for production
macos_gatekeeper_enabled: true            # Enforce code signing
```

### Services to Disable (adjust for your needs)

```yaml
# Default: All disabled
macos_disable_airdrop: true
macos_disable_bluetooth: true
macos_disable_remote_desktop: true
macos_disable_printer_sharing: true
macos_disable_file_sharing: true
macos_disable_remote_apple_events: true

# Override if needed:
# macos_disable_airdrop: false             # Keep AirDrop enabled
# macos_disable_bluetooth: false           # Keep Bluetooth enabled
```

### User Access

```yaml
# Sudo configuration
macos_sudo_timeout_minutes: 5             # Session timeout
macos_sudo_password_required: true        # Require password
macos_sudo_logging_enabled: true          # Log commands

# Login security
macos_disable_auto_login: true            # No auto-login
macos_hide_user_list_login: true          # Hide users on login screen
```

---

## Pre-Deployment Checklist

- [ ] Verify SSH keys are configured on all target systems
- [ ] Ensure admin user has sudo access
- [ ] Test SSH connectivity BEFORE applying (will restart SSH daemon)
- [ ] Review variable overrides for your infrastructure
- [ ] Test on staging first, then production
- [ ] Verify System Integrity Protection is enabled: `csrutil status`

---

## Apply the Role

### 1. Create Playbook
```bash
cat > harden-macs.yml << 'EOF'
---
- name: Harden macOS infrastructure
  hosts: macos_servers
  become: yes
  roles:
    - role: common
    - role: system_hardening_macos
EOF
```

### 2. Test Connectivity
```bash
ansible all -i inventory.yml -m ping
```

### 3. Run Playbook
```bash
ansible-playbook harden-macs.yml -i inventory.yml
```

### 4. Verify
```bash
# After playbook completes, test SSH
ssh -v user@macos-server

# Check firewall
ssh user@macos-server 'sudo pfctl -s info'

# Verify SSH config
ssh user@macos-server 'sudo sshd -T | head -20'
```

---

## What to Expect

### During Execution
- SSH daemon may briefly disconnect (expected during restart)
- Firewall will be activated (may affect local services)
- Network configuration may change (DNS update)
- Login experience changes (hidden users, no auto-login)

### After Completion
- SSH requires key-based authentication only
- Sudo requires password (30-minute timeout)
- Automatic security updates enabled
- System logs to OpenBSM audit daemon
- Packet Filter prevents SSH bruteforce attacks

---

## Troubleshooting

### Lost SSH Access
If you lose SSH access:
1. Console into the Mac
2. Check PF rules: `sudo pfctl -s rules`
3. View blocked IPs: `sudo pfctl -t bruteforce -T show`
4. Restart PF: `sudo pfctl -f /etc/pf.conf`

### SSH Not Starting
If SSH daemon won't start:
```bash
# Check daemon status
launchctl list | grep ssh

# Check sshd configuration
sudo sshd -T

# Test syntax
sudo sshd -t

# Restore backup if needed
sudo cp /etc/ssh/sshd_config.backup.* /etc/ssh/sshd_config
sudo launchctl stop com.openssh.sshd
sudo launchctl start com.openssh.sshd
```

### Firewall Issues
If local services don't work:
```bash
# View current PF rules
sudo pfctl -s rules

# Temporarily disable PF
sudo pfctl -d

# Check blocked connections
sudo pfctl -t bruteforce -T show
```

### Verify System Integrity
```bash
# Check SIP (must be enabled)
csrutil status

# Check Gatekeeper
spctl --status

# Check XProtect
launchctl list | grep xprotect
```

---

## Example Inventory

```yaml
# inventory.yml
all:
  children:
    macos_servers:
      hosts:
        mac1.example.com:
          ansible_host: 10.0.1.10
          ansible_user: admin
          ansible_become_method: sudo
        mac2.example.com:
          ansible_host: 10.0.1.11
          ansible_user: admin
          ansible_become_method: sudo
```

---

## Compliance & References

This role implements:
- **NIST SP 800-219** (macOS Security Compliance Project)
- **CIS macOS Benchmarks** (January 2025)
- **Apple Security Hardening Guidelines**

---

## Getting Help

1. Check role README: `roles/system_hardening_macos/README.md`
2. Review task files: `roles/system_hardening_macos/tasks/`
3. Check Ansible logs: `ansible-playbook -vvv harden-macs.yml`
4. Verify system state: Manual commands in verification section above

---

## Next Steps

After hardening macOS systems:
1. ✅ Deploy `macos_monitoring` role (Node Exporter + Prometheus)
2. ✅ Deploy `app_health_check` role (Blackbox Exporter for health checks)
3. ✅ Setup Grafana dashboards for monitoring
4. ✅ Configure Alertmanager for notifications

See `../../docs/ARCHITECTURE.md` for complete framework architecture and deployment patterns.
