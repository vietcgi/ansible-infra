# KumoMTA Deployment Guide

Complete guide for deploying KumoMTA using the Ansible role in this infrastructure framework.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Single Node Deployment](#single-node-deployment)
4. [Cluster Deployment](#cluster-deployment)
5. [Post-Deployment Configuration](#post-deployment-configuration)
6. [Monitoring & Observability](#monitoring--observability)
7. [Troubleshooting](#troubleshooting)
8. [Backup & Recovery](#backup--recovery)

## Prerequisites

### System Requirements

- Ubuntu 20.04 LTS or later
- Minimum 2GB RAM, 1GB free disk space
- Root or sudo access
- Python 3.8+ installed

### Network Requirements

- SMTP Port 25 accessible (for receiving mail)
- Submission Port 587 accessible (for authenticated sending)
- SMTPS Port 465 optional (for TLS-wrapped SMTP)
- Metrics Port 9184 for Prometheus scraping
- Cluster ports 9100-9101 (for clustering)

### DNS Requirements

Prepare the following DNS records:

```
mail.example.com A    203.0.113.1
                 AAAA 2001:db8::1

SPF:  v=spf1 mx ~all
DKIM: selector._domainkey.example.com TXT "v=DKIM1; k=rsa; p=..."
```

## Quick Start

### 1. Update Inventory

Add hosts to `inventory/hosts`:

```ini
[kumomta_servers]
mail1.example.com

[kumomta_cluster]
mail1.example.com
mail2.example.com
mail3.example.com
```

### 2. Run Deployment

For single node:
```bash
ansible-playbook playbooks/deploy-kumomta-single-node.yml -i inventory/hosts
```

For cluster:
```bash
ansible-playbook playbooks/deploy-kumomta-cluster.yml -i inventory/hosts
```

### 3. Validate Deployment

```bash
ansible-playbook playbooks/kumomta-validation.yml -i inventory/hosts
```

## Single Node Deployment

### Configuration Example

Create `group_vars/kumomta_servers.yml`:

```yaml
# KumoMTA Configuration
kumomta_hostname: "mail.example.com"
kumomta_version: "1.1.2"

# Network
kumomta_listen_port: 25
kumomta_submit_port: 587
kumomta_tls_port: 465
kumomta_admin_port: 8008
kumomta_metrics_port: 9184

# Security
kumomta_tls_enabled: true
kumomta_dkim_enabled: true
kumomta_dkim_selector: "default"

# Performance
kumomta_worker_threads: 4
kumomta_max_connections: 1000
kumomta_max_concurrent_connections_per_domain: 50

# Queue
kumomta_queue_strategy: "exponential_backoff"
kumomta_queue_retry_interval: 300
kumomta_queue_max_attempts: 20
kumomta_queue_expiration: 86400

# Monitoring
kumomta_monitoring_enabled: true
kumomta_metrics_enabled: true
kumomta_syslog_enabled: true
kumomta_log_level: "info"

# Features
kumomta_bounce_handling_enabled: true
kumomta_fbl_enabled: true
kumomta_backup_enabled: true

# Suppression
kumomta_suppressed_domains:
  - noreply.example.com
  - test.local
```

### Deployment Steps

```bash
# 1. Syntax check
ansible-playbook playbooks/deploy-kumomta-single-node.yml -i inventory/hosts --syntax-check

# 2. Dry run
ansible-playbook playbooks/deploy-kumomta-single-node.yml -i inventory/hosts -C

# 3. Deploy
ansible-playbook playbooks/deploy-kumomta-single-node.yml -i inventory/hosts

# 4. Verify
ssh mail.example.com
systemctl status kumomta.service
/opt/kumomta/kumomta --version
journalctl -u kumomta.service -n 20
```

### Post-Deployment Checks

```bash
# Check service
systemctl status kumomta.service

# Check ports
netstat -tlnp | grep kumomta

# Check configuration
/opt/kumomta/kumomta --validate-config /etc/kumomta/kumomta.conf

# View metrics
curl http://localhost:9184/metrics | head -20

# Check logs
journalctl -u kumomta.service -f
```

## Cluster Deployment

### Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   mail1     │     │   mail2     │     │   mail3     │
│  kumomta    │────▶│  kumomta    │────▶│  kumomta    │
│  (primary)  │     │ (secondary) │     │ (secondary) │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  Load Balancer │
                    │   (optional)   │
                    └────────────────┘
```

### Configuration Example

Create `group_vars/kumomta_cluster.yml`:

```yaml
# Clustering
kumomta_clustering_enabled: true
kumomta_cluster_peers:
  - mail1.example.com:9100
  - mail2.example.com:9100
  - mail3.example.com:9100
kumomta_cluster_consensus_port: 9100
kumomta_cluster_data_port: 9101

# Higher performance for cluster
kumomta_worker_threads: 8
kumomta_max_connections: 5000
kumomta_max_concurrent_connections_per_domain: 200
kumomta_memory_limit: "4G"

# Aggressive retry strategy for cluster
kumomta_queue_strategy: "aggressive_retries"

# Enhanced monitoring
kumomta_monitoring_enabled: true
kumomta_metrics_enabled: true
kumomta_grafana_enabled: true

# Remote backup for cluster
kumomta_backup_enabled: true
kumomta_remote_backup_enabled: true
kumomta_remote_backup_host: "backup.example.com"
```

### Cluster Deployment Steps

```bash
# 1. Deploy all nodes
ansible-playbook playbooks/deploy-kumomta-cluster.yml -i inventory/hosts

# 2. Verify cluster status
ansible kumomta_cluster -i inventory/hosts -m command \
  -a "curl -s http://localhost:8008/cluster/status"

# 3. Check cluster consensus
ssh mail1.example.com
journalctl -u kumomta.service -g "cluster"
```

### Load Balancer Configuration

For HAProxy:

```haproxy
global
    log stdout local0
    maxconn 4096

defaults
    log     global
    mode    tcp
    option  tcplog
    timeout connect 5000ms
    timeout client  50000ms
    timeout server  50000ms

frontend smtp_in
    bind *:25
    default_backend smtp_backend

backend smtp_backend
    balance roundrobin
    server mail1 mail1.example.com:25 check
    server mail2 mail2.example.com:25 check
    server mail3 mail3.example.com:25 check

frontend submission_in
    bind *:587
    default_backend submission_backend

backend submission_backend
    balance roundrobin
    server mail1 mail1.example.com:587 check
    server mail2 mail2.example.com:587 check
    server mail3 mail3.example.com:587 check
```

## Post-Deployment Configuration

### DNS Configuration

After deployment, obtain the DKIM public key:

```bash
# Extract DKIM public key
ssh mail.example.com
openssl rsa -in /etc/kumomta/dkim/private.pem -pubout -outform DER | \
  base64 | tr -d '\n'
```

Add DNS records:

```
SPF:  example.com TXT "v=spf1 mx -all"

DKIM: default._domainkey.example.com TXT \
  "v=DKIM1; k=rsa; p=YOUR_PUBLIC_KEY_HERE"

DMARC: _dmarc.example.com TXT \
  "v=DMARC1; p=quarantine; rua=mailto:admin@example.com"
```

### Firewall Configuration

```bash
# UFW
ufw allow 25/tcp comment "SMTP"
ufw allow 587/tcp comment "Submission"
ufw allow 465/tcp comment "SMTPS"
ufw allow 9184/tcp comment "Prometheus metrics"

# For cluster
ufw allow from <internal_network> to any port 9100 comment "Cluster consensus"
ufw allow from <internal_network> to any port 9101 comment "Cluster data"
```

## Monitoring & Observability

### Prometheus Integration

Create `/etc/prometheus/prometheus.yml` config:

```yaml
scrape_configs:
  - job_name: 'kumomta'
    static_configs:
      - targets: ['mail1.example.com:9184']

  # For cluster, add all nodes
  - job_name: 'kumomta-cluster'
    static_configs:
      - targets:
          - 'mail1.example.com:9184'
          - 'mail2.example.com:9184'
          - 'mail3.example.com:9184'
```

### Grafana Dashboards

Import dashboard from `roles/kumomta/templates/kumomta-grafana-dashboard.json.j2`

Key metrics to monitor:

- `kumomta_messages_sent_total` - Total messages sent
- `kumomta_queue_size` - Current queue size
- `kumomta_connections_active` - Active connections
- `kumomta_bounce_rate` - Bounce rate percentage
- `kumomta_delivery_time_seconds` - Average delivery time

### Log Monitoring

```bash
# Real-time logs
journalctl -u kumomta.service -f

# Error logs
journalctl -u kumomta.service -p err

# Specific time range
journalctl -u kumomta.service --since "2024-01-01" --until "2024-01-02"

# Syslog forwarding (if enabled)
tail -f /var/log/kumomta/kumomta-syslog.log
```

## Troubleshooting

### Service Won't Start

```bash
# Check configuration
/opt/kumomta/kumomta --validate-config /etc/kumomta/kumomta.conf

# Check logs
journalctl -u kumomta.service -n 50

# Check permissions
ls -la /etc/kumomta/
ls -la /var/spool/kumomta/

# Try manual start
/opt/kumomta/kumomta --config /etc/kumomta/kumomta.conf
```

### Port Already in Use

```bash
# Check what's using the port
netstat -tlnp | grep :25
lsof -i :25

# Stop conflicting service
systemctl stop postfix  # or other service
```

### High CPU Usage

```bash
# Check top processes
top -p $(pidof kumomta)

# Increase worker threads
# Edit group_vars and redeploy
kumomta_worker_threads: 8

# Check queue buildup
du -sh /var/spool/kumomta/
```

### Cluster Not Synchronizing

```bash
# Check cluster ports
netstat -tlnp | grep kumomta

# Verify peer connectivity
ping mail2.example.com
telnet mail2.example.com 9100

# Check cluster logs
journalctl -u kumomta.service -g cluster
```

## Backup & Recovery

### Automated Backups

Backups run daily at the configured time:

```yaml
kumomta_backup_hour: 2
kumomta_backup_minute: 0
```

Verify backups:

```bash
ls -la /var/backups/kumomta/
# Check backup size
du -sh /var/backups/kumomta/*
```

### Manual Backup

```bash
/var/backups/kumomta/backup.sh

# Verify backup integrity
/var/backups/kumomta/verify.sh
```

### Recovery Procedure

```bash
# 1. Stop service
systemctl stop kumomta.service

# 2. Backup current queue
cp -r /var/spool/kumomta /var/spool/kumomta.backup

# 3. Restore from backup
/var/backups/kumomta/restore.sh <backup_file>

# 4. Restart service
systemctl start kumomta.service

# 5. Verify restoration
/opt/kumomta/kumomta --validate-config /etc/kumomta/kumomta.conf
```

## Performance Tuning

### For High Volume (10K+ msgs/hour)

```yaml
kumomta_worker_threads: 16
kumomta_max_connections: 10000
kumomta_max_concurrent_connections_per_domain: 500
kumomta_memory_limit: "8G"
kumomta_cpu_quota: "200%"
```

### For Resource-Constrained

```yaml
kumomta_worker_threads: 2
kumomta_max_connections: 500
kumomta_submission_max_connections: 100
kumomta_memory_limit: "512M"
```

### Queue Tuning

```yaml
# Faster retries for transient failures
kumomta_queue_retry_interval: 60

# Longer TTL for messages
kumomta_queue_expiration: 172800  # 2 days

# More aggressive retry attempts
kumomta_queue_max_attempts: 30
```

## Support & Resources

- [KumoMTA Documentation](https://github.com/kumocorp/kumomta)
- [Ansible Documentation](https://docs.ansible.com)
- Infrastructure Repository: This repository
- Admin Portal: `http://mail.example.com:8008`
- Metrics: `http://mail.example.com:9184/metrics`

## Maintenance

### Regular Tasks

- **Weekly**: Review bounce rates and suppression lists
- **Monthly**: Check backup integrity and test recovery
- **Quarterly**: Update KumoMTA version, review performance metrics
- **Annually**: Full audit of configuration, TLS certificates, firewall rules

### Updates

To update KumoMTA:

```bash
# Change version
kumomta_version: "1.2.0"

# Redeploy
ansible-playbook playbooks/deploy-kumomta-single-node.yml

# Service should restart automatically
```
