# Centralized User Management System

## Overview

This infrastructure implements a **single source of truth** for user access control across all systems:

```
┌─────────────────────────────────────────────────────────┐
│         inventories/*/group_vars/users.yml              │
│              (SINGLE SOURCE OF TRUTH)                   │
│                                                         │
│   managed_users:                                        │
│     admin:                                              │
│       system:  {shell, groups, home}                   │
│       auth0:   {email, name, password}                 │
│       rbac:    {roles, permissions, policies}          │
│                                                         │
│     support:                                            │
│       system:  {shell, groups, home}                   │
│       auth0:   {email, name, password}                 │
│       rbac:    {roles, permissions, policies}          │
│                                                         │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
   ┌─────────┐ ┌──────────┐ ┌──────────────┐
   │  LINUX  │ │  Auth0   │ │ Application  │
   │  (SSH)  │ │          │ │   (RBAC)     │
   └─────────┘ └──────────┘ └──────────────┘
```

## How It Works

### 1. Define User Once (users.yml)

```yaml
managed_users:
  admin:
    # Linux/SSH Configuration
    system:
      shell: "/bin/bash"
      groups: ["sudo"]
      home: "/home/admin"
      manage_ssh_key: true

    # Auth0 Cloud Configuration
    auth0:
      email: "admin@vietcgi.us"
      given_name: "Admin"
      family_name: "User"
      password: "{{ vault_initial_admin_password }}"
      email_verified: true

    # Role-Based Access Control
    rbac:
      auth0_roles: ["admin"]
      sudo_access: true
      can_deploy: true
      can_manage_users: true
```

### 2. Reference in All Systems (all.yml)

**SSH Users** - from common role:
```yaml
common_users:
  - name: "admin"
    shell: "{{ managed_users.admin.system.shell }}"
    groups: "{{ managed_users.admin.system.groups }}"
```

**Auth0 Users** - from auth0 role:
```yaml
auth0_users:
  - email: "{{ managed_users.admin.auth0.email }}"
    username: "admin"
    given_name: "{{ managed_users.admin.auth0.given_name }}"
    family_name: "{{ managed_users.admin.auth0.family_name }}"
    password: "{{ managed_users.admin.auth0.password }}"
```

### 3. Single Identity Across Systems

Same user everywhere:
```
┌─────────────────────────────────────────────────────┐
│ admin (username: admin)                             │
│                                                     │
│ ✓ SSH Login                                         │
│   ssh admin@server.example.com                      │
│   (uses SSH key from managed_users.admin.ssh_keys)  │
│                                                     │
│ ✓ Application Login                                 │
│   Email: admin@vietcgi.us                          │
│   Username: admin                                   │
│   Password: {{ vault_initial_admin_password }}      │
│                                                     │
│ ✓ Roles & Permissions                              │
│   Auth0 roles: ["admin"]                           │
│   RBAC access: Full system access                  │
│   Sudo: Yes                                         │
│   Deployments: Yes                                  │
│   User management: Yes                              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Benefits

### ✓ Single Source of Truth
- Define user once, deploy everywhere
- No duplicate user definitions
- Reduce copy-paste errors

### ✓ Consistency
- Same user ID across all systems
- Email matches SSH username
- Password synced automatically

### ✓ Scalability
- Easy to add new users (1 place)
- Easy to modify permissions (1 place)
- Easy to remove users (1 place)

### ✓ Audit Trail
- All changes tracked in git
- Full user lifecycle history
- Access policies documented

### ✓ Security
- Centralized role management
- Consistent RBAC across systems
- Password rotation tracking
- SSH key rotation policies

## Adding a New User

### Step 1: Add to users.yml

```yaml
managed_users:
  developer:
    system:
      shell: "/bin/bash"
      groups: ["developers"]
      home: "/home/developer"
      manage_ssh_key: true

    auth0:
      email: "developer@vietcgi.us"
      given_name: "Dev"
      family_name: "Loper"
      password: "{{ vault_developer_password }}"
      email_verified: true

    rbac:
      auth0_roles: ["user"]
      sudo_access: false
      can_deploy: true
      can_manage_users: false
```

### Step 2: Update all.yml references

Add to common_users:
```yaml
common_users:
  - name: "developer"
    shell: "{{ managed_users.developer.system.shell }}"
    groups: "{{ managed_users.developer.system.groups }}"
```

Add to auth0_users:
```yaml
auth0_users:
  - email: "{{ managed_users.developer.auth0.email }}"
    username: "developer"
    given_name: "{{ managed_users.developer.auth0.given_name }}"
    family_name: "{{ managed_users.developer.auth0.family_name }}"
    password: "{{ managed_users.developer.auth0.password }}"
    email_verified: "{{ managed_users.developer.auth0.email_verified }}"
```

### Step 3: Run Playbook

```bash
ansible-playbook playbooks/client_onboarding.yml -i inventories/projects/vietcgi/hosts.yml
```

The new user will be:
- Created as a system user (SSH access)
- Registered in Auth0 (app login)
- Assigned roles and permissions (RBAC)

## Removing a User

### Step 1: Remove from users.yml

Delete the user entry from managed_users

### Step 2: Remove references from all.yml

Delete from common_users and auth0_users lists

### Step 3: Run Playbook

The user will be:
- Removed from system (SSH access revoked)
- Deactivated in Auth0 (app login blocked)
- Permissions revoked

## Access Policies

### SSH Access Policy
```yaml
access_policies:
  ssh:
    enabled: true
    key_based_only: true          # No password auth
    port: 22
    max_retries: 3
    timeout_minutes: 30
    require_mfa: false            # Future enhancement
```

### Auth0 Access Policy
```yaml
access_policies:
  auth0:
    enabled: true
    mfa_required: true
    password_min_length: 12
    password_policy: "good"
    session_timeout_hours: 8
    require_email_verification: true
```

### Application Access Policy
```yaml
access_policies:
  application:
    api_rate_limit: 1000          # Requests per hour
    session_timeout_minutes: 60
    require_https: true
    require_secure_cookies: true
```

## Role-Based Access Control (RBAC)

### Role Hierarchy

```
Admin
  ├─ Full system access
  ├─ User management
  ├─ Application deployment
  └─ Audit logs access

Manager
  ├─ Team management
  ├─ Read-only system access
  ├─ Limited deployments
  └─ Report generation

User
  ├─ Basic features
  ├─ Personal data access
  └─ Standard permissions

Viewer
  ├─ Read-only access
  ├─ Report access
  └─ No modifications allowed
```

### Permission Mapping

Each role gets permissions in three areas:

**SSH Permissions**
```
admin:    ALL
manager:  LIMITED
user:     NONE
viewer:   NONE
```

**Auth0 Permissions**
```
admin:    read:users, create:users, update:users, delete:users, manage:roles
manager:  read:users, update:users
user:     read:profile
viewer:   read:profile
```

**Application Permissions**
```
admin:    admin_panel, user_management, system_settings, audit_logs
manager:  team_management, reports, resource_allocation
user:     basic_features, personal_data
viewer:   read_only, reports
```

## Audit & Monitoring

### What Gets Logged

```yaml
audit_config:
  enabled: true
  log_all_logins: true          # Every login recorded
  log_all_changes: true         # Every permission change
  log_retention_days: 90        # 3 months retention
  alert_on_failed_attempts: true
  failed_attempts_threshold: 5  # Alert after 5 failures
```

### Viewing Audit Logs

SSH access attempts are logged by auditd:
```bash
# On server:
sudo ausearch -m auth | grep "user=admin"
```

Auth0 logs are available in dashboard:
```
https://manage.auth0.com/dashboard → Logs
```

## Security Best Practices

### 1. Password Management
- Store passwords in Ansible Vault
- Use strong password policies
- Rotate passwords every 90 days

### 2. SSH Key Rotation
- Rotate SSH keys every 90 days
- Track key fingerprints in users.yml
- Immediately revoke compromised keys

### 3. MFA Enforcement
- Require MFA for Auth0 logins
- Implement SSH MFA (future)
- Audit all authentication methods

### 4. Access Review
- Quarterly access reviews
- Remove unused accounts
- Update role assignments

### 5. Audit Logging
- Enable full audit logging
- 90+ day retention
- Alert on suspicious activity

## Integration Points

### With Ansible Roles

**Common Role** (OS baseline)
```yaml
# Uses: managed_users for SSH users
# Creates: System users, groups, home directories
# Manages: SSH keys, shell configuration
```

**Auth0 Role** (Identity)
```yaml
# Uses: managed_users for Auth0 users
# Creates: Auth0 users, roles, permissions
# Manages: MFA, password policies, connections
```

**App Integration Role** (Applications)
```yaml
# Uses: managed_users RBAC for permission grants
# Creates: Application-level access controls
# Manages: API rate limiting, session timeouts
```

## Troubleshooting

### User Not Syncing

**Problem:** User exists in users.yml but not in Auth0

**Solution:**
1. Check if all.yml has auth0_users reference
2. Verify managed_users variable is accessible
3. Run: `ansible all -m debug -a "var=managed_users"`
4. Check Auth0 role logs for errors

### Permission Mismatch

**Problem:** User has different permissions in SSH vs Auth0

**Solution:**
1. Edit users.yml to ensure rbac section is complete
2. Verify all.yml references auth0_roles correctly
3. Update group_vars as needed
4. Re-run playbook with `-v` for verbose output

### SSH Key Not Working

**Problem:** User can't SSH despite being created

**Solution:**
1. Verify managed_users.USER.system.manage_ssh_key = true
2. Check SSH key exists in manage_users.USER.ssh_keys
3. Verify key is in ~/.ssh/authorized_keys on server
4. Test: `ssh -v user@server` to debug

## Future Enhancements

- [ ] SSH key auto-rotation
- [ ] LDAP/Active Directory sync
- [ ] Automated user provisioning/deprovisioning
- [ ] Real-time audit webhooks
- [ ] Okta/Azure AD integration
- [ ] SSH MFA enforcement
- [ ] API-based user management
- [ ] Self-service password reset
