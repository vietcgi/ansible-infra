# Architecture & Design Strategy

**ansible-infra - System Design and Implementation Approach**

---

## Core Architecture: Hybrid Deployment Model

The ansible-infra framework uses a **hybrid deployment model** to handle the complexities of multi-platform infrastructure, particularly the macOS + Linux combination required for modern infrastructure projects.

---

## Problem Statement

### Why "Hybrid"?

**The Challenge**: Official Ansible collections are Linux-focused
- prometheus.prometheus - 26 roles for Linux monitoring
- grafana.grafana - 7 roles for Linux dashboarding
- No macOS support in official collections
- systemd (Linux) vs launchd (macOS) incompatibility

**The Solution**: Use a hybrid approach

```
Official Collections (Linux Backend)
├─ prometheus.prometheus (26+ roles)
├─ grafana.grafana (7+ roles)
└─ community.general (utilities)

+ Custom Roles (macOS Specific)
├─ system_hardening_macos IMPLEMENTED
├─ macos_monitoring (planned)
└─ app_health_check (planned)

= Unified Framework
├─ Works on any Linux distribution
├─ Works on macOS with custom roles
├─ Monitoring aggregates to central backend
└─ Single source of truth
```

---

## Deployment Architecture

### Client-Server Model

```
┌─────────────────────────────────────┐
│ CLIENT LAYER (Distributed) │
├─────────────────────────────────────┤
│ │
│ macOS Clients (e.g., Arnio) │
│ ├─ Common role │
│ ├─ system_hardening_macos │
│ ├─ macos_monitoring │
│ └─ app_health_check │
│ │
│ Linux Servers │
│ ├─ Common role │
│ ├─ prometheus.prometheus │
│ ├─ Official collections │
│ └─ Custom roles (as needed) │
│ │
└─────────────────────────────────────┘
 (Ansible Push)
 ↓
┌─────────────────────────────────────┐
│ BACKEND LAYER (Centralized) │
├─────────────────────────────────────┤
│ │
│ Linux Server │
│ ├─ Prometheus (metrics) │
│ ├─ Grafana (dashboards) │
│ ├─ AlertManager (alerting) │
│ └─ Persistent Storage │
│ │
└─────────────────────────────────────┘
```

---

## Role Strategy

### Role Categories

#### 1. **Foundation Roles** (Works Everywhere)

**`common` Role**
- **Purpose**: OS baseline for all servers
- **Platforms**: Linux (Ubuntu, Debian, RHEL) + macOS
- **Includes**:
 - System updates
 - SSH hardening
 - NTP configuration
 - Basic security settings
 - Package management

**Why**: Every system needs basic hardening and configuration

#### 2. **Official Collection Roles** (Linux Only)

**`prometheus.prometheus` (26+ roles)**
- node_exporter (metrics collection)
- prometheus (time-series DB)
- alertmanager (alert routing)
- pushgateway (metrics push)
- And 20+ more

**`grafana.grafana` (7+ roles)**
- grafana (dashboarding)
- datasource configuration
- dashboard provisioning
- Plugin management

**Why**: Well-maintained, battle-tested, large community

#### 3. **Custom Roles** (Client-Specific)

**macOS Roles** (for Arnio and Mac-heavy clients)
- `system_hardening_macos` - IMPLEMENTED
 - 31 security controls
 - NIST + CIS compliance
 - Post-quantum SSH
 - Firewall configuration (ALF + PF)

- `macos_monitoring` - (planned)
 - Node exporter via launchd
 - Homebrew package management
 - macOS-specific metrics

- `app_health_check` - (planned)
 - Blackbox exporter wrapper
 - Application-level monitoring

**Linux Roles** (for specialized deployments)
- Client-specific monitoring roles
- Application-specific configurations
- Custom automation

**Why**: Some requirements are platform-specific or client-specific

---

## Platform Compatibility Matrix

| Feature | Linux | macOS | Solution |
|---------|-------|-------|----------|
| Service management | systemd | launchd | Custom roles for macOS |
| Package management | apt/yum | homebrew | community.general.homebrew |
| SSH hardening | | | Common role supports both |
| Monitoring | | ⚠️ | Custom metrics collection |
| Prometheus | | | Run on Linux backend |
| Grafana | | | Run on Linux backend |

---

## Configuration Hierarchy

### Environment-Based Configuration

```
inventories/
├── production/
│ ├── hosts.yml (Production servers)
│ └── group_vars/ (Production-specific variables)
│
├── staging/
│ ├── hosts.yml (Staging servers)
│ └── group_vars/ (Staging-specific variables)
│
└── development/
 ├── hosts.yml (Dev servers)
 └── group_vars/ (Dev-specific variables)
```

### Variable Precedence

1. **Defaults** (role defaults/main.yml) - Lowest
2. **Inventory vars** (group_vars/, host_vars/) - Override defaults
3. **Playbook vars** (playbook-specific) - Override inventory
4. **Command-line vars** (-e flag) - Highest priority

### Example Configuration

**Production macOS (Arnio)**
```yaml
---
hosts:
 arnio_macs:
 - mac01.internal
 - mac02.internal
 - mac03.internal

group_vars:
 arnio_macs:
 # Common role variables
 enable_auto_update: true
 ssh_port: 2222
 ntp_servers:
 - time1.apple.com
 - time2.apple.com

 # Hardening variables
 firewall_enabled: true
 pf_ssh_rate_limit: 5 # 5 connections per 30 seconds
 xprotect_enabled: true
 sip_verify: true

 # Monitoring variables
 node_exporter_port: 9100
 prometheus_backend: monitoring.internal:9090
```

---

## Playbook Composition

### Three Core Playbooks

#### 1. **provision.yml** - Initial Setup
```yaml
- Common role (OS baseline)
- Configure basic network
- Install required packages
- Set up SSH
- Enable monitoring
```

**When to run**: New servers being added
**Time**: 5-10 minutes
**Idempotent**: Yes (safe to run multiple times)

#### 2. **configure.yml** - Full Configuration
```yaml
- All of provision.yml
- Security hardening
- Application configuration
- Monitoring setup
- Advanced networking
```

**When to run**: Initial deployment, major updates
**Time**: 10-15 minutes
**Idempotent**: Yes

#### 3. **maintenance.yml** - Ongoing Updates
```yaml
- System updates
- Security patches
- Log rotation
- Cache cleanup
- Health checks
```

**When to run**: Regularly (daily/weekly)
**Time**: 2-5 minutes
**Idempotent**: Yes

---

## Data Flow

### Metrics Collection → Storage → Visualization

```
macOS Clients
├─ Node exporter (custom launchd wrapper)
└─ Custom health checks
 ↓
Linux Backend (Prometheus)
├─ Scrapes metrics from clients
├─ Stores time-series data
└─ Evaluates alert rules
 ↓
Grafana
├─ Queries Prometheus
├─ Renders dashboards
└─ Sends alerts
 ↓
Alert Destinations
├─ Email
├─ Slack
├─ PagerDuty
└─ Custom webhooks
```

---

## Security Layers

### Layer 1: OS-Level (Common Role)
- SSH key-based authentication
- Firewall configuration
- User access control
- Update automation

### Layer 2: Network-Level
- Private network architecture
- Firewall rules (ALF + PF on macOS)
- SSH rate limiting
- IDS/IPS integration (future)

### Layer 3: Application-Level
- Service hardening
- Application-specific security rules
- Monitoring for anomalies
- Alert escalation

### Layer 4: Backend-Level
- Prometheus authentication
- Grafana access control
- Encrypted communication (TLS)
- Data retention policies

---

## Testing & Validation

### Pre-Deployment Testing

**Local Validation** (Developer Machine)
```bash
make test-fast # Lint + syntax (2 min)
make molecule-test # Multi-scenario tests (12 min)
make security # Security scanning
```

**Staging Validation** (Test Environment)
```bash
ansible-playbook playbooks/provision.yml -i inventories/staging/hosts.yml
# Verify all services running
make test-connectivity
```

### Production Deployment

**Safe Deployment Process**
1. Run in check mode first
 ```bash
 ansible-playbook playbooks/configure.yml -i inventories/production/hosts.yml --check
 ```

2. Deploy to first server
 ```bash
 ansible-playbook playbooks/configure.yml -i inventories/production/hosts.yml -l first_server
 ```

3. Verify before rolling out
4. Deploy to remaining servers

---

## Scalability Considerations

### Horizontal Scaling
- Add new servers to inventory
- Roles automatically apply
- No additional configuration needed
- Monitoring automatically includes new servers

### Vertical Scaling
- Increase role variables (memory, CPU allocation)
- Configure via inventory variables
- Safe to update on running systems (idempotent)

### Geographic Distribution
- Federated Prometheus instances
- Central aggregation possible
- Multi-region support via inventory groups

---

## Maintenance & Updates

### Regular Maintenance
1. **Weekly**: `make maintain-prod` (updates, logs)
2. **Monthly**: Role variable reviews
3. **Quarterly**: Dependency updates

### Major Updates
1. Test in staging first
2. Update role files
3. Run `make test` to validate
4. Deploy via playbooks
5. Monitor and verify

---

## Integration Points

### With Ansible
- Playbooks invoke roles with configurations
- Roles support both push and pull (via cron)
- Jinja2 templates for dynamic configuration

### With Version Control
- Git tracks all infrastructure code
- Branch-based deployments available
- Rollback via git revert

### With CI/CD
- GitHub Actions automated testing
- Pre-commit hooks local validation
- Status checks prevent bad deployments

---

## Future Enhancements

### Near-term
- [ ] Kubernetes role support
- [ ] Container monitoring
- [ ] Advanced network policies

### Medium-term
- [ ] Multi-cloud support (AWS, Azure, GCP)
- [ ] Terraform integration
- [ ] Configuration drift detection

### Long-term
- [ ] AI-based anomaly detection
- [ ] Self-healing infrastructure
- [ ] Policy as Code (OPA/Rego)

---

## Design Principles

### 1. **Simplicity**
- Minimal dependencies
- Clear role separation
- Straightforward configurations

### 2. **Idempotence**
- Safe to run repeatedly
- No harmful side effects
- Convergent design

### 3. **Testability**
- Comprehensive test coverage
- Multi-platform validation
- Molecule testing framework

### 4. **Security**
- Defense in depth
- Compliance-aligned
- Regular auditing

### 5. **Maintainability**
- Clear documentation
- Modular design
- Version control

---

## Summary

The hybrid deployment model combines:
- **Official collections** for battle-tested Linux infrastructure
- **Custom roles** for macOS and specialized requirements
- **Central backend** for aggregated monitoring and dashboarding
- **Enterprise QA** for reliability and compliance

This approach enables rapid deployment while maintaining professional standards across diverse infrastructure types.

**Last Updated**: November 15, 2025
