# Example Client: Python/Django Application

This is a complete working example of a client configuration for deploying Python/Django applications with Auth0 integration.

## What This Shows

- Complete client directory structure for Python apps
- Django application configuration with OIDC
- Auth0 setup for OIDC authentication
- Database and Redis configuration
- Production-ready settings
- Multiple environment support

## Quick Start

1. **Copy to your project**:
   ```bash
   cp -r inventories/projects/example-client-python \
         inventories/projects/mycompany
   ```

2. **Update server IPs** in `hosts.yml`

3. **Create vault**:
   ```bash
   ansible-vault create auth0_vault.yml
   ```

4. **Customize configuration** in `group_vars/all.yml`

5. **Deploy**:
   ```bash
   ansible-playbook ../../playbooks/client_onboarding.yml \
     -i hosts.yml --ask-vault-pass
   ```

## Configuration Features

- **Framework**: Python/Django
- **Auth0**: OIDC integration
- **Database**: PostgreSQL connection  
- **Cache**: Redis
- **Environment**: Production

## Django Integration

After deployment, configure Django:

```python
# settings.py
from auth0_config import Auth0Config

AUTH0_DOMAIN = Auth0Config.DOMAIN
AUTH0_CLIENT_ID = Auth0Config.CLIENT_ID

AUTHENTICATION_BACKENDS = [
    'social_core.backends.open_id_connect.OpenIdConnectAuth',
]
```

## Documentation

See [example-client-nodejs/README.md](../example-client-nodejs/README.md) for detailed examples - the process is the same, only the framework differs.

---

**Status**: Example / Template  
**Framework**: Python/Django
**Last Updated**: November 16, 2025
