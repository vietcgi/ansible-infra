# Prometheus Integration Guide

## Overview

Sentinel Infrastructure now includes the official **prometheus.prometheus** Ansible collection for comprehensive metrics collection and monitoring.

## Collections Used

### prometheus.prometheus (v0.14.0+)
Official Prometheus community collection with production-grade roles for:
- **prometheus**: Time-series metrics database
- **node_exporter**: System metrics collection
- **alertmanager**: Alert routing and management
- **pushgateway**: Short-lived job metrics

### grafana.grafana (v6.0.6+)
Official Grafana collection for:
- **grafana_agent**: Unified telemetry collection
- **loki**: Log aggregation
- **grafana**: Visualization and dashboarding

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Monitoring Stack                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Application Servers                                    │
│  ├─ Grafana Agent (metrics → Prometheus)               │
│  ├─ Node Exporter (system metrics)                      │
│  └─ Log forwarding → Loki                               │
│                                                         │
│  ↓↓↓                                                     │
│                                                         │
│  Prometheus (Time-Series DB)                            │
│  ├─ Scrapes metrics from agents                         │
│  ├─ Stores historical data (15 days default)            │
│  └─ Triggers alert rules                                │
│                                                         │
│  ↓↓↓                                                     │
│                                                         │
│  Grafana (Visualization)                                │
│  ├─ Queries Prometheus                                  │
│  ├─ Queries Loki (logs)                                 │
│  ├─ Creates dashboards                                  │
│  └─ Sends alerts                                        │
│                                                         │
│  ↓↓↓                                                     │
│                                                         │
│  Alertmanager (Alert Routing)                           │
│  ├─ Routes alerts based on rules                        │
│  ├─ Sends notifications (email, Slack, etc.)            │
│  └─ Manages silence periods                             │
│                                                         │
│  Loki (Log Aggregation)                                 │
│  ├─ Receives logs from all servers                      │
│  ├─ Stores with labels for querying                     │
│  └─ Integrates with Grafana                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Deployment

### 1. Install Collections

```bash
cd /Users/kevin/sentinel-infra
make install
# or
ansible-galaxy collection install -r requirements.yml
```

### 2. Configure Inventory

Edit `inventories/production/hosts.yml`:

```yaml
prometheus_servers:
  hosts:
    prometheus01.sentinel.local:
      ansible_host: 10.0.3.10

loki_servers:
  hosts:
    loki01.sentinel.local:
      ansible_host: 10.0.3.20

grafana_servers:
  hosts:
    grafana01.sentinel.local:
      ansible_host: 10.0.3.30
```

### 3. Run Configuration Playbook

```bash
# Deploy monitoring stack
ansible-playbook playbooks/configure.yml -i inventories/production/hosts.yml -v

# Or specific components
ansible-playbook playbooks/configure.yml -i inventories/production/hosts.yml --tags prometheus
ansible-playbook playbooks/configure.yml -i inventories/production/hosts.yml --tags grafana
```

## Component Details

### Prometheus

**Role**: `prometheus.prometheus.prometheus`

**Configuration**:
```yaml
prometheus_version: "2.48.0"
prometheus_listen_address: "0.0.0.0:9090"
prometheus_scrape_interval: "15s"
prometheus_evaluation_interval: "15s"
prometheus_retention_time: "15d"
```

**Features**:
- Multi-target scraping
- Alert rule evaluation
- Service discovery
- Data retention policies
- Remote storage integration

**Usage**:
```bash
# Access Prometheus UI
http://prometheus01.sentinel.local:9090

# Query metrics
curl http://prometheus01.sentinel.local:9090/api/v1/query?query=up
```

### Node Exporter

**Role**: `prometheus.prometheus.node_exporter`

**Installed on**: All non-disabled monitoring targets

**Metrics Collected**:
- CPU usage and time
- Memory utilization
- Disk I/O and space
- Network interfaces
- System load
- Process information
- Filesystem metrics
- Context switches

**Usage**:
```bash
# Verify node exporter running
systemctl status node_exporter

# Access metrics endpoint
curl http://localhost:9100/metrics
```

### Grafana Agent

**Role**: `grafana.grafana.grafana_agent`

**Responsibilities**:
- Scrapes local node exporter
- Sends metrics to Prometheus
- Ships logs to Loki
- Provides unified telemetry collection

**Configuration**:
- Runs as systemd service
- Includes service scrape configs
- Automatic service discovery

### Loki

**Role**: `grafana.grafana.loki`

**Features**:
- Log aggregation
- LogQL query language
- Label-based indexing
- Lightweight storage

**Integration**:
- Receives logs from all servers
- Queryable from Grafana
- Complements Prometheus metrics

### Grafana

**Role**: `grafana.grafana.grafana`

**Features**:
- Visualizations
- Dashboard management
- Alert configuration
- Multi-datasource support
- User management

**Default Credentials**:
```
URL: http://grafana01.sentinel.local:3000
Username: admin
Password: admin (CHANGE IMMEDIATELY!)
```

**Configure Datasources**:

1. Login to Grafana
2. Configuration → Data Sources
3. Add Prometheus:
   ```
   Name: Prometheus
   URL: http://prometheus01.sentinel.local:9090
   Default: Yes
   ```
4. Add Loki:
   ```
   Name: Loki
   URL: http://loki01.sentinel.local:3100
   ```

## Scrape Configurations

### Default Scrape Jobs

Prometheus automatically scrapes:

1. **node**: Node Exporter on all servers
   ```
   targets: [localhost:9100]
   ```

2. **grafana-agent**: Grafana Agent metrics
   ```
   targets: [localhost:12345]
   ```

3. **prometheus**: Prometheus self-monitoring
   ```
   targets: [localhost:9090]
   ```

### Adding Custom Scrape Jobs

Add to Prometheus config:

```yaml
scrape_configs:
  - job_name: 'custom-app'
    static_configs:
      - targets: ['localhost:8080']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: '{{ inventory_hostname }}'
```

## Alert Rules

### Default Alert Rules

Located in: `/etc/prometheus/rules.d/`

Example rules included:
- InstanceDown
- HighCPU
- HighMemory
- HighDiskUsage
- NodeExporterDown

### Creating Custom Alerts

Create file: `/etc/prometheus/rules.d/custom.yml`

```yaml
groups:
  - name: custom_alerts
    interval: 30s
    rules:
      - alert: CustomAlert
        expr: some_metric > 100
        for: 5m
        annotations:
          summary: "Custom alert triggered"
```

## Monitoring & Maintenance

### Service Status

```bash
# Prometheus
systemctl status prometheus

# Node Exporter
systemctl status node_exporter

# Grafana Agent
systemctl status grafana-agent

# Grafana
systemctl status grafana-server
```

### Viewing Logs

```bash
# Prometheus logs
journalctl -u prometheus -f

# Node Exporter logs
journalctl -u node_exporter -f

# Grafana logs
journalctl -u grafana-server -f
```

### Data Retention

Prometheus retains metrics for 15 days by default.

To modify:
```yaml
prometheus_retention_time: "30d"  # Change in inventory
```

Then redeploy:
```bash
ansible-playbook playbooks/configure.yml --tags prometheus
```

## Troubleshooting

### Prometheus Not Scraping

Check `/etc/prometheus/prometheus.yml`:
```bash
curl http://localhost:9090/api/v1/targets
```

### High Disk Usage

```bash
# Check Prometheus data directory
du -sh /var/lib/prometheus

# Reduce retention period
prometheus_retention_time: "7d"
```

### Grafana Not Connecting to Prometheus

1. Verify Prometheus running: `systemctl status prometheus`
2. Check firewall: `sudo ufw status`
3. Test connectivity: `curl http://prometheus:9090/api/v1/query?query=up`
4. Verify datasource URL in Grafana

### Node Exporter Missing Metrics

```bash
# Check which collectors are enabled
curl http://localhost:9100/metrics | grep -i collector

# Disable problematic collectors in node exporter config
node_exporter_disabled_collectors: ['hwmon', 'zoneinfo']
```

## Best Practices

1. **High Availability**
   - Run Prometheus with remote storage
   - Use Alertmanager for alert redundancy
   - Replicate Grafana across multiple nodes

2. **Security**
   - Restrict Prometheus to internal networks
   - Use reverse proxy with authentication
   - Rotate Grafana passwords regularly
   - Enable SSL/TLS for all connections

3. **Performance**
   - Set appropriate scrape intervals (15s for most cases)
   - Limit retention period (15d is default)
   - Use recording rules for complex queries
   - Monitor Prometheus itself

4. **Reliability**
   - Set up alerting for monitoring system failures
   - Regular backups of Grafana dashboards
   - Document custom dashboards and alerts
   - Test alert notification channels

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/overview/)
- [prometheus.prometheus Collection](https://galaxy.ansible.com/prometheus/prometheus)
- [grafana.grafana Collection](https://galaxy.ansible.com/grafana/grafana)

## Next Steps

1. Deploy monitoring stack
2. Configure datasources in Grafana
3. Import community dashboards
4. Create custom dashboards
5. Configure alert rules and notifications
6. Test alerting system
7. Monitor monitoring system itself
