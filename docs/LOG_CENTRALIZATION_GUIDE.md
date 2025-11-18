# Log Centralization and Shipping Guide

**Date**: November 17, 2025
**Version**: 1.0
**Status**: Production Ready

---

## Overview

Log shipping and centralization is **now enabled by default** in the common role. This provides:

 **Local log collection** (always active) - collects system logs, auth logs, audit logs
 **Central log aggregation** (optional) - ships logs to Elasticsearch/Logstash if configured
 **Graceful fallback** - works fine without external log server, stores locally
 **Zero disruption** - existing deployments can enable without outages

---

## Default Behavior

### Without External Log Server (Default)

```yaml
log_shipping_enabled: true
log_shipping_elasticsearch_host: "localhost"  # No external server
```

**What happens:**
- Logs are collected locally via rsyslog
- Stored in `/var/log/` on each system
- Log retention: 30 days (configurable)
- No external dependencies needed

### With External Elasticsearch/Logstash

```yaml
log_shipping_enabled: true
log_shipping_elasticsearch_host: "logs.example.com"
log_shipping_elasticsearch_port: 9200
```

**What happens:**
- Filebeat 8.12+ installed automatically
- Logs shipped real-time to Elasticsearch
- Index prefix: `logs-YYYY.MM.DD`
- Index Lifecycle Management (ILM) enabled
- Logs still stored locally as fallback

---

## Configuration Options

### Basic Settings

```yaml
# Master enable flag
log_shipping_enabled: true                  # Enable log collection/shipping

# Transport method
log_shipping_use_filebeat: true             # Use Filebeat (recommended)
                                            # false = rsyslog fallback

# Centralization servers (set to non-localhost to enable)
log_shipping_elasticsearch_host: "logs.example.com"
log_shipping_elasticsearch_port: 9200

log_shipping_logstash_host: "logs.example.com"
log_shipping_logstash_port: 5000
```

### Log Collection Options

```yaml
# What gets shipped
log_shipping_collect_syslog: true      # System messages
log_shipping_collect_auth: true         # Authentication logs
log_shipping_collect_audit: true        # Audit logs (auditd)
log_shipping_collect_kern: true         # Kernel messages
log_shipping_collect_systemd: true      # Systemd journal
```

### Retention & Index Settings

```yaml
# Local retention
log_shipping_retention_days: 30         # Keep local logs for N days

# Elasticsearch index configuration
log_shipping_index_prefix: "logs"       # Index name: logs-YYYY.MM.DD
log_shipping_index_lifecycle_enabled: true  # Use ILM for auto-cleanup
log_shipping_index_lifecycle_policy: "logs" # ILM policy name

# Environment tagging
log_shipping_environment: "production"  # Tag logs with environment
```

### Filebeat Configuration

```yaml
# Filebeat version
log_shipping_filebeat_version: "8.12.0"

# Buffer settings
log_shipping_buffer_size: "4096"        # Buffer before sending
```

---

## Usage Scenarios

### Scenario 1: Basic Deployment (Local Logs Only)

 **Best for**: Small deployments, testing, development

```yaml
# defaults/main.yml or group_vars/all
log_shipping_enabled: true
# Leave elasticsearch_host as "localhost" to use local logging only
```

**What you get:**
- Logs collected and stored locally
- No external dependencies
- 30-day retention
- Access logs via: `tail -f /var/log/syslog`

### Scenario 2: Central Log Aggregation

 **Best for**: Production, multiple systems, compliance

**Prerequisites:**
1. Elasticsearch cluster (or Logstash) deployed
2. Network access from all servers to log server
3. Sufficient storage for log volume

**Configuration:**

```yaml
# roles/common/defaults/main.yml
log_shipping_enabled: true
log_shipping_elasticsearch_host: "logs.example.com"
log_shipping_elasticsearch_port: 9200

# Or use Logstash
log_shipping_logstash_host: "logs.example.com"
log_shipping_logstash_port: 5000
```

**Deployment:**
```bash
# Deploy will automatically:
# 1. Install Filebeat 8.12
# 2. Configure log collection
# 3. Connect to Elasticsearch
# 4. Create index templates
# 5. Start log shipping

ansible-playbook playbook.yml -i inventory
```

**Verification:**
```bash
# On any client:
systemctl status filebeat
journalctl -u filebeat -f

# On Elasticsearch:
curl http://logs.example.com:9200/_cat/indices
# Should show: logs-YYYY.MM.DD indices
```

### Scenario 3: Hybrid (Local + Central with Fallback)

 **Best for**: High-reliability requirements

```yaml
log_shipping_enabled: true
log_shipping_elasticsearch_host: "logs.example.com"
log_shipping_elasticsearch_port: 9200

# If ES unavailable:
# - Logs still collected locally
# - Queued in Filebeat buffer
# - Shipped when ES recovers
```

**Monitoring:**
```bash
# Check Filebeat connection status
filebeat status

# View queue depth if ES is down
journalctl -u filebeat | grep queue
```

---

## Log Types Collected

### System Logs (syslog)
- General system messages
- Service logs
- Application output
- **Location**: `/var/log/syslog` (Debian) or `/var/log/messages` (RHEL)

### Authentication Logs (auth)
- SSH login attempts
- sudo usage
- User creation/deletion
- **Location**: `/var/log/auth.log` (Debian) or `/var/log/secure` (RHEL)

### Audit Logs (auditd)
- System calls
- File access
- Privilege escalation
- **Enabled by**: `audit.yml` task (always enabled)

### Kernel Logs (kern)
- Kernel messages
- Hardware events
- Module loading/unloading
- **Source**: `/proc/kmsg`

### Systemd Journal (systemd)
- All unit status changes
- Service restarts
- Boot/shutdown events
- **Command**: `journalctl`

---

## Elasticsearch Index Structure

When logs are shipped to Elasticsearch, they're stored in daily indices:

```
logs-2025.11.17 (November 17)
logs-2025.11.18 (November 18)
logs-2025.11.19 (November 19)
...
```

### ILM (Index Lifecycle Management)

With `log_shipping_index_lifecycle_enabled: true`, indices automatically:

```
Logs for < 30 days  → Warm tier (searchable)
Logs for 30+ days   → Cold tier (archived)
Logs for 90+ days   → Delete (if configured)
```

Benefits:
- Automatic cleanup
- Cost optimization
- Storage management

---

## Troubleshooting

### Filebeat Not Starting

```bash
# Check service status
systemctl status filebeat

# View logs
journalctl -u filebeat -n 50

# Test configuration
filebeat test config
```

**Common issue**: Elasticsearch not available
```bash
# Solution: Ensure ES server is reachable
curl http://logs.example.com:9200

# Filebeat will buffer logs until ES is available
```

### Logs Not Appearing in Elasticsearch

```bash
# Verify Filebeat is running
systemctl is-active filebeat

# Check if Filebeat can connect to ES
filebeat test output

# View Filebeat status
curl http://localhost:5066/stats
```

**Common issue**: Network firewall blocking port 9200
```bash
# From client: Check connectivity
telnet logs.example.com 9200

# From server: Check listening port
netstat -tlnp | grep 9200
```

### High Disk Usage

```bash
# Check log sizes
du -sh /var/log/

# Reduce retention
log_shipping_retention_days: 7  # Down from 30

# Rotate logs manually
logrotate -f /etc/logrotate.conf
```

### Logs Stuck in Queue

If Elasticsearch unavailable, logs buffer in Filebeat:

```bash
# Check queue status
journalctl -u filebeat | grep -i queue

# Monitor queue size
filebeat test output

# Manually flush (forces retry)
systemctl restart filebeat
```

---

## Performance Impact

### CPU
- Filebeat: <1% (lightweight)
- rsyslog: <1% (already running)

### Disk
- Local logs: ~100 MB/day per system (depends on activity)
- Elasticsearch index: ~1 GB/day per 100 active systems

### Network
- Filebeat: ~500 KB/sec per system (depends on log volume)
- Bulk indexing reduces overhead

### Memory
- Filebeat: ~50-100 MB
- Buffer (if ES down): Up to `buffer_size` × number of lines

---

## Security Considerations

### Log Data Privacy

⚠️ **Logs contain sensitive information:**
- Usernames (auth logs)
- IP addresses (connection logs)
- Error messages (application logs)
- System configuration (kernel logs)

**Recommendations:**
-  Use TLS for log shipping to ES
-  Restrict access to log server
-  Implement log retention policies
-  Encrypt logs at rest in Elasticsearch
-  Redact sensitive patterns before shipping

### Authentication to Elasticsearch

If Elasticsearch requires authentication:

```yaml
log_shipping_elasticsearch_username: "logs-user"
log_shipping_elasticsearch_password: "{{ vault_elasticsearch_password }}"
log_shipping_elasticsearch_tls_enabled: true
```

### Log Server Access Control

**Elasticsearch should NOT be publicly accessible:**

```bash
#  Good: Firewall blocks external access
firewall-cmd --add-rich-rule='rule family="ipv4"
  source address="10.0.0.0/8" port protocol="tcp" port="9200" accept'

# ❌ Bad: Exposed to internet
curl http://ELASTICSEARCH_IP:9200/_cat/indices
# Would expose all logs!
```

---

## Monitoring & Alerting

### Key Metrics to Monitor

1. **Filebeat Health**
   - Is service running?
   - Is it connected to Elasticsearch?
   - Are logs being shipped?

2. **Log Volume**
   - Bytes/day shipped
   - Events/day indexed
   - Average log size

3. **Elasticsearch Storage**
   - Index size
   - Disk usage
   - ILM policy execution

4. **Latency**
   - Time from log creation to index
   - Queue depth if ES is unavailable

### Alert Examples

```yaml
# Alert if Filebeat down
- alert: FilebeadDown
  expr: up{job="filebeat"} == 0
  for: 5m

# Alert if Elasticsearch unreachable
- alert: ElasticsearchDown
  expr: elasticsearch_up == 0
  for: 5m

# Alert if log queue growing (ES down)
- alert: FilebeadQueueFull
  expr: filebeat_queue_size > 1000
  for: 10m
```

---

## Migration Path

### From Local-Only to Centralized

If already deployed with local logging, migration is simple:

```bash
# 1. Deploy Elasticsearch/Logstash
# 2. Update configuration
log_shipping_elasticsearch_host: "logs.example.com"

# 3. Re-run playbook
ansible-playbook playbook.yml

# 4. Filebeat automatically installed and configured
# 5. Logs start shipping immediately
```

### From Old Filebeat to 8.12

```bash
# 1. Set new version
log_shipping_filebeat_version: "8.12.0"

# 2. Run playbook
# 3. Old version removed, new version installed
# 4. Logs continue without interruption
```

---

## Best Practices

###  DO

1. **Enable log centralization for production** - Needed for compliance
2. **Use dedicated log server** - Don't run on application servers
3. **Monitor log volume** - Plan storage accordingly
4. **Implement log retention** - Prevent storage runaway
5. **Use ILM policies** - Automate index management
6. **Encrypt in transit** - Use TLS for shipping
7. **Restrict access** - Log server should be locked down
8. **Test recovery** - Restore logs from ES if needed

### ❌ DON'T

1. **Don't expose Elasticsearch publicly** - Major security risk
2. **Don't store passwords in playbooks** - Use Vault
3. **Don't ignore log volume growth** - Leads to disk full
4. **Don't skip retention policies** - Logs accumulate
5. **Don't disable Filebeat in production** - Lose visibility

---

## Deployment Checklist

- [ ] Review log collection requirements
- [ ] Decide: Local-only or Centralized?
- [ ] If centralized: Deploy Elasticsearch/Logstash first
- [ ] Update configuration variables
- [ ] Test in non-production environment
- [ ] Verify logs are collected/shipped
- [ ] Set up monitoring and alerting
- [ ] Document access procedures
- [ ] Train team on log queries
- [ ] Deploy to production

---

## References

- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Filebeat User Guide](https://www.elastic.co/guide/en/beats/filebeat/current/index.html)
- [rsyslog Documentation](https://www.rsyslog.com/)
- [Index Lifecycle Management](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-lifecycle-management.html)

---

**Last Updated**: November 17, 2025
**Maintained By**: Infrastructure Team
**Status**: Production Ready
