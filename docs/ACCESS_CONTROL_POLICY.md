# Access Control Policy

## Overview

This document defines role-based access control (RBAC) for ansible-infra infrastructure. It establishes the principle of least privilege while enabling necessary operational flexibility.

---

## Core Principles

1. **Principle of Least Privilege**: Users get minimum permissions needed for their role
2. **Separation of Duties**: Critical operations require multiple approvals
3. **Regular Auditing**: Access reviewed quarterly, revoked when no longer needed
4. **Documented Justification**: All access grants require business justification
5. **Immediate Revocation**: Access removed immediately on role change or departure

---

## Role Definitions

### Infrastructure Administrator (DevOps/SRE)
**Permissions**:
- ✓ Run Ansible playbooks (all environments)
- ✓ Modify roles and playbooks
- ✓ Manage infrastructure (provision/deprovision)
- ✓ Access Vault secrets
- ✓ SSH to all hosts
- ✓ Approve changes (critical role)

**Restrictions**:
- ✗ Cannot modify access control policies
- ✗ Cannot approve their own critical changes
- ✗ Cannot delete backups
- ✗ Cannot modify audit logs

**Users**: [List of current admins]

---

### Senior Engineer / Tech Lead
**Permissions**:
- ✓ Run Ansible playbooks (all environments)
- ✓ Review and approve code changes
- ✓ Approve critical changes
- ✓ Access Vault secrets
- ✓ SSH to production (limited scope)
- ✓ Escalate incidents

**Restrictions**:
- ✗ Cannot modify infrastructure code without review
- ✗ Cannot approve their own changes
- ✗ Cannot modify access control
- ✗ Limited Vault operations (read-only secrets)

**Users**: [List of current leads]

---

### Software Engineer
**Permissions**:
- ✓ Modify roles and playbooks (in dev/staging)
- ✓ SSH to staging/dev environments
- ✓ Read-only Vault access
- ✓ Submit pull requests
- ✓ Run tests locally

**Restrictions**:
- ✗ No production SSH access
- ✗ Cannot approve changes
- ✗ Cannot modify critical roles
- ✗ Cannot access production secrets

**Users**: [List of current engineers]

---

### Operations Support
**Permissions**:
- ✓ Monitor infrastructure (read-only)
- ✓ SSH to hosts (read-only access)
- ✓ Run approved playbooks (limited set)
- ✓ View logs

**Restrictions**:
- ✗ Cannot modify any infrastructure code
- ✗ Cannot make changes without approval
- ✗ No Vault access
- ✗ Limited SSH commands

**Users**: [List of operations staff]

---

### Contractor / Temporary Staff
**Permissions**:
- ✓ Limited to assigned task only
- ✓ Staging environment only
- ✓ Supervised access with lead present
- ✓ Time-limited (expires automatically)

**Restrictions**:
- ✗ No production access
- ✗ No SSH access
- ✗ No Vault access
- ✗ No code modifications

**Users**: [List temporary staff]

**Expires**: [Date]

---

## Environment Access Control

### Development Environment
**Access**: Engineers, DevOps
**No restrictions**: Full access for testing
**Backup**: Not required
**Monitoring**: Basic

### Staging Environment
**Access**: Engineers (limited), Senior Engineers, DevOps, Tech Leads
**Restrictions**: Read-only for some roles
**Backup**: Daily backups maintained
**Monitoring**: Full monitoring, alerts

### Production Environment
**Access**: Senior Engineers, DevOps (with approval)
**Restrictions**: No direct code modifications, changes only via approved process
**Backup**: Hourly backups, offsite replication
**Monitoring**: Real-time monitoring, immediate alerts
**Approval Required**: All changes need approval

---

## SSH Access Control

### Key Management

**Key Lifecycle**:
```
1. Generate (new hire)
2. Distribute securely
3. Store in ~/.ssh/ (0600 permissions)
4. Rotate annually
5. Revoke (departure or compromise)
```

**Key Generation**:
```bash
# Generate new key for user
ssh-keygen -t ed25519 -C "user@example.com" -f ~/.ssh/id_ed25519
# Do NOT use passphrase for Ansible automation
# DO use passphrase for personal access

# Add to server
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@host

# Set correct permissions
chmod 0600 ~/.ssh/id_ed25519
chmod 0644 ~/.ssh/id_ed25519.pub
chmod 0700 ~/.ssh/
chmod 0600 ~/.ssh/authorized_keys
```

### Bastion Host Access

For production, use bastion host:

```
Local System → Bastion Host → Production Host

# Configure SSH config
Host bastion
  HostName bastion.example.com
  User user
  IdentityFile ~/.ssh/id_ed25519

Host prod-*
  ProxyJump bastion
  HostName %h.example.com
  User user
  IdentityFile ~/.ssh/id_ed25519
```

### SSH Access Matrix

| Environment | Role | Access | Via Bastion |
|-------------|------|--------|-------------|
| Dev | Engineers | Full | No |
| Dev | DevOps | Full | No |
| Staging | Engineers | Read-only | No |
| Staging | Senior Engineers | Full | No |
| Staging | DevOps | Full | No |
| Production | DevOps (approval) | Limited | Yes |
| Production | Senior Engineers | Limited | Yes |
| Production | Engineers | None | N/A |

---

## Vault Access Control

### Access Tiers

**Tier 1: Full Access**
- Can read all secrets
- Can write new secrets
- Can rotate keys
- Can delete (with approval)

Users: DevOps team, Security team

```bash
# Grant full access
ansible-vault --vault-id prod@/path/to/password \
  encrypt inventories/production/vault/main.yml
```

**Tier 2: Read Access**
- Can read all secrets
- Cannot modify
- Cannot rotate
- Cannot delete

Users: Senior Engineers, Tech Leads

```bash
# Grant read-only
# Use separate vault ID with limited permissions
vault policy write senior-read - <<EOF
path "secret/data/*" {
  capabilities = ["read", "list"]
}
EOF
```

**Tier 3: Limited Read**
- Can read specific secrets only
- Cannot modify or rotate
- Cannot delete

Users: Application teams, Ops Support

```bash
# Grant access to specific secret
vault policy write app-read - <<EOF
path "secret/data/app/prod" {
  capabilities = ["read"]
}
EOF
```

**Tier 4: No Access**
- Cannot access any secrets
- Use environment variables passed securely

Users: Contractors, Temporary staff

### Secret Rotation

Quarterly minimum:

```bash
#!/bin/bash
# rotate-secrets.sh - Rotate all secrets

ROTATION_DATE=$(date +%Y%m%d)

# 1. Generate new passwords
NEW_DB_PASSWORD=$(openssl rand -base64 32)
NEW_API_KEY=$(openssl rand -hex 32)

# 2. Update vault
ansible-vault encrypt inventories/production/vault/main.yml \
  --vault-id old@/path/to/old \
  --vault-id new@/path/to/new

# 3. Update targets
ansible all -i inventories/production -m shell \
  -a "update-password.sh '$NEW_DB_PASSWORD'"

# 4. Verify access works
ansible all -i inventories/production -m command \
  -a "psql -U user -c 'SELECT version();'"

# 5. Document rotation
echo "Secrets rotated: $ROTATION_DATE" >> /var/log/audit/secret-rotation.log
```

---

## GitHub Repository Access

### Branch Protection

```yaml
# Protect main branch
- Require pull request reviews (minimum 2)
- Require status checks to pass (ansible-lint, tests)
- Require branches to be up to date
- Require review from code owners
- Dismiss stale reviews
- Restrict who can push (admin only)
```

### Code Owner Requirements

Create `.github/CODEOWNERS` file:

```
# Global owners
* @team-lead @devops-lead

# Role-specific owners
roles/common/ @devops-lead @senior-engineer-1
roles/system_hardening_macos/ @macos-specialist
playbooks/provision.yml @devops-lead
playbooks/configure.yml @senior-engineer-1

# Security-critical
SECURITY.md @security-team
roles/*/tasks/ssh_hardening.yml @security-team
inventories/*/vault/ @devops-lead
```

### Pull Request Approval Process

```
Developer: Creates PR → Automated checks run
                          ↓
   Tests pass? → No → Developer fixes
                  ↓ Yes
   Lint passes? → No → Developer fixes
                  ↓ Yes
Peer review requested (2 reviewers)
                ↓
   Concerns? → Yes → Discussion → Resolve
                ↓ No
Code owner review requested
                ↓
   Approved? → Yes → Ready to merge
           ↓ No
   Address concerns → Resubmit for review
```

---

## Audit & Monitoring

### Access Logging

All access logged to `/var/log/ansible-infra/access.log`:

```
2025-11-15T14:23:45 user=alice action=login host=prod-01 status=success
2025-11-15T14:24:12 user=alice action=execute playbook=provision status=success duration=23m
2025-11-15T14:25:30 user=bob action=vault_read path=secrets/db/password status=success
2025-11-15T14:26:15 user=charlie action=ssh host=prod-02 status=failed reason=key_mismatch
```

### Quarterly Access Review

All access reviewed quarterly:

```
ACCESS REVIEW - Q4 2025
=======================

Reviewed by: @security-team
Date: 2025-11-15

Current Access:
- Alice (DevOps): prod_full + staging_full + vault_read ✓
- Bob (Engineer): staging_read + dev_full ✓
- Charlie (Ops): monitoring_read ✓
- David (Contractor): staging_read (expires 2025-12-15) ✓

Access to be revoked:
- Eve (departed 2025-11-01): remove all access ✗

Recommendations:
- Update DevOps team access after latest hire
- Schedule security training for Ops team
```

### Suspicious Activity Alerts

```yaml
# Alert on suspicious access patterns
rules:
  - Failed SSH attempts > 3 in 10 min: page on-call
  - After-hours production access: notify manager
  - Bulk secret reads: investigate immediately
  - Access from unknown IP: require MFA
  - Vault root token used: immediate investigation
```

---

## Multi-Factor Authentication (MFA)

### Required for Production

All users with production access must use MFA:

```
SSH to Bastion:
1. Enter password: [password]
2. Enter MFA code: [TOTP from authenticator]
3. MFA verified - Access granted

Vault Access:
1. Enter Vault ID: [auth method]
2. Verify MFA token: [TOTP]
3. Access granted (24-hour token)
```

### MFA Configuration

```bash
# Configure TOTP for user
# 1. Generate shared secret
openssl rand -hex 20

# 2. Set up authenticator app
qrencode -o mfa-qr.png [shared-secret]

# 3. Verify
oathtool --totp [shared-secret]  # Should match app

# 4. Store backup codes securely
# Keep in password manager, not with key
```

---

## Access Revocation Procedures

### Upon Departure

```
Day of departure:
- [ ] Disable SSH key
- [ ] Revoke Vault access
- [ ] Remove GitHub write access (to read-only if needed)
- [ ] Disable email account
- [ ] Remove from on-call rotation
- [ ] Document in access log

Day 1:
- [ ] Rotate shared secrets they had access to
- [ ] Review audit logs for unusual activity
- [ ] Confirm all access removed

Day 7:
- [ ] Final access audit
- [ ] Archive access records
- [ ] Confirm no residual access
```

### Immediate Revocation (Security Issue)

If user key compromised:

```
Immediate:
- [ ] Revoke SSH key
- [ ] Force logout of all sessions
- [ ] Revoke Vault tokens
- [ ] Notify user of revocation
- [ ] Audit what was accessed

Within 1 hour:
- [ ] Rotate all potentially compromised secrets
- [ ] Generate new SSH key for user
- [ ] Clear cached credentials

Within 24 hours:
- [ ] Security incident report filed
- [ ] Post-mortem scheduled
- [ ] User retraining completed
```

---

## Documentation & Compliance

### Access Control Audit Trail

Maintain for minimum 1 year:

```
audited_access_log.txt:
Date | User | Action | Resource | Result | Approver | Notes
-----|------|--------|----------|--------|----------|------
2025-11-15 | alice | grant_access | production | approved | @lead | Employee hired
2025-11-16 | bob | revoke_access | staging | completed | @lead | Role changed
```

### Compliance Mappings

- **NIST AC-2**: Account Management - Documented here
- **NIST AC-3**: Access Enforcement - Role-based control
- **NIST AU-2**: Audit Events - Logging configured
- **CIS 5.2**: Principle of Least Privilege - Enforced
- **CIS 5.3**: Separation of Duties - Role definitions enforce

---

## Incident Response

### Unauthorized Access Detected

1. **Immediately isolate**
   ```bash
   # Revoke compromised key
   # Remove from authorized_keys
   # Kill active sessions
   pkill -u username
   ```

2. **Investigate**
   ```bash
   # Check what was accessed
   grep "username" /var/log/auth.log
   # Check file modifications
   find / -newer /var/log/access.log.bak
   ```

3. **Notify**
   - Security team
   - Affected user
   - Management

4. **Recover**
   - Rotate secrets accessed
   - Reset credentials
   - Enable MFA for user
   - Consider additional monitoring

---

## Access Request Form

For new or modified access:

```
ACCESS REQUEST FORM
===================

Requestor: [Name]
Date: [Date]
Business Justification: [Why this access needed]

Employee Information:
- Name: [Full name]
- Role: [Job title]
- Department: [Dept]
- Start date: [Date]
- Manager: [Manager name]

Access Requested:
- [ ] Development environment SSH
- [ ] Staging environment SSH
- [ ] Production environment SSH (requires manager approval)
- [ ] Vault read access
- [ ] Vault write access
- [ ] GitHub commit rights
- [ ] Code owner responsibilities
- [ ] Other: [Specify]

Duration: Permanent / Until [Date]

Approvals:
- Manager approval: ___________ (signature/date)
- Security review: ___________ (signature/date)
- Access granted: ___________ (signature/date)
- Date effective: ___________
```

---

## Documentation

**Last Updated**: November 15, 2025
**Version**: 1.0.0
**Status**: Production-Ready
**Next Review**: February 15, 2026

This policy is reviewed annually and updated as roles/responsibilities change.
