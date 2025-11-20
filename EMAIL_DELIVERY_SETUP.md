# Email Delivery Setup Guide

Complete automated email server configuration using Ansible with KumoMTA, Cloudflare DNS, and Let's Encrypt.

## Overview

This solution automates the complete setup of an email delivery platform that includes:

- **DNS Configuration**: Automatic A, MX, SPF, DKIM, and DMARC record creation in Cloudflare
- **TLS Certificates**: Let's Encrypt certificates via DNS validation with automatic renewal
- **DKIM**: Automatic key generation and DNS record publishing
- **Email Delivery**: KumoMTA configured for outbound email with intelligent routing
- **Monitoring**: Built-in metrics collection and health checks
- **Logging**: Structured JSON logging with log rotation

## Prerequisites

### Infrastructure Requirements
- Ubuntu 20.04 LTS or later (Focal Fossa or newer)
- Minimum 2 CPU cores, 2GB RAM
- Public static IP address
- Domain registered with Cloudflare as DNS provider

### Credentials Required
- **Cloudflare API Token** with DNS:Edit permission
  - Get from: https://dash.cloudflare.com/profile/api-tokens
  - Required permissions: Zone > DNS > Edit
- **Cloudflare Zone ID** (numeric ID for your domain)
  - Find in: https://dash.cloudflare.com → Select domain → Right sidebar

### Local Requirements
- Ansible 2.9+ installed on control machine
- SSH access to target server with sudo privileges

## Setup Steps

### 1. Prepare Vault Credentials

Create the vault file with your Cloudflare credentials:

```bash
# Copy template and edit with your real credentials
cp group_vars/email_servers.vault.yml.example group_vars/email_servers.vault.yml

# Edit the file
nano group_vars/email_servers.vault.yml
# Replace:
# - vault_cloudflare_api_token: "YOUR_API_TOKEN"
# - vault_cloudflare_zone_id: "YOUR_ZONE_ID"

# Encrypt the vault file
ansible-vault encrypt group_vars/email_servers.vault.yml
# You'll be prompted to create a vault password
```

### 2. Configure Inventory

Edit `inventory/email-delivery.ini` with your server details:

```ini
[email_servers]
mail.example.com  ansible_user=ubuntu  ansible_host=YOUR_IP_ADDRESS

[email_servers:vars]
email_domain=example.com
email_server_ip=YOUR_IP_ADDRESS
```

### 3. Run the Email Delivery Setup Playbook

```bash
ansible-playbook playbooks/email-delivery-setup.yml \
  -i inventory/email-delivery.ini \
  --ask-vault-pass
```

You'll be prompted for the vault password (the one you created in step 1).

**Alternatively, create a vault password file:**

```bash
# Create password file
echo "your-vault-password" > ~/.ansible-vault-pass
chmod 600 ~/.ansible-vault-pass

# Run without prompting
ansible-playbook playbooks/email-delivery-setup.yml \
  -i inventory/email-delivery.ini \
  --vault-password-file ~/.ansible-vault-pass
```

### 4. Verify Deployment

The playbook will display a summary at the end. Verify the setup:

```bash
# SSH into the server
ssh ubuntu@your.mail.server

# Check service status
sudo systemctl status kumomta

# Run health check
/usr/local/bin/kumomta-health-check.sh

# View monitoring status
/usr/local/bin/kumomta-monitoring-status.sh
```

## Verifying DNS Records

After deployment, verify that all DNS records are properly configured:

```bash
# Check A record
nslookup example.com

# Check MX record
nslookup -type=MX example.com

# Check SPF record
nslookup -type=TXT example.com

# Check DKIM record (replace 'default' with your selector if different)
nslookup -type=TXT default._domainkey.example.com

# Check DMARC record
nslookup -type=TXT _dmarc.example.com

# Detailed DNS check
dig example.com +short
```

DNS records typically propagate within 5-15 minutes but can take up to 24 hours globally.

## Sending Test Emails

Once DNS is configured and propagated, test email delivery:

### Using Command Line
```bash
# SSH into the mail server
ssh ubuntu@your.mail.server

# Send a test email
echo "Test message" | mail -s "Test Subject" recipient@example.com
```

### Using Python
```python
import smtplib
from email.mime.text import MIMEText

msg = MIMEText("Test message body")
msg['Subject'] = "Test Email"
msg['From'] = "sender@example.com"
msg['To'] = "recipient@example.com"

with smtplib.SMTP('your.mail.server', 25) as server:
    server.send_message(msg)
```

## Configuration Files

### Main Configuration
- **Role Defaults**: `roles/email-delivery/defaults/main.yml`
  - All customizable variables with documentation

### Task Files
- **DNS Setup**: `roles/email-delivery/tasks/cloudflare-dns.yml`
- **DKIM**: `roles/email-delivery/tasks/dkim-setup.yml`
- **SPF**: `roles/email-delivery/tasks/spf-setup.yml`
- **DMARC**: `roles/email-delivery/tasks/dmarc-setup.yml`
- **TLS Certificates**: `roles/email-delivery/tasks/tls-certificates.yml`
- **Delivery**: `roles/email-delivery/tasks/kumomta-delivery.yml`
- **Routing**: `roles/email-delivery/tasks/email-routing.yml`
- **Monitoring**: `roles/email-delivery/tasks/monitoring-setup.yml`

### Templates (deployed to /etc/kumomta/)
- **Cloudflare Credentials**: `templates/cloudflare-credentials.j2`
- **Delivery Queue**: `templates/email-delivery-queue.lua.j2`
- **Delivery Policy**: `templates/email-delivery-policy.lua.j2`
- **Routing Config**: `templates/email-routing-config.lua.j2`

## Server-Side Files (Post-Deployment)

### Configuration
- `/etc/kumomta/kumomta.conf` - Main KumoMTA configuration
- `/etc/kumomta/cloudflare.ini` - Certbot DNS credentials
- `/etc/kumomta/domain_routes.conf` - Domain routing rules

### Scripts
- `/etc/kumomta/email-delivery-queue.lua` - Queue management
- `/etc/kumomta/email-delivery-policy.lua` - Policy enforcement
- `/etc/kumomta/email-routing.lua` - Routing logic

### Keys & Certificates
- `/etc/kumomta/dkim/` - DKIM private/public keys
- `/etc/kumomta/certs/` - Symlinked TLS certificates
- `/etc/letsencrypt/live/{{ domain }}/` - Let's Encrypt certificates

### Logs & Monitoring
- `/var/log/kumomta/kumomta.log` - Main KumoMTA log file
- `/etc/kumomta/prometheus-config.txt` - Prometheus configuration
- `/etc/kumomta/prometheus-alerts.yml` - Alert rules

### Health & Status Scripts
- `/usr/local/bin/kumomta-health-check.sh` - Health verification
- `/usr/local/bin/kumomta-monitoring-status.sh` - Status reporting

## Monitoring

### Health Checks
```bash
# Run health check
/usr/local/bin/kumomta-health-check.sh

# View status
/usr/local/bin/kumomta-monitoring-status.sh
```

### Prometheus Metrics
KumoMTA exposes Prometheus metrics on `127.0.0.1:9090`

Key metrics:
- `kumomta_messages_accepted_total` - Total messages accepted
- `kumomta_messages_delivered_total` - Successfully delivered messages
- `kumomta_messages_bounced_total` - Messages that bounced
- `kumomta_messages_failed_total` - Permanently failed messages
- `kumomta_queue_depth` - Messages currently in queue
- `kumomta_delivery_latency_seconds` - Delivery latency histogram

### Log Files
```bash
# View real-time logs
tail -f /var/log/kumomta/kumomta.log

# View specific message delivery
grep "recipient@domain.com" /var/log/kumomta/kumomta.log | tail -20

# Check for errors
grep -i error /var/log/kumomta/kumomta.log | tail -20
```

## Customization

### Change DMARC Policy
Edit `inventory/email-delivery.ini` or pass via command line:
```bash
ansible-playbook playbooks/email-delivery-setup.yml \
  -i inventory/email-delivery.ini \
  --ask-vault-pass \
  -e "dmarc_policy=none"  # Options: none, quarantine, reject
```

### Add Additional Domains
Modify in inventory or roles/email-delivery/defaults/main.yml:
```yaml
email_alternate_domains:
  - mail2.example.com
  - alt.example.com
```

### Configure Email Relay
Set relay host if you need to relay through another server:
```bash
ansible-playbook playbooks/email-delivery-setup.yml \
  -i inventory/email-delivery.ini \
  --ask-vault-pass \
  -e "kumomta_relay_host=relay.example.com" \
  -e "kumomta_relay_port=587" \
  -e "kumomta_relay_use_tls=true"
```

### Adjust Delivery Parameters
```bash
# Max delivery attempts before bouncing
-e "kumomta_max_delivery_attempts=7"

# Maximum message size (bytes)
-e "kumomta_max_message_size=52428800"  # 50MB

# Messages per minute per domain
-e "kumomta_max_messages_per_minute=500"
```

## Troubleshooting

### DNS Records Not Propagating
```bash
# Check Cloudflare API connection
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/YOUR_ZONE_ID/dns_records"

# Verify records in Cloudflare dashboard
# https://dash.cloudflare.com → Select domain → DNS tab
```

### KumoMTA Not Starting
```bash
# Check service status
sudo systemctl status kumomta

# View service logs
sudo journalctl -u kumomta -n 50 --no-pager

# Check configuration syntax
sudo kumomta -c /etc/kumomta/kumomta.conf --validate
```

### Certificate Issues
```bash
# Check certificate expiry
openssl x509 -in /etc/kumomta/certs/kumomta.crt -noout -dates

# Check Let's Encrypt renewal
sudo certbot certificates

# Manual renewal
sudo certbot renew --dns-cloudflare --dry-run
```

### DKIM Signature Issues
```bash
# Verify DKIM key exists
ls -l /etc/kumomta/dkim/

# Check DKIM DNS record
dig default._domainkey.example.com TXT

# Test DKIM signing (requires test email)
grep "DKIM-Signature" /var/log/kumomta/kumomta.log
```

## Backup & Recovery

### Backup Critical Files
```bash
# Backup DKIM keys
tar -czf backup-dkim.tar.gz /etc/kumomta/dkim/

# Backup certificates
tar -czf backup-certs.tar.gz /etc/letsencrypt/live/

# Backup configuration
tar -czf backup-config.tar.gz /etc/kumomta/*.conf /etc/kumomta/*.lua
```

### Restore from Backup
```bash
# Restore DKIM keys
tar -xzf backup-dkim.tar.gz

# Fix permissions
sudo chown -R kumomta:kumomta /etc/kumomta/dkim/
sudo chmod 600 /etc/kumomta/dkim/*.key

# Restart service
sudo systemctl restart kumomta
```

## Security Considerations

1. **Vault Password**: Store vault password securely, never commit to git
2. **API Token**: Use Cloudflare API tokens with minimal required permissions
3. **DKIM Keys**: Backup DKIM private keys securely; if compromised, regenerate
4. **TLS Certificates**: Monitor certificate expiry; renewal is automatic
5. **Firewall**: Open only required ports:
   - Port 25 (SMTP) - Mail submission from external servers
   - Port 587 (Submission) - Authenticated mail submission
   - Port 465 (SMTPS) - Secure SMTP (optional)
   - Restrict other ports to localhost only

## Support & Troubleshooting

For detailed logs and debugging:
```bash
# Enable verbose Ansible output
ansible-playbook playbooks/email-delivery-setup.yml \
  -i inventory/email-delivery.ini \
  --ask-vault-pass \
  -vvv
```

Check role documentation:
- KumoMTA Role: `roles/kumomta/README.md`
- Email Delivery Role: `roles/email-delivery/README.md`

## References

- **KumoMTA**: https://www.kumomta.com
- **Let's Encrypt**: https://letsencrypt.org
- **Cloudflare API**: https://developers.cloudflare.com/api/
- **DKIM**: https://tools.ietf.org/html/rfc6376
- **DMARC**: https://tools.ietf.org/html/rfc7489
- **SPF**: https://tools.ietf.org/html/rfc7208

## Version Information

- Ansible: 2.9+
- KumoMTA: Latest stable
- Ubuntu: 20.04 LTS or newer
- Certbot: 1.0+
- Python: 3.6+
