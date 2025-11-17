# Auth0 Role - Identity and Access Management Integration

Automates Auth0 tenant configuration and application setup for client onboarding.

## Overview

This role manages Auth0 via the Auth0 Management API:
- Creates OIDC/OAuth applications
- Manages users and roles
- Configures social/enterprise connections
- Generates application configuration files

**Auth0 provides the identity service** (managed), while this role **configures it via API**.

## Requirements

### Credentials
1. Auth0 account (free tier supports up to 25,000 monthly active users)
2. Machine-to-Machine (M2M) application in Auth0 with:
 - Auth0 Management API access
 - All necessary scopes enabled

### Python Modules
- `auth0-python` (automatically installed by role)

### Network
- HTTPS access to Auth0 API (https://{domain}/api/v2/)

## Variables

### Required
```yaml
auth0_domain: "acme-corp.auth0.com" # Your Auth0 tenant domain
auth0_client_id: "{{ vault_auth0_client_id }}" # M2M app client ID
auth0_client_secret: "{{ vault_auth0_client_secret }}" # M2M app secret
```

### Applications
```yaml
auth0_applications:
 - name: "acme-webapp"
 type: "regular_web"
 redirect_uris:
 - "https://app.example.com/callback"
 allowed_logout_urls:
 - "https://app.example.com/logout"
 web_origins:
 - "https://app.example.com"
```

### Users
```yaml
auth0_users:
 - email: "john@example.com"
 given_name: "John"
 family_name: "Doe"
 password: "{{ vault_user_password }}"
```

### Roles and Permissions
```yaml
auth0_roles:
 - name: "admin"
 description: "Administrator"
 permissions:
 - resource: "api://acme-api"
 permission: "write:users"
```

### Connections (Social Login)
```yaml
auth0_connections:
 - name: "google-oauth2"
 enabled: true
 strategy: "google-oauth2"
 options:
 client_id: "{{ vault_google_client_id }}"
 client_secret: "{{ vault_google_secret }}"
```

### Settings
```yaml
auth0_mfa_enabled: true
auth0_mfa_methods:
 - "sms"
 - "totp"
auth0_password_policy: "good"
auth0_log_retention_days: 30
```

## Tasks

1. **validate_credentials.yml**
 - Checks Auth0 credentials
 - Installs auth0-python module
 - Tests API connectivity

2. **create_applications.yml**
 - Creates OIDC/OAuth applications
 - Sets redirect URIs and CORS origins
 - Saves credentials to file

3. **manage_users.yml**
 - Creates/updates users
 - Sets user metadata
 - Assigns roles

4. **configure_roles.yml**
 - Creates roles
 - Defines permissions
 - Links to API resources

5. **configure_connections.yml**
 - Enables social logins (Google, Microsoft)
 - Configures enterprise connections

6. **configure_api.yml**
 - Creates API resources
 - Defines scopes
 - Sets token expiration

7. **configure_settings.yml**
 - Enables MFA
 - Sets password policy
 - Configures rate limiting
 - Applies branding

8. **generate_configs.yml**
 - Creates .env files
 - Generates application configs
 - Outputs credential files

## Usage

### Basic Setup
```yaml
---
- name: Configure Auth0 for client
 hosts: localhost
 gather_facts: no
 roles:
 - auth0
 vars:
 auth0_domain: "acme-corp.auth0.com"
 auth0_client_id: "{{ vault_auth0_client_id }}"
 auth0_client_secret: "{{ vault_auth0_client_secret }}"
 auth0_applications:
 - name: "acme-webapp"
 type: "regular_web"
 redirect_uris:
 - "https://acme.example.com/callback"
```

### Running Specific Tasks
```bash
# Only validate credentials
ansible-playbook playbook.yml -t validation

# Only create applications
ansible-playbook playbook.yml -t applications

# Everything
ansible-playbook playbook.yml
```

## Output Files

The role generates:
- `{{ client_name }}_auth0_credentials.txt` - Application credentials (client IDs/secrets)
- `{{ client_name }}_auth0_configs/.env` - Environment variables for applications

**Store credentials securely!** Client secrets are only shown once.

## Vault Setup

Protect credentials with Ansible Vault:

```bash
# Create vault file
ansible-vault create inventories/projects/acme_corp/auth0_vault.yml

# Edit vault file
ansible-vault edit inventories/projects/acme_corp/auth0_vault.yml

# Run playbook with vault
ansible-playbook playbook.yml --ask-vault-pass
```

### Vault File Contents
```yaml
---
vault_auth0_client_id: "your_m2m_client_id"
vault_auth0_client_secret: "your_m2m_client_secret"
vault_google_oauth_client_id: "google_client_id"
vault_google_oauth_secret: "google_secret"
vault_user_password: "initial_user_password"
```

## Examples

### Complete Client Onboarding
```yaml
---
- name: Onboard new client
 hosts: localhost
 gather_facts: no
 roles:
 - auth0
 vars:
 client_name: "acme-corp"
 auth0_domain: "acme-corp.auth0.com"
 auth0_client_id: "{{ vault_auth0_client_id }}"
 auth0_client_secret: "{{ vault_auth0_client_secret }}"

 auth0_applications:
 - name: "acme-webapp"
 type: "regular_web"
 redirect_uris:
 - "https://acme.example.com/callback"
 - "http://localhost:3000/callback"
 - name: "acme-api"
 type: "non_interactive"

 auth0_users:
 - email: "admin@acme.com"
 given_name: "Admin"
 family_name: "User"
 - email: "user1@acme.com"
 given_name: "John"
 family_name: "Doe"

 auth0_connections:
 - name: "google-oauth2"
 enabled: true
 strategy: "google-oauth2"
 options:
 client_id: "{{ vault_google_client_id }}"
 client_secret: "{{ vault_google_secret }}"
```

## Troubleshooting

### "Failed to connect to Auth0"
- Verify auth0_domain is correct
- Check auth0_client_id and auth0_client_secret
- Ensure M2M app has Auth0 Management API access
- Check network connectivity to Auth0

### "Application already exists"
- Role skips existing applications
- To update, manually modify in Auth0 dashboard
- Or delete and re-run playbook

### Credentials not saved
- Check file permissions in playbook directory
- Ensure `{{ playbook_dir }}` is writable
- Check for secrets in Ansible output (don't paste in logs!)

## Security Notes

1. **Never commit credentials** to git
2. **Use Ansible Vault** for all secrets
3. **Rotate client secrets** regularly in Auth0
4. **Monitor Auth0 logs** for suspicious activity
5. **Enable MFA** on Auth0 admin accounts
6. **Limit API scope** - M2M apps should only have needed permissions

## Limitations

- Auth0 free tier: 25,000 monthly active users
- Manual user creation (bulk import available via API)
- Some advanced features require paid Auth0 plan
- Social connection setup requires external credentials (Google, Microsoft, etc.)

## Next Steps

1. **Apply this role** to configure Auth0
2. **Create app_integration role** to apply configs to apps
3. **Create client onboarding playbook** for complete setup
4. **Deploy applications** with Auth0 environment variables

## Support

- [Auth0 Documentation](https://auth0.com/docs)
- [Auth0 Python SDK](https://github.com/auth0/auth0-python)
- [Auth0 API Reference](https://auth0.com/docs/api/management/v2)

---

**Status**: In Development | **Last Updated**: {{ ansible_date_time.iso8601 }}
