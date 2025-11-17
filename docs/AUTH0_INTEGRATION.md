# Auth0 Integration Guide

Complete guide to implementing Auth0 identity management with this Ansible infrastructure framework.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Setup Prerequisites](#setup-prerequisites)
4. [Auth0 Tenant Configuration](#auth0-tenant-configuration)
5. [Framework Integration](#framework-integration)
6. [Client Onboarding Workflow](#client-onboarding-workflow)
7. [Security Best Practices](#security-best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Topics](#advanced-topics)

## Overview

The Auth0 integration provides:
- **Managed Identity Service**: Uses Auth0's cloud-based authentication platform (no self-hosted maintenance)
- **Multi-Application Support**: Seamlessly integrate multiple applications across different frameworks
- **Social Login**: Enable Google, Microsoft, GitHub, and other OAuth providers
- **RBAC & Permissions**: Fine-grained role-based access control
- **Automated Onboarding**: Complete client setup via Ansible orchestration
- **Scalable**: Supports up to 25,000 monthly active users on free tier

### Why Auth0?

| Feature | Benefit |
|---------|---------|
| **Managed Service** | No infrastructure to maintain, automatic updates |
| **Free Tier** | 25,000 MAU sufficient for 5-10 person teams |
| **Enterprise Ready** | MFA, social login, RBAC, audit logs included |
| **Developer Friendly** | Excellent documentation, multiple SDKs |
| **Clear Upsell Path** | Grows with your business seamlessly |
| **No Competitors** | Only Auth0 Ansible integration available |

## Architecture

### Three-Tier Integration Model

```
┌─────────────────────────────────────────────┐
│ Client Onboarding Playbook │
│ (orchestrates all 3 roles) │
└──────────┬──────────────────────────────────┘
 │
 ┌─────┴─────────────────────────────┐
 │ │
 ▼ ▼
┌──────────────────┐ ┌──────────────────┐
│ Common Role │ │ Auth0 Role │
│ (OS Baseline) │ │ (Identity Setup)│
│ │ │ │
│ • Security │ │ • Create Apps │
│ • Networking │ │ • Manage Users │
│ • System Config │ │ • Setup Roles │
│ • Firewalls │ │ • Social Login │
└──────────────────┘ └──────┬───────────┘
 │
 ▼
 ┌──────────────────────┐
 │ App Integration Role │
 │ (Finalize Apps) │
 │ │
 │ • Generate .env │
 │ • Framework Configs │
 │ • Setup Guidance │
 └──────────────────────┘
```

### Components

#### 1. Common Role (`roles/common/`)
Establishes consistent OS baseline across all distributions.

**Key Tasks**:
- Security hardening (firewall, fail2ban, auto-updates)
- System configuration (hostname, timezone, DNS)
- User and group management
- Package management

**Coverage**: Ubuntu, Debian, CentOS, Rocky, Alpine, macOS

#### 2. Auth0 Role (`roles/auth0/`)
Configures Auth0 tenant and creates applications.

**Key Tasks**:
- Validates Auth0 credentials and API connectivity
- Creates OIDC/OAuth applications
- Manages users and team members
- Defines roles and permissions
- Configures social login providers
- Generates configuration files

**Key Files**:
- `/roles/auth0/tasks/validate_credentials.yml` - Test API access
- `/roles/auth0/tasks/create_applications.yml` - Create OAuth apps
- `/roles/auth0/tasks/manage_users.yml` - Create/manage users
- `/roles/auth0/tasks/configure_roles.yml` - RBAC setup
- `/roles/auth0/tasks/configure_connections.yml` - Social login

#### 3. App Integration Role (`roles/app_integration/`)
Configures applications with Auth0 credentials.

**Supported Frameworks**:
- Node.js (Express, Next.js, NestJS)
- Python (Flask, FastAPI, Starlette)
- Django (with OIDC support)
- Go (with oauth2 package)
- Java (Spring Boot with OAuth2)

**Key Tasks**:
- Generates `.env` files with credentials
- Creates framework-specific configuration
- Provides integration code samples
- Sets up authentication flows

#### 4. Client Onboarding Playbook (`playbooks/client_onboarding.yml`)
Orchestrates complete client setup.

**Features**:
- State-based execution (create/destroy)
- Pre-flight validation
- Comprehensive reporting
- Rollback capability

## Setup Prerequisites

### 1. Auth0 Account

**Create a free Auth0 account**:
- Visit https://auth0.com/
- Sign up for free tier
- Verify email

**Create Machine-to-Machine Application**:

1. Go to Dashboard → Applications
2. Click "Create Application"
3. Select "Machine to Machine Applications"
4. Name: "Ansible Management"
5. Select "Auth0 Management API"
6. Grant all necessary scopes:
 - `create:clients` - Create applications
 - `read:clients` - List applications
 - `delete:clients` - Delete applications
 - `create:users` - Create users
 - `read:users` - List users
 - `update:users` - Update user information
 - `create:roles` - Create roles
 - `read:roles` - List roles
 - `delete:roles` - Delete roles
 - `create:connections` - Create connections
 - `read:connections` - List connections
 - `update:connections` - Update connections

### 2. Ansible & Dependencies

```bash
# Install Ansible
pip install ansible

# Install required Ansible modules
ansible-galaxy install community.general

# Install auth0-python SDK
pip install auth0-python
```

### 3. Infrastructure Prerequisites

```bash
# Target servers ready (SSH access configured)
# Python 3 installed
# Sudo access for configuration tasks
```

## Auth0 Tenant Configuration

### Step 1: Gather M2M Credentials

1. Navigate to Auth0 Dashboard → Applications → Machines to Machines
2. Click your "Ansible Management" application
3. Copy and save:
 - **Domain**: `your-domain.auth0.com`
 - **Client ID**: `{{ vault_auth0_client_id }}`
 - **Client Secret**: `{{ vault_auth0_client_secret }}`

⚠️ **IMPORTANT**: Client secret is only shown once. Store securely!

### Step 2: Create Vault File

```bash
# Create encrypted vault for credentials
ansible-vault create inventories/projects/acme_corp/auth0_vault.yml
```

**Vault Content**:
```yaml
---
vault_auth0_domain: "acme-corp.auth0.com"
vault_auth0_client_id: "abc123..."
vault_auth0_client_secret: "xyz789..."
vault_google_oauth_client_id: "google_id..."
vault_google_oauth_secret: "google_secret..."
vault_initial_admin_password: "strong_password"
```

### Step 3: Configure Social Login (Optional)

**Google OAuth**:
1. Visit https://console.developers.google.com/
2. Create new project
3. Enable "Google+ API"
4. Create OAuth 2.0 credentials (Web Application)
5. Add Auth0 callback: `https://YOUR_DOMAIN/login/callback`
6. Copy Client ID and Secret to vault

**Microsoft/Office365**:
1. Register application at https://portal.azure.com/
2. Create client secret
3. Set redirect URI: `https://YOUR_DOMAIN/login/callback`
4. Copy Application ID and secret to vault

## Framework Integration

### Node.js / Express

**Generated Files**:
- `.env` - Environment variables
- `auth0.config.js` - Auth0 configuration module

**Setup**:
```bash
npm install auth0 dotenv passport passport-auth0
```

**Example Middleware**:
```javascript
require('dotenv').config();
const Auth0Config = require('./auth0.config');

const passport = require('passport');
const Auth0Strategy = require('passport-auth0');

passport.use(new Auth0Strategy(
 {
 domain: Auth0Config.domain,
 clientID: Auth0Config.clientId,
 clientSecret: Auth0Config.clientSecret,
 callbackURL: 'http://localhost:3000/callback'
 },
 (accessToken, refreshToken, extraParams, profile, done) => {
 return done(null, profile);
 }
));
```

### Python / Flask

**Generated Files**:
- `.env` - Environment variables
- `auth0_config.py` - Auth0 configuration
- `auth0_settings_snippet.py` - Integration example

**Setup**:
```bash
pip install auth0-python python-dotenv authlib
```

**Example Initialization**:
```python
from auth0_config import Auth0Config
from authlib.integrations.flask_client import OAuth

oauth = OAuth()
oauth.register(
 'auth0',
 client_id=Auth0Config.CLIENT_ID,
 client_secret=Auth0Config.CLIENT_SECRET,
 api_base_url=f'https://{Auth0Config.DOMAIN}',
 access_token_url=f'https://{Auth0Config.DOMAIN}/oauth/token',
 authorize_url=f'https://{Auth0Config.DOMAIN}/authorize',
 client_kwargs={'scope': 'openid profile email'}
)
```

### Django

**Generated Files**:
- `.env` - Environment variables
- `auth0_config.py` - Auth0 configuration
- `auth0_settings_snippet.py` - Django settings for OIDC

**Setup**:
```bash
pip install python-social-auth[django] python-dotenv
```

**settings.py**:
```python
from auth0_config import Auth0Config

AUTHENTICATION_BACKENDS = [
 'social_core.backends.open_id_connect.OpenIdConnectAuth',
]

SOCIAL_AUTH_OIDC_ENDPOINT = f'https://{Auth0Config.DOMAIN}/'
SOCIAL_AUTH_OIDC_KEY = Auth0Config.CLIENT_ID
SOCIAL_AUTH_OIDC_SECRET = Auth0Config.CLIENT_SECRET
```

### Go

**Generated Files**:
- `.env` - Environment variables
- `config/auth0.go` - Configuration struct
- `auth/auth0.go` - OAuth2 helpers

**Setup**:
```bash
go get golang.org/x/oauth2
go get github.com/joho/godotenv
```

**Example Login**:
```go
cfg := config.LoadAuth0Config()
provider := auth.NewAuth0Provider(cfg)

// In HTTP handler:
loginURL := provider.GetLoginURL(state)
http.Redirect(w, r, loginURL, http.StatusFound)

// In callback handler:
token, err := provider.ExchangeCode(r.Context(), code)
userInfo, err := provider.GetUserInfo(r.Context(), token)
```

### Java / Spring Boot

**Generated Files**:
- `.env` - Environment variables
- `Auth0Config.java` - Spring configuration class
- `application.properties` - OAuth2 settings
- `POM_AUTH0_SNIPPET.xml` - Maven dependencies

**Setup**:
```bash
# Add to pom.xml
<dependency>
 <groupId>org.springframework.boot</groupId>
 <artifactId>spring-boot-starter-oauth2-client</artifactId>
</dependency>
```

**application.properties**:
```properties
spring.security.oauth2.client.registration.auth0.client-id=${AUTH0_CLIENT_ID}
spring.security.oauth2.client.registration.auth0.client-secret=${AUTH0_CLIENT_SECRET}
spring.security.oauth2.client.provider.auth0.issuer-uri=https://${AUTH0_DOMAIN}/
```

## Client Onboarding Workflow

### Step 1: Prepare Client Configuration

```bash
# Create client directory
mkdir -p inventories/projects/acme_corp

# Copy template
cp inventories/projects/_templates/client_template.yml \
 inventories/projects/acme_corp/group_vars/all.yml

# Edit configuration
vim inventories/projects/acme_corp/group_vars/all.yml
```

### Step 2: Create Encrypted Vault

```bash
ansible-vault create inventories/projects/acme_corp/auth0_vault.yml

# Enter vault password
# Add credentials from Step 1 above
```

### Step 3: Create Inventory

```bash
cat > inventories/projects/acme_corp/hosts.yml << 'EOF'
---
all:
 children:
 app_servers:
 hosts:
 acme-prod-01:
 ansible_host: 10.0.1.10
 ansible_user: ubuntu
 acme-prod-02:
 ansible_host: 10.0.1.11
 ansible_user: ubuntu
EOF
```

### Step 4: Run Onboarding Playbook

**Create Infrastructure**:
```bash
ansible-playbook playbooks/client_onboarding.yml \
 -i inventories/projects/acme_corp/hosts.yml \
 --ask-vault-pass \
 -v
```

**Dry Run** (preview changes):
```bash
ansible-playbook playbooks/client_onboarding.yml \
 -i inventories/projects/acme_corp/hosts.yml \
 --ask-vault-pass \
 --check \
 --diff
```

**Destroy Infrastructure**:
```bash
ansible-playbook playbooks/client_onboarding.yml \
 -i inventories/projects/acme_corp/hosts.yml \
 --ask-vault-pass \
 -e "onboarding_state=absent"
```

### Step 5: Deploy Applications

```bash
# Applications are configured with Auth0 credentials
# Deploy your applications using generated .env files
```

### Step 6: Verify Integration

1. **Check Auth0 Dashboard**:
 - Applications created and listed
 - Users created (if configured)
 - Roles and permissions defined

2. **Verify Application Configuration**:
 ```bash
 # Check .env file on application server
 ssh ubuntu@10.0.1.10
 cat /opt/acme-corp-app/.env
 ```

3. **Test Login Flow**:
 - Navigate to application login
 - Authenticate via Auth0
 - Verify user information appears
 - Test logout

## Security Best Practices

### 1. Credential Management

 **DO**:
- Store credentials in Ansible Vault
- Rotate client secrets quarterly
- Use separate clients for different environments
- Limit M2M app scopes to minimum needed
- Use strong vault passwords (24+ characters)

 **DON'T**:
- Commit vault credentials to git
- Hardcode secrets in playbooks
- Share vault passwords via email
- Use same credentials for multiple clients
- Disable MFA on Auth0 admin accounts

### 2. Inventory Security

```bash
# Add to .gitignore
echo "inventories/projects/*/auth0_vault.yml" >> .gitignore
echo "inventories/projects/*/group_vars/vault*.yml" >> .gitignore
echo ".env*" >> .gitignore
```

### 3. Auth0 Account Security

1. **Enable MFA** on all auth0.com login accounts
2. **Rotate Client Secrets** regularly:
 - Generate new secret in Auth0 dashboard
 - Update vault and redeploy
 - Revoke old secret
3. **Monitor Auth0 Logs**:
 - Review suspicious authentication attempts
 - Audit user creation and deletion
 - Track role permission changes
4. **Limit Admin Access**:
 - Use separate admin account
 - Enable multi-factor authentication
 - Regular access reviews

### 4. Application Security

1. **HTTPS Only**:
 - Use TLS 1.2+ for all communications
 - Set secure cookie flags:
 ```yaml
 SESSION_COOKIE_SECURE: true
 SESSION_COOKIE_HTTPONLY: true
 SESSION_COOKIE_SAMESITE: 'Lax'
 ```

2. **Token Validation**:
 - Always validate JWT signature
 - Check token expiration
 - Verify audience claim

3. **Rate Limiting**:
 - Enable Auth0 rate limiting
 - Set reasonable limits (10 req/sec default)
 - Monitor for abuse patterns

### 5. Backup & Disaster Recovery

```bash
# Backup Auth0 configuration
ansible-playbook playbooks/backup_auth0_config.yml

# Store in secure location (S3, encrypted backup)
```

## Troubleshooting

### Auth0 API Connection Errors

**Error**: `Failed to connect to Auth0`

**Solutions**:
1. Verify auth0_domain is correct (without protocol)
2. Check client_id and client_secret match
3. Verify M2M app has Auth0 Management API access
4. Test credentials manually:
 ```python
 from auth0.authentication import GetToken

 get_token = GetToken('your-domain.auth0.com')
 token = get_token.client_credentials(
 'your_client_id',
 'your_client_secret',
 'https://your-domain.auth0.com/api/v2/'
 )
 ```

### Application Already Exists

**Error**: `Application 'my-app' already exists in Auth0`

**Solutions**:
1. Role skips existing applications (idempotent)
2. To update: delete and re-run playbook
3. Or modify directly in Auth0 dashboard

### Permission Denied on .env File

**Error**: `Permission denied: /opt/app/.env`

**Solutions**:
1. Check file permissions:
 ```bash
 ls -la /opt/app/.env
 # Should show: -rw-r----- app app 0640
 ```
2. Verify application runs as `app` user
3. Check user is in `app` group:
 ```bash
 groups app
 ```

### Auth0 User Creation Fails

**Error**: `User creation failed: email already exists`

**Solutions**:
1. Check Auth0 dashboard for existing user
2. Use different email or delete existing user
3. Update vault with correct email addresses

### .env Variables Not Loading

**Error**: `AUTH0_DOMAIN is undefined in application`

**Solutions**:
1. Verify `.env` file exists:
 ```bash
 file /opt/app/.env
 ```
2. Check application loads dotenv:
 - Node.js: `require('dotenv').config()`
 - Python: `from dotenv import load_dotenv; load_dotenv()`
3. Verify file is readable by application user
4. Check application startup logs

## Advanced Topics

### Multi-Environment Setup

Create separate configurations for dev/staging/prod:

```bash
inventories/projects/acme_corp/
├── dev/
│ ├── hosts.yml
│ ├── group_vars/all.yml
│ └── auth0_vault.yml
├── staging/
│ ├── hosts.yml
│ ├── group_vars/all.yml
│ └── auth0_vault.yml
└── prod/
 ├── hosts.yml
 ├── group_vars/all.yml
 └── auth0_vault.yml
```

Run for specific environment:
```bash
ansible-playbook playbooks/client_onboarding.yml \
 -i inventories/projects/acme_corp/prod/hosts.yml \
 --ask-vault-pass
```

### Custom Auth0 Configuration

Extend auth0 role for additional features:

```yaml
# In your playbook
- role: auth0
 vars:
 # Custom settings
 auth0_extra_scopes:
 - "offline_access"
 - "email_verified"

 # Custom metadata
 auth0_user_metadata:
 preferences:
 theme: "dark"
```

### CI/CD Integration

Integrate with GitLab CI/GitHub Actions:

```yaml
# .gitlab-ci.yml example
deploy_to_acme:
 stage: deploy
 script:
 - ansible-playbook playbooks/client_onboarding.yml \
 -i inventories/projects/acme_corp/prod/hosts.yml \
 --vault-password-file=$ANSIBLE_VAULT_PASS
 only:
 - main
```

### Monitoring & Alerts

Configure Auth0 monitoring:

```bash
# Configure Auth0 Rules for audit logging
# Set up Splunk/ELK integration for log aggregation
# Enable Auth0 Anomaly Detection
```

## Support & Resources

- **Auth0 Documentation**: https://auth0.com/docs
- **Auth0 API Reference**: https://auth0.com/docs/api/management/v2
- **Auth0 Community**: https://auth0.com/blog
- **Ansible Documentation**: https://docs.ansible.com
- **This Framework**: See docs/ and role README files

---

**Last Updated**: November 2025
**Version**: 1.0
**Status**: Production Ready
