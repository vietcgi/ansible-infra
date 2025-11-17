# User Management - Quick Reference

## The Three Layers of User Access

```
┌──────────────────────────────────────────────────────────┐
│ LAYER 1: SSH/Infrastructure Access (Linux Users)         │
│ - Login: ssh username@server.ip                          │
│ - Auth: SSH key-based (no passwords)                     │
│ - Scope: Full server/infrastructure access               │
└──────────────────────────────────────────────────────────┘
                            ↕
┌──────────────────────────────────────────────────────────┐
│ LAYER 2: Application Access (Auth0 Identity)             │
│ - Login: username@domain.auth0.com                       │
│ - Auth: Email/Password (with MFA)                        │
│ - Scope: Web application/cloud services                  │
└──────────────────────────────────────────────────────────┘
                            ↕
┌──────────────────────────────────────────────────────────┐
│ LAYER 3: Feature Access (RBAC - Role-Based)              │
│ - Roles: admin, manager, user, viewer                    │
│ - Permissions: Specific features & data                  │
│ - Scope: What features user can access                   │
└──────────────────────────────────────────────────────────┘

All three are synchronized through: inventories/*/group_vars/users.yml
```

## Add a User in 3 Steps

### Step 1: Edit users.yml
```bash
# inventories/projects/vietcgi/group_vars/users.yml

managed_users:
  newuser:                                    # 1. Username
    system:
      shell: "/bin/bash"
      groups: ["sudo"]
      home: "/home/newuser"
      manage_ssh_key: true

    auth0:
      email: "newuser@vietcgi.us"            # 2. Email
      given_name: "New"
      family_name: "User"
      password: "{{ vault_newuser_password }}"
      email_verified: true

    rbac:
      auth0_roles: ["user"]                   # 3. Role (admin, manager, user, viewer)
      sudo_access: false
      can_deploy: false
      can_manage_users: false
```

### Step 2: Update all.yml
```bash
# inventories/projects/vietcgi/group_vars/all.yml

common_users:
  - name: "newuser"
    shell: "{{ managed_users.newuser.system.shell }}"
    groups: "{{ managed_users.newuser.system.groups }}"

auth0_users:
  - email: "{{ managed_users.newuser.auth0.email }}"
    username: "newuser"
    given_name: "{{ managed_users.newuser.auth0.given_name }}"
    family_name: "{{ managed_users.newuser.auth0.family_name }}"
    password: "{{ managed_users.newuser.auth0.password }}"
    email_verified: "{{ managed_users.newuser.auth0.email_verified }}"
```

### Step 3: Run Playbook
```bash
ansible-playbook playbooks/client_onboarding.yml \
  -i inventories/projects/vietcgi/hosts.yml
```

**Done!** User now has:
- ✓ SSH access as `newuser`
- ✓ Auth0 account `newuser@vietcgi.us`
- ✓ Application role `user`

---

## Modify User Permissions

### Change SSH Access
```yaml
# users.yml
managed_users:
  admin:
    system:
      shell: "/bin/bash"
      groups: ["sudo"]  # Add/remove groups here

    rbac:
      sudo_access: true  # Toggle sudo here
```

### Change Application Role
```yaml
# users.yml
managed_users:
  support:
    rbac:
      auth0_roles: ["manager"]  # Change from ["user"] to ["manager"]
      can_deploy: true          # Grant deployment access
      can_manage_users: false    # Deny user management
```

### Change Auth0 Email/Password
```yaml
# users.yml
managed_users:
  admin:
    auth0:
      email: "newemail@vietcgi.us"
      password: "{{ vault_new_password }}"
```

---

## Remove a User

### Step 1: Delete from users.yml
```bash
# Remove entire user block from managed_users
```

### Step 2: Delete from all.yml
```bash
# Remove user from common_users list
# Remove user from auth0_users list
```

### Step 3: Run Playbook
```bash
ansible-playbook playbooks/client_onboarding.yml \
  -i inventories/projects/vietcgi/hosts.yml
```

**Done!** User is removed from:
- ✓ SSH system
- ✓ Auth0
- ✓ All applications

---

## Current Users

### admin
```
SSH Username:     admin
Auth0 Email:      admin@vietcgi.us
Role:             admin (full access)
SSH Access:       ✓ Yes
Deployments:      ✓ Yes
User Management:  ✓ Yes
```

### support
```
SSH Username:     support
Auth0 Email:      support@vietcgi.us
Role:             manager (team management)
SSH Access:       ✓ Yes
Deployments:      ✗ No
User Management:  ✗ No
```

---

## Access Control Matrix

| Feature | Admin | Manager | User | Viewer |
|---------|-------|---------|------|--------|
| SSH Access | ✓ | ✓ | ✗ | ✗ |
| User Management | ✓ | ✗ | ✗ | ✗ |
| Deploy Applications | ✓ | ✗ | ✗ | ✗ |
| Modify Settings | ✓ | ✗ | ✗ | ✗ |
| View Reports | ✓ | ✓ | ✗ | ✓ |
| Basic Features | ✓ | ✓ | ✓ | ✗ |
| Personal Data | ✓ | ✓ | ✓ | ✗ |
| Read-Only Access | ✓ | ✓ | ✗ | ✓ |

---

## Login Instructions

### SSH (for ops/admin)
```bash
# Login as admin
ssh admin@108.181.38.69 -i ~/.ssh/vietcgi_prod_key

# Login as support
ssh support@108.181.38.69 -i ~/.ssh/vietcgi_prod_key
```

### Application (for end users)
```
1. Visit: https://vietcgi.us
2. Click: "Login with Auth0"
3. Enter: admin@vietcgi.us or support@vietcgi.us
4. Password: (set in vault)
5. MFA: (if enabled)
```

---

## Vault Password Variables

Store these in Ansible Vault:
```bash
vault_initial_admin_password: "VietCGI@Admin2025!Secure"
vault_support_user_password: "VietCGI@Support2025!Secure"
vault_newuser_password: "NewUser@Password2025!"
```

Encrypt vault file:
```bash
ansible-vault encrypt inventories/projects/vietcgi/group_vars/vault.yml
```

Run playbook with vault password:
```bash
ansible-playbook playbooks/client_onboarding.yml \
  -i inventories/projects/vietcgi/hosts.yml \
  --ask-vault-pass
```

---

## Common Tasks

### Reset User Password
```bash
# Edit users.yml
managed_users:
  admin:
    auth0:
      password: "{{ vault_new_admin_password }}"

# Run playbook to sync
ansible-playbook playbooks/client_onboarding.yml ...
```

### Grant Sudo Access
```bash
# Edit users.yml
managed_users:
  support:
    rbac:
      sudo_access: true

# Run playbook
ansible-playbook playbooks/client_onboarding.yml ...
```

### Enable Deployments
```bash
# Edit users.yml
managed_users:
  newuser:
    rbac:
      can_deploy: true

# Run playbook
ansible-playbook playbooks/client_onboarding.yml ...
```

### View User Audit Logs
```bash
# SSH logs (server side)
sudo ausearch -m auth | grep "user=admin"

# Auth0 logs (cloud dashboard)
https://manage.auth0.com/dashboard → Logs → Search by user
```

---

## Security Checklist

- [ ] Store all passwords in Ansible Vault
- [ ] Rotate SSH keys every 90 days
- [ ] Review user access quarterly
- [ ] Remove inactive accounts within 30 days
- [ ] Enable MFA for all Auth0 logins
- [ ] Monitor audit logs weekly
- [ ] Update role assignments as needed
- [ ] Document all access changes in git commits
- [ ] Use strong passwords (12+ characters, mixed case, special chars)
- [ ] Never commit passwords to git (use vault only)

---

## Files to Know

```
inventories/projects/vietcgi/group_vars/
  ├── users.yml          ← User definitions (MAIN FILE)
  └── all.yml            ← References to users.yml

docs/
  ├── CENTRALIZED_USER_MANAGEMENT.md
  └── USER_MANAGEMENT_QUICK_REFERENCE.md (this file)

roles/
  ├── common/            ← Creates SSH users
  ├── auth0/             ← Creates Auth0 users
  └── app_integration/   ← Sets up RBAC
```

---

## Need Help?

See full documentation:
- 📖 [Centralized User Management](./CENTRALIZED_USER_MANAGEMENT.md)
- 📚 [SSH Access Control](./SSH_AND_AUTH0_USERS.md)
- 🔐 [Security Best Practices](../README.md#security)
