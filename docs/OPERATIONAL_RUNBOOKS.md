# Operational Runbooks

Day-2 operations procedures for managing the ansible-infra framework in production.

---

## Table of Contents

1. Client Onboarding
2. Credential Rotation
3. Disaster Recovery
4. Troubleshooting
5. Scaling Operations
6. Monitoring & Alerting
7. Security Incident Response
8. Maintenance Windows

---

## 1. Client Onboarding

### Quick Summary

Onboard a new client to the framework from start to production deployment.

### Prerequisites

- Auth0 tenant access (admin role)
- SSH access to deployment machine
- Vault password for encryption
- Target server IPs/credentials
- 1-2 hours for complete onboarding

### Step-by-Step Procedure

#### Step 1: Create Project Directory

```bash
cd /path/to/ansible-infra
cp -r inventories/projects/example-client-nodejs \
  inventories/projects/mycompany
cd inventories/projects/mycompany
```

#### Step 2: Create Auth0 M2M Application

1. Login to Auth0 dashboard
2. Navigate: Applications → Applications
3. Click "Create Application"
4. Name: "mycompany-automation" (or similar)
5. Type: "Machine to Machine"
6. Click "Create"
7. Go to Settings tab
8. Copy: Domain, Client ID, Client Secret

#### Step 3: Grant Auth0 Permissions

1. Go to M2M app → "API Explorer"
2. Check Auth0 Management API
3. Select scopes:
   - create:clients
   - read:clients
   - delete:clients
   - create:users
   - read:users
   - create:roles
   - read:roles
4. Click "Update"

#### Step 4: Create Vault File

```bash
# Create encrypted vault
ansible-vault create auth0_vault.yml

# Paste these values (from Auth0 dashboard):
vault_auth0_domain: "your-tenant.auth0.com"
vault_auth0_client_id: "YOUR_M2M_CLIENT_ID"
vault_auth0_client_secret: "YOUR_M2M_SECRET"
vault_google_oauth_client_id: ""
vault_google_oauth_secret: ""
vault_initial_admin_password: "InitialPass123!"

# When prompted for vault password:
# Create strong password (24+ characters, mixed case/numbers/symbols)
```

#### Step 5: Update Server Inventory

Edit `hosts.yml`:

```yaml
all:
  vars:
    ansible_user: ubuntu
    ansible_ssh_private_key_file: ~/.ssh/ansible_key

app_servers:
  hosts:
    prod-01:
      ansible_host: "203.0.113.10"
      app_framework: "nodejs"
      app_name: "api-gateway"
    prod-02:
      ansible_host: "203.0.113.11"
      app_framework: "nodejs"
      app_name: "api-gateway"
```

#### Step 6: Update Client Configuration

Edit `group_vars/all.yml`:

```yaml
client_name: "mycompany"
client_domain: "mycompany.com"
client_env: "production"

auth0_domain: "{{ vault_auth0_domain }}"
auth0_applications:
  - name: "myapp"
    type: "non_interactive"

app_framework: "nodejs"
app_name: "api-gateway"
app_root_path: "/opt/api-gateway"
```

#### Step 7: Test SSH Connectivity

```bash
ansible all -i hosts.yml -m ping --ask-vault-pass

# Expected output:
# prod-01 | SUCCESS => {"ping": "pong"}
# prod-02 | SUCCESS => {"ping": "pong"}
```

#### Step 8: Deploy Framework

```bash
# Dry run to preview changes
ansible-playbook ../../playbooks/client_onboarding.yml \
  -i hosts.yml \
  --ask-vault-pass \
  --check \
  --diff

# If everything looks good, deploy for real
ansible-playbook ../../playbooks/client_onboarding.yml \
  -i hosts.yml \
  --ask-vault-pass \
  -v
```

#### Step 9: Verify Deployment

```bash
# Check servers are configured
ansible all -i hosts.yml -m shell -a "systemctl status common" --ask-vault-pass

# Check Auth0 applications created
# - Login to Auth0 dashboard
# - Verify applications appear under Applications

# Check .env file exists on servers
ansible all -i hosts.yml -m shell -a "ls -la /opt/api-gateway/.env" --ask-vault-pass
```

#### Step 10: Deploy Application

Deploy your application using the generated configuration:

```bash
# Copy your Node.js app to /opt/api-gateway
scp -r your-app/* ubuntu@prod-01:/opt/api-gateway/
scp -r your-app/* ubuntu@prod-02:/opt/api-gateway/

# Install dependencies and start
ssh ubuntu@prod-01 'cd /opt/api-gateway && npm install && npm start'
ssh ubuntu@prod-02 'cd /opt/api-gateway && npm install && npm start'
```

### Verification Checklist

- [ ] Auth0 tenant has M2M application
- [ ] M2M app has required scopes
- [ ] Vault file created and encrypted
- [ ] SSH connectivity works
- [ ] Deployment completes without errors
- [ ] Auth0 applications visible in dashboard
- [ ] .env files created on servers
- [ ] Application starts and connects to Auth0

### Rollback Procedure

If deployment fails:

```bash
# SSH to servers and restore from backup
ansible all -i hosts.yml -m shell -a "restore-backup.sh" --ask-vault-pass

# Re-run deployment
ansible-playbook ../../playbooks/client_onboarding.yml \
  -i hosts.yml \
  --ask-vault-pass
```

---

## 2. Credential Rotation

### Quick Summary

Safely rotate Auth0 credentials without downtime.

### Prerequisites

- Auth0 admin access
- Current vault password
- 15-30 minutes maintenance window (optional)

### Step-by-Step Procedure

#### Step 1: Generate New Client Secret

1. Login to Auth0 dashboard
2. Go to Applications → your-client-app
3. Click Settings tab
4. Scroll to "Client Secret"
5. Click "Rotate"
6. Confirm rotation
7. Copy new secret (appears at top of settings)

#### Step 2: Update Vault File

```bash
cd inventories/projects/mycompany

# Edit vault file
ansible-vault edit auth0_vault.yml

# Update:
vault_auth0_client_secret: "YOUR_NEW_SECRET"

# Save and close
```

#### Step 3: Deploy Updated Configuration

```bash
# This updates all servers with new credentials
ansible-playbook ../../playbooks/client_onboarding.yml \
  -i hosts.yml \
  --ask-vault-pass \
  --tags auth0

# Or just update the app_integration role:
ansible-playbook ../../playbooks/client_onboarding.yml \
  -i hosts.yml \
  --ask-vault-pass \
  --tags app_integration
```

#### Step 4: Verify New Credentials

```bash
# Test Auth0 connectivity with new credentials
ansible all -i hosts.yml -m shell -a "curl -X POST https://YOUR-TENANT.auth0.com/oauth/token \
  -H 'Content-Type: application/json' \
  -d '{\"client_id\": \"YOUR-CLIENT-ID\", \"client_secret\": \"YOUR-NEW-SECRET\", \
  \"audience\": \"https://YOUR-TENANT.auth0.com/api/v2/\", \"grant_type\": \"client_credentials\"}'" \
  --ask-vault-pass

# Expected: JSON response with access_token
```

#### Step 5: Revoke Old Secret

1. Go back to Auth0 dashboard
2. Applications → your-client-app → Settings
3. Scroll to "Client Secret"
4. Click X next to old secret
5. Confirm revocation

### Verification Checklist

- [ ] New secret generated in Auth0
- [ ] Vault file updated
- [ ] Deployment succeeds
- [ ] New credentials work
- [ ] Old credentials revoked
- [ ] Application still running and authenticated

### Rollback Procedure

If new credentials don't work:

```bash
# Restore old secret in vault
ansible-vault edit inventories/projects/mycompany/auth0_vault.yml
# Revert to old secret

# Re-deploy
ansible-playbook playbooks/client_onboarding.yml \
  -i inventories/projects/mycompany/hosts.yml \
  --ask-vault-pass

# In Auth0: re-activate old secret or create fallback
```

---

## 3. Disaster Recovery

### Quick Summary

Recover from infrastructure failure to last known good state.

### Prerequisites

- Backup files available
- Vault password
- 1-2 hours for recovery
- Access to recovery infrastructure

### Step-by-Step Procedure

#### Scenario A: Server Hardware Failure

```bash
# 1. Provision replacement server (same specs)
# 2. Get new IP address
# 3. Update inventory
vim inventories/projects/mycompany/hosts.yml
# Change: ansible_host: "NEW_IP"

# 4. Re-run deployment to new server
ansible-playbook playbooks/client_onboarding.yml \
  -i inventories/projects/mycompany/hosts.yml \
  --ask-vault-pass \
  --limit prod-01  # Replace with new server name

# 5. Restore application from backup
ssh ubuntu@NEW_IP "restore-backup.sh /backups/app-latest.tar.gz"

# 6. Restart application
ssh ubuntu@NEW_IP "systemctl restart myapp"

# 7. Verify
ansible all -i inventories/projects/mycompany/hosts.yml -m ping --ask-vault-pass
```

#### Scenario B: Lost Credentials

```bash
# 1. Generate new Auth0 client secret (see Credential Rotation section)
# 2. Update vault file
ansible-vault edit inventories/projects/mycompany/auth0_vault.yml

# 3. Redeploy with new credentials
ansible-playbook playbooks/client_onboarding.yml \
  -i inventories/projects/mycompany/hosts.yml \
  --ask-vault-pass

# 4. Verify application connects with new credentials
```

#### Scenario C: Application Data Loss

```bash
# 1. List available backups
ls -la /backups/

# 2. Restore from backup
ssh ubuntu@prod-01 "restore-backup.sh /backups/db-2025-11-17.tar.gz"

# 3. Verify data integrity
ssh ubuntu@prod-01 "application-health-check.sh"

# 4. If verification fails, restore from earlier backup
ssh ubuntu@prod-01 "restore-backup.sh /backups/db-2025-11-16.tar.gz"
```

### Backup Strategy

Create daily backups:

```bash
# Schedule in crontab
0 2 * * * /opt/backup-scripts/backup-all.sh

# Manual backup
ssh ubuntu@prod-01 "/opt/backup-scripts/backup-all.sh"
```

### RTO/RPO Targets

- **RTO (Recovery Time Objective)**: <2 hours for full recovery
- **RPO (Recovery Point Objective)**: <24 hours (daily backups)

### Verification Checklist

- [ ] Replacement infrastructure available
- [ ] Backups are recent and valid
- [ ] Recovery procedure tested
- [ ] All systems come back online
- [ ] Data integrity verified
- [ ] Application authentication works
- [ ] Monitoring restored

---

## 4. Troubleshooting

### SSH Connection Issues

**Problem**: "SSH connection refused"

```bash
# 1. Check server is running
ping 203.0.113.10

# 2. Check SSH key permissions
ls -la ~/.ssh/ansible_key
# Should be: -rw------- (600)

# 3. Check SSH service is running
ssh ubuntu@203.0.113.10 "sudo systemctl status ssh"

# 4. Check security group allows port 22
# (In cloud provider console)

# 5. Try with verbose output
ssh -vvv -i ~/.ssh/ansible_key ubuntu@203.0.113.10
```

### Auth0 API Errors

**Problem**: "Auth0 API returned 401 Unauthorized"

```bash
# 1. Check vault has correct credentials
ansible-vault view inventories/projects/mycompany/auth0_vault.yml

# 2. Verify credentials in Auth0 dashboard
# - Go to Applications → your-app → Settings
# - Copy Domain, Client ID
# - Compare with vault file

# 3. Check M2M app has Management API scope
# - Applications → your-app → API Explorer
# - Should show Auth0 Management API with green checkmark

# 4. Test auth0-python SDK directly
python3 << 'EOF'
from auth0.management import Auth0Error, GetToken, Management

domain = "your-domain.auth0.com"
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"

get_token = GetToken(domain)
token = get_token.client_credentials(client_id, client_secret,
    f"https://{domain}/api/v2/")
print(f"✓ Auth0 connection successful: {token['access_token'][:20]}...")
EOF
```

### Deployment Hangs

**Problem**: Playbook seems stuck (no progress for 10+ minutes)

```bash
# 1. Stop playbook (Ctrl+C)
# 2. Check for hung SSH connections
netstat -an | grep :22

# 3. Run with verbose output to see where it's stuck
ansible-playbook playbooks/client_onboarding.yml \
  -i inventories/projects/mycompany/hosts.yml \
  --ask-vault-pass \
  -vvv

# 4. Check server is responsive
ansible all -i inventories/projects/mycompany/hosts.yml \
  -m shell -a "uptime" --ask-vault-pass

# 5. If server is not responsive, restart it
# (In cloud provider console)
```

### .env File Not Created

**Problem**: ".env file not found on server"

```bash
# 1. Check app_root_path is correct
ansible all -i inventories/projects/mycompany/hosts.yml \
  -m shell -a "ls -la /opt/api-gateway/" --ask-vault-pass

# 2. Check playbook has app_integration role
vim playbooks/client_onboarding.yml
# Should have: - role: app_integration

# 3. Check configuration variables are set
grep -A 5 "app_root_path" inventories/projects/mycompany/group_vars/all.yml

# 4. Re-run just the app_integration role
ansible-playbook playbooks/client_onboarding.yml \
  -i inventories/projects/mycompany/hosts.yml \
  --ask-vault-pass \
  --tags app_integration

# 5. Verify file permissions
ssh ubuntu@prod-01 "ls -la /opt/api-gateway/.env"
# Should be: -rw-r----- (640)
```

### Application Can't Connect to Auth0

**Problem**: "Authentication failed" or "Invalid credentials"

```bash
# 1. Check .env file has correct values
ssh ubuntu@prod-01 "cat /opt/api-gateway/.env"

# 2. Verify Auth0 credentials are current
ansible-vault view inventories/projects/mycompany/auth0_vault.yml

# 3. Test with curl
ssh ubuntu@prod-01 << 'EOF'
curl -X POST https://YOUR-DOMAIN.auth0.com/oauth/token \
  -H "Content-Type: application/json" \
  -d "{\"client_id\": \"$(grep AUTH0_CLIENT_ID .env | cut -d= -f2)\",
       \"client_secret\": \"$(grep AUTH0_CLIENT_SECRET .env | cut -d= -f2)\",
       \"audience\": \"https://YOUR-DOMAIN.auth0.com/api/v2/\",
       \"grant_type\": \"client_credentials\"}"
EOF

# 4. Check application logs
ssh ubuntu@prod-01 "docker logs my-app" 2>&1 | tail -50

# 5. If credentials invalid, see Credential Rotation section
```

---

## 5. Scaling Operations

### Add New Server

```bash
# 1. Provision new server
# - Same OS as existing servers
# - Same specs or larger
- Get IP address

# 2. Update inventory
vim inventories/projects/mycompany/hosts.yml
# Add:
prod-03:
  ansible_host: "203.0.113.12"
  app_framework: "nodejs"
  app_name: "api-gateway"

# 3. Test connectivity
ansible prod-03 -i inventories/projects/mycompany/hosts.yml \
  -m ping --ask-vault-pass

# 4. Deploy to new server
ansible-playbook playbooks/client_onboarding.yml \
  -i inventories/projects/mycompany/hosts.yml \
  --ask-vault-pass \
  --limit prod-03

# 5. Verify
ssh ubuntu@203.0.113.12 "ls /opt/api-gateway/.env"
```

### Increase Server Resources

```bash
# 1. Scale server resources (in cloud provider)
# 2. Test connectivity still works
ansible all -i inventories/projects/mycompany/hosts.yml \
  -m ping --ask-vault-pass

# 3. Monitor application performance
# Use monitoring dashboard to verify improvement
```

### Remove Server

```bash
# 1. Drain workload from server (if load balanced)
# 2. Update inventory to remove server
vim inventories/projects/mycompany/hosts.yml
# Remove prod-03 section

# 3. Tear down (in cloud provider)
# 4. Verify remaining servers have capacity
```

---

## 6. Monitoring & Alerting

### Setup Monitoring

```bash
# 1. Enable Auth0 logging
# - Login to Auth0 dashboard
# - Settings → Logs
# - Ensure logging is enabled

# 2. Setup server monitoring
ansible all -i inventories/projects/mycompany/hosts.yml \
  -m shell -a "apt-get install prometheus-node-exporter" \
  --ask-vault-pass

# 3. Configure alerts
# Create alerts for:
# - Failed authentication attempts
# - API errors > 5% rate
# - Server CPU > 80%
# - Server memory > 85%
```

### Key Metrics to Monitor

| Metric | Threshold | Action |
|--------|-----------|--------|
| Failed Auth attempts | >10/min | Investigate |
| API error rate | >5% | Page on-call |
| Server CPU | >90% | Scale/investigate |
| Server memory | >85% | Scale/investigate |
| Disk usage | >90% | Cleanup/expand |
| SSL certificate expiry | <30 days | Renew |

### Check Logs

```bash
# Auth0 logs
# - Login to Auth0 dashboard
# - Logs section
# - Filter by event type, date, IP

# Server application logs
ssh ubuntu@prod-01 "journalctl -u my-app -f"

# System logs
ssh ubuntu@prod-01 "tail -f /var/log/syslog"
```

---

## 7. Security Incident Response

### Suspected Credential Compromise

**Action**: Immediately rotate credentials

```bash
# 1. In Auth0 dashboard, revoke all current secrets
# - Applications → your-app → Settings
# - Revoke all Client Secrets

# 2. Generate new secret (see Credential Rotation section)

# 3. Update vault immediately
ansible-vault edit inventories/projects/mycompany/auth0_vault.yml
# Change vault_auth0_client_secret to new value

# 4. Deploy new credentials
ansible-playbook playbooks/client_onboarding.yml \
  -i inventories/projects/mycompany/hosts.yml \
  --ask-vault-pass

# 5. Audit Auth0 logs for suspicious activity
# - Auth0 dashboard → Logs
# - Check for unusual API calls
# - Review failed authentication attempts
```

### Suspicious Server Access

```bash
# 1. Review SSH logs
ssh ubuntu@prod-01 "tail -100 /var/log/auth.log"

# 2. Check for unauthorized users
ssh ubuntu@prod-01 "cat /etc/passwd"

# 3. Check sudo logs
ssh ubuntu@prod-01 "tail -100 /var/log/sudo.log"

# 4. If compromise suspected:
# - Isolate server (stop network access)
# - Create forensic backup
# - Rebuild server from scratch
# - Restore from clean backup
```

### DDoS or Performance Attack

```bash
# 1. Check connection rates
ssh ubuntu@prod-01 "netstat -an | grep ESTABLISHED | wc -l"

# 2. Block attacking IP (if identified)
ssh ubuntu@prod-01 "sudo ufw deny from 203.0.113.99"

# 3. Enable rate limiting on load balancer
# (In load balancer configuration)

# 4. Scale up servers to handle load
# See Scaling Operations section

# 5. Contact hosting provider if DDoS
```

---

## 8. Maintenance Windows

### Planned Maintenance (Zero-Downtime)

```bash
# 1. Schedule maintenance window
# - Notify users
# - Send calendar invites

# 2. For load-balanced setup:
# - Drain traffic from first server
# - Perform maintenance on first server
# - Bring back online
# - Repeat for other servers

# 3. For single server setup:
# - Perform maintenance during off-hours
# - Use read-only mode if possible

# 4. Examples of maintenance:
# - Update OS packages
# - Update application dependencies
# - Database maintenance
# - Certificate renewal
```

### Certificate Renewal

```bash
# 1. Check certificate expiry
openssl s_client -connect your-domain.com:443 -showcerts 2>/dev/null | \
  openssl x509 -noout -enddate

# 2. If expiry < 30 days, request new certificate
# - From certificate provider

# 3. Update certificate on servers
scp new-certificate.pem ubuntu@prod-01:/etc/ssl/certs/
ssh ubuntu@prod-01 "sudo systemctl restart nginx"

# 4. Verify certificate is updated
openssl s_client -connect your-domain.com:443 2>/dev/null | \
  openssl x509 -noout -subject -enddate
```

### OS Updates

```bash
# 1. Run updates (one server at a time for HA)
ssh ubuntu@prod-01 << 'EOF'
sudo apt-get update
sudo apt-get upgrade -y
sudo reboot
EOF

# 2. Wait for server to come back online
# 3. Verify application is running
ansible prod-01 -i inventories/projects/mycompany/hosts.yml \
  -m shell -a "systemctl status my-app" --ask-vault-pass

# 4. Repeat for other servers
```

---

## Support & Contact

For issues not covered in these runbooks:

1. Check docs/SECURITY_AUDIT.md for security issues
2. Check docs/AUTH0_INTEGRATION.md for Auth0 questions
3. Review DEPLOYMENT_GUIDE.md for configuration questions
4. Check application logs for detailed error messages

---

**Last Updated**: November 17, 2025
**Framework**: ansible-infra
**Status**: Production Ready

---

For additional help, see:
- DEPLOYMENT_GUIDE.md - Complete setup guide
- docs/SECURITY_AUDIT.md - Security procedures
- docs/AUTH0_INTEGRATION.md - Auth0 configuration
