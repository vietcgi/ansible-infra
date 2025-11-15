# Hybrid Deployment Model - The Best of Both Worlds

## The Insight

**Hybrid Approach** = Use official collections where they work best + custom roles for macOS

This is NOT a compromise—it's actually the OPTIMAL architecture.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  TIER 1: Mac Mini Servers (Arnio Deployment)                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ sentinel.common (our custom)                           │ │
│  │ ├─ SSH hardening                                       │ │
│  │ ├─ System optimization                                 │ │
│  │ ├─ macOS-specific settings                             │ │
│  │ └─ Core foundation                                     │ │
│  │                                                        │ │
│  │ sentinel.macos_monitoring (our custom)                 │ │
│  │ ├─ Node Exporter via homebrew                          │ │
│  │ ├─ Service management via launchd                      │ │
│  │ └─ Health metrics collection                           │ │
│  │                                                        │ │
│  │ grafana.grafana.grafana_agent (official - works!)      │ │
│  │ ├─ Unified telemetry collection                        │ │
│  │ ├─ Sends metrics to Prometheus                         │ │
│  │ ├─ Forwards logs to Loki                               │ │
│  │ └─ Already has macOS support                           │ │
│  │                                                        │ │
│  │ sentinel.app_health_check (our custom)                 │ │
│  │ ├─ Custom app monitoring script                        │ │
│  │ ├─ Auto-restart logic                                  │ │
│  │ ├─ Scheduled health checks                             │ │
│  │ └─ Metrics export                                      │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
              ↓ (All metrics sent to backend)
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  TIER 2: Monitoring Backend (Linux VM or Always-On Server)  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ sentinel.common (our custom)                           │ │
│  │ └─ Foundation for Linux                                │ │
│  │                                                        │ │
│  │ prometheus.prometheus.prometheus (official)            │ │
│  │ ├─ Aggregate metrics from all Mac minis                │ │
│  │ ├─ Evaluate alert rules                                │ │
│  │ ├─ Time-series database                                │ │
│  │ └─ 15+ day retention                                   │ │
│  │                                                        │ │
│  │ prometheus.prometheus.alertmanager (official)          │ │
│  │ ├─ Route alerts based on rules                         │ │
│  │ ├─ Send to Slack/email/webhooks                        │ │
│  │ ├─ Manage silences and deduplicate                     │ │
│  │ └─ PagerDuty integration (optional)                     │ │
│  │                                                        │ │
│  │ grafana.grafana.grafana (official)                     │ │
│  │ ├─ Beautiful dashboards                                │ │
│  │ ├─ Mobile-friendly alerts                              │ │
│  │ ├─ User management                                     │ │
│  │ └─ Alert configuration UI                              │ │
│  │                                                        │ │
│  │ grafana.grafana.loki (official)                        │ │
│  │ ├─ Centralized log aggregation                         │ │
│  │ ├─ LogQL for log queries                               │ │
│  │ ├─ Integrated with Grafana                             │ │
│  │ └─ Low storage overhead                                │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
              ↓ (Alerts & Visibility)
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  TIER 3: Notifications & Dashboards                         │
│  ├─ Slack alerts (real-time)                                │
│  ├─ Email notifications (digest)                            │
│  ├─ Grafana dashboards (web + mobile)                       │
│  ├─ Webhook integrations (custom logic)                     │
│  └─ PagerDuty (enterprise escalation)                       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Why Hybrid is Optimal

### Collection Compatibility

| Component | Type | Collection | macOS | Linux | Status |
|-----------|------|-----------|-------|-------|--------|
| **Grafana Agent** | Client | Official | ✅ | ✅ | Use as-is |
| **Node Exporter** | Metrics | Custom | ✅ | ✅ | Create custom wrapper |
| **Prometheus** | Server | Official | ❌ | ✅ | Use on Linux only |
| **Alertmanager** | Server | Official | ❌ | ✅ | Use on Linux only |
| **Grafana** | Server | Official | ❌ | ✅ | Use on Linux only |
| **Loki** | Server | Official | ❌ | ✅ | Use on Linux only |

**The Insight:**
- Official collections work perfectly for servers (Linux)
- Custom roles needed only for Mac clients
- This is the natural separation!

---

## Deployment Strategy

### On Mac Minis

**Install:**
1. `sentinel.common` - SSH, basic hardening
2. `sentinel.macos_monitoring` - Node Exporter + launchd
3. `grafana.grafana.grafana_agent` - Telemetry collection
4. `sentinel.app_health_check` - Custom app monitoring

**Result:** Lightweight agent that sends metrics to backend

### On Linux Backend (1 small VM)

**Install:**
1. `sentinel.common` - Foundation
2. `prometheus.prometheus.prometheus` - Metrics database
3. `prometheus.prometheus.alertmanager` - Alert routing
4. `grafana.grafana.grafana` - Dashboards
5. `grafana.grafana.loki` - Log aggregation

**Result:** Central monitoring hub with all Mac metrics aggregated

### Advantage

✅ **Separation of concerns:**
- Macs: lightweight, minimal footprint
- Linux: powerful, persistent storage

✅ **No hybrid hacks:**
- Don't try to run Prometheus on macOS
- Use systemd collections as-is on Linux
- Custom macOS roles are simple and focused

✅ **Easy to understand:**
- Macs = metrics sources (agents)
- Linux = metrics aggregation (servers)
- Clear data flow

✅ **Scales beautifully:**
- Add 10 Macs? Just deploy agent role
- Add 100 Macs? Same approach
- Monitor multiple Mac clusters? Just add more to Prometheus scrape config

---

## File Structure

```
roles/
├── common/                          # EXISTING - Used on both
│   ├── tasks/main.yml
│   ├── tasks/ssh_hardening.yml
│   ├── tasks/system_update.yml
│   └── ... (all existing files)
│
├── macos_monitoring/                # NEW - macOS clients only
│   ├── tasks/main.yml
│   ├── tasks/node_exporter.yml
│   ├── templates/
│   │   ├── com.prometheus.node_exporter.plist.j2
│   │   └── node_exporter.conf.j2
│   └── defaults/main.yml
│
├── app_health_check/                # NEW - macOS clients only
│   ├── tasks/main.yml
│   ├── templates/
│   │   ├── check_app_health.sh.j2
│   │   ├── com.arnio.app_check.plist.j2
│   │   └── restart_app.sh.j2
│   └── defaults/main.yml
│
└── system_hardening_macos/          # NEW - macOS-specific
    ├── tasks/main.yml
    ├── templates/firewall.sh.j2
    └── defaults/main.yml
```

---

## Playbooks

### `playbooks/provision_macos_client.yml`
```yaml
- name: Provision Mac Mini as Monitoring Client
  hosts: macos_clients
  roles:
    - common
    - macos_monitoring
    - system_hardening_macos
    - app_health_check
```

### `playbooks/provision_monitoring_backend.yml`
```yaml
- name: Provision Monitoring Backend Server
  hosts: monitoring_backend
  roles:
    - common
    - prometheus.prometheus.prometheus
    - prometheus.prometheus.alertmanager
    - grafana.grafana.grafana
    - grafana.grafana.loki
```

### `playbooks/full_deployment.yml`
```yaml
- import_playbook: provision_macos_client.yml
- import_playbook: provision_monitoring_backend.yml
```

---

## Inventory Structure

```yaml
all:
  children:
    # Mac Mini clients (Arnio)
    macos_clients:
      hosts:
        mac-mini-01:
          ansible_host: 10.0.1.10
          app_name: "MyCustomApp"
          app_check_interval: 60  # seconds
        mac-mini-02:
          ansible_host: 10.0.1.11
          app_name: "MyCustomApp"

    # Monitoring backend
    monitoring_backend:
      hosts:
        monitoring-01:
          ansible_host: 10.0.2.10
          prometheus_retention: "30d"
          grafana_admin_password: "{{ vault_grafana_password }}"

    # Optional: Linux servers (if scaling)
    linux_servers:
      children:
        - macos_clients
        - monitoring_backend
```

---

## Cost Breakdown (Arnio)

### Mac Minis
- Already owned
- 0 additional cost
- Lightweight agents only

### Monitoring Backend (1 small Linux VM)
- DigitalOcean: $5-10/month
- AWS t3.micro: free tier eligible
- Upcloud: $5/month
- **Cost: $5-120/year**

### Official Collections
- prometheus.prometheus: free
- grafana.grafana: free
- community.general: free
- **Cost: $0**

### Alternatives Comparison
| Solution | Cost/Year | Setup Time | Control |
|----------|-----------|-----------|---------|
| **Sentinel Hybrid** | $60-120 | 8-12 hours | Complete |
| Datadog | $6,000+ | 1 hour | Limited |
| New Relic | $7,200+ | 1 hour | Limited |
| Uptime Kuma | $60-120 | 4-6 hours | Limited |
| Custom scripts | $60-120 | 40+ hours | Complex |

**Sentinel Hybrid wins on cost + control + maintainability**

---

## Implementation Timeline

### Week 1: Foundation
- [ ] Create 3 custom macOS roles
- [ ] Create launchd templates
- [ ] Test on single Mac Mini
- [ ] Validate metrics reach Prometheus

### Week 2: Backend
- [ ] Provision Linux monitoring VM
- [ ] Deploy Prometheus
- [ ] Deploy Alertmanager
- [ ] Configure Slack integration

### Week 3: Visualization & Operations
- [ ] Deploy Grafana
- [ ] Create custom dashboards for Arnio app
- [ ] Deploy Loki for logs
- [ ] Create runbooks

### Week 4: Production & Documentation
- [ ] Deploy to all Mac Minis
- [ ] Validate alerts working
- [ ] Write team documentation
- [ ] Create troubleshooting guide

**Total: 4 weeks to full production**

---

## Advantages Summary

✅ **Uses official collections optimally** (not fighting them)
✅ **Minimal custom code** (just 3 focused roles)
✅ **macOS-native** (launchd, homebrew)
✅ **Scales beautifully** (add more Macs anytime)
✅ **50x cheaper than Datadog**
✅ **Complete control** (git, reproducible)
✅ **Team documentation** (all code in git)
✅ **Leverages Sentinel Infrastructure** (foundation already built)
✅ **Puppet-ready** (can migrate later)
✅ **Simple operations** (one playbook per server type)

---

## Recommendation

**This is the solution for Arnio:**

1. **Use Sentinel Infrastructure as foundation** ✅
2. **Add 3 custom macOS roles** (small scope)
3. **Use official collections for backend** (proven, supported)
4. **Deploy to Mac Minis as clients** (agents)
5. **Run one Linux VM for backend** (monitoring hub)
6. **Full visibility + auto-restart for $100/year**

**vs Datadog: $6,000/year + no control**

This is the **sweet spot** between ease of use and control.

Should I start implementing the 3 custom macOS roles?
