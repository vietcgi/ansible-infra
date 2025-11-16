# Service Level Agreements & Objectives

## Overview

This document defines Service Level Agreements (SLAs) and Service Level Objectives (SLOs) for ansible-infra infrastructure automation platform. These targets guide operational decisions, capacity planning, and incident response priorities.

---

## SLA vs SLO Definitions

### Service Level Agreement (SLA)
Contractual commitment with business partners/customers. Violations result in penalties or credits.

### Service Level Objective (SLO)
Internal target for engineering team. Guides operational decisions and resource allocation.

### Service Level Indicator (SLI)
Actual measured metric reflecting service performance.

---

## Infrastructure Availability SLOs

### Primary Infrastructure (Production)

| Service | SLO | Downtime Budget | Measurement |
|---------|-----|-----------------|-------------|
| **Configuration Management** | 99.9% | 43.2 min/month | Playbook execution success rate |
| **SSH Access** | 99.95% | 21.6 min/month | Successful authentication rate |
| **Monitoring Stack** | 99.5% | 216 min/month | Prometheus + Grafana uptime |
| **Log Aggregation** | 99.0% | 432 min/month | Log ingestion success rate |
| **Vault (Secrets)** | 99.99% | 4.3 min/month | Vault API availability |

### Staging Environment

| Service | SLO | Purpose |
|---------|-----|---------|
| **Uptime** | 95% | Testing and validation |
| **RTO** | 1 hour | Acceptable recovery time |
| **RPO** | 4 hours | Data loss acceptable |

### Development Environment

| Service | SLO | Purpose |
|---------|-----|---------|
| **Uptime** | 90% | Development and testing |
| **RTO** | 24 hours | Not business critical |
| **RPO** | 24 hours | Non-critical data |

---

## Operational SLOs

### Deployment Performance

| Metric | SLO | Target |
|--------|-----|--------|
| **Playbook execution time** | p99 < 10 min | 99% of runs complete in time |
| **Configuration convergence** | < 2 min avg | Idempotent application |
| **Role application latency** | p95 < 5 sec | Per-host configuration time |
| **Deployment approval time** | < 1 hour | From submission to approval |
| **Deployment failure rate** | < 0.5% | 99.5% success rate |

### Change Management

| Metric | SLO | Target |
|--------|-----|--------|
| **Change review time** | < 4 hours | Initial review by team |
| **Emergency change approval** | < 30 min | Fast-track for critical fixes |
| **Change rollback time** | < 5 minutes | Quick revert if issues detected |
| **Change documentation** | 100% | All changes documented |
| **Post-change verification** | 100% | Smoke tests after all changes |

### Incident Response

| Metric | SLO | Definition |
|--------|-----|-----------|
| **Acknowledgment time** | < 15 min | From alert to first response |
| **Initial investigation** | < 30 min | Root cause identified |
| **Mitigation start time** | < 1 hour | Remediation begins |
| **Resolution time** | Varies by severity | See incident response plan |
| **Post-incident report** | 24 hours | Documented after resolution |

---

## Severity-Based Response SLOs

### Critical Severity (CVSS 9.0-10.0)

**Characteristics**:
- Complete system unavailability
- Data loss imminent
- Security breach active
- Multiple services affected

**SLOs**:

| Stage | SLO | Details |
|-------|-----|---------|
| **Detection** | < 5 min | Alert fires and is acknowledged |
| **Response** | < 5 min | On-call engineer begins assessment |
| **Mitigation** | < 30 min | Issue contained, impact stopped |
| **Resolution** | < 2 hours | Service restored to normal |
| **Post-incident** | < 24 hours | Report completed, lessons learned |

**Example Escalation**:
```
On-call Engineer (immediate)
  ↓ (if not resolved in 15 min)
Team Lead + Director
  ↓ (if not resolved in 30 min)
CTO + Full Team
  ↓ (notify CEO and executive team)
```

### High Severity (CVSS 7.0-8.9)

**Characteristics**:
- Partial service unavailability
- Single component failure
- Degraded performance
- Limited user impact

**SLOs**:

| Stage | SLO |
|-------|-----|
| **Acknowledgment** | < 30 min |
| **Investigation** | < 1 hour |
| **Mitigation** | < 2 hours |
| **Resolution** | < 4 hours |
| **Post-incident report** | < 48 hours |

### Medium Severity (CVSS 4.0-6.9)

**Characteristics**:
- Minor degradation
- Non-critical features affected
- Workaround available

**SLOs**:

| Stage | SLO |
|-------|-----|
| **Acknowledgment** | < 2 hours |
| **Investigation** | < 4 hours |
| **Resolution** | < 8 hours |
| **Post-incident report** | < 72 hours |

### Low Severity (CVSS 0.1-3.9)

**Characteristics**:
- Cosmetic issues
- Documentation problems
- Minor inefficiencies

**SLOs**:

| Stage | SLO |
|-------|-----|
| **Acknowledgment** | < 24 hours |
| **Resolution** | Best effort |
| **Post-incident report** | As needed |

---

## Performance SLOs

### Ansible Playbook Execution

```yaml
# p50 (median) - 50% of runs complete faster
playbook_execution_p50:
  target: 2 minutes
  measurement: median execution time
  frequency: per playbook per run

# p95 (95th percentile) - 95% complete faster
playbook_execution_p95:
  target: 5 minutes
  measurement: 95th percentile

# p99 (99th percentile) - 99% complete faster
playbook_execution_p99:
  target: 10 minutes
  measurement: 99th percentile
```

### Configuration Drift Detection

| Metric | SLO | Details |
|--------|-----|---------|
| **Detection time** | < 15 min | From drift to alert |
| **Convergence time** | < 10 min | Drift correction via playbook |
| **Drift detection frequency** | Every 30 min | Regular drift checks |

### SSH Authentication

| Metric | SLO |
|--------|-----|
| **Authentication success rate** | 99.95% |
| **Connection establishment time** | < 5 sec p95 |
| **Key rotation completion** | < 4 hours per host |

---

## Availability SLI Calculations

### Monthly Uptime Percentage

```
Uptime % = (Total Minutes in Month - Downtime Minutes) / Total Minutes in Month × 100

Examples for 30-day month (43,200 minutes):
- 99.9% uptime = 43.2 minutes downtime/month allowed
- 99.95% uptime = 21.6 minutes downtime/month allowed
- 99.99% uptime = 4.32 minutes downtime/month allowed
```

### Tracking Downtime

Include in calculation:
- ✓ Planned maintenance window
- ✓ Unplanned outages
- ✓ Partial service degradation (% of service)
- ✗ Incidents not affecting monitored services

---

## Error Budget

### Understanding Error Budget

Error budget = (1 - SLO) × number of time units

```
Example for 99.9% SLO:
Error budget per month = 0.1% × 43,200 min = 43.2 minutes

You have 43.2 minutes of acceptable downtime per month.
When error budget exhausted → focus on stability, freeze new features.
```

### Error Budget Policy

| Budget Remaining | Action |
|-----------------|--------|
| **> 50%** | Normal operations, proceed with deployments |
| **25-50%** | Cautious deployments, increase monitoring |
| **10-25%** | High alert status, emergency changes only |
| **< 10%** | Critical status, all changes frozen except critical fixes |
| **Exhausted** | Postmortem required before resuming changes |

---

## SLO Measurement & Monitoring

### Key Metrics to Track

1. **Infrastructure Availability**
   ```prometheus
   # Prometheus queries for monitoring
   up{job="ansible"}  # Host up/down status
   ansible_plays_failed  # Failed playbooks
   ansible_plays_ok  # Successful plays
   ```

2. **Performance Metrics**
   ```prometheus
   playbook_execution_seconds  # Execution time distribution
   configuration_drift_detected  # Drift incidents
   ssh_auth_success_rate  # SSH authentication success
   ```

3. **Error Rates**
   ```prometheus
   ansible_failures_total  # Total failures
   rate(ansible_failures_total[5m])  # Failure rate
   ```

### SLO Dashboard

Create Grafana dashboards showing:
- Real-time uptime percentage
- Error budget consumption
- P50/P95/P99 latencies
- Service availability by component
- Trend analysis (weekly, monthly)

### Alerting Thresholds

```yaml
# Alerting on SLO violations
groups:
  - name: slo
    rules:
      # Alert when uptime drops below 99.9%
      - alert: AvailabilityBelowSLO
        expr: |
          (count(up{job="ansible"} == 1) / count(up{job="ansible"})) < 0.999
        for: 5m
        annotations:
          summary: "Availability below 99.9% SLO"

      # Alert when error budget exhausted
      - alert: ErrorBudgetExhausted
        expr: |
          rate(ansible_failures_total[30d]) > 0.001
        annotations:
          summary: "Error budget exhausted for month"
```

---

## SLO Targets by Service Tier

### Tier 1: Critical Infrastructure
- **SLO**: 99.99% (4 nines)
- **Downtime budget**: 4.3 min/month
- **Examples**: Vault, core Ansible controller
- **Tolerance**: Zero unplanned downtime acceptable

### Tier 2: Core Services
- **SLO**: 99.9% (3 nines)
- **Downtime budget**: 43.2 min/month
- **Examples**: SSH, configuration management
- **Tolerance**: Brief outages acceptable with quick recovery

### Tier 3: Supporting Services
- **SLO**: 99.5%
- **Downtime budget**: 216 min/month
- **Examples**: Monitoring, logging
- **Tolerance**: Short outages acceptable

### Tier 4: Non-Critical Services
- **SLO**: 99% or less
- **Downtime budget**: 7+ hours/month
- **Examples**: Development tools, documentation
- **Tolerance**: Extended outages acceptable

---

## SLA Definition for External Commitments

### Service Level Agreement Template

If offering services externally, define:

```
SERVICE LEVEL AGREEMENT
=======================

Service: [Description]
Period: [Measurement period - typically monthly]
Effective Date: [Start date]

SERVICE AVAILABILITY:
- Uptime Target: [e.g., 99.9%]
- Measurement Window: [e.g., calendar month]
- Exclusions: [Scheduled maintenance, customer actions, etc.]

SUPPORT RESPONSE TIMES:
- Critical (P1): [e.g., 1 hour]
- High (P2): [e.g., 4 hours]
- Medium (P3): [e.g., 8 hours]
- Low (P4): [e.g., 24 hours]

REMEDIES FOR SLA VIOLATION:
- 99.0-99.9% uptime: 5% monthly credit
- 98.0-99.0% uptime: 10% monthly credit
- < 98.0% uptime: 25% monthly credit

REPORTING:
- Monthly availability reports provided within 5 days
- Written notification of breaches within 24 hours
```

---

## SLO Review & Adjustment

### Quarterly Review

Every quarter:
1. **Analyze metrics**
   - Did we meet SLOs?
   - Which metrics exceeded/missed targets?
   - What caused failures?

2. **Capacity planning**
   - Are infrastructure resources adequate?
   - Do we need to scale?
   - Are we over-provisioned?

3. **Trend analysis**
   - Improving or degrading?
   - Seasonal patterns?
   - Growth trajectory?

4. **Adjust if needed**
   - Are SLOs realistic?
   - Do they align with business needs?
   - Update targets for next period

### Annual Review

Once per year:
1. Strategic alignment - Do SLOs match business goals?
2. Cost analysis - Cost per SLO target percentage
3. Technology updates - New capabilities enabling better SLOs?
4. Team capacity - Sufficient staffing for SLO targets?

---

## Cost of SLOs

Higher SLOs cost more due to:
- **Infrastructure**: Redundancy, failover systems, backup systems
- **Labor**: On-call support, incident response, automation
- **Testing**: More comprehensive testing required
- **Monitoring**: More detailed monitoring and alerting

```
Uptime %    Annual Downtime    Cost Factor
99%         3.7 days          1.0x
99.5%       1.8 days          1.2x
99.9%       8.8 hours         1.5x
99.95%      4.4 hours         2.0x
99.99%      52.6 minutes      3.0x
99.999%     5.3 minutes       5.0x
```

---

## SLO Communication

### Team Communication

- **Weekly**: SLO performance dashboard review
- **Monthly**: SLA/SLO report to leadership
- **Quarterly**: SLO analysis and adjustments
- **Annually**: Strategic SLO planning

### Customer Communication

- **Proactive notification** of planned maintenance 72 hours in advance
- **Real-time status page** showing current and historical uptime
- **Monthly reports** detailing SLO performance and trends
- **Incident notifications** for any SLA-impacting events

---

## Emergency Contacts & Escalation

Maintain current list of:
- On-call engineer contact (24/7)
- Team lead escalation
- Director/VP escalation
- Executive escalation for Level 3-4 incidents

Update quarterly and test annually.

---

## Documentation

**Last Updated**: November 15, 2025
**Version**: 1.0.0
**Status**: Production-Ready
**Next Review**: February 15, 2026

This document guides operational decisions and is reviewed quarterly.
