# Secret Management Strategy

## Overview

This document defines comprehensive secret management practices for ansible-infra, covering encryption, storage, rotation, and access control of sensitive data.

---

## Secret Types & Classification

### Type 1: Infrastructure Secrets (Critical)
- SSH private keys
- Ansible Vault password
- Database credentials
- API tokens
- Certificate private keys
- Encryption keys

**Storage**: Encrypted at-rest, access-controlled
**Access**: Limited to infrastructure team
**Rotation**: Quarterly or on compromise

### Type 2: Application Secrets (High)
- API keys (third-party services)
- Database connection strings
- Service credentials
- Configuration keys

**Storage**: Encrypted, versioned
**Access**: Application-specific roles
**Rotation**: Semi-annually or per policy

### Type 3: Credentials (Medium)
- User passwords
- Service account passwords
- TOTP backup codes

**Storage**: Vault, encrypted
**Access**: Individual users or service accounts
**Rotation**: Annually or on compromise

---

## Ansible Vault Strategy

### Vault Organization

```
inventories/
├── production/
│   └── vault/
│       ├── main.yml                 # Core secrets
│       ├── ssh_keys.yml            # SSH credentials
│       └── database.yml             # DB passwords
├── staging/
│   └── vault/
│       └── main.yml
└── development/
    └── vault/
        └── main.yml
```

### Vault Password Management

**Primary Password Storage**:
```bash
# Generate secure password
openssl rand -base64 32 > /etc/ansible/vault-password

# Set permissions (readable only by Ansible user)
chmod 0600 /etc/ansible/vault-password
chown ansible:ansible /etc/ansible/vault-password

# Never commit to git
echo "vault-password" >> .gitignore
```

**CI/CD Password Handling**:
```bash
# Store in CI/CD secrets (GitHub, GitLab, Jenkins, etc.)
# Do NOT commit to git repository
export ANSIBLE_VAULT_PASSWORD_FILE="/dev/stdin"
echo "$VAULT_PASSWORD_SECRET" | ansible-playbook ...
```

**Backup Password**:
```bash
# Store in secure location separate from vault files
# Examples:
# - Encrypted file in 1Password, LastPass
# - Physical copy in secure safe
# - Hardware security module (HSM)

# Recovery procedure (if password lost)
1. Access backup password from secure storage
2. Decrypt vault files
3. Generate new password
4. Re-encrypt all vault files
```

### Vault File Encryption

**Encrypting a file**:
```bash
# Create plain file initially
cat > inventories/production/vault/main.yml <<EOF
---
db_password: mypassword123
api_key: secret-api-key-here
EOF

# Encrypt with Vault
ansible-vault encrypt inventories/production/vault/main.yml
# Prompts for password

# Verify encryption
file inventories/production/vault/main.yml
# Output: ASCII text, with very long lines (encrypted)
```

**Editing encrypted file**:
```bash
# Edit without decrypting to disk
ansible-vault edit inventories/production/vault/main.yml

# Decrypt, edit, re-encrypt automatically
# File remains encrypted on disk
```

**Rotating vault password**:
```bash
# Old password
OLD_PASS="old-password"

# New password
NEW_PASS="new-password"

# Rekey all vault files
find inventories -name "*.yml" -type f | while read file; do
  if grep -q "!vault" "$file" 2>/dev/null; then
    ansible-vault rekey --vault-id old@- --vault-id new@- "$file" <<< "$OLD_PASS\n$NEW_PASS"
  fi
done

# Update stored password
echo "$NEW_PASS" > /etc/ansible/vault-password
chmod 0600 /etc/ansible/vault-password
```

---

## Using Secrets in Playbooks

### Method 1: Variable Substitution

```yaml
# inventories/production/vault/database.yml (encrypted)
---
postgres_password: "secret_password_123"
postgres_user: "admin"

# roles/common/tasks/configure_database.yml
---
- name: Configure PostgreSQL access
  lineinfile:
    path: /etc/postgresql/postgresql.conf
    regexp: "^#password ="
    line: "password = {{ postgres_password }}"
  no_log: true  # Don't log password
  become: yes
```

### Method 2: Vault Lookup (dynamic)

```yaml
- name: Get secret from Vault
  set_fact:
    api_token: "{{ lookup('vault', 'secret/prod/api/token') }}"
  no_log: true
```

### Method 3: File-based Secrets

```yaml
- name: Copy encrypted SSH key
  copy:
    src: "{{ lookup('file', 'inventories/{{ env }}/vault/ssh_key.pem') }}"
    dest: /home/ansible/.ssh/id_rsa
    mode: '0600'
    owner: ansible
  no_log: true
```

### Best Practices

**Always use `no_log: true`**:
```yaml
- name: Task that handles secrets
  shell: |
    mysql -u user -p'{{ mysql_password }}' << EOF
    SELECT * FROM users;
    EOF
  no_log: true  # Prevents password in logs
```

**Never hardcode secrets**:
```yaml
# ❌ WRONG
- name: Bad - hardcoded password
  shell: mysql -u admin -psecret_password_123

# ✓ CORRECT
- name: Good - use variable
  shell: mysql -u admin -p'{{ vault_password }}'
  no_log: true
```

**Validate secret format**:
```yaml
- name: Validate database password
  assert:
    that:
      - db_password is defined
      - db_password | length > 12
    fail_msg: "Database password not set or too weak"
```

---

## Secret Rotation Process

### Quarterly Rotation

**Schedule**: First Monday of every quarter at 02:00 UTC

**Process**:

```bash
#!/bin/bash
# rotate-all-secrets.sh - Complete secret rotation

set -e
QUARTER=$(date +%q-%Y)
LOG_FILE="/var/log/ansible-infra/secret-rotation-${QUARTER}.log"

echo "Starting secret rotation: $QUARTER" | tee -a "$LOG_FILE"

# 1. SSH Keys (on all hosts)
echo "1. Rotating SSH keys..." | tee -a "$LOG_FILE"
ansible-playbook playbooks/rotate-ssh-keys.yml \
  -i inventories/production \
  >> "$LOG_FILE" 2>&1

# 2. Database passwords
echo "2. Rotating database credentials..." | tee -a "$LOG_FILE"
for db in postgres mysql redis; do
  ansible-playbook playbooks/rotate-db-password.yml \
    -e "database=$db" \
    >> "$LOG_FILE" 2>&1
done

# 3. API tokens
echo "3. Rotating API tokens..." | tee -a "$LOG_FILE"
ansible-playbook playbooks/rotate-api-tokens.yml \
  >> "$LOG_FILE" 2>&1

# 4. Vault password (last)
echo "4. Rotating Vault master password..." | tee -a "$LOG_FILE"
bash /usr/local/bin/rotate-vault-password.sh \
  >> "$LOG_FILE" 2>&1

# 5. Verification
echo "5. Verifying rotation..." | tee -a "$LOG_FILE"
ansible all -i inventories/production -m ping \
  >> "$LOG_FILE" 2>&1

# 6. Audit log
echo "Rotation completed: $(date)" >> "$LOG_FILE"
chmod 0600 "$LOG_FILE"

# 7. Notify team
mail -s "Secret rotation complete: $QUARTER" ops@example.com < "$LOG_FILE"
```

### Emergency Rotation (Suspected Compromise)

```bash
#!/bin/bash
# emergency-rotate-secrets.sh - Immediate secret rotation

set -e

echo "🚨 EMERGENCY SECRET ROTATION"
echo "Time: $(date)"
echo ""

# Phase 1: Immediate containment (5 min)
echo "Phase 1: Containing potential compromise..."
# Kill active sessions
pkill -u suspected_user
# Revoke SSH keys
ansible all -i inventories/production -m authorized_key \
  -a "user=ansible key={{item}} state=absent"
# Reset Vault token
vault token revoke -self

# Phase 2: Generate new secrets (10 min)
echo "Phase 2: Generating new secrets..."
NEW_DB_PASS=$(openssl rand -base64 32)
NEW_API_KEY=$(openssl rand -hex 32)
NEW_SSH_KEY=$(ssh-keygen -t ed25519 -f /tmp/new_key -N "")

# Phase 3: Deploy new secrets (20 min)
echo "Phase 3: Deploying new secrets..."
ansible-playbook playbooks/deploy-new-secrets.yml \
  -e "db_password=$NEW_DB_PASS" \
  -e "api_key=$NEW_API_KEY"

# Phase 4: Verify functionality (10 min)
echo "Phase 4: Verifying system functionality..."
ansible all -i inventories/production -m command \
  -a "systemctl status ansible"

# Phase 5: Audit
echo "Phase 5: Auditing compromised access..."
grep suspected_user /var/log/auth.log > /tmp/audit-report.log

echo ""
echo "✓ Emergency rotation complete"
echo "  Audit report: /tmp/audit-report.log"
echo "  Next: Investigate root cause and file incident"
```

---

## External Secret Management (Optional)

### HashiCorp Vault Integration

For larger deployments, integrate external Vault:

```yaml
# vault-config.yml
- name: Configure Vault integration
  hosts: localhost
  tasks:
    - name: Authenticate to Vault
      uri:
        url: "http://vault.example.com:8200/v1/auth/approle/login"
        method: POST
        body_format: json
        body:
          role_id: "{{ vault_role_id }}"
          secret_id: "{{ vault_secret_id }}"
      register: vault_login

    - name: Get database credentials from Vault
      uri:
        url: "http://vault.example.com:8200/v1/secret/data/database/prod"
        headers:
          X-Vault-Token: "{{ vault_login.json.auth.client_token }}"
      register: vault_secrets

    - name: Use secrets in playbook
      debug:
        msg: "DB Username: {{ vault_secrets.json.data.data.username }}"
```

### AWS Secrets Manager Integration

```bash
#!/bin/bash
# Get secret from AWS Secrets Manager

SECRET_NAME="ansible-infra/prod/db-password"
SECRET_VALUE=$(aws secretsmanager get-secret-value \
  --secret-id "$SECRET_NAME" \
  --query SecretString \
  --output text)

# Use in playbook
export DB_PASSWORD="$SECRET_VALUE"
ansible-playbook playbooks/configure.yml \
  -e "db_password=${DB_PASSWORD}"
```

---

## Security Best Practices

### Principle of Least Privilege

```yaml
# ❌ WRONG - Everyone has access to all secrets
vault_passwords:
  - db_password
  - api_keys
  - ssh_keys

# ✓ CORRECT - Separate by environment and role
inventories/
├── production/
│   └── vault/
│       ├── database.yml     (only db team reads)
│       ├── api.yml         (only app team reads)
│       └── infra.yml       (only devops reads)
├── staging/
│   └── vault/
│       └── main.yml        (team leads read)
```

### Encryption Standards

- **Algorithm**: AES-256 (Ansible Vault default)
- **Key derivation**: PBKDF2 (Ansible Vault default)
- **Transport**: TLS 1.3+ always
- **At-rest**: Encrypted files, no plaintext

### Access Auditing

```bash
# Log all secret access
- name: Audit secret access
  lineinfile:
    path: /var/log/ansible-infra/vault-access.log
    line: "{{ ansible_date_time.iso8601 }} - {{ ansible_user }} accessed {{ secret_name }}"
    create: yes

# Review access logs monthly
grep "SECRET" /var/log/ansible-infra/vault-access.log | wc -l
```

### Backup of Secrets

```bash
#!/bin/bash
# Backup vault files securely

BACKUP_DIR="/backups/vault"
mkdir -p "$BACKUP_DIR"

# Create tarball
tar -czf "${BACKUP_DIR}/vault-$(date +%Y%m%d).tar.gz" \
  inventories/*/vault/

# Encrypt backup
openssl enc -aes-256-cbc -salt -in \
  "${BACKUP_DIR}/vault-$(date +%Y%m%d).tar.gz" \
  -out "${BACKUP_DIR}/vault-$(date +%Y%m%d).tar.gz.enc" \
  -k "$VAULT_BACKUP_KEY"

# Remove unencrypted
rm "${BACKUP_DIR}/vault-$(date +%Y%m%d).tar.gz"

# Store offsite
aws s3 cp "${BACKUP_DIR}/vault-$(date +%Y%m%d).tar.gz.enc" \
  s3://backups-bucket/vault/
```

---

## Secret Validation

### Pre-Deployment Checks

```bash
#!/bin/bash
# validate-secrets.sh - Check all required secrets are set

REQUIRED_SECRETS=(
  "db_password"
  "api_key"
  "ssh_key"
  "vault_password"
)

for secret in "${REQUIRED_SECRETS[@]}"; do
  if ! ansible-vault view inventories/production/vault/main.yml \
    2>/dev/null | grep -q "^${secret}:"; then
    echo "✗ Missing secret: $secret"
    exit 1
  fi
done

echo "✓ All required secrets present"
```

### Password Strength Requirements

```yaml
- name: Validate password strength
  assert:
    that:
      - db_password | length >= 16
      - db_password is regex('[A-Z]')      # Uppercase
      - db_password is regex('[a-z]')      # Lowercase
      - db_password is regex('[0-9]')      # Number
      - db_password is regex('[!@#$%^&*]') # Special char
    fail_msg: "Password does not meet complexity requirements"
```

---

## Incident Response

### Suspected Compromise

1. **Immediate actions** (< 5 min)
   - Revoke compromised credentials
   - Kill active sessions
   - Notify security team

2. **Investigation** (5-30 min)
   - Review access logs
   - Identify what was accessed
   - Assess damage

3. **Remediation** (30-60 min)
   - Rotate all potentially compromised secrets
   - Deploy new credentials
   - Verify system functionality

4. **Post-incident**
   - Document incident
   - Review security controls
   - Update procedures

---

## Documentation

**Last Updated**: November 15, 2025
**Version**: 1.0.0
**Status**: Production-Ready
**Next Review**: February 15, 2026

For sensitive questions, contact security@example.com
