# system_hardening_macos Role

**Purpose:** Harden macOS systems according to 2025 best practices (NIST SP 800-219, CIS Benchmarks)

**Target:** macOS 14 (Sonoma) through macOS 26 (Tahoe)

---

## What This Role Does

Implements comprehensive macOS security hardening across multiple layers:

### 1. **Firewall Hardening**
- ✅ Enable Application Firewall (ALF) with stealth mode
- ✅ Configure Packet Filter (PF) with rate limiting and anti-bruteforce
- ✅ Enable logging for both layers

### 2. **SSH Security**
- ✅ Deploy hardened sshd_config with:
  - Post-quantum key exchange (`sntrup761x25519-sha512@openssh.com`)
  - Modern ciphers (ChaCha20-Poly1305, AES-GCM)
  - Secure MACs (HMAC-SHA2 with encrypt-then-MAC)
  - Rate limiting (5 connections per 30 seconds)
  - Disable password authentication
  - Disable root login
  - Disable empty passwords

### 3. **System Integrity**
- ✅ Verify SIP is enabled (non-negotiable for production)
- ✅ Verify Gatekeeper is enforcing code signing
- ✅ Verify XProtect malware protection is active

### 4. **User Access Control**
- ✅ Enforce strong sudo configuration
  - Password required for all sudo commands
  - Session timeout: 5 minutes
  - Log all sudo commands
  - Use `/etc/sudoers.d/` for granular permissions
- ✅ Disable automatic login
- ✅ Disable guest account (if applicable)
- ✅ Hide user list on login window

### 5. **System Monitoring & Logging**
- ✅ Enable OpenBSM audit logging
- ✅ Configure unified logging
- ✅ Set appropriate log retention policies

### 6. **Network Security**
- ✅ Configure DNS security (DoH/DoT)
- ✅ Disable unnecessary services:
  - AirDrop (unless needed)
  - Bluetooth (unless needed)
  - Remote Desktop (unless needed)
  - Printer sharing (unless needed)

### 7. **System Updates**
- ✅ Enable automatic security updates
- ✅ Enable automatic malware definition updates

---

## Role Variables

### **Firewall Settings**
```yaml
# Enable macOS Application Firewall
macos_firewall_enabled: true
macos_firewall_stealth_mode: true
macos_firewall_logging_enabled: true
macos_firewall_block_all_incoming: false  # May break local services

# Enable Packet Filter
macos_pf_enabled: true
macos_pf_rate_limit_ssh: true             # 5 conn / 30 seconds
```

### **SSH Security**
```yaml
# SSH hardening
macos_ssh_hardening_enabled: true
macos_ssh_key_exchange:
  - sntrup761x25519-sha512@openssh.com
  - curve25519-sha256
  - curve25519-sha256@libssh.org
macos_ssh_ciphers:
  - chacha20-poly1305@openssh.com
  - aes256-gcm@openssh.com
  - aes128-gcm@openssh.com
macos_ssh_macs:
  - hmac-sha2-512-etm@openssh.com
  - hmac-sha2-256-etm@openssh.com

# SSH daemon settings
macos_sshd_permit_root_login: "no"
macos_sshd_password_authentication: "no"
macos_sshd_empty_password_login: "no"
macos_sshd_permit_user_environment: "no"
macos_sshd_max_auth_tries: 3
macos_sshd_max_sessions: 5
```

### **System Integrity**
```yaml
# SIP verification (should always be true)
macos_sip_check_enabled: true
macos_sip_required: true  # MUST be true for production

# Gatekeeper enforcement
macos_gatekeeper_enabled: true
```

### **User Access Control**
```yaml
# Sudo configuration
macos_sudo_password_required: true
macos_sudo_timeout_minutes: 5
macos_sudo_logging_enabled: true

# Login security
macos_disable_auto_login: true
macos_hide_user_list_login: true
```

### **Network & Services**
```yaml
# Service disabling
macos_disable_airdrop: true              # Set to false if needed
macos_disable_bluetooth: true            # Set to false if needed
macos_disable_remote_desktop: true
macos_disable_printer_sharing: true

# DNS security
macos_dns_security_enabled: true         # DoH/DoT
macos_dns_servers:                       # Quad9 example
  - 9.9.9.9
  - 149.112.112.112
```

### **System Updates**
```yaml
# Automatic updates
macos_auto_security_updates: true
macos_auto_os_updates: true
macos_auto_check_enabled: true
```

---

## Prerequisites

- ✅ Common role applied first
- ✅ Admin privileges required
- ✅ macOS 14+ (Sonoma or later)
- ✅ System Integrity Protection enabled (non-negotiable)

---

## Task Files

| File | Purpose |
|------|---------|
| `tasks/main.yml` | Orchestration, runs all subtasks |
| `tasks/firewall_alf.yml` | Application Firewall configuration |
| `tasks/firewall_pf.yml` | Packet Filter configuration |
| `tasks/ssh_hardening.yml` | SSH daemon hardening |
| `tasks/system_integrity.yml` | SIP, Gatekeeper, XProtect verification |
| `tasks/user_access.yml` | Sudo, login window, account settings |
| `tasks/network_services.yml` | Service disabling, DNS security |
| `tasks/system_updates.yml` | Automatic update configuration |
| `tasks/logging.yml` | Audit logging and unified logging |

---

## Template Files

| File | Purpose |
|------|---------|
| `templates/sshd_config_macos.j2` | Hardened SSH daemon config |
| `templates/pf_macos.conf.j2` | Hardened Packet Filter rules |
| `templates/sudoers_macos.j2` | Secure sudoers configuration |
| `templates/audit_macos.conf.j2` | OpenBSM audit rules |

---

## Important Caveats

⚠️ **System Integrity Protection (SIP)**
- Must remain enabled on production systems
- Role will fail if SIP is disabled (by design)
- Never disable SIP for infrastructure servers

⚠️ **Firewall Configuration**
- PF configuration may lock you out if misconfigured
- Role includes "allow loopback" to prevent this
- Test on staging before production deployment
- `block-all-incoming` is commented out to avoid service interruption

⚠️ **SSH Hardening**
- Disables password authentication (key-based only)
- Disables root login
- Verify SSH keys are properly configured before running
- Test SSH connectivity immediately after applying

⚠️ **Service Disabling**
- Default disables AirDrop, Bluetooth, Remote Desktop, Printer Sharing
- Adjust variables if your infrastructure needs these services
- Some applications may require re-enabling certain services

---

## Compliance References

This role implements recommendations from:

- **NIST SP 800-219** - macOS Security Compliance Project (official)
- **CIS macOS Benchmarks** (January 2025, Level 1 & 2)
- **Apple Security Hardening Guidelines**
- **DISA macOS STIGs** (where applicable)

---

## Example Playbook

```yaml
---
- name: Harden macOS systems
  hosts: macos_servers
  become: yes
  roles:
    - role: common                      # Apply foundation first
    - role: system_hardening_macos      # Apply hardening
      vars:
        macos_firewall_enabled: true
        macos_sshd_password_authentication: "no"
        macos_disable_airdrop: true
        macos_sudo_timeout_minutes: 5
```

---

## Testing & Validation

After applying, verify:

```bash
# Verify firewall status
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
sudo pfctl -s info

# Verify SIP status
csrutil status

# Verify SSH configuration
sudo sshd -T

# Verify Gatekeeper
spctl --status

# Verify audit logging is enabled
sudo launchctl list com.apple.auditd
```

---

## Support & References

- **Apple Security Documentation**: https://support.apple.com/en-us/security
- **NIST SP 800-219**: https://pages.nist.gov/macos_security/
- **CIS Benchmarks**: https://www.cisecurity.org/cis-benchmarks/
- **macOS Security Compliance Project**: Official NIST guidance

---

## Author Notes

This role is part of the **ansible-infra** framework and follows the hybrid approach:
- Uses macOS-native commands where possible
- Leverages Ansible modules for idempotency
- Maintains compatibility with the common role foundation
- Allows selective hardening via variables

Each setting includes rationale and can be adjusted for specific infrastructure needs.
