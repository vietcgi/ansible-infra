# App Integration Role - Auth0 Configuration for Applications

Applies Auth0 OIDC/OAuth configuration to applications across multiple frameworks.

## Overview

This role integrates Auth0 identity credentials into applications by:
- Generating `.env` files with Auth0 domain and client credentials
- Creating framework-specific configuration files
- Providing setup guidance and code samples
- Supporting multiple application frameworks

**Prerequisite**: Auth0 role must be executed first to generate credentials and application IDs.

## Requirements

### Variables from Auth0 Role
```yaml
auth0_domain: "acme-corp.auth0.com" # Auth0 tenant domain
auth0_client_id: "{{ created_app.client_id }}" # Application client ID
auth0_client_secret: "{{ created_app.client_secret }}" # Application client secret
```

### Framework Support
- **Node.js** (Express, Next.js, etc.)
- **Python** (Flask, FastAPI, etc.)
- **Django** (with social-auth integration)
- **Go** (with oauth2 package)
- **Java** (Spring Boot with OAuth2)

## Variables

### Required
```yaml
app_framework: "nodejs" # Framework type: nodejs, python, django, go, java
app_name: "my-app" # Application name (used in configs)
auth0_domain: "" # Auth0 tenant domain
auth0_client_id: "" # Application client ID
```

### Optional
```yaml
app_env: "development" # Environment: development, staging, production
app_root_path: "/opt/app" # Path to application root
app_config_path: "{{ app_root_path }}/config" # Config directory
app_env_path: "{{ app_root_path }}/.env" # .env file location
app_config_user: "app" # File owner
app_config_group: "app" # File group
app_config_mode: "0640" # File permissions
auth0_client_secret: "" # Application client secret
auth0_audience: "" # API audience URI
app_env_vars: {} # Additional environment variables
```

## Tasks

### 1. **validate.yml**
- Validates required variables are set
- Checks Auth0 configuration is complete
- Verifies framework type is supported
- Fails fast if setup is incomplete

### 2. **generate_env.yml**
- Creates application config directory
- Generates `.env` file with Auth0 credentials
- Sets proper file permissions for security
- Backs up existing files

### 3. **configure_nodejs.yml**
- Creates `auth0.config.js` configuration module
- Provides integration guidance for Express/Next.js
- Shows dotenv setup and usage patterns
- Explains auth0-node package integration

### 4. **configure_python.yml**
- Creates `auth0_config.py` configuration module
- Generates Django settings snippet for OIDC setup
- Shows python-dotenv integration
- Provides authentication backend examples

### 5. **configure_go.yml**
- Creates `config/auth0.go` configuration struct
- Generates `auth/auth0.go` OAuth2 helper functions
- Provides golang.org/x/oauth2 integration
- Includes token exchange and user info retrieval

### 6. **configure_java.yml**
- Creates `Auth0Config.java` Spring configuration class
- Generates `application.properties` with OAuth2 settings
- Provides Maven pom.xml dependencies snippet
- Includes Spring Security configuration example

## Usage

### Basic Node.js Application
```yaml
---
- name: Configure Node.js app with Auth0
 hosts: app_servers
 roles:
 - common # Apply baseline OS config first
 - app_integration
 vars:
 app_framework: "nodejs"
 app_name: "api-gateway"
 app_root_path: "/opt/api-gateway"
 auth0_domain: "acme-corp.auth0.com"
 auth0_client_id: "{{ vault_app_client_id }}"
 auth0_client_secret: "{{ vault_app_client_secret }}"
```

### Python/Django Application
```yaml
---
- name: Configure Django app with Auth0
 hosts: app_servers
 roles:
 - common
 - app_integration
 vars:
 app_framework: "django"
 app_name: "web-portal"
 app_root_path: "/opt/web-portal"
 app_env: "production"
 auth0_domain: "acme-corp.auth0.com"
 auth0_client_id: "{{ vault_app_client_id }}"
 auth0_client_secret: "{{ vault_app_client_secret }}"
 app_env_vars:
 DATABASE_URL: "postgresql://user:pass@db.example.com/web_portal"
 REDIS_URL: "redis://cache.example.com:6379"
```

### Go Application
```yaml
---
- name: Configure Go app with Auth0
 hosts: api_servers
 roles:
 - common
 - app_integration
 vars:
 app_framework: "go"
 app_name: "rest-api"
 app_root_path: "/opt/rest-api"
 auth0_domain: "{{ auth0_domain }}"
 auth0_client_id: "{{ vault_rest_api_client_id }}"
```

### Java/Spring Boot Application
```yaml
---
- name: Configure Spring Boot app with Auth0
 hosts: java_servers
 roles:
 - common
 - app_integration
 vars:
 app_framework: "java"
 app_name: "corporate-app"
 app_root_path: "/opt/corporate-app"
 auth0_domain: "acme-corp.auth0.com"
 auth0_client_id: "{{ vault_spring_client_id }}"
 auth0_client_secret: "{{ vault_spring_secret }}"
```

### Running Specific Framework Configuration
```bash
# Only generate .env file (all frameworks)
ansible-playbook playbook.yml -t env_generation

# Only configure Node.js
ansible-playbook playbook.yml -t nodejs

# Only configure Python/Django
ansible-playbook playbook.yml -t python

# Skip validation (for faster re-runs)
ansible-playbook playbook.yml --skip-tags validation
```

## Generated Files

| Framework | Generated Files | Purpose |
|-----------|-----------------|---------|
| All | `.env` | Environment variables with Auth0 credentials |
| Node.js | `auth0.config.js` | Auth0 configuration module for Node.js |
| Python | `auth0_config.py` | Auth0 configuration module for Python |
| Python/Django | `auth0_settings_snippet.py` | Django settings snippet for OIDC |
| Go | `config/auth0.go` | Go configuration struct and loaders |
| Go | `auth/auth0.go` | OAuth2 helper functions for Go |
| Java | `Auth0Config.java` | Spring Boot configuration class |
| Java | `application.properties` | Spring properties with OAuth2 config |
| Java | `POM_AUTH0_SNIPPET.xml` | Maven dependencies for Auth0 |

## Integration Steps by Framework

### Node.js

1. Install dependencies:
 ```bash
 npm install auth0 dotenv
 ```

2. Load configuration:
 ```javascript
 require('dotenv').config();
 const Auth0Config = require('./auth0.config');
 ```

3. Use in middleware:
 ```javascript
 const { ManagementClient } = require('auth0');
 const mgmt = new ManagementClient({
 domain: process.env.AUTH0_DOMAIN,
 clientId: process.env.AUTH0_CLIENT_ID,
 clientSecret: process.env.AUTH0_CLIENT_SECRET
 });
 ```

### Python/Django

1. Install dependencies:
 ```bash
 pip install auth0-python python-dotenv django-social-auth
 ```

2. Update Django settings:
 ```python
 from auth0_config import Auth0Config

 AUTH0_DOMAIN = Auth0Config.DOMAIN
 AUTH0_CLIENT_ID = Auth0Config.CLIENT_ID
 ```

3. Add OIDC backend:
 ```python
 AUTHENTICATION_BACKENDS = [
 'social_core.backends.open_id_connect.OpenIdConnectAuth',
 ]
 ```

### Go

1. Get dependencies:
 ```bash
 go get github.com/joho/godotenv
 go get golang.org/x/oauth2
 ```

2. Load configuration:
 ```go
 cfg := config.LoadAuth0Config()
 provider := auth.NewAuth0Provider(cfg)
 ```

3. Implement login:
 ```go
 loginURL := provider.GetLoginURL(state)
 // Redirect user to loginURL
 ```

### Java/Spring Boot

1. Add Maven dependencies from `POM_AUTH0_SNIPPET.xml`

2. Update `application.properties`:
 ```properties
 spring.security.oauth2.client.registration.auth0.client-id=YOUR_CLIENT_ID
 spring.security.oauth2.client.provider.auth0.issuer-uri=https://YOUR_DOMAIN/
 ```

3. Create security configuration:
 ```java
 @Configuration
 public class SecurityConfiguration {
 @Bean
 public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
 http.oauth2Login()
 .and()
 .authorizeRequests()
 .anyRequest().authenticated();
 return http.build();
 }
 }
 ```

## Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `AUTH0_DOMAIN` | Auth0 tenant domain | `acme-corp.auth0.com` |
| `AUTH0_CLIENT_ID` | Application client ID | `abc123xyz...` |
| `AUTH0_CLIENT_SECRET` | Application client secret | `xyz789abc...` |
| `AUTH0_AUDIENCE` | API audience URI | `https://acme-corp.auth0.com/api/v2/` |
| `APP_NAME` | Application name | `my-app` |
| `APP_ENV` | Environment | `production` |

## Troubleshooting

### ".env file not found"
- Check `app_env_path` variable is set correctly
- Verify application user has read permissions: `ls -la {{ app_env_path }}`
- Ensure application runs with correct user context

### "Auth0 credentials not loaded"
- Verify .env file exists and is readable
- Check application loads dotenv at startup
- Ensure AUTH0_DOMAIN is set (required for API calls)
- Test with: `grep AUTH0 {{ app_env_path }}`

### "Permission denied" on .env
- .env file should not be world-readable (contains secrets)
- Default permissions: 0640 (owner/group read, others denied)
- Update if needed: `chmod 640 {{ app_env_path }}`

### Framework-specific config not created
- Verify `app_framework` variable is set to correct value
- Check supported frameworks: nodejs, python, django, go, java
- Review role output for framework-specific tasks

### Client secret exposure
- **Never commit .env to git** - add to .gitignore
- Use Ansible Vault for secrets in playbooks
- Rotate client secrets regularly in Auth0 dashboard
- Restrict file permissions to necessary users only

## Security Considerations

1. **Protect .env files**
 - Set permissions to 0640 (owner/group readable only)
 - Don't commit to version control
 - Add to .gitignore: `echo '.env' >> .gitignore`

2. **Rotate credentials regularly**
 - Generate new client secrets in Auth0 dashboard
 - Update .env files on applications
 - Revoke old secrets after verification

3. **Use Ansible Vault**
 ```bash
 # Store secrets securely
 ansible-vault create group_vars/all/auth0_secrets.yml
 ```

4. **Limit credential scope**
 - Auth0 client should only have needed permissions
 - Use different clients for different apps
 - Regular audit of client access logs

5. **Encrypt in transit**
 - Use HTTPS for all Auth0 API calls (automatic)
 - Use SSH for Ansible connections
 - Enable TLS on application endpoints

## Limitations

- Requires Auth0 role to be executed first
- Application framework must be installed on target system
- Configuration files are templates (may need adjustment)
- Secrets stored in .env are readable by application user
- MFA and advanced Auth0 features require additional setup

## Next Steps

1. **Generate Auth0 credentials** using the auth0 role
2. **Apply this role** to configure applications
3. **Implement login flows** using generated config examples
4. **Test OAuth2 flow** (login, token exchange, user info)
5. **Deploy application** with configured Auth0 integration
6. **Monitor Auth0 logs** for authentication issues

## Related Documentation

- [Auth0 Role](../auth0/README.md) - Generate Auth0 credentials
- [Auth0 Documentation](https://auth0.com/docs)
- [Auth0 Python SDK](https://github.com/auth0/auth0-python)
- [OAuth2 & OIDC](https://auth0.com/docs/get-started/authentication-and-authorization)

---

**Status**: Ready for Use | **Last Updated**: {{ ansible_date_time.iso8601 }}
