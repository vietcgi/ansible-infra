# Testing Guide for Ansible Infrastructure Automation

This directory contains comprehensive test scenarios for validating the Ansible infrastructure automation roles.

## Test Structure

```
tests/
├── README.md (this file)
├── test-syntax-validation.yml
├── test-idempotency.yml
├── test-connectivity.yml
└── fixtures/ (test data)
```

## Test Categories

### 1. Syntax Validation
**File:** `test-syntax-validation.yml`

Validates YAML syntax and Ansible playbook correctness.

```bash
ansible-playbook tests/test-syntax-validation.yml
```

**What It Tests:**
- All playbooks parse without errors
- All roles are syntactically valid
- Template files are valid

**Expected Result:** ✓ All Playbooks: VALID

---

### 2. Idempotency Testing
**File:** `test-idempotency.yml`

Runs each deployment twice to verify no changes on second run.

```bash
ansible-playbook tests/test-idempotency.yml \
  -i inventories/testing/hosts
```

**What It Tests:**
- Wireguard Full Mesh: Idempotent
- Wireguard Hub-Spoke: Idempotent
- Wireguard Site-to-Site: Idempotent
- OPNSense Firewall: Idempotent
- pfSense Firewall: Idempotent

**Expected Result:** Second run should show `changed: false`

---

### 3. Connectivity Testing
**File:** `test-connectivity.yml`

Validates VPN connectivity between deployed nodes.

```bash
ansible-playbook tests/test-connectivity.yml \
  -i inventories/testing/hosts
```

**What It Tests:**
- **Full Mesh:** All nodes can ping all other nodes
- **Hub-Spoke:** Spokes can reach hub, and spokes can reach each other via hub
- **Site-to-Site:** Remote site gateways reachable via VPN

**Expected Result:** All pings successful

---

## Molecule Testing

Molecule provides integrated testing with Docker containers.

### Full Mesh Topology

```bash
cd roles/wireguard_vpn
molecule test -s full-mesh
```

**Tests:**
- Syntax validation
- Role execution (converge)
- Idempotency (second run)
- Verification (interface, keys, config)
- Cleanup

**Expected Output:**
```
PASSED converge - ...
PASSED verify - ...
```

### Hub-Spoke Topology

```bash
cd roles/wireguard_vpn
molecule test -s hub-spoke
```

**Expected:** Hub and spoke nodes properly configured

### Site-to-Site Topology

```bash
cd roles/wireguard_vpn
molecule test -s site-to-site
```

**Expected:** 3 gateway nodes with inter-site routes

---

## Manual Testing Steps

If Molecule is not available, follow these steps for manual testing:

### Step 1: Setup Test Environment

```bash
# Create test VMs or use existing infrastructure
# Configure inventory with test hosts

cd /Users/kevin/ansible-infra
```

### Step 2: Syntax Validation

```bash
# Check all playbooks
ansible-playbook --syntax-check playbooks/*.yml

# Check all roles
find roles -name "*.yml" | xargs -I {} ansible-playbook --syntax-check {}
```

**Expected:** No errors reported

### Step 3: Deploy Wireguard Full Mesh

```bash
ansible-playbook playbooks/deploy-wireguard.yml \
  -i inventories/testing/hosts \
  -e "wireguard_topology=full_mesh" \
  -v
```

**Verify:**
- All nodes deployed successfully
- Wireguard interface created on each node
- Configuration file present: `/etc/wireguard/wg0.conf`
- Keys generated: `/etc/wireguard/wg0.key`, `/etc/wireguard/wg0_public.key`

### Step 4: Test Idempotency

```bash
# Run again - should show no changes
ansible-playbook playbooks/deploy-wireguard.yml \
  -i inventories/testing/hosts \
  -e "wireguard_topology=full_mesh"
```

**Expected:** No changes reported (all "ok" status)

### Step 5: Test Connectivity

```bash
# From node1, ping other nodes
ansible wireguard_full_mesh -i inventories/testing/hosts \
  -m shell -a "ping -c 3 10.100.0.2"
```

**Expected:** All ping replies successful

### Step 6: Deploy Hub-Spoke

```bash
ansible-playbook playbooks/deploy-wireguard.yml \
  -i inventories/testing/hosts \
  -e "wireguard_topology=hub_spoke"
```

**Verify:**
- Hub node has multiple peers configured
- Spoke nodes have only hub peer configured

### Step 7: Test Hub Failover

```bash
# On primary hub, temporarily disable Wireguard
ssh hub "sudo ip link set wg0 down"

# Verify spokes can still communicate
ansible spoke1 -i inventories/testing/hosts \
  -m shell -a "ping -c 3 10.100.0.22"

# Re-enable hub
ssh hub "sudo ip link set wg0 up"
```

### Step 8: Deploy Firewalls

```bash
# OPNSense
ansible-playbook playbooks/deploy-firewalls.yml \
  -i inventories/testing/hosts/firewall-example.yml

# pfSense
ansible-playbook playbooks/deploy-firewalls.yml \
  -i inventories/testing/hosts/pfsense-example.yml
```

**Verify:** Firewall configuration applied via API/SSH

### Step 9: Full Integration Test

```bash
# Deploy all components
ansible-playbook playbooks/deploy-infrastructure.yml \
  -i inventories/testing/hosts
```

**Verify:** All 6 stages complete without errors

---

## Test Inventory Configuration

Create `inventories/testing/hosts` for testing:

```yaml
all:
  children:
    wireguard_full_mesh:
      hosts:
        node1:
          ansible_host: 192.168.100.10
          wireguard_interface: wg0
          wireguard_vpn_ip: 10.100.0.1
        node2:
          ansible_host: 192.168.100.11
          wireguard_vpn_ip: 10.100.0.2
        node3:
          ansible_host: 192.168.100.12
          wireguard_vpn_ip: 10.100.0.3

    wireguard_hub_spoke:
      hosts:
        hub:
          ansible_host: 192.168.100.20
          wireguard_hub_node: hub
        spoke1:
          ansible_host: 192.168.100.21
        spoke2:
          ansible_host: 192.168.100.22

    opnsense_firewall:
      hosts:
        opnsense:
          ansible_host: 192.168.100.30
          opnsense_api_host: opnsense.local

    pfsense_firewall:
      hosts:
        pfsense:
          ansible_host: 192.168.100.31
          ansible_python_interpreter: /usr/local/bin/python3.11
```

---

## Troubleshooting Tests

### Molecule Not Available

```bash
pip install molecule molecule-docker ansible-lint
```

### Docker Permission Denied

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Wireguard Interface Not Created

Check:
1. Wireguard package installed: `apt-get install wireguard wireguard-tools`
2. Kernel support: `modprobe wireguard`
3. Task execution: Check Ansible output for errors

### Connectivity Test Fails

Check:
1. Firewall rules allowing UDP 51820
2. Network connectivity between test nodes
3. Wireguard status: `wg show`
4. Interface status: `ip link show wg0`

### Idempotency Test Fails

Check:
1. Task handlers properly configured
2. State-based module parameters correct
3. File permissions unchanged between runs

---

## Test Results Documentation

After running tests, document results:

### Sample Test Report

```markdown
# Test Results - 2025-11-19

## Syntax Validation
- Status: ✓ PASS
- All playbooks valid
- All roles valid

## Idempotency (Wireguard Full Mesh)
- First run: changed=3
- Second run: changed=0
- Status: ✓ PASS (idempotent)

## Connectivity (Wireguard Full Mesh)
- node1 → node2: ✓ OK (3 packets received)
- node1 → node3: ✓ OK
- node2 → node3: ✓ OK
- Status: ✓ PASS (all connected)

## Overall
- Status: ✓ READY FOR PRODUCTION
```

---

## Continuous Testing

### Pre-Commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
ansible-playbook --syntax-check playbooks/*.yml || exit 1
```

### CI/CD Integration

For GitHub Actions or similar:

```yaml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: geerlingguy/setup-docker-ubuntu@master
      - run: pip install molecule molecule-docker
      - run: molecule test -s full-mesh
```

---

## Test Coverage Goals

- ✓ Syntax: 100% (all files)
- ✓ Idempotency: 100% (all roles)
- ✓ Connectivity: 100% (all topologies)
- ✓ Integration: 100% (full stack)
- ✓ Error Handling: 90%+ (known edge cases)

---

## Contact & Support

For test failures or questions:
1. Check role README.md
2. Review task output with `-vvv` flag
3. Consult IMPLEMENTATION_STATUS.md for known issues
4. Report reproducible failures with test output

---

**Last Updated:** 2025-11-19
**Status:** Ready for Testing
