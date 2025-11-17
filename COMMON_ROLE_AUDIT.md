# Common Role Audit - Default vs Optional Tasks

**Date**: November 17, 2025
**Scope**: Complete analysis of which tasks run by default and which require explicit enablement

---

## Executive Summary

The common role has a three-phase architecture:
- **Foundation** (Always runs): Core system setup
- **PHASE 1** (Mostly enabled): Security & monitoring
- **PHASE 2 & 3** (Mostly disabled): Advanced features

**Total Tasks**: 21 main tasks + 45+ wrapper tasks
**Default Enabled**: 13 core + 6 PHASE 1 = ~19 tasks enabled by default (lightweight foundation)
**Disabled by Default**: ~26 advanced tasks requiring explicit enablement

---

## FOUNDATION: Core Tasks (ALWAYS RUN)

These tasks execute unconditionally on every role apply:

| Task | File | Enable Flag | Default | Purpose |
|------|------|-------------|---------|---------|
| OS Validation | validate_os.yml | None | Always | Check OS compatibility |
| System Update | system_update.yml | `common_update_packages` | true | Update package cache |
| Package Upgrade | system_update.yml | `common_upgrade_packages` | true | Upgrade installed packages |
| Core Packages | core_packages.yml | None | Always | Install curl, wget, git, vim, etc. |
| Python Setup | python.yml | None | Always | Install Python 3 + pip + venv |
| User Management | manage_users.yml | None | Always | Configure users/groups |
| Chrony (NTP) | chrony.yml | `common_chrony_enabled` | **true** | Time synchronization (Chrony) |
| SSH Hardening | ssh_hardening.yml | None | Always | Harden SSH configuration |
| Sysctl Tuning | sysctl.yml | None | Always | Apply kernel parameters (production tuned) |
| Audit Setup | audit.yml | `common_enable_audit` | **true** | Linux audit daemon |
| File Limits | limits.yml | None | Always | PAM limits (file + process) |
| DNS Config | dns.yml | None | Always | Configure resolvers (8.8.8.8, 1.1.1.1) |
| System Logging | logging.yml | None | Always | Configure rsyslog |

**Key Stats**:
- Foundation tasks: 13
- Default enabled: 100% (all always run)
- No conditional logic: Just works on any supported OS

---

## PHASE 1: Security, Monitoring, and Backup

These tasks run conditionally based on enable flags:

### Security & Hardening Tasks

| Task | Enable Flag | Default | Time | Status | Comment |
|------|-------------|---------|------|--------|---------|
| Firewall (UFW/firewalld) | `firewall_enabled` | **true** | 5 min | Enabled | SSH + ICMP allowed by default |
| fail2ban (IPS) | `fail2ban_enabled` | **true** | 3 min | Enabled | SSH jail enabled, HTTP/FTP optional |
| Sudo Hardening | `sudo_hardening_enabled` | **true** | 2 min | Enabled | TTY requirement, input/output logging |
| AppArmor | `apparmor_enabled` | false | 5 min | Disabled | Ubuntu/Debian only |
| SELinux | `selinux_enabled` | false | 10 min | Disabled | RHEL/CentOS only |

### Monitoring & Metrics

| Task | Enable Flag | Default | Time | Status | Comment |
|------|-------------|---------|------|--------|---------|
| Metrics (node_exporter) | `metrics_enabled` | **true** | 3 min | Enabled | Port 9100 (Prometheus format) |
| Prometheus Wrapper | `monitoring_prometheus_enabled` | false | 5 min | Disabled | Full Prometheus stack |
| Grafana Wrapper | `monitoring_grafana_enabled` | false | 8 min | Disabled | Visualization on port 3000 |
| AlertManager Wrapper | `monitoring_alertmanager_enabled` | false | 5 min | Disabled | Alert aggregation on port 9093 |

### Optional Services

| Task | Enable Flag | Default | Time | Status | Comment |
|------|-------------|---------|------|--------|---------|
| Log Shipping | `log_shipping_enabled` | false | 10 min | Disabled | ELK stack integration |
| Vault Integration | `vault_enabled` | false | 15 min | Disabled | Secrets management |
| Backup Client | `backup_enabled` | false | 20 min | Disabled | Bacula/Veeam/Restic |

**PHASE 1 Summary**:
- Total PHASE 1 tasks: 12
- Enabled by default: 8 (firewall, fail2ban, sudo, metrics, prometheus, grafana, alertmanager, node_exporter)
- Disabled by default: 4 (apparmor, selinux, log shipping, vault, backup)

---

## PHASE 2.A: Advanced Monitoring Stack

Already counted above in PHASE 1 (Prometheus/Grafana/AlertManager)

---

## PHASE 2.B: Container & Application Deployment

### Docker Configuration

| Task | Enable Flag | Default | Time | Status | Comment |
|------|-------------|---------|------|--------|---------|
| Docker Installation | `container_docker_enabled` | false | 10 min | Disabled | Latest Docker version |
| Docker Compose | `container_docker_compose_enabled` | false | 3 min | Disabled | Multi-container orchestration |
| Docker Security | (integrated) | N/A | N/A | N/A | AppArmor, seccomp, capabilities (enabled when Docker is) |

**PHASE 2.B Summary**:
- Total tasks: 3
- Enabled by default: 0
- Requires explicit enablement for container workloads

---

## PHASE 2.C: Service Discovery & Load Balancing

### Optional Service Discovery & Load Balancing

| Task | Enable Flag | Default | Time | Status | Comment |
|------|-------------|---------|------|--------|---------|
| Consul Installation | `service_discovery_consul_enabled` | **false** | 15 min | Disabled | Service registration/discovery |
| Consul Service Discovery | (part of above) | **false** | N/A | Disabled | DNS, HTTP API, watch |
| HAProxy Load Balancer | `loadbalancing_haproxy_enabled` | **false** | 8 min | Disabled | Frontend/backend load balancing |

**PHASE 2.C Summary**:
- Total tasks: 3
- Enabled by default: 0
- Use case: Multi-node clusters with service discovery needs

---

## PHASE 2.D: Security & PKI Infrastructure

### Vault Secrets Management

| Task | Enable Flag | Default | Time | Status | Comment |
|------|-------------|---------|------|--------|---------|
| Vault Installation | `security_vault_enabled` | **false** | 20 min | Disabled | Secrets/PKI management |
| Vault PKI | `security_vault_pki_enabled` | **false** | 15 min | Disabled | Certificate authority |
| Vault Secrets Rotation | Multiple flags | **false** | 10 min | Disabled | Database/SSH/API key rotation |

**PHASE 2.D Summary**:
- Total tasks: 3
- Enabled by default: 0
- Use case: Enterprise secrets management

---

## PHASE 2.E: Database Replication & HA

### Database High Availability

| Task | Enable Flag | Default | Time | Status | Comment |
|------|-------------|---------|------|--------|---------|
| PostgreSQL Replication | `database_postgresql_enabled` | **false** | 20 min | Disabled | Primary-replica streaming |
| MySQL/Galera | `database_mysql_enabled` | **false** | 25 min | Disabled | Clustered replication |
| Database Failover | `database_failover_enabled` | **false** | 30 min | Disabled | Patroni/Pacemaker integration |

**PHASE 2.E Summary**:
- Total tasks: 3
- Enabled by default: 0
- Use case: Database redundancy and failover

---

## PHASE 3: Final Integration & Orchestration

### Kubernetes & Advanced Orchestration

| Task | Enable Flag | Default | Time | Status | Comment |
|------|-------------|---------|------|--------|---------|
| Kubernetes Orchestration | `orchestration_kubernetes_enabled` | **false** | 60 min | Disabled | Full K8s cluster |
| Application Deployment | `deployment_automation_enabled` | **false** | 45 min | Disabled | K8s workload automation |
| Service Mesh (Istio) | `service_mesh_enabled` | **false** | 40 min | Disabled | Advanced traffic management |
| Disaster Recovery | `disaster_recovery_enabled` | **false** | 30 min | Disabled | Backup + failover automation |
| Advanced Monitoring | `monitoring_observability_enabled` | **false** | 25 min | Disabled | Jaeger + ELK + Prometheus |

**PHASE 3 Summary**:
- Total tasks: 5
- Enabled by default: 0
- Use case: Enterprise-grade orchestration

---

## Quick Reference: Enable/Disable by Category

### Always Enabled (No Configuration Needed)
- OS validation
- System updates
- Core packages (curl, git, vim, etc.)
- Python 3 + pip
- SSH hardening
- Sysctl optimization (production tuned)
- PAM limits (1M file descriptors, 10M processes)
- DNS (8.8.8.8, 1.1.1.1)
- Logging

### Enabled by Default (Can Disable)
```yaml
# Security & Monitoring (enabled by default - lightweight)
firewall_enabled: true                          # Firewall
fail2ban_enabled: true                          # Intrusion prevention
sudo_hardening_enabled: true                    # Sudo hardening
common_chrony_enabled: true                     # Time sync
common_enable_audit: true                       # Audit daemon
metrics_enabled: true                           # Prometheus metrics (node_exporter only)
```

### Disabled by Default (Must Enable)
```yaml
# Monitoring Stack (disabled by default - enable if needed)
monitoring_prometheus_enabled: false            # Prometheus server
monitoring_grafana_enabled: false               # Grafana UI
monitoring_alertmanager_enabled: false          # AlertManager

# Containers (disabled by default - enable if needed)
container_docker_enabled: false                 # Docker
container_docker_compose_enabled: false         # Docker Compose

# Enterprise Features (disabled by default)
apparmor_enabled: false                         # AppArmor (Ubuntu/Debian)
selinux_enabled: false                          # SELinux (RHEL/CentOS)
log_shipping_enabled: false                     # ELK stack
vault_enabled: false                            # Vault secrets
backup_enabled: false                           # Backup client
service_discovery_consul_enabled: false         # Consul discovery
loadbalancing_haproxy_enabled: false            # HAProxy load balancer
database_postgresql_enabled: false              # PostgreSQL
database_mysql_enabled: false                   # MySQL/Galera
database_failover_enabled: false                # Database failover
orchestration_kubernetes_enabled: false         # Kubernetes
deployment_automation_enabled: false            # App deployment
service_mesh_enabled: false                     # Istio
disaster_recovery_enabled: false                # Disaster recovery
monitoring_observability_enabled: false         # Advanced observability
```

---

## How to Enable Optional Features

### Example 1: Enable Vault for Secrets Management
```yaml
# In your inventory vars or playbook:
security_vault_enabled: true
security_vault_pki_enabled: true
security_vault_audit_enabled: true
security_vault_database_rotation_enabled: true
```

### Example 2: Enable Kubernetes
```yaml
orchestration_kubernetes_enabled: true
orchestration_kubernetes_version: "1.28"
orchestration_kubernetes_network_plugin: "flannel"
```

### Example 3: Enable Database Replication
```yaml
database_postgresql_enabled: true
database_postgresql_version: "15"
database_failover_enabled: true
database_failover_manager: "patroni"
```

---

## Recommended Deployment Scenarios

### Scenario 1: Minimal (Dev/Test)
- Use defaults as-is
- Only foundation + monitoring
- Time to apply: 10-15 minutes

### Scenario 2: Production Single-Server
- Use defaults with Docker enabled
- Enable Vault for secrets
- Backup enabled
- Time to apply: 25-35 minutes

### Scenario 3: Production Cluster
- All defaults
- Enable Consul for service discovery
- Enable HAProxy for load balancing
- Enable PostgreSQL replication + failover
- Enable Kubernetes
- Time to apply: 120-180 minutes

### Scenario 4: Enterprise Kubernetes
- Enable Kubernetes + all orchestration features
- Enable service mesh (Istio)
- Enable disaster recovery
- Enable advanced monitoring (Jaeger + ELK)
- Time to apply: 180-240 minutes

---

## Task Dependencies

Some tasks depend on others being enabled:

```
Kubernetes
├── Requires: Docker (✓ enabled by default)
├── Requires: Monitoring (✓ enabled by default)
└── Requires: Networking (service_discovery)

Disaster Recovery
├── Requires: PostgreSQL/MySQL (if enabled)
├── Requires: Kubernetes (if applicable)
└── Requires: Monitoring

Service Mesh (Istio)
├── Requires: Kubernetes (✓ can enable)
├── Requires: Monitoring (✓ enabled by default)
└── Requires: Advanced Observability

Advanced Monitoring
├── Requires: Prometheus (✓ enabled by default)
├── Requires: Elasticsearch (optional)
└── Requires: Jaeger (optional)
```

---

## Performance Impact by Feature

| Feature | CPU Impact | Memory Impact | Disk Impact | Network |
|---------|-----------|---------------|-------------|---------|
| Foundation | <1% | 50-100MB | 500MB | Light |
| Firewall + fail2ban | <1% | 20-50MB | 100MB | Light |
| Monitoring (Prometheus) | 1-3% | 200-400MB | 5-10GB | Light |
| Docker | 1-2% | 100-200MB | Variable | Light |
| Consul | 1-2% | 100-150MB | 500MB | Medium |
| Vault | <1% (idle) | 100-200MB | 1-5GB | Light |
| PostgreSQL | Variable | 500MB-5GB | 10GB+ | Medium |
| Kubernetes | 3-5% | 1-2GB | 20GB+ | Medium |
| Service Mesh | 5-10% | 500MB-1GB | 5GB | Medium |

---

## Troubleshooting: Which Task Failed?

If something isn't working, check which phase is causing issues:

```yaml
# Check Foundation (always runs)
- Is SSH hardened? (check /etc/ssh/sshd_config)
- Are packages installed? (check /usr/bin/curl, /usr/bin/git)
- Is Python 3 available? (python3 --version)

# Check PHASE 1 (mostly enabled)
- Is firewall enabled? (ufw status / firewall-cmd --list-all)
- Is fail2ban running? (systemctl status fail2ban)
- Are metrics being collected? (curl localhost:9100/metrics)

# Check PHASE 2 (optional)
- Is Docker running? (docker ps)
- Is Prometheus scraping? (curl localhost:9090/api/v1/targets)
- Is Grafana accessible? (curl localhost:3000)

# Check PHASE 3 (enterprise)
- Is Kubernetes master running? (kubectl get nodes)
- Is service mesh injecting sidecars? (kubectl get pods -o jsonpath)
```

---

## Summary Table: All 21 Core Tasks

| # | Task | Phase | Default | Required | Time |
|---|------|-------|---------|----------|------|
| 1 | validate_os.yml | Foundation | Always | Yes | 1 min |
| 2 | system_update.yml | Foundation | Always | Yes | 3-5 min |
| 3 | core_packages.yml | Foundation | Always | Yes | 2-3 min |
| 4 | python.yml | Foundation | Always | Yes | 2 min |
| 5 | manage_users.yml | Foundation | Always | Yes | 1 min |
| 6 | chrony.yml | Foundation | true | No | 2 min |
| 7 | ssh_hardening.yml | Foundation | Always | Yes | 2 min |
| 8 | sysctl.yml | Foundation | Always | Yes | 1 min |
| 9 | audit.yml | Foundation | true | No | 1 min |
| 10 | limits.yml | Foundation | Always | Yes | 1 min |
| 11 | dns.yml | Foundation | Always | Yes | 1 min |
| 12 | logging.yml | Foundation | Always | Yes | 1 min |
| 13 | firewall.yml | PHASE 1 | true | No | 5 min |
| 14 | fail2ban.yml | PHASE 1 | true | No | 3 min |
| 15 | metrics.yml | PHASE 1 | true | No | 3 min |
| 16 | log_shipping.yml | PHASE 1 | false | No | 10 min |
| 17 | sudo_hardening.yml | PHASE 1 | true | No | 2 min |
| 18 | vault.yml | PHASE 1 | false | No | 20 min |
| 19 | backup.yml | PHASE 1 | false | No | 20 min |
| 20 | apparmor.yml | PHASE 1 | false | No | 5 min |
| 21 | selinux.yml | PHASE 1 | false | No | 10 min |

**Plus 45+ wrapper tasks for PHASE 2 & 3 (monitoring, docker, kubernetes, etc.)**

---

**Created**: November 17, 2025
**Status**: Complete Audit
**Next Review**: When new PHASE tasks are added

