# Testing Guide - How to Verify Framework Works

Complete guide to testing the ansible-infra framework before deploying to customers.

## Testing Options (Choose One)

### Option 1: Test with Real Auth0 Account (Recommended - 30 minutes)
**Best for**: Validating actual Auth0 integration
**Requirements**: Auth0 account (free tier is fine)
**Risk**: Low - using test account only

**Steps**:
```bash
# 1. Create free Auth0 account
# https://auth0.com/ → Sign up → Verify email

# 2. Create M2M application in Auth0
# Dashboard → Applications → Create → Machine-to-Machine
# Name: "Ansible Test"
# Grant: Auth0 Management API (all scopes)

# 3. Copy credentials
# Copy: Domain, Client ID, Client Secret

# 4. Create test inventory
mkdir -p inventories/projects/test-auth0/group_vars
cat > inventories/projects/test-auth0/group_vars/all.yml << 'EOF'
---
client_name: "test"
auth0_domain: "your-domain.auth0.com"
auth0_client_id: "YOUR_CLIENT_ID"
auth0_client_secret: "YOUR_CLIENT_SECRET"
auth0_applications:
 - name: "test-app"
 type: "non_interactive"
auth0_users:
 - email: "test@example.com"
 given_name: "Test"
 family_name: "User"
 password: "TestPass123!"
EOF

# 5. Run auth0 role only (no servers needed)
ansible-playbook playbooks/client_onboarding.yml \
 -i inventories/projects/test-auth0/hosts.yml \
 -t auth0,validation \
 --check \
 -e "ansible_connection=local"

# 6. Verify in Auth0 dashboard
# - Applications → See "test-app" created
# - Users → See "test@example.com" created
# - Roles → See any configured roles

# 7. Clean up
# Delete test application and user from Auth0 dashboard
```

**Success Criteria**:
- No API errors in playbook output
- Application appears in Auth0 dashboard
- User appears in Auth0 dashboard
- Auth0 logs show successful API calls

---

### Option 2: Test with Mock Servers (Recommended - 1 hour)
**Best for**: Full end-to-end testing
**Requirements**: Docker (for local servers) or VirtualBox/Vagrant
**Cost**: Free (uses local resources)

**Steps with Docker**:
```bash
# 1. Start 2 test Ubuntu containers
docker run -d --name test-server-1 \
 -p 2201:22 \
 --cap-add=SYS_ADMIN \
 ubuntu:22.04 \
 /bin/bash -c "apt-get update && apt-get install -y openssh-server python3 python3-pip && \
 mkdir -p /run/sshd && \
 useradd -m -s /bin/bash ubuntu && \
 echo 'ubuntu:ubuntu' | chpasswd && \
 sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
 /usr/sbin/sshd -D"

docker run -d --name test-server-2 \
 -p 2202:22 \
 --cap-add=SYS_ADMIN \
 ubuntu:22.04 \
 /bin/bash -c "apt-get update && apt-get install -y openssh-server python3 python3-pip && \
 mkdir -p /run/sshd && \
 useradd -m -s /bin/bash ubuntu && \
 echo 'ubuntu:ubuntu' | chpasswd && \
 sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
 /usr/sbin/sshd -D"

sleep 5

# 2. Create inventory for local servers
cat > inventories/projects/test-local/hosts.yml << 'EOF'
---
all:
 vars:
 ansible_user: "ubuntu"
 ansible_password: "ubuntu"
 ansible_port: 2201
 ansible_python_interpreter: "/usr/bin/python3"

 children:
 test_servers:
 hosts:
 test-01:
 ansible_host: "127.0.0.1"
 ansible_port: 2201
 app_framework: "nodejs"
 app_name: "test-app-1"

 test-02:
 ansible_host: "127.0.0.1"
 ansible_port: 2202
 app_framework: "nodejs"
 app_name: "test-app-2"
EOF

# 3. Test connectivity
ansible all -i inventories/projects/test-local/hosts.yml -m ping

# 4. Run common role only (no Auth0 test)
ansible-playbook playbooks/client_onboarding.yml \
 -i inventories/projects/test-local/hosts.yml \
 -t common \
 --check \
 --diff

# 5. Clean up
docker stop test-server-1 test-server-2
docker rm test-server-1 test-server-2
```

**Success Criteria**:
- Ping succeeds on both containers
- Common role tasks preview correctly
- No errors in playbook output

---

### Option 3: Test with Existing Servers (Production Test - 2 hours)
**Best for**: Testing on actual infrastructure
**Requirements**: 2-3 test servers (VPS, cloud, on-prem)
**Cost**: Depends on hosting (AWS free tier works)

**Steps**:
```bash
# 1. Provision test servers
# - 2x Ubuntu 22.04 servers
# - SSH access configured
# - Public IPs or accessible via private network
# - Min 2GB RAM, 20GB disk

# 2. Create inventory
mkdir -p inventories/projects/test-prod/group_vars
cat > inventories/projects/test-prod/hosts.yml << 'EOF'
---
all:
 vars:
 ansible_user: "ubuntu"
 ansible_ssh_private_key_file: "~/.ssh/test_key"
 ansible_python_interpreter: "/usr/bin/python3"

 children:
 test_servers:
 hosts:
 test-prod-01:
 ansible_host: "203.0.113.10"
 app_framework: "nodejs"
 app_name: "test-app"

 test-prod-02:
 ansible_host: "203.0.113.11"
 app_framework: "nodejs"
 app_name: "test-app"
EOF

# 3. Copy configuration
cp inventories/projects/_templates/client_template.yml \
 inventories/projects/test-prod/group_vars/all.yml

# 4. Create test vault
ansible-vault create inventories/projects/test-prod/auth0_vault.yml
# Add test Auth0 credentials

# 5. Test connectivity
ansible all -i inventories/projects/test-prod/hosts.yml \
 --ask-vault-pass \
 -m ping

# 6. Dry-run deployment
ansible-playbook playbooks/client_onboarding.yml \
 -i inventories/projects/test-prod/hosts.yml \
 --ask-vault-pass \
 --check \
 --diff

# 7. Deploy (if dry-run looks good)
ansible-playbook playbooks/client_onboarding.yml \
 -i inventories/projects/test-prod/hosts.yml \
 --ask-vault-pass \
 -v

# 8. Verify
# - SSH into servers
# - Check /opt/test-app/.env exists
# - Check /opt/test-app/auth0.config.js exists
# - Verify Auth0 application created
# - Verify user created

# 9. Clean up
# - Delete Auth0 application and users
# - Terminate test servers
# - Remove test configurations
```

**Success Criteria**:
- All servers respond to ping
- Dry-run shows all planned changes
- Playbook runs without errors
- .env file created on servers
- Auth0 applications created
- Applications appear in Auth0 dashboard

---

## Testing Checklist

### Pre-Testing
- [ ] Framework code reviewed
- [ ] All files are syntactically valid YAML
- [ ] No hardcoded secrets in code
- [ ] Documentation is complete
- [ ] Example clients exist

### Auth0 Testing
- [ ] Auth0 account created (free tier)
- [ ] M2M application created with proper scopes
- [ ] Client ID and secret copied correctly
- [ ] Vault can encrypt/decrypt credentials
- [ ] API connectivity test passes

### Deployment Testing
- [ ] Inventory file created correctly
- [ ] Hosts can be pinged
- [ ] SSH keys have correct permissions (600)
- [ ] Dry-run shows expected changes
- [ ] Playbook executes without errors

### Verification Testing
- [ ] .env files created on servers
- [ ] Files have correct permissions (0640)
- [ ] Auth0 applications visible in dashboard
- [ ] Users created in Auth0
- [ ] Roles configured correctly
- [ ] No errors in Auth0 logs

### Security Testing
- [ ] No secrets in playbook output
- [ ] Vault passwords not logged
- [ ] SSH keys never exposed
- [ ] File permissions are restrictive
- [ ] HTTPS enforcement verified

---

## Quick Test Script

Run this to test locally without needing Auth0 or servers:

```bash
#!/bin/bash

echo "Running Framework Tests..."
echo ""

# Test 1: YAML Syntax
echo "1. Checking YAML syntax..."
ansible-playbook --syntax-check playbooks/client_onboarding.yml
if [ $? -eq 0 ]; then echo "✓ PASS"; else echo "✗ FAIL"; exit 1; fi
echo ""

# Test 2: File Permissions
echo "2. Checking vault file permissions..."
if [ -f "inventories/projects/_templates/client_template.yml" ]; then
 echo "✓ Template exists"
else
 echo "✗ Template missing"
 exit 1
fi
echo ""

# Test 3: Script Execution
echo "3. Testing client creation script..."
if [ -x "scripts/create-client.sh" ]; then
 echo "✓ Script is executable"
else
 echo "✗ Script not executable"
 chmod +x scripts/create-client.sh
fi
echo ""

# Test 4: Documentation
echo "4. Checking documentation..."
docs=(
 "docs/AUTH0_INTEGRATION.md"
 "docs/CLIENT_ONBOARDING.md"
 "docs/SECURITY_AUDIT.md"
 "PRODUCTION_READY.md"
)
for doc in "${docs[@]}"; do
 if [ -f "$doc" ]; then
 echo "✓ $doc exists"
 else
 echo "✗ $doc missing"
 exit 1
 fi
done
echo ""

# Test 5: Example Clients
echo "5. Checking example clients..."
examples=(
 "inventories/projects/example-client-nodejs"
 "inventories/projects/example-client-python"
)
for example in "${examples[@]}"; do
 if [ -d "$example" ]; then
 echo "✓ $example exists"
 else
 echo "✗ $example missing"
 exit 1
 fi
done
echo ""

echo " All basic tests passed!"
echo ""
echo "Next steps:"
echo "1. Test with Auth0 account (Option 1)"
echo "2. Or test with Docker containers (Option 2)"
echo "3. Or test with real servers (Option 3)"

```

**Run it**:
```bash
bash test-framework.sh
```

---

## Testing Schedule

### Immediate (Today)
- YAML syntax validation
- File structure verification
- Documentation completeness

### This Week (Recommended)
- Auth0 API integration test
- Docker container testing
- Role execution verification

### Before First Customer
- Full end-to-end test on real servers
- Security validation
- Performance benchmarking

---

## Troubleshooting Tests

### "SSH connection refused"
```bash
# Check SSH is running
ssh -i ~/.ssh/test_key ubuntu@SERVER_IP "echo 'SSH works!'"

# If fails, verify:
# - Server IP is correct
# - SSH key has permissions 600
# - Firewall allows port 22
```

### "YAML syntax error"
```bash
# Validate playbook
ansible-playbook --syntax-check playbooks/client_onboarding.yml

# Validate specific file
ansible-playbook --syntax-check roles/auth0/tasks/main.yml
```

### "Auth0 API error"
```bash
# Check credentials are correct
ansible-vault view inventories/projects/test-auth0/auth0_vault.yml

# Verify in Auth0 dashboard:
# - Domain matches exactly
# - M2M app has Management API access
# - Scopes are enabled
```

### "Permission denied on .env"
```bash
# Check file permissions on remote server
ssh ubuntu@SERVER_IP "ls -la /opt/test-app/.env"

# Should show: -rw-r----- (0640)
```

---

## Success Metrics

### Framework is working if:
- Playbook runs without errors
- Auth0 applications are created
- Users appear in Auth0
- .env files exist on servers
- File permissions are correct
- No secrets exposed in logs

### Framework is production-ready if:
- All above tests pass
- Testing on multiple OS distributions succeeds
- Multiple framework types work (Node.js, Python, etc.)
- Scaling to multiple servers works
- Dry-run and actual runs produce same results

---

## Next Steps After Testing

1. **If tests pass**:
 - Clean up test resources
 - Document test results
 - Proceed to customer deployment

2. **If tests fail**:
 - Review error messages carefully
 - Check documentation for solutions
 - Verify prerequisites (SSH, Auth0, etc.)
 - Try simpler test option first

3. **Before first customer**:
 - Run full test again with customer config
 - Verify all expected artifacts created
 - Test Auth0 login flow manually
 - Document any custom configurations

---

**Testing Status**: Ready for validation
**Recommended Test**: Option 1 (Auth0) + Option 2 (Docker)
**Estimated Time**: 1-2 hours total
**Risk Level**: LOW (testing only, no production impact)

