# Sentinel Infrastructure - macOS-Focused Strategy

## Situation Analysis

**The Arnio Project Requirements:**
- Multiple Mac Mini servers running custom application
- Need automation for outage detection & auto-restart
- Need lightweight, affordable monitoring (not Datadog)
- Real-time alerts (Slack, email, webhooks)
- Server reliability and health visibility
- Team documentation for operations

**Why Sentinel Infrastructure is PERFECT for this:**
✅ Already multi-platform (Linux + macOS)
✅ Lightweight foundation role
✅ Flexible monitoring options
✅ Grafana (free) + Prometheus (free) = < $5/month vs Datadog ($500+)
✅ Git-based for team operations
✅ Documented playbooks for repeatable deployments

---

## Redesigned Architecture for macOS-Centric Deployment

### The Problem with Official Collections

**prometheus.prometheus collection** assumes systemd:
- ❌ Prometheus needs launchd wrapper
- ❌ Alertmanager needs launchd wrapper
- ❌ Node Exporter needs launchd wrapper

**Solution: Create Custom macOS Roles**

Instead of forking, we'll create lightweight Sentinel roles that:
1. Use `homebrew` for package installation
2. Use `launchd` property lists for service management
3. Mirror the Prometheus architecture but in macOS-native way
4. Reuse Grafana Agent (already works on macOS)

---

## Revised Deployment Model

```
┌─────────────────────────────────────────────────┐
│        Mac Mini Servers (Arnio Project)         │
├─────────────────────────────────────────────────┤
│                                                 │
│  sentinel.common (our custom role)              │
│  ├─ SSH hardening                               │
│  ├─ System optimization                         │
│  ├─ Audit logging                               │
│  └─ Health check scripts                        │
│                                                 │
│  sentinel.macos_monitoring (NEW)                │
│  ├─ Grafana Agent (via brew)                    │
│  ├─ Node Exporter (via brew + launchd)          │
│  ├─ Custom app health check script              │
│  └─ Auto-restart supervisor script              │
│                                                 │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│     Monitoring Backend (Linux or Cloud)         │
├─────────────────────────────────────────────────┤
│                                                 │
│  sentinel.prometheus (custom + official)        │
│  └─ Prometheus server (aggregates metrics)      │
│                                                 │
│  sentinel.alertmanager (custom + official)      │
│  └─ Routes alerts to Slack/email/webhooks       │
│                                                 │
│  grafana.grafana.grafana                        │
│  └─ Dashboards (connects to Prometheus)         │
│                                                 │
│  grafana.grafana.loki                           │
│  └─ Log aggregation from all servers            │
│                                                 │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│         Notifications & Visibility              │
├─────────────────────────────────────────────────┤
│  • Slack alerts                                 │
│  • Email notifications                          │
│  • Grafana dashboards (mobile-friendly)         │
│  • PagerDuty integration (optional)              │
└─────────────────────────────────────────────────┘
```

---

## What We Build

### Phase 1: macOS-Focused Foundation (THIS FIRST)

**New Roles to Create:**

1. **sentinel.macos_monitoring**
   - Install node_exporter via homebrew
   - Create launchd plist for node_exporter
   - Install Grafana Agent via homebrew
   - Configure service auto-start

2. **sentinel.app_health_check**
   - Custom bash script to check app status
   - Auto-restart logic with exponential backoff
   - Health check metrics export
   - Runs via launchd scheduler

3. **sentinel.system_hardening_macos**
   - macOS-specific security hardening
   - Firewall configuration (macOS built-in)
   - SSH key-based auth
   - Audit logging (macOS native)

### Phase 2: Monitoring Backend (Linux-based)

**Use Official Collections (NO changes needed):**
- `prometheus.prometheus.prometheus` (runs on Linux server)
- `prometheus.prometheus.alertmanager` (runs on Linux server)
- `grafana.grafana.grafana` (runs on Linux server)
- `grafana.grafana.loki` (runs on Linux server)

Mac minis send metrics → Linux Prometheus
Linux Prometheus → Grafana dashboards + Alertmanager → Slack/email

---

## Implementation Plan

### Step 1: Create Custom macOS Roles

**New directory structure:**
```
roles/
├── common/                    # Existing - OS-agnostic
├── macos_monitoring/          # NEW - Node exporter + Grafana Agent on macOS
├── app_health_check/          # NEW - Custom app monitoring
├── system_hardening_macos/    # NEW - macOS-specific security
└── macos_node_exporter/       # NEW - Lightweight Node Exporter launcher
```

**Key files to create:**

`roles/macos_monitoring/tasks/main.yml`:
```yaml
- name: Install node_exporter via homebrew
  homebrew:
    name: node_exporter
    state: present

- name: Create node_exporter launchd plist
  template:
    src: com.prometheus.node_exporter.plist.j2
    dest: /Library/LaunchDaemons/com.prometheus.node_exporter.plist
    mode: '0644'
  become: yes

- name: Start node_exporter service
  command: launchctl load /Library/LaunchDaemons/com.prometheus.node_exporter.plist
  become: yes
```

`roles/app_health_check/tasks/main.yml`:
```yaml
- name: Create app health check script
  template:
    src: check_app_health.sh.j2
    dest: /usr/local/bin/check_app_health.sh
    mode: '0755'

- name: Create launchd plist for health checks
  template:
    src: com.arnio.app_healthcheck.plist.j2
    dest: /Library/LaunchDaemons/com.arnio.app_healthcheck.plist
    mode: '0644'
  become: yes

- name: Load health check service
  command: launchctl load /Library/LaunchDaemons/com.arnio.app_healthcheck.plist
  become: yes
```

### Step 2: Create Custom Monitoring Scripts

**`check_app_health.sh`** - Monitor your custom app:
```bash
#!/bin/bash

APP_PID=$(pgrep -f "your_app_name")

if [ -z "$APP_PID" ]; then
    # App not running
    logger -t app_health "App is down, attempting restart"
    /path/to/app/restart.sh
    # Send metric to node_exporter textfile collector
    echo "app_running 0" > /var/lib/node_exporter/app_status.prom
else
    echo "app_running 1" > /var/lib/node_exporter/app_status.prom
fi
```

**Metrics to expose:**
- `app_running` (0 or 1)
- `app_restart_count` (counter)
- `app_last_restart_timestamp` (gauge)

### Step 3: Configure Monitoring Backend (Linux)

**Single Linux server (could be cloud VM, $5-10/month):**
- Prometheus (aggregates metrics from all Macs)
- Alertmanager (sends Slack/email alerts)
- Grafana (beautiful dashboards)
- Loki (centralized logging)

All run on Linux, all Mac minis send data to it.

### Step 4: Create Playbooks

**`playbooks/setup_macos_servers.yml`**
```yaml
- name: Setup Mac Mini Servers for Arnio
  hosts: macos_servers
  roles:
    - common                       # SSH, system hardening
    - macos_monitoring             # Node exporter + Grafana Agent
    - app_health_check             # Custom app monitoring
    - system_hardening_macos       # macOS-specific security
```

**`playbooks/setup_monitoring_backend.yml`**
```yaml
- name: Setup Monitoring Backend
  hosts: monitoring_servers
  roles:
    - common                       # Foundation
    - prometheus.prometheus.prometheus
    - prometheus.prometheus.alertmanager
    - grafana.grafana.grafana
    - grafana.grafana.loki
```

---

## Why This Works for Arnio

| Requirement | Our Solution |
|-------------|---|
| Detect outages | Custom health check script + metrics |
| Auto-restart app | launchd supervisor script |
| Affordable monitoring | Prometheus + Grafana (free) |
| Real-time alerts | Alertmanager → Slack/email/webhooks |
| Mac Mini native | launchd services, homebrew packages |
| Multiple servers | Metrics aggregated in one Prometheus |
| Documentation | Playbooks are self-documenting |
| Easy operations | One playbook deploy, git history for changes |

---

## Cost Comparison

### Current (Datadog)
- $500+/month for 5 servers
- $6,000+/year
- Limited customization

### Sentinel Infrastructure
- **Monitoring backend server**: $5-10/month (DigitalOcean/AWS/UpCloud)
- **Mac minis**: Already owned
- **Total**: ~$60-120/year
- **ROI**: 50x cheaper than Datadog
- **Bonus**: Full customization & control

---

## Next Steps

### To Implement This:

1. **Create 3 new custom roles** (2-3 hours work)
   - `sentinel.macos_monitoring`
   - `sentinel.app_health_check`
   - `sentinel.system_hardening_macos`

2. **Create launchd templates** (1-2 hours work)
   - Node exporter plist
   - Health check plist
   - Auto-restart supervisor plist

3. **Create custom monitoring scripts** (2-3 hours work)
   - App health check script
   - Auto-restart logic
   - Metrics export

4. **Test on one Mac Mini** (1-2 hours work)
   - Deploy and validate
   - Check metrics in Prometheus
   - Test alerts to Slack

5. **Document procedures** (1 hour work)
   - How to add new Mac Mini
   - How to troubleshoot
   - How to modify health checks

**Total Implementation Time**: ~8-12 hours of focused work

---

## Files to Create

```
roles/
├── macos_monitoring/
│   ├── tasks/main.yml
│   ├── templates/
│   │   ├── com.prometheus.node_exporter.plist.j2
│   │   └── node_exporter_config.j2
│   └── defaults/main.yml
│
├── app_health_check/
│   ├── tasks/main.yml
│   ├── templates/
│   │   ├── check_app_health.sh.j2
│   │   ├── com.arnio.app_healthcheck.plist.j2
│   │   └── app_restart.sh.j2
│   └── defaults/main.yml
│
└── system_hardening_macos/
    ├── tasks/main.yml
    ├── templates/
    │   └── firewall_rules.sh.j2
    └── defaults/main.yml
```

---

## Summary

**Sentinel Infrastructure IS suitable for the Arnio project, with one critical addition:**

**Create 3 macOS-specific custom roles** that:
1. Use homebrew for package management
2. Use launchd for service management
3. Mirror Prometheus/Node Exporter functionality on macOS
4. Integrate with Linux-based monitoring backend

This approach:
✅ Reuses our existing foundation
✅ Leverages official collections for monitoring backend
✅ Provides true macOS-native automation
✅ Costs 50x less than Datadog
✅ Gives Arnio complete control
✅ Scales to 10, 50, 100+ Mac minis easily
✅ Integrates with Puppet later

**Should I implement these 3 new roles now?**
