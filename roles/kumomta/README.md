# KumoMTA Email Delivery Role

This Ansible role deploys and configures [KumoMTA](https://github.com/kumocorp/kumomta), a modern, high-performance email delivery engine written in Rust. KumoMTA provides SMTP server capabilities with advanced queue management, bounce handling, and observability features.

## Features

- **Binary Installation**: Downloads and verifies KumoMTA binary from GitHub releases
- **TLS Support**: Automatic self-signed certificate generation with DKIM support
- **Queue Management**: Configurable retry strategies with exponential backoff
- **Bounce & FBL Handling**: Automatic bounce detection and feedback loop processing
- **Monitoring**: Prometheus metrics export and Grafana dashboard integration
- **Clustering**: Multi-node cluster support with peer discovery and consensus
- **Backup & Retention**: Automated backup with restore capabilities
- **Systemd Integration**: Socket activation and service management
- **Rate Limiting**: Per-source IP and per-domain connection limits
- **Policy Engine**: Lua-based policy scripting for advanced routing rules

## Requirements

- Ubuntu 20.04 or later (Debian-based)
- Ansible 2.9+
- At least 2GB RAM and 1GB disk space
- Root or sudo access

## Role Variables

### Installation Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `kumomta_enabled` | `true` | Enable KumoMTA deployment |
| `kumomta_version` | `1.1.2` | KumoMTA release version |
| `kumomta_user` | `kumomta` | System user for KumoMTA |
| `kumomta_group` | `kumomta` | System group for KumoMTA |
| `kumomta_home` | `/opt/kumomta` | Installation directory |
| `kumomta_config_dir` | `/etc/kumomta` | Configuration directory |
| `kumomta_queue_dir` | `/var/spool/kumomta` | Queue directory |
| `kumomta_log_dir` | `/var/log/kumomta` | Log directory |

### Network Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `kumomta_hostname` | `{{ ansible_fqdn }}` | Server hostname |
| `kumomta_listen_port` | `25` | SMTP port |
| `kumomta_submit_port` | `587` | Submission port |
| `kumomta_tls_port` | `465` | SMTPS port |
| `kumomta_admin_port` | `8008` | Admin API port |
| `kumomta_metrics_port` | `9184` | Prometheus metrics port |

### Queue Management

| Variable | Default | Description |
|----------|---------|-------------|
| `kumomta_queue_strategy` | `exponential_backoff` | Retry strategy |
| `kumomta_queue_retry_interval` | `300` | Initial retry interval (seconds) |
| `kumomta_queue_max_attempts` | `20` | Maximum retry attempts |
| `kumomta_queue_expiration` | `86400` | Message expiration time (seconds) |
| `kumomta_worker_threads` | `4` | Queue worker thread count |

### Security & TLS

| Variable | Default | Description |
|----------|---------|-------------|
| `kumomta_tls_enabled` | `true` | Enable TLS support |
| `kumomta_tls_certificate` | `/etc/kumomta/certs/cert.pem` | Certificate path |
| `kumomta_tls_key` | `/etc/kumomta/certs/key.pem` | Private key path |
| `kumomta_dkim_enabled` | `true` | Enable DKIM signing |
| `kumomta_dkim_key` | `/etc/kumomta/dkim/private.pem` | DKIM key path |
| `kumomta_dkim_selector` | `default` | DKIM selector |

### Rate Limiting

| Variable | Default | Description |
|----------|---------|-------------|
| `kumomta_rate_limit_count` | `100` | Connections per window per IP |
| `kumomta_rate_limit_window` | `3600` | Rate limit window (seconds) |
| `kumomta_max_connections` | `1000` | Max concurrent connections |
| `kumomta_max_concurrent_connections_per_domain` | `50` | Per-domain connection limit |
| `kumomta_submission_max_connections` | `500` | Submission port max connections |
| `kumomta_max_message_size` | `52428800` | Max message size (50MB) |

### Monitoring & Observability

| Variable | Default | Description |
|----------|---------|-------------|
| `kumomta_monitoring_enabled` | `true` | Enable monitoring |
| `kumomta_metrics_enabled` | `true` | Enable Prometheus metrics |
| `kumomta_metrics_port` | `9184` | Metrics export port |
| `kumomta_metrics_scrape_interval` | `15s` | Prometheus scrape interval |
| `kumomta_syslog_enabled` | `true` | Enable syslog forwarding |
| `kumomta_log_level` | `info` | Logging level |
| `kumomta_log_format` | `json` | Log format (json or text) |
| `kumomta_log_rotation_size` | `100M` | Log rotation size |
| `kumomta_log_retention_days` | `30` | Log retention days |

### Bounce & FBL Handling

| Variable | Default | Description |
|----------|---------|-------------|
| `kumomta_bounce_handling_enabled` | `true` | Enable bounce handling |
| `kumomta_bounce_dir` | `/var/lib/kumomta/bounces` | Bounce directory |
| `kumomta_bounce_notify_sender` | `true` | Notify sender of bounces |
| `kumomta_fbl_enabled` | `true` | Enable FBL processing |
| `kumomta_fbl_dir` | `/var/lib/kumomta/fbl` | FBL directory |

### Clustering

| Variable | Default | Description |
|----------|---------|-------------|
| `kumomta_clustering_enabled` | `false` | Enable clustering |
| `kumomta_cluster_peers` | `[]` | List of cluster peer addresses |
| `kumomta_cluster_consensus_port` | `9100` | Consensus protocol port |
| `kumomta_cluster_data_port` | `9101` | Data replication port |

### Backup & Retention

| Variable | Default | Description |
|----------|---------|-------------|
| `kumomta_backup_enabled` | `true` | Enable automated backups |
| `kumomta_backup_dir` | `/var/backups/kumomta` | Backup directory |
| `kumomta_backup_hour` | `2` | Backup cron hour |
| `kumomta_backup_minute` | `0` | Backup cron minute |
| `kumomta_remote_backup_enabled` | `false` | Enable remote backups |
| `kumomta_remote_backup_host` | `` | Remote backup host |

### Service Management

| Variable | Default | Description |
|----------|---------|-------------|
| `kumomta_service_enabled` | `true` | Enable service on boot |
| `kumomta_service_state` | `started` | Service state |
| `kumomta_cpu_quota` | `100%` | CPU quota limit |
| `kumomta_memory_limit` | `2G` | Memory limit |

### Policy Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `kumomta_suppressed_domains` | `[]` | List of suppressed recipient domains |
| `kumomta_suppression_list_path` | `/etc/kumomta/suppression.txt` | Suppression list file |

## Usage

### Basic Deployment

Include the role in your playbook:

```yaml
- hosts: mail_servers
  roles:
    - kumomta
```

### Single Node with Custom Configuration

```yaml
- hosts: mail.example.com
  vars:
    kumomta_hostname: mail.example.com
    kumomta_listen_port: 25
    kumomta_submit_port: 587
    kumomta_tls_enabled: true
    kumomta_dkim_enabled: true
    kumomta_monitoring_enabled: true
  roles:
    - kumomta
```

### Cluster Deployment

```yaml
- hosts: mail_cluster
  vars:
    kumomta_clustering_enabled: true
    kumomta_cluster_peers:
      - mail1.example.com:9100
      - mail2.example.com:9100
      - mail3.example.com:9100
  roles:
    - kumomta
```

### With Custom Suppression List

```yaml
- hosts: mail_servers
  vars:
    kumomta_bounce_handling_enabled: true
    kumomta_suppressed_domains:
      - example.com
      - test.local
    kumomta_suppression_list_path: /etc/kumomta/custom-suppression.txt
  roles:
    - kumomta
```

## Directory Structure

```
roles/kumomta/
├── defaults/
│   └── main.yml              # Default variables
├── handlers/
│   └── main.yml              # Service handlers
├── tasks/
│   ├── main.yml              # Main orchestration
│   ├── install.yml           # Binary installation
│   ├── certificates.yml      # TLS/DKIM certificate generation
│   ├── configure.yml         # Configuration templating
│   ├── service.yml           # Systemd integration
│   ├── monitoring.yml        # Prometheus/Grafana setup
│   ├── bounce_handling.yml   # Bounce and FBL handling
│   ├── clustering.yml        # Cluster configuration
│   ├── backup.yml            # Backup and retention
│   └── validation.yml        # Health checks
├── templates/
│   ├── kumomta.conf.j2       # Main configuration
│   ├── policy.lua.j2         # Policy scripting
│   ├── queue.lua.j2          # Queue management
│   ├── logging.toml.j2       # Logging configuration
│   ├── kumomta.service.j2    # Systemd service
│   ├── kumomta-submission.socket.j2  # Socket activation
│   ├── bounce-policy.lua.j2  # Bounce handling
│   ├── kumomta-logrotate.j2  # Log rotation
│   └── rsyslog-kumomta.conf.j2 # Syslog configuration
└── README.md                 # This file
```

## Post-Deployment

### Verify Installation

```bash
# Check service status
systemctl status kumomta.service

# Check if listening on ports
netstat -tlnp | grep kumomta

# View logs
journalctl -u kumomta.service -f

# Validate configuration
/opt/kumomta/kumomta --validate-config /etc/kumomta/kumomta.conf
```

### Monitor Service

View metrics on Prometheus:
```
http://your-server:{{ kumomta_metrics_port }}/metrics
```

### Configure Email Routing

Edit `/etc/kumomta/policy.lua` to customize:
- Rate limiting rules
- Recipient validation
- Domain-specific routing
- Message filtering

### Backup Queue Data

Manually trigger backup:
```bash
/var/backups/kumomta/backup.sh
```

## Clustering Operations

### Setting Up a Cluster

1. Configure cluster peers on all nodes:
```yaml
kumomta_clustering_enabled: true
kumomta_cluster_peers:
  - "mail1.example.com:9100"
  - "mail2.example.com:9100"
  - "mail3.example.com:9100"
```

2. Ensure cluster ports are open between nodes:
```bash
# Open ports 9100 (consensus) and 9101 (data) for inter-node communication
firewall-cmd --add-port=9100/tcp --permanent
firewall-cmd --add-port=9101/tcp --permanent
```

3. Run cluster join script:
```bash
/etc/kumomta/cluster-join.sh
```

### Troubleshooting Cluster Issues

Check peer connectivity:
```bash
/etc/kumomta/cluster-health-check.sh
```

Monitor cluster status:
```bash
curl -s http://localhost:8008/api/cluster/status | jq
```

### Handling Cluster Node Failures

If a node goes down:
1. Fix the issue on the failed node
2. Restart KumoMTA: `systemctl restart kumomta`
3. Cluster will automatically resync from healthy peers
4. Monitor progress: `tail -f /var/log/kumomta/cluster.log`

## Backup and Recovery

### Automated Backups

Backups run automatically via cron. To verify:
```bash
ls -lh /var/backups/kumomta/backup-*.tar.gz
```

### Manual Backup

```bash
/var/backups/kumomta/kumomta-backup.sh
```

### Restore from Backup

```bash
# Stop the service
systemctl stop kumomta.service

# Restore from backup
/var/backups/kumomta/kumomta-restore.sh /var/backups/kumomta/backup-20231201-020000.tar.gz

# Restart the service
systemctl start kumomta.service

# Verify restoration
systemctl status kumomta.service
```

### Remote Backups

Enable remote backups in variables:
```yaml
kumomta_remote_backup_enabled: true
kumomta_remote_backup_host: "backup.example.com"
kumomta_remote_backup_port: 22
kumomta_remote_backup_protocol: "sftp"
kumomta_remote_backup_path: "/backups/kumomta"
```

## Certificate Renewal

### Self-Signed Certificates

Renewal happens automatically before expiration. To force renewal:
```bash
ansible-playbook playbooks/kumomta-renew-certs.yml
```

### Using Custom Certificates

1. Place your certificate and key files in:
   - Certificate: `/etc/kumomta/certs/kumomta.crt`
   - Key: `/etc/kumomta/certs/kumomta.key`

2. Update variables:
```yaml
kumomta_tls_certificate: "/etc/kumomta/certs/kumomta.crt"
kumomta_tls_key: "/etc/kumomta/certs/kumomta.key"
```

3. Reload configuration:
```bash
systemctl reload kumomta.service
```

## Troubleshooting

### Service fails to start

Check configuration:
```bash
/opt/kumomta/kumomta --validate-config /etc/kumomta/kumomta.conf
```

Check logs:
```bash
journalctl -u kumomta.service -n 50
```

Check for port conflicts:
```bash
ss -tlnp | grep -E ":(25|587|465|8008|9184)"
```

### High CPU Usage

Adjust worker threads in variables:
```yaml
kumomta_worker_threads: 8  # Increase from default 4
```

### Disk Space Issues

Check queue directory:
```bash
du -sh /var/spool/kumomta
```

Reduce retention or increase backup frequency if queue grows.

### Certificate Issues

Regenerate certificates:
```bash
ansible-playbook playbooks/kumomta-renew-certs.yml
```

## Performance Tuning

### For High-Volume Deployments

```yaml
kumomta_worker_threads: 16
kumomta_max_connections: 5000
kumomta_max_concurrent_connections_per_domain: 200
kumomta_memory_limit: "8G"
kumomta_queue_strategy: "aggressive_retries"
```

### For Resource-Constrained Systems

```yaml
kumomta_worker_threads: 2
kumomta_max_connections: 500
kumomta_submission_max_connections: 100
kumomta_memory_limit: "512M"
```

## Security Considerations

1. **TLS Certificates**: Replace self-signed certificates with valid CA-signed certificates in production
2. **DKIM Keys**: Protect DKIM private keys with proper file permissions (mode 0600)
3. **Authentication**: Configure authentication for the submission port (587)
4. **Firewall**: Only allow SMTP ports from trusted networks
5. **Suppression Lists**: Maintain and regularly update suppression/blacklist files
6. **Backup Security**: Encrypt backups if stored remotely

## Support and Documentation

- [KumoMTA GitHub Repository](https://github.com/kumocorp/kumomta)
- [KumoMTA Official Documentation](https://kumocorp.com/docs)
- [Ansible Role Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html)

## License

This Ansible role is provided as-is. KumoMTA is licensed under the Elastic License 2.0.
