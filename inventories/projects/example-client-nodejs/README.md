# Example Client: Node.js Application

This is a complete working example of a client configuration for deploying Node.js applications with Auth0 integration.

## What This Shows

- Complete client directory structure
- Node.js application configuration
- Auth0 credentials setup
- Multiple server deployment
- Environment-specific settings
- Best practices for production

## Files

| File | Purpose |
|------|---------|
| `hosts.yml` | Server inventory (example IPs) |
| `group_vars/all.yml` | Client & Auth0 configuration |
| `host_vars/*.yml` | Per-server configuration |
| `auth0_vault.yml` | Encrypted Auth0 credentials |
| `README.md` | This file |

## Quick Start

### 1. Copy to Your Project

```bash
# Copy example configuration
cp -r inventories/projects/example-client-nodejs \
 inventories/projects/mycompany

# Edit configuration
cd inventories/projects/mycompany
```

### 2. Update Server IPs

Edit `hosts.yml` and replace example IPs with your servers:

```yaml
app_servers:
 hosts:
 prod-01:
 ansible_host: "203.0.113.10" # ← Replace with your IP
 prod-02:
 ansible_host: "203.0.113.11" # ← Replace with your IP
```

### 3. Create Vault

Create encrypted vault with your Auth0 credentials:

```bash
ansible-vault create auth0_vault.yml
# Enter your vault password (strong, 24+ characters)

# Add these values (from Auth0 dashboard):
vault_auth0_domain: "your-tenant.auth0.com"
vault_auth0_client_id: "your_m2m_client_id"
vault_auth0_client_secret: "your_m2m_secret"
vault_google_oauth_client_id: ""
vault_google_oauth_secret: ""
vault_initial_admin_password: "InitialPass123!"
```

### 4. Customize Configuration

Edit `group_vars/all.yml`:
- Change `client_name: "example"` to your company name
- Update `client_domain: "example.com"` to your domain
- Modify application names and ports
- Add environment variables for your app

### 5. Test Connectivity

```bash
# Verify SSH access works
ansible all -i hosts.yml -m ping --ask-vault-pass

# Expected output:
# prod-01 | SUCCESS => {"ping": "pong"}
# prod-02 | SUCCESS => {"ping": "pong"}
```

### 6. Deploy

```bash
# Dry-run to preview changes
ansible-playbook ../../playbooks/client_onboarding.yml \
 -i hosts.yml \
 --ask-vault-pass \
 --check \
 --diff

# If everything looks good, deploy:
ansible-playbook ../../playbooks/client_onboarding.yml \
 -i hosts.yml \
 --ask-vault-pass \
 -v
```

## Configuration Breakdown

### hosts.yml

- **prod-01, prod-02**: Two application servers
- **app_framework: "nodejs"**: Tells role to create Node.js config
- **app_name**: Application identifier (appears in configs)

```yaml
prod-01:
 ansible_host: "203.0.113.10"
 app_framework: "nodejs"
 app_name: "api-gateway"
```

### group_vars/all.yml

**Client Information**:
```yaml
client_name: "example" # Company/client name
client_domain: "example.com" # Primary domain
client_env: "production" # Environment
```

**Auth0 Applications**:
```yaml
auth0_applications:
 - name: "example-api" # Application name in Auth0
 type: "non_interactive" # Backend app (no UI)

 - name: "example-webapp" # Web application
 type: "regular_web"
 redirect_uris:
 - "https://example.com/callback"
 - "https://app.example.com/callback"
```

**Node.js Application**:
```yaml
app_framework: "nodejs" # Activates Node.js config
app_name: "api-gateway" # App identifier
app_root_path: "/opt/api-gateway" # Where app is deployed
app_env_vars:
 API_PORT: "3000"
 LOG_LEVEL: "info"
 CACHE_ENABLED: "true"
```

## What Gets Deployed

After running the playbook, you'll have:

### On Each Server

1. **OS Baseline** (via common role):
 - Security updates applied
 - Firewall configured
 - SSH hardened
 - System users created

2. **Auth0 Configuration** (via auth0 role):
 - Applications created in Auth0 tenant
 - Users registered (if configured)
 - Roles and permissions set up
 - Social login enabled (if configured)

3. **Application Setup** (via app_integration role):
 - `.env` file generated with Auth0 credentials
 - `auth0.config.js` created for Node.js
 - File permissions secured (0640)
 - Ready for application deployment

### Generated Files

```
/opt/api-gateway/
├── .env # Auth0 domain, client ID, secret
├── auth0.config.js # Node.js configuration module
├── package.json # (you provide)
├── server.js # (you provide)
└── node_modules/ # (npm install)
```

### In Auth0 Dashboard

- Application "example-api" created (non_interactive)
- Application "example-webapp" created (regular_web)
- Redirect URIs configured
- CORS origins set up
- Initial user created (if configured)

## Node.js Integration Example

Once deployed, integrate Auth0 in your Node.js app:

```javascript
// Load configuration
require('dotenv').config();
const Auth0Config = require('./auth0.config');

// Use in your application
const { ManagementClient } = require('auth0');

const management = new ManagementClient({
 domain: process.env.AUTH0_DOMAIN,
 clientId: process.env.AUTH0_CLIENT_ID,
 clientSecret: process.env.AUTH0_CLIENT_SECRET
});

// Example: Get all users
management.getUsers()
 .then(users => console.log('Users:', users))
 .catch(err => console.error('Error:', err));
```

## Modifications

### Add Another Server

Edit `hosts.yml`:
```yaml
app_servers:
 hosts:
 prod-01:
 ansible_host: "203.0.113.10"
 app_name: "api-gateway"

 prod-02:
 ansible_host: "203.0.113.11"
 app_name: "api-gateway"

 prod-03: # ← New server
 ansible_host: "203.0.113.12"
 app_name: "api-gateway"
```

### Deploy Different Apps on Different Servers

Use `host_vars`:

Create `host_vars/prod-01.yml`:
```yaml
---
app_framework: "nodejs"
app_name: "api-gateway"
```

Create `host_vars/prod-02.yml`:
```yaml
---
app_framework: "nodejs"
app_name: "web-app"
```

### Use Staging Environment

Create separate directories:
```bash
inventories/projects/example-client-nodejs/
├── staging/
│ ├── hosts.yml
│ ├── group_vars/all.yml
│ └── auth0_vault.yml
└── production/
 ├── hosts.yml
 ├── group_vars/all.yml
 └── auth0_vault.yml
```

Deploy to staging:
```bash
ansible-playbook playbooks/client_onboarding.yml \
 -i inventories/projects/example-client-nodejs/staging/hosts.yml \
 --ask-vault-pass
```

## Security Checklist

Before deploying to production:

- [ ] Vault password stored in password manager
- [ ] Auth0 account has MFA enabled
- [ ] M2M application has only necessary scopes
- [ ] SSH keys are Ed25519 with proper permissions
- [ ] .env files will have 0640 permissions
- [ ] Credentials backed up securely
- [ ] Team members know vault password (securely shared)
- [ ] Firewall rules allow only necessary ports

## Troubleshooting

### "SSH connection failed"

```bash
# Check connectivity
ssh -i ~/.ssh/id_rsa ubuntu@203.0.113.10

# If fails, verify:
# - Server IP is correct
# - SSH key has correct permissions (600)
# - Security group allows port 22
# - Server is running
```

### "Auth0 API error"

```bash
# Check vault file has correct credentials
ansible-vault view auth0_vault.yml

# Verify in Auth0 dashboard:
# - Domain is exactly "your-domain.auth0.com"
# - M2M app has Auth0 Management API access
# - Client ID and secret are correct
```

### ".env file not created"

Check playbook output for errors in app_integration role. Verify:
- `app_framework: "nodejs"` is set
- `app_name` is defined
- `app_root_path` is writable

## Next Steps

1. Copy example to your project
2. Update server IPs and names
3. Create vault with Auth0 credentials
4. Customize configuration
5. Test connectivity
6. Deploy with playbook
7. Verify in Auth0 dashboard
8. Deploy your Node.js application
9. Test Auth0 login flow
10. Set up monitoring and backups

## Documentation

- [Client Onboarding Guide](../../docs/CLIENT_ONBOARDING.md) - Complete walkthrough
- [Auth0 Integration Guide](../../docs/AUTH0_INTEGRATION.md) - Detailed Auth0 setup
- [Security Audit](../../docs/SECURITY_AUDIT.md) - Security practices
- [Role Documentation](../../roles/app_integration/README.md) - App integration details

---

**Status**: Example / Template
**Last Updated**: November 16, 2025
**Framework**: Node.js
**Environment**: Production (example IPs are for illustration)
