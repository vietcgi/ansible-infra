# Headscale Control Server Role

Ansible role for deploying [Headscale](https://github.com/juanfont/headscale) - a self-hosted, open-source implementation of the Tailscale control server.

## Overview

Headscale allows you to run your own Tailscale control server, giving you full control over your mesh VPN network without relying on Tailscale's cloud service. This role deploys Headscale via Docker with optional [Headplane](https://github.com/tale/headplane) web UI.

### Features

- **Docker-based deployment** - Easy installation and updates
- **Headplane Web UI** - Optional web interface for management
- **SQLite or PostgreSQL** - Flexible database options
- **OIDC/SSO support** - Integrate with identity providers
- **Let's Encrypt** - Automatic TLS certificate management
- **ACL policies** - Fine-grained access control
- **MagicDNS** - Automatic DNS for your tailnet
- **Prometheus metrics** - Built-in monitoring support

## Requirements

- Ubuntu 20.04+ or Debian 11+
- Docker and Docker Compose v2 installed
- A domain name pointing to your server
- Ports 8080 (API), 9090 (metrics), 3000 (Headplane UI) available

### Dependencies

This role requires Docker to be installed. Use the `common` role with Docker enabled:

```yaml
- hosts: headscale_servers
  roles:
    - role: common
      vars:
        container_docker_enabled: true
    - role: headscale
```

## Quick Start

### Minimal Configuration

```yaml
# host_vars/headscale.example.com.yml
headscale_domain: "headscale.example.com"
headscale_server_url: "https://headscale.example.com"
headplane_cookie_secret: "your-32-character-secret-here!!"  # Generate: openssl rand -hex 16
```

### Run the Playbook

```bash
uv run ansible-playbook playbooks/deploy-headscale.yml -l headscale_servers
```

## Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `headscale_domain` | Domain for Headscale server | `headscale.example.com` |
| `headscale_server_url` | Public URL for clients | `https://headscale.example.com` |
| `headplane_cookie_secret` | 32+ char secret for Headplane | Generate with `openssl rand -hex 16` |

### Core Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `headscale_enabled` | `true` | Enable/disable the role |
| `headscale_version` | `0.27.1` | Headscale version to deploy |
| `headscale_state` | `present` | `present` or `absent` |
| `headscale_port` | `8080` | API listen port |
| `headscale_metrics_port` | `9090` | Prometheus metrics port |
| `headscale_grpc_port` | `50443` | gRPC port |

### Database Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `headscale_database_type` | `sqlite` | `sqlite` or `postgres` |
| `headscale_sqlite_path` | `/var/lib/headscale/db.sqlite` | SQLite database path |
| `headscale_postgres_host` | `localhost` | PostgreSQL host |
| `headscale_postgres_port` | `5432` | PostgreSQL port |
| `headscale_postgres_name` | `headscale` | Database name |
| `headscale_postgres_user` | `headscale` | Database user |
| `headscale_postgres_password` | `""` | Database password |

### TLS Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `headscale_tls_enabled` | `false` | Enable TLS |
| `headscale_tls_mode` | `letsencrypt` | `letsencrypt` or `manual` |
| `headscale_acme_email` | `""` | Email for Let's Encrypt |
| `headscale_tls_cert_path` | `""` | Path to certificate (manual mode) |
| `headscale_tls_key_path` | `""` | Path to private key (manual mode) |

### DNS Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `headscale_dns_enabled` | `true` | Enable DNS features |
| `headscale_dns_magic_enabled` | `true` | Enable MagicDNS |
| `headscale_dns_base_domain` | `tail.net` | Base domain for MagicDNS |
| `headscale_dns_nameservers_global` | `["1.1.1.1", "8.8.8.8"]` | Global DNS servers |

### OIDC Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `headscale_oidc_enabled` | `false` | Enable OIDC authentication |
| `headscale_oidc_issuer` | `""` | OIDC issuer URL |
| `headscale_oidc_client_id` | `""` | OIDC client ID |
| `headscale_oidc_client_secret` | `""` | OIDC client secret |
| `headscale_oidc_allowed_domains` | `[]` | Allowed email domains |

### Headplane Web UI

| Variable | Default | Description |
|----------|---------|-------------|
| `headplane_enabled` | `true` | Enable Headplane web UI |
| `headplane_port` | `3000` | Headplane listen port |
| `headplane_cookie_secret` | `""` | Cookie secret (required, 32+ chars) |

## Example Configurations

### Basic Setup with Headplane UI

```yaml
headscale_domain: "vpn.mycompany.com"
headscale_server_url: "https://vpn.mycompany.com"
headplane_enabled: true
headplane_cookie_secret: "{{ lookup('password', '/dev/null chars=hexdigits length=32') }}"

# Pre-create users
headscale_users:
  - "admin"
  - "developers"
  - "servers"
```

### With OIDC (Google)

```yaml
headscale_domain: "vpn.mycompany.com"
headscale_server_url: "https://vpn.mycompany.com"

headscale_oidc_enabled: true
headscale_oidc_issuer: "https://accounts.google.com"
headscale_oidc_client_id: "your-client-id.apps.googleusercontent.com"
headscale_oidc_client_secret: "{{ vault_headscale_oidc_secret }}"
headscale_oidc_allowed_domains:
  - "mycompany.com"
```

### With PostgreSQL

```yaml
headscale_domain: "vpn.mycompany.com"
headscale_server_url: "https://vpn.mycompany.com"

headscale_database_type: "postgres"
headscale_postgres_host: "db.internal"
headscale_postgres_port: 5432
headscale_postgres_name: "headscale"
headscale_postgres_user: "headscale"
headscale_postgres_password: "{{ vault_headscale_db_password }}"
```

### With Let's Encrypt TLS

```yaml
headscale_domain: "vpn.mycompany.com"
headscale_server_url: "https://vpn.mycompany.com"

headscale_tls_enabled: true
headscale_tls_mode: "letsencrypt"
headscale_acme_email: "admin@mycompany.com"
```

### ACL Policy Example

```yaml
headscale_acl_policy:
  hosts:
    server1: "100.64.0.1"
  groups:
    "group:admin":
      - "admin@mycompany.com"
    "group:dev":
      - "dev@mycompany.com"
  tagOwners:
    "tag:server":
      - "group:admin"
  acls:
    # Admins can access everything
    - action: "accept"
      src:
        - "group:admin"
      dst:
        - "*:*"
    # Developers can access servers on specific ports
    - action: "accept"
      src:
        - "group:dev"
      dst:
        - "tag:server:22,80,443"
```

## Usage

### Connecting Clients

After deployment, connect Tailscale clients to your Headscale server:

```bash
# Create a user
docker exec headscale headscale users create myuser

# Create a pre-auth key
docker exec headscale headscale preauthkeys create --user myuser --expiration 24h

# On the client machine
tailscale up --login-server https://vpn.mycompany.com --authkey <YOUR_KEY>
```

### Headplane Web UI

1. Access Headplane at `http://your-server:3000/admin`
2. Generate an API key:
   ```bash
   docker exec headscale headscale apikeys create --expiration 90d
   ```
3. Use the API key to log in

### Common Commands

```bash
# List users
docker exec headscale headscale users list

# List nodes
docker exec headscale headscale nodes list

# Create API key
docker exec headscale headscale apikeys create --expiration 90d

# Register a node manually
docker exec headscale headscale nodes register --user myuser --key nodekey:abc123...

# Delete a node
docker exec headscale headscale nodes delete -i <node-id>
```

## Monitoring

Prometheus metrics are available at `http://your-server:9090/metrics`.

Example Prometheus scrape config:

```yaml
scrape_configs:
  - job_name: 'headscale'
    static_configs:
      - targets: ['headscale.example.com:9090']
```

## Backup

Enable automatic backups:

```yaml
headscale_backup_enabled: true
headscale_backup_dir: "/var/backups/headscale"
headscale_backup_schedule: "0 3 * * *"  # Daily at 3 AM
headscale_backup_retention_days: 30
```

Manual backup:

```bash
# Stop the container (for SQLite)
docker stop headscale

# Copy the data directory
cp -r /opt/headscale/data /backup/headscale-$(date +%Y%m%d)

# Restart
docker start headscale
```

## Troubleshooting

### Check container logs

```bash
docker logs headscale
docker logs headplane
```

### Verify configuration

```bash
docker exec headscale headscale configtest
```

### Health check

```bash
curl http://localhost:8080/health
```

### Common Issues

1. **"connection refused" from clients**
   - Ensure `headscale_server_url` matches your public URL
   - Check firewall allows port 8080

2. **Headplane can't connect**
   - Verify Docker socket is mounted
   - Check Headscale is healthy first

3. **OIDC login fails**
   - Verify redirect URI in your identity provider matches `{server_url}/oidc/callback`

## Directory Structure

```
/opt/headscale/
├── config/
│   ├── config.yaml      # Headscale configuration
│   ├── acl.json         # ACL policy
│   └── headplane.yaml   # Headplane configuration
├── data/
│   └── db.sqlite        # SQLite database
├── run/                 # Runtime files
├── headplane/           # Headplane data
└── docker-compose.yml   # Docker Compose file
```

## Infisical Secret Management (Optional)

This role supports Infisical for centralized secret management. Enable it to retrieve secrets from Infisical instead of providing them directly:

```yaml
headscale_infisical_enabled: true
headscale_infisical_project_id: "your-project-id"
headscale_infisical_env: "prod"
headscale_infisical_path: "/headscale"
```

Secrets retrieved from Infisical:
- `HEADSCALE_OIDC_CLIENT_SECRET` → `headscale_oidc_client_secret`
- `HEADSCALE_POSTGRES_PASSWORD` → `headscale_postgres_password`
- `HEADPLANE_COOKIE_SECRET` → `headplane_cookie_secret`

## Handler Naming Convention

This role follows [geerlingguy's handler patterns](https://github.com/geerlingguy/ansible-role-docker) using lowercase `[action] [service]` naming:
- `restart headscale`
- `restart headplane`
- `restart headscale stack`
- `validate headscale config`

## References

- [Headscale Documentation](https://headscale.net/)
- [Headscale GitHub](https://github.com/juanfont/headscale)
- [Headplane GitHub](https://github.com/tale/headplane)
- [Tailscale Documentation](https://tailscale.com/kb/)
