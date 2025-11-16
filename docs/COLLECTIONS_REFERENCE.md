# Ansible Collections Reference

Complete guide to installed collections and available roles for ansible-infra framework.

## Installed Collections

### 1. grafana.grafana (v5.7.0)
**Official Grafana Ansible Collection**

GitHub: https://github.com/grafana/grafana-ansible-collection
Galaxy: https://galaxy.ansible.com/grafana/grafana

#### Available Roles

| Role | Purpose | Status |
|------|---------|--------|
| `grafana_agent` | Unified telemetry agent (metrics, logs, traces) | ✅ Used |
| `grafana` | Grafana server, dashboards, provisioning | ✅ Used |
| `loki` | Log aggregation and storage | ✅ Used |
| `promtail` | Grafana log agent | ⏳ Optional |
| `mimir` | Distributed Prometheus-compatible metrics DB | ⏳ Optional |
| `alloy` | Advanced telemetry collector (grafana-agent replacement) | ⏳ Optional |
| `opentelemetry_collector` | OpenTelemetry collector | ⏳ Optional |

#### Role Details

**grafana_agent**
- Collects metrics from local node_exporter
- Ships metrics to Prometheus
- Forwards logs to Loki
- Provides distributed tracing support
- Runs as systemd service
- Auto-discovery for services

**grafana**
- Installs Grafana server
- Configures datasources
- Provisions dashboards
- Sets up authentication
- Manages users and organizations
- Supports alerting

**loki**
- Log aggregation service
- LogQL query language
- Multi-tenant support
- Storage backends (filesystem, S3, GCS)
- Integrates with Grafana
- Horizontal scalability

### 2. prometheus.prometheus (v0.27.4)
**Official Prometheus Community Ansible Collection**

GitHub: https://github.com/prometheus-community/ansible
Galaxy: https://galaxy.ansible.com/prometheus/prometheus

#### Available Roles

| Role | Purpose | Status |
|------|---------|--------|
| `prometheus` | Prometheus time-series database | ✅ Used |
| `node_exporter` | System/host metrics collector | ✅ Used |
| `alertmanager` | Alert routing and management | ✅ Used |
| `pushgateway` | Scraping batch jobs | ⏳ Optional |
| `nginx_exporter` | NGINX metrics | ⏳ Optional |
| `postgres_exporter` | PostgreSQL metrics | ⏳ Optional |
| `mongodb_exporter` | MongoDB metrics | ⏳ Optional |
| `redis_exporter` | Redis metrics | ⏳ Optional |
| `mysql_exporter` | MySQL/MariaDB metrics | ⏳ Optional |
| `blackbox_exporter` | Endpoint/HTTP probing | ⏳ Optional |
| `consul_exporter` | Consul metrics | ⏳ Optional |
| `snmp_exporter` | SNMP metrics | ⏳ Optional |
| `ipmi_exporter` | IPMI/Server hardware metrics | ⏳ Optional |
| `apache_exporter` | Apache HTTP metrics | ⏳ Optional |
| `bind_exporter` | BIND DNS metrics | ⏳ Optional |
| `nginx_exporter` | NGINX HTTP metrics | ⏳ Optional |
| `fail2ban_exporter` | Fail2ban metrics | ⏳ Optional |
| `systemd_exporter` | Systemd unit metrics | ⏳ Optional |
| `process_exporter` | Custom process metrics | ⏳ Optional |
| `cadvisor` | Container metrics | ⏳ Optional |
| `smartctl_exporter` | Hard drive S.M.A.R.T. metrics | ⏳ Optional |
| `nvidia_gpu_exporter` | GPU metrics | ⏳ Optional |
| `memcached_exporter` | Memcached metrics | ⏳ Optional |
| `influxdb_exporter` | InfluxDB metrics | ⏳ Optional |
| `smokeping_prober` | Network latency probing | ⏳ Optional |
| `chronyd_exporter` | Chrony NTP metrics | ⏳ Optional |

#### Role Details

**prometheus**
- Installs Prometheus server
- Configures scrape jobs
- Manages alert rules
- Sets data retention
- Supports remote storage
- Handles multiple instances

**node_exporter**
- Collects system metrics:
  - CPU usage and time
  - Memory utilization
  - Disk I/O and space
  - Network interfaces
  - System load
  - Process information
- Runs as systemd service
- Configurable collectors

**alertmanager**
- Routes alerts by labels
- Sends notifications (email, Slack, PagerDuty, etc.)
- Groups related alerts
- Manages silence periods
- Handles alert deduplication
- Multi-instance clustering

### 3. Community Collections (v11.4.0)
**community.general** - General utilities and modules

Includes:
- File management
- System administration
- Notification modules
- Monitoring utilities

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Application Servers                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  grafana.grafana:                                       │
│  └─ grafana_agent (metrics + logs + traces)             │
│                                                         │
│  prometheus.prometheus:                                 │
│  └─ node_exporter (system metrics)                      │
│  └─ [optional exporters for apps]                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
              ↓↓↓
┌─────────────────────────────────────────────────────────┐
│              Metrics & Logs Stack                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  prometheus.prometheus:prometheus (9090)                │
│  ├─ Scrapes node_exporter                              │
│  ├─ Scrapes grafana_agent                              │
│  └─ Evaluates alert rules                              │
│                                                         │
│  grafana.grafana:loki (3100)                            │
│  ├─ Receives logs from grafana_agent                    │
│  ├─ Stores with labels                                  │
│  └─ Queryable by Grafana                                │
│                                                         │
│  prometheus.prometheus:alertmanager (9093)              │
│  ├─ Routes alerts from Prometheus                       │
│  └─ Sends notifications                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
              ↓↓↓
┌─────────────────────────────────────────────────────────┐
│              Visualization & Control                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  grafana.grafana:grafana (3000)                         │
│  ├─ Connects to Prometheus datasource                   │
│  ├─ Connects to Loki datasource                         │
│  ├─ Creates dashboards                                  │
│  ├─ Configures alerts                                   │
│  └─ Manages users/teams                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Usage in Playbooks

### Using grafana.grafana Roles

```yaml
roles:
  # Deploy Grafana Agent on all servers
  - role: grafana.grafana.grafana_agent
    tags: [monitoring, grafana]
    when: '"monitoring_disabled" not in group_names'
    vars:
      grafana_agent_version: latest
      grafana_agent_enabled: true

  # Deploy Grafana server
  - role: grafana.grafana.grafana
    tags: [grafana, visualization]
    when: '"grafana_servers" in group_names'
    vars:
      grafana_admin_user: admin
      grafana_admin_password: "{{ vault_grafana_password }}"

  # Deploy Loki for log aggregation
  - role: grafana.grafana.loki
    tags: [logging, loki]
    when: '"loki_servers" in group_names'
```

### Using prometheus.prometheus Roles

```yaml
roles:
  # Deploy Prometheus on dedicated servers
  - role: prometheus.prometheus.prometheus
    tags: [prometheus, monitoring]
    when: '"prometheus_servers" in group_names'
    vars:
      prometheus_version: "2.48.0"
      prometheus_listen_address: "0.0.0.0:9090"

  # Deploy Node Exporter on all servers
  - role: prometheus.prometheus.node_exporter
    tags: [prometheus, metrics]
    when: '"monitoring_disabled" not in group_names'
    vars:
      node_exporter_version: "1.7.0"
      node_exporter_listen_address: "0.0.0.0:9100"

  # Deploy Alertmanager for alert routing
  - role: prometheus.prometheus.alertmanager
    tags: [alerting, prometheus]
    when: '"alertmanager_servers" in group_names'
    vars:
      alertmanager_version: "0.26.0"
```

## Collection Variables

### grafana.grafana Variables

**grafana_agent**
```yaml
grafana_agent_enabled: true
grafana_agent_version: latest
grafana_agent_log_level: info
grafana_agent_listen_port: 12345
prometheus_listen_address: "0.0.0.0:9090"  # Where to send metrics
prometheus_external_labels: {}
```

**grafana**
```yaml
grafana_admin_user: admin
grafana_admin_password: admin
grafana_admin_password_hash: false
grafana_install_method: package
grafana_version: latest
grafana_port: 3000
grafana_datasources: {}
grafana_dashboards: {}
```

**loki**
```yaml
loki_install_method: package
loki_version: latest
loki_listen_port: 3100
loki_storage_path: /loki
loki_retention_period: 7d
```

### prometheus.prometheus Variables

**prometheus**
```yaml
prometheus_version: "2.48.0"
prometheus_listen_address: "0.0.0.0:9090"
prometheus_scrape_interval: "15s"
prometheus_evaluation_interval: "15s"
prometheus_retention_time: "15d"
prometheus_external_labels: {}
prometheus_scrape_configs: []
```

**node_exporter**
```yaml
node_exporter_version: "1.7.0"
node_exporter_listen_address: "0.0.0.0:9100"
node_exporter_enabled_collectors: []
node_exporter_disabled_collectors: []
```

**alertmanager**
```yaml
alertmanager_version: "0.26.0"
alertmanager_listen_port: 9093
alertmanager_config: {}
alertmanager_templates: []
```

## Best Practices

### 1. Version Pinning
Always pin collection and role versions:
```yaml
roles:
  - role: prometheus.prometheus.prometheus
    vars:
      prometheus_version: "2.48.0"  # Explicit version
```

### 2. Variable Scope
Use group_vars for environment-specific settings:
```
inventories/
  production/
    group_vars/
      all.yml
      prometheus_servers.yml
      grafana_servers.yml
```

### 3. Multiple Instances
Deploy multiple Prometheus instances for HA:
```yaml
prometheus_servers:
  prometheus01: 10.0.3.10
  prometheus02: 10.0.3.11
  prometheus03: 10.0.3.12
```

### 4. Security
Use Ansible Vault for sensitive data:
```bash
ansible-vault encrypt inventories/production/group_vars/all/vault.yml
```

### 5. Testing
Test roles individually before full deployment:
```bash
ansible-playbook playbooks/configure.yml --tags prometheus -C
```

## Common Tasks

### Add Custom Prometheus Scrape Job

```yaml
# In group_vars or playbook
prometheus_scrape_configs:
  - job_name: 'custom-app'
    static_configs:
      - targets: ['localhost:8080']
```

### Configure Grafana Datasource

```yaml
grafana_datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    access: proxy
    is_default: true
```

### Add Grafana Dashboard

```yaml
grafana_dashboards:
  - dashboard_id: 1860  # Node Exporter Full
    state: present
  - dashboard_id: 3662  # Prometheus
    state: present
```

### Configure Alertmanager Notifications

```yaml
alertmanager_config:
  route:
    receiver: 'slack'
  receivers:
    - name: 'slack'
      slack_configs:
        - api_url: 'YOUR_SLACK_WEBHOOK'
          channel: '#alerts'
```

## Troubleshooting

### Role Not Found

```bash
# Verify collection is installed
ansible-galaxy collection list

# Reinstall if needed
ansible-galaxy collection install grafana.grafana
ansible-galaxy collection install prometheus.prometheus
```

### Version Mismatch

```bash
# Install specific version
ansible-galaxy collection install grafana.grafana:5.7.0
ansible-galaxy collection install prometheus.prometheus:0.27.4
```

### Check Role Documentation

```bash
# View role defaults
cat ~/.ansible/collections/ansible_collections/grafana/grafana/roles/grafana_agent/defaults/main.yml

# View role variables
cat ~/.ansible/collections/ansible_collections/prometheus/prometheus/roles/prometheus/defaults/main.yml
```

## Resources

- [Grafana Ansible Collection Docs](https://github.com/grafana/grafana-ansible-collection)
- [Prometheus Ansible Collection Docs](https://github.com/prometheus-community/ansible)
- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)

## Next Steps

1. Review role defaults and requirements
2. Customize variables for your environment
3. Test in staging before production
4. Monitor collection updates
5. Join community for support
