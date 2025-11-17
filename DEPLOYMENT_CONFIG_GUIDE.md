# Deployment Configuration Guide

**Date**: November 17, 2025
**Status**: Pre-Deployment Configuration Guide
**Purpose**: Configure critical settings before staging/production deployment

---

## Step 1: Review & Customize Alert Thresholds

Alert thresholds should match your environment's baseline performance. Review and adjust these values in `roles/common/defaults/main.yml`:

### CPU Alerts
```yaml
alert_cpu_high: 85          # Trigger warning at 85% CPU usage
alert_cpu_critical: 95      # Trigger critical at 95% CPU usage
```

**Recommendation**:
- For batch processing: Keep high=85, critical=95
- For real-time systems: Reduce to high=75, critical=85
- For development: Increase to high=90, critical=98

### Memory Alerts
```yaml
alert_memory_high: 85       # Trigger warning at 85% memory
alert_memory_critical: 95   # Trigger critical at 95% memory
```

**Recommendation**:
- Production: high=80, critical=90 (conservative)
- Development: high=85, critical=95 (relaxed)

### Disk Space Alerts
```yaml
alert_disk_warning: 80      # Warning at 80% capacity
alert_disk_high: 90         # High alert at 90% capacity
alert_disk_critical: 95     # Critical at 95% capacity
```

**Recommendation**:
- Database servers: Reduce to warning=70, high=80, critical=90
- Application servers: warning=80, high=90, critical=95
- Log servers: warning=85, high=92, critical=98

### Network Alerts
```yaml
alert_latency_high: 100     # Warning: 100ms latency
alert_latency_critical: 500 # Critical: 500ms latency
alert_packet_loss: 1        # Warning: 1% packet loss
```

**Recommendation**:
- Cloud environments: Increase latency threshold to 200/1000ms
- On-premises: Keep strict at 50/300ms
- WAN links: Adjust based on SLA (typically 100-500ms)

### Authentication Alerts
```yaml
alert_failed_logins: 5      # Warning after 5 failed attempts
alert_sudo_spike: 300       # Alert if sudo usage increases 300%
```

**Recommendation**:
- Strict security: Keep at 3-5 failed attempts
- High-volume systems: Increase to 10-20
- Development: Disable by setting to 999

### Custom Thresholds to Consider
```yaml
# Add to defaults/main.yml for your environment:
alert_load_high: "{{ ansible_processor_vcpus | default(4) * 1.5 }}"
alert_load_critical: "{{ ansible_processor_vcpus | default(4) * 2.5 }}"
alert_connection_timeout: 10  # seconds
alert_service_restart_threshold: 5  # restarts in 24 hours
```

---

## Step 2: Configure Notification Channels

### 2.1 Email Configuration

Enable email alerts in `defaults/main.yml`:

```yaml
monitoring_email_enabled: true
monitoring_email_from: "alerts@example.com"
monitoring_email_to: "ops@example.com,on-call@example.com"
monitoring_smtp_server: "smtp.gmail.com"  # or your mail server
monitoring_smtp_port: 587
monitoring_smtp_user: "alerts@example.com"
monitoring_smtp_password: "{{ vault_smtp_password }}"  # Use Ansible Vault
monitoring_smtp_tls: true
```

**Setup Steps**:
1. Create email account for alerts
2. Generate app-specific password (for Gmail, use 16-char app password)
3. Store in Ansible Vault: `ansible-vault edit group_vars/all.yml`
4. Add: `vault_smtp_password: "your-app-password"`
5. Test: `echo "test" | mail -s "Test Alert" ops@example.com`

### 2.2 Slack Configuration

Enable Slack integration:

```yaml
monitoring_slack_enabled: true
monitoring_slack_webhook_url: "{{ vault_slack_webhook }}"  # Store in Vault
```

**Setup Steps**:
1. Create Slack workspace (or use existing)
2. Create channel: `#alerts-critical`, `#alerts-ops`, `#alerts` (adjust as needed)
3. Go to Slack App Directory → Incoming Webhooks
4. Create webhook, select channels
5. Copy webhook URL to Vault:
   ```bash
   ansible-vault edit group_vars/all.yml
   ```
   Add:
   ```yaml
   vault_slack_webhook: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
   ```

**Test Slack Integration**:
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test alert from Ansible"}' \
  $SLACK_WEBHOOK_URL
```

### 2.3 PagerDuty Configuration (Optional)

For critical production incidents:

```yaml
monitoring_pagerduty_enabled: true
monitoring_pagerduty_token: "{{ vault_pagerduty_token }}"
monitoring_pagerduty_escalation_policy: "your-escalation-policy-id"
monitoring_pagerduty_service_key: "{{ vault_pagerduty_service_key }}"
```

**Setup Steps**:
1. Create PagerDuty account or use existing
2. Create Integration Key for Events API v2
3. Set escalation policy (who to notify first, second, etc.)
4. Store in Vault:
   ```yaml
   vault_pagerduty_token: "your-api-token"
   vault_pagerduty_service_key: "your-service-key"
   ```

### 2.4 SMS Notifications (Optional)

For truly critical alerts:

```yaml
monitoring_sms_enabled: true
monitoring_sms_provider: "twilio"  # or "sns" for AWS
monitoring_sms_account_id: "{{ vault_twilio_account }}"
monitoring_sms_auth_token: "{{ vault_twilio_token }}"
monitoring_sms_from_number: "+1-555-0100"
```

---

## Step 3: Customize Compliance Settings

### Enable/Disable Compliance Frameworks

```yaml
# In defaults/main.yml - adjust based on your requirements:

compliance_fedramp_enabled: true      # Federal systems
compliance_hipaa_enabled: false       # Healthcare data
compliance_pci_dss_enabled: false     # Payment cards
compliance_soc2_enabled: false        # Service providers
compliance_nist_sp800_53_enabled: true # Standard security

# Scanning frequency
compliance_aide_scan_time: "03:00"    # Daily at 3 AM
compliance_weekly_scan_time: "01:00"  # Weekly Sunday at 1 AM
```

### Configure Compliance Exception Handling

```yaml
compliance_exception_enabled: true
compliance_remediation_enabled: false  # Don't auto-fix, manual review first
compliance_audit_tamper_detection: true
compliance_audit_check_interval: "hourly"
```

---

## Step 4: Performance Tuning for Your Environment

### Database Performance

Adjust based on your database:

```yaml
# PostgreSQL (8GB RAM example)
postgres_shared_buffers: "2GB"        # 25% of RAM
postgres_cache_size: "6GB"            # 75% of RAM
postgres_work_mem: "256MB"
postgres_max_conn: 200

# MySQL (8GB RAM example)
mysql_buffer_pool: "6GB"              # 75% of RAM
mysql_tmp_table: "512M"
mysql_max_conn: 300
```

**Calculation Guide**:
- Shared Buffers: 25% of system RAM
- Effective Cache: 75% of system RAM
- Work Memory: (RAM / max_connections) / 2

### Storage Optimization

```yaml
storage_io_scheduler: "mq-deadline"   # For SSD/NVMe
# Or use: "bfq" for traditional disks
storage_queue_depth: 256              # For NVMe (increase from 128)
storage_readahead: 4096               # For NVMe (increase from 2048)
```

---

## Step 5: Create Environment-Specific Configurations

### Staging Environment (roles/group_vars/staging.yml)

```yaml
---
# Staging-specific overrides
alert_cpu_high: 90                    # More relaxed thresholds
alert_memory_high: 90
compliance_remediation_enabled: true  # Test auto-remediation
monitoring_slack_enabled: true
monitoring_slack_webhook_url: "{{ vault_slack_webhook_staging }}"
```

### Production Environment (roles/group_vars/production.yml)

```yaml
---
# Production-specific settings
alert_cpu_high: 80                    # Strict thresholds
alert_memory_high: 80
alert_disk_critical: 90
compliance_remediation_enabled: false # Manual review required
monitoring_pagerduty_enabled: true
monitoring_email_enabled: true
kernel_hardening_enabled: true
password_policy_enabled: true
compliance_scanning_enabled: true
```

---

## Step 6: Deployment Checklist

### Pre-Staging Deployment

- [ ] Review all alert thresholds
- [ ] Customize thresholds for your workload
- [ ] Create email account for alerts
- [ ] Create Slack channels for alerts
- [ ] Generate Slack webhook URL
- [ ] Store secrets in Ansible Vault
- [ ] Create staging environment group_vars
- [ ] Test email delivery
- [ ] Test Slack integration
- [ ] Review compliance requirements
- [ ] Document any custom exceptions

### Staging Deployment (24-hour validation)

- [ ] Run playbook on staging environment
- [ ] Validate kernel hardening applied (no errors)
- [ ] Check password policy enforced
- [ ] Verify storage mounts changed correctly
- [ ] Monitor compliance scanning
- [ ] Verify alerts trigger appropriately
- [ ] Test alert delivery channels
- [ ] Confirm performance impact within expectations
- [ ] Review compliance reports
- [ ] Collect baseline metrics for 24 hours

### Production Rollout (Phased approach)

**Phase 1: Non-Critical Systems (Week 1)**
- [ ] Deploy to 2-3 non-production servers
- [ ] Monitor for 48 hours
- [ ] Resolve any issues

**Phase 2: Development Systems (Week 2)**
- [ ] Deploy to development environment
- [ ] Gather feedback from development team
- [ ] Adjust thresholds if needed

**Phase 3: Production Systems (Week 3-4)**
- [ ] Deploy to 25% of production (Phase 3a)
- [ ] Monitor for 48 hours
- [ ] Deploy to 50% of production (Phase 3b)
- [ ] Monitor for 48 hours
- [ ] Deploy to 100% of production (Phase 3c)

### Post-Deployment (Ongoing)

- [ ] Monitor alerts for 1 week
- [ ] Adjust thresholds based on baseline data
- [ ] Review compliance reports daily
- [ ] Train ops team on new features
- [ ] Document any custom configurations
- [ ] Schedule monthly compliance audits
- [ ] Plan quarterly security reviews

---

## Step 7: Monitoring & Adjustments

### Daily Operations

```bash
# Check compliance status
sudo /opt/compliance-frameworks/fedramp-check.sh

# View recent alerts
tail -50 /var/log/auth.log

# Monitor disk usage
sudo /usr/local/bin/check-disk-usage.sh

# Check system performance
vmstat 1 5
iostat -x 1 5
```

### Weekly Reviews

- Review compliance reports in `/var/log/compliance/`
- Analyze alert patterns in monitoring system
- Verify backup recovery tests completed
- Check for security updates needed

### Threshold Adjustment Strategy

If alerts are firing too frequently:
1. Increase thresholds by 5-10%
2. Monitor for 1 week
3. Adjust again if needed

If alerts are not firing enough:
1. Decrease thresholds by 5-10%
2. Monitor for 1 week
3. Adjust again if needed

**Example**: CPU at 87% triggering too many alerts?
```yaml
# Adjust from 85 to 88
alert_cpu_high: 88
# Test change
ansible-playbook site.yml -t monitoring_tuning
```

---

## Troubleshooting

### Email Alerts Not Working

```bash
# Test SMTP connection
telnet smtp.gmail.com 587

# Check mail logs
sudo tail -50 /var/log/mail.log

# Test sendmail manually
echo "test" | mail -s "Test" ops@example.com
```

### Slack Integration Failures

```bash
# Test webhook
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test"}' \
  https://hooks.slack.com/services/YOUR/WEBHOOK

# Check Slack app permissions
# Ensure bot has "chat:write" permission
```

### Compliance Scanning Issues

```bash
# Check compliance status
sudo /opt/compliance-frameworks/fedramp-check.sh

# View detailed logs
sudo tail -100 /var/log/compliance/fedramp-check-*.log

# Verify AIDE database
sudo aide --check | tail -20
```

---

## Next Steps After Deployment

1. **Week 1**: Monitor alerts, adjust thresholds
2. **Week 2**: Review compliance reports
3. **Week 3**: Conduct security audit
4. **Week 4**: Document custom configurations
5. **Month 2+**: Plan enhancement phasesFocus on:
   - Implementing anomaly detection
   - Adding custom compliance exceptions
   - Tuning performance parameters
   - Establishing SLO targets

---

**This guide ensures smooth deployment with properly configured alerts and monitoring.**

